# Áp dụng cho chuỗi siêu thị và cửa hàng bán lẻ

Phạm vi doanh nghiệp đã xác nhận: chuỗi siêu thị/cửa hàng bán lẻ. Tài liệu này bổ sung RUNBOOK và báo cáo mô hình hiện tại.

## Chọn PoC đầu tiên

Ưu tiên hợp nhất và đối soát doanh thu toàn chuỗi, sau đó thử dự báo bán theo cửa hàng–SKU và chăm sóc khách hàng xuyên cửa hàng. Dữ liệu public hiện chỉ phản ánh panel hộ mua hàng; không có doanh thu đầy đủ hay tồn kho từng cửa hàng. Giữ kết quả public làm demo phương pháp, không lấy dự báo nhóm hàng toàn panel để phát lệnh đặt hàng.

Đề xuất thí điểm 5–10 cửa hàng có quy mô, khu vực và cơ cấu ngành khác nhau, với một nhóm hàng có dữ liệu tốt. Đây là phạm vi ban đầu để thống nhất với doanh nghiệp, chưa phải số cửa hàng được khảo sát thực tế. Chọn mục tiêu trước khi xem kết quả: giảm thời gian đối soát, cải thiện forecast so với cách lập kế hoạch hiện tại hoặc tăng retention qua thử nghiệm có đối chứng.

## Mô hình dữ liệu cần có

| Bảng | Grain / khóa | Yêu cầu riêng cho chuỗi |
|---|---|---|
| POS | source_system + store_id + business_date + receipt_id + line_id | Không trùng hóa đơn giữa cửa hàng; giữ hoàn/hủy và hóa đơn gốc; định nghĩa tiền, thuế, discount thống nhất |
| Danh mục SKU | canonical_sku + thời gian hiệu lực | Mapping mã nội bộ/barcode giữa POS–ERP–WMS; đơn vị và quy cách; phân cấp ngành hàng, nhãn riêng |
| Cửa hàng | store_id + thời gian hiệu lực | Khu vực, format, diện tích nếu có, ngày mở/đóng, lịch hoạt động; đánh dấu cửa hàng mới và tạm đóng |
| Danh mục được kinh doanh | store_id + sku + khoảng hiệu lực | Phân biệt SKU không được bán, chưa lên kệ, hết hàng và có hàng nhưng không bán được |
| Giá và khuyến mãi | store_id + sku + khoảng hiệu lực + promotion_id | Phân biệt giá toàn chuỗi/khu vực/cửa hàng; xác định ưu đãi chồng nhau; chỉ dùng thông tin đã biết tại thời điểm dự báo |
| Tồn kho | location_id + sku + business_date; thêm lot_id nếu cần | Tồn kho cửa hàng/kho trung tâm, lượng khả dụng, đặt trước, kiểm kê, hủy và điều chỉnh |
| Điều chuyển | transfer_id + line_id + sự kiện | Nối xuất nơi gửi–đang vận chuyển–nhận nơi đến; không tính điều chuyển là bán hàng |
| Mua hàng và nhận hàng | PO + line_id + lần nhận | Lead time theo NCC–điểm nhận, nhận từng phần, MOQ, case pack, lịch giao |
| Khách hàng | customer_id ẩn danh toàn chuỗi | Mapping loyalty/xuyên kênh; khách chuyển mua sang cửa hàng khác không tự động bị gắn là rời bỏ chuỗi |
| Giá vốn / đối soát | sku + thời gian hiệu lực; ngày–cửa hàng | Tách doanh thu, lãi gộp, chi phí và tài trợ khuyến mãi; thống nhất thời điểm ghi nhận |

## Các đầu ra theo cấp quản lý

| Người dùng | Câu hỏi | Đầu ra và giới hạn |
|---|---|---|
| Ban điều hành | Chuỗi tăng trưởng ở đâu và do yếu tố nào? | Tổng chuỗi → khu vực → format → cửa hàng → ngành; phân rã số giỏ và giá trị giỏ; so cùng cửa hàng đủ kỳ để tránh tăng trưởng chỉ do mở mới |
| Quản lý vùng / cửa hàng | Điểm nào cần xử lý hôm nay? | Cờ thiếu nguồn, doanh số khác thường, hết hàng và hủy hàng khi có dữ liệu; so nhóm cửa hàng tương đồng và cùng lịch hoạt động |
| Ngành hàng / cung ứng | SKU nào cần bổ sung, giảm hoặc điều chuyển? | Forecast cửa hàng–SKU, bias, mức tồn và lead time; chỉ đưa khuyến nghị đặt/điều chuyển khi đủ ràng buộc |
| CRM | Khách giảm mua ở một cửa hàng hay trên toàn chuỗi? | RFM và nguy cơ không mua ở cấp chuỗi, thêm cửa hàng thường mua; kiểm tra chuyển kênh/cửa hàng trước khi can thiệp |
| Marketing | Chương trình có tăng lãi hay chỉ chuyển doanh số? | Thử nghiệm theo cửa hàng/cụm phù hợp; theo dõi thay thế giữa SKU, mua sớm rồi giảm mua sau khuyến mãi, dịch chuyển giữa cửa hàng |

Không xếp hạng hiệu suất cửa hàng chỉ bằng doanh thu tuyệt đối. Cần xét format, quy mô, số ngày mở, thời gian hoạt động, tập SKU và độ phủ nguồn. Same-store sales phải chốt danh sách cửa hàng đủ kỳ trước khi tính và công bố định nghĩa.

## Điều chỉnh mô hình khi có dữ liệu doanh nghiệp

1. Dựng lịch ngày–cửa hàng–SKU từ ngày mở cửa và danh mục kinh doanh. Không điền 0 cho mọi tổ hợp vắng; xác định thiếu nguồn, đóng cửa, không kinh doanh và hết hàng riêng.
2. Dự báo 7/14 ngày ở cấp cửa hàng–SKU hoặc cấp ngành trước nếu SKU quá thưa. So mô hình dùng chung toàn chuỗi với baseline từng chuỗi con; chỉ dùng đặc trưng và lịch khuyến mãi đã biết trước origin.
3. Backtest theo thời gian, kèm kiểm tra cửa hàng/SKU mới. Báo MAE, WAPE và bias theo cửa hàng, ngành, nhóm bán chậm và đợt khuyến mãi; chỉ tiêu tổng không được che nhóm nhỏ có sai số lớn.
4. Khi cần forecast nhiều cấp, thống nhất cách tổng hợp hoặc reconciliation giữa SKU–cửa hàng–khu vực–chuỗi và kiểm tra tổng khớp. Pipeline public hiện chưa triển khai mô hình phân cấp này.
5. Chuyển dự báo bán thành bổ sung hàng bằng tồn khả dụng, hàng đang về, lead time, MOQ, case pack, hạn dùng và mục tiêu service level. Doanh số bị giới hạn bởi hết hàng không đại diện nhu cầu tiềm ẩn.
6. Refit mô hình CRM bằng giao dịch toàn chuỗi và kiểm tra khả năng khách chuyển cửa hàng. Mô hình nguy cơ không mua không dự báo khách nào sẽ phản hồi ưu đãi; hiệu quả cần đo bằng đối chứng.

## Tự động hóa và kiểm soát

Giữ pipeline hiện tại làm khung chạy, thêm adapter từng nguồn và bảng kiểm soát batch theo source_system–store_id–business_date. Mỗi batch có watermark, số dòng, tổng tiền, thời gian chốt và trạng thái. Cửa hàng gửi muộn phải được đánh dấu, không âm thầm coi là bán bằng 0. Khi backfill, cập nhật partition và báo cáo liên quan, giữ lịch sử phiên bản.

Sau chốt ngày: nhận POS/ERP/WMS → kiểm tra và đối soát theo cửa hàng → cập nhật mart → score bằng model được phê duyệt → xuất dashboard/danh sách hành động. Khi đủ nhãn mới: đánh giá forecast/risk đã phát hành, kiểm tra bias và drift, rồi xem xét train lại. Phân quyền theo vùng/cửa hàng và lưu người duyệt trước mọi hành động đổi giá, đặt hàng hoặc gửi ưu đãi.

## Tiêu chí nghiệm thu PoC cần thống nhất

- Chênh lệch đối soát theo ngày/cửa hàng có ngưỡng được kế toán duyệt và nguyên nhân được giải thích; không tự đặt mức chấp nhận từ dữ liệu public.
- Forecast vượt baseline doanh nghiệp trên test giữ riêng và không gây bias nghiêm trọng ở nhóm hàng ưu tiên; công bố độ phủ dữ liệu và trường hợp chưa score được.
- CRM/combo/khuyến mãi đánh giá tăng thêm bằng thử nghiệm, với chi phí và lợi nhuận khi đủ dữ liệu; không dùng lift offline thay ROI.
- Lỗi nguồn bị chặn hoặc hiển thị rõ; score/báo cáo tốt gần nhất còn truy cập được; có người sở hữu cảnh báo và cách khôi phục.

Chưa kết nối doanh nghiệp, chưa đo ROI, chưa triển khai đặt hàng hay lập lịch nhận POS tự động. Các phần này cần dữ liệu và quyết định vận hành thực tế của chuỗi.
