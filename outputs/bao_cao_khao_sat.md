# Khảo sát dữ liệu và đề xuất bài toán siêu thị

Ngày khảo sát: 01/11/2026. Mục tiêu: dùng dữ liệu công khai để kiểm chứng phương pháp và lập danh sách bài toán/dữ liệu cần trao đổi với doanh nghiệp. Kết quả dưới đây là phân tích khám phá và baseline; chưa chứng minh hiệu quả kinh doanh khi triển khai.

## 1. Bộ dữ liệu đã tải và lựa chọn

| Bộ dữ liệu | Nội dung và khả năng sử dụng | Trạng thái / giới hạn |
|---|---|---|
| [Complete Journey, bản do Brad Boehmke xử lý](https://bradleyboehmke.github.io/completejourney/) | Giao dịch hàng tiêu dùng, hộ mua hàng, cửa hàng, danh mục sản phẩm, chiết khấu, chiến dịch và coupon. Ưu tiên cho demo siêu thị. | Đã tải toàn bộ transactions và 6 bảng tham chiếu. Chưa tải bảng promotions lớn. Bản này có một năm; không trộn với mô tả bộ dunnhumby hai năm. DESCRIPTION của package ghi CC0. |
| [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) | Hóa đơn, mặt hàng, khách hàng, ngày giờ, giá, số lượng, quốc gia. Hữu ích cho RFM, giỏ hàng, chất lượng dữ liệu. | Đã tải và kiểm tra toàn bộ. Bán lẻ quà tặng trực tuyến ở Anh, có khách sỉ, không đại diện trực tiếp cho siêu thị Việt Nam. CC BY 4.0; tác giả Daqing Chen (2015), DOI 10.24432/C5BW33. |
| [Favorita Grocery Sales](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/data) | Dữ liệu bán hàng theo ngày–cửa hàng–mặt hàng, kèm cửa hàng, mặt hàng, khuyến mãi, ngày lễ. Phù hợp nghiên cứu dự báo theo SKU. | Đã tìm nguồn chính thức, chưa tải/kiểm chứng file. Cần kiểm tra quyền tải và điều kiện cuộc thi trên Kaggle. |
| [dunnhumby Source Files](https://www.dunnhumby.com/source-files/) | Breakfast at the Frat có giá cơ sở, giá kệ, lượng bán và hỗ trợ quảng bá theo tuần. Hữu ích cho giá/khuyến mãi. | Chưa tải: nút tải đi qua biểu mẫu. Nguồn tự mô tả là dữ liệu mô phỏng/đại diện thực tế; không mặc định mọi bộ là giao dịch gốc. |

File gốc giữ nguyên trong `data/raw/`; `data/manifest.json` lưu URL, kích thước, ngày tải và SHA-256. Hai bộ đã tải được phân tích độc lập, không nối khách hàng hay sản phẩm giữa chúng.

## 2. Kết quả kiểm tra Complete Journey

- 1,469,307 dòng, 155,848 giỏ hàng, 2,469 hộ, 457 mã cửa hàng, 68,509 sản phẩm xuất hiện trong giao dịch.
- Khoảng thời gian ghi trong file: 2017-01-01 11:53:26 đến 2018-01-01 04:01:20. Không suy diễn đây là thời điểm giao dịch gốc chưa qua xử lý của nhà phát hành.
- Tháng 01/2018 chỉ có phần đầu ngày 01/01. Biểu đồ chỉ so sánh các tháng đủ lịch trong năm 2017; CSV tháng vẫn giữ toàn bộ và có cột full_calendar_month để nhận diện.
- Tổng sales_value: 4,596,039.58 USD. Theo tài liệu, đây là số tiền nhà bán lẻ nhận, có quy tắc bù coupon của nhà sản xuất; không đồng nhất với tiền khách trả hay lợi nhuận. Không trừ chiết khấu lần nữa.
- Dòng trùng toàn bộ: 0; số lượng không dương: 8,869; sales_value không dương: 11,226. Các chỉ tiêu mô tả giữ nguyên giao dịch gốc; giỏ hàng chỉ dùng dòng có số lượng và sales_value dương. Chưa xác định ngữ nghĩa của từng dòng ngoại lệ.
- Sản phẩm không nối được danh mục: 4,836 dòng; dòng thiếu product_category: 7,045. Kiểm tra khóa products là duy nhất trước khi nối để tránh nhân doanh thu.
- Nhân khẩu học có 801 hộ, bao phủ 32.4% số hộ và 56.4% dòng giao dịch. Không dùng phân bố nhóm có hồ sơ để đại diện mọi khách hàng.
- 20% hộ có sales_value cao nhất đóng góp 54.6% sales_value. Đây là lý do có thể thử phân nhóm và chăm sóc khách hàng, chưa phải bằng chứng chiến dịch sẽ tăng doanh thu.
- 50.8% dòng có ít nhất một trường chiết khấu khác 0. Có thể nghiên cứu khuyến mãi, nhưng so sánh bán có/không giảm giá đơn giản chưa xác định tác động nhân quả.
- Đây là panel hộ mua hàng thường xuyên. Tổng theo cửa hàng chỉ phản ánh nhóm hộ quan sát, không phải doanh thu toàn bộ cửa hàng. Số lượng có nhiều quy cách/đơn vị; không cộng mọi quantity để kết luận tổng nhu cầu hàng hóa.

### Nhóm ngành đóng góp lớn

| department | sales_value | lines | share |
|---|---|---|---|
| GROCERY | 2316393.89 | 928997 | 50.4% |
| DRUG GM | 596827.45 | 156171 | 13.0% |
| FUEL | 329594.45 | 12997 | 7.2% |
| PRODUCE | 322858.82 | 147651 | 7.0% |
| MEAT | 308575.33 | 49822 | 6.7% |
| MEAT-PCKGD | 232282.53 | 63041 | 5.1% |
| DELI | 148344.06 | 35478 | 3.2% |

### Cặp ngành hàng cùng giỏ

| category_A | category_B | baskets_together | support | confidence_A_to_B | lift |
|---|---|---|---|---|---|
| CONDIMENTS/SAUCES | SALD DRSNG/SNDWCH SPRD | 2805 | 0.0181 | 0.2778 | 4.5544 |
| SOUP | VEGETABLES - SHELF STABLE | 4304 | 0.0277 | 0.3259 | 4.014 |
| FROZEN PIZZA | FRZN MEAT/MEAT DINNERS | 4058 | 0.0261 | 0.3149 | 3.7908 |
| CRACKERS/MISC BKD FD | SOUP | 4125 | 0.0265 | 0.3218 | 3.7852 |
| COOKIES/CONES | CRACKERS/MISC BKD FD | 2908 | 0.0187 | 0.3094 | 3.7495 |

Phương pháp: gom danh mục duy nhất trong mỗi giỏ có giao dịch dương; xét 30 danh mục xuất hiện trong nhiều giỏ nhất; chỉ báo cáo cặp cùng xuất hiện ít nhất 500 giỏ. Support = số giỏ có cả A,B / 155,368 giỏ hợp lệ; confidence A→B = số giỏ có cả / số giỏ có A; lift = support(A,B)/(support(A)×support(B)). Đây là kết quả mô tả cùng tập dữ liệu; cần xác nhận trên giai đoạn sau trước khi đề xuất combo. Lift cao không chứng minh mua A gây mua B.

### Thử baseline dự báo

Dự báo tổng sales_value của panel theo tuần. Loại tuần không đủ 7 ngày trong khoảng quan sát; kiểm tra 8 tuần đầy đủ cuối bằng rolling one-step-ahead, mỗi lần chỉ dùng tuần trước thời điểm dự báo. WAPE = tổng sai số tuyệt đối / tổng giá trị thực tế.

- Lặp lại tuần trước: WAPE 12.24%.
- Trung bình 4 tuần trước: WAPE 7.90%.

Chưa phải mô hình dự báo SKU/cửa hàng hay dự báo nhiều tuần cùng lúc. Tập kiểm tra nhỏ, chưa có chu kỳ nhiều năm và chưa xử lý khuyến mãi. Mô hình tiếp theo phải vượt baseline trên nhiều mốc thời gian và đánh giá theo nhóm hàng/cửa hàng.

## 3. Kiểm tra chéo UCI Online Retail

- 541,909 dòng từ 2010-12-01 08:26:00 đến 2011-12-09 12:50:00.
- Thiếu CustomerID: 135,080 dòng (24.9%); thiếu mô tả: 1,454 dòng; trùng toàn bộ: 5,268 dòng.
- 9,288 dòng có mã hóa đơn bắt đầu C; 10,624 dòng số lượng không dương; 2,517 dòng giá không dương. Các nhóm có thể giao nhau, không cộng số đếm để suy ra số dòng loại.
- Tập mua dương dùng Quantity>0, UnitPrice>0, hóa đơn không bắt đầu C, bỏ trùng toàn bộ: 524,878 dòng, 19,960 hóa đơn, 4,338 khách có mã. Tổng Quantity×UnitPrice = 10,642,110.80 GBP, chưa trừ hoàn/hủy, không gọi là doanh thu thuần.
- Giữ khách thiếu mã khi mô tả bán hàng; chỉ dùng khách có mã cho RFM/retention. Không mặc định dòng trùng chắc chắn là lỗi nếu triển khai với POS thực tế.
- Tháng 12/2011 chỉ có dữ liệu tới ngày 9, không so trực tiếp với tháng đủ ngày. Phát hiện thiếu dữ liệu trong file có ý nghĩa hơn nhãn “no missing” trên trang giới thiệu.

## 4. Bài toán ưu tiên và điều kiện dữ liệu

| Ưu tiên | Câu hỏi/quyết định | Dữ liệu tối thiểu từ doanh nghiệp | Demo công khai | Cách đánh giá |
|---|---|---|---|---|
| P0 | Hợp nhất số liệu bán hàng, tìm chênh lệch giữa POS–kho–kế toán | Chi tiết hóa đơn, danh mục SKU/cửa hàng, hoàn/hủy, thuế, chiết khấu; tổng đối soát | Complete Journey cho nối bảng; UCI cho ngoại lệ | Tỷ lệ nối khóa, thiếu/trùng, chênh lệch tiền theo ngày/cửa hàng |
| P1 | Doanh thu thay đổi do số giỏ, giá trị giỏ hay cơ cấu hàng? | POS theo dòng, nhóm hàng, cửa hàng, lịch | Complete Journey | Đối soát tổng; định nghĩa KPI thống nhất; phân rã biến động cùng kỳ |
| P1 | Khách nào đang giảm mua, nên chăm sóc ai? | Mã khách ẩn danh bền vững, hóa đơn và lịch tương tác | RFM/recency trên Complete Journey và UCI | Retention theo cohort; đánh giá ở mốc tương lai; thử nghiệm nhóm đối chứng cho chiến dịch |
| P1 | Mặt hàng nào thường đi cùng để thử combo/trưng bày? | basket_id, SKU, số lượng, ngày, cửa hàng | Cặp ngành hàng trong Complete Journey; có thể mở xuống SKU | Support/lift trên thời kỳ sau; A/B test doanh thu hoặc lãi/giỏ |
| P2 | Cần dự kiến bán bao nhiêu theo SKU–cửa hàng trong 7/14 ngày? | Lịch sử bán 12–24 tháng, ngày mở cửa, khuyến mãi, giá, tình trạng hết hàng | Baseline panel đã chạy; Favorita là ứng viên cho SKU | Rolling backtest, WAPE/MAE và bias; tách hàng bán chậm và hàng mới |
| P2 | Khuyến mãi nào tăng lãi sau chi phí? | Lịch chương trình, SKU/cửa hàng áp dụng, giá thường/giảm, giá vốn, tài trợ, nhóm đối chứng | Complete Journey có discount/campaign/coupon; chưa có lợi nhuận | Incremental gross profit, cannibalization, A/B hoặc thiết kế nhân quả phù hợp |
| P2 | Đặt hàng bao nhiêu, tránh hết hàng/dư hàng? | Tồn hàng ngày, nhập/xuất/chuyển, lead time, MOQ, chi phí giữ hàng, lịch bán | Chỉ demo dự báo từ dữ liệu hiện có; chưa tối ưu tồn kho thực | Service level/fill rate, thiếu hàng, ngày tồn; mô phỏng có ràng buộc |
| P3 | Giảm hủy hàng cận hạn và thất thoát? | Lô/hạn dùng, kiểm kê, hủy, điều chỉnh kho, lượng nhập/bán | Hai bộ đã tải không đủ | Giá trị hủy, sai lệch kho; kiểm tra nghiệp vụ cảnh báo |
| P3 | Cửa hàng/danh mục/nhà cung cấp nào đem lại lợi nhuận tốt? | Giá vốn hiệu lực theo ngày, chi phí phân bổ, trả hàng, hợp đồng NCC, PO và nhận hàng | Hai bộ đã tải không đủ để tính lãi/hiệu suất NCC | Lãi gộp, GMROI khi đủ tồn kho theo giá vốn, OTIF |

Không kết luận doanh nghiệp cần toàn bộ bài toán trên. Đây là danh mục để phỏng vấn và chọn theo quyết định kinh doanh, mức độ sẵn sàng dữ liệu và khả năng đo hiệu quả.

## 5. Gói dữ liệu cần xin và cách xử lý SILO

Xin trước một mẫu 2–4 tuần ở 1–3 cửa hàng để kiểm tra cấu trúc; nếu hợp lệ, xin lịch sử liên tục 12–24 tháng. Với dự báo mùa vụ, ưu tiên đủ hai chu kỳ năm nếu có. Đây là phạm vi đề xuất, không phải điều kiện đủ cho mọi mô hình.

| Nguồn/chủ dữ liệu dự kiến | Đơn vị mỗi dòng | Trường cần có | Mục đích |
|---|---|---|---|
| POS / vận hành bán hàng | Một dòng hóa đơn; khóa store_id + receipt_id + line_id hoặc ID toàn cục | Thời gian, SKU, số lượng, đơn vị, giá trước/sau giảm, tiền giảm, thuế, tiền dòng, trạng thái, tham chiếu hoàn/hủy, customer_id nếu có | Nền tảng doanh thu và giỏ hàng |
| ERP / quản lý ngành hàng | Một SKU hoặc một phiên bản SKU theo thời gian | Mã SKU/barcode, tên, phân cấp ngành, quy cách, đơn vị và hệ số quy đổi, ngày hiệu lực, NCC | Nối hệ thống và chuẩn hóa đơn vị |
| Vận hành chuỗi | Một cửa hàng và thời gian hiệu lực | Mã cửa hàng, khu vực, loại, mở/đóng, lịch hoạt động | Tránh coi ngày đóng cửa là mất nhu cầu |
| WMS / kho | SKU–địa điểm–ngày và từng giao dịch kho | Tồn đầu/cuối, nhập, bán, chuyển, hủy, điều chỉnh, lô/hạn dùng nếu có | Tồn kho và rủi ro hết hàng |
| Mua hàng / NCC | Dòng đơn mua và dòng nhận hàng | PO, SKU, cửa hàng/kho, ngày đặt/hứa/nhận, lượng đặt/nhận, MOQ, lead time | Bổ sung hàng và hiệu suất NCC |
| Marketing / pricing | Chương trình–SKU–cửa hàng–thời gian | ID chương trình, giá hiệu lực, cơ chế giảm, nhóm được nhận, chi phí, tài trợ, phân nhóm thử nghiệm | Đo khuyến mãi, tránh nối chồng chương trình |
| CRM / loyalty | Một khách ẩn danh; thêm nhật ký tương tác riêng | Mã bền vững xuyên kênh, ngày gia nhập, phân nhóm, lịch gửi/nhận/đổi ưu đãi | RFM, cohort, đo phản hồi; không cần tên/SĐT cho PoC |
| Kế toán | SKU–ngày hiệu lực và tổng đối soát ngày/cửa hàng | Giá vốn, thuế, hoàn, chi phí, doanh thu chốt kỳ; định nghĩa và thời điểm ghi nhận | Xác minh doanh thu/lợi nhuận |

Cho mỗi nguồn, cần hỏi: ai sở hữu, nằm ở hệ thống nào, xuất dạng gì, có bao nhiêu lịch sử, tần suất cập nhật, độ trễ, múi giờ, định nghĩa ngày kinh doanh, và khóa nào nối được. Đề nghị cung cấp data dictionary, 20–100 dòng mẫu có ẩn danh và tổng đối soát cùng kỳ.

Quy trình SILO: (1) lập bản đồ nguồn và chủ sở hữu; (2) chốt grain/khóa và định nghĩa tiền/thuế/hoàn; (3) lập bảng ánh xạ SKU, cửa hàng, khách xuyên hệ thống có ngày hiệu lực; (4) giữ raw bất biến, chuẩn hóa riêng; (5) nối có kiểm tra cardinality và tỷ lệ không khớp; (6) đối soát POS–kho–kế toán theo ngày/cửa hàng, ghi nguyên nhân sai lệch; (7) chỉ đưa bảng đã kiểm chứng vào báo cáo/mô hình. Không xem bán bằng 0 là nhu cầu bằng 0 khi thiếu dữ liệu tồn kho.

## 6. Kế hoạch một tuần làm việc

1. Ngày 1: chốt câu hỏi kinh doanh, chọn Complete Journey làm demo chính, đọc từ điển dữ liệu và lưu nguồn. Việc tải/kiểm tra ban đầu đã hoàn thành trong lần khảo sát này.
2. Ngày 2: rà ngoại lệ, định nghĩa KPI và đối soát bảng nối; dựng báo cáo doanh thu/ngành hàng.
3. Ngày 3: mở rộng giỏ hàng xuống SKU hoặc phân nhóm RFM, xác minh tính ổn định trên thời kỳ sau.
4. Ngày 4: thử dự báo theo nhóm hàng, so với baseline trên nhiều mốc; không dùng random split cho chuỗi thời gian.
5. Ngày 5: tổng hợp demo, chọn 2–3 PoC, lập bảng dữ liệu còn thiếu và buổi trao đổi với doanh nghiệp.

Đề xuất mang đi trao đổi trước: (a) hợp nhất và đối soát doanh thu; (b) phân tích khách hàng/giỏ hàng; (c) dự báo bán khi đủ lịch sử và bối cảnh khuyến mãi. Tồn kho, giá và lợi nhuận được mở rộng theo dữ liệu thực có.

## 7. Tệp và cách chạy lại

- `research/download_data.py`: tải file và lưu manifest; `research/analyze.py`: tạo toàn bộ kết quả khám phá.
- `outputs/profile.json`: kiểm tra chất lượng và chỉ tiêu tổng; CSV: doanh số tháng, ngành hàng, cặp ngành, RFM, baseline tuần và bảng tham chiếu đã chuyển từ R.
- `outputs/overview.png`: biểu đồ mô tả panel. Các CSV là kết quả tĩnh, chạy lại script để cập nhật.
- Môi trường đã dùng: Python bundled của Codex với pandas, numpy, matplotlib, openpyxl (chỉ đọc); pyreadr 0.5.9 cài riêng trong `research/vendor` để đọc định dạng R. Chạy hai script từ thư mục dự án bằng cùng interpreter.

Nguồn định nghĩa sales_value, discount và cấu trúc bảng: [Complete Journey User Guide](https://bradleyboehmke.github.io/completejourney/articles/completejourney.html). Nguồn file: [repository của người duy trì package](https://github.com/bradleyboehmke/completejourney). Bản public dùng để thử phương pháp; mô hình và ngưỡng cảnh báo phải được đánh giá lại trên dữ liệu doanh nghiệp Việt Nam.
