# Retail Intelligence Web: bản demo phân tích kinh doanh siêu thị

Web demo cho khách hàng (chuỗi siêu thị) xem năng lực phân tích dữ liệu kinh doanh: bảng điều hành, các phân hệ phân tích theo nghiệp vụ, mô phỏng giá/khuyến mãi, tra cứu dữ liệu và lộ trình triển khai. Dữ liệu demo: 5 bộ bán lẻ công khai (dunnhumby Complete Journey, Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real; Walmart M5).

- **Frontend:** React 18 + TypeScript + Tailwind CSS 3 + ECharts, build bằng Vite.
- **Backend:** FastAPI + duckdb.

## Chạy nhanh

```bash
./run.sh          # Linux/WSL: build giao diện nếu cần, rồi mở http://localhost:8000
./dev.sh          # phát triển: FastAPI :8000 (tự nạp lại) + Vite :5173 (hot reload)
```

Windows: `./run.ps1`. Tài liệu API (Swagger) ở http://localhost:8000/docs.

Cần Python 3.11+ (`pip install -r backend/requirements.txt`) và Node 18+.

## Kiến trúc

```
data/raw_* (dữ liệu gốc)
   │  research/multisource/analyze_*.py      phân tích: duckdb, pandas, statsmodels, scikit-learn
   ▼
outputs/multisource/results*.json + trang HTML phân tích
   │  backend/scripts/build_cache.py         đóng gói cho web
   ▼
backend/data/
   content.json          nội dung 12 chương (tiêu đề, Góc dữ liệu, Góc kinh tế, thẻ tổng hợp, hành động)
   chart_data.json       dữ liệu 29 biểu đồ
   results*.json         hệ số mô hình cho mô phỏng
   m5_store_dept_daily.parquet   136 nghìn dòng: ngày × cửa hàng × nhóm hàng (lượng, doanh thu, tỷ lệ ngày bằng 0)
   m5_calendar.parquet, cj_dept_weekly.parquet
   │  FastAPI (backend/app)
   ▼
/api/*  ──────►  React SPA (frontend/src)  ◄── FastAPI cũng phục vụ frontend/dist ở "/"
```

| Endpoint | Chức năng |
|---|---|
| `GET /api/dashboard/periods` | Các kỳ tháng/quý/năm trọn vẹn |
| `GET /api/dashboard` | KPI, so kỳ trước/cùng kỳ, cửa hàng, nhóm hàng, xu hướng, cảnh báo, bản tin. Tham số: `grain`, `key`, `state`, `store`, `cat` |
| `GET /api/meta` | KPI, 5 nguồn, ma trận 17 nhóm trường, bảng chất lượng, dòng thời gian |
| `GET /api/sections`, `GET /api/sections/{id}` | Danh sách và nội dung 12 chương |
| `GET /api/charts` | Dữ liệu cho mọi biểu đồ |
| `GET /api/simulate/options` | Ngành và hệ số dùng cho mô phỏng |
| `POST /api/simulate/promotion` | Lượng bán, doanh thu, lợi nhuận và đường lợi nhuận theo mức giảm. Đầu vào: ngành, biên gộp, mức giảm, trưng bày, tờ rơi, đối thủ, tuần sau |
| `POST /api/simulate/price` | Tác động của thay đổi giá, kèm khoảng tin cậy độ co giãn |
| `GET /api/explorer/m5` | Chuỗi M5 lọc theo bang, cửa hàng, ngành, nhóm hàng, kỳ, tần suất (duckdb) |
| `GET /api/explorer/cj` | Doanh thu tuần CJ theo ngành, tỷ lệ giảm giá, nhãn riêng |

## Giao diện

| Trang | Đường dẫn | Dành cho | Nội dung |
|---|---|---|---|
| Trang chủ | `/` | Mọi người | Giới thiệu, năng lực, màn hình theo vai trò, phát hiện nổi bật, cách triển khai |
| Bảng điều hành | `/dieu-hanh` | Ban điều hành, quản lý vùng | KPI theo tháng/quý/năm so kỳ trước và cùng kỳ, bản tin tự sinh, cảnh báo, xu hướng theo năm, xếp hạng cửa hàng, nhóm hàng, doanh thu từng ngày |
| Khách hàng | `/phan-tich/khach-hang` | CRM, Marketing | Tập trung doanh thu, động lực tăng trưởng, RFM, thu nhập và nhãn riêng |
| Giá & khuyến mãi | `/phan-tich/gia-khuyen-mai` | Ngành hàng, Marketing | Độ nhạy giá, trưng bày/tờ rơi, coupon, lãi khi giảm giá |
| Giỏ hàng & thời điểm | `/phan-tich/gio-hang` | Vận hành, Marketing | Loại chuyến, giờ/thứ, mua kèm, ngày nhận trợ cấp, ngày lễ |
| Dự báo nhu cầu | `/phan-tich/du-bao` | Cung ứng | So sánh mô hình dự báo 28 ngày |
| Mô phỏng giá & KM | `/mo-phong` | Ngành hàng | What-if khuyến mãi và đổi giá |
| Tra cứu dữ liệu | `/tra-cuu` | Phân tích viên | Lọc chuỗi cửa hàng (M5) và khách thành viên (CJ) |
| Kết quả & triển khai | `/trien-khai` | Ban điều hành | 9 kết luận, việc nên làm, dữ liệu cần chuẩn bị, lộ trình thí điểm 12 tuần |
| Dữ liệu demo | `/du-lieu` | Mọi người | Nguồn dữ liệu, ma trận trường, giới hạn từng nguồn |

Link cũ `/chuong/:id` và `/kham-pha` tự chuyển sang trang mới.

Giao diện sáng/tối/theo hệ thống (nút ở góc phải trên), bố cục một cột trên điện thoại, điều hướng bằng bàn phím.

Cấu hình biểu đồ ở `frontend/src/charts/registry.ts` được chuyển nguyên từ trang phân tích tĩnh đã kiểm số liệu. File này để `@ts-nocheck`; các trang và component còn lại chạy TypeScript strict.

## Kiểm thử

```bash
cd backend && python3 -m pytest -q          # 7 test: nội dung, dữ liệu, mô phỏng khớp số offline, khám phá, bảng điều hành, cấu hình môi trường
cd frontend && npx tsc -b                   # kiểm tra kiểu
```

## Cập nhật dữ liệu

Chạy lại phân tích trong `research/multisource/`, rồi:

```bash
python3 webapp/backend/scripts/build_cache.py
```

Script này dựng lại `backend/data`. Bước tạo parquet cần dữ liệu gốc trong `data/raw_m5` và `data/raw_dunnhumby`.

## Môi trường và deploy lên Vercel

Cấu hình tách theo môi trường; không có bí mật nào trong file.

| File | Dùng khi |
|---|---|
| `backend/.env.development` | Chạy local (`APP_ENV` mặc định `development`): bật Swagger, CORS cho Vite :5173 |
| `backend/.env.production` | `APP_ENV=production` hoặc Vercel Production: tắt Swagger, không CORS (cùng domain) |
| `backend/.env.local` | Ghi đè riêng trên máy, không commit (mẫu: `backend/.env.example`) |
| `frontend/.env.development`, `frontend/.env.production` | `vite dev` / `vite build`; `VITE_API_BASE` để trống khi API cùng domain |

Thứ tự ưu tiên: biến môi trường thật (Vercel Dashboard, shell) > `.env.local` > `.env.<APP_ENV>`. Trên Vercel, `APP_ENV` lấy từ `VERCEL_ENV`, nên bản Production dùng `.env.production`, bản Preview dùng giá trị mặc định (giống development nhưng không phục vụ frontend).

Biến backend: `APP_ENV`, `CORS_ORIGINS` (phân tách bằng dấu phẩy), `ENABLE_DOCS` (1/0), `DATA_DIR`, `SERVE_FRONTEND` (1/0).

**Cấu trúc trên Vercel** (`vercel.json`, Root Directory = `webapp`):

- Frontend: `npm ci` + `npm run build` trong `frontend/`, phục vụ `frontend/dist` từ CDN; mọi đường dẫn không phải file rewrite về `index.html` (SPA).
- Backend: hàm Python `api/index.py` nạp FastAPI từ `backend/app`; `/api/*`, `/docs`, `/openapi.json` rewrite về hàm này. Thư viện ở `requirements.txt` gốc (chỉ phần chạy, khoảng 170 MB khi giải nén, dưới giới hạn 250 MB). Dữ liệu `backend/data` (2 MB) được đóng gói kèm hàm.
- Cache: `/assets/*` 1 năm; `/api/*` cache CDN 1 giờ.

Deploy:

```bash
cd webapp
npx vercel link                 # chọn/tạo project, Root Directory: webapp
npx vercel                      # bản Preview
npx vercel --prod               # bản Production
# tùy chọn: bật Swagger trên production
npx vercel env add ENABLE_DOCS production    # nhập 1
```

Hoặc nối repo Git trên vercel.com, đặt Root Directory là `webapp`; nhánh chính deploy Production, các nhánh khác deploy Preview.
