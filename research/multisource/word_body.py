# Thân báo cáo Word — được build_word.py exec() sau phần helper. Dùng chung biến: doc, para, bullet, lens, table, toc, H, n, p, mil ...
import json as _json

D2 = _json.loads((H.OUT / "results_deep.json").read_text(encoding="utf-8"))
cj2, ba2, m52, cl2 = D2["cj"], D2["batf"], D2["m5"], D2["carbo"]
SHOTS = H.OUT / "screens"
WEB_URL = "https://claude.ai/artifact/RzirnZ38DAooHUMgoBWC52 (bản trực tuyến, riêng tư — chia sẻ qua nút Share) và tệp outputs/multisource/Phan_tich_da_nguon.html (mở trực tiếp bằng trình duyệt)"
el_b, el_c, el_m, snap, cds, ct, cause, inc, incpl, comp, loy, cl_comm = H.el_b, H.el_c, H.el_m, H.snap, H.cds, H.ct, H.cause, H.inc, H.incpl, H.comp, H.loy, H.cl_comm
traj = {t["traj"]: t for t in cj2["trajectory"]}
gd = cj2["growth_decomp"]
rfm = {x["segment"]: x for x in cj2["rfm"]}
ps = cj2["pasta_sauce_full"]
dyn = {x["category"]: x for x in ba2["dynamics"]}
ler = {x["category"]: x for x in ba2["lerner"]}
fc = sorted(m52["forecast"], key=lambda x: x["wrmsse_item"])
fcm = {x["model"]: x for x in m52["forecast"]}
best = fc[0]
pcf = {x["cat"]: x for x in m52["price_change_freq"]}
pcs = {x["cat"]: x for x in m52["price_change_size"]}
hhi = {h["commodity"]: h["hhi"] for h in CL["hhi"]}
FIGN = [0]
TABN = [0]


def fig(name, caption, width=16, folder=None):
    FIGN[0] += 1
    doc.add_picture(str((folder or FIG) / name), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    para(f"Hình {FIGN[0]}. {caption}", italic=True, size=9, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)


def tab(caption, *a, **k):
    TABN[0] += 1
    pa = para(f"Bảng {TABN[0]}. {caption}", bold=True, size=9.5, color=BRAND, after=3)
    pa.paragraph_format.keep_with_next = True
    return table(*a, **k)


def part(title, sub):
    doc.add_page_break()
    para(title, bold=True, size=26, color=BRAND, after=6)
    para(sub, size=12, color=MUTED, after=12)


def h1(t):
    doc.add_heading(t, 1)


def h2(t):
    doc.add_heading(t, 2)


def take(items):
    pa = para("Điều rút ra", bold=True, size=10, color=ACCENT, after=2)
    pa.paragraph_format.keep_with_next = True
    for t in items:
        bullet(t)


# =========================================================================== BÌA
for _ in range(4):
    para()
para("RETAIL INTELLIGENCE · PHÂN TÍCH ĐA NGUỒN", bold=True, size=10, color=ACCENT)
para("Phân tích dữ liệu bán lẻ đa nguồn và hệ thống web trình bày kết quả", bold=True, size=26, color=BRAND, after=12)
para("Báo cáo gồm ba phần: (I) phân tích dữ liệu theo góc độ dữ liệu và góc độ kinh tế trên 5 bộ dữ liệu công khai; "
     "(II) xây dựng trang web phân tích; (III) mô tả chi tiết từng phần của trang web.", size=12, color=MUTED, after=24)
table(["Hạng mục", "Nội dung"], [
    ["Dữ liệu", f"dunnhumby Complete Journey (bản gốc 2 năm), Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real (mẫu 5K khách); Walmart M5. Tổng {n(H.TOTAL_ROWS / 1e6, 0)} triệu dòng/ô."],
    ["Trang web", WEB_URL],
    ["Mã nguồn", "research/multisource/ (phân tích, biểu đồ, web, báo cáo)"],
    ["Ngày lập", "07/11/2026"],
], widths=[3.5, 13])
doc.add_page_break()

# =========================================================================== TÓM TẮT
h1("Tóm tắt điều hành")
para("Báo cáo trả lời một câu hỏi: những quy luật nào trong dữ liệu bán lẻ đủ ổn định để chuỗi siêu thị dựa vào khi ra quyết định về giá, khuyến mãi, khách hàng và tồn kho. "
     "Năm bộ dữ liệu không có khóa chung nên được **hài hòa ở mức chỉ số**: mỗi chỉ số được ước lượng riêng trong từng nguồn bằng cùng phương pháp rồi đối chiếu. "
     "Kết luận lặp lại ở nhiều nguồn độc lập được coi là đáng tin hơn. Kết quả được trình bày trên một trang web tương tác gồm 12 chương và 29 biểu đồ.")
h2("Mười phát hiện chính")
for t in [
    f"**Doanh thu tập trung mạnh.** 20% khách hoặc mặt hàng tạo 53–66% doanh thu ở cả 4 nguồn có số liệu.",
    f"**Tăng trưởng đến từ giỏ lớn hơn.** Doanh thu panel CJ tăng {p(2.718281828 ** gd['sales'] - 1)} giữa đầu và cuối kỳ; hơn một nửa nhờ giá trị giỏ, phần nhỏ nhờ thêm hộ và thêm chuyến.",
    f"**Độ nhạy giá phụ thuộc ngành.** Pizza đông lạnh {n(el_b['FROZEN PIZZA']['elasticity'], 2)}, ngũ cốc {n(el_b['COLD CEREAL']['elasticity'], 2)}; mì Ý, sốt, siro và ba ngành Walmart chỉ −0,27 đến −0,54.",
    "**Vị trí kệ và tờ rơi quan trọng hơn mức giảm.** Giữ giá cố định, trưng bày tăng lượng bán 28–69% (BATF) và 33–47% (Carbo). Cờ giảm giá tạm thời không có tác dụng thêm.",
    f"**Khuyến mãi ăn mòn SKU cùng ngành.** Khi các SKU khác cùng ngành khuyến mãi, lượng bán một SKU giảm 5–22%.",
    "**Giảm giá thường lỗ nếu không kèm trưng bày.** Ở biên gộp 30%, giảm 10% đơn thuần làm giảm lợi nhuận ở cả 4 ngành; kèm trưng bày thì 3/4 ngành có lãi.",
    f"**Đo coupon dễ nhầm do chọn mẫu.** Hộ nhận chiến dịch đã chi gấp 2,3–2,8 lần hộ khác từ trước; chênh lệch tăng trưởng gần 0.",
    f"**Dòng tiền hộ quyết định thời điểm mua.** Ngày nhận SNAP làm thực phẩm tăng {p(snap[('CA', 'FOODS')]['lift'])}–{p(snap[('WI', 'FOODS')]['lift'])}.",
    f"**Phạm vi dữ liệu quyết định kết luận giỏ hàng.** Lift mì Ý + sốt là {n(ps['lift'], 1)} trên giỏ đầy đủ nhưng {n(comp[('pasta', 'pasta sauce')]['lift'], 2)} trên dữ liệu đã lọc ngành.",
    f"**Học máy cải thiện dự báo, nhưng mô hình đơn giản đã gần bằng.** GBM đạt WRMSSE {n(best['wrmsse_item'], 3)}, trung bình 28 ngày {n(fcm['Trung bình 28 ngày']['wrmsse_item'], 3)}, naive mùa vụ {n(fcm['Naive mùa vụ 7 ngày']['wrmsse_item'], 3)}.",
]:
    bullet(t)
para("Giới hạn chung: dữ liệu Mỹ và Anh 2006–2016; Let's Get Sort-of-Real là dữ liệu mô phỏng; không có giá vốn và tồn kho. Kết quả dùng để đặt giả thuyết và chọn phương pháp cho chuỗi Việt Nam.",
     italic=True, color=MUTED)
doc.add_page_break()
h1("Mục lục")
toc()

# =========================================================================== PHẦN I
part("PHẦN I", "Phân tích dữ liệu: góc độ dữ liệu và góc độ kinh tế")

h1("1. Mục tiêu, câu hỏi và cách đọc")
para("Phần này trả lời tám câu hỏi nghiệp vụ, mỗi câu gắn với một chương:")
table(["#", "Câu hỏi", "Nguồn chính", "Chương"], [
    ["Q1", "Doanh thu phụ thuộc vào bao nhiêu khách và mặt hàng?", "CJ, Carbo, LGSR, M5", "5"],
    ["Q2", "Tăng trưởng đến từ đâu; khách nào đang tăng, giảm, rời bỏ?", "CJ", "6"],
    ["Q3", "Khách phản ứng với giá mạnh đến đâu; biên lợi nhuận hợp lý là bao nhiêu?", "BATF, Carbo, M5", "7"],
    ["Q4", "Khuyến mãi tạo thêm bao nhiêu lượng bán và lợi nhuận?", "CJ, BATF, Carbo", "8–9"],
    ["Q5", "Lịch, ngày lễ và trợ cấp ảnh hưởng thế nào?", "M5", "10"],
    ["Q6", "Thu nhập, nhãn riêng và thương hiệu tương tác ra sao?", "CJ, BATF, Carbo", "11"],
    ["Q7", "Khách mua gì cùng nhau, vào lúc nào?", "CJ, Carbo, LGSR", "12"],
    ["Q8", "Dự báo được nhu cầu chính xác đến mức nào?", "M5", "13"],
], widths=[1, 8.5, 4, 2], font=9)
para("Mỗi phát hiện có hai khung: **Góc dữ liệu** (đo cái gì, ở hạt nào, sai lệch nào có thể làm lệch con số) và **Góc kinh tế** (cơ chế hành vi hoặc thị trường và hệ quả cho quyết định).")

h1("2. Nguồn dữ liệu")
tab("Tổng quan năm nguồn", ["Nguồn", "Quy mô", "Hạt dữ liệu", "Trả lời được"],
    [[f"**{t}**\n{sub}", desc, grain, ans] for k, t, sub, desc, grain, ans in H.SOURCES], widths=[3.4, 6, 3.4, 3.8], font=8.5)
para("Tải ngày 07/11/2026 từ dunnhumby.com/source-files (tải trực tiếp, kiểm tra SHA-256) và Zenodo (M5, DOI 10.5281/zenodo.12636070, CC BY 4.0, md5 khớp). "
     "Let's Get Sort-of-Real dùng mẫu 5.000 khách thay vì bản đầy đủ 4,3 GB nén.", size=9.5, color=MUTED)

h2("2.1. Từ điển trường theo nguồn")
DICT = {
    "The Complete Journey": [
        ("transaction_data", "household_key, BASKET_ID, DAY (1–711), PRODUCT_ID, QUANTITY, SALES_VALUE, STORE_ID, RETAIL_DISC, COUPON_DISC, COUPON_MATCH_DISC, TRANS_TIME, WEEK_NO",
         "SALES_VALUE là tiền nhà bán lẻ nhận (đã trừ giảm giá thẻ, cộng bù coupon). Giá kệ = (SALES_VALUE − RETAIL_DISC − COUPON_MATCH_DISC)/QUANTITY."),
        ("product", "PRODUCT_ID, MANUFACTURER, DEPARTMENT, BRAND (Private/National), COMMODITY_DESC, SUB_COMMODITY_DESC, CURR_SIZE_OF_PRODUCT", "Ba cấp phân loại; BRAND chỉ phân biệt nhãn riêng/quốc gia."),
        ("hh_demographic", "classification_1…5 (tuổi, hôn nhân, thu nhập Level1–12, quy mô hộ, thành phần hộ), HOMEOWNER_DESC, KID_CATEGORY_DESC", "Bản mới ẩn tên nhãn, giữ thứ bậc; 801 hộ."),
        ("causal_data", "product_id, store_id, week_no, display (0–9, A), mailer (0, A–Z)", "36,8 triệu dòng; mã vị trí trưng bày/trang tờ rơi."),
        ("campaign_*, coupon*", "Loại chiến dịch A/B/C, ngày bắt đầu/kết thúc, hộ nhận, coupon và sản phẩm áp dụng, lượt đổi", "TypeA cá nhân hóa 16 coupon/hộ."),
    ],
    "Breakfast at the Frat": [
        ("Transaction Data", "WEEK_END_DATE, STORE_NUM, UPC, UNITS, VISITS, HHS, SPEND, PRICE, BASE_PRICE, FEATURE, DISPLAY, TPR_ONLY", "PRICE là giá thực; BASE_PRICE là giá cơ sở; ba cờ khuyến mãi 0/1."),
        ("Store Lookup", "STORE_ID, tên, thành phố, bang, MSA, SEG_VALUE_NAME (Value/Mainstream/Upscale), PARKING_SPACE_QTY, SALES_AREA_SIZE_NUM, AVG_WEEKLY_BASKETS", "Thuộc tính cửa hàng hiếm có trong dữ liệu công khai."),
        ("Products Lookup", "UPC, DESCRIPTION, MANUFACTURER, CATEGORY, SUB_CATEGORY, PRODUCT_SIZE", "55 SKU, có nhãn riêng."),
    ],
    "Carbo-Loading": [
        ("dh_transactions", "upc, dollar_sales, units, time_of_transaction, geography (1/2), week, household, store, basket, day, coupon (0/1)", "5,2 triệu dòng; coupon chỉ là cờ."),
        ("dh_product_lookup", "upc, product_description, commodity, brand, product_size", "4 ngành, 927 SKU."),
        ("dh_causal_lookup", "upc, store, week, feature_desc, display_desc, geography", "Chỉ tuần 43–104."),
    ],
    "Let's Get Sort-of-Real": [
        ("transactions_YYYYWW", "SHOP_WEEK, SHOP_DATE, SHOP_WEEKDAY, SHOP_HOUR, QUANTITY, SPEND, PROD_CODE (+4 cấp), CUST_CODE, seg_1, seg_2, BASKET_ID, BASKET_SIZE, BASKET_PRICE_SENSITIVITY, BASKET_TYPE, BASKET_DOMINANT_MISSION, STORE_CODE, STORE_FORMAT, STORE_REGION",
         "Dữ liệu mô phỏng; nhãn giỏ và phân khúc có sẵn."),
    ],
    "M5 Walmart": [
        ("sales_train_evaluation", "id, item_id, dept_id, cat_id, store_id, state_id, d_1…d_1941", "Bảng rộng; mỗi ô là lượng bán ngày."),
        ("sell_prices", "store_id, item_id, wm_yr_wk, sell_price", "Giá theo tuần; thiếu khi SKU chưa bán."),
        ("calendar", "date, wm_yr_wk, weekday, wday, month, year, d, event_name_1/2, event_type_1/2, snap_CA, snap_TX, snap_WI", "Biến chính sách SNAP và sự kiện."),
    ],
}
for ds, rows in DICT.items():
    tab(f"Từ điển trường — {ds}", ["Bảng", "Trường", "Ghi chú"], [[a, b, c] for a, b, c in rows], widths=[3, 8.3, 5.3], font=8.3)

h2("2.2. Ma trận trường dữ liệu")
para("Trộn nhiều nguồn có lợi vì mỗi nguồn có những trường nguồn khác không có. Không nguồn nào có đủ cả giá cơ sở, mã khách, tồn kho và giá vốn — bốn trường cần cho bài toán giá–khuyến mãi–tồn kho hoàn chỉnh.")
tab("Nhóm trường có trong từng nguồn", ["Nhóm trường", "CJ", "BATF", "Carbo", "LGSR", "M5", "Ghi chú"],
    [[f, *["●" if s in have else "" for s in ["cj", "batf", "carbo", "lgsr", "m5"]], note] for f, have, note in H.FIELDS],
    widths=[4.2, 1, 1.1, 1.2, 1.1, 1, 6.2], font=8.5)

h1("3. Phương pháp luận")
h2("3.1. Vì sao không nối dòng giữa các nguồn")
para("Năm nguồn khác nhau về quốc gia, thời kỳ (2006–2016), nhà bán lẻ và mã hóa. Không có khóa khách hàng, sản phẩm hay cửa hàng chung. Nối dòng (ví dụ ghép giá BATF vào giao dịch CJ theo tên ngành) "
     "sẽ tạo quan hệ giả. Thay vào đó báo cáo dùng **hài hòa ở mức chỉ số**: định nghĩa một chỉ số (độ co giãn, mức tăng do trưng bày, tỷ trọng top 20%, lift), tính riêng trong từng nguồn với cùng mô hình, rồi đặt cạnh nhau. "
     "Đây là cách làm của phân tích tổng hợp (meta-analysis): độ tin cậy của một kết luận tăng theo số nguồn độc lập cho cùng kết quả.")
h2("3.2. Các mô hình dùng trong báo cáo")
tab("Mô hình và định nghĩa", ["Chỉ số", "Định nghĩa / mô hình", "Nguồn"], [
    ["Độ co giãn giá", "log(lượng) = β·log(giá) + γ·(tờ rơi, trưng bày, TPR) + α(SKU×cửa hàng) + δ(tuần) + ε. β là độ co giãn. Khử hiệu ứng cố định hai chiều bằng khử trung bình lặp; sai số chuẩn cụm theo SKU×cửa hàng.", "BATF, Carbo, M5"],
    ["Hiệu ứng khuyến mãi", "exp(γ) − 1 trong cùng mô hình; CJ dùng biến trưng bày/tờ rơi và tương tác.", "CJ, BATF, Carbo"],
    ["Mua dồn, ăn mòn", "Thêm biến trễ khuyến mãi 1–2 tuần và tỷ lệ SKU khác cùng ngành đang khuyến mãi.", "BATF"],
    ["Biên Lerner", "(P − MC)/P = 1/|β|: biên tối ưu nếu định giá độc lập từng SKU.", "BATF"],
    ["Hiệu ứng SNAP", "log(lượng ngày) = θ·SNAP + FE(năm-tháng) + FE(thứ) + sự kiện; sai số HAC 7 trễ.", "M5"],
    ["DiD chiến dịch", "(tăng trưởng chi/ngày trong chiến dịch so với 30 ngày trước)_nhận − (…)_không nhận.", "CJ"],
    ["Tập trung", "Đường Lorenz, hệ số Gini, tỷ trọng top 20%.", "CJ, Carbo, LGSR, M5"],
    ["Luật kết hợp", "support = P(A∩B); confidence = P(B|A); lift = P(A∩B)/(P(A)P(B)).", "CJ, Carbo"],
    ["RFM", "Recency, Frequency, Monetary chấm 1–5 theo nhóm 20%, gộp thành 7 phân khúc.", "CJ"],
    ["Dự báo", "Naive, naive mùa vụ, trung bình 28 ngày, trung bình theo thứ 8 tuần, GBM Poisson toàn cục (độ trễ ≥ 28). Chấm bằng WRMSSE cấp SKU và WAPE trên 28 ngày cuối.", "M5"],
    ["Kiểu nhu cầu", "Syntetos–Boylan: ADI (khoảng cách trung bình giữa ngày có bán) và CV² (biến thiên lượng khi có bán).", "M5"],
], widths=[3, 10.5, 3], font=8.5)

h1("4. Chất lượng dữ liệu và đối soát")
tab("Giới hạn chính và cách xử lý", ["Nguồn", "Giới hạn chính", "Bằng chứng trong dữ liệu", "Cách xử lý"],
    [[{"cj": "CJ", "batf": "BATF", "carbo": "Carbo", "lgsr": "LGSR", "m5": "M5"}[s], a, b, c] for s, a, b, c in H.QUALITY], widths=[1.4, 3.6, 6.3, 5.4], font=8.5)
tab("Kiểm tra định lượng", ["Chỉ tiêu", "CJ", "BATF", "Carbo", "LGSR", "M5"], [
    ["Số dòng", n(CJ["profile"]["rows"]), n(BA["profile"]["rows"]), n(CL["profile"]["rows"]), n(LG["profile"]["rows"]), f"{n(H.M5_CELLS)} ô"],
    ["Thời gian", "102 tuần", "156 tuần", "104 tuần", f"{LG['profile']['weeks']} tuần", f"{n(M5['profile']['days'])} ngày"],
    ["Dòng trùng hoàn toàn", n(CJ["profile"]["duplicate_rows"]), "–", "–", "–", "–"],
    ["Giá trị ≤ 0", n(CJ["profile"]["nonpos_sales"]), n(BA["profile"]["nonpos_units"]), n(CL["profile"]["nonpos_sales"]), n(LG["profile"]["nonpos_spend"]), f"{p(M5['profile']['zero_share'])} ô = 0"],
    ["Mã SP không khớp", n(CJ["profile"]["unmatched_products"]), "0", n(CL["profile"]["unmatched_upc"]), "–", "–"],
    ["Hoạt động thương mại", f"{mil(CJ['profile']['causal_rows'])} dòng", "Cột trong bảng", f"{n(CL['profile']['causal_rows'])} dòng", "Không", "Sự kiện, SNAP"],
    ["Thông tin khách", f"Nhân khẩu {CJ['profile']['demographic_households']}/2.500 hộ", "Không", "Không nhân khẩu", f"{p(LG['profile']['share_rows_no_card'])} dòng không thẻ", "Không"],
    ["Giá bất thường", "–", f"{n(BA['profile']['price_above_base'])} dòng giá > giá cơ sở", "–", "–", "Thiếu giá khi chưa bán"],
], widths=[3.6, 2.8, 2.6, 2.8, 2.4, 2.5], font=8.5)
para("Quy tắc làm sạch: giữ nguyên dữ liệu gốc khi mô tả; trong mô hình chỉ dùng dòng có lượng và giá trị dương; loại xăng dầu và giao dịch không phải hàng hóa khỏi phân tích giỏ và trưng bày; "
     "kiểm tra khóa danh mục duy nhất trước khi nối để tránh nhân doanh thu.")
fig("f11_m5.png", "Lượng bán theo tháng và kiểu nhu cầu SKU-cửa hàng (M5).")
lens(f"{p(H.intermittent_all)} chuỗi SKU-cửa hàng có nhu cầu gián đoạn hoặc cục; ở Thực phẩm chỉ {p(H.foods_smooth_share)} chuỗi bán đều. Tỷ lệ ngày bằng 0: Thực phẩm {p(H.zero['FOODS'])}, Gia dụng {p(H.zero['HOUSEHOLD'])}, Sở thích {p(H.zero['HOBBIES'])}. 25/12 hằng năm gần như không có giao dịch.",
     "Lượng bán bằng 0 có thể là không có cầu hoặc hết hàng. Thiếu tồn kho, mô hình đánh giá thấp nhu cầu của mặt hàng hay hết hàng và chuỗi tiếp tục nhập thiếu. Chuỗi cần ghi tồn kho đầu ngày.")

# --- 5 Tập trung
h1("5. Tập trung doanh thu")
fig("f01_lorenz.png", "Đường Lorenz của 5 góc nhìn.")
tab("Chỉ số tập trung", ["Góc nhìn", "Số đơn vị", "Top 1%", "Top 20%", "Gini"],
    [[l["name"], n(l["p"]["n"]), p(l["p"]["top1"], 1), p(l["p"]["top20"], 1), n(l["p"]["gini"], 3)] for l in H.DATA["lorenz"]], widths=[5, 3, 2.6, 2.6, 2.6], font=9)
lens("Panel CJ chỉ gồm hộ mua thường xuyên, nên mức tập trung của toàn bộ khách cửa hàng có thể còn cao hơn. LGSR là mô phỏng nhưng cho đường gần giống dữ liệu thật — dấu hiệu nhà phát hành đã hiệu chỉnh theo phân phối thực.",
     f"Giá trị kinh tế nằm ở việc giữ nhóm đầu: mất 1% hộ đầu CJ tương đương mất {p(CJ['pareto_households']['top1'])} doanh thu. 40% SKU bán chậm nhất M5 chỉ tạo {p(1 - M5['pareto_items']['curve'][7]['share'])} doanh thu nhưng chiếm kệ và vốn lưu động.")
take(["Ngân sách CRM chia theo giá trị vòng đời, không chia đều.", "Rà soát đuôi dài danh mục mỗi quý theo doanh thu và biên."])

# --- 6 Khách hàng theo thời gian
h1("6. Khách hàng theo thời gian")
fig("f15_customers.png", "Ba động lực doanh thu theo chu kỳ 4 tuần và quỹ đạo từng hộ (CJ).")
tab("Phân rã tăng trưởng (kỳ 3–8 so với kỳ 20–25, điểm log)", ["Thành phần", "Đóng góp"],
    [["Doanh thu", n(gd["sales"] * 100, 1)], ["Số hộ hoạt động", n(gd["hh"] * 100, 1)], ["Chuyến mỗi hộ", n(gd["trips_per_hh"] * 100, 1)], ["Giá trị mỗi giỏ", n(gd["aov"] * 100, 1)]], widths=[8, 4], font=9)
lens("Hai kỳ đầu thấp do hộ được đưa vào panel dần, nên so kỳ 3–8 với kỳ 20–25. Phân tích quỹ đạo chỉ gồm hộ có giao dịch trong 120 ngày đầu. "
     f"{n(traj['Tăng chi (>+20%)']['households'])} hộ tăng chi >20% là con số cao bất thường; có thể do hộ dùng thẻ thành viên đều hơn theo thời gian chứ không hẳn chi tiêu thật tăng.",
     f"Hơn một nửa mức tăng đến từ giá trị giỏ: hộ dồn thêm chi tiêu vào cửa hàng (tăng thị phần ví) chứ không đến thường xuyên hơn. Nhóm giảm chi và rời bỏ mất {n(-(traj['Giảm chi (<−20%)']['delta'] + traj['Rời bỏ (≥8 tuần không mua)']['delta']))} USD, "
     f"bằng {p(-(traj['Giảm chi (<−20%)']['delta'] + traj['Rời bỏ (≥8 tuần không mua)']['delta']) / traj['Tăng chi (>+20%)']['delta'])} phần tăng của nhóm tăng chi. Phần giá trị giỏ còn chứa lạm phát giá cần trừ trước khi gọi là tăng trưởng thực.")
fig("f16_rfm.png", "Phân khúc RFM tại ngày 711 (CJ).")
tab("Phân khúc RFM", ["Phân khúc", "Số hộ", "% hộ", "% doanh thu", "Chi TB/hộ (USD)", "Recency trung vị (ngày)", "Số giỏ trung vị"],
    [[x["segment"], n(x["households"]), p(x["hh_share"], 1), p(x["rev_share"], 1), n(x["avg_m"]), n(x["recency"]), n(x["frequency"])] for x in cj2["rfm"]], widths=[4, 1.6, 1.6, 2, 2.4, 2.6, 2.2], font=8.5)
lens("RFM chỉ cần mã khách, ngày và số tiền — có ở mọi hệ thống POS có thẻ thành viên — nên chuyển sang chuỗi Việt Nam ngay được. Ngưỡng theo nhóm 20% là tương đối.",
     f"Nhóm 'Có nguy cơ mất' chỉ {p(rfm['Có nguy cơ mất (giá trị cao)']['hh_share'])} số hộ nhưng chi bình quân {n(rfm['Có nguy cơ mất (giá trị cao)']['avg_m'])} USD/hộ, cao hơn nhóm 'Trung thành'. Đây là nơi chi phí giữ chân có lợi nhất.")
take(["Theo dõi hằng tháng ba động lực: số khách hoạt động, tần suất, giá trị giỏ.", "Ưu tiên chăm sóc nhóm giá trị cao đang giảm tần suất."])

# --- 7 Giá
h1("7. Giá và độ co giãn")
fig("f02_elasticity.png", "Độ co giãn của lượng bán theo giá, khoảng tin cậy 95%.")
tab("Ước lượng độ co giãn", ["Nguồn · ngành", "Co giãn", "KTC 95%"],
    [[e["name"], n(e["v"], 2), f"{n(e['lo'], 2)} → {n(e['hi'], 2)}"] for e in H.DATA["elasticity"]], widths=[8, 3, 5], font=9)
lens("BATF đo trên giá kệ so với giá cơ sở nên sạch nhất. Carbo và M5 suy giá từ doanh thu/đơn vị hoặc giá niêm yết tuần; biến động giá nhỏ và có sai số đo nên hệ số bị kéo về 0. Chỉ so thứ hạng giữa nguồn, không so trị tuyệt đối.",
     f"Pizza đông lạnh ({n(el_b['FROZEN PIZZA']['elasticity'], 2)}) nhạy nhất: nhiều sản phẩm thay thế và dễ tích trữ. Với |e| < 1, tăng giá nhẹ làm tăng doanh thu; với |e| > 1, giảm giá có thể tăng doanh thu nhưng chỉ có lãi khi |e| lớn hơn 1/biên gộp.")
fig("f03_batf_segment.png", "Độ co giãn theo phân khúc cửa hàng (BATF).")
para("Khoảng tin cậy giữa ba phân khúc cửa hàng chồng nhau ở hầu hết ngành; giả thuyết “cửa hàng bình dân nhạy giá hơn” không được ủng hộ rõ. Độ nhạy giá phụ thuộc ngành nhiều hơn vị trí cửa hàng.")
h2("7.1. Từ độ co giãn đến biên lợi nhuận")
fig("f20_price.png", "Biên ngụ ý theo quy tắc Lerner (BATF) và mức thay đổi khi giá đổi (M5).")
tab("Biên ngụ ý và biên hòa vốn", ["Ngành (BATF)", "Co giãn", "Biên tối ưu 1/|e|", "Giảm 20% có lãi khi biên <"],
    [[x["category"].title(), n(x["elasticity"], 2), p(x["implied_margin"], 1), p(x["breakeven_margin_20pct_cut"], 1)] for x in ba2["lerner"]], widths=[5, 2.6, 3.6, 4.6], font=9)
lens("Độ co giãn cấp SKU đã gồm phần khách chuyển từ SKU khác, nên co giãn cấp ngành thấp hơn và biên ngụ ý cho cả ngành cao hơn bảng trên. Không có giá vốn để kiểm tra trực tiếp.",
     "Quy tắc Lerner nối độ co giãn với quyết định giá: ngành co giãn mạnh (pizza) chỉ chịu được biên khoảng 33%; ngành ít co giãn chịu được biên cao. Biên hòa vốn cho biết khi nào một đợt giảm giá 20% tự trả được chi phí bằng lượng bán tăng thêm.")
h2("7.2. Giá cứng và lạm phát")
tab("Tần suất và độ lớn thay đổi giá (M5)", ["Ngành", "% tuần có đổi giá", "Tăng", "Giảm", "Trung vị |thay đổi|", "Giá giữ nguyên (tuần)"],
    [[c, p(pcf[c]["freq"], 2), p(pcf[c]["up"], 2), p(pcf[c]["down"], 2), p(pcs[c]["median_abs"], 1), n(m52["duration_weeks"][c])] for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]], widths=[2.6, 3, 1.8, 1.8, 3.4, 3.4], font=9)
tab("Lạm phát giá bình quân cùng SKU-cửa hàng (M5)", ["Năm", "Thực phẩm", "Gia dụng", "Sở thích"],
    [[x["year"], p(x["FOODS"], 2), p(x["HOUSEHOLD"], 2), p(x["HOBBIES"], 2)] for x in m52["inflation"]], widths=[3, 4, 4, 4], font=9)
lens("Giá đổi rất thưa nên ước lượng co giãn từ M5 kém chính xác hơn BATF. Khi giá đổi, thay đổi lớn (trung vị 8–10%).",
     "Giá cứng là dấu hiệu chi phí thay đổi giá (menu cost): in nhãn, cập nhật hệ thống, rủi ro làm khách khó chịu. Lạm phát giá danh nghĩa của Walmart giai đoạn 2012–2016 thấp (0–2%/năm).")

# --- 8 Khuyến mãi
h1("8. Khuyến mãi")
fig("f04_promo.png", "Mức tăng lượng bán khi có hoạt động thương mại.", width=15)
lens(f"CJ chỉ quan sát tuần có hộ panel mua, nên mức tăng ({p(cause['lift_display'])} trưng bày, {p(cause['lift_mailer'])} tờ rơi, {p(cause['lift_both'])} cả hai; {n(cause['pairs'])} cặp SKU-cửa hàng) là cận dưới. BATF và Carbo đo ở cấp cửa hàng.",
     "Trưng bày tăng 28–69% (BATF) và 33–47% (Carbo) khi giá không đổi. Cờ “chỉ giảm giá tạm thời” có hệ số ≈ 0 hoặc âm: giảm giá chỉ tác động qua mức giá. Khách phản ứng với sự chú ý nhiều hơn với phép tính.")
fig("f13_depth.png", "Lượng bán theo độ sâu giảm giá (BATF).")
para(f"{p(BA['discount_depth'][0]['rows'] / sum(x['rows'] for x in BA['discount_depth']))} quan sát bán đúng giá cơ sở; nhóm giảm ≥ 40% bán {n(BA['discount_depth'][-1]['units_per_row'], 1)} đơn vị/tuần so với {n(BA['discount_depth'][0]['units_per_row'], 1)} khi không giảm.")
h2("8.1. Mua dồn và ăn mòn")
fig("f18_dynamics.png", "Tuần sau khuyến mãi và khuyến mãi của đối thủ cùng ngành (BATF).")
tab("Hệ số động thái khuyến mãi", ["Ngành", "Co giãn", "Trễ 1 tuần", "Trễ 2 tuần", "Đối thủ khuyến mãi (100%)", "Số quan sát"],
    [[x["category"].title(), n(x["lp"], 2), p(2.718281828 ** x["promo_l1"] - 1, 1), p(2.718281828 ** x["promo_l2"] - 1, 1), p(2.718281828 ** x["rival_promo"] - 1, 1), n(x["n"])] for x in ba2["dynamics"]], widths=[4, 2, 2.2, 2.2, 3.6, 2.4], font=9)
lens("Mô hình chỉ dùng chuỗi tuần liên tiếp. Nếu khách tích trữ, hệ số trễ sẽ âm. Kết quả trễ 1 tuần dương nhẹ, trễ 2 tuần gần 0: BATF không cho thấy mua dồn rõ, có thể vì khuyến mãi thường kéo dài nhiều tuần liên tiếp nên “tuần sau” vẫn còn hiệu ứng.",
     "Khi toàn bộ SKU khác cùng ngành khuyến mãi, lượng bán một SKU giảm 5–22%, mạnh nhất ở ngũ cốc. Một phần lượng tăng của SKU khuyến mãi lấy từ SKU khác trong cùng cửa hàng — đánh giá khuyến mãi phải ở cấp ngành.")
h2("8.2. Mô phỏng lợi nhuận")
fig("f19_profit_sim.png", "Thay đổi lợi nhuận khi giảm giá ở biên gộp 30% (−100% nghĩa là bán bằng giá vốn).")
sim = [x for x in ba2["profit_sim"] if x["cut"] == 0.1]
tab("Thay đổi lợi nhuận khi giảm 10% theo biên gộp", ["Ngành", "Biên", "Lượng bán ×", "Chỉ giảm giá", "Kèm trưng bày"],
    [[x["category"].title(), p(x["margin"]), n(x["units_mult"], 2), p(x["profit_change_price_only"], 1), p(x["profit_change_with_display"], 1)] for x in sim], widths=[4.6, 1.8, 2.4, 3.2, 3.2], font=8.5)
lens("Lượng mới = (1 − mức giảm)^e (nhân thêm hiệu ứng trưng bày nếu có). Lợi nhuận = (biên − mức giảm) × lượng, so với không giảm. Biên gộp là giả định; chưa trừ ăn mòn nên là cận trên.",
     "Ở biên 30%, giảm 10% đơn thuần làm giảm lợi nhuận cả 4 ngành; kèm trưng bày thì ngũ cốc (+35%), pizza (+32%), snack (+11%) có lãi. Giảm 20% chỉ có lãi ở biên 40%, có trưng bày, với ngũ cốc và pizza. Tiền khuyến mãi nên đi cùng vị trí kệ.")
take(["Ưu tiên trưng bày và tờ rơi; giảm giá nhỏ hơn biên một khoảng đủ lớn.", "Đo hiệu quả khuyến mãi ở cấp ngành, trừ phần ăn mòn SKU khác."])

# --- 9 Chiến dịch
h1("9. Chiến dịch coupon và vấn đề chọn mẫu")
fig("f12_campaigns.png", "Tỷ lệ đổi coupon và chênh lệch tăng trưởng (DiD) của 29 chiến dịch (CJ).")
tab("Kết quả theo loại chiến dịch", ["Loại", "Số chiến dịch", "Hộ nhận", "Tỷ lệ đổi", "Chi trước (nhận/không)", "DiD trung vị"],
    [[t, ct[t]["campaigns"], n(ct[t]["households"]), p(ct[t]["redemption_rate"], 1), f"×{n(1 + cds[t]['level_gap'], 2)}", p(cds[t]["did_pp_median"], 1)] for t in ["TypeA", "TypeB", "TypeC"]],
    widths=[1.8, 2.4, 2.2, 2.2, 4.6, 2.6], font=9)
lens("Hộ nhận chiến dịch không ngẫu nhiên: trước chiến dịch đã chi gấp 2,3–2,8 lần. So mức chi thô sẽ gán nhầm thành tích. DiD so tốc độ tăng chi tiêu giữa hai nhóm, chỉ trên hộ hoạt động trước và sau chiến dịch; vẫn chưa loại hết khác biệt xu hướng.",
     "Chênh lệch tăng trưởng gần 0: coupon có thể đang trợ giá cho chi tiêu vốn sẽ xảy ra (deadweight loss của khuyến mãi). Tỷ lệ đổi cao nhất ở TypeA vì cá nhân hóa. Cần nhóm đối chứng ngẫu nhiên trước khi mở rộng.")

# --- 10 Lịch
h1("10. Lịch, trợ cấp và dòng tiền hộ gia đình")
fig("f05_snap.png", "Mức tăng lượng bán ngày SNAP và nhịp theo ngày trong tháng (M5).")
tab("Hiệu ứng SNAP (KTC 95%)", ["Bang", "Thực phẩm", "Gia dụng", "Sở thích"],
    [[s, *[f"{p(snap[(s, c)]['lift'], 1)} ({p(snap[(s, c)]['ci_low'], 1)}–{p(snap[(s, c)]['ci_high'], 1)})" for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]]] for s in ["CA", "TX", "WI"]], widths=[2, 4.8, 4.8, 4.8], font=9)
lens("Lịch SNAP khác nhau giữa bang (CA ngày 1–10; TX, WI xen kẽ trong 15 ngày đầu) nên tách được khỏi hiệu ứng nhận lương. Đường WI có răng cưa đúng lịch chi trả.",
     "Theo giả thuyết thu nhập thường xuyên, ngày nhận tiền không làm đổi tiêu dùng. Dữ liệu cho thấy hộ có ràng buộc thanh khoản chi ngay khi có tiền, và hiệu ứng gần như chỉ ở Thực phẩm — đúng phạm vi SNAP. Ở Việt Nam: ngày lương, lương hưu, trợ cấp.")
fig("f06_events.png", "Ngày lễ so với cùng thứ tuần trước và sau (M5).", width=14)
para(f"Lễ Tạ ơn {p(H.ev['Thanksgiving']['lift'])}, Năm mới {p(H.ev['NewYear']['lift'])} (hộ mua trước và ở nhà); Lễ Lao động +{p(H.ev['LaborDay']['lift'])}. Mô hình dự báo cần biến “ngày trước lễ”; với Tết cần mô hình riêng cho 2–3 tuần trước Tết.")

# --- 11 Thu nhập & thương hiệu
h1("11. Thu nhập, nhãn riêng và thương hiệu")
fig("f07_income.png", "Chi tiêu tuần và tỷ trọng nhãn riêng theo bậc thu nhập (CJ).")
tab("Chỉ số theo bậc thu nhập", ["Bậc", "Số hộ", "Chi/tuần (USD)", "Giá trị giỏ", "Nhãn riêng", "Tỷ lệ giảm giá"],
    [[x["level"], x["households"], n(x["weekly_spend"], 1), n(x["basket_value"], 1), p(x["pl_share"], 1), p(x["disc_rate"], 1)] for x in CJ["demo_income"]], widths=[2.4, 1.8, 2.8, 2.6, 2.6, 2.8], font=8.5)
lens(f"Thu nhập mã hóa thứ bậc; bậc 10–12 chỉ 5–11 hộ. Hồi quy: +{p(inc['log_spend_per_level'], 1)} chi tiêu/bậc (SE {n(inc['se'], 3)}), nhãn riêng {n(incpl['pl_share_per_level'] * 100, 2)} điểm %/bậc; R² {n(inc['r2'], 2)}. Hộ có hồ sơ chiếm {p(CJ['profile']['demographic_sales_share'])} doanh thu — nghiêng về hộ chi nhiều.",
     "Chi tiêu thực phẩm tăng chậm hơn thu nhập (quy luật Engel). Nhãn riêng hành xử như hàng cấp thấp. Hộ thu nhập cao cũng dùng giảm giá ít hơn (20% → 13%): độ nhạy giá giảm theo thu nhập. Tỷ trọng nhãn riêng tăng là chỉ báo sớm khi kinh tế đi xuống.")
pl = H.pl_b
tab("Nhãn riêng và thương hiệu quốc gia (BATF)", ["Ngành", "Giá TB thương hiệu", "Giá TB nhãn riêng", "Chênh", "% tuần TPR (TH/NR)"],
    [[c.title(), n(pl[(c, False)]["avg_price"], 2), n(pl[(c, True)]["avg_price"], 2), "−" + p(1 - pl[(c, True)]["avg_price"] / pl[(c, False)]["avg_price"]), f"{p(pl[(c, False)]['promo'])} / {p(pl[(c, True)]['promo'])}"] for c in sorted({k[0] for k in pl})],
    widths=[4.2, 3.2, 3.2, 2, 3.8], font=9)
fig("f10_carbo.png", "Lift cùng giỏ và cơ cấu trung thành thương hiệu (Carbo).")
fig("f22_switch.png", "Ma trận chuyển đổi thương hiệu giữa hai lần mua liên tiếp (Carbo).")
tab("Mua lặp lại và thị phần dừng", ["Ngành", "Thương hiệu", "Mua lặp lại", "Thị phần hiện tại", "Thị phần dừng"],
    [[k, b, p(cl2[k]["repeat"][b]), p(cl2[k]["current_share"][b], 1), p(cl2[k]["steady_share"][b], 1)] for k in ["pasta sauce", "pasta"] for b in cl2[k]["brands"]], widths=[2.6, 3.6, 2.6, 3.4, 3.4], font=8.5)
lens(f"HHI: bột bánh {n(hhi['pancake mixes'])}, sốt {n(hhi['pasta sauce'])}, mì Ý {n(hhi['pasta'])}, siro {n(hhi['syrups'])}. Thị phần dừng (vector riêng của ma trận chuyển) gần bằng thị phần hiện tại: thị trường cân bằng trong 2 năm.",
     f"Bột bánh có {p(loy['pancake mixes']['share_loyal_80'])} hộ trung thành, mì Ý chỉ {p(loy['pasta']['share_loyal_80'])}. Mì Ý gần như hàng đồng nhất nên nhãn riêng chiếm {p(cl_comm['pasta']['private_share'])} doanh thu và giữ chân {p(cl2['pasta']['repeat']['Private Label'])} khách. "
     "Thương hiệu nhỏ giữ chân kém (30–45%): khuyến mãi của họ chủ yếu tạo lượt mua thử.")

# --- 12 Giỏ hàng
h1("12. Giỏ hàng và nhịp thời gian")
fig("f17_rules.png", "15 cặp nhóm hàng có lift cao nhất trên giỏ đầy đủ (CJ).")
tab("Mì Ý + sốt: cùng một cặp, hai kết luận", ["Chỉ số", "CJ (giỏ đầy đủ)", "Carbo (lọc 4 ngành)"], [
    ["Lift", n(ps["lift"], 2), n(comp[("pasta", "pasta sauce")]["lift"], 2)],
    ["P(sốt | mì)", p(ps["conf_sauce_given_pasta"], 1), p(comp[("pasta", "pasta sauce")]["conf_a_b"], 1)],
    ["P(mì | sốt)", p(ps["conf_pasta_given_sauce"], 1), p(comp[("pasta", "pasta sauce")]["conf_b_a"], 1)],
    ["Support", p(ps["support"], 2), p(comp[("pasta", "pasta sauce")]["support"], 1)],
], widths=[5, 5, 5], font=9)
lens("Confidence gần như nhau ở hai nguồn (42–55%), nhưng lift chênh hơn 10 lần. Carbo chỉ giữ giỏ có ít nhất một trong 4 ngành nên P(A), P(B) bị thổi phồng và lift bị kéo về 1. Luật kết hợp phải chạy trên giỏ đầy đủ.",
     "Các cặp lift cao là bữa ăn hoàn chỉnh: mì + sốt, phô mai + thịt nguội, cà chua + rau salad, xúc xích + bánh. Khách mua giải pháp cho bữa ăn. Hàng bổ trợ có co giãn chéo âm: giảm giá món chính kéo doanh thu món đi kèm có biên tốt hơn.")
fig("f09_missions.png", "Số giỏ và doanh thu theo loại chuyến và độ nhạy giá (LGSR, mô phỏng).")
fig("f08_heat.png", "Số giỏ theo thứ × giờ (LGSR).")
fig("f14_hours.png", "Nhịp giờ mua sắm ở ba nguồn.")
bt = H.lg_bt
para(f"Small Shop chiếm {p(bt['Small Shop']['baskets'] / LG['profile']['baskets'])} số giỏ nhưng {p(bt['Small Shop']['spend'] / LG['profile']['spend'])} doanh thu; Full Shop {p(bt['Full Shop']['baskets'] / LG['profile']['baskets'])} số giỏ, {p(bt['Full Shop']['spend'] / LG['profile']['spend'])} doanh thu. "
     "CJ và Carbo (dữ liệu thật) đạt đỉnh 16–19 giờ; LGSR (mô phỏng) đạt đỉnh 13–15 giờ và trải đều hơn, nên không dùng LGSR để xếp ca.")

# --- 13 Dự báo
h1("13. Dự báo nhu cầu")
para("Bài toán M5: dự báo 28 ngày cuối (23/04–22/05/2016) cho 30.490 chuỗi SKU-cửa hàng. Mô hình học máy chỉ dùng thông tin trễ ít nhất 28 ngày, nên dự báo trực tiếp cả 28 ngày mà không rò rỉ tương lai.")
fig("f21_forecast.png", "So sánh mô hình và tổng lượng bán 28 ngày kiểm tra (M5).")
tab("Kết quả kiểm tra 28 ngày", ["Mô hình", "WRMSSE (SKU)", "WAPE", "Lệch tổng", "RMSE tổng/ngày"],
    [[x["model"], n(x["wrmsse_item"], 3), p(x["wape"], 1), p(x["bias"], 1), n(x["rmse_total_daily"])] for x in fc], widths=[5, 2.8, 2.4, 2.4, 3.4], font=9)
tab("WAPE theo ngành", ["Ngành", "Naive mùa vụ", "TB theo thứ 8 tuần", "GBM"],
    [[c, *[p(next(x["wape"] for x in m52["forecast_by_cat"] if x["cat"] == c and x["model"] == mm), 1) for mm in ["Naive mùa vụ 7 ngày", "TB theo thứ, 8 tuần", "GBM toàn cục (Poisson)"]]] for c in ["FOODS", "HOUSEHOLD", "HOBBIES"]],
    widths=[4, 4, 4, 4], font=9)
lens(f"GBM huấn luyện trên {n(m52['forecast_train_rows'])} quan sát lấy mẫu từ 420 ngày trước kỳ kiểm tra; biến quan trọng nhất là trung bình trượt 28 ngày (rm28), sau đó rm91, rm7. Biến lịch gần như không quan trọng ở cấp SKU vì nhiễu ngày-SKU lấn át. Chỉ một kỳ kiểm tra — cần thêm kỳ để khẳng định thứ hạng.",
     f"GBM tốt nhất nhưng trung bình 28 ngày chỉ kém {p(fcm['Trung bình 28 ngày']['wrmsse_item'] / best['wrmsse_item'] - 1, 1)} ở cấp SKU. Ở cấp tổng, GBM có sai số ngày {n(fcm['GBM toàn cục (Poisson)']['rmse_total_daily'])} so với {n(fcm['Trung bình 28 ngày']['rmse_total_daily'])} vì bắt được nhịp cuối tuần. "
     "Tồn kho an toàn tỷ lệ với độ lệch chuẩn sai số: dùng mô hình đơn giản cho từng SKU, học máy cho kế hoạch tổng (nhân sự, vận tải, nhập hàng theo ngành).")

# --- 14 Tổng hợp
h1("14. Tổng hợp mức tin cậy")
tab("Kết luận và độ tin cậy", ["Kết luận", "Nguồn ủng hộ", "Độ lớn", "Tin cậy"], [
    ["Doanh thu tập trung mạnh", "CJ, Carbo, LGSR, M5", "Top 20% = 53–66%", "Cao"],
    ["Trưng bày/tờ rơi tăng lượng bán khi giá không đổi", "CJ, BATF, Carbo", "+6% (cận dưới CJ) đến +69%", "Cao"],
    ["Phạm vi dữ liệu quyết định lift", "CJ, Carbo", f"{n(ps['lift'], 1)} so với {n(comp[('pasta', 'pasta sauce')]['lift'], 2)}", "Cao"],
    ["Nhu cầu SKU-cửa hàng gián đoạn", "M5", f"{p(H.intermittent_all)} chuỗi", "Cao"],
    ["Co giãn khác nhau theo ngành", "BATF, Carbo, M5", "−0,27 đến −2,99", "Trung bình"],
    ["Khuyến mãi ăn mòn SKU cùng ngành", "BATF", "−5% đến −22%", "Trung bình"],
    ["Giảm giá đơn thuần thường lỗ", "BATF (mô phỏng)", "Phụ thuộc biên giả định", "Trung bình"],
    ["Dòng tiền hộ quyết định thời điểm mua", "M5", f"+{p(snap[('CA', 'FOODS')]['lift'])} đến +{p(snap[('WI', 'FOODS')]['lift'])}", "Trung bình – cao"],
    ["Nhãn riêng là hàng cấp thấp", "CJ, BATF, Carbo", "−0,78 điểm %/bậc; rẻ hơn 30–62%", "Trung bình"],
    ["Coupon chủ yếu đến hộ vốn chi nhiều", "CJ", "×2,3–2,8; DiD ≈ 0", "Trung bình"],
    ["Tăng trưởng chủ yếu nhờ giá trị giỏ", "CJ", f"{n(gd['aov'] * 100, 1)}/{n(gd['sales'] * 100, 1)} điểm log", "Trung bình"],
    ["Học máy cải thiện dự báo tổng", "M5", "RMSE tổng/ngày −50% so với TB 28 ngày", "Trung bình"],
], widths=[6, 3.4, 4.6, 2.4], font=8.5)

# =========================================================================== PHẦN II
part("PHẦN II", "Xây dựng trang web phân tích")
h1("15. Mục tiêu và yêu cầu")
para("Trang web là sản phẩm trình bày chính của phân tích: người đọc (ban điều hành, nhóm thương mại, nhóm dữ liệu) xem kết quả, tương tác với biểu đồ và đọc hai lớp diễn giải mà không cần cài đặt.")
tab("Yêu cầu và cách đáp ứng", ["Yêu cầu", "Cách đáp ứng"], [
    ["Truy cập không cần cài đặt", "Một trang HTML tĩnh duy nhất: mở bằng trình duyệt hoặc qua link Artifact; không cần máy chủ."],
    ["Số liệu khớp phân tích", "Số liệu và câu chữ sinh tự động từ results.json và results_deep.json; không gõ tay số."],
    ["Hai lớp đọc dữ liệu/kinh tế", "Mỗi phát hiện có panel biểu đồ và hai thẻ “Góc dữ liệu”, “Góc kinh tế”."],
    ["Tương tác", "Tooltip mọi biểu đồ; nút chuyển chiều (loại chuyến, độ nhạy giá…), mô phỏng lợi nhuận theo biên và mức giảm, ma trận chuyển đổi theo ngành."],
    ["Đọc tốt trên điện thoại", "Bố cục lưới tự xếp một cột dưới 860px; mục lục cuộn ngang; không cuộn ngang toàn trang."],
    ["Giao diện sáng/tối", "Bảng màu định nghĩa bằng biến CSS cho cả hai chế độ; biểu đồ vẽ lại khi đổi chế độ."],
    ["Tái lập", "Chạy lại 4 script Python là dựng lại toàn bộ phân tích, web và báo cáo."],
], widths=[4.5, 12], font=9)

h1("16. Kiến trúc và luồng dữ liệu")
tab("Các bước từ dữ liệu gốc đến web", ["Bước", "Thành phần", "Đầu vào → đầu ra"], [
    ["1. Tải", "curl, Zenodo API", "dunnhumby, Zenodo → data/raw_dunnhumby, data/raw_m5 (giữ nguyên gốc, kiểm tra checksum)"],
    ["2. Phân tích", "analyze_multisource.py, analyze_deep.py (duckdb, pandas, statsmodels, scikit-learn)", "CSV/XLSX gốc → results.json, results_deep.json"],
    ["3. Biểu đồ tĩnh", "make_figures.py (matplotlib)", "JSON → 22 hình PNG cho báo cáo Word"],
    ["4. Dựng web", "build_html.py + html_extra.py", "JSON → Phan_tich_da_nguon.html và web/index.html (dữ liệu tổng hợp nhúng trong trang)"],
    ["5. Chụp màn hình", "Microsoft Edge headless, chế độ ?shot=<chương>&theme=light", "Trang → outputs/multisource/screens/*.png"],
    ["6. Báo cáo", "build_word.py + word_body.py (python-docx)", "JSON, hình, ảnh chụp → Bao_cao_phan_tich_da_nguon.docx"],
], widths=[2.4, 5.6, 8.6], font=8.5)
para("Trang web không gọi máy chủ dữ liệu khi chạy: toàn bộ dữ liệu tổng hợp (khoảng 120 KB JSON) nằm trong trang. Thiết kế này chọn vì dữ liệu là ảnh chụp lịch sử, không cần cập nhật theo thời gian thực, và giúp trang tải nhanh, không phụ thuộc backend. "
     "Dữ liệu chi tiết (hàng triệu dòng) không đưa lên web.")

h1("17. Công nghệ và thiết kế giao diện")
tab("Công nghệ", ["Lớp", "Lựa chọn", "Lý do"], [
    ["Biểu đồ", "Apache ECharts 5.5 (CDN cdnjs)", "Nhiều loại biểu đồ (forest plot tùy biến, heatmap, timeline), tooltip, hiệu năng canvas."],
    ["Phông chữ", "Bricolage Grotesque (tiêu đề), Be Vietnam Pro (nội dung), JetBrains Mono (nhãn số)", "Hỗ trợ đầy đủ dấu tiếng Việt; Be Vietnam Pro thiết kế cho tiếng Việt."],
    ["Bố cục", "CSS Grid/Flex, biến CSS, không framework", "Một file, không bước build JavaScript."],
    ["Màu", "Xanh rêu thương hiệu Retail Intelligence + 5 màu định danh nguồn", "Nối tiếp nhận diện dashboard cũ; mỗi nguồn một màu nhất quán trên mọi biểu đồ."],
    ["Nền mở đầu", "Canvas: chấm 5 màu nối nhau", "Hình ảnh hóa ý tưởng “trộn 5 nguồn”; tắt chuyển động khi người dùng chọn giảm chuyển động."],
], widths=[2.6, 6, 8], font=8.5)
para("Khả năng tiếp cận: tương phản màu đủ cho cả hai chế độ; nút có trạng thái aria-pressed; tiêu điểm bàn phím hiển thị; tôn trọng prefers-reduced-motion. Biểu đồ đọc màu từ biến CSS nên luôn khớp chế độ sáng/tối.")

h1("18. Cấu trúc mã nguồn")
tab("Tệp và vai trò", ["Tệp", "Vai trò"], [
    ["research/multisource/analyze_multisource.py", "Hồ sơ dữ liệu, chất lượng, tập trung, co giãn, khuyến mãi, SNAP, sự kiện, nhân khẩu, chiến dịch, giỏ Carbo, LGSR."],
    ["research/multisource/analyze_deep.py", "Phân rã tăng trưởng, quỹ đạo hộ, RFM, luật kết hợp CJ, động thái khuyến mãi, mô phỏng lợi nhuận, Lerner, giá cứng, lạm phát, benchmark dự báo, chuyển đổi thương hiệu."],
    ["research/multisource/make_figures.py", "22 hình PNG cho báo cáo."],
    ["research/multisource/build_html.py", "Trang chính: CSS, 10 chương gốc, 18 biểu đồ, bản HTML độc lập."],
    ["research/multisource/html_extra.py", "Chương Khách hàng, Dự báo và các khối chuyên sâu (11 biểu đồ, mô phỏng), chế độ chụp màn hình, đánh số chương tự động."],
    ["research/multisource/build_word.py, word_body.py", "Báo cáo Word."],
    ["outputs/multisource/web/index.html", "Bản HTML đầy đủ (có thẻ doctype) để mở trực tiếp và chụp màn hình."],
    ["outputs/multisource/", "results*.json, figures/, screens/, HTML và DOCX."],
], widths=[6.5, 10], font=8.5)
h2("18.1. Hợp đồng dữ liệu giữa phân tích và web")
para("Trang nhận hai đối tượng JSON: D (kết quả phân tích chính) và D2 (phân tích chuyên sâu). Mỗi biểu đồ đăng ký bằng hàm reg(id, t => option) nhận bộ màu hiện hành t và trả về cấu hình ECharts. "
     "Khi đổi chế độ sáng/tối hoặc bấm nút chuyển chiều, trang gọi lại hàm này để vẽ lại. Câu chữ có số được sinh bởi Python bằng định dạng số Việt Nam (dấu chấm phân cách nghìn, dấu phẩy thập phân).")

h1("19. Kiểm thử")
tab("Các bước kiểm tra", ["Kiểm tra", "Cách làm", "Kết quả"], [
    ["Cú pháp JavaScript", "node --check trên toàn bộ script trong trang", "Đạt"],
    ["Dựng biểu đồ", "Chạy toàn bộ hàm cấu hình biểu đồ trong Node với DOM giả", "29/29 biểu đồ dựng không lỗi"],
    ["Hiển thị thật", "Edge headless chụp 12 chương ở giao diện sáng, 1 bản tối, 1 bản điện thoại 420px", "Đã xem; sửa chồng chú thích và nhãn trục dày"],
    ["Đối chiếu số liệu", "Mọi số trong câu chữ lấy từ JSON; kiểm tra lại các câu so sánh (ví dụ giờ cao điểm, biên hòa vốn)", "Sửa 2 câu không khớp trước khi phát hành"],
    ["Tái lập", "Chạy lại toàn bộ chuỗi script", "Khoảng 4 phút trên máy 16 luồng, 7 GB RAM"],
], widths=[3.4, 8.6, 4.6], font=8.5)

h1("20. Chạy và chia sẻ trang web")
para(f"Địa chỉ: **{WEB_URL}**")
for t in [
    "Mở trực tiếp: nhấp đúp outputs/multisource/Phan_tich_da_nguon.html (hoặc web/index.html). Cần kết nối mạng để tải thư viện biểu đồ ECharts và phông chữ.",
    "Bản trực tuyến: link Artifact ở trên; mặc định riêng tư, người khác chỉ xem được sau khi được chia sẻ qua nút Share.",
    "Cập nhật: chạy lại build_html.py; tệp HTML được ghi đè với số liệu mới.",
    "Trang không chứa dữ liệu cá nhân: chỉ có chỉ số tổng hợp từ dữ liệu công khai đã ẩn danh.",
]:
    bullet(t)

# =========================================================================== PHẦN III
part("PHẦN III", "Mô tả chi tiết trang web")
h1("21. Bố cục chung và điều hướng")
fig("s00_hero.png", "Phần mở đầu: luận điểm, 5 chỉ số tổng quan và chú giải màu 5 nguồn.", width=16, folder=SHOTS)
para("Trang là một tài liệu cuộn dọc gồm phần mở đầu, thanh mục lục dính ở đầu trang và 12 chương. Phần mở đầu nêu luận điểm, năm chỉ số tổng quan "
     f"({n(H.TOTAL_ROWS / 1e6, 0)} triệu dòng/ô dữ liệu, 5 nguồn, 2006–2016, số mã cửa hàng, 17 nhóm trường) và chú giải màu: CJ xanh rêu, BATF vàng hổ phách, Carbo đỏ gạch, LGSR tím, M5 xanh thép. "
     "Màu này giữ nguyên trên mọi biểu đồ để người đọc nhận ra nguồn mà không cần đọc nhãn.")
para("Thanh mục lục có 12 mục; mục đang đọc được tô đậm tự động khi cuộn. Trên điện thoại thanh mục lục cuộn ngang. Mỗi chương có cấu trúc: nhãn chương, tiêu đề là kết luận chính, đoạn dẫn, sau đó là các khối phát hiện. "
     "Mỗi khối phát hiện gồm panel biểu đồ bên trái và hai thẻ bên phải: **Góc dữ liệu** (nhãn xanh) và **Góc kinh tế** (nhãn cam). Trên màn hình hẹp hai thẻ xuống dưới biểu đồ.")
fig("m_hero.png", "Hiển thị trên điện thoại (420px): bố cục một cột.", width=6, folder=SHOTS)
fig("d_full.png", "Giao diện tối: toàn bộ màu và biểu đồ chuyển theo cài đặt hệ thống.", width=14, folder=SHOTS)
para("Thao tác chung: rê chuột (hoặc chạm) vào điểm, cột, ô bất kỳ để xem tooltip với số chính xác; bấm chú giải để ẩn/hiện chuỗi; các nhóm nút tròn đổi chiều dữ liệu của biểu đồ ngay tại chỗ.")

WEBSEC = [
    ("nguon", "Chương 1 — Bản đồ nguồn",
     "Năm thẻ nguồn (quy mô, hạt dữ liệu, câu hỏi trả lời được), dòng thời gian các nguồn có ngày thật và ma trận 17 nhóm trường × 5 nguồn.",
     ["Đọc thẻ nguồn để biết mỗi bộ đo ở hạt nào trước khi xem kết quả.", "Ma trận trường: chấm màu là có trường; cột ghi chú nêu giới hạn (ví dụ Carbo chỉ có tờ rơi từ tuần 43).", "Dòng thời gian cho thấy không nguồn nào trùng kỳ — lý do không nối dòng."]),
    ("du-lieu", "Chương 2 — Góc dữ liệu",
     "Nguyên tắc trộn (hài hòa ở mức chỉ số), bảng giới hạn của từng nguồn kèm bằng chứng và cách xử lý, biểu đồ kiểu nhu cầu M5.",
     ["Bảng chất lượng là phần nên đọc trước khi trích dẫn bất kỳ con số nào.", "Biểu đồ thanh chồng: tỷ lệ chuỗi Đều/Thất thường/Gián đoạn/Cục theo ngành; rê chuột để xem phần trăm."]),
    ("tap-trung", "Chương 3 — Tập trung doanh thu",
     "Đường Lorenz của 5 góc nhìn trên cùng trục; đánh dấu điểm top 20% của CJ.",
     ["Đường càng cong lên góc trái trên, doanh thu càng tập trung; đường chấm là phân bổ đều.", "Bấm tên chuỗi ở chú giải để so từng cặp."]),
    ("khach-hang", "Chương 4 — Khách hàng theo thời gian",
     "Chỉ số ba động lực (hộ hoạt động, chuyến/hộ, giá trị giỏ) theo kỳ 4 tuần; quỹ đạo hộ; phân khúc RFM.",
     ["Đường đen là doanh thu; ba đường màu cho biết động lực nào kéo doanh thu.", "Biểu đồ quỹ đạo: cột là số hộ, đường là chênh doanh thu giữa hai nửa giai đoạn.", "RFM: so cột nhạt (% hộ) với cột đậm (% doanh thu) để thấy nhóm nào đóng góp vượt tỷ lệ."]),
    ("gia", "Chương 5 — Giá",
     "Forest plot độ co giãn 11 ngành ở 3 nguồn kèm khoảng tin cậy; co giãn theo phân khúc cửa hàng; biên Lerner; phân bố mức thay đổi giá M5.",
     ["Forest plot: chấm là ước lượng, thanh là khoảng tin cậy 95%, vạch đứt là co giãn đơn vị −1.", "Biểu đồ Lerner: cột là biên tối ưu ngụ ý, vạch đen là biên hòa vốn khi giảm giá 20%."]),
    ("khuyen-mai", "Chương 6 — Khuyến mãi",
     "Mức tăng do trưng bày/tờ rơi/TPR ở 3 nguồn; lượng bán theo độ sâu giảm giá; chiến dịch coupon (DiD); động thái khuyến mãi và đối thủ; mô phỏng lợi nhuận tương tác.",
     ["Mô phỏng lợi nhuận: chọn biên gộp (20/30/40%) và mức giảm (10/20/30%); biểu đồ cập nhật ngay, so “chỉ giảm giá” với “giảm giá + trưng bày”.", "Biểu đồ chiến dịch: mỗi chấm là một chiến dịch; chấm càng xa bên phải là hộ được chọn càng chi nhiều từ trước."]),
    ("chinh-sach", "Chương 7 — Lịch và chính sách",
     "Hiệu ứng ngày SNAP theo bang × ngành; nhịp chi tiêu theo ngày trong tháng; hiệu ứng 29 ngày lễ/sự kiện.",
     ["Nhãn trên cột SNAP là mức tăng phần trăm.", "Đường ngày trong tháng: trên 1,0 là cao hơn trung bình tháng; răng cưa của WI trùng lịch chi trả."]),
    ("thu-nhap", "Chương 8 — Thu nhập và nhãn riêng",
     "Chi tiêu và tỷ trọng nhãn riêng theo 12 bậc thu nhập; chênh giá nhãn riêng; trung thành thương hiệu; ma trận chuyển đổi thương hiệu.",
     ["Tooltip ở biểu đồ thu nhập hiện số hộ của bậc để biết độ tin cậy.", "Ma trận chuyển đổi: bấm “Sốt mì Ý”/“Mì Ý” để đổi ngành; đường chéo là tỷ lệ mua lặp lại."]),
    ("hanh-vi", "Chương 9 — Hành vi giỏ hàng",
     "Số giỏ và doanh thu theo loại chuyến/độ nhạy giá/nhiệm vụ/định dạng cửa hàng; bản đồ nhiệt thứ × giờ; nhịp giờ 3 nguồn; lift Carbo; luật kết hợp CJ.",
     ["Bốn nút phía trên biểu đồ đầu đổi chiều phân tích.", "So lift Carbo (dưới 1 với mì + sốt) và lift CJ (9,8) để thấy ảnh hưởng của phạm vi dữ liệu."]),
    ("du-bao", "Chương 10 — Dự báo",
     "WRMSSE của 5 mô hình; tổng lượng bán 28 ngày thực tế và dự báo.",
     ["Cột xanh đậm là mô hình tốt nhất.", "Biểu đồ đường: đường đen là thực tế; nét đứt là mô hình cơ sở."]),
    ("tong-hop", "Chương 11 — Tổng hợp",
     "Chín thẻ kết luận, mỗi thẻ ghi các nguồn ủng hộ bằng nhãn màu, độ lớn và mức tin cậy.", ["Số nhãn nguồn trên thẻ là thước đo nhanh độ vững của kết luận."]),
    ("hanh-dong", "Chương 12 — Hành động cho chuỗi",
     "Sáu hành động đề xuất cho chuỗi siêu thị Việt Nam, xếp theo thứ tự triển khai.", ["Mỗi hành động gắn với chương bằng chứng tương ứng."]),
]
h1("22. Mô tả từng chương")
for sid, title, what, how in WEBSEC:
    h2(title)
    fig(f"s_{sid}.png", f"{title} trên trang web.", width=16, folder=SHOTS)
    para(f"**Nội dung.** {what}")
    pa = para("Cách đọc và tương tác", bold=True, size=10, color=ACCENT, after=2)
    pa.paragraph_format.keep_with_next = True
    for t in how:
        bullet(t)

# =========================================================================== PHẦN IV
part("PHẦN IV", "Khuyến nghị, lộ trình và phụ lục")
h1("23. Khuyến nghị cho chuỗi siêu thị")
recs = [
    ("Ghi đủ trường mà các nguồn công khai thiếu", "Hóa đơn có mã khách; giá kệ và giá cơ sở theo ngày; cờ tờ rơi/trưng bày theo cửa hàng-SKU-tuần; tồn kho đầu ngày; giá vốn."),
    ("Ước lượng co giãn theo ngành trước khi đổi giá", "Áp dụng mô hình hiệu ứng cố định như BATF cho 20 ngành hàng đầu; dùng quy tắc Lerner và biên thật để xác định khoảng giá."),
    ("Chuyển ngân sách từ giảm giá sang vị trí kệ và tờ rơi", "Thử theo cặp cửa hàng cùng mức giá; đo 4 tuần sau; đánh giá ở cấp ngành để trừ ăn mòn."),
    ("Đặt lịch hàng thiết yếu theo ngày nhận lương", "Thêm biến ngày lương, lương hưu, trợ cấp, “ngày trước lễ” và cửa sổ Tết vào mô hình dự báo."),
    ("Mọi chiến dịch CRM phải có nhóm đối chứng", "Giữ ngẫu nhiên khoảng 10% khách đủ điều kiện; ưu tiên nhóm RFM “có nguy cơ mất”."),
    ("Dự báo theo kiểu nhu cầu và cấp tổng hợp", "SKU: trung bình trượt hoặc Croston/TSB; kế hoạch tổng: học máy. Đánh giá bằng WRMSSE thay vì MAPE."),
]
for i, (hh_, t) in enumerate(recs, 1):
    pa = doc.add_paragraph()
    r_ = pa.add_run(f"{i:02d}  {hh_}")
    r_.bold = True
    r_.font.color.rgb = BRAND
    pa.paragraph_format.space_after = Pt(2)
    pa.paragraph_format.keep_with_next = True
    para(t, after=8)
h2("23.1. Lộ trình dữ liệu")
tab("Lộ trình đề xuất", ["Giai đoạn", "Dữ liệu cần", "Phân tích mở khóa", "Tham chiếu"], [
    ["Tuần 1–2", "POS 12–24 tháng, danh mục SKU, danh sách cửa hàng", "Tập trung, RFM, nhịp thời gian, giỏ hàng", "CJ, LGSR"],
    ["Tuần 3–4", "Lịch sử giá kệ, giá cơ sở; lịch khuyến mãi, tờ rơi, trưng bày", "Co giãn, hiệu ứng khuyến mãi, ăn mòn", "BATF, Carbo"],
    ["Tháng 2", "Tồn kho đầu ngày, hàng về, hết hàng", "Dự báo có hiệu chỉnh hết hàng", "M5"],
    ["Tháng 2–3", "Mã khách, chiến dịch, coupon, nhóm đối chứng", "Đo hiệu quả CRM tăng thêm", "CJ"],
    ["Tháng 3", "Giá vốn, biên gộp theo SKU", "ROI khuyến mãi, tối ưu giá", "Dữ liệu nội bộ"],
], widths=[2.2, 5.4, 4.6, 4.2], font=9)

h1("24. Hạn chế")
for t in [
    "Dữ liệu Mỹ/Anh 2006–2016; hành vi người mua Việt Nam (chợ truyền thống, mua lẻ nhiều lần, Tết) có thể khác.",
    "LGSR là dữ liệu mô phỏng; chỉ dùng để thử phương pháp.",
    "CJ là panel 2.500 hộ thường xuyên; nhân khẩu học có 801 hộ, nghiêng về hộ chi nhiều.",
    "Không có giá vốn, tồn kho: mô phỏng lợi nhuận dùng biên giả định; không tách hết hàng khỏi không có cầu.",
    "Các ước lượng là quan sát, không phải thử nghiệm ngẫu nhiên; độ co giãn chỉ dùng tuần có bán.",
    "Benchmark dự báo có một kỳ kiểm tra 28 ngày.",
]:
    bullet(t)
h1("25. Tái lập")
for t in ["python3 research/multisource/analyze_multisource.py", "python3 research/multisource/analyze_deep.py", "python3 research/multisource/make_figures.py",
          "python3 research/multisource/build_html.py", "python3 research/multisource/build_word.py"]:
    pa = para(t, size=9)
    pa.runs[0].font.name = "Consolas"
para("Thư viện: duckdb 2.0, pandas, numpy, statsmodels, scikit-learn, matplotlib, python-docx.", size=9.5, color=MUTED)
h1("26. Thuật ngữ")
tab("Thuật ngữ", ["Thuật ngữ", "Giải thích"], [
    ["Độ co giãn giá", "% thay đổi lượng bán khi giá thay đổi 1%."],
    ["Hiệu ứng cố định", "Biến giả cho từng SKU×cửa hàng và từng tuần, loại khác biệt cố định và cú sốc chung."],
    ["Quy tắc Lerner", "Biên tối ưu (P − MC)/P = 1/|độ co giãn|."],
    ["TPR", "Temporary Price Reduction — giảm giá tạm thời không kèm quảng bá."],
    ["Ăn mòn (cannibalization)", "Lượng bán tăng của SKU khuyến mãi lấy từ SKU khác cùng cửa hàng."],
    ["DiD", "Difference-in-differences — so chênh lệch thay đổi giữa nhóm nhận và nhóm không nhận."],
    ["SNAP", "Chương trình trợ cấp thực phẩm của Mỹ cho hộ thu nhập thấp."],
    ["Lift", "P(A∩B)/(P(A)P(B)); > 1 là hay mua cùng nhau."],
    ["RFM", "Recency, Frequency, Monetary."],
    ["HHI", "Chỉ số Herfindahl–Hirschman: tổng bình phương thị phần (%)."],
    ["WRMSSE", "Sai số bình phương trung bình chuẩn hóa theo naive, có trọng số doanh thu (thước đo cuộc thi M5)."],
    ["WAPE", "Tổng |sai số| / tổng thực tế."],
    ["GBM", "Gradient boosting — mô hình cây tăng cường."],
    ["Nhu cầu gián đoạn", "Chuỗi có nhiều ngày bằng 0 xen kẽ ngày có bán."],
], widths=[4, 12.5], font=9)
h2("Nguồn dữ liệu")
for t in ["dunnhumby. The Complete Journey; Breakfast at the Frat; Carbo-Loading; Let's Get Sort-of-Real (Sample 5K customers). https://www.dunnhumby.com/source-files/ (truy cập 07/11/2026).",
          "Kaggle / Walmart. M5 Forecasting – Accuracy. Bản lưu Zenodo, DOI 10.5281/zenodo.12636070, CC BY 4.0.",
          "Makridakis, S., Spiliotis, E., Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and conclusions. International Journal of Forecasting 38(4).",
          "Syntetos, A. A., Boylan, J. E., Croston, J. D. (2005). On the categorization of demand patterns. Journal of the Operational Research Society 56."]:
    bullet(t)
