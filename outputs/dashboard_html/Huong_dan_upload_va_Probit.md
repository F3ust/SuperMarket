# Dữ liệu mới → 5 model Probit đã train → xác suất

Đây là inference thật bằng các hệ số/ngưỡng/scaler đã fit trên dữ liệu lịch sử. Tải dữ liệu mới không fit lại model, không thay scaler hoặc target. Trang này có ở cả hai vai trò hiện tại; không tạo người dùng thứ ba.

## Thử ngay trong dashboard

1. Mở **Dữ liệu mới & xác suất / Nạp dữ liệu & chạy model**.
2. Bấm **Nạp mẫu lịch sử thật**, xem mapping và ngày bao phủ.
3. Xác nhận phạm vi nguồn, bấm **Kiểm tra dữ liệu**, rồi **Chạy 5 model đã train**.
4. Xem phân bố, tìm mã khách, thay tiêu chí xếp hạng/công suất rà soát và mở từng khách để xem các phân phối.
5. Xuất toàn bộ xác suất CSV và audit JSON. Mẫu là replay lịch sử 60 mã hộ, 54 hộ đủ điều kiện, không phải test mới. Sáu mã còn lại không đủ điều kiện mua dương trong 90 ngày.

## Năm bài toán đã huấn luyện

| Model | Dạng | Đầu ra |
|---|---|---|
| Không mua 28 ngày | Binary Probit có L2 cố định | P(không có mua dương trong 28 ngày tiếp theo) |
| Thời gian quay lại | Ordered Probit | 5 xác suất cho 1–7, 8–14, 15–28, 29–56 ngày, chưa quay lại trong 56 ngày; suy ra P(quay lại ≤7/14/28/56 ngày) |
| Số giỏ kỳ tới | Ordered Probit | 5 xác suất cho 0, 1, 2–3, 4–7 và 8+ giỏ mua dương trong 28 ngày |
| Giảm giá trị mua | Binary Probit có L2 cố định | P(sales 28 ngày tới ≤70% sales 28 ngày trước), chỉ khi kỳ trước sales >0 |
| Mua được giảm giá | Binary Probit có L2 cố định | P(có ít nhất một dòng mua dương được discount trong 28 ngày tới) |

Probit nhị phân vẫn học target nội bộ hai trạng thái; predict trả xác suất liên tục, không ép thành Yes/No. Ordered Probit trả phân phối nhiều mức. Xác suất thời gian quay lại tích lũy nhất quán theo thiết kế, nhưng Binary Probit 28 ngày và Ordered Probit thời gian là hai model khác nhau; không lấy trung bình hoặc buộc bằng nhau tùy ý. Không đưa dự báo số tiền liên tục vào Probit chỉ để dùng tên thuật toán.

Probability ở CSV nằm trong [0,1], ví dụ 0.187 nghĩa là 18,7%, không là nhãn 0/1. Ô thiếu điều kiện giảm giá trị mua để trống; không điền xác suất 0. Giao diện dùng <0,1% hoặc >99,9% cho giá trị sát biên, không khẳng định sự kiện chắc chắn.

## File đầu vào

CSV UTF-8, tối đa 50 MB và 500.000 dòng ở trình duyệt. Có ánh xạ cột theo header thực tế, tự nhận comma/semicolon; chọn rõ dấu thập phân. Không chứa dấu hàng nghìn trong ô số.

| Cột chuẩn | Yêu cầu |
|---|---|
| line_id | Khóa dòng ổn định, duy nhất. Không dùng số thứ tự mới mỗi lần xuất. |
| date | Ngày nghiệp vụ YYYY-MM-DD; nếu dùng timestamp phải chuẩn hóa về ngày kinh doanh của nguồn, không tự chuyển UTC sang ngày địa phương trong model. |
| household_id | Mã khách hoặc hộ, dạng text, giữ số 0 đầu. |
| basket_id | Khóa giỏ toàn cục, nhất quán một khách/một ngày. Có thể phải ghép source + store + business_date + receipt. |
| product_category | Cùng cấp taxonomy với định nghĩa train; không trộn department và category. |
| quantity | Số lượng dòng; dùng điều kiện mua dương, không cộng các SKU khác đơn vị thành nhu cầu. |
| sales_value | Cùng ngữ nghĩa số tiền bán của retailer; cần đối soát VAT, hoàn/hủy và discount của nguồn. |
| retail_disc, coupon_disc, coupon_match_disc | Ba cột discount. Thiếu cột thì chỉ chọn hằng 0 khi nguồn xác nhận thật sự không có, không mặc định impute. |

Giữ mã dạng text khi xuất từ Excel; ký pháp khoa học bị chặn. Không nhận .joblib, pickle hoặc mã thực thi từ người dùng. Số không hữu hạn, dòng trùng line_id, khóa giỏ xung đột và ngày sau as-of bị chặn. Quantity/sales không dương giữ trong thống kê raw và loại khỏi feature mua dương; không sửa thành dương. Gate raw = positive + ngoại lệ giúp đọc file, chưa thay đối soát với sổ ERP.

Model train bằng USD. File VND cần tỷ giá VND/USD do người dùng cung cấp, quy đổi nhất quán tiền và discount. Tỷ giá không làm model tự phù hợp với thị trường, sức mua hoặc lạm phát mới. Chưa có tỷ giá thị trường live trong app.

## Snapshot độc lập

- Xuất tối thiểu 90 ngày bao phủ đến as-of cho khách được xét. Được chứa lịch sử dài hơn.
- Khai báo ngày đầu bao phủ, ngày chấm điểm và xác nhận dữ liệu đủ phạm vi kể cả ngày không có giao dịch.
- Không ghép mã khách với panel cũ trong chế độ này; model suy luận từ covariate, không từ tên/mã khách.
- Không suy ra file đủ lịch sử chỉ vì min/max có vẻ đủ 90 ngày. Chất lượng nguồn và bao phủ vẫn cần người sở hữu dữ liệu xác nhận.

## Bổ sung dữ liệu

- Nền ban đầu đóng đến **31/12/2017**. Append chỉ nhận ngày mới sau cutoff và phải cùng hệ mã.
- Batch mới phải nối liên tục với watermark thành công trước đó. Nếu watermark 31/12 và file chỉ bắt đầu 05/01, cần bổ sung 01–04/01 hoặc khai báo đúng bao phủ nguồn có cả ngày zero; không điền khoảng trống tùy ý.
- Cùng line_id, cùng nội dung giữa các batch được coi là gửi lại idempotent, không nhân dòng. Cùng ID nhưng nội dung đổi bị chặn; dùng snapshot đã đối soát cho sửa hồi tố.
- Chỉ commit batch vào nền append trong RAM sau khi suy luận và đối soát thành công. Batch lỗi giữ kết quả thành công trước.
- Watermark và raw upload chỉ ở RAM tab. Nạp lại/đóng tab sẽ mất. Khi mở lại, cần file bổ sung tích lũy từ sau cutoff hoặc snapshot độc lập đủ 90 ngày. Đây chưa là kho dữ liệu bền vững, CDC hoặc scheduler sản xuất.

## Feature, kiểm tra và giới hạn

Tám feature: recency, visits_7, visits_28, visits_90, sales_ratio = (sales_28+1)/(sales_56/2+1), categories_28, discount_line_share_90, aov_90. Chỉ mua dương trong quá khứ tới as-of, không dùng giao dịch tương lai. Log1p, mean/std và ngưỡng Ordered Probit được fit/lưu từ train, không tính lại trên file mới.

Validation: **13/08/2017**. Holdout: **08/10 và 05/11/2017**. Train chỉ dùng target đã hoàn thành trước validation; validation hoàn thành trước test đầu. Các cửa sổ 56 ngày overlap 28 ngày, hộ lặp giữa snapshot; không xem chúng là mẫu độc lập. Final refit chỉ dùng target hoàn tất tới 31/12. Không dùng model này hồi tố trước cutoff.

Hồ sơ model hiển thị log loss, Brier và baseline từ train; Brier multiclass dùng tổng bình phương sai số các mức, khác thang Brier nhị phân. Không claim xác suất đã calibration riêng. Model mới không tự thay champion gradient boosting của bài risk cũ; đây là bộ Probit bổ sung được kiểm tra riêng.

Đã kiểm tra CDF portable so với SciPy trên fixture và pipeline feature CSV: sai khác xác suất tối đa <2×10^-7. Kiểm tra tổng phân phối bằng 1, xác suất quay lại tích lũy không giảm, hội tụ gradient của Probit có regularization và hội tụ Ordered Probit. Xem chứng cứ trong `qa/` ở workspace.

Feature ngoài quantile train 1–99% là tín hiệu điều tra, không tự kết luận model sai. Hộ có lịch sử mua ngắn được đánh dấu. Xác suất không mua không là responsiveness/uplift; xác suất có discount không đo hiệu quả khuyến mãi. Trước dùng tại doanh nghiệp mới cần target đủ 28/56 ngày, đo calibration/log loss/Brier và so baseline trên đúng nguồn mới. Không auto gửi ưu đãi, đặt hàng hoặc chi ngân sách.

Các KPI và model lịch sử ở màn hình khác vẫn dùng snapshot 2017, không bị ghi đè bởi file upload. Kết quả mới có không gian và audit riêng. Chưa có nhãn tương lai để hiển thị accuracy trên dữ liệu tải lên.

## Batch Python cho snapshot lớn

Gói model portable có `probability_registry.json`, `probability_runtime.py`, `score_probability.py`, schema và mẫu công khai. Không cần train hoặc tải lại dữ liệu cũ để score. Python cần numpy, pandas, scipy; Parquet thêm pyarrow.

```powershell
python score_probability.py --input snapshot.csv --as-of 2018-03-31 --coverage-start 2018-01-01 --complete --currency USD --output ket_qua
```

CLI nhận CSV hoặc Parquet chuẩn schema, không áp giới hạn trình duyệt; dung lượng vẫn phụ thuộc RAM máy. Xuất `probabilities.csv` và `audit.json`. File VND thêm `--currency VND --fx <tỷ_giá_người_dùng_cung_cấp>`. CLI hiện dùng snapshot độc lập, không tự quản trị watermark của app.

Thay đổi target, lịch sử, threshold 30%, cửa sổ hoặc train cutoff cần huấn luyện/đánh giá và phát hành model version mới. Không cho người dùng đổi các định nghĩa này chỉ bằng bộ lọc.

Nguồn kỹ thuật: [Statsmodels GLM](https://www.statsmodels.org/stable/glm.html), [OrderedModel](https://www.statsmodels.org/stable/generated/statsmodels.miscmodels.ordinal_model.OrderedModel.html). Phân biệt Probit nhị phân trả xác suất và Ordered Probit trả xác suất từng mức.
