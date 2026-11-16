# Retail Intelligence — hai không gian điều hành

Bản hiện tại có đúng hai vai trò trình diễn: **Ban điều hành cấp cao** và **Điều hành vận hành**. Menu và trang chủ tách theo nhu cầu ra quyết định; không còn góc nhìn Data & AI. Chưa có hai tài khoản xác thực hoặc RBAC riêng.

Đọc [BUSINESS_GUIDE.md](BUSINESS_GUIDE.md) để biết phạm vi, công thức tài chính, ngữ nghĩa kỳ so sánh và kịch bản trình diễn.

## Chạy và tái tạo

- Mở `dist/index.html` bằng Edge/Chrome: dữ liệu, biểu đồ, artifact kết quả model và Word đều nhúng, dùng offline.
- Bản bàn giao ở `../outputs/dashboard_html/`, kèm ZIP và hướng dẫn tiếng Việt.
- Từ workspace đầy đủ chạy `python build_data.py`, rồi `python build_html.py`. Cần pandas, numpy, joblib, pyarrow và plotly. Build HTML nhúng `src/business.js` trong app closure.
- Không cần build hoặc Python để chạy `dist/index.html` đã tạo.
- Pipeline thật ở `../run_pipeline.ps1`; tài liệu triển khai ở `../RUNBOOK.md`, `../CHAIN_ROLLOUT.md`.

## Kiểm tra

`qa/business-v2.cjs` kiểm tra hai vai trò/menu, chuyển từ URL pipeline cũ, so sánh tháng lịch, cầu nối tăng trưởng, kịch bản tài chính, biên không dương, xuất CSV, lưu bàn công việc, desktop/mobile và đối soát toàn bộ dữ liệu. Kết quả trong `qa/business-v2-results.json`. Các script QA trước bản hai vai trò là bằng chứng lịch sử; dùng script v2 cho giao diện hiện tại.

## Inference từ file mới

Hai vai trò đều có trang nạp dữ liệu và chạy 5 model Probit đã train. Xem [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md). Registry portable được version trong `probability_registry.json`. `score_probability.py` chỉ suy luận; `train_probability.py` là job huấn luyện riêng trên dữ liệu lịch sử, không gọi tự động khi upload. Build HTML nhúng runtime CSV/Probit worker và gói batch Python, chạy cả offline. Các file upload chỉ ở RAM tab. QA thêm `qa/probability-worker.cjs`, `qa/probability-parity.py`, `qa/upload-browser.cjs`.
