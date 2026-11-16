# SuperMarket: phân tích kinh doanh siêu thị

| Thư mục | Nội dung |
|---|---|
| `webapp/` | Web demo cho khách hàng: React + TypeScript + Tailwind, FastAPI; deploy Vercel. Xem `webapp/README.md` |
| `research/` | Script tải dữ liệu, phân tích, hồ sơ dữ liệu (`research/data_report/`), phân tích đa nguồn (`research/multisource/`) |
| `outputs/` | Báo cáo Word, trang HTML, biểu đồ, kết quả; `outputs/data_report/` là báo cáo dữ liệu |
| `retail_pipeline/`, `dashboard_enterprise/` | Pipeline và dashboard của vòng đầu (Complete Journey gói R) |
| `docs/DATA_REPORT.md` | **Báo cáo dữ liệu**: nguồn, quy mô, chất lượng, xử lý, tái lập |
| `data/` | Chỉ có `manifest.json` trong git. Dữ liệu thô (2,3 GB) tải theo mục 7 của báo cáo dữ liệu |

## Khảo sát dữ liệu siêu thị

## Bản giao cuối (MVP)

Thư mục `outputs/FINAL`: đề xuất MVP bằng Tiếng Việt và English (Word) và dashboard hai ngôn ngữ chạy offline. Dựng lại: `python dashboard_enterprise/build_insights.py`, `python dashboard_enterprise/build_html.py`, `python research/build_mvp_report.py`.

## Báo cáo Word chuyên sâu

[Báo cáo tiếng Việt](outputs/word_report/Bao_cao_chuyen_sau_chuoi_sieu_thi.docx) tổng hợp bằng chứng kinh doanh, đánh giá mô hình, biểu đồ, thiết kế dữ liệu và kế hoạch PoC cho chuỗi. Tạo lại bằng `.\build_word_report.ps1 -Render` với snapshot đã được đánh giá. Script khóa chữ ký nguồn và code để tránh phát hành nhận định cũ khi dữ liệu hoặc mô hình đổi; cần rà soát nội dung trước khi mở khóa cho kỳ mới. Ảnh trang và PDF trong thư mục render chỉ phục vụ kiểm tra bố cục.

## Pipeline phân tích và mô hình đầy đủ

Xem [báo cáo tương tác mới nhất](outputs/enterprise/latest_report.html), [báo cáo phương pháp và kết quả](outputs/enterprise/latest_report.md) và [hướng dẫn vận hành](RUNBOOK.md).

Phạm vi doanh nghiệp đã xác nhận là **chuỗi siêu thị/cửa hàng bán lẻ**. Xem [kế hoạch PoC cho chuỗi](CHAIN_ROLLOUT.md) để xác định dữ liệu theo cửa hàng–SKU, đối soát liên hệ thống, đánh giá xuyên cửa hàng và điều kiện bổ sung tồn kho.

Chạy toàn bộ bằng `.\run_pipeline.ps1`. Pipeline có quality gates, báo cáo kinh doanh, RFM/ABC/cohort/KMeans, bốn mô hình dự báo và baseline, mô hình không mua trong 28 ngày, association/popularity có validation/test theo thời gian, score, monitoring và xuất báo cáo offline. Kết quả mới chỉ được công bố sau khi kiểm tra thành công. Code/config/input không đổi thì bỏ qua train lại.

`business_mart.sqlite` trong run thành công có các bảng tổng hợp phục vụ SQL/BI. Dữ liệu chi tiết ở Parquet. Danh sách hành động CRM/dự báo là đề xuất để rà soát, chưa tác động POS hay gửi khách hàng. Script scheduler đã cung cấp, chưa cài lịch nền.

Ví dụ score lại bằng model đã train: `.\run_pipeline.ps1 -Mode score -AsOf 2017-12-31`. CLI gợi ý danh mục: `python -m retail_pipeline.recommend --category SOUP`.

Bắt đầu tại [báo cáo khảo sát](outputs/bao_cao_khao_sat.md): nguồn dữ liệu, kết quả phân tích, danh mục bài toán, yêu cầu dữ liệu doanh nghiệp và kế hoạch một tuần làm việc.

## Dữ liệu và kết quả

- `data/raw/`: dữ liệu công khai gốc, không chỉnh sửa.
- `data/manifest.json`: nguồn tải, ngày tải và SHA-256 của file tải về.
- `outputs/`: báo cáo tiếng Việt, biểu đồ, chỉ tiêu chất lượng và bảng kết quả CSV.
- `research/`: script tải và phân tích có thể chạy lại.

Complete Journey là mẫu theo dõi hộ mua hàng, không phải doanh thu đầy đủ của toàn bộ cửa hàng. Online Retail là bán lẻ quà tặng trực tuyến ở Anh. Không gộp hai bộ thành một nguồn và không dùng kết quả để suy diễn trực tiếp cho siêu thị Việt Nam.

## Chạy lại

Đã chạy với Python 3.12 của runtime bundled, pandas 2.2.3, numpy 2.3.2, matplotlib 3.10.1, openpyxl 3.1.5. Thư viện pyreadr 0.5.9 đặt riêng ở `research/vendor` để đọc RDS/RDA.

```powershell
& 'C:/Users/pc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' research/download_data.py
& 'C:/Users/pc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' research/analyze.py
```

Script tải bỏ qua file đã tồn tại; manifest ghi dấu kiểm tra file. Script phân tích tạo lại báo cáo và các kết quả tĩnh trong `outputs/`. Để tái lập trên máy khác, cài các thư viện tương ứng và `pyreadr` hoặc đưa pyreadr vào `research/vendor`.

## Ghi công nguồn

- Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. CC BY 4.0.
- Complete Journey: dữ liệu nguồn 84.51°, bản xử lý và package bởi Brad Boehmke và Steven M. Mortimer. https://github.com/bradleyboehmke/completejourney. Trường License trong DESCRIPTION của package ghi CC0.

Các bộ trên Kaggle/dunnhumby khác chỉ được khảo sát nguồn, chưa tải. Xem trạng thái chính xác trong báo cáo.

## Phân tích đa nguồn (07/11/2026)

Thư mục `outputs/multisource/`: trang tương tác [Phan_tich_da_nguon.html](outputs/multisource/Phan_tich_da_nguon.html) và báo cáo Word [Bao_cao_phan_tich_da_nguon.docx](outputs/multisource/Bao_cao_phan_tich_da_nguon.docx). Trộn 5 bộ: dunnhumby Complete Journey (bản gốc 2 năm), Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real (mẫu 5K khách, dữ liệu mô phỏng) và Walmart M5 (bản Zenodo). Dữ liệu gốc ở `data/raw_dunnhumby/`, `data/raw_m5/`. Các bộ không có khóa chung nên được hài hòa ở mức chỉ số, không nối dòng.

Báo cáo Word gồm 4 phần: phân tích dữ liệu (14 chương), xây dựng web, mô tả từng chương web (ảnh chụp thật), khuyến nghị. Tái lập: `python3 research/multisource/analyze_multisource.py`, `analyze_deep.py`, rồi `make_figures.py`, `build_html.py`, `build_word.py` trong cùng thư mục (cần duckdb, pandas, statsmodels, matplotlib, python-docx). Trang HTML tải ECharts từ CDN nên cần mạng để hiện biểu đồ.

## Báo cáo dữ liệu (17/11/2026)

[docs/DATA_REPORT.md](docs/DATA_REPORT.md) (bản Word: `outputs/data_report/Bao_cao_du_lieu.docx`) mô tả 7 bộ dữ liệu: nguồn gốc, bản quyền, quy mô, từ điển dữ liệu, kiểm tra chất lượng, hài hòa đa nguồn, dòng dõi dữ liệu tới web và cách tái lập. Số liệu tính từ file gốc bằng `python3 research/data_report/profile_data.py`, rồi `build_data_report.py`.
