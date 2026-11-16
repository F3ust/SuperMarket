# Vận hành pipeline phân tích bán lẻ

## Đầu ra chính

- `outputs/enterprise/latest_report.html`: báo cáo tương tác tiếng Việt, mở offline, không cần server hay kết nối mạng.
- `outputs/enterprise/latest_report.md`: báo cáo phương pháp, kết quả và giới hạn.
- `outputs/enterprise/latest.json`: con trỏ đến bộ artifact thành công gần nhất; đây là nguồn chuẩn khi tích hợp ứng dụng.
- Mỗi run giữ dữ liệu enriched Parquet, bảng KPI/insight/action CSV, features, dự báo tiếp theo, danh sách khách cần xem xét, metrics validation/test, model registry và log.
- `models/challengers/`: bốn mô hình dự báo ML đã fit toàn bộ nhãn đã hoàn thành. Artifact champion có thể là baseline nếu baseline thắng validation.

## Chạy toàn bộ tự động bằng một lệnh

```powershell
.\run_pipeline.ps1
```

Pipeline đọc dữ liệu, kiểm tra chất lượng, tổng hợp phân tích, train/evaluate/select/refit mô hình, score, giám sát và xuất báo cáo. Không thay đổi nguồn gốc. Nếu hash input + code + config không đổi, lệnh tự skip. Dùng `-Force` khi cần chạy lại dù không thay đổi.

```powershell
.\run_pipeline.ps1 -Force
```

Mặc định dùng interpreter bundled của máy đã thực hiện dự án; trên máy khác truyền `-Python C:\path\python.exe`, cài phiên bản trong `retail_pipeline/requirements.txt`. Package pyreadr đang nằm ở `research/vendor`; muốn môi trường sạch có thể cài pyreadr bình thường. Python 3.12 đã được dùng. `run_manifest.json` là bản ghi phiên bản thực tế và input checksum.

Kiểm tra logic chống leakage và nhãn:

```powershell
& 'C:/Users/pc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m unittest retail_pipeline.test_pipeline -v
```

## Score dữ liệu mới mà không train lại

```powershell
.\run_pipeline.ps1 -Mode score -AsOf 2017-12-31
```

Lệnh dùng model từ run thành công gần nhất, giữ nguyên vocabulary nhóm hàng/feature, tạo bảng forecast và customer risk mới trong `outputs/enterprise/scores/`. `latest_score.json` chỉ cập nhật khi score thành công. Dữ liệu phải đủ lịch sử và có bản ghi của ngày sau AsOf để tránh lấy ngày cuối chưa hoàn tất. Không được score quá khứ trước ngày model đã train vì sẽ gây leakage. Model file joblib chỉ dùng từ nguồn local đáng tin cậy.

Lệnh train giữ `analysis_end` trong config, không tự dùng hôm nay với dữ liệu lịch sử. Khi thay nguồn, sao chép config để ghi rõ ngày kinh doanh hoàn tất. Lệnh score có thể override `-AsOf`; không tự nhận một ngày vắng là hoàn tất chỉ vì đã qua nửa đêm.

## Lịch chạy

Đã cung cấp script cài Windows Task Scheduler, **chưa đăng ký task chạy nền** vì dữ liệu hiện tại là lịch sử cố định và chưa có nguồn POS mới. Nếu muốn bật trên máy có dữ liệu được cập nhật:

```powershell
.\install_schedule.ps1 -TaskName 'SieuThi-Retail-Analytics' -DailyTime '06:00' -Mode train
```

Script yêu cầu múi giờ Windows SE Asia Standard Time, tương ứng Asia/Saigon. Task gọi PowerShell Hidden, bỏ qua lần chồng nhau, chạy lại khi máy sẵn sàng, timeout 2 giờ. Nếu task trùng tên, script dừng để tránh ghi đè lịch khác. Quyền tạo task phụ thuộc tài khoản Windows. Với dữ liệu lịch sử không đổi, full run sẽ skip; script không tự tải dữ liệu POS mới hoặc tự đổi ngày AsOf.

Vận hành doanh nghiệp đề xuất: ingest/score sau khi POS chốt ngày; train lại hàng tuần hoặc khi có đủ nhãn mới; kiểm tra model degradation trên nhãn đã chín; chỉ đổi champion qua đánh giá thời gian và kiểm duyệt nghiệp vụ. Scheduler mẫu hiện gọi trọn pipeline; lịch train và score riêng có thể được đăng ký bằng hai tên task khi quy trình nguồn đã ổn định.

## Hợp đồng dữ liệu và tích hợp POS/ERP

Config `input_dir` nhận đường dẫn tương đối dự án hoặc tuyệt đối. CSV được ưu tiên hơn RDS/RDA cùng tên để có thể thử adapter mà không sửa code. Trong thư mục nguồn:

| Bảng | Grain và trường bắt buộc |
|---|---|
| transactions.csv | Một dòng hóa đơn; household_id, store_id, basket_id, product_id dạng chuỗi; transaction_timestamp dạng ISO local time nhất quán; quantity, sales_value, retail_disc, coupon_disc, coupon_match_disc dạng số |
| products.csv | Một dòng/SKU; product_id duy nhất, department, product_category, brand |
| campaigns.csv (tùy chọn) | campaign_id + household_id duy nhất |
| campaign_descriptions.csv (tùy chọn) | campaign_id duy nhất, campaign_type, start_date, end_date |
| coupon_redemptions.csv (tùy chọn) | household_id, coupon_upc, campaign_id, redemption_date |

Mã basket_id phải duy nhất toàn hệ thống, thuộc một cửa hàng và một khách. Nếu POS chỉ có receipt_id cục bộ, adapter phải tạo basket_id từ store_id + business_date + receipt_id. Trường customer_id vắng không được tự điền một khách chung; cần tách tập analytics giao dịch ẩn danh và tập CRM, điều chỉnh code/đánh giá trước khi dùng thật. Bản hiện tại yêu cầu mã hộ vì bài toán panel có đầy đủ mã.

CSV mẫu/nguồn thực phải dùng UTF-8 và lưu ID dưới dạng text để giữ số 0 đầu. Nguồn cần đã chuẩn hóa múi giờ, ngày kinh doanh, tiền tệ, đơn vị, thuế, hoàn/hủy. Không đưa trực tiếp trường doanh thu POS vào sales_value nếu định nghĩa khác. Nếu định nghĩa khác nguồn public, cập nhật adapter, report và kiểm tra đối soát.

Pipeline hiện đọc trọn lịch sử và ghi snapshot thành công; không tự suy ra CDC hay upsert nếu không có line_id ổn định. Khi tích hợp thật cần bảng raw theo batch, source_system, line_id, ingested_at, updated_at và watermark; late-arrival/backfill ghi lại partition liên quan rồi chạy lại. Bảo toàn mã cũ, dùng mapping có ngày hiệu lực cho SKU/cửa hàng. Nếu cần ẩn danh, băm với salt được quản lý bên ngoài repository.

## Quality gates và lỗi

- Dừng khi thiếu cột, ID rỗng, numeric không hữu hạn, trùng nguyên dòng, trùng khóa products, basket xung đột, không đủ lịch sử, lấy ngày cuối chưa hoàn thành, hoặc join miss vượt ngưỡng config.
- Ngày vắng trong lịch làm pipeline dừng, trừ danh sách giả định khai báo rõ trong `observed_zero_transaction_dates`. Bộ hiện tại có 25/12/2017 vắng bản ghi. Xử lý bằng 0 chỉ mô tả số tiền quan sát trong panel; báo cáo có độ nhạy loại tuần đó. Không dùng giả định này thay cho xác minh nguồn thật.
- Dòng quantity/sales_value không dương giữ riêng để giải thích, không tự coi là giao dịch gian lận. Bảng `model_excluded_lines.csv` và `unmatched_products.csv` phục vụ xử lý nghiệp vụ.
- Lỗi ghi `last_failure.json` và run pending với traceback; không cập nhật latest thành công. Lock còn lại sau tắt đột ngột cần kiểm tra PID có còn chạy trước khi xóa **đúng file** `outputs/enterprise/pipeline.lock`.
- Mỗi run có đối soát raw = positive + excluded, tổng theo tháng = enriched, kiểm tra reload artifact. Lock chỉ áp dụng full training; score xuất thư mục riêng và có thể chạy độc lập, không ghi đè model.

## Giám sát

`monitoring.json` so phân bố sales/ngày của 28 ngày cuối với 28 ngày trước; PSI >0.2 là cờ điều tra, không tự retrain hay chứng minh suy giảm. Mùa vụ và dữ liệu vắng có thể làm đổi phân bố. Dữ liệu lịch sử không bị đánh giá “stale” theo ngày hiện tại. Với dữ liệu thật cần theo dõi thời gian batch chốt, số dòng/tổng tiền nguồn, tỷ lệ khóa thiếu, delay và availability riêng.

Sau khi label mới đủ 7/28 ngày, đối chiếu forecast/risk đã xuất với thực tế và lưu metrics theo origin; tránh đánh giá khi nhãn chưa đủ. Pipeline hiện cung cấp historical backtests và bản score mới, chưa có dịch vụ nhận nhãn hoặc hệ thống cảnh báo ngoài máy. Không tự gửi khách hàng, đổi giá, đặt hàng hay tác động POS.

## Chuyển thành PoC doanh nghiệp

1. Data owner và kế toán chốt định nghĩa KPI; lấy 2–4 tuần mẫu và tổng đối soát, xác minh khóa/thuế/hoàn/ngày kinh doanh.
2. Lấy lịch sử 12–24 tháng đủ giao dịch; bổ sung tồn, giá vốn, khuyến mãi, lead time theo bài toán. Kiểm tra có bias do chỉ lấy khách loyalty.
3. Adapter → quality gate → dashboard chạy song song báo cáo hiện tại; tìm và giải thích từng chênh lệch đáng kể.
4. Backtest nhiều mốc trên dữ liệu doanh nghiệp, chọn mô hình theo validation rồi giữ test riêng. Đo WAPE/bias theo ngành, cold-start và hàng bán chậm; CRM đo precision/lift theo công suất.
5. Thử nghiệm có đối chứng cho CRM/combo/khuyến mãi, tính lợi nhuận sau chi phí khi có giá vốn. Không lấy độ chính xác offline làm ROI.
6. Chỉ sau khi đạt tiêu chí nghiệp vụ mới tích hợp quyết định, phân quyền, lưu audit, SLA và quy trình rollback/champion–challenger.
