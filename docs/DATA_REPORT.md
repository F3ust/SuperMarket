# Báo cáo dữ liệu: dự án phân tích kinh doanh siêu thị

Báo cáo mô tả toàn bộ dữ liệu dự án dùng: nguồn gốc, quy mô, cấu trúc, chất lượng, cách xử lý và dữ liệu đưa lên web demo. Mọi con số được tính tự động từ file gốc bằng `research/data_report/profile_data.py` (lần chạy 2026-11-17 01:10). Báo cáo phân tích kinh doanh nằm ở `outputs/multisource/Bao_cao_phan_tich_da_nguon.docx`; báo cáo này chỉ nói về dữ liệu.

## Tóm tắt

- 7 bộ dữ liệu công khai, 154 file, 2,44 GB trên đĩa. 5 bộ dùng cho phân tích đa nguồn và web: Complete Journey, Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real (dunnhumby) và Walmart M5. 2 bộ của vòng khảo sát đầu: UCI Online Retail và Complete Journey bản gói R.
- Khoảng 115 triệu dòng (tính M5 theo ô ngày × chuỗi SKU-cửa hàng), giai đoạn 2006–2016, Mỹ và Anh.
- Không có khóa chung giữa các nguồn (mã khách, mã hàng, mã cửa hàng đều riêng). Vì vậy dự án hài hòa ở mức chỉ số: tính cùng một chỉ số trong từng nguồn rồi so sánh, không nối dòng.
- Dữ liệu sạch về kỹ thuật: không có giá trị thiếu ở cột khóa giao dịch (trừ mã khách của LGSR và UCI: khách vãng lai), 0 dòng trùng hoàn toàn ở CJ, 0 ở Carbo. Vấn đề chính là về nghiệp vụ: panel không phải toàn bộ khách, nhu cầu cấp SKU-ngày phần lớn bằng 0 (60% ô của M5 sau ngày lên kệ), LGSR là dữ liệu mô phỏng, không có giá vốn hay tồn kho ở nguồn nào.
- Web demo chỉ dùng 2,1 MB dữ liệu đã tổng hợp; tổng lượng bán M5 trên web khớp file gốc (66.927.173 so với 66.927.173 đơn vị).

## 1. Danh mục nguồn dữ liệu

| Nguồn | Đơn vị phát hành | Giai đoạn | Hạt dữ liệu | Số file | Dung lượng | Số dòng |
|---|---|---|---|---|---|---|
| The Complete Journey | dunnhumby | 102 tuần (711 ngày) | Dòng hóa đơn của 2.500 hộ | 8 | 847,0 MB | 39.609.514 |
| Breakfast at the Frat | dunnhumby | 2009-01-14 → 2012-01-04 | Tuần × cửa hàng × SKU | 1 xlsx (3 sheet) | 31,6 MB | 525.087 |
| Carbo-Loading | dunnhumby | 104 tuần | Dòng giao dịch hộ, 4 ngành | 3 | 287,8 MB | 5.549.980 |
| Let's Get Sort-of-Real (mẫu 5K) | dunnhumby (mô phỏng) | tuần 200607 → 200819 | Dòng giỏ hàng có nhãn | 115 + 1 | 443,0 MB | 3.105.213 |
| M5 Forecasting | Walmart / Kaggle (bản Zenodo) | 2011-01-29 → 2016-05-22 | Ngày × cửa hàng × SKU; giá tuần | 4 | 325,2 MB | 66.024.180 |
| Online Retail | UCI ML Repository | 2010-12-01 → 2011-12-09 | Dòng hóa đơn bán lẻ online (Anh) | 1 | 23,7 MB | 541.909 |
| Complete Journey (gói R) | 84.51° / B. Boehmke | 2017 (1 năm) | Dòng hóa đơn, 2.469 hộ | 7 rds/rda | 14,2 MB | 1.469.307 |

*Số dòng M5 tính theo ô ngày × chuỗi (30.490 chuỗi × 1.941 ngày) cộng bảng giá và lịch. Dung lượng là file đã giải nén.*

### Bản quyền và trích dẫn

- dunnhumby Source Files (Complete Journey, Breakfast at the Frat, Carbo-Loading, Let's Get Sort-of-Real): https://www.dunnhumby.com/source-files/ . Dùng theo điều khoản trên trang dunnhumby; repository không chứa file gốc.
- M5 Forecasting – Accuracy: Makridakis, Spiliotis, Assimakopoulos (2022), bản lưu trên Zenodo record 12636070 (https://zenodo.org/records/12636070), dữ liệu gốc của cuộc thi Kaggle.
- Online Retail: Chen, D. (2015), UCI Machine Learning Repository, https://doi.org/10.24432/C5BW33, CC BY 4.0.
- completejourney (gói R): Boehmke & Mortimer, https://github.com/bradleyboehmke/completejourney, dữ liệu 84.51°.

## 2. Hồ sơ từng nguồn

### 2.1 The Complete Journey (dunnhumby, bản gốc)

Panel 2.500 hộ mua thường xuyên tại một chuỗi bán lẻ Mỹ trong 2 năm. Là nguồn duy nhất có cả mã hộ, nhân khẩu học, chiến dịch marketing, coupon và trưng bày/tờ rơi theo cửa hàng-tuần.

| Bảng | File | Số dòng | Số cột | Cột có giá trị thiếu |
|---|---|---|---|---|
| transaction_data | transaction_data.csv | 2.595.732 | 12 | không |
| causal_data | causal_data.csv | 36.786.524 | 5 | không |
| product | product.csv | 92.353 | 7 | không |
| hh_demographic | hh_demographic.csv | 801 | 8 | không |
| campaign_table | campaign_table.csv | 7.208 | 3 | không |
| campaign_desc | campaign_desc.csv | 30 | 4 | không |
| coupon | coupon.csv | 124.548 | 3 | không |
| coupon_redempt | coupon_redempt.csv | 2.318 | 4 | không |

| Chỉ tiêu | Giá trị | Ghi chú |
|---|---|---|
| Hộ / giỏ / mặt hàng / cửa hàng | 2.500 / 276.484 / 92.339 / 582 | 444/582 cửa hàng có dưới 50 giỏ: hộ panel thỉnh thoảng mua ở cửa hàng khác |
| Ngày, tuần | DAY 1–711, WEEK 1–102 | Ngày tương đối, không có ngày lịch; ngày nào cũng có giao dịch |
| Doanh thu (SALES_VALUE) | 8.057.463 USD | Giá đã trừ giảm giá thẻ; tổng giảm giá 1.448.522 USD |
| Dòng SALES_VALUE ≤ 0 | 18.850 (0,73%) | Tất cả đều bằng 0, không có giá trị âm: đổi trả không ghi thành dòng âm |
| Dòng QUANTITY = 0 / > 1.000 | 14.466 / 23.101 | Số lượng > 1.000 chủ yếu thuộc KIOSK-GAS (nhiên liệu): loại khi tính lượng mua |
| Giảm giá dương (sai dấu) | RETAIL_DISC 36, COUPON_DISC 0 | Giảm giá ghi số âm; dòng dương là điều chỉnh |
| Dòng trùng hoàn toàn | 0 |  |
| Mặt hàng không có trong product.csv | 0 | Khóa PRODUCT_ID khớp đầy đủ |
| Hộ có nhân khẩu học / có chiến dịch | 801 (32%) / 1.584 | Phân tích thu nhập chỉ trên 801 hộ |
| TRANS_TIME sai định dạng | 0 | Dạng HHMM |
| Giỏ nằm ở > 1 cửa hàng / > 1 ngày | 0 / 0 | BASKET_ID nhất quán |
| Trung vị số tuần có mua của một hộ | 50 | Panel chọn hộ mua thường xuyên |
| 10 cửa hàng lớn nhất chiếm | 19% doanh thu | Doanh thu panel trải trên nhiều cửa hàng |
| causal_data: tuần, cửa hàng | tuần 9–101, 115 cửa hàng | Chỉ ghi SKU-cửa hàng-tuần có trưng bày hoặc tờ rơi |

Phân bố mã trưng bày (display) trong causal_data: 0: 21.038.745; 1: 1.102.141; 2: 1.812.840; 3: 2.073.738; 4: 592.985; 5: 2.575.289; 6: 1.816.021; 7: 2.362.118; 9: 2.699.467; A: 713.180. Mã tờ rơi (mailer): 0: 11.534.183; A: 17.106.789; C: 291.059; D: 4.467.453; F: 1.077.549; H: 1.560.395; J: 306.924; L: 301.327; P: 569; X: 120.823; Z: 19.453. Mã 0 nghĩa là không có; ý nghĩa các mã khác theo User Guide.

Bậc thu nhập (classification_3) trong 801 hộ có nhân khẩu học: Level5 192; Level4 172; Level6 96; Level3 77; Level2 74; Level1 61; Level8 38; Level7 34; Level9 30; Level12 11; Level10 11; Level11 5.

### 2.2 Breakfast at the Frat (dunnhumby)

Dữ liệu tuần × cửa hàng × SKU của 4 ngành (snack đóng gói, ngũ cốc, pizza đông lạnh, vệ sinh răng miệng), có cả giá bán (PRICE) và giá cơ sở (BASE_PRICE), cờ tờ rơi (FEATURE), trưng bày (DISPLAY), giảm giá tạm thời (TPR_ONLY). Đây là nguồn tốt nhất để ước lượng độ co giãn giá.

| Bảng | File | Số dòng | Số cột | Cột có giá trị thiếu |
|---|---|---|---|---|
| dh_Transaction_Data | dunnhumby - Breakfast at the Frat.xlsx · sheet dh_Transaction_Data | 524.950 | 12 | PRICE (23 dòng, 0,00%), BASE_PRICE (185 dòng, 0,04%) |
| dh_Products_Lookup | dunnhumby - Breakfast at the Frat.xlsx · sheet dh_Products_Lookup | 58 | 6 | không |
| dh_Store_Lookup | dunnhumby - Breakfast at the Frat.xlsx · sheet dh_Store_Lookup | 79 | 9 | PARKING_SPACE_QTY (52 dòng, 65,8%) |

| Chỉ tiêu | Giá trị | Ghi chú |
|---|---|---|
| Tuần / cửa hàng / UPC | 156 / 77 / 55 | 2009-01-14 → 2012-01-04 |
| Tổng lượng / doanh thu | 10.293.354 đơn vị / 27.927.723 USD |  |
| PRICE thiếu / BASE_PRICE thiếu | 23 / 185 | Dòng thiếu giá cơ sở bị loại khỏi hồi quy giá |
| PRICE > BASE_PRICE | 4.710 | Giá bán cao hơn giá cơ sở; loại khi tính mức giảm giá |
| Tỷ lệ tuần có tờ rơi / trưng bày / chỉ giảm giá | 8,4% / 11,0% / 13,5% | Đủ biến thiên để tách hiệu ứng |
| Dòng UNITS ≤ 0 | 5 | Tuần không bán không được ghi thành dòng 0 |
| Trùng khóa tuần-cửa hàng-UPC | 0 |  |
| Độ đầy của panel | 86,1% | Tỷ lệ ô tuần × (cửa hàng, UPC) có dòng; ô vắng là không bán hoặc không kinh doanh |

### 2.3 Carbo-Loading (dunnhumby)

Dòng giao dịch của hộ cho 4 ngành bổ trợ nhau: mì Ý, sốt mì Ý, bột bánh pancake, siro. Có tờ rơi và trưng bày theo tuần-cửa hàng-UPC.

| Bảng | File | Số dòng | Số cột | Cột có giá trị thiếu |
|---|---|---|---|---|
| dh_transactions | dh_transactions.csv | 5.197.681 | 11 | không |
| dh_causal_lookup | dh_causal_lookup.csv | 351.372 | 6 | không |
| dh_product_lookup | dh_product_lookup.csv | 927 | 5 | không |

| Chỉ tiêu | Giá trị | Ghi chú |
|---|---|---|
| Hộ / giỏ / cửa hàng / UPC | 510.027 / 3.316.349 / 387 / 927 |  |
| Tuần, ngày | tuần 1–104, ngày 1–728 | Ngày tương đối |
| Doanh thu | 9.130.080 USD | Theo ngành: pasta sauce 4.025.026; pasta 2.851.931; syrups 1.741.309; pancake mixes 511.814 |
| Dòng doanh thu ≤ 0 / lượng ≤ 0 | 9.585 / 0 |  |
| Dòng có coupon | 91.188 (1,75%) |  |
| Dòng trùng hoàn toàn | 0 |  |
| UPC không có trong bảng sản phẩm | 0 |  |
| Giá đơn vị > 20 USD | 0 | Không có giá ngoại lai |
| Vùng (geography): số cửa hàng | vùng 1: 227; vùng 2: 160 |  |

Lưu ý phạm vi: Carbo chỉ ghi 4 ngành, nên giỏ hàng bị cắt. Mức bổ trợ (lift) giữa mì Ý và sốt tính trên Carbo khác hẳn khi tính trên giỏ đầy đủ của CJ (0,90 so với 9,81). Đây là ví dụ rõ nhất trong dự án về việc phạm vi dữ liệu quyết định kết luận.

### 2.4 Let's Get Sort-of-Real (dunnhumby, mẫu 5.000 khách)

Dữ liệu mô phỏng (synthetic) do dunnhumby tạo, có sẵn nhãn loại chuyến mua, độ nhạy giá của giỏ, nhiệm vụ giỏ, định dạng và vùng cửa hàng, giờ mua. Dùng để thử phương pháp và đặt giả thuyết, không dùng để rút con số thị trường.

| Bảng | File | Số dòng | Số cột | Cột có giá trị thiếu |
|---|---|---|---|---|
| transactions_YYYYWW | 115 file tuần transactions_*.csv | 3.105.071 | 22 | CUST_CODE (607.203 dòng, 19,6%), seg_1 (607.203 dòng, 19,6%), seg_2 (909.141 dòng, 29,3%) |
| time | time.csv | 142 | 3 | không |

| Chỉ tiêu | Giá trị | Ghi chú |
|---|---|---|
| File tuần / tuần có dữ liệu | 115 / 115 | tuần 200607–200819; thiếu tuần 200608, 200703 (không có trong file zip gốc) |
| Khách / giỏ / cửa hàng / mặt hàng | 4.983 / 482.636 / 761 / 4.997 |  |
| Dòng không có mã khách | 607.203 (19,6%) | Khách vãng lai; loại khỏi phân tích theo khách |
| Dòng thiếu phân khúc khách (seg_1) | 607.203 |  |
| Chi tiêu | 5.933.712 (đơn vị tiền không nêu) | 6 dòng ≤ 0 |
| Giờ mua | 8–22 giờ |  |
| Loại chuyến (số giỏ) | Small Shop: 265.908; Top Up: 158.439; Full Shop: 52.053; XX: 6.236 | XX là chưa phân loại |
| Định dạng cửa hàng | LS: 330; MS: 236; SS: 167; XLS: 28 | Số cửa hàng theo định dạng |

### 2.5 Walmart M5 Forecasting

Lượng bán theo ngày của 3.049 mặt hàng tại 10 cửa hàng ở 3 bang (California, Texas, Wisconsin), kèm giá bán theo tuần, lịch sự kiện và ngày chi trả trợ cấp thực phẩm SNAP. Là nguồn duy nhất có cấu trúc chuỗi cửa hàng đầy đủ theo ngày, nên được dùng cho bảng điều hành và dự báo.

| Bảng | File | Số dòng | Số cột | Cột có giá trị thiếu |
|---|---|---|---|---|
| sales_train_evaluation | sales_train_evaluation.csv | 30.490 | 7 | không |
| calendar | calendar.csv | 1.969 | 14 | event_name_1 (1.807 dòng, 91,8%), event_type_1 (1.807 dòng, 91,8%), event_name_2 (1.964 dòng, 99,7%), event_type_2 (1.964 dòng, 99,7%) |
| sell_prices | sell_prices.csv | 6.841.121 | 4 | không |

| Chỉ tiêu | Giá trị | Ghi chú |
|---|---|---|
| Chuỗi SKU-cửa hàng × ngày | 30.490 × 1.941 = 59.181.090 ô | 3.049 SKU, 7 nhóm hàng, 3 ngành, 10 cửa hàng, 3 bang |
| Tổng lượng bán | 66.927.173 | Ô âm: 0 |
| Ô bằng 0 (toàn bộ) | 68,0% | Trong đó 20,9% số ô là trước ngày SKU lên kệ |
| Ô bằng 0 sau ngày lên kệ | 59,5% | Nhu cầu gián đoạn: cần mô hình riêng (Croston/TSB, Poisson) |
| Ô bằng 0 theo ngành | FOODS 61,8%; HOBBIES 77,1%; HOUSEHOLD 71,6% |  |
| Chuỗi không bán lần nào | 0 |  |
| Ngày gần như không bán (< 1% trung bình) | d_331, d_697, d_1062, d_1427, d_1792 | Đều là 25/12 (2011–2015): cửa hàng đóng cửa; gắn cờ khi dự báo |
| Bảng giá: dòng / thiếu / ≤ 0 | 6.841.121 / 0 / 0 | Giá 0,01–107,32 USD |
| Tỷ lệ tuần đổi giá | 1,2% | Giá đổi thưa, theo bước |
| Ô có bán và có giá tuần | 100,00% | Ước tính trên mẫu 3.000 chuỗi; doanh thu = lượng × giá tuần |
| Ngày có sự kiện / ngày SNAP | 162 / CA 650, TX 650, WI 650 | Mỗi bang 10 ngày SNAP mỗi tháng |

sales_train_validation.csv là 1.913 ngày đầu của sales_train_evaluation.csv (dùng bản evaluation 1.941 ngày).

### 2.6 Nguồn của vòng khảo sát đầu

| Chỉ tiêu | Online Retail (UCI) | Ghi chú |
|---|---|---|
| Hóa đơn / khách / quốc gia | 25.900 / 4.372 / 38 | Anh chiếm 91% số dòng |
| Dòng thiếu CustomerID | 135.080 (24,9%) | Không gắn được khách |
| Dòng hủy (InvoiceNo bắt đầu bằng C) | 9.288 |  |
| Quantity ≤ 0 / UnitPrice ≤ 0 | 10.624 / 2.517 |  |
| Dòng trùng hoàn toàn | 5.268 |  |
| Mã không phải hàng (phí, bưu phí…) | 2.916 | POST, M, BANK CHARGES… |

Complete Journey bản gói R (dùng cho dashboard_enterprise và retail_pipeline): 1.469.307 dòng, 2.469 hộ, 2017-01-01 → 2018-01-01, doanh thu 4.596.040 USD. Đây là bản xử lý lại, có ngày giờ thật, khác bản gốc 2 năm ở mục 2.1.

Online Retail là bán lẻ quà tặng trực tuyến ở Anh, không phải siêu thị; chỉ dùng ở vòng khảo sát, không trộn vào phân tích đa nguồn.

## 3. Vấn đề chất lượng và cách xử lý

| Vấn đề | Nguồn | Bằng chứng | Ảnh hưởng | Cách xử lý |
|---|---|---|---|---|
| Panel không phải toàn bộ khách | CJ, Carbo | CJ chỉ 2.500 hộ mua thường xuyên | Mức tập trung, tăng trưởng không đại diện cho toàn cửa hàng | Chỉ so sánh chỉ số tương đối, ghi rõ giới hạn |
| Nhu cầu gián đoạn | M5 | 60% ô bằng 0 sau ngày lên kệ | Sai số % (MAPE) vô nghĩa; mô hình chuẩn đoán sai | Đánh giá bằng WRMSSE, WAPE; phân loại kiểu nhu cầu |
| Ô trước ngày lên kệ ghi 0 | M5 | 20,9% số ô | Tỷ lệ 0 bị thổi phồng | Cắt chuỗi từ ngày bán đầu tiên |
| Ngày đóng cửa | M5 | 5 ngày 25/12 (d_331, d_697, d_1062, d_1427, d_1792) gần như không bán | Kéo lệch trung bình và mô hình | Gắn cờ ngày lễ, loại khỏi huấn luyện |
| Không có giá vốn, tồn kho | Tất cả | Không có trường cost, on-hand | Không tính được lợi nhuận thật, không phân biệt hết hàng với không có nhu cầu | Biên gộp là tham số người dùng nhập trong mô phỏng |
| Giá bán so với giá cơ sở | BATF | 185 dòng thiếu BASE_PRICE | Sai lệch độ co giãn | Hồi quy log–log với hiệu ứng cố định, loại dòng thiếu |
| Giỏ bị cắt theo ngành | Carbo | Chỉ 4 ngành | Lift giỏ hàng sai lệch (0,90 so với 9,81) | Không suy luận bổ trợ từ Carbo; dùng CJ |
| Dữ liệu mô phỏng | LGSR | Do dunnhumby sinh | Không phản ánh hành vi thật | Chỉ dùng thử phương pháp, đặt giả thuyết |
| Đổi trả, điều chỉnh | CJ, Online Retail | CJ 18.850 dòng giá trị 0; UCI 9.288 dòng hủy | Doanh thu ròng và lượng mua bị lệch nếu không tách | Giữ trong doanh thu ròng, loại khi mô hình hóa lượng mua |
| Khách vãng lai | LGSR, Online Retail | LGSR 19,6%, UCI 24,9% dòng không có mã khách | Phân tích khách bỏ sót | Phân tích khách chỉ trên dòng có mã |
| Ngày tương đối | CJ, Carbo | DAY 1…711, không có ngày lịch | Không gắn được lễ, mùa vụ thật | Dùng tuần tương đối; mùa vụ lấy từ M5 |
| Không có khóa chung | Tất cả | Mã khách, hàng, cửa hàng riêng từng nguồn | Không nối dòng được | Hài hòa ở mức chỉ số (mục 4) |

## 4. Hài hòa nhiều nguồn

Vì các nguồn không có khóa chung, dự án không nối dòng. Mỗi chỉ số (mức tập trung doanh thu, độ co giãn giá, mức tăng khi trưng bày, nhịp theo giờ…) được tính riêng trong từng nguồn bằng cùng phương pháp, rồi so sánh. Một kết luận được coi là đáng tin khi nhiều nguồn độc lập cho cùng kết quả. Bảng dưới là ma trận nhóm trường: nguồn nào có trường nào.

| Nhóm trường | CJ | BATF | Carbo | LGSR | M5 | Ghi chú |
|---|---|---|---|---|---|---|
| Mã khách / hộ | có |  | có | có |  | Có trong CJ, Carbo; LGSR có nhưng 20% giỏ không thẻ |
| Mã giỏ / hóa đơn | có |  | có | có |  |  |
| Giờ giao dịch | có |  | có | có |  | LGSR theo khung giờ |
| Giá kệ / giá cơ sở |  | có |  |  |  | Chỉ BATF tách giá thực và giá cơ sở |
| Giá bán thực tế | có | có | có |  | có | CJ, Carbo phải tự suy ra = tiền/đơn vị |
| Giảm giá thẻ thành viên | có |  |  |  |  |  |
| Coupon | có |  | có |  |  | Carbo: cờ 0/1; CJ: số tiền + chiến dịch |
| Tờ rơi / quảng cáo | có | có | có |  |  | Carbo chỉ từ tuần 43 |
| Trưng bày tại cửa hàng | có | có | có |  |  |  |
| Chiến dịch marketing trực tiếp | có |  |  |  |  |  |
| Nhân khẩu học hộ | có |  |  |  |  | 801/2.500 hộ |
| Phân khúc khách / độ nhạy giá |  |  |  | có |  | Nhãn có sẵn, dữ liệu mô phỏng |
| Thuộc tính cửa hàng |  | có |  | có | có | BATF: diện tích, phân khúc; LGSR: định dạng, vùng; M5: bang |
| Thương hiệu / nhãn riêng | có | có | có |  |  |  |
| Lịch lễ & sự kiện |  |  |  |  | có |  |
| Trợ cấp thực phẩm (SNAP) |  |  |  |  | có | Biến chính sách duy nhất |
| Ngày không bán (zero) |  |  |  |  | có | Chỉ M5 ghi nhận lượng 0 tường minh |

## 5. Luồng xử lý và dòng dõi dữ liệu

| Bước | Script | Đầu vào | Đầu ra |
|---|---|---|---|
| Tải dữ liệu | research/download_data.py; tải tay từ dunnhumby, Zenodo | Internet | data/raw, data/raw_dunnhumby, data/raw_m5 (+ data/manifest.json) |
| Hồ sơ dữ liệu | research/data_report/profile_data.py | data/raw* | outputs/data_report/profile.json, báo cáo này |
| Phân tích đa nguồn | research/multisource/analyze_multisource.py, analyze_deep.py | data/raw_dunnhumby, data/raw_m5 | outputs/multisource/results.json, results_deep.json |
| Biểu đồ, báo cáo | make_figures.py, build_html.py, build_word.py | results*.json | outputs/multisource/*.html, *.docx, figures/ |
| Đóng gói cho web | webapp/backend/scripts/build_cache.py | results*.json, trang HTML, data/raw_m5, data/raw_dunnhumby | webapp/backend/data/* |
| Pipeline gói R (vòng đầu) | retail_pipeline/run.py, dashboard_enterprise/build_*.py | data/raw (CJ gói R) | outputs/enterprise, dashboard_enterprise/dist |

### Dữ liệu web dùng

| File | Dung lượng | Số dòng | Cột | SHA-256 (16 ký tự đầu) |
|---|---|---|---|---|
| chart_data.json | 79,8 KB | JSON |  | 9c547157bf08273d |
| cj_dept_weekly.parquet | 58,9 KB | 2.544 | week, department, sales, baskets, households, discount, private_sales | da6bc63b20c71464 |
| content.json | 46,1 KB | JSON |  | b41125f2a3f8e4b6 |
| m5_calendar.parquet | 22,3 KB | 1.941 | date, event_name_1, event_type_1, snap_CA, snap_TX, snap_WI | ad3d883725a5bce0 |
| m5_store_dept_daily.parquet | 1.613,9 KB | 135.870 | date, store, state, dept, cat, units, revenue, zero_share | 26c23736dbd6e4d5 |
| results.json | 214,1 KB | JSON |  | 794ae226565fe2da |
| results_deep.json | 39,1 KB | JSON |  | 1fc5882424f84dc3 |

Đối soát: bảng m5_store_dept_daily.parquet (ngày × cửa hàng × nhóm hàng) có tổng lượng 66.927.173 so với 66.927.173 ở file gốc (khớp tuyệt đối), giai đoạn 2011-01-29 → 2016-05-22, doanh thu ước tính 191.577.546 USD.

## 6. Dữ liệu cần từ siêu thị khi triển khai

Bản demo thiếu những trường mà một chuỗi siêu thị thật có. Khi triển khai, cần các bảng sau (chi tiết khóa và quy tắc ở CHAIN_ROLLOUT.md):

| Bảng | Khóa | Lấp khoảng trống nào của bản demo |
|---|---|---|
| Hóa đơn POS | cửa hàng + ngày + số hóa đơn + dòng | Doanh thu toàn bộ khách, không chỉ panel; ngày lịch thật |
| Danh mục mặt hàng | mã hàng + thời gian hiệu lực | Khóa chung giữa POS, ERP, kho |
| Giá và khuyến mãi | cửa hàng + mã hàng + khoảng hiệu lực | Giá cơ sở, tờ rơi, trưng bày theo cửa hàng-tuần |
| Tồn kho | địa điểm + mã hàng + ngày | Phân biệt hết hàng với không có nhu cầu |
| Giá vốn | mã hàng + thời gian hiệu lực | Lợi nhuận thật thay cho biên gộp giả định |
| Thẻ thành viên | mã khách ẩn danh toàn chuỗi | Phân tích khách xuyên cửa hàng |

## 7. Tái lập dữ liệu

Dữ liệu thô không nằm trong repository (2,3 GB; nhiều file trên 100 MB, vượt giới hạn 100 MB/file của GitHub). Tải về và đặt đúng thư mục:

| Thư mục | Nguồn | File | SHA-256 file nén |
|---|---|---|---|
| data/raw_dunnhumby/ | https://www.dunnhumby.com/source-files/ (đăng ký, tải 4 bộ) | dunnhumby_The-Complete-Journey.zip | 5e0a3d72fe8562fe0ab995f70fb58b74359e8ec4bbccd1521e2b137da0558f9a |
|  |  | dunnhumby_Breakfast-at-the-Frat.zip | 74cb41cb8b19dc61bb8a5731c3774b802e9a8da3b64cdd1872640890d0b54216 |
|  |  | dunnhumby_Carbo-Loading.zip | 64f2d0793ab1a6d0a0a1c981122cd6eeafb451e6328a10085b345cdc0156b10a |
|  |  | dunnhumby_Let-s-Get-Sort-of-Real-_Sample-5K-customers_.zip | 4c847515b74592c5d368433543b12585460e0c789cef7b129358a357bac1cfb7 |
| data/raw_m5/ | https://zenodo.org/records/12636070 | m5-forecasting-accuracy.zip | 0349ba38a2efd30d0f5acc6394c1110e140e1a990c650d7b5ca44c5b25dd12f5 |
| data/raw/ | python research/download_data.py | UCI Online Retail, gói R completejourney | xem data/manifest.json |

Giải nén mỗi file zip vào thư mục cùng tên (bỏ đuôi .zip). Sau đó chạy:

```bash
python3 research/data_report/profile_data.py      # hồ sơ dữ liệu
python3 research/data_report/build_data_report.py  # báo cáo này
python3 research/multisource/analyze_multisource.py && python3 research/multisource/analyze_deep.py
python3 webapp/backend/scripts/build_cache.py       # dữ liệu cho web
```

## Phụ lục: từ điển dữ liệu

Mọi bảng thô, mỗi cột: kiểu (duckdb tự nhận), số giá trị thiếu và số giá trị khác nhau (ước lượng HyperLogLog, sai số khoảng 2%).

### Complete Journey · transaction_data (2.595.732 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| household_key | BIGINT | 0 | 2.532 |
| BASKET_ID | BIGINT | 0 | 290.226 |
| DAY | BIGINT | 0 | 709 |
| PRODUCT_ID | BIGINT | 0 | 92.005 |
| QUANTITY | BIGINT | 0 | 11.625 |
| SALES_VALUE | DOUBLE | 0 | 5.403 |
| STORE_ID | BIGINT | 0 | 587 |
| RETAIL_DISC | DOUBLE | 0 | 2.309 |
| TRANS_TIME | VARCHAR | 0 | 1.427 |
| WEEK_NO | BIGINT | 0 | 104 |
| COUPON_DISC | DOUBLE | 0 | 413 |
| COUPON_MATCH_DISC | DOUBLE | 0 | 81 |

### Complete Journey · causal_data (36.786.524 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| PRODUCT_ID | BIGINT | 0 | 67.375 |
| STORE_ID | BIGINT | 0 | 114 |
| WEEK_NO | BIGINT | 0 | 94 |
| display | VARCHAR | 0 | 10 |
| mailer | VARCHAR | 0 | 11 |

### Complete Journey · product (92.353 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| PRODUCT_ID | BIGINT | 0 | 92.005 |
| MANUFACTURER | BIGINT | 0 | 6.359 |
| DEPARTMENT | VARCHAR | 0 | 42 |
| BRAND | VARCHAR | 0 | 2 |
| COMMODITY_DESC | VARCHAR | 0 | 302 |
| SUB_COMMODITY_DESC | VARCHAR | 0 | 2.424 |
| CURR_SIZE_OF_PRODUCT | VARCHAR | 0 | 4.392 |

### Complete Journey · hh_demographic (801 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| classification_1 | VARCHAR | 0 | 6 |
| classification_2 | VARCHAR | 0 | 3 |
| classification_3 | VARCHAR | 0 | 12 |
| HOMEOWNER_DESC | VARCHAR | 0 | 5 |
| classification_5 | VARCHAR | 0 | 6 |
| classification_4 | VARCHAR | 0 | 5 |
| KID_CATEGORY_DESC | VARCHAR | 0 | 4 |
| household_key | BIGINT | 0 | 820 |

### Complete Journey · campaign_table (7.208 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| DESCRIPTION | VARCHAR | 0 | 3 |
| household_key | BIGINT | 0 | 1.609 |
| CAMPAIGN | BIGINT | 0 | 30 |

### Complete Journey · campaign_desc (30 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| DESCRIPTION | VARCHAR | 0 | 3 |
| CAMPAIGN | BIGINT | 0 | 30 |
| START_DAY | BIGINT | 0 | 26 |
| END_DAY | BIGINT | 0 | 28 |

### Complete Journey · coupon (124.548 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| COUPON_UPC | BIGINT | 0 | 1.142 |
| PRODUCT_ID | BIGINT | 0 | 46.034 |
| CAMPAIGN | BIGINT | 0 | 30 |

### Complete Journey · coupon_redempt (2.318 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| household_key | BIGINT | 0 | 439 |
| DAY | BIGINT | 0 | 331 |
| COUPON_UPC | BIGINT | 0 | 564 |
| CAMPAIGN | BIGINT | 0 | 30 |

### Breakfast at the Frat · dh_Transaction_Data (524.950 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| WEEK_END_DATE | TIMESTAMP_NS | 0 | 160 |
| STORE_NUM | BIGINT | 0 | 74 |
| UPC | BIGINT | 0 | 55 |
| UNITS | BIGINT | 0 | 571 |
| VISITS | BIGINT | 0 | 457 |
| HHS | BIGINT | 0 | 445 |
| SPEND | DOUBLE | 0 | 20.201 |
| PRICE | DOUBLE | 23 (0,0%) | 692 |
| BASE_PRICE | DOUBLE | 185 (0,0%) | 666 |
| FEATURE | BIGINT | 0 | 2 |
| DISPLAY | BIGINT | 0 | 2 |
| TPR_ONLY | BIGINT | 0 | 2 |

### Breakfast at the Frat · dh_Products_Lookup (58 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| UPC | BIGINT | 0 | 59 |
| DESCRIPTION | VARCHAR | 0 | 57 |
| MANUFACTURER | VARCHAR | 0 | 15 |
| CATEGORY | VARCHAR | 0 | 4 |
| SUB_CATEGORY | VARCHAR | 0 | 7 |
| PRODUCT_SIZE | VARCHAR | 0 | 30 |

### Breakfast at the Frat · dh_Store_Lookup (79 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| STORE_ID | BIGINT | 0 | 74 |
| STORE_NAME | VARCHAR | 0 | 74 |
| ADDRESS_CITY_NAME | VARCHAR | 0 | 51 |
| ADDRESS_STATE_PROV_CODE | VARCHAR | 0 | 4 |
| MSA_CODE | BIGINT | 0 | 9 |
| SEG_VALUE_NAME | VARCHAR | 0 | 3 |
| PARKING_SPACE_QTY | DOUBLE | 52 (65,8%) | 24 |
| SALES_AREA_SIZE_NUM | BIGINT | 0 | 72 |
| AVG_WEEKLY_BASKETS | DOUBLE | 0 | 79 |

### Carbo-Loading · dh_transactions (5.197.681 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| upc | VARCHAR | 0 | 923 |
| dollar_sales | DOUBLE | 0 | 1.482 |
| units | BIGINT | 0 | 49 |
| time_of_transaction | VARCHAR | 0 | 1.427 |
| geography | BIGINT | 0 | 2 |
| week | BIGINT | 0 | 105 |
| household | BIGINT | 0 | 508.416 |
| store | BIGINT | 0 | 383 |
| basket | BIGINT | 0 | 3.241.469 |
| day | BIGINT | 0 | 721 |
| coupon | BIGINT | 0 | 2 |

### Carbo-Loading · dh_causal_lookup (351.372 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| upc | VARCHAR | 0 | 478 |
| store | BIGINT | 0 | 378 |
| week | BIGINT | 0 | 61 |
| feature_desc | VARCHAR | 0 | 8 |
| display_desc | VARCHAR | 0 | 11 |
| geography | BIGINT | 0 | 2 |

### Carbo-Loading · dh_product_lookup (927 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| upc | BIGINT | 0 | 952 |
| product_description | VARCHAR | 0 | 870 |
| commodity | VARCHAR | 0 | 4 |
| brand | VARCHAR | 0 | 131 |
| product_size | VARCHAR | 0 | 147 |

### Let's Get Sort-of-Real · transactions_YYYYWW (3.105.071 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| SHOP_WEEK | BIGINT | 0 | 120 |
| SHOP_DATE | BIGINT | 0 | 806 |
| SHOP_WEEKDAY | BIGINT | 0 | 7 |
| SHOP_HOUR | BIGINT | 0 | 15 |
| QUANTITY | BIGINT | 0 | 94 |
| SPEND | DOUBLE | 0 | 3.357 |
| PROD_CODE | VARCHAR | 0 | 5.020 |
| PROD_CODE_10 | VARCHAR | 0 | 253 |
| PROD_CODE_20 | VARCHAR | 0 | 90 |
| PROD_CODE_30 | VARCHAR | 0 | 30 |
| PROD_CODE_40 | VARCHAR | 0 | 9 |
| CUST_CODE | VARCHAR | 607.203 (19,6%) | 4.919 |
| seg_1 | VARCHAR | 607.203 (19,6%) | 4 |
| seg_2 | VARCHAR | 909.141 (29,3%) | 6 |
| BASKET_ID | BIGINT | 0 | 458.556 |
| BASKET_SIZE | VARCHAR | 0 | 3 |
| BASKET_PRICE_SENSITIVITY | VARCHAR | 0 | 4 |
| BASKET_TYPE | VARCHAR | 0 | 4 |
| BASKET_DOMINANT_MISSION | VARCHAR | 0 | 5 |
| STORE_CODE | VARCHAR | 0 | 756 |
| STORE_FORMAT | VARCHAR | 0 | 4 |
| STORE_REGION | VARCHAR | 0 | 12 |

### Let's Get Sort-of-Real · time (142 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| shop_week | BIGINT | 0 | 144 |
| date_from | BIGINT | 0 | 144 |
| date_to | BIGINT | 0 | 144 |

### Walmart M5 · sales_train_evaluation (30.490 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| id | VARCHAR | 0 | 30.490 |
| item_id | VARCHAR | 0 | 3.049 |
| dept_id | VARCHAR | 0 | 7 |
| cat_id | VARCHAR | 0 | 3 |
| store_id | VARCHAR | 0 | 10 |
| state_id | VARCHAR | 0 | 3 |
| d_1 … d_1941 | INT (lượng bán ngày) | 0 | 1.941 |

### Walmart M5 · calendar (1.969 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| date | DATE | 0 | 1.975 |
| wm_yr_wk | BIGINT | 0 | 282 |
| weekday | VARCHAR | 0 | 7 |
| wday | BIGINT | 0 | 7 |
| month | BIGINT | 0 | 12 |
| year | BIGINT | 0 | 6 |
| d | VARCHAR | 0 | 1.999 |
| event_name_1 | VARCHAR | 1.807 (91,8%) | 29 |
| event_type_1 | VARCHAR | 1.807 (91,8%) | 4 |
| event_name_2 | VARCHAR | 1.964 (99,7%) | 4 |
| event_type_2 | VARCHAR | 1.964 (99,7%) | 2 |
| snap_CA | BIGINT | 0 | 2 |
| snap_TX | BIGINT | 0 | 2 |
| snap_WI | BIGINT | 0 | 2 |

### Walmart M5 · sell_prices (6.841.121 dòng)

| Cột | Kiểu | Thiếu | Giá trị khác nhau |
|---|---|---|---|
| store_id | VARCHAR | 0 | 10 |
| item_id | VARCHAR | 0 | 2.920 |
| wm_yr_wk | BIGINT | 0 | 282 |
| sell_price | DOUBLE | 0 | 1.042 |
