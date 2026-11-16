import html,json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .common import md_table,write_json,save

def monitor(j,config,out):
    end=pd.Timestamp(config['analysis_end']);daily=j.groupby('date').sales_value.sum().asfreq('D',fill_value=0)
    old=daily[(daily.index>end-pd.Timedelta(days=56))&(daily.index<=end-pd.Timedelta(days=28))]
    new=daily[daily.index>end-pd.Timedelta(days=28)]
    edges=np.unique(np.r_[-np.inf,np.quantile(old,[.2,.4,.6,.8]),np.inf])
    p=np.histogram(old,edges)[0]/len(old);q=np.histogram(new,edges)[0]/len(new)
    p=np.maximum(p,1e-4);q=np.maximum(q,1e-4)
    psi=float(np.sum((q-p)*np.log(q/p)))
    result={'comparison':'Last 28 observed days vs previous 28 days, household panel sales_value per day','daily_sales_PSI':psi,'PSI_warning_threshold':config['monitoring_psi_warning'],'daily_sales_change':float(new.mean()/old.mean()-1),'status':'review_distribution_change' if psi>config['monitoring_psi_warning'] else 'no_distribution_warning','caveat':'28 observations each; threshold is configurable heuristic, seasonality is not removed, not proof of degradation. No live current-date freshness assertion on historical files.'}
    write_json(out/'monitoring.json',result)
    return result

def build_report(out,config,qa,analytics,forecast,risk,association,monitoring,runmeta):
    def read(name): return pd.read_csv(out/f'{name}.csv')
    monthly=read('monthly_kpis');abc=read('product_abc');seg=read('segment_summary');bridge=read('sales_bridge');rules=read('association_rules');campaign=read('campaign_redemption') if (out/'campaign_redemption.csv').exists() else pd.DataFrame()
    ftest=read('forecast_test_metrics');rtest=read('risk_test_metrics');latest=read('forecast_next_7_days');actions=read('customer_risk_actions')
    b=bridge.iloc[-1];cur=monthly.iloc[-1];prev=monthly.iloc[-2]
    top_rule=rules.iloc[0]
    cs=rtest[rtest.model==risk['champion_selected_on_validation']]
    insights=[
        {'finding':f'Tháng {cur.month}: sales_value {cur.sales:,.2f} USD, thay đổi {cur.sales/prev.sales-1:+.1%} so với {prev.month}.','evidence':f'Chênh lệch {b.sales_delta:,.2f} USD = hiệu ứng số giỏ {b.basket_count_effect:,.2f} + giá trị giỏ {b.basket_value_effect:,.2f}. Phân rã đối xứng, đã đối soát.','action':'Kiểm tra ngành hàng đóng góp và số hộ mua; đối chiếu lịch chương trình trước khi quy nguyên nhân.','owner':'Vận hành / ngành hàng','measure':'Số giỏ, giá trị giỏ; không suy diễn lợi nhuận.'},
        {'finding':f'20% hộ có giá trị mua cao nhất đóng góp {analytics["top20_sales_share"]:.1%} doanh số mua dương.','evidence':'Xếp hạng tổng sales_value dương trong kỳ; không tính lãi gộp hay CLV.','action':'Lập nhóm chăm sóc giá trị cao, xem thêm thay đổi hành vi và thử nghiệm có đối chứng.','owner':'CRM','measure':'Incremental retention và lãi sau chi phí khi có dữ liệu giá vốn.'},
        {'finding':f'{analytics["A_product_count"]:,}/{analytics["product_count"]:,} SKU thuộc nhóm ABC-A theo ngưỡng 80% doanh số mua dương.','evidence':'Ngưỡng tích lũy 80%/95%, gồm SKU vượt ngưỡng; kết quả phụ thuộc panel khách đang quan sát.','action':'Dùng làm danh sách đối chiếu danh mục và mức sẵn hàng; chưa đặt hàng theo ABC khi thiếu tồn kho.','owner':'Ngành hàng / cung ứng','measure':'Doanh số và tỷ lệ có hàng; cần số liệu tồn cho service level.'},
        {'finding':f'Quy tắc mua cùng có điểm xếp hạng cao nhất: {top_rule.A} → {top_rule.B}.','evidence':f'Lift train {top_rule.train_lift:.2f}; lift kỳ sau {top_rule.test_lift:.2f}; {int(top_rule.test_pair_baskets):,} giỏ cùng xuất hiện trong kỳ sau.','action':'Chọn vài cặp phù hợp nghiệp vụ để thử trưng bày/combo; dùng phương án có hit@3 tốt hơn sau kiểm tra.','owner':'Merchandising','measure':'A/B test giá trị/lãi giỏ; cùng xuất hiện không chứng minh tác động nhân quả.'},
        {'finding':f'Mô hình dự báo được chọn: {forecast["champion_selected_on_validation"]}; kiểm tra tương lai ở 4 mốc tuần.','evidence':f'WAPE của champion {float(ftest.loc[ftest.model==forecast["champion_selected_on_validation"],"WAPE"].iloc[0]):.2%}. Mô hình và baseline được báo cáo cùng nhau.','action':'Chạy quan sát song song trước khi dùng lập kế hoạch; ưu tiên nhóm hàng có sai số và bias ổn định.','owner':'Kế hoạch / BI','measure':'WAPE, MAE, bias theo nhóm; chưa dự báo số lượng SKU hay tồn kho.'},
        {'finding':f'Ưu tiên rà soát {int(actions.priority_top20.sum()):,} hộ ở top 20% điểm rủi ro.','evidence':f'Precision top20 trên các mốc test: {", ".join(f"{v:.1%}" for v in cs.precision_top20)}. Nhãn là không mua trong 28 ngày, không phải rời bỏ vĩnh viễn.','action':'CRM kiểm tra danh sách, loại trường hợp không phù hợp và thiết kế nhóm đối chứng; không tự gửi ưu đãi.','owner':'CRM','measure':'So với quy tắc recency; đo phản hồi tăng thêm bằng thử nghiệm.'},
        {'finding':f'{qa["unmatched_product_rows"]:,} dòng không nối danh mục; {qa["model_excluded_rows"]:,} dòng không đủ điều kiện mô hình mua dương.','evidence':f'Chênh raw–positive sales_value {qa["excluded_model_sales"]:,.2f} USD đã giữ riêng; không xóa khỏi đối soát.','action':'Đối chiếu master SKU và giải thích giao dịch ngoại lệ trước khi nối POS–ERP thật.','owner':'Data owner / IT / kế toán','measure':'Tỷ lệ join, độ đầy đủ, chênh tổng đối soát.'}
    ]
    save(pd.DataFrame(insights),out,'business_insights_actions')
    assumptions='''Dữ liệu gốc Complete Journey là một panel hộ mua hàng thường xuyên. Mọi tổng tiền theo cửa hàng chỉ thuộc panel, không đại diện toàn cửa hàng. `sales_value` là số tiền nhà bán lẻ nhận theo quy tắc coupon của nguồn, không phải lợi nhuận và không nhất thiết là tiền khách trả. Không lấy số lượng khác quy cách cộng chung thành nhu cầu. Khoảng dữ liệu mô hình kết thúc ngày '''+config['analysis_end']+'''; file có phần ngày tiếp theo đã loại khỏi kỳ. Dữ liệu lịch sử không phải dữ liệu đang cập nhật trực tiếp của doanh nghiệp.'''
    methods='''
### Dữ liệu và KPI

- Raw không đổi; enriched có kiểm tra many-to-one; unknown được giữ thành UNKNOWN để không mất tổng tiền. Giao dịch quantity<=0 hoặc sales_value<=0 giữ ở đối soát nhưng không đưa vào RFM mua dương, association và nhãn khách.
- Nguồn không có dòng giao dịch ngày 25/12/2017. Config khai báo rõ ngày này bằng 0 cho số tiền *quan sát trong panel*, chưa xác minh đóng cửa hay mất bản ghi. Các ngày vắng khác khiến pipeline dừng. Báo cáo kèm độ nhạy forecast loại cả tuần chứa ngày giả định; nhãn khách trong kỳ cũng có giới hạn quan sát này.
- Doanh số báo cáo và dự báo dùng raw sales_value trong kỳ. Dự báo tổng theo ngày được clip tối thiểu 0 ở mức ngành hàng; với bộ hiện tại kiểm tra không phát hiện tổng ngày âm. Bảng `quality.json` giải thích phần chênh với tập mua dương.
- Cohort là tháng đầu *xuất hiện trong file*, không khẳng định tháng thu hút khách thật. Tháng đầu bị giới hạn bởi đầu kỳ quan sát; ô tương lai để trống.
- ABC dùng doanh số mua dương, ngưỡng 80%/95%; phân nhóm nghiệp vụ theo recency 14/28 ngày và tứ phân vị sales/frequency là giả định có thể thay đổi. KMeans kiểm tra k=3..6 bằng silhouette, không dùng cluster ID như nhãn churn.
- Discount/campaign là mô tả quan sát. Redemption rate = số hộ được gán campaign có ít nhất một lần đổi coupon / số hộ được gán campaign, chỉ giữ redemption khớp assignment. Không nối coupon–product nhiều-nhiều trực tiếp vào POS. Không biết chính xác từng coupon Type A đã gửi cho từng hộ; không tính ROI/uplift nhân quả khi thiếu đối chứng và chi phí.

### Dự báo bán hàng

- Target trực tiếp: tổng sales_value của 7 ngày sau mỗi origin, theo 20 ngành hàng chọn ở 180 ngày đầu và OTHER; toàn bộ cửa hàng trong panel. Features chỉ dùng dữ liệu đến origin: lags, rolling 7/14/28/56, xu hướng, lịch và mã nhóm hàng. Target được chuẩn hóa bằng sales trung bình 28 ngày ×7; không đưa chiết khấu tương lai vào feature.
- Bốn ứng viên: Ridge, hai cấu hình histogram gradient boosting, ExtraTrees; so với lặp 7 ngày trước và trung bình 28 ngày. Chọn WAPE validation thấp nhất trên 3 mốc. Holdout cuối: 4 tuần không chồng nhau. Tại từng origin, chỉ train hàng có label kết thúc <= origin; dùng expanding history, không random split.
- WAPE=Σ|y−ŷ|/Σ|y|; MAE và RMSE bằng USD/nhóm/7 ngày; bias=Σ(ŷ−y)/Σ|y|. Tổng WAPE có thể bị OTHER chi phối; bảng theo nhóm kèm theo. Khoảng dự báo là dải residual tương đối lấy ở validation, báo coverage test thực nghiệm; không phải khoảng tin cậy đã hiệu chỉnh bảo đảm 90%.
- Model chọn dựa validation được giữ nguyên để test. Sau đánh giá, refit champion trên mọi nhãn đã hoàn thành để xuất dự báo tiếp theo. Chưa có lịch khuyến mãi tương lai, tồn kho, kỳ nhiều năm; không khẳng định tổng quát được mùa vụ hàng năm.

### Khả năng không mua trong 28 ngày

- Chỉ score hộ có giao dịch mua dương trong 90 ngày trước origin. Feature lịch sử recency, tenure quan sát, lượt mua, sales, đa dạng ngành 7/28/56/90 ngày, tỷ lệ discount. Không dùng demographic thiếu cho đa số hộ.
- Nhãn 1: không có giao dịch mua dương từ origin+1 đến origin+28; 0: có. Snapshot cách 28 ngày. Chọn LogisticRegression hoặc histogram gradient boosting hoặc quy tắc recency bằng average precision validation. Train chỉ dùng snapshot có label kết thúc trước hoặc tại thời điểm validation/test.
- Hai snapshot test tương lai; hộ có thể lặp xuyên thời gian vì đây là chấm điểm lại cùng khách. Không diễn giải số dòng như số khách độc lập. Model test được fit trước origin test đầu và không dùng nhãn test để chọn champion. Refit cuối chỉ gồm label đã chín.
- PR-AUC trong báo cáo là average precision (AP); ROC-AUC, Brier, precision/recall/lift top20 kèm theo. Quy tắc recency được scale thành score không có ý nghĩa xác suất hiệu chỉnh. Champion chưa calibration riêng, nên dùng để xếp hạng và kiểm tra, không dùng như xác suất tài chính.
- Nhóm nguy cơ cao có thể khó tác động. Mô hình không dự báo uplift, chi phí, CLV hay lợi nhuận tăng thêm. Ngưỡng 20% là công suất xử lý giả định; không phải ngưỡng tối ưu đã xác minh.

### Giỏ hàng

- Chia thời gian: train kết thúc 119 ngày trước cuối kỳ, validation 28 ngày tiếp theo, test 91 ngày cuối. Chọn top30 danh mục theo số giỏ train. Support/confidence/lift dùng tổng giỏ mua dương; chỉ giữ cặp >=100 giỏ train và lift>1. Score = confidence×log(lift). Chọn association hay popularity theo hit@3 validation trước khi xem test; xuất cả kết quả kỳ sau để thấy độ ổn định.
- Offline completion: trên giỏ test chứa >=2 danh mục top30, chọn 1 danh mục bằng hash cố định làm seed, ẩn danh mục còn lại; gợi ý top3 và so với popularity. Báo hit@3, recall@3, coverage. Chỉ đo hoàn thiện cùng giỏ trong nhóm đủ điều kiện, không đo mua thêm thật hay mua ở lần sau.
- Artifact recommender giữ quy tắc fit train và nhãn phương án thắng validation. Không tự triển khai ngoài ứng dụng; cần thử nghiệm mới trước khi phục vụ người dùng.

### Giám sát và vận hành

- Input hash + code/config hash xác định bản chạy; nếu không thay đổi thì skip. Một lock ngăn chạy đồng thời. Mỗi lần chạy có manifest, phiên bản thư viện, thời gian, log và bộ model riêng.
- Pipeline tự chạy ingest → quality → analytics → train/validate/test → score → monitoring → report. Lỗi ghi trạng thái failed, giữ báo cáo thành công trước đó; chỉ xuất latest sau khi mọi bước và kiểm tra đối soát hoàn thành.
- PSI so 28 ngày cuối với 28 ngày trước bằng bins từ giai đoạn trước; ngưỡng 0.2 là heuristic trong config, chỉ 28 điểm/nhóm và chưa loại mùa vụ. Cảnh báo cần điều tra, không tự quy lỗi model. Chưa có ground truth tương lai cho forecast/risk mới nhất.
- Pipeline local chưa có kết nối POS/ERP, kiểm soát truy cập hay hạ tầng cloud của doanh nghiệp. CSV adapter có schema rõ trong RUNBOOK; lịch chạy Windows được cung cấp bằng script cài đặt, chưa đăng ký chạy nền. Khi có nguồn thực, cần thêm watermark, backfill, SLA, mã đơn vị/thuế, kiểm soát phạm vi và cơ chế nhận nhãn thực tế.
'''
    decision_rows=[{'Bài toán':'Chất lượng/hợp nhất','Có thể chạy':'Có','Cần bổ sung':'Ánh xạ mã xuyên POS–ERP, định nghĩa tiền/thuế/hoàn và tổng đối soát.'},{'Bài toán':'CRM và giỏ hàng','Có thể chạy':'Offline demo','Cần bổ sung':'Mã khách bền vững, lịch tương tác, nhóm đối chứng, chi phí ưu đãi.'},{'Bài toán':'Dự báo nhóm hàng','Có thể chạy':'Offline demo 7 ngày','Cần bổ sung':'Lịch sử nhiều năm, toàn giao dịch, giá/khuyến mãi đã biết trước.'},{'Bài toán':'Tối ưu tồn kho/đặt hàng','Có thể chạy':'Chưa đủ dữ liệu','Cần bổ sung':'Tồn theo SKU–cửa hàng–ngày, lead time, MOQ, service target, đơn vị.'},{'Bài toán':'Lợi nhuận/ROI/CLV','Có thể chạy':'Chưa đủ dữ liệu','Cần bổ sung':'Giá vốn hiệu lực, chi phí, tài trợ, biên lợi nhuận và tác động nhân quả.'},{'Bài toán':'Hủy/cận hạn/NCC','Có thể chạy':'Chưa đủ dữ liệu','Cần bổ sung':'Lô/hạn dùng, kiểm kê, PO–nhận hàng và lịch hẹn.'}]
    md='# Phân tích bán lẻ và pipeline mô hình\n\n'+assumptions+'\n\n## Kết luận và hành động\n\n'+ '\n\n'.join(f'### {i+1}. {x["finding"]}\n\n{x["evidence"]}\n\n**Hành động:** {x["action"]} Chủ trì: {x["owner"]}. Đo bằng: {x["measure"]}' for i,x in enumerate(insights))
    md+='\n\n## Kiểm tra chất lượng\n\n'+md_table(pd.DataFrame([qa]).T.reset_index().rename(columns={'index':'metric',0:'value'}),40)
    md+='\n\n## Kết quả mô hình\n\n### Dự báo: validation\n\n'+md_table(read('forecast_validation_leaderboard'))+'\n\n### Dự báo: holdout\n\n'+md_table(ftest)+'\n\nDải residual: coverage thực nghiệm '+f'{forecast["interval_empirical_test_coverage"]:.1%}.'
    md+='\n\n### Dự báo: độ nhạy loại tuần chứa ngày không có bản ghi\n\n'+md_table(read('forecast_test_without_assumed_zero_week'))+'\n\nBảng holdout có cả challengers để kiểm tra; không chọn lại champion theo holdout. Dữ liệu 25/12/2017 bằng 0 là giả định quan sát, không chứng minh nhu cầu bằng 0.'
    md+='\n\n### Khách hàng: validation\n\n'+md_table(read('risk_validation_leaderboard'))+'\n\n### Khách hàng: holdout\n\n'+md_table(rtest)+'\n\n### Giỏ hàng: holdout\n\n'+md_table(pd.DataFrame([{'model':n,**association[n]} for n in ['association','popularity']]))
    md+='\n\n### Phân cụm\n\n'+md_table(read('cluster_selection'))+f'\n\nChọn k={analytics["clustering"]["selected_k"]}; ARI giữa hai seed {analytics["clustering"]["seed_stability_ARI"]:.3f}. Silhouette không chứng minh hiệu quả kinh doanh.'
    md+='\n\n## Phạm vi áp dụng doanh nghiệp\n\n'+md_table(pd.DataFrame(decision_rows))+ '\n\n## Thiết kế và phương pháp\n'+methods
    md+='\n\n## Nguồn và tái lập\n\n[Complete Journey](https://bradleyboehmke.github.io/completejourney/) và [từ điển dữ liệu](https://bradleyboehmke.github.io/completejourney/articles/completejourney.html); [mã nguồn bộ dữ liệu](https://github.com/bradleyboehmke/completejourney), package ghi CC0. [Scikit-learn ensemble](https://scikit-learn.org/stable/modules/ensemble.html) và [metrics](https://scikit-learn.org/stable/modules/model_evaluation.html). UCI đã kiểm tra ở báo cáo khảo sát trước và không nối vào bộ train này.\n\nRun ID: '+runmeta['run_id']+'. Xem run_manifest.json, models/model_registry.json và RUNBOOK.md để tái lập.\n'
    (out/'report.md').write_text(md,encoding='utf-8')
    charts=[]
    def chart(fig):
        fig.update_layout(template='plotly_white',font_family='Arial',height=400,margin=dict(l=55,r=25,t=60,b=55))
        charts.append(fig.to_html(full_html=False,include_plotlyjs=True if not charts else False))
    chart(px.line(monthly,x='month',y='sales',markers=True,title='Doanh số tháng của panel (USD)'))
    chart(px.bar(bridge,x='month',y=['basket_count_effect','basket_value_effect'],title='Phân rã biến động: số giỏ và giá trị giỏ',barmode='relative'))
    dept=read('department_monthly').groupby('department').sales.sum().nlargest(10).reset_index()
    chart(px.bar(dept,x='sales',y='department',orientation='h',title='Ngành hàng trong nhóm hộ quan sát'))
    chart(px.bar(seg,x='segment',y='sales',title='Doanh số mua dương theo nhóm khách nghiệp vụ'))
    cohorts=read('observed_cohorts').pivot(index='first_observed_month',columns='age_month',values='active_rate')
    chart(px.imshow(cohorts,aspect='auto',color_continuous_scale='Blues',range_color=[0,1],title='Tỷ lệ còn mua theo tháng đầu xuất hiện; ô tương lai để trống',labels={'color':'Tỷ lệ','x':'Tháng sau lần đầu quan sát','y':'Cohort quan sát'}))
    preds=read('forecast_test_predictions');preds=preds[preds.model==forecast['champion_selected_on_validation']]
    lines=preds.groupby('origin')[['actual','prediction']].sum().reset_index()
    chart(px.line(lines,x='origin',y=['actual','prediction'],markers=True,title='Dự báo: tổng các nhóm theo 4 tuần holdout (USD)'))
    chart(px.bar(ftest,x='model',y='WAPE',title='Sai số dự báo holdout: thấp hơn tốt hơn'))
    chart(px.bar(rtest,x='origin',y='precision_top20',color='model',barmode='group',title='Tỷ lệ không mua thực tế trong top 20% được chọn'))
    stable=rules.head(10).copy();stable['pair']=stable.A+' → '+stable.B
    chart(px.bar(stable,x='pair',y=['train_lift','test_lift'],barmode='group',title='Độ ổn định quy tắc giỏ hàng trên kỳ sau'))
    chart(px.bar(latest.sort_values('forecast',ascending=False),x='series',y='forecast',title='Dự báo 7 ngày tiếp theo, toàn panel (USD)'))
    if not campaign.empty:
        chart(px.bar(campaign,x='campaign_id',y='household_redemption_rate',color='campaign_type',title='Hộ có đổi coupon / hộ được gán campaign; chưa đo uplift'))
    cards=f'<div class="cards"><div><b>{qa["raw_sales"]:,.0f} USD</b><span>sales_value trong kỳ</span></div><div><b>{qa["households"]:,}</b><span>Hộ quan sát</span></div><div><b>{qa["basket_count"]:,}</b><span>Giỏ hàng</span></div><div><b>{forecast["champion_selected_on_validation"]}</b><span>Champion dự báo từ validation</span></div></div>'
    insight_html=''.join('<article><h3>'+html.escape(v['finding'])+'</h3><p>'+html.escape(v['evidence'])+'</p><p><b>Hành động:</b> '+html.escape(v['action'])+'</p><small>'+html.escape(v['owner']+' — '+v['measure'])+'</small></article>' for v in insights)
    tables='<h2>Kết quả kiểm tra tương lai</h2><h3>Dự báo</h3>'+ftest.round(4).to_html(index=False)+'<h3>Không mua trong 28 ngày</h3>'+rtest.round(4).to_html(index=False)+'<h3>Giỏ hàng</h3>'+pd.DataFrame([{'model':n,**association[n]} for n in ['association','popularity']]).round(4).to_html(index=False)
    tables+='<h3>Độ nhạy dự báo: loại tuần có ngày 25/12 không có bản ghi</h3>'+read('forecast_test_without_assumed_zero_week').round(4).to_html(index=False)+'<p>Champion chọn theo validation trước khi mở holdout. Các challenger cũng được train, lưu artifact và kiểm tra; không chọn lại bằng kết quả test.</p>'
    page='''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Phân tích bán lẻ</title><style>body{font:16px/1.6 Arial,sans-serif;color:#17324d;background:#f4f6fa;margin:0}main{max-width:1240px;margin:auto;padding:28px}h1{font-size:30px}h2{margin-top:38px}h3{font-size:19px}.note,article,.chart{background:white;border:1px solid #dfe5ed;border-radius:10px;padding:20px;margin:18px 0}.note{border-left:5px solid #de9b28}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px}.cards div{background:#17324d;color:white;padding:20px;border-radius:9px}.cards b{display:block;font-size:24px}.cards span{font-size:13px}small{color:#576a7e}table{border-collapse:collapse;width:100%;font-size:13px;background:white}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}th{background:#e5edf5}details{background:white;padding:18px;margin:20px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 Arial}a{color:#166a9e}@media(max-width:700px){main{padding:14px}table{display:block;overflow:auto}}</style><main>'''
    page+='<h1>Phân tích bán lẻ và hành động kinh doanh</h1><p>Kỳ quan sát đến '+config['analysis_end']+' · Dữ liệu công khai · Run '+html.escape(runmeta['run_id'])+'</p><div class="note">'+html.escape(assumptions)+'</div>'+cards+'<h2>Phát hiện và quyết định đề xuất</h2>'+insight_html+tables+'<h2>Khám phá kết quả</h2>'+''.join('<div class="chart">'+x+'</div>' for x in charts)+'<h2>Phạm vi triển khai</h2>'+pd.DataFrame(decision_rows).to_html(index=False)+'<details><summary>Phương pháp, giới hạn và vận hành</summary><pre>'+html.escape(methods)+'</pre></details><p>Nguồn: <a href="https://bradleyboehmke.github.io/completejourney/">Complete Journey</a> · <a href="https://bradleyboehmke.github.io/completejourney/articles/completejourney.html">Từ điển dữ liệu</a>. Biểu đồ tương tác hoạt động offline. Xem report.md, run_manifest.json và model_registry.json để kiểm tra.</p></main></html>'
    (out/'report.html').write_text(page,encoding='utf-8')
    return insights
