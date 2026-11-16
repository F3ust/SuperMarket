# Đánh giá dashboard bán lẻ

Ngày tổng hợp 02 tháng 11 năm 2026. Đối tượng sử dụng là người phụ trách dự án, DA, DE và đại diện tài chính vận hành. Báo cáo đối chiếu tài liệu công khai với dashboard Retail Intelligence trong workspace, nhằm xác định thứ tự nâng cấp và bằng chứng nghiệm thu.

Kết luận của tôi là ưu tiên tiếp theo nên tập trung vào định nghĩa chỉ tiêu có người chịu trách nhiệm, đối soát với nguồn doanh nghiệp, lưu trữ bền vững và đo hiệu quả quyết định. Dashboard đã có phân tích và suy luận model thật, nhưng chưa có đủ bằng chứng để gọi là hệ thống vận hành doanh nghiệp đã được kiểm chứng. Những đề xuất trong báo cáo là đánh giá áp dụng cho dự án này, không phải một chứng chỉ hoặc điểm chuẩn do các nguồn bên ngoài cấp.

Phạm vi nghiên cứu gồm tài liệu chính thức, bài viết của đội kỹ thuật, trang tác giả và nhà xuất bản. Với sách thương mại, tôi đối chiếu phần giới thiệu, mục lục và tài liệu mở; không coi đó là đã đọc toàn bộ nội dung trả phí. Không dùng danh tiếng của một công ty để suy ra rằng dự án nhỏ phải sao chép toàn bộ công nghệ của họ.

## 1 Tiêu chuẩn đánh giá một sản phẩm dữ liệu tốt

Theo tài liệu Tableau, mục đích và người đọc phải dẫn dắt thiết kế. Sách Dashboards That Deliver mô tả cả quá trình khám phá nhu cầu, prototype, kiểm thử người dùng, phát hành và bảo trì. Từ đó, tôi đề xuất xem dashboard này như một sản phẩm phục vụ các quyết định lặp lại, có chủ sở hữu và được đánh giá sau khi dùng. [S01] [S02]

Một tiêu chuẩn nghiệm thu phù hợp là người dùng biết số liệu thuộc kỳ nào, khác điều gì so với kế hoạch hoặc kỳ trước, nguyên nhân nào có bằng chứng, ai cần hành động và khi nào sẽ kiểm tra kết quả. Nếu chưa có dữ liệu để trả lời, màn hình cần ghi rõ thiếu gì và ai chịu trách nhiệm bổ sung. Đề xuất này không có nghĩa mọi màn hình phải chứa tất cả thông tin cùng lúc.

Tôi đề xuất bốn mức trưởng thành để quản lý dự án: demo phân tích có thể tái tạo; pilot với dữ liệu doanh nghiệp được đối soát; vận hành ổn định có phân quyền và phục hồi; sản phẩm có bằng chứng cải thiện quyết định hoặc kết quả. Đây là thang mô tả do tôi đề xuất, không phải thang điểm của NIST hay Tableau. Hiện tại, dự án có nhiều năng lực của mức demo và một số thành phần có thể dùng để bắt đầu pilot, nhưng chưa đáp ứng đầy đủ mức vận hành.

## 2 Những tài liệu đáng đọc và cách áp dụng

Sách **Dashboards That Deliver**, của Steve Wexler, Jeffrey Shaffer, Andy Cotgreave và Amanda Makulec, phù hợp nhất với giai đoạn hiện tại. Trang sách nêu quy trình từ discovery đến maintenance và các tình huống thực tế. Đầu ra tôi đề xuất sau khi đọc là bộ câu hỏi phỏng vấn và biên bản thống nhất phạm vi cho hai vai trò đang có. [S01]

**Storytelling with Data**, của Cole Nussbaumer Knaflic, giúp rà lại ngữ cảnh, lựa chọn biểu đồ, giảm chi tiết gây nhiễu và hướng sự chú ý. Áp dụng vào bài này bằng tiêu đề nêu phát hiện có căn cứ và chú thích kỳ so sánh; mỗi phát hiện phải phân biệt quan sát, giả thuyết và khuyến nghị. [S03]

**Information Dashboard Design**, của Stephen Few, tập trung vào theo dõi thông tin rõ ràng ở mức nhìn nhanh. **The Big Book of Dashboards**, của Wexler, Shaffer và Cotgreave, cung cấp các ví dụ theo tình huống kinh doanh. Tôi đề xuất dùng hai sách để so sánh cách tổ chức trang cấp cao và trang vận hành, không sao chép hình thức một mẫu chỉ vì đẹp. [S04] [S05]

**Fundamentals of Data Engineering**, của Joe Reis và Matt Housley, đặt công việc DE trong vòng đời sinh dữ liệu, ingest, lưu trữ, biến đổi và phục vụ người dùng. Áp dụng ở đây là thiết kế đường đi của một batch mới, quyền truy cập và cách phục hồi trước khi chọn thêm công cụ. [S06]

Kimball Group trình bày bốn quyết định nền tảng khi thiết kế dimensional model: quy trình kinh doanh, grain, dimensions và facts. Bài này cần bắt đầu từ grain của dòng bán, giỏ, tồn cuối ngày và quyết định CRM; không gộp tất cả vào một bảng phẳng có nhiều phép nối không kiểm soát. [S07]

## 3 Một DA và DE chuyên nghiệp thực hiện những việc gì

DA cần dẫn dắt câu hỏi kinh doanh, định nghĩa và kiểm chứng chỉ tiêu, phân tích các cách giải thích cạnh tranh, thiết kế cách đọc và kiểm thử với người dùng. DE cần làm rõ nguồn, khóa, grain, tính đầy đủ, lịch xử lý và khả năng tái tạo. Cả hai cùng kiểm tra đối soát và thống nhất điều kiện để công bố dữ liệu. Phân chia này là đề xuất cho dự án; doanh nghiệp nhỏ có thể để một người đảm nhiệm nhiều phần.

Đại diện tài chính cần xác nhận ngữ nghĩa doanh thu, giá vốn, kỳ đóng sổ và nguyên tắc phân bổ. Vận hành xác nhận khả năng thực thi hành động, thời gian đáp ứng và tiêu chí hoàn tất. Người quản lý sản phẩm hoặc sponsor quyết định phạm vi, ưu tiên và nguồn lực. Hai vai trò người dùng cuối vẫn giữ nguyên; các trách nhiệm hậu trường không tạo thêm một người dùng Data và AI trên giao diện.

Trước khi thêm một biểu đồ, DA nên lập một bản ghi quyết định với các trường: người quyết định; câu hỏi; nhịp xem; lựa chọn hành động; chi phí của quyết định sai; chỉ tiêu nền và guardrail; dữ liệu cần có; người xác nhận; thời điểm đánh giá lại. Ví dụ, với CRM, câu hỏi hữu ích là nhóm nào nên được đưa vào thử nghiệm giữ chân và ở công suất nào, chứ chưa phải tất cả khách có risk cao cần được giảm giá.

Trước khi nối một nguồn mới, DE nên chốt data contract: ai sở hữu nguồn; một dòng nghĩa là gì; khóa ổn định; ngày nghiệp vụ và timezone; đơn vị tiền và số lượng; nguồn sửa hồi tố thế nào; khoảng dữ liệu được coi là đủ; quyền sử dụng; phiên bản schema. Quy tắc này cần được kiểm thử bằng một batch lỗi và một batch gửi lại.

## 4 Chốt chỉ tiêu và mô hình dữ liệu trước khi mở rộng

Semantic layer của dbt minh họa cách tập trung định nghĩa metric để các nơi tiêu thụ dùng cùng logic. Điều cần học là quản lý định nghĩa chung; không bắt buộc mua hoặc triển khai dbt Semantic Layer cho prototype này. Có thể bắt đầu bằng metric catalog, SQL views và kiểm thử phiên bản hóa. [S08]

Mỗi metric nên có mã, tên dễ hiểu, câu hỏi kinh doanh, numerator, denominator, bộ lọc, grain, ngày áp dụng, đơn vị, nguồn, người phê duyệt và test đối soát. Khi định nghĩa đổi, cần biết báo cáo quá khứ được restate theo định nghĩa mới hay giữ nguyên như lúc phát hành. Hai cách đều cần có chủ đích và được ghi nhận.

Ví dụ, AOV phải tính từ tổng tiền và số giỏ cùng phạm vi; không lấy trung bình AOV các cửa hàng mà bỏ trọng số. Không cộng số giỏ distinct giữa các ngành để ra tổng vì một giỏ có thể có nhiều ngành. Với driver tree, nếu dùng hộ mua dương thì các thành phần giỏ và số tiền cũng phải cùng nhánh mua dương. Tổng tiền raw cần giữ phép đối soát riêng với ngoại lệ.

Đề xuất các fact riêng cho dòng giao dịch, tồn theo SKU cửa hàng ngày, nhận hàng hoặc đơn mua, assignment campaign, score tại as-of và hành động được ghi nhận. Dimensions dùng để diễn giải sản phẩm, cửa hàng, khách và lịch. Giá vốn và taxonomy cần khoảng ngày hiệu lực để tránh nối giá trị hiện tại vào toàn bộ quá khứ. Đây là thiết kế đề xuất, chưa phải các bảng production đã tồn tại.

Đối với tài chính, dữ liệu hiện tại chỉ hỗ trợ số tiền bán quan sát trong household panel. Muốn có lãi gộp cần cơ sở giá vốn được xác nhận; muốn có dòng tiền cần dữ liệu thu chi và công nợ. IAS 2 và IAS 7 là nguồn tham chiếu về hai miền thông tin này; báo cáo không kết luận doanh nghiệp mục tiêu phải áp dụng IFRS. [S16] [S17]

## 5 Kiến trúc tối thiểu để dùng với dữ liệu doanh nghiệp

Kiến trúc đề xuất là nguồn POS ERP CRM đi vào raw được giữ phiên bản, qua schema và quality gate, tới fact dimension và chỉ tiêu đã xác nhận; từ đó phục vụ dashboard và feature model. Quyết định được ghi vào một sổ hành động, rồi kết quả thực tế quay lại để đánh giá. Chưa có đề xuất tự động chi ngân sách hoặc đặt hàng chỉ bằng score.

Với pilot, nên ưu tiên một kho file riêng tư, một database cho metadata và trạng thái, một worker chạy job và một API phục vụ giao diện. Lựa chọn cụ thể cần dựa trên khối lượng, tần suất, nhân lực và chi phí. Tài liệu vòng đời DE hỗ trợ tư duy này; quy mô Uber chỉ cung cấp bài học vận hành, không là lý do để mặc định đưa Kafka hoặc Spark vào hệ thống nhỏ. [S06] [S09]

Luồng upload production nên lưu checksum byte gốc, schema version, đơn vị, khoảng bao phủ, mapping và người nạp. Job chỉ chuyển watermark khi raw, mart hoặc score của lần chạy đã được commit thành công. Mỗi lần công bố cần truy được từ KPI tới batch, code và model version. Trạng thái job, watermark và kết quả phải còn sau khi restart worker hoặc người dùng đóng tab.

Airflow khuyến nghị task có kết quả nhất quán khi retry và không để lại kết quả dở dang; tài liệu cũng nêu rủi ro duplicate khi INSERT lại và việc đọc dữ liệu không cố định theo partition. Áp dụng ở đây là idempotency, input version cố định, commit có kiểm soát và kiểm thử crash recovery. Đây là nguyên tắc thiết kế, không phải yêu cầu phải cài Airflow. [S10]

Hai giao diện cấp cao và vận hành cần được gắn với danh tính và quyền phía server khi dùng dữ liệu thật. Kiểm tra quyền phải áp dụng cả API, truy vấn và export. Bản HTML hiện nhúng toàn bộ dữ liệu công khai là cách bàn giao demo thuận tiện; cách này chưa chứng minh được quyền xem theo cửa hàng hoặc theo từng người dùng doanh nghiệp.

## 6 Chất lượng dữ liệu phải có quy trình xử lý sự cố

Uber mô tả các nhóm kiểm tra như freshness, completeness, duplicate và consistency, cùng quy trình onboarding, cảnh báo và xử lý. Bài học tôi áp dụng là mỗi rule cần có mức ảnh hưởng, người xử lý và hành động sau lỗi; thêm nhiều test nhưng không có owner vẫn chưa tạo được khả năng vận hành. [S09]

Nhóm kiểm tra cần có ở bài bán lẻ này gồm schema và kiểu; uniqueness của khóa; cardinality trước và sau join; raw so với positive và ngoại lệ; kiểm tra tổng tiền với control total từ nguồn; lịch mở cửa và heartbeat; UOM và currency; late arrival hoặc correction. Tổng tiền tự khớp trong cùng một file chưa chứng minh file đó khớp POS hoặc sổ đối soát bên ngoài.

Ngày không có bản ghi cần được phân biệt với ngày đã xác nhận không phát sinh giao dịch. Cảnh báo nguồn trễ chỉ có ý nghĩa nếu biết lịch giao dữ liệu và phần dữ liệu nào đã chốt. Với file lịch sử 2017, không dùng khoảng cách tới ngày hiện tại để tự kết luận pipeline live bị trễ.

Đề xuất một bảng incident gồm rule, batch bị ảnh hưởng, mức chênh lệch, chỉ tiêu bị ảnh hưởng, owner, thời hạn phản hồi, nguyên nhân, bản sửa và bằng chứng đóng sự cố. Cần thử cả tình huống nguồn bị nhân dòng sau join và nguồn sửa giá vốn của một kỳ đã công bố.

## 7 Thiết kế hai không gian theo công việc thực tế

Với ban điều hành cấp cao, tôi đề xuất một trang tổng quan ngắn gồm kết quả so với kế hoạch khi có kế hoạch thật, cầu nối thay đổi, rủi ro trọng yếu và các quyết định đang chờ. Phần chi tiết mở khi cần. Đây là cách áp dụng nguyên tắc mục đích và người đọc của Tableau, cùng tư duy theo dõi nhanh của Few. [S02] [S04]

Với điều hành vận hành, trang chủ nên là hàng chờ các việc có thể xử lý: đối tượng nào, ngoại lệ gì, bằng chứng nào, ai phụ trách, hạn nào, trạng thái nào và cách đo kết quả. Khi chưa có owner hoặc deadline thật, phải giữ nhãn đề xuất. Nút chuyển việc cần đi tới record bền vững, không chỉ đổi trạng thái local.

Mỗi KPI nên có kỳ, đơn vị, ngữ nghĩa numerator denominator, baseline và trạng thái dữ liệu. Tiêu đề nêu phát hiện chỉ dùng khi bộ lọc hiện tại thực sự hỗ trợ phát hiện đó. Hình thức biểu đồ nên theo câu hỏi: line cho diễn biến, bar cho so sánh, waterfall cho cầu nối có đồng nhất thức và phân phối cho xác suất. Các tác phẩm của Knaflic và ví dụ theo tình huống trong Big Book là nguồn phù hợp để thực hành lựa chọn này. [S03] [S05]

WCAG 2.2 yêu cầu contrast tối thiểu 4,5:1 cho chữ thông thường ở mức AA, có ngoại lệ được quy định; chữ lớn có ngưỡng khác. Kiểm tra tính toán trên một số cặp màu CSS hiện tại cho thấy #74817c trên trắng khoảng 4,06:1, #8e9b88 khoảng 2,92:1 và #93a08d khoảng 2,74:1. Đây là bằng chứng cần kiểm tra computed styles và chức năng thực tế của từng phần tử, chưa phải kết luận audit toàn site. [S11]

Ngoài contrast, cần kiểm tra keyboard, focus, mô tả biểu đồ, zoom, bảng thay thế cho biểu đồ và tín hiệu ngoài màu sắc. Một lần xem screenshot mobile chưa thay thế kiểm thử người dùng. Tôi đề xuất cho đại diện mỗi vai trò làm các nhiệm vụ cụ thể, ghi thời gian, số lỗi hiểu và nơi phải hỏi người giải thích; các ngưỡng nghiệm thu phải được chốt với nhóm dự án.

## 8 Đưa Probit vào quy trình kiểm chứng xác suất

Đầu ra liên tục chưa đủ để xác nhận xác suất đúng. Tài liệu scikit learn phân biệt calibration curve với Brier và log loss: các scoring rule này còn phản ánh khả năng phân biệt và độ bất định, nên Brier thấp hơn không tự chứng minh calibration tốt hơn. Áp dụng vào bộ Probit là đánh giá reliability theo nhóm xác suất cùng kích thước mẫu và kiểm tra ngoài thời gian. [S12]

Bộ hiện tại đã có kiểm tra temporal, model version, parity Python và JavaScript, tổng phân phối và suy luận không retrain. Phần còn thiếu cho doanh nghiệp mới là label table đã đủ thời gian quan sát, phân tích calibration theo cohort và giai đoạn, lựa chọn policy trên chi phí lợi ích thực tế, cùng điều kiện dừng hoặc rollback. Hai holdout 56 ngày đang overlap và các hộ có thể lặp, nên chưa là hai mẫu độc lập.

Một mức risk cao không xác định người nên được ưu đãi. Muốn ra quyết định CRM cần thêm giả thuyết can thiệp và đo giá trị tăng thêm. Từ kinh nghiệm experimentation của Microsoft, tôi đề xuất chốt outcome chính, guardrail và kiểm tra chất lượng randomization trước khi xem treatment thắng hay thua. [S13]

Với dữ liệu panel có nhiều hộ mua nhiều cửa hàng, thử nghiệm CRM nên cân nhắc phân nhóm theo hộ để giảm lẫn treatment giữa cửa hàng. Can thiệp trưng bày tại cửa hàng có thể cần thiết kế theo cụm hoặc theo thời gian; phải tính power và phụ thuộc dữ liệu phù hợp trước khi chọn. Đây là đề xuất thống kê cần xác nhận với dữ liệu thật, không là một thiết kế A/B đã chạy.

Google Research nêu một rubric gồm các yêu cầu kiểm thử và monitoring cho ML production. NIST đặt quản trị rủi ro trong các chức năng Govern Map Measure Manage. Đối với bài này, tôi đề xuất dùng chúng để xây checklist review và trách nhiệm sau phát hành, không dùng số lượng model hoặc tên thuật toán làm thước đo độ trưởng thành. [S14] [S15]

## 9 Đánh giá hiện trạng dựa trên artifact

Phần đã có bằng chứng gồm phân tích dữ liệu công khai toàn kỳ, đối soát tổng tiền trong bộ dữ liệu, phân biệt raw và mua dương, kiểm tra temporal, baseline thắng model phức tạp ở một số tác vụ, hai vai trò giao diện, upload suy luận thật, kiểm tra khóa và audit export. Báo cáo QA hiện tại ghi sai khác tối đa giữa hai runtime khoảng 1,38 × 10⁻⁷; đây là kiểm tra tính nhất quán tính toán, không phải hiệu quả kinh doanh.

Phần có một phần gồm metric definitions trong code và hướng dẫn, quality gate cho file, metadata model, action tracking và kiểm thử browser. Cần đưa các phần này thành quy trình được owner doanh nghiệp chấp nhận, trạng thái bền vững và tiêu chí phát hành rõ ràng. Nhãn vai trò trên giao diện chưa là phân quyền hai tài khoản thật.

Phần chưa có đủ bằng chứng gồm POS ERP CRM doanh nghiệp đã đối soát, giá vốn và OPEX thực tế, lịch nguồn tự động live, restore sau sự cố production, quyền xem và export theo danh tính, calibration trên khách doanh nghiệp mới và tác động tăng thêm của hành động. Phân tích hiện dùng household panel nên chưa xác nhận tăng trưởng hoặc hiệu suất toàn chuỗi.

Artifact HTML hiện khoảng 22,48 MiB và nhúng dữ liệu công khai để mở offline. Đây là quan sát kích thước file, không phải phép đo latency hoặc kết luận hệ thống chậm. Với production, tôi đề xuất tách giao diện khỏi dữ liệu đầy đủ, chỉ tải các tổng hợp cần thiết và đo p50 p95 trên dữ liệu, thiết bị và mạng đại diện trước khi quyết định tối ưu.

## 10 Thứ tự nâng cấp và điều kiện nghiệm thu

Ưu tiên P0 là các phần làm thay đổi tính đúng và khả năng giải thích: decision brief, metric catalog, grain, data contract, control totals, phân biệt missing với zero và các giới hạn của nguồn. Cần hoàn thành trước khi quảng bá số liệu như chỉ tiêu tài chính hoặc doanh thu toàn chuỗi.

Ưu tiên P1 là các phần đưa pilot vào vận hành: lưu batch và watermark bền vững, kiểm thử retry và crash recovery, API có quyền truy cập, sổ hành động, monitoring và label table. Các phần đòi hỏi nguồn doanh nghiệp hoặc hạ tầng cần được ghi là phụ thuộc bên ngoài, không thể giải quyết chỉ bằng thêm code HTML.

Ưu tiên P2 là đo giá trị và tinh chỉnh trải nghiệm: usability theo nhiệm vụ, accessibility, tối ưu latency đã đo, pilot CRM có đối chứng và đánh giá hiệu quả tài chính theo chính sách đã thống nhất. Không nên chờ làm xong mọi biểu đồ mới bắt đầu kiểm thử người dùng.

Một chu kỳ bốn tuần có thể dùng làm khung kế hoạch khi có đủ người và dữ liệu: tuần đầu chốt quyết định và định nghĩa; tuần hai đối soát và dựng nền trạng thái; tuần ba nối workflow và kiểm thử; tuần bốn UAT và thiết kế đánh giá tác động. Đây là trình tự đề xuất, không phải cam kết có thể triển khai production trong bốn tuần khi các phụ thuộc chưa được đáp ứng.

## 11 Bộ hồ sơ nên bàn giao

Bộ hồ sơ gồm decision brief theo vai trò, metric catalog có phiên bản, data contract và sơ đồ grain, báo cáo đối soát có ngoại lệ, lineage, model card và evaluation, runbook có khôi phục, test evidence, kết quả UAT, decision ledger và kế hoạch đo outcome. Mỗi tài liệu phải gắn với người chịu trách nhiệm và cách xác nhận, thay vì chỉ tồn tại để đủ danh mục.

Tôi đề xuất điều kiện hoàn thành pilot là một người khác có thể tái tạo chỉ tiêu, truy nguồn chênh lệch, chạy lại batch không nhân dữ liệu, nhận biết dữ liệu chưa đủ để dùng, và ghi lại hành động kèm kết quả. Điều kiện đạt giá trị kinh doanh cần thêm bằng chứng outcome; số lần mở dashboard hoặc số dòng score chỉ là tín hiệu sử dụng.

## 12 Nguồn tham khảo đã đối chiếu

[S01] Dashboards That Deliver. Trang tác giả và mục lục về discovery, prototype, user testing, release, adoption và maintenance. https://dashboardsthatdeliver.com/

[S02] Tableau. Best Practices for Effective Dashboards. Tài liệu chính thức về mục đích, audience và bố cục. https://help.tableau.com/current/pro/desktop/en-us/dashboards_best_practices.htm

[S03] Cole Nussbaumer Knaflic. Storytelling with Data. Trang nhà xuất bản, mục lục và giới thiệu ấn bản kỷ niệm. https://www.wiley.com/en-us/storytelling-with-data-a-data-visualization-guide-for-business-professionals-10th-anniversary-edition-p-9781394388097

[S04] Stephen Few. Information Dashboard Design. Trang nhà xuất bản về thiết kế phục vụ theo dõi nhanh. https://analyticspress.com/idd.php

[S05] Steve Wexler, Jeffrey Shaffer, Andy Cotgreave. The Big Book of Dashboards. Trang tác giả về ví dụ theo tình huống kinh doanh. https://www.bigbookofdashboards.com/

[S06] Joe Reis và Matt Housley. Fundamentals of Data Engineering. Trang nhà xuất bản và mục lục. https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/

[S07] Kimball Group. Four Step Dimensional Design Process. https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/

[S08] dbt Labs. dbt Semantic Layer. Tài liệu chính thức về định nghĩa metric tập trung. https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl

[S09] Uber Engineering. How Uber Achieves Operational Excellence in the Data Quality Experience. Kinh nghiệm đội kỹ thuật về tiêu chuẩn và vòng đời xử lý chất lượng. https://www.uber.com/gb/en/blog/operational-excellence-data-quality/

[S10] Apache Airflow. Best Practices. Tài liệu về retry, partition và kết quả task nhất quán. https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

[S11] W3C. Web Content Accessibility Guidelines 2.2. https://www.w3.org/TR/WCAG22/

[S12] scikit learn. Probability calibration. https://scikit-learn.org/stable/modules/calibration

[S13] Microsoft Research. Patterns of Trustworthy Experimentation During Experiment Stage. https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-during-experiment-stage/

[S14] Google Research. The ML Test Score A Rubric for ML Production Readiness and Technical Debt Reduction. https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/

[S15] NIST. AI RMF Core. https://airc.nist.gov/airmf-resources/airmf/5-sec-core/

[S16] IFRS Foundation. IAS 2 Inventories. https://www.ifrs.org/issued-standards/list-of-standards/ias-2-inventories/

[S17] IFRS Foundation. IAS 7 Statement of Cash Flows. https://www.ifrs.org/issued-standards/list-of-standards/ias-7-statement-of-cash-flows/

Các mô tả hiện trạng đối chiếu từ BUSINESS_GUIDE.md, UPLOAD_GUIDE.md, RUNBOOK.md, registry Probit, source CSS và Ket_qua_kiem_tra.json trong workspace. Chúng là bằng chứng nội bộ của dự án, không được các tác giả nguồn bên ngoài đánh giá hoặc chứng nhận.
