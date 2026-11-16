# Hai không gian điều hành

Dashboard có đúng hai vai trò trình diễn: **Ban điều hành cấp cao** và **Điều hành vận hành**. Chuyển vai trò thay đổi trang chủ, menu và nội dung ưu tiên; chưa tạo hai tài khoản xác thực hoặc phân quyền bảo mật riêng.

## 1. Ban điều hành cấp cao

- **Toàn cảnh chiến lược:** bản tin điều hành, KPI theo phạm vi, mức tập trung ngành/khách hàng và bản đồ các chỉ tiêu tài chính đã có/chưa có.
- **Động lực tăng trưởng:** cầu nối số giỏ–AOV, xu hướng, cơ cấu ngành và cây câu hỏi để điều tra price–volume–mix. Chưa tách được giá, lượng, mix hoàn chỉnh nếu thiếu dữ liệu chuẩn hóa.
- **Hiệu quả & vốn lưu động:** mô phỏng biên gộp, biến phí, định phí, mức thay đổi bán và độ nhạy vốn tồn. Tất cả tỷ lệ chi phí và thay đổi số ngày tồn là giả định.
- **Rủi ro & quyết định:** bằng chứng, quyết định đề xuất, đầu mối đề xuất và cổng kiểm soát trước cấp ngân sách/mở rộng pilot.
- **Báo cáo & trợ lý:** tải báo cáo Word lịch sử và giải thích theo quy tắc. Chưa kết nối LLM.

## 2. Điều hành vận hành

Trang chủ ưu tiên nơi cần rà soát và bước tiếp theo. Bàn công việc cho nhập owner, hạn, trạng thái, ghi chú; có tiêu chí hoàn tất và xuất CSV. Các trang cửa hàng, danh mục, khách hàng, giỏ hàng, kế hoạch bán, danh sách rủi ro, bổ sung hàng và tra cứu dùng cho kiểm tra chi tiết. AI được trình bày như công cụ hỗ trợ công việc; không có người dùng hoặc menu Data & AI riêng.

Owner, hạn và trạng thái chỉ lưu trên trình duyệt, chưa đồng bộ hoặc thông báo cho doanh nghiệp. Đánh dấu hoàn tất không xác nhận đã có hiệu quả tài chính.

## 3. Đọc đúng so sánh kỳ

Mặc định mở tháng 12/2017. Nếu chọn trọn tháng/quý/năm, kỳ trước là cùng số tháng lịch liền trước. Ví dụ tháng 12 so với tháng 11, không lấy thêm 31/10 để bù 31 ngày. Nếu chọn khoảng tùy chỉnh không trọn kỳ lịch, so với khoảng liền trước cùng số ngày. Thiếu lịch sử thì không tính tăng trưởng.

Số tiền bán quan sát tháng 12: **421.882,29 USD**; tháng 11: **385.552,25 USD**; thay đổi **36.330,04 USD, khoảng 9,42%**. Phân rã đối xứng chia đều tương tác số giỏ và AOV, không diễn giải đóng góp AOV là tăng giá. Hai tháng khác độ dài; chưa điều chỉnh mùa vụ hoặc độ phủ panel.

## 4. Tài chính: giả định, công thức và giới hạn

- Lãi đóng góp mô phỏng = bán mô phỏng × (biên gộp − tỷ lệ biến phí).
- Kết quả mô phỏng sau định phí = lãi đóng góp − định phí cùng kỳ. Không gọi là EBITDA, EBIT hay lợi nhuận thực tế.
- Mức bán hòa vốn = định phí / tỷ lệ đóng góp, chỉ có nghiệm hữu ích khi tỷ lệ đóng góp dương.
- Để giữ kết quả nền khi định phí không đổi: hệ số bán mới = tỷ lệ đóng góp nền / tỷ lệ đóng góp mới. Đây không phải dự báo nhu cầu có thể đạt được.
- Độ nhạy vốn tồn = COGS/ngày giả định × số ngày tồn giảm giả định. Không khẳng định đã giải phóng cash flow; cần kiểm soát mức phục vụ, công nợ và lịch thanh toán.
- CCC = DIO + DSO − DPO. GMROI = lãi gộp / tồn bình quân theo giá vốn, cùng kỳ và cơ sở đo. Chưa có actual các chỉ tiêu này.

Đối soát VAT, hoàn/hủy, ghi nhận doanh thu, cost có ngày hiệu lực và chính sách phân bổ trước khi dựng P&L. Định phí phải tương thích kỳ và phạm vi chọn; giá trị mặc định không là benchmark ngành. Tham khảo IAS 2 và IAS 7 được liên kết trong dashboard; mô phỏng không là báo cáo tuân thủ chuẩn mực.

## 5. Dữ liệu và AI

Giữ toàn bộ 1.468.773 dòng trong kỳ 2017, tổng raw sales_value 4.594.146,32 USD. Complete Journey là household panel, không là doanh số toàn bộ chuỗi hoặc dữ liệu cửa hàng Việt Nam. 534 dòng đầu 2018 ngoài kỳ; giao dịch không dương giữ raw và tách khỏi model mua dương. Ngày 25/12 vắng bản ghi, chưa chứng minh không có nhu cầu.

AI đã train trong pipeline Python; dashboard đọc evaluation và score, không train lại theo bộ lọc. Model dùng cửa sổ lịch sử cố định. Chưa có COGS/OPEX, tồn, công nợ, đầy đủ POS hoặc đối chứng campaign để tính lợi nhuận, ROIC, CCC, same-store sales hay ROI thực tế. Tồn kho vẫn là sandbox.

## 6. Kịch bản trình diễn cho doanh nghiệp

1. Mở Ban điều hành cấp cao, tháng 12; giải thích kết quả và giới hạn panel.
2. Mở Động lực tăng trưởng, chỉ cầu nối tháng 11 → tháng 12 và câu hỏi về mix.
3. Mở Hiệu quả & vốn lưu động, giảm biên một điểm %, kiểm tra mức tăng bán cần có để giữ kết quả nền.
4. Mở hồ sơ quyết định, chọn một pilot cùng cổng đo lường và điều kiện dừng.
5. Chuyển Điều hành vận hành, mở bàn công việc, ghi owner/hạn và bằng chứng dự kiến.
6. Đi sâu tới cửa hàng/SKU/khách hàng và xuất bảng; phân biệt quan sát, dự báo và giả định.

Mở `dist/index.html` bằng Edge/Chrome hoặc dùng bản hosted. HTML tự chứa dữ liệu và biểu đồ, chạy offline. Build từ workspace đầy đủ bằng `python build_data.py`, rồi `python build_html.py`; script nhúng `src/business.js` vào cùng phạm vi app. Không đóng gói dữ liệu nhạy cảm của doanh nghiệp theo cách offline này nếu chưa có thiết kế bảo mật phù hợp.


## Dữ liệu mới và Probit

Bản hiện tại bổ sung cùng một không gian nạp dữ liệu ở cả hai vai trò. Có snapshot 90 ngày hoặc append cùng hệ mã, 5 model Probit đã train và xuất xác suất/audit. Xem `Huong_dan_upload_va_Probit.md` trong ZIP để biết schema, phạm vi, kiểm tra và chạy batch Python. Hai không gian giữ riêng dữ liệu nền 2017 và kết quả upload; không tự ghi đè báo cáo cũ.
