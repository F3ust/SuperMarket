# Phân tích bán lẻ và pipeline mô hình

Dữ liệu gốc Complete Journey là một panel hộ mua hàng thường xuyên. Mọi tổng tiền theo cửa hàng chỉ thuộc panel, không đại diện toàn cửa hàng. `sales_value` là số tiền nhà bán lẻ nhận theo quy tắc coupon của nguồn, không phải lợi nhuận và không nhất thiết là tiền khách trả. Không lấy số lượng khác quy cách cộng chung thành nhu cầu. Khoảng dữ liệu mô hình kết thúc ngày 2017-12-31; file có phần ngày tiếp theo đã loại khỏi kỳ. Dữ liệu lịch sử không phải dữ liệu đang cập nhật trực tiếp của doanh nghiệp.

## Kết luận và hành động

### 1. Tháng 2017-12: sales_value 421,882.29 USD, thay đổi +9.4% so với 2017-11.

Chênh lệch 36,330.04 USD = hiệu ứng số giỏ 11,696.78 + giá trị giỏ 24,633.26. Phân rã đối xứng, đã đối soát.

**Hành động:** Kiểm tra ngành hàng đóng góp và số hộ mua; đối chiếu lịch chương trình trước khi quy nguyên nhân. Chủ trì: Vận hành / ngành hàng. Đo bằng: Số giỏ, giá trị giỏ; không suy diễn lợi nhuận.

### 2. 20% hộ có giá trị mua cao nhất đóng góp 54.6% doanh số mua dương.

Xếp hạng tổng sales_value dương trong kỳ; không tính lãi gộp hay CLV.

**Hành động:** Lập nhóm chăm sóc giá trị cao, xem thêm thay đổi hành vi và thử nghiệm có đối chứng. Chủ trì: CRM. Đo bằng: Incremental retention và lãi sau chi phí khi có dữ liệu giá vốn.

### 3. 10,899/68,183 SKU thuộc nhóm ABC-A theo ngưỡng 80% doanh số mua dương.

Ngưỡng tích lũy 80%/95%, gồm SKU vượt ngưỡng; kết quả phụ thuộc panel khách đang quan sát.

**Hành động:** Dùng làm danh sách đối chiếu danh mục và mức sẵn hàng; chưa đặt hàng theo ABC khi thiếu tồn kho. Chủ trì: Ngành hàng / cung ứng. Đo bằng: Doanh số và tỷ lệ có hàng; cần số liệu tồn cho service level.

### 4. Quy tắc mua cùng có điểm xếp hạng cao nhất: DELI MEATS → BAKED BREAD/BUNS/ROLLS.

Lift train 2.91; lift kỳ sau 2.95; 1,478 giỏ cùng xuất hiện trong kỳ sau.

**Hành động:** Chọn vài cặp phù hợp nghiệp vụ để thử trưng bày/combo; dùng phương án có hit@3 tốt hơn sau kiểm tra. Chủ trì: Merchandising. Đo bằng: A/B test giá trị/lãi giỏ; cùng xuất hiện không chứng minh tác động nhân quả.

### 5. Mô hình dự báo được chọn: mean_28_days; kiểm tra tương lai ở 4 mốc tuần.

WAPE của champion 14.99%. Mô hình và baseline được báo cáo cùng nhau.

**Hành động:** Chạy quan sát song song trước khi dùng lập kế hoạch; ưu tiên nhóm hàng có sai số và bias ổn định. Chủ trì: Kế hoạch / BI. Đo bằng: WAPE, MAE, bias theo nhóm; chưa dự báo số lượng SKU hay tồn kho.

### 6. Ưu tiên rà soát 465 hộ ở top 20% điểm rủi ro.

Precision top20 trên các mốc test: 43.4%, 45.3%. Nhãn là không mua trong 28 ngày, không phải rời bỏ vĩnh viễn.

**Hành động:** CRM kiểm tra danh sách, loại trường hợp không phù hợp và thiết kế nhóm đối chứng; không tự gửi ưu đãi. Chủ trì: CRM. Đo bằng: So với quy tắc recency; đo phản hồi tăng thêm bằng thử nghiệm.

### 7. 4,833 dòng không nối danh mục; 11,266 dòng không đủ điều kiện mô hình mua dương.

Chênh raw–positive sales_value 12.52 USD đã giữ riêng; không xóa khỏi đối soát.

**Hành động:** Đối chiếu master SKU và giải thích giao dịch ngoại lệ trước khi nối POS–ERP thật. Chủ trì: Data owner / IT / kế toán. Đo bằng: Tỷ lệ join, độ đầy đủ, chênh tổng đối soát.

## Kiểm tra chất lượng

| metric | value |
|---|---|
| source_rows | 1469307 |
| in_scope_rows | 1468773 |
| out_of_scope_rows | 534 |
| start | 2017-01-01 |
| end | 2017-12-31 |
| raw_sales | 4594146.32 |
| positive_sales | 4594133.800000001 |
| excluded_model_sales | 12.52000000000001 |
| model_excluded_rows | 11266 |
| unmatched_product_rows | 4833 |
| unmatched_product_rate | 0.0032905016636335226 |
| unknown_category_rows | 7041 |
| basket_count | 155762 |
| households | 2469 |
| stores | 457 |
| numeric_gate | passed |
| join_gate | passed |
| duplicates | 0 |
| calendar_missing_days | 1 |
| zero_transaction_dates_assumption | ['2017-12-25'] |
| calendar_note | Explicitly configured dates treated as zero observed panel receipts only, not proof of zero customer demand or store closure. |

## Kết quả mô hình

### Dự báo: validation

| model | WAPE | MAE | RMSE | bias |
|---|---|---|---|---|
| mean_28_days | 0.0539 | 219.24 | 453.52 | 0.0131 |
| ridge | 0.0602 | 245.18 | 553.73 | 0.0385 |
| extra_trees | 0.0695 | 282.98 | 653.70 | 0.0434 |
| hist_gradient_small | 0.0820 | 333.69 | 766.74 | 0.0581 |
| hist_gradient_medium | 0.0831 | 338.08 | 720.99 | 0.0632 |
| last_7_days | 0.0986 | 401.38 | 1,015.96 | 0.0819 |

### Dự báo: holdout

| model | WAPE | MAE | RMSE | bias |
|---|---|---|---|---|
| mean_28_days | 0.1499 | 668.84 | 2,196.42 | -0.0148 |
| hist_gradient_small | 0.1886 | 841.49 | 2,745.83 | 0.0344 |
| hist_gradient_medium | 0.1907 | 850.95 | 2,768.28 | 0.0378 |
| ridge | 0.1929 | 860.40 | 2,888.24 | -0.1022 |
| extra_trees | 0.2040 | 910.09 | 2,869.03 | 0.0406 |
| last_7_days | 0.2108 | 940.31 | 3,376.10 | 0.0295 |

Dải residual: coverage thực nghiệm 61.9%.

### Dự báo: độ nhạy loại tuần chứa ngày không có bản ghi

| model | WAPE | MAE | RMSE | bias | series_origin_rows |
|---|---|---|---|---|---|
| extra_trees | 0.1522 | 714.63 | 2,351.93 | -0.0505 | 63.00 |
| hist_gradient_medium | 0.1342 | 630.26 | 2,119.90 | -0.0556 | 63.00 |
| hist_gradient_small | 0.1363 | 640.07 | 2,182.89 | -0.0552 | 63.00 |
| last_7_days | 0.1388 | 651.86 | 2,416.73 | -0.0850 | 63.00 |
| mean_28_days | 0.1235 | 580.02 | 2,103.27 | -0.0780 | 63.00 |
| ridge | 0.1941 | 911.14 | 3,250.19 | -0.1737 | 63.00 |

Bảng holdout có cả challengers để kiểm tra; không chọn lại champion theo holdout. Dữ liệu 25/12/2017 bằng 0 là giả định quan sát, không chứng minh nhu cầu bằng 0.

### Khách hàng: validation

| model | PR_AUC_AP | ROC_AUC | Brier | prevalence | precision_top20 | recall_top20 | lift_top20 | n |
|---|---|---|---|---|---|---|---|---|
| hist_gradient | 0.5088 | 0.8638 | 0.0966 | 0.1517 | 0.4644 | 0.6125 | 3.0614 | 2,314.00 |
| logistic | 0.4914 | 0.8577 | 0.0987 | 0.1517 | 0.4492 | 0.5926 | 2.9617 | 2,314.00 |
| recency_rule | 0.4234 | 0.7950 | 0.1092 | 0.1517 | 0.4233 | 0.5584 | 2.7908 | 2,314.00 |

### Khách hàng: holdout

| origin | model | PR_AUC_AP | ROC_AUC | Brier | prevalence | precision_top20 | recall_top20 | lift_top20 | n |
|---|---|---|---|---|---|---|---|---|---|
| 2017-11-05 | hist_gradient | 0.4643 | 0.8525 | 0.0961 | 0.1450 | 0.4338 | 0.5988 | 2.9927 | 2,304.00 |
| 2017-11-05 | recency_rule | 0.3777 | 0.7557 | 0.1105 | 0.1450 | 0.3666 | 0.5060 | 2.5288 | 2,304.00 |
| 2017-12-03 | hist_gradient | 0.4519 | 0.8511 | 0.1001 | 0.1510 | 0.4526 | 0.6000 | 2.9974 | 2,318.00 |
| 2017-12-03 | recency_rule | 0.3848 | 0.7702 | 0.1129 | 0.1510 | 0.3815 | 0.5057 | 2.5264 | 2,318.00 |

### Giỏ hàng: holdout

| model | hit_at_3 | recall_at_3 | evaluated_baskets |
|---|---|---|---|
| association | 0.6344 | 0.2589 | 20,461.00 |
| popularity | 0.6629 | 0.2807 | 20,461.00 |

### Phân cụm

| k | silhouette |
|---|---|
| 3.0000 | 0.3681 |
| 4.0000 | 0.2852 |
| 5.0000 | 0.3168 |
| 6.0000 | 0.2939 |

Chọn k=3; ARI giữa hai seed 0.978. Silhouette không chứng minh hiệu quả kinh doanh.

## Phạm vi áp dụng doanh nghiệp

| Bài toán | Có thể chạy | Cần bổ sung |
|---|---|---|
| Chất lượng/hợp nhất | Có | Ánh xạ mã xuyên POS–ERP, định nghĩa tiền/thuế/hoàn và tổng đối soát. |
| CRM và giỏ hàng | Offline demo | Mã khách bền vững, lịch tương tác, nhóm đối chứng, chi phí ưu đãi. |
| Dự báo nhóm hàng | Offline demo 7 ngày | Lịch sử nhiều năm, toàn giao dịch, giá/khuyến mãi đã biết trước. |
| Tối ưu tồn kho/đặt hàng | Chưa đủ dữ liệu | Tồn theo SKU–cửa hàng–ngày, lead time, MOQ, service target, đơn vị. |
| Lợi nhuận/ROI/CLV | Chưa đủ dữ liệu | Giá vốn hiệu lực, chi phí, tài trợ, biên lợi nhuận và tác động nhân quả. |
| Hủy/cận hạn/NCC | Chưa đủ dữ liệu | Lô/hạn dùng, kiểm kê, PO–nhận hàng và lịch hẹn. |

## Thiết kế và phương pháp

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


## Nguồn và tái lập

[Complete Journey](https://bradleyboehmke.github.io/completejourney/) và [từ điển dữ liệu](https://bradleyboehmke.github.io/completejourney/articles/completejourney.html); [mã nguồn bộ dữ liệu](https://github.com/bradleyboehmke/completejourney), package ghi CC0. [Scikit-learn ensemble](https://scikit-learn.org/stable/modules/ensemble.html) và [metrics](https://scikit-learn.org/stable/modules/model_evaluation.html). UCI đã kiểm tra ở báo cáo khảo sát trước và không nối vào bộ train này.

Run ID: 20261101_211545_762551_356e56a9. Xem run_manifest.json, models/model_registry.json và RUNBOOK.md để tái lập.
