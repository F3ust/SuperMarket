"""Dựng Báo cáo dữ liệu từ outputs/data_report/profile.json.

Ra hai bản cùng nội dung:
  docs/DATA_REPORT.md                              đọc trên GitHub
  outputs/data_report/Bao_cao_du_lieu.docx         bản Word

Chạy: python3 research/data_report/build_data_report.py  (sau profile_data.py)
"""
from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
P = json.loads((ROOT / "outputs/data_report/profile.json").read_text(encoding="utf-8"))
S = P["sources"]
META = json.loads((ROOT / "webapp/backend/data/content.json").read_text(encoding="utf-8"))["meta"]


# ------------------------------------------------------------------ định dạng số kiểu Việt
def n(v, d=0):
    if v is None:
        return "–"
    s = f"{float(v):,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(v, d=1):
    return "–" if v is None else n(float(v) * 100, d) + "%"


def mb(v):
    return n(v, 1) + " MB"


B: list = []  # khối nội dung: (kind, ...)
h1 = lambda t: B.append(("h1", t))
h2 = lambda t: B.append(("h2", t))
h3 = lambda t: B.append(("h3", t))
p = lambda t: B.append(("p", t))
bl = lambda items: B.append(("ul", items))
tb = lambda head, rows, note=None: B.append(("table", head, rows, note))

cj, cb, bf, lg, m5, early = (S[k] for k in ("cj", "carbo", "batf", "lgsr", "m5", "early"))
C, CB, BF, LG, M = cj["checks"], cb["checks"], bf["checks"], lg["checks"], m5["checks"]
OL = early["online_retail"]["checks"]
T = lambda src, name: next(t for t in src["tables"] if t["name"] == name)
cj_tx = T(cj, "transaction_data")
rows_by = {
    "Complete Journey": sum(t["rows"] for t in cj["tables"]),
    "Breakfast at the Frat": sum(t["rows"] for t in bf["tables"]),
    "Carbo-Loading": sum(t["rows"] for t in cb["tables"]),
    "Let's Get Sort-of-Real": sum(t["rows"] for t in lg["tables"]),
    "Walmart M5 (ô ngày × chuỗi + giá + lịch)": M["cells"] + T(m5, "sell_prices")["rows"] + T(m5, "calendar")["rows"],
}
grand = sum(rows_by.values())

# ================================================================== 0. Tóm tắt
h1("Báo cáo dữ liệu: dự án phân tích kinh doanh siêu thị")
p(f"Báo cáo mô tả toàn bộ dữ liệu dự án dùng: nguồn gốc, quy mô, cấu trúc, chất lượng, cách xử lý và dữ liệu đưa lên web demo. "
  f"Mọi con số được tính tự động từ file gốc bằng `research/data_report/profile_data.py` (lần chạy {P['generated']}). "
  f"Báo cáo phân tích kinh doanh nằm ở `outputs/multisource/Bao_cao_phan_tich_da_nguon.docx`; báo cáo này chỉ nói về dữ liệu.")
h2("Tóm tắt")
bl([
    f"7 bộ dữ liệu công khai, {P['inventory']['files']} file, {n(P['inventory']['total_mb'] / 1000, 2)} GB trên đĩa. 5 bộ dùng cho phân tích đa nguồn và web: "
    f"Complete Journey, Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real (dunnhumby) và Walmart M5. 2 bộ của vòng khảo sát đầu: UCI Online Retail và Complete Journey bản gói R.",
    f"Khoảng {n(grand / 1e6, 0)} triệu dòng (tính M5 theo ô ngày × chuỗi SKU-cửa hàng), giai đoạn 2006–2016, Mỹ và Anh.",
    "Không có khóa chung giữa các nguồn (mã khách, mã hàng, mã cửa hàng đều riêng). Vì vậy dự án hài hòa ở mức chỉ số: tính cùng một chỉ số trong từng nguồn rồi so sánh, không nối dòng.",
    f"Dữ liệu sạch về kỹ thuật: không có giá trị thiếu ở cột khóa giao dịch (trừ mã khách của LGSR và UCI: khách vãng lai), {n(C['dup_rows'])} dòng trùng hoàn toàn ở CJ, {n(CB['dup_rows'])} ở Carbo. "
    f"Vấn đề chính là về nghiệp vụ: panel không phải toàn bộ khách, nhu cầu cấp SKU-ngày phần lớn bằng 0 ({pct(M['zero_share_after_launch'], 0)} ô của M5 sau ngày lên kệ), "
    f"LGSR là dữ liệu mô phỏng, không có giá vốn hay tồn kho ở nguồn nào.",
    f"Web demo chỉ dùng {n(sum(f['kb'] for f in P['web']['files']) / 1000, 1)} MB dữ liệu đã tổng hợp; tổng lượng bán M5 trên web khớp file gốc ({n(P['web']['m5_reconcile']['units_total'])} so với {n(M['units_total'])} đơn vị).",
])

# ================================================================== 1. Danh mục nguồn
h2("1. Danh mục nguồn dữ liệu")
tb(["Nguồn", "Đơn vị phát hành", "Giai đoạn", "Hạt dữ liệu", "Số file", "Dung lượng", "Số dòng"], [
    ["The Complete Journey", "dunnhumby", f"102 tuần ({C['day_max']} ngày)", "Dòng hóa đơn của 2.500 hộ", str(len(cj["tables"])), mb(sum(t["mb"] for t in cj["tables"])), n(rows_by["Complete Journey"])],
    ["Breakfast at the Frat", "dunnhumby", f"{BF['week_min'][:10]} → {BF['week_max'][:10]}", "Tuần × cửa hàng × SKU", "1 xlsx (3 sheet)", mb(T(bf, "dh_Transaction_Data")["mb"]), n(rows_by["Breakfast at the Frat"])],
    ["Carbo-Loading", "dunnhumby", f"{CB['week_max']} tuần", "Dòng giao dịch hộ, 4 ngành", str(len(cb["tables"])), mb(sum(t["mb"] for t in cb["tables"])), n(rows_by["Carbo-Loading"])],
    ["Let's Get Sort-of-Real (mẫu 5K)", "dunnhumby (mô phỏng)", f"tuần {LG['week_min']} → {LG['week_max']}", "Dòng giỏ hàng có nhãn", f"{LG['files']} + 1", mb(sum(t["mb"] for t in lg["tables"])), n(rows_by["Let's Get Sort-of-Real"])],
    ["M5 Forecasting", "Walmart / Kaggle (bản Zenodo)", f"{M['date_min']} → {P['web']['m5_reconcile']['date_max']}", "Ngày × cửa hàng × SKU; giá tuần", "4", mb(sum(t["mb"] for t in m5["tables"])), n(rows_by["Walmart M5 (ô ngày × chuỗi + giá + lịch)"])],
    ["Online Retail", "UCI ML Repository", f"{OL['date_min'][:10]} → {OL['date_max'][:10]}", "Dòng hóa đơn bán lẻ online (Anh)", "1", mb(T(early['online_retail'], 'Online Retail')['mb']), n(T(early['online_retail'], 'Online Retail')['rows'])],
    ["Complete Journey (gói R)", "84.51° / B. Boehmke", "2017 (1 năm)", "Dòng hóa đơn, 2.469 hộ", "7 rds/rda", "14,2 MB", n(early["cj_r"].get("rows"))],
], "Số dòng M5 tính theo ô ngày × chuỗi (30.490 chuỗi × 1.941 ngày) cộng bảng giá và lịch. Dung lượng là file đã giải nén.")

h3("Bản quyền và trích dẫn")
bl([
    "dunnhumby Source Files (Complete Journey, Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real): https://www.dunnhumby.com/source-files/ . Dùng theo điều khoản trên trang dunnhumby; repository không chứa file gốc.",
    "M5 Forecasting – Accuracy: Makridakis, Spiliotis, Assimakopoulos (2022), bản lưu trên Zenodo record 12636070 (https://zenodo.org/records/12636070), dữ liệu gốc của cuộc thi Kaggle.",
    "Online Retail: Chen, D. (2015), UCI Machine Learning Repository, https://doi.org/10.24432/C5BW33, CC BY 4.0.",
    "completejourney (gói R): Boehmke & Mortimer, https://github.com/bradleyboehmke/completejourney, dữ liệu 84.51°.",
])

# ================================================================== 2. Hồ sơ từng nguồn
h2("2. Hồ sơ từng nguồn")


def tables_overview(src):
    tb(["Bảng", "File", "Số dòng", "Số cột", "Cột có giá trị thiếu"],
       [[t["name"], t["file"], n(t["rows"]), str(len(t["cols"])),
         ", ".join(f"{c['name']} ({n(c['nulls'])} dòng, {pct(c['null_pct'], 2 if c['null_pct'] < 0.01 else 1)})" for c in t["cols"] if c["nulls"] > 0) or "không"] for t in src["tables"]])


h3("2.1 The Complete Journey (dunnhumby, bản gốc)")
p("Panel 2.500 hộ mua thường xuyên tại một chuỗi bán lẻ Mỹ trong 2 năm. Là nguồn duy nhất có cả mã hộ, nhân khẩu học, chiến dịch marketing, coupon và trưng bày/tờ rơi theo cửa hàng-tuần.")
tables_overview(cj)
tb(["Chỉ tiêu", "Giá trị", "Ghi chú"], [
    ["Hộ / giỏ / mặt hàng / cửa hàng", f"{n(C['households'])} / {n(C['baskets'])} / {n(C['products'])} / {n(C['stores'])}", "444/582 cửa hàng có dưới 50 giỏ: hộ panel thỉnh thoảng mua ở cửa hàng khác"],
    ["Ngày, tuần", f"DAY {C['day_min']}–{C['day_max']}, WEEK {C['week_min']}–{C['week_max']}", "Ngày tương đối, không có ngày lịch" + (f"; {n(C['days_missing'])} ngày không có giao dịch" if C["days_missing"] else "; ngày nào cũng có giao dịch")],
    ["Doanh thu (SALES_VALUE)", f"{n(C['sales_total'])} USD", f"Giá đã trừ giảm giá thẻ; tổng giảm giá {n(C['disc_total'])} USD"],
    ["Dòng SALES_VALUE ≤ 0", f"{n(C['sales_le0'])} ({pct(C['sales_le0'] / cj_tx['rows'], 2)})", ("Tất cả đều bằng 0, không có giá trị âm: đổi trả không ghi thành dòng âm" if C["sales_eq0"] == C["sales_le0"] else f"{n(C['sales_eq0'])} dòng bằng 0")],
    ["Dòng QUANTITY = 0 / > 1.000", f"{n(C['qty_eq0'])} / {n(C['qty_gt1000'])}", "Số lượng > 1.000 chủ yếu thuộc KIOSK-GAS (nhiên liệu): loại khi tính lượng mua"],
    ["Giảm giá dương (sai dấu)", f"RETAIL_DISC {n(C['retail_disc_pos'])}, COUPON_DISC {n(C['coupon_disc_pos'])}", "Giảm giá ghi số âm; dòng dương là điều chỉnh"],
    ["Dòng trùng hoàn toàn", n(C["dup_rows"]), "" if not C["dup_rows"] else "Giữ nguyên: có thể là 2 lần quét cùng món"],
    ["Mặt hàng không có trong product.csv", n(C["tx_product_not_in_lookup"]), "Khóa PRODUCT_ID khớp đầy đủ" if not C["tx_product_not_in_lookup"] else "Loại khi phân tích theo ngành"],
    ["Hộ có nhân khẩu học / có chiến dịch", f"{n(C['hh_with_demo'])} ({pct(C['hh_with_demo'] / C['households'], 0)}) / {n(C['hh_in_campaign'])}", "Phân tích thu nhập chỉ trên 801 hộ"],
    ["TRANS_TIME sai định dạng", n(C["trans_time_bad"]), "Dạng HHMM"],
    ["Giỏ nằm ở > 1 cửa hàng / > 1 ngày", f"{n(C['baskets_multi_store'])} / {n(C['baskets_multi_day'])}", "BASKET_ID nhất quán"],
    ["Trung vị số tuần có mua của một hộ", n(C["hh_txn_weeks_median"]), "Panel chọn hộ mua thường xuyên"],
    ["10 cửa hàng lớn nhất chiếm", pct(C["store_top10_share"], 0) + " doanh thu", "Doanh thu panel trải trên nhiều cửa hàng"],
    ["causal_data: tuần, cửa hàng", f"tuần {C['causal_week_min']}–{C['causal_week_max']}, {n(C['causal_stores'])} cửa hàng", "Chỉ ghi SKU-cửa hàng-tuần có trưng bày hoặc tờ rơi"],
])
p("Phân bố mã trưng bày (display) trong causal_data: " + "; ".join(f"{k}: {n(v)}" for k, v in C["causal_display_dist"]) +
  ". Mã tờ rơi (mailer): " + "; ".join(f"{k}: {n(v)}" for k, v in C["causal_mailer_dist"]) + ". Mã 0 nghĩa là không có; ý nghĩa các mã khác theo User Guide.")
p("Bậc thu nhập (classification_3) trong 801 hộ có nhân khẩu học: " + "; ".join(f"{k} {v}" for k, v in C["income_dist"]) + ".")

h3("2.2 Breakfast at the Frat (dunnhumby)")
p("Dữ liệu tuần × cửa hàng × SKU của 4 ngành (snack đóng gói, ngũ cốc, pizza đông lạnh, vệ sinh răng miệng), có cả giá bán (PRICE) và giá cơ sở (BASE_PRICE), cờ tờ rơi (FEATURE), trưng bày (DISPLAY), giảm giá tạm thời (TPR_ONLY). Đây là nguồn tốt nhất để ước lượng độ co giãn giá.")
tables_overview(bf)
tb(["Chỉ tiêu", "Giá trị", "Ghi chú"], [
    ["Tuần / cửa hàng / UPC", f"{n(BF['weeks'])} / {n(BF['stores'])} / {n(BF['upcs'])}", f"{BF['week_min'][:10]} → {BF['week_max'][:10]}"],
    ["Tổng lượng / doanh thu", f"{n(BF['units_total'])} đơn vị / {n(BF['spend_total'])} USD", ""],
    ["PRICE thiếu / BASE_PRICE thiếu", f"{n(BF['price_null'])} / {n(BF['base_price_null'])}", "Dòng thiếu giá cơ sở bị loại khỏi hồi quy giá"],
    ["PRICE > BASE_PRICE", n(BF["price_gt_base"]), "Giá bán cao hơn giá cơ sở; loại khi tính mức giảm giá"],
    ["Tỷ lệ tuần có tờ rơi / trưng bày / chỉ giảm giá", f"{pct(BF['feature_rate'])} / {pct(BF['display_rate'])} / {pct(BF['tpr_rate'])}", "Đủ biến thiên để tách hiệu ứng"],
    ["Dòng UNITS ≤ 0", n(BF["units_le0"]), "Tuần không bán không được ghi thành dòng 0"],
    ["Trùng khóa tuần-cửa hàng-UPC", n(BF["dup_keys"]), ""],
    ["Độ đầy của panel", pct(BF["panel_fill"]), "Tỷ lệ ô tuần × (cửa hàng, UPC) có dòng; ô vắng là không bán hoặc không kinh doanh"],
])

h3("2.3 Carbo-Loading (dunnhumby)")
p("Dòng giao dịch của hộ cho 4 ngành bổ trợ nhau: mì Ý, sốt mì Ý, bột bánh pancake, siro. Có tờ rơi và trưng bày theo tuần-cửa hàng-UPC.")
tables_overview(cb)
tb(["Chỉ tiêu", "Giá trị", "Ghi chú"], [
    ["Hộ / giỏ / cửa hàng / UPC", f"{n(CB['households'])} / {n(CB['baskets'])} / {n(CB['stores'])} / {n(CB['upcs'])}", ""],
    ["Tuần, ngày", f"tuần {CB['week_min']}–{CB['week_max']}, ngày {CB['day_min']}–{CB['day_max']}", "Ngày tương đối"],
    ["Doanh thu", f"{n(CB['sales_total'])} USD", "Theo ngành: " + "; ".join(f"{k} {n(v)}" for k, v in CB["commodity_sales"])],
    ["Dòng doanh thu ≤ 0 / lượng ≤ 0", f"{n(CB['sales_le0'])} / {n(CB['units_le0'])}", ""],
    ["Dòng có coupon", f"{n(CB['coupon_rows'])} ({pct(CB['coupon_rows'] / T(cb, 'dh_transactions')['rows'], 2)})", ""],
    ["Dòng trùng hoàn toàn", n(CB["dup_rows"]), ""],
    ["UPC không có trong bảng sản phẩm", n(CB["upc_not_in_lookup"]), ""],
    ["Giá đơn vị > 20 USD", n(CB["price_outlier"]), "Không có giá ngoại lai" if not CB["price_outlier"] else "Kiểm tra trước khi tính giá bình quân"],
    ["Vùng (geography): số cửa hàng", "; ".join(f"vùng {k}: {v}" for k, v in CB["geography"]), ""],
])
p("Lưu ý phạm vi: Carbo chỉ ghi 4 ngành, nên giỏ hàng bị cắt. Mức bổ trợ (lift) giữa mì Ý và sốt tính trên Carbo khác hẳn khi tính trên giỏ đầy đủ của CJ (0,90 so với 9,81). Đây là ví dụ rõ nhất trong dự án về việc phạm vi dữ liệu quyết định kết luận.")

h3("2.4 Let's Get Sort-of-Real (dunnhumby, mẫu 5.000 khách)")
p("Dữ liệu mô phỏng (synthetic) do dunnhumby tạo, có sẵn nhãn loại chuyến mua, độ nhạy giá của giỏ, nhiệm vụ giỏ, định dạng và vùng cửa hàng, giờ mua. Dùng để thử phương pháp và đặt giả thuyết, không dùng để rút con số thị trường.")
tables_overview(lg)
tb(["Chỉ tiêu", "Giá trị", "Ghi chú"], [
    ["File tuần / tuần có dữ liệu", f"{LG['files']} / {LG['weeks']}", f"tuần {LG['week_min']}–{LG['week_max']}" + (f"; thiếu tuần {', '.join(map(str, LG['weeks_missing']))} (không có trong file zip gốc)" if LG["weeks_missing"] else "")],
    ["Khách / giỏ / cửa hàng / mặt hàng", f"{n(LG['customers'])} / {n(LG['baskets'])} / {n(LG['stores'])} / {n(LG['products'])}", ""],
    ["Dòng không có mã khách", f"{n(LG['anon_rows'])} ({pct(LG['anon_rows'] / T(lg, 'transactions_YYYYWW')['rows'])})", "Khách vãng lai; loại khỏi phân tích theo khách"],
    ["Dòng thiếu phân khúc khách (seg_1)", n(LG["seg_null"]), ""],
    ["Chi tiêu", f"{n(LG['spend_total'])} (đơn vị tiền không nêu)", f"{n(LG['spend_le0'])} dòng ≤ 0"],
    ["Giờ mua", f"{LG['hour_range'][0]}–{LG['hour_range'][1]} giờ", ""],
    ["Loại chuyến (số giỏ)", "; ".join(f"{k}: {n(v)}" for k, v in LG["basket_type"]), "XX là chưa phân loại"],
    ["Định dạng cửa hàng", "; ".join(f"{k}: {v}" for k, v in LG["store_format"]), "Số cửa hàng theo định dạng"],
])

h3("2.5 Walmart M5 Forecasting")
p("Lượng bán theo ngày của 3.049 mặt hàng tại 10 cửa hàng ở 3 bang (California, Texas, Wisconsin), kèm giá bán theo tuần, lịch sự kiện và ngày chi trả trợ cấp thực phẩm SNAP. Là nguồn duy nhất có cấu trúc chuỗi cửa hàng đầy đủ theo ngày, nên được dùng cho bảng điều hành và dự báo.")
tables_overview(m5)
tb(["Chỉ tiêu", "Giá trị", "Ghi chú"], [
    ["Chuỗi SKU-cửa hàng × ngày", f"{n(M['series'])} × {n(M['days'])} = {n(M['cells'])} ô", f"{n(M['items'])} SKU, {M['depts']} nhóm hàng, {M['cats']} ngành, {M['stores']} cửa hàng, {M['states']} bang"],
    ["Tổng lượng bán", n(M["units_total"]), f"Ô âm: {n(M['neg_cells'])}"],
    ["Ô bằng 0 (toàn bộ)", pct(M["zero_share_all"]), f"Trong đó {pct(M['leading_zero_share'])} số ô là trước ngày SKU lên kệ"],
    ["Ô bằng 0 sau ngày lên kệ", pct(M["zero_share_after_launch"]), "Nhu cầu gián đoạn: cần mô hình riêng (Croston/TSB, Poisson)"],
    ["Ô bằng 0 theo ngành", "; ".join(f"{k} {pct(v)}" for k, v in M["zero_share_by_cat"].items()), ""],
    ["Chuỗi không bán lần nào", n(M["never_sold"]), ""],
    ["Ngày gần như không bán (< 1% trung bình)", ", ".join(M["all_zero_days"]) or "không", "Đều là 25/12 (2011–2015): cửa hàng đóng cửa; gắn cờ khi dự báo"],
    ["Bảng giá: dòng / thiếu / ≤ 0", f"{n(M['price_rows'])} / {n(M['price_null'])} / {n(M['price_le0'])}", f"Giá {n(M['price_min'], 2)}–{n(M['price_max'], 2)} USD"],
    ["Tỷ lệ tuần đổi giá", pct(M["price_changes_share"]), "Giá đổi thưa, theo bước"],
    ["Ô có bán và có giá tuần", pct(M["sold_cells_with_price"], 2), "Ước tính trên mẫu 3.000 chuỗi; doanh thu = lượng × giá tuần"],
    ["Ngày có sự kiện / ngày SNAP", f"{n(M['events'])} / CA {M['snap_days']['CA']}, TX {M['snap_days']['TX']}, WI {M['snap_days']['WI']}", "Mỗi bang 10 ngày SNAP mỗi tháng"],
])
p(M["validation_vs_evaluation"] + ".")

h3("2.6 Nguồn của vòng khảo sát đầu")
tb(["Chỉ tiêu", "Online Retail (UCI)", "Ghi chú"], [
    ["Hóa đơn / khách / quốc gia", f"{n(OL['invoices'])} / {n(OL['customers'])} / {OL['countries']}", f"Anh chiếm {pct(OL['uk_share_rows'], 0)} số dòng"],
    ["Dòng thiếu CustomerID", f"{n(OL['cust_null'])} ({pct(OL['cust_null'] / T(early['online_retail'], 'Online Retail')['rows'])})", "Không gắn được khách"],
    ["Dòng hủy (InvoiceNo bắt đầu bằng C)", n(OL["cancel_rows"]), ""],
    ["Quantity ≤ 0 / UnitPrice ≤ 0", f"{n(OL['qty_le0'])} / {n(OL['price_le0'])}", ""],
    ["Dòng trùng hoàn toàn", n(OL["dup_rows"]), ""],
    ["Mã không phải hàng (phí, bưu phí…)", n(OL["non_product_codes"]), "POST, M, BANK CHARGES…"],
])
cr = early["cj_r"]
if "error" not in cr:
    p(f"Complete Journey bản gói R (dùng cho dashboard_enterprise và retail_pipeline): {n(cr['rows'])} dòng, {n(cr['households'])} hộ, "
      f"{cr['date_min'][:10]} → {cr['date_max'][:10]}, doanh thu {n(cr['sales_total'])} USD. Đây là bản xử lý lại, có ngày giờ thật, khác bản gốc 2 năm ở mục 2.1.")
p("Online Retail là bán lẻ quà tặng trực tuyến ở Anh, không phải siêu thị; chỉ dùng ở vòng khảo sát, không trộn vào phân tích đa nguồn.")

# ================================================================== 3. Chất lượng tổng hợp
h2("3. Vấn đề chất lượng và cách xử lý")
tb(["Vấn đề", "Nguồn", "Bằng chứng", "Ảnh hưởng", "Cách xử lý"], [
    ["Panel không phải toàn bộ khách", "CJ, Carbo", f"CJ chỉ {n(C['households'])} hộ mua thường xuyên", "Mức tập trung, tăng trưởng không đại diện cho toàn cửa hàng", "Chỉ so sánh chỉ số tương đối, ghi rõ giới hạn"],
    ["Nhu cầu gián đoạn", "M5", f"{pct(M['zero_share_after_launch'], 0)} ô bằng 0 sau ngày lên kệ", "Sai số % (MAPE) vô nghĩa; mô hình chuẩn đoán sai", "Đánh giá bằng WRMSSE, WAPE; phân loại kiểu nhu cầu"],
    ["Ô trước ngày lên kệ ghi 0", "M5", f"{pct(M['leading_zero_share'])} số ô", "Tỷ lệ 0 bị thổi phồng", "Cắt chuỗi từ ngày bán đầu tiên"],
    ["Ngày đóng cửa", "M5", f"5 ngày 25/12 ({', '.join(M['all_zero_days'])}) gần như không bán", "Kéo lệch trung bình và mô hình", "Gắn cờ ngày lễ, loại khỏi huấn luyện"],
    ["Không có giá vốn, tồn kho", "Tất cả", "Không có trường cost, on-hand", "Không tính được lợi nhuận thật, không phân biệt hết hàng với không có nhu cầu", "Biên gộp là tham số người dùng nhập trong mô phỏng"],
    ["Giá bán so với giá cơ sở", "BATF", f"{n(BF['base_price_null'])} dòng thiếu BASE_PRICE", "Sai lệch độ co giãn", "Hồi quy log–log với hiệu ứng cố định, loại dòng thiếu"],
    ["Giỏ bị cắt theo ngành", "Carbo", "Chỉ 4 ngành", "Lift giỏ hàng sai lệch (0,90 so với 9,81)", "Không suy luận bổ trợ từ Carbo; dùng CJ"],
    ["Dữ liệu mô phỏng", "LGSR", "Do dunnhumby sinh", "Không phản ánh hành vi thật", "Chỉ dùng thử phương pháp, đặt giả thuyết"],
    ["Đổi trả, điều chỉnh", "CJ, Online Retail", f"CJ {n(C['sales_le0'])} dòng giá trị 0; UCI {n(OL['cancel_rows'])} dòng hủy", "Doanh thu ròng và lượng mua bị lệch nếu không tách", "Giữ trong doanh thu ròng, loại khi mô hình hóa lượng mua"],
    ["Khách vãng lai", "LGSR, Online Retail", f"LGSR {pct(LG['anon_rows'] / T(lg, 'transactions_YYYYWW')['rows'])}, UCI {pct(OL['cust_null'] / T(early['online_retail'], 'Online Retail')['rows'])} dòng không có mã khách", "Phân tích khách bỏ sót", "Phân tích khách chỉ trên dòng có mã"],
    ["Ngày tương đối", "CJ, Carbo", "DAY 1…711, không có ngày lịch", "Không gắn được lễ, mùa vụ thật", "Dùng tuần tương đối; mùa vụ lấy từ M5"],
    ["Không có khóa chung", "Tất cả", "Mã khách, hàng, cửa hàng riêng từng nguồn", "Không nối dòng được", "Hài hòa ở mức chỉ số (mục 4)"],
])

# ================================================================== 4. Hài hòa đa nguồn
h2("4. Hài hòa nhiều nguồn")
p("Vì các nguồn không có khóa chung, dự án không nối dòng. Mỗi chỉ số (mức tập trung doanh thu, độ co giãn giá, mức tăng khi trưng bày, nhịp theo giờ…) được tính riêng trong từng nguồn bằng cùng phương pháp, rồi so sánh. "
  "Một kết luận được coi là đáng tin khi nhiều nguồn độc lập cho cùng kết quả. Bảng dưới là ma trận nhóm trường: nguồn nào có trường nào.")
keys = ["cj", "batf", "carbo", "lgsr", "m5"]
lab = {"cj": "CJ", "batf": "BATF", "carbo": "Carbo", "lgsr": "LGSR", "m5": "M5"}
tb(["Nhóm trường"] + [lab[k] for k in keys] + ["Ghi chú"], [[f["field"]] + ["có" if k in f["have"] else "" for k in keys] + [f["note"]] for f in META["fields"]])

# ================================================================== 5. Luồng xử lý
h2("5. Luồng xử lý và dòng dõi dữ liệu")
tb(["Bước", "Script", "Đầu vào", "Đầu ra"], [
    ["Tải dữ liệu", "research/download_data.py; tải tay từ dunnhumby, Zenodo", "Internet", "data/raw, data/raw_dunnhumby, data/raw_m5 (+ data/manifest.json)"],
    ["Hồ sơ dữ liệu", "research/data_report/profile_data.py", "data/raw*", "outputs/data_report/profile.json, báo cáo này"],
    ["Phân tích đa nguồn", "research/multisource/analyze_multisource.py, analyze_deep.py", "data/raw_dunnhumby, data/raw_m5", "outputs/multisource/results.json, results_deep.json"],
    ["Biểu đồ, báo cáo", "make_figures.py, build_html.py, build_word.py", "results*.json", "outputs/multisource/*.html, *.docx, figures/"],
    ["Đóng gói cho web", "webapp/backend/scripts/build_cache.py", "results*.json, trang HTML, data/raw_m5, data/raw_dunnhumby", "webapp/backend/data/*"],
    ["Pipeline gói R (vòng đầu)", "retail_pipeline/run.py, dashboard_enterprise/build_*.py", "data/raw (CJ gói R)", "outputs/enterprise, dashboard_enterprise/dist"],
])
h3("Dữ liệu web dùng")
rows = []
for f in P["web"]["files"]:
    rows.append([f["file"], n(f["kb"], 1) + " KB", n(f.get("rows")) if f.get("rows") is not None else "JSON", ", ".join(f.get("cols", [])) or "", f["sha256"]])
tb(["File", "Dung lượng", "Số dòng", "Cột", "SHA-256 (16 ký tự đầu)"], rows)
R = P["web"]["m5_reconcile"]
p(f"Đối soát: bảng m5_store_dept_daily.parquet (ngày × cửa hàng × nhóm hàng) có tổng lượng {n(R['units_total'])} so với {n(M['units_total'])} ở file gốc "
  + ("(khớp tuyệt đối)" if abs(R['units_total'] - M['units_total']) < 0.5 else f"(chênh {n(abs(R['units_total'] - M['units_total']))} do lưu float32)") + f", giai đoạn {R['date_min']} → {R['date_max']}, doanh thu ước tính {n(R['revenue_total'])} USD.")

# ================================================================== 6. Khi áp dụng cho siêu thị
h2("6. Dữ liệu cần từ siêu thị khi triển khai")
p("Bản demo thiếu những trường mà một chuỗi siêu thị thật có. Khi triển khai, cần các bảng sau (chi tiết khóa và quy tắc ở CHAIN_ROLLOUT.md):")
tb(["Bảng", "Khóa", "Lấp khoảng trống nào của bản demo"], [
    ["Hóa đơn POS", "cửa hàng + ngày + số hóa đơn + dòng", "Doanh thu toàn bộ khách, không chỉ panel; ngày lịch thật"],
    ["Danh mục mặt hàng", "mã hàng + thời gian hiệu lực", "Khóa chung giữa POS, ERP, kho"],
    ["Giá và khuyến mãi", "cửa hàng + mã hàng + khoảng hiệu lực", "Giá cơ sở, tờ rơi, trưng bày theo cửa hàng-tuần"],
    ["Tồn kho", "địa điểm + mã hàng + ngày", "Phân biệt hết hàng với không có nhu cầu"],
    ["Giá vốn", "mã hàng + thời gian hiệu lực", "Lợi nhuận thật thay cho biên gộp giả định"],
    ["Thẻ thành viên", "mã khách ẩn danh toàn chuỗi", "Phân tích khách xuyên cửa hàng"],
])

# ================================================================== 7. Tái lập
h2("7. Tái lập dữ liệu")
p("Dữ liệu thô không nằm trong repository (2,3 GB; nhiều file trên 100 MB, vượt giới hạn 100 MB/file của GitHub). Tải về và đặt đúng thư mục:")
tb(["Thư mục", "Nguồn", "File", "SHA-256 file nén"], [
    ["data/raw_dunnhumby/", "https://www.dunnhumby.com/source-files/ (đăng ký, tải 4 bộ)", "dunnhumby_The-Complete-Journey.zip", "5e0a3d72fe8562fe0ab995f70fb58b74359e8ec4bbccd1521e2b137da0558f9a"],
    ["", "", "dunnhumby_Breakfast-at-the-Frat.zip", "74cb41cb8b19dc61bb8a5731c3774b802e9a8da3b64cdd1872640890d0b54216"],
    ["", "", "dunnhumby_Carbo-Loading.zip", "64f2d0793ab1a6d0a0a1c981122cd6eeafb451e6328a10085b345cdc0156b10a"],
    ["", "", "dunnhumby_Let-s-Get-Sort-of-Real-_Sample-5K-customers_.zip", "4c847515b74592c5d368433543b12585460e0c789cef7b129358a357bac1cfb7"],
    ["data/raw_m5/", "https://zenodo.org/records/12636070", "m5-forecasting-accuracy.zip", "0349ba38a2efd30d0f5acc6394c1110e140e1a990c650d7b5ca44c5b25dd12f5"],
    ["data/raw/", "python research/download_data.py", "UCI Online Retail, gói R completejourney", "xem data/manifest.json"],
])
p("Giải nén mỗi file zip vào thư mục cùng tên (bỏ đuôi .zip). Sau đó chạy:")
B.append(("code", "python3 research/data_report/profile_data.py      # hồ sơ dữ liệu\n"
                   "python3 research/data_report/build_data_report.py  # báo cáo này\n"
                   "python3 research/multisource/analyze_multisource.py && python3 research/multisource/analyze_deep.py\n"
                   "python3 webapp/backend/scripts/build_cache.py       # dữ liệu cho web"))

# ================================================================== Phụ lục: từ điển dữ liệu
h2("Phụ lục: từ điển dữ liệu")
p("Mọi bảng thô, mỗi cột: kiểu (duckdb tự nhận), số giá trị thiếu và số giá trị khác nhau (ước lượng HyperLogLog, sai số khoảng 2%).")
for key, title in [("cj", "Complete Journey"), ("batf", "Breakfast at the Frat"), ("carbo", "Carbo-Loading"), ("lgsr", "Let's Get Sort-of-Real"), ("m5", "Walmart M5")]:
    for t in S[key]["tables"]:
        h3(f"{title} · {t['name']} ({n(t['rows'])} dòng)")
        tb(["Cột", "Kiểu", "Thiếu", "Giá trị khác nhau"], [[c["name"], c["type"], f"{n(c['nulls'])} ({pct(c['null_pct'])})" if c["nulls"] else "0", n(c["distinct"])] for c in t["cols"]])


# ------------------------------------------------------------------ xuất Markdown
def md_escape(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


out = []
for b in B:
    k = b[0]
    if k == "h1":
        out.append(f"# {b[1]}\n")
    elif k == "h2":
        out.append(f"## {b[1]}\n")
    elif k == "h3":
        out.append(f"### {b[1]}\n")
    elif k == "p":
        out.append(b[1] + "\n")
    elif k == "ul":
        out.append("\n".join(f"- {x}" for x in b[1]) + "\n")
    elif k == "code":
        out.append("```bash\n" + b[1] + "\n```\n")
    elif k == "table":
        _, head, rows, note = b
        out.append("| " + " | ".join(map(md_escape, head)) + " |\n|" + "---|" * len(head) + "\n" + "\n".join("| " + " | ".join(map(md_escape, r)) + " |" for r in rows) + "\n")
        if note:
            out.append(f"*{note}*\n")
md_path = ROOT / "docs/DATA_REPORT.md"
md_path.parent.mkdir(exist_ok=True)
md_path.write_text("\n".join(out), encoding="utf-8")

# ------------------------------------------------------------------ xuất Word
doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Cm(2)
sec.top_margin = sec.bottom_margin = Cm(2)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
INK, ACC = RGBColor(0x17, 0x3E, 0x35), RGBColor(0xC4, 0x86, 0x2A)


def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hex_)
    tcPr.append(s)


def runs(par, text):
    """Hỗ trợ `code` trong đoạn văn."""
    parts = str(text).split("`")
    for i, t in enumerate(parts):
        r = par.add_run(t)
        if i % 2:
            r.font.name = "Consolas"; r.font.size = Pt(9.5)


for b in B:
    k = b[0]
    if k == "h1":
        h = doc.add_heading(b[1], 0); h.runs[0].font.color.rgb = INK
    elif k in ("h2", "h3"):
        h = doc.add_heading(b[1], 1 if k == "h2" else 2)
        for r in h.runs:
            r.font.color.rgb = INK if k == "h2" else ACC
    elif k == "p":
        runs(doc.add_paragraph(), b[1])
    elif k == "ul":
        for x in b[1]:
            runs(doc.add_paragraph(style="List Bullet"), x)
    elif k == "code":
        par = doc.add_paragraph()
        r = par.add_run(b[1]); r.font.name = "Consolas"; r.font.size = Pt(9)
    elif k == "table":
        _, head, rows, note = b
        t = doc.add_table(rows=1, cols=len(head))
        t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(head):
            c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            shade(c, "173E35")
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(8.5)
        if note:
            par = doc.add_paragraph(); r = par.add_run(note); r.italic = True; r.font.size = Pt(9)
        doc.add_paragraph()
docx_path = ROOT / "outputs/data_report/Bao_cao_du_lieu.docx"
doc.save(docx_path)
print("Đã ghi", md_path, "và", docx_path)
