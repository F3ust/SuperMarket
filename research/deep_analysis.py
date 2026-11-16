"""Additional evidence and publication figures for the Vietnamese Word report."""
from pathlib import Path
import json,os
os.environ.setdefault('OMP_NUM_THREADS','2')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter,FuncFormatter
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from matplotlib.path import Path as MplPath
from sklearn.metrics import average_precision_score,precision_recall_curve,brier_score_loss

ROOT=Path(__file__).resolve().parents[1]
RUN=Path(json.loads((ROOT/'outputs/enterprise/latest.json').read_text(encoding='utf-8'))['path'])
OUT=ROOT/'outputs/word_report';ASSETS=OUT/'figures';ASSETS.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':12,'axes.labelsize':10,'figure.dpi':120,'savefig.dpi':220,'axes.titleweight':'bold'})
BLUE='#244D73';TEAL='#158483';ORANGE='#CD7D28';RED='#B94E48';GRAY='#738397'
def read(n):return pd.read_csv(RUN/f'{n}.csv')
def output(d,n):d.to_csv(OUT/f'{n}.csv',index=False,encoding='utf-8-sig')
def finish(fig,name):
    fig.tight_layout(pad=1.2);fig.savefig(ASSETS/f'{name}.png',bbox_inches='tight',facecolor='white');plt.close(fig)
def chartbar(data,x,y,name,title,percent=False):
    fig,ax=plt.subplots(figsize=(8.4,4));d=data.iloc[::-1]
    ax.barh(d[x],d[y],color=BLUE);ax.set_title(title);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    if percent:ax.xaxis.set_major_formatter(PercentFormatter(1))
    finish(fig,name)
def diagram(name,title,labels,subtitles):
    fig,ax=plt.subplots(figsize=(8.5,4.3));ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off');ax.set_title(title,pad=15)
    for i,(label,sub) in enumerate(zip(labels,subtitles)):
        col=i%3;row=i//3;x=.1+col*3.35;y=3.1-row*2.35
        box=FancyBboxPatch((x,y),3.1,1.55,boxstyle='round,pad=.08',facecolor='#EEF3F7',edgecolor=BLUE,linewidth=1)
        ax.add_patch(box);ax.text(x+1.55,y+1.08,label,ha='center',va='center',fontsize=11,weight='bold',color=BLUE);ax.text(x+1.55,y+.47,sub,ha='center',va='center',fontsize=9,linespacing=1.5)
        if col<2 and not (name=='25_chain_architecture' and row==0):ax.annotate('',xy=(x+3.32,y+.8),xytext=(x+3.14,y+.8),arrowprops={'arrowstyle':'->','color':BLUE,'lw':1.3})
    if name=='25_chain_architecture':
        # POS, ERP/WMS and shared dimensions are parallel inputs to the data warehouse.
        for cx in [1.65,5,8.35]:ax.plot([cx,cx],[3.0,2.7],color=BLUE,lw=1.1)
        ax.plot([1.65,8.35],[2.7,2.7],color=BLUE,lw=1.1)
        ax.annotate('',xy=(1.65,2.4),xytext=(1.65,2.7),arrowprops={'arrowstyle':'->','color':BLUE,'lw':1.1})
    else:
        connection=MplPath([(8.35,3.0),(8.35,2.7),(1.65,2.7),(1.65,2.4)],[MplPath.MOVETO,MplPath.LINETO,MplPath.LINETO,MplPath.LINETO])
        ax.add_patch(FancyArrowPatch(path=connection,arrowstyle='->',mutation_scale=11,color=BLUE,lw=1.1))
    finish(fig,name)

def main():
    j=pd.read_parquet(RUN/'transactions_enriched.parquet');pos=j[(j.quantity>0)&(j.sales_value>0)].copy();end=j.date.max()
    qa=json.loads((RUN/'quality.json').read_text(encoding='utf-8'));summary={}
    monthly=read('monthly_kpis');dept=read('department_monthly');abc=read('product_abc');customers=read('customer_segments');segments=read('segment_summary')
    # Revenue and exact contribution of individual departments to the final monthly change.
    last=dept.pivot(index='department',columns='month',values='sales').fillna(0)
    delta=(last[monthly.month.iloc[-1]]-last[monthly.month.iloc[-2]]).sort_values(ascending=False).reset_index(name='delta_sales')
    delta['share_of_net_change']=delta.delta_sales/(monthly.sales.iloc[-1]-monthly.sales.iloc[-2]);output(delta,'department_growth_contribution')
    fig,axes=plt.subplots(2,1,figsize=(8.5,6.0),sharex=True)
    axes[0].plot(monthly.month,monthly.sales/1000,'o-',color=BLUE);axes[0].set(ylabel='Nghìn USD',title='Số tiền bán quan sát theo tháng')
    axes[1].bar(monthly.month,monthly.baskets/1000,color=TEAL,label='Số giỏ');axes[1].set(ylabel='Nghìn giỏ');axes[1].tick_params(axis='x',rotation=40)
    ax2=axes[1].twinx();ax2.plot(monthly.month,monthly.aov,color=ORANGE,marker='s',label='Giá trị giỏ');ax2.set_ylabel('USD mỗi giỏ');ax2.spines['top'].set_visible(False)
    finish(fig,'01_revenue')
    bridge=read('sales_bridge').iloc[-1];fig,ax=plt.subplots(figsize=(8.3,3.7))
    vals=[monthly.sales.iloc[-2],bridge.basket_count_effect,bridge.basket_value_effect,monthly.sales.iloc[-1]];bottom=[0,vals[0],vals[0]+vals[1],0]
    bars=ax.bar(['Tháng 11','Hiệu ứng\nsố giỏ','Hiệu ứng\ngiá trị giỏ','Tháng 12'],np.array(vals)/1000,bottom=np.array(bottom)/1000,color=[BLUE,TEAL,ORANGE,BLUE])
    for b,v,base in zip(bars,vals,bottom):ax.text(b.get_x()+b.get_width()/2,(base+v)/1000+3,f'{v/1000:,.1f}',ha='center',fontsize=10)
    ax.set(ylabel='Nghìn USD',title='Phân rã mức tăng tháng 12 so với tháng 11');ax.set_ylim(0,470);finish(fig,'02_bridge')
    chartbar(delta.head(8),'department','delta_sales','03_department_delta','Các ngành đóng góp nhiều nhất vào mức tăng cuối kỳ')
    depts=dept.groupby('department').sales.sum().sort_values(ascending=False).head(8).reset_index();depts['share']=depts.sales/qa['raw_sales']
    chartbar(depts,'department','share','04_department_share','Tỷ trọng số tiền bán theo ngành',True)
    fig,ax=plt.subplots(figsize=(8.3,3.8));x=np.arange(1,len(abc)+1)/len(abc);ax.plot(x,abc.cumulative_share,color=BLUE);ax.axhline(.8,color=ORANGE,ls='--');ax.axhline(.95,color=GRAY,ls=':');ax.set(xlabel='Tỷ lệ SKU đã xếp giảm dần theo doanh số',ylabel='Tỷ lệ doanh số tích lũy',title='Mức tập trung doanh số theo SKU');ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1));finish(fig,'05_abc')
    ordered=customers.sort_values('sales');cum=ordered.sales.cumsum()/ordered.sales.sum();fig,ax=plt.subplots(figsize=(8.2,3.9));ax.plot(np.arange(1,len(cum)+1)/len(cum),cum,color=TEAL,label='Phân bố quan sát');ax.plot([0,1],[0,1],ls='--',color=GRAY,label='Phân bố đồng đều');ax.set(xlabel='Tỷ lệ hộ từ giá trị thấp đến cao',ylabel='Tỷ lệ doanh số tích lũy',title='Mức tập trung giá trị mua giữa các hộ');ax.legend(frameon=False);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1));finish(fig,'06_customer_concentration')
    summary['gini_observed_sales']=float(1-2*np.trapezoid(np.r_[0,cum],np.linspace(0,1,len(cum)+1)))
    fig,axes=plt.subplots(1,2,figsize=(8.5,4));short={'Giá trị cao, cần kiểm tra giảm mua':'Giá trị cao giảm mua','Khách hàng chủ lực':'Chủ lực','Mới xuất hiện trong dữ liệu':'Mới quan sát','Mua thường xuyên':'Thường xuyên','Nhóm còn lại':'Còn lại'}
    axes[0].barh(segments.segment.map(short),segments.households,color=BLUE);axes[0].set_title('Quy mô nhóm hộ');axes[1].barh(segments.segment.map(short),segments.sales_share,color=TEAL);axes[1].set_title('Tỷ trọng doanh số mua dương');axes[1].xaxis.set_major_formatter(PercentFormatter(1));finish(fig,'07_segments')
    cohort=read('observed_cohorts').pivot(index='first_observed_month',columns='age_month',values='active_rate')
    fig,ax=plt.subplots(figsize=(8.2,4.5));im=ax.imshow(cohort,vmin=0,vmax=1,cmap='Blues',aspect='auto');ax.set_xticks(range(len(cohort.columns)),cohort.columns);ax.set_yticks(range(len(cohort)),cohort.index);ax.set(xlabel='Số tháng từ tháng đầu xuất hiện',ylabel='Tháng đầu quan sát',title='Hoạt động giao dịch theo nhóm tháng đầu xuất hiện');fig.colorbar(im,ax=ax,format=PercentFormatter(1),label='Tỷ lệ hộ có giao dịch');finish(fig,'08_cohorts')
    # Cross-store purchasing, with active-quarter restriction for dominant-store comparison.
    store_count=pos.groupby('household_id').store_id.nunique();hist=store_count.value_counts().sort_index().reset_index();hist.columns=['stores','households'];output(hist,'cross_store_distribution')
    quarters=[]
    for q,sub in pos.groupby(pos.date.dt.quarter):
        s=sub.groupby(['household_id','store_id']).sales_value.sum().reset_index();s=s.sort_values(['household_id','sales_value','store_id'],ascending=[True,False,True]).drop_duplicates('household_id');s['quarter']=q;quarters.append(s[['household_id','store_id','quarter']])
    dom=pd.concat(quarters).pivot(index='household_id',columns='quarter',values='store_id');both=dom[[3,4]].dropna();switched=both[3]!=both[4]
    summary['cross_store']={'multiple_store_households':int((store_count>1).sum()),'share_multiple_stores':float((store_count>1).mean()),'median_stores':float(store_count.median()),'q3_q4_comparable_households':len(both),'q3_q4_dominant_store_changed':int(switched.sum()),'q3_q4_dominant_store_changed_share':float(switched.mean())}
    bins=pd.cut(store_count,bins=[0,1,2,4,9,np.inf],labels=['1','2','3 đến 4','5 đến 9','10 trở lên']).value_counts(sort=False)
    fig,ax=plt.subplots(figsize=(8,3.5));ax.bar(bins.index.astype(str),bins.values,color=BLUE);ax.set(xlabel='Số cửa hàng có mua trong kỳ',ylabel='Số hộ',title='Mua xuyên cửa hàng trong panel');finish(fig,'09_cross_store')
    # Non-merchandise taxonomy investigation, does not mutate any earlier model results.
    special=pos[pos.product_category.eq('COUPON/MISC ITEMS')]
    special_types=special.groupby(['department','product_type'],dropna=False).sales_value.sum().sort_values(ascending=False).reset_index(name='sales');output(special_types,'coupon_misc_taxonomy')
    summary['taxonomy_special_sales']=float(special.sales_value.sum());summary['taxonomy_special_top']=special_types.head(8).to_dict('records')
    # Discount associations only; control product-store where both statuses occur.
    pos['discounted']=(pos[['retail_disc','coupon_disc','coupon_match_disc']]!=0).any(axis=1)
    promo=pos.groupby('discounted').agg(lines=('product_id','size'),sales=('sales_value','sum'),retail_disc=('retail_disc','sum'),manufacturer_coupon=('coupon_disc','sum')).reset_index();output(promo,'promo_composition')
    pairs=pos.groupby(['product_id','store_id','discounted']).agg(line_mean_sales=('sales_value','mean'),lines=('sales_value','size')).reset_index();pv=pairs.pivot(index=['product_id','store_id'],columns='discounted',values='line_mean_sales').dropna();pv['ratio']=pv[True]/pv[False]
    summary['discount_observational']={'positive_line_discount_share':float(pos.discounted.mean()),'paired_product_store_count':len(pv),'median_discounted_to_nondiscounted_line_value':float(pv.ratio.median()),'ratio_q25':float(pv.ratio.quantile(.25)),'ratio_q75':float(pv.ratio.quantile(.75))}
    fig,ax=plt.subplots(figsize=(8,3.6));ax.hist(np.log2(pv.ratio.clip(.125,8)),bins=35,color=TEAL);ax.axvline(0,color=GRAY,ls='--');ax.set(xlabel='Log cơ số 2 của tỷ lệ tiền mỗi dòng có giảm giá so với không giảm',ylabel='Số cặp SKU và cửa hàng',title='Liên hệ quan sát trong cùng SKU và cửa hàng');finish(fig,'10_discount')
    campaigns=read('campaign_redemption');campaigns['lo']=0.;campaigns['hi']=0.
    for i,row in campaigns.iterrows():
        n=row.assigned_households;p=row.household_redemption_rate;z=1.96;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;campaigns.loc[i,['lo','hi']]=[center-half,center+half]
    output(campaigns,'campaign_intervals');eligible=campaigns[campaigns.window_fully_observed & (campaigns.assigned_households>=100)].sort_values('household_redemption_rate',ascending=False).head(10)
    fig,ax=plt.subplots(figsize=(8.1,4));yy=np.arange(len(eligible));ax.errorbar(eligible.household_redemption_rate,yy,xerr=np.vstack([eligible.household_redemption_rate-eligible.lo,eligible.hi-eligible.household_redemption_rate]),fmt='o',color=BLUE,capsize=3);ax.set_yticks(yy,['Chiến dịch '+str(v) for v in eligible.campaign_id]);ax.invert_yaxis();ax.xaxis.set_major_formatter(PercentFormatter(1));ax.set(title='Tỷ lệ hộ đổi coupon và khoảng Wilson 95 phần trăm',xlabel='Chỉ chiến dịch đủ cửa sổ quan sát và ít nhất 100 hộ được gán');finish(fig,'11_campaigns')
    # Forecast evaluation decomposition, preserving the preselected champion.
    fp=read('forecast_test_predictions');champ=fp[fp.model=='mean_28_days'].copy();champ['abs_error']=(champ.actual-champ.prediction).abs()
    err=champ.groupby('series').agg(actual=('actual','sum'),absolute_error=('abs_error','sum'),predicted=('prediction','sum')).reset_index();err['wape']=err.absolute_error/err.actual;err['error_share']=err.absolute_error/err.absolute_error.sum();err['actual_share']=err.actual/err.actual.sum();err['bias']=(err.predicted-err.actual)/err.actual;err=err.sort_values('absolute_error',ascending=False);output(err,'forecast_error_contribution')
    origin=champ.groupby('origin').agg(actual=('actual','sum'),predicted=('prediction','sum'),absolute_error=('abs_error','sum')).reset_index();origin['series_wape']=origin.absolute_error/origin.actual;output(origin,'forecast_error_by_origin')
    summary['forecast']={'OTHER_actual_share':float(err.loc[err.series.eq('OTHER'),'actual_share'].iloc[0]),'OTHER_error_share':float(err.loc[err.series.eq('OTHER'),'error_share'].iloc[0]),'macro_series_wape':float(err.wape.mean()),'median_series_wape':float(err.wape.median()),'interval_test_coverage':json.loads((RUN/'forecast_summary.json').read_text(encoding='utf-8'))['interval_empirical_test_coverage'],'test_origin_metrics':origin.to_dict('records')}
    fig,ax=plt.subplots(figsize=(8.3,4));v=read('forecast_validation_leaderboard')[['model','WAPE']].rename(columns={'WAPE':'Validation'});v=v.merge(read('forecast_test_metrics')[['model','WAPE']].rename(columns={'WAPE':'Test'}),on='model');x=np.arange(len(v));ax.bar(x-.18,v.Validation,.36,label='Validation',color=TEAL);ax.bar(x+.18,v.Test,.36,label='Test',color=BLUE);ax.set_xticks(x,v.model,rotation=22,ha='right');ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set(title='WAPE của sáu phương án trên hai giai đoạn',ylabel='Thấp hơn tốt hơn');ax.legend(frameon=False);finish(fig,'12_forecast_models')
    fig,axes=plt.subplots(1,2,figsize=(8.5,4));axes[0].plot(origin.origin,origin.actual/1000,'o-',label='Thực tế',color=BLUE);axes[0].plot(origin.origin,origin.predicted/1000,'s--',label='Dự báo',color=ORANGE);axes[0].set(ylabel='Nghìn USD',title='Tổng các nhóm trong mỗi tuần');axes[0].tick_params(axis='x',rotation=35);axes[0].legend(frameon=False);axes[1].bar(origin.origin,origin.series_wape,color=TEAL);axes[1].set_title('WAPE theo mốc kiểm tra');axes[1].tick_params(axis='x',rotation=35);axes[1].yaxis.set_major_formatter(PercentFormatter(1));finish(fig,'13_forecast_weeks')
    chartbar(err.head(8),'series','error_share','14_forecast_errors','Tỷ trọng sai số tuyệt đối theo nhóm',True)
    series_metrics=read('forecast_series_metrics').sort_values('WAPE',ascending=False).head(10);chartbar(series_metrics,'series','WAPE','15_forecast_wape','Mười nhóm có WAPE cao nhất trong bốn tuần test',True)
    intervals=read('forecast_test_intervals');fig,ax=plt.subplots(figsize=(8.2,4));ii=intervals[intervals.series.eq('OTHER')];xx=np.arange(len(ii));ax.fill_between(xx,ii.lower,ii.upper,color=BLUE,alpha=.18,label='Dải residual heuristic');ax.plot(xx,ii.prediction,'s--',color=BLUE,label='Dự báo');ax.plot(xx,ii.actual,'o-',color=ORANGE,label='Thực tế');ax.set_xticks(xx,ii.origin,rotation=25);ax.set(ylabel='USD mỗi tuần',title='Dải dự báo minh họa cho nhóm OTHER');ax.legend(frameon=False,fontsize=9);finish(fig,'16_forecast_band')
    # Customer model, paired holdout and household-cluster bootstrap.
    risk=read('risk_test_predictions');risk['household_id']=risk.household_id.astype(str)
    original_order=risk[['household_id','origin']].drop_duplicates().reset_index(drop=True).reset_index(names='row_order')
    rs=risk.pivot(index=['household_id','origin','actual'],columns='model',values='score').reset_index().merge(original_order,on=['household_id','origin'],validate='one_to_one').sort_values('row_order')
    y=rs.actual.astype(int).to_numpy();ml=rs.hist_gradient.to_numpy();baseline=rs.recency_rule.to_numpy()
    fig,ax=plt.subplots(figsize=(8.1,4));
    for label,p,color in [('Gradient boosting',ml,BLUE),('Quy tắc recency',baseline,ORANGE)]:
        precision,recall,_=precision_recall_curve(y,p);ax.plot(recall,precision,label=f'{label}   AP {average_precision_score(y,p):.3f}',color=color)
    ax.axhline(y.mean(),color=GRAY,ls='--',label=f'Tỷ lệ nhãn dương {y.mean():.1%}');ax.set(xlabel='Recall',ylabel='Precision',title='Precision và recall trên hai snapshot test gộp');ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1));ax.legend(frameon=False,fontsize=9);finish(fig,'17_risk_pr')
    capacity=[]
    for origin,g in rs.groupby('origin'):
        for name in ['hist_gradient','recency_rule']:
            for fraction in [.05,.1,.2,.3,.5]:
                n=int(np.ceil(len(g)*fraction));chosen=g.sort_values(name,ascending=False,kind='stable').head(n);tp=int(chosen.actual.sum());capacity.append({'origin':origin,'model':name,'fraction':fraction,'selected':n,'true_positive':tp,'false_positive':n-tp,'precision':tp/n,'recall':tp/g.actual.sum(),'lift':(tp/n)/g.actual.mean()})
    capacity=pd.DataFrame(capacity);output(capacity,'risk_capacity')
    fig,axes=plt.subplots(1,2,figsize=(8.4,3.9));
    for name,color,label in [('hist_gradient',BLUE,'Gradient boosting'),('recency_rule',ORANGE,'Recency')]:
        q=capacity[capacity.model.eq(name)].groupby('fraction')[['precision','recall']].mean();axes[0].plot(q.index,q.precision,'o-',color=color,label=label);axes[1].plot(q.index,q.recall,'o-',color=color,label=label)
    for ax,title in zip(axes,['Precision theo công suất chọn','Recall theo công suất chọn']):ax.set(title=title,xlabel='Tỷ lệ hộ được chọn');ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1));ax.legend(frameon=False,fontsize=9)
    finish(fig,'18_risk_capacity')
    rs['decile']=pd.qcut(rs.hist_gradient.rank(method='first'),10,labels=False)
    calibration=rs.groupby('decile').agg(predicted=('hist_gradient','mean'),observed=('actual','mean'),n=('actual','size')).reset_index();output(calibration,'risk_calibration')
    fig,ax=plt.subplots(figsize=(7.9,3.8));ax.plot([0,1],[0,1],ls='--',color=GRAY);ax.plot(calibration.predicted,calibration.observed,'o-',color=BLUE);ax.set(xlabel='Điểm dự báo trung bình theo decile',ylabel='Tỷ lệ không mua thực tế',title='Kiểm tra độ phù hợp của điểm rủi ro theo decile');ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1));finish(fig,'19_risk_calibration')
    importance=read('risk_feature_importance').head(8);translate={'visits_90':'Lượt mua trong 90 ngày','visits_28':'Lượt mua trong 28 ngày','recency':'Số ngày từ lần mua cuối','categories_90':'Số nhóm hàng trong 90 ngày','categories_56':'Số nhóm hàng trong 56 ngày','observed_tenure':'Số ngày từ lần đầu quan sát','sales_28':'Giá trị mua trong 28 ngày','discount_line_share_90':'Tỷ lệ dòng giảm giá trong 90 ngày'};importance['label']=importance.feature.map(translate).fillna(importance.feature)
    chartbar(importance,'label','importance_mean','20_risk_importance','Mức giảm AP khi hoán vị đặc trưng trên validation')
    rng=np.random.default_rng(42);ids=rs.household_id.unique();groups={v:np.flatnonzero(rs.household_id.to_numpy()==v) for v in ids};boot=[]
    def top_precision(labels,score):return labels[np.argsort(-score,kind='stable')[:int(np.ceil(len(labels)*.2))]].mean()
    for _ in range(1000):
        ix=np.concatenate([groups[v] for v in rng.choice(ids,len(ids),replace=True)]);yy=y[ix]
        boot.append([average_precision_score(yy,ml[ix])-average_precision_score(yy,baseline[ix]),top_precision(yy,ml[ix])-top_precision(yy,baseline[ix])])
    boot=np.array(boot);summary['risk_bootstrap']={'method':'1000 household-cluster bootstrap replications, retaining both snapshots for each sampled household; percentile 95% intervals conditional on two observed calendar origins','AP_difference':float(average_precision_score(y,ml)-average_precision_score(y,baseline)),'AP_difference_CI':np.quantile(boot[:,0],[.025,.975]).tolist(),'precision_top20_difference':float(top_precision(y,ml)-top_precision(y,baseline)),'precision_top20_difference_CI':np.quantile(boot[:,1],[.025,.975]).tolist(),'pooled_ML_AP':float(average_precision_score(y,ml)),'pooled_baseline_AP':float(average_precision_score(y,baseline)),'pooled_prevalence':float(y.mean()),'pooled_Brier_ML':float(brier_score_loss(y,ml)),'pooled_Brier_baseline':float(brier_score_loss(y,baseline))}
    fig,ax=plt.subplots(figsize=(8,3.6));ax.hist(boot[:,1]*100,bins=35,color=TEAL);ax.axvline(0,color=RED,ls='--');ax.set(xlabel='Chênh lệch precision top 20 tính bằng điểm phần trăm',ylabel='Số lần lấy mẫu',title='Độ bất định khi lấy mẫu lại theo hộ');finish(fig,'21_risk_bootstrap')
    am=json.loads((RUN/'association_metrics.json').read_text(encoding='utf-8'));vals=[am['association']['hit_at_3'],am['popularity']['hit_at_3']];fig,ax=plt.subplots(figsize=(7.8,3.3));bars=ax.bar(['Association','Hàng phổ biến'],vals,color=[ORANGE,BLUE]);ax.bar_label(bars,labels=[f'{v:.1%}' for v in vals],padding=4);ax.set_ylim(0,.8);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set(title='Hit ở ba gợi ý trên giỏ test được che bớt danh mục',ylabel='Tỷ lệ giỏ có ít nhất một gợi ý đúng');finish(fig,'22_basket_models')
    rules=read('association_rules').head(6);rules['label']=rules.A.str.slice(0,20)+' → '+rules.B.str.slice(0,20)
    fig,ax=plt.subplots(figsize=(8.4,4));yy=np.arange(len(rules));ax.barh(yy-.17,rules.train_lift,.34,color=TEAL,label='Train');ax.barh(yy+.17,rules.test_lift,.34,color=BLUE,label='Test');ax.set_yticks(yy,rules.label,fontsize=9);ax.invert_yaxis();ax.set(title='Độ ổn định của các quy tắc có điểm train cao nhất',xlabel='Lift');ax.legend(frameon=False);finish(fig,'23_basket_rules')
    diagram('24_pipeline','Luồng dữ liệu và mô hình đã thực hiện',['Nguồn dữ liệu','Kiểm tra và chuẩn hóa','Phân tích kinh doanh','Huấn luyện và kiểm tra','Chấm điểm và theo dõi','Công bố kết quả'],['RDS hoặc CSV\nManifest và mã kiểm tra','Schema và khóa nối\nĐối soát và ngoại lệ','KPI và phân nhóm\nGiỏ hàng và coupon','Tách theo thời gian\nSo baseline và chọn model','Dự báo và danh sách CRM\nTheo dõi phân bố','Word và báo cáo HTML\nSQL và Parquet'])
    diagram('25_chain_architecture','Mô hình dữ liệu đề xuất cho chuỗi bán lẻ',['POS và thương mại số','ERP và WMS','Danh mục dùng chung','Kho dữ liệu hợp nhất','Mô hình phục vụ quyết định','Kiểm soát vận hành'],['Chi tiết dòng hóa đơn\nKhách hàng và cửa hàng','Nhập xuất tồn và PO\nGiá vốn và điều chuyển','SKU và đơn vị quy đổi\nMapping có ngày hiệu lực','Raw bất biến và lịch batch\nBảng nghiệp vụ đã đối soát','Cửa hàng và SKU\nCRM xuyên chuỗi','Phân quyền và nhật ký\nDuyệt hành động và rollback'])
    diagram('26_poc','Các bước triển khai PoC với dữ liệu doanh nghiệp',['Chốt quyết định và KPI','Kiểm tra mẫu dữ liệu','Đối soát liên hệ thống','Backtest theo thời gian','Thử nghiệm nghiệp vụ','Vận hành có giám sát'],['Người sử dụng và công suất\nBaseline và tiêu chí đạt','2 đến 4 tuần mẫu\nKhóa và định nghĩa tiền','POS ERP và WMS\nGiải thích từng chênh lệch','Train validation test\nCửa hàng và SKU mới','Nhóm đối chứng phù hợp\nĐo lợi ích sau chi phí','SLA và dữ liệu đến muộn\nChịu trách nhiệm và khôi phục'])
    summary.update({'run_id':RUN.name,'data_end':str(end.date()),'department_growth':delta.head(8).to_dict('records'),'segment_summary':segments.to_dict('records'),'monthly_kpis':monthly.to_dict('records'),'source_signature':json.loads((RUN/'run_manifest.json').read_text(encoding='utf-8'))['signature']})
    (OUT/'deep_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print(json.dumps({'status':'success','figures':len(list(ASSETS.glob('*.png'))),'summary_file':str(OUT/'deep_summary.json')}))

if __name__=='__main__':main()
