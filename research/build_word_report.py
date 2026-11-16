"""Build the full Vietnamese business and technical report from verified run artifacts."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Inches,Pt,RGBColor,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_TAB_ALIGNMENT,WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/word_report'
RUN=Path(json.loads((ROOT/'outputs/enterprise/latest.json').read_text(encoding='utf-8'))['path'])
S=json.loads((OUT/'deep_summary.json').read_text(encoding='utf-8'))
Q=json.loads((RUN/'quality.json').read_text(encoding='utf-8'))
A=json.loads((RUN/'analytics_summary.json').read_text(encoding='utf-8'))
F=json.loads((RUN/'forecast_summary.json').read_text(encoding='utf-8'))
R=json.loads((RUN/'risk_summary.json').read_text(encoding='utf-8'))
B=json.loads((RUN/'association_metrics.json').read_text(encoding='utf-8'))
EXPECTED_SIGNATURE='356e56a950890ee4f7016e41c6b77a9d741c54e4661c70d9619475ab2189601b'
manifest=json.loads((RUN/'run_manifest.json').read_text(encoding='utf-8'))
if S['run_id']!=RUN.name or S['source_signature']!=manifest['signature']:
    raise RuntimeError('Deep analysis does not match latest model run; regenerate the evidence first')
if manifest['signature']!=EXPECTED_SIGNATURE:
    raise RuntimeError('Source/code/config differs from the reviewed snapshot. Review the report narrative and benchmarks before issuing a new Word report.')
def read(n,deep=False):return pd.read_csv((OUT if deep else RUN)/f'{n}.csv')
def num(v,d=0):return f'{float(v):,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
def pct(v,d=1):return num(v*100,d)+'%'
doc=Document();section=doc.sections[0];section.page_width=Cm(21);section.page_height=Cm(29.7)
section.top_margin=Cm(1.8);section.bottom_margin=Cm(1.8);section.left_margin=Cm(2);section.right_margin=Cm(2);section.footer_distance=Cm(.7)
styles=doc.styles
for style in styles:
    for border in list(style._element.xpath('.//w:pBdr')):border.getparent().remove(border)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
    style=styles[name];style.font.name='Arial';style.font.color.rgb=RGBColor(0,0,0)
    style._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Arial')
styles['Normal'].font.size=Pt(10.5);styles['Normal'].paragraph_format.line_spacing=1.13;styles['Normal'].paragraph_format.space_after=Pt(6)
styles['Title'].font.size=Pt(27);styles['Title'].font.bold=True;styles['Title'].paragraph_format.space_after=Pt(18)
styles['Subtitle'].font.size=Pt(14);styles['Subtitle'].paragraph_format.space_after=Pt(14)
for name,size in [('Heading 1',17),('Heading 2',12),('Heading 3',11)]:
    styles[name].font.size=Pt(size);styles[name].font.bold=True;styles[name].paragraph_format.space_before=Pt(10 if name!='Heading 1' else 0);styles[name].paragraph_format.space_after=Pt(7)
styles['Caption'].font.size=Pt(9);styles['Caption'].font.italic=True;styles['Caption'].paragraph_format.space_after=Pt(6)
footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
run=footer.add_run('Trang ');run.font.size=Pt(9)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
doc.core_properties.title='Phân tích dữ liệu và mô hình cho chuỗi siêu thị'
doc.core_properties.subject='Phân tích kinh doanh mô hình dự báo và quy trình dữ liệu tự động'
doc.core_properties.author='';doc.core_properties.keywords='bán lẻ, siêu thị, phân tích dữ liệu, dự báo, CRM, tự động hóa'
PAGES=[];FIGURES=[]
def p(text,bold=False):
    x=doc.add_paragraph();r=x.add_run(str(text));r.bold=bold;return x
def h(text):return doc.add_paragraph(text,style='Heading 2')
def page(title):
    doc.add_page_break();heading=doc.add_paragraph(title,style='Heading 1');PAGES.append(title)
    start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(len(PAGES)));start.set(qn('w:name'),f'section_{len(PAGES)}')
    stop=OxmlElement('w:bookmarkEnd');stop.set(qn('w:id'),str(len(PAGES)))
    heading._p.insert(1,start);heading._p.append(stop)
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths is None:widths=[17/len(headers)]*len(headers)
    for i,width in enumerate(widths):t.columns[i].width=Cm(width)
    for i,name in enumerate(headers):t.rows[0].cells[i].text=str(name)
    for row in rows:
        cells=t.add_row().cells
        for i,value in enumerate(row):cells[i].text=str(value)
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for ri,row in enumerate(t.rows):
        no_split=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no_split)
        for ci,cell in enumerate(row.cells):
            cell.width=Cm(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'244D73' if ri==0 else ('F0F4F8' if ri%2==0 else 'FFFFFF'));pr.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'5');x.set(qn('w:color'),'D9D9D9');borders.append(x)
            pr.append(borders);margins=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                x=OxmlElement('w:'+edge);x.set(qn('w:w'),'85');x.set(qn('w:type'),'dxa');margins.append(x)
            pr.append(margins)
            for para in cell.paragraphs:
                para.paragraph_format.space_after=Pt(1);para.paragraph_format.space_before=Pt(1);para.paragraph_format.line_spacing=1.07
                if ri==0:para.alignment=WD_ALIGN_PARAGRAPH.CENTER
                elif ci>0 and len(str(rows[ri-1][ci]))<18:para.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for rr in para.runs:rr.font.name='Arial';rr.font.size=Pt(9);rr.bold=ri==0;rr.font.color.rgb=RGBColor(255,255,255) if ri==0 else RGBColor(0,0,0)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t
def fig(name,caption,width=16.6):
    path=next((OUT/'figures').glob(name+'*.png'));para=doc.add_paragraph();para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(2);para.paragraph_format.keep_with_next=True
    rr=para.add_run();shape=rr.add_picture(str(path),width=Cm(width));shape._inline.docPr.set('descr',caption)
    idx=len(FIGURES)+1;doc.add_paragraph(f'Hình {idx}  {caption}',style='Caption');FIGURES.append({'number':idx,'caption':caption,'file':path.name})
def source(text='Kết quả tính từ dữ liệu và artifact của lần chạy D1 và phân tích bổ sung D2'):
    pp=doc.add_paragraph('Nguồn: '+text+'.');pp.paragraph_format.space_after=Pt(5)
    for rr in pp.runs:rr.font.size=Pt(8.5);rr.italic=True

def build():
    doc.add_paragraph('Phân tích dữ liệu và mô hình cho chuỗi siêu thị',style='Title')
    doc.add_paragraph('Báo cáo kinh doanh và thiết kế quy trình dữ liệu tự động',style='Subtitle')
    p('Ngày báo cáo 01 tháng 11 năm 2026')
    p('Kỳ dữ liệu chính từ ngày 01 tháng 01 đến ngày 31 tháng 12 năm 2017')
    h('Mục đích của báo cáo')
    p('Báo cáo đánh giá khả năng khai thác dữ liệu giao dịch để hỗ trợ quản lý chuỗi siêu thị và cửa hàng bán lẻ. Nội dung kết hợp phân tích hoạt động bán hàng, hành vi khách hàng, khuyến mãi, dự báo và quy trình xử lý dữ liệu có thể chạy lại. Người đọc có thể sử dụng kết quả để lựa chọn bài toán PoC, xác định dữ liệu cần yêu cầu và thống nhất tiêu chí nghiệm thu với doanh nghiệp.')
    p('Kết quả hiện tại ủng hộ việc ưu tiên hợp nhất và đối soát dữ liệu, sau đó thử mô hình khách hàng và dự báo nhóm hàng. Mô hình khách hàng cải thiện khả năng xếp hạng so với quy tắc recency. Với dự báo và gợi ý giỏ hàng, các phương án đơn giản vẫn cạnh tranh tốt hơn trong thiết kế kiểm tra hiện có. Vì vậy, việc lựa chọn giải pháp phải dựa trên bằng chứng đánh giá và quyết định vận hành cần hỗ trợ.')
    h('Phạm vi bằng chứng')
    p('Phân tích chính dùng Complete Journey, một panel hộ mua hàng thường xuyên do người duy trì package xử lý từ nguồn 84.51°. Các giá trị tiền là USD trong bộ dữ liệu nước ngoài. Số liệu theo cửa hàng chỉ thuộc nhóm hộ quan sát, chưa đại diện doanh thu đầy đủ của chuỗi. Báo cáo phân biệt kết quả đã đo, giả định mô hình và đề xuất cần kiểm chứng bằng dữ liệu doanh nghiệp Việt Nam. [1][2]')
    p('Đối tượng sử dụng gồm lãnh đạo chuỗi, vận hành, ngành hàng, CRM, kế toán, IT và nhóm phân tích dữ liệu. Các khuyến nghị đặt hàng, đổi giá hay gửi ưu đãi cần dữ liệu bổ sung và quy trình duyệt trước khi áp dụng.')

    page('Tóm tắt dành cho người ra quyết định')
    table(['Nội dung','Bằng chứng chính','Hàm ý'],[
        ['Phạm vi dữ liệu',f'{num(Q["in_scope_rows"])} dòng và {num(Q["households"])} hộ trong năm 2017','Phù hợp thử phương pháp và kiểm tra pipeline'],
        ['Tăng trưởng cuối kỳ','Tháng 12 tăng 9,4% so với tháng 11','Giá trị giỏ đóng góp nhiều hơn số giỏ'],
        ['Tập trung khách hàng','20% hộ đóng góp 54,6% doanh số mua dương','Ưu tiên giữ quan hệ với nhóm giá trị cao'],
        ['Khách hàng không mua','Precision top 20 đạt khoảng 43 đến 45%','Khoảng ba lần tỷ lệ nhãn dương chung'],
        ['Dự báo 7 ngày','Baseline trung bình 28 ngày đạt WAPE 15,0%','Chưa có bằng chứng ML dự báo vượt baseline'],
        ['Gợi ý giỏ hàng','Popularity đạt hit ở ba gợi ý khoảng 66,3%','Association chưa cải thiện tiêu chí kiểm tra']],[3.2,7.4,6.4])
    h('Ba quyết định nên thực hiện trước')
    p('Trước hết, chỉ định chủ sở hữu dữ liệu và chốt định nghĩa doanh thu, hoàn hủy, thuế, ngày kinh doanh và mã SKU dùng chung. Những điểm này quyết định độ tin cậy của mọi báo cáo sau đó. Tiếp theo, chạy PoC trên một nhóm cửa hàng và ngành hàng đại diện, có baseline hiện hành để so sánh. Cuối cùng, đưa mô hình vào chế độ quan sát song song và đánh giá hành động nghiệp vụ bằng thử nghiệm phù hợp.')
    h('Những giới hạn ảnh hưởng trực tiếp đến quyết định')
    p('Dữ liệu chỉ có một năm và một nhóm hộ; không có tồn kho đầy đủ, giá vốn, lead time hay chi phí marketing. Ngày 25/12/2017 vắng bản ghi và được khai báo là giả định số tiền quan sát bằng 0. Dải dự báo heuristic chỉ bao phủ 61,9% quan sát test, thấp hơn mức danh nghĩa 90%; không sử dụng dải này để cam kết mức dịch vụ tồn kho.')
    source()

    page('Mục lục')
    toc=[
      'Dữ liệu và khả năng áp dụng','Chất lượng và đối soát','Biến động doanh thu','Ngành hàng và nguyên nhân biến động','Danh mục sản phẩm và tập trung doanh số','Giá trị khách hàng và phân nhóm','Nhóm khách theo thời điểm xuất hiện','Hành vi mua xuyên cửa hàng','Khuyến mãi và giới hạn diễn giải','Đánh giá chiến dịch coupon','Thiết kế bài toán dự báo','So sánh các mô hình dự báo','Sai số theo ngành hàng và theo tuần','Bất định và giới hạn dự báo','Thiết kế mô hình khách hàng','Kết quả nhận diện khách giảm mua','Công suất chăm sóc và độ bất định','Giải thích và kiểm tra điểm rủi ro','Giỏ hàng và gợi ý mua cùng','Kiến trúc quy trình dữ liệu','Mô hình dữ liệu cho chuỗi','Vận hành tự động và giám sát','Thiết kế thử nghiệm kinh doanh','Lộ trình PoC và điều kiện nghiệm thu','Hiệu quả kinh tế và quản trị rủi ro','Hồ sơ mô hình và tái lập','Từ điển chỉ tiêu và dữ liệu cần xin','Nguồn tham khảo','Phụ lục sai số dự báo chi tiết']
    toc.append('Thuật ngữ chuyên môn')
    for i,title in enumerate(toc,1):
        pp=doc.add_paragraph();pp.paragraph_format.space_after=Pt(4);pp.paragraph_format.line_spacing=1.05
        pp.paragraph_format.tab_stops.add_tab_stop(Cm(16.8),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
        link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),f'section_{i+2}')
        rr=OxmlElement('w:r');tt=OxmlElement('w:t');tt.text=f'{i:02d}  {title}';rr.append(tt);link.append(rr);pp._p.append(link)
        pp.add_run('\t'+str(i+3))
    p('Các chương đi từ bằng chứng dữ liệu đến đánh giá mô hình và điều kiện triển khai. Mỗi biểu đồ thể hiện kết quả đã tính hoặc được ghi rõ là sơ đồ thiết kế đề xuất. Số trang ở chân trang hỗ trợ đối chiếu khi trao đổi.')

    page('01 Dữ liệu và khả năng áp dụng')
    p('Complete Journey là bộ dữ liệu chính vì có giao dịch hàng tiêu dùng, thông tin nhóm hàng, mã hộ, mã cửa hàng và dữ liệu chiến dịch. Bản package được dùng cung cấp 1.469.307 dòng giao dịch, khác với mô tả nguồn dunnhumby có thể bao phủ hai năm. Phân tích giữ đúng phiên bản đã tải và không trộn các phiên bản. [1][2]')
    table(['Nguồn','Vai trò trong nghiên cứu','Trạng thái'],[
       ['Complete Journey','Phân tích chính và huấn luyện mô hình','Đã tải và xử lý'],['UCI Online Retail','Đối chiếu vấn đề chất lượng giao dịch','Đã tải và khảo sát riêng'],['Favorita Grocery Sales','Ứng viên mở rộng dự báo ngày và SKU','Đã xác định nguồn chưa train'],['dunnhumby Source Files','Ứng viên nghiên cứu giá và quảng bá','Đã xác định nguồn chưa tải']],[4.2,8.1,4.7])
    h('Đơn vị quan sát và ý nghĩa số tiền')
    p('Một dòng giao dịch mô tả một sản phẩm trong một lần mua, nhưng không được xem mỗi dòng là một đơn hàng. Các chỉ tiêu giỏ hàng phải gom theo basket_id. Trường sales_value thể hiện khoản nhà bán lẻ nhận theo quy tắc discount và bù coupon của nguồn, chưa phải lợi nhuận và có thể khác số tiền khách trả. Không trừ discount thêm lần nữa để tạo một chỉ tiêu doanh thu chưa được định nghĩa. [2]')
    h('Khả năng chuyển sang doanh nghiệp Việt Nam')
    p('Các quy trình kiểm tra dữ liệu, phân rã doanh thu, đánh giá theo thời gian và quản lý model có thể tái sử dụng. Các hệ số, ngưỡng RFM, điểm rủi ro, lịch mùa vụ và kết quả mô hình phải được huấn luyện và đánh giá lại. Tên ngành hàng và mã cửa hàng trong báo cáo là nhãn của nguồn nước ngoài, không phải thông tin của một chuỗi Việt Nam đã khảo sát.')
    p('Trong kỳ năm 2017 có 457 mã cửa hàng nhưng chỉ 2.469 hộ. Vì thế, so sánh tổng tiền giữa các cửa hàng phản ánh cả độ phủ của panel. Không dùng trực tiếp bảng này để xếp hạng năng suất, lợi nhuận hay hiệu quả nhân viên của cửa hàng.')
    source('Tài liệu nguồn [1][2][3] và metadata của lần chạy D1')

    page('02 Chất lượng và đối soát')
    table(['Kiểm tra','Kết quả','Cách xử lý'],[
      ['Dòng thuộc năm 2017',num(Q['in_scope_rows']),'Loại 534 dòng thuộc phần đầu ngày 01/01/2018'],['Số tiền raw',num(Q['raw_sales'],2)+' USD','Dùng cho tổng hợp và đối soát'],['Dòng không đủ điều kiện mua dương',num(Q['model_excluded_rows']),'Giữ riêng không xóa khỏi đối soát'],['Không nối được SKU',num(Q['unmatched_product_rows'])+' dòng','Giữ UNKNOWN và xuất danh sách xử lý'],['Dòng trùng nguyên bản','0','Gate dừng nếu phát hiện trùng'],['Ngày không có bản ghi','25/12/2017','Giả định khai báo rõ và phân tích độ nhạy']],[5.2,4.1,7.7])
    h('Đối soát có thể truy vết')
    p(f'Tổng số tiền raw là {num(Q["raw_sales"],2)} USD, bằng doanh số mua dương {num(Q["positive_sales"],2)} USD cộng {num(Q["excluded_model_sales"],2)} USD của các dòng loại khỏi mô hình. Số dòng ngoại lệ tương đối nhiều nhưng phần chênh tiền nhỏ. Điều đó không đủ để bỏ qua ngoại lệ vì chúng vẫn có thể ảnh hưởng tần suất mua, số giỏ và ý nghĩa giao dịch.')
    p('Pipeline kiểm tra cột bắt buộc, ID rỗng, giá trị số không hữu hạn, khóa danh mục bị trùng và một basket_id thuộc nhiều khách hoặc cửa hàng. Phép nối products được kiểm tra many to one để ngăn nhân doanh thu. Tổng theo tháng, dữ liệu enriched và SQL mart được đối soát trước khi công bố kết quả.')
    h('Những điểm cần xác minh với chủ dữ liệu')
    p('Cần giải thích ngày vắng bản ghi bằng lịch mở cửa hoặc log xuất dữ liệu. Không có dòng giao dịch chỉ chứng minh không quan sát được giao dịch, chưa chứng minh không có nhu cầu. Với dữ liệu thật, cờ mất nguồn phải tách khỏi đóng cửa và hết hàng. Các bản ghi không khớp SKU cần người quản lý danh mục xác nhận mã mới, mã tạm, mã dịch vụ hoặc khác hệ thống.')
    p('UCI là ví dụ kiểm tra chéo: 135.080 dòng thiếu CustomerID và 5.268 dòng trùng toàn bộ. Các kết quả đó không được ghép vào train của Complete Journey; chúng cho thấy kiểm tra trực tiếp file có giá trị hơn việc chỉ tin mô tả trên trang tải.')
    source('quality.json của D1 và profile.json của khảo sát ban đầu')

    page('03 Biến động doanh thu')
    fig('01_revenue','Số tiền bán và các thành phần của giỏ hàng trong năm 2017')
    p('Doanh số tháng cần được đọc đồng thời với số giỏ và giá trị bình quân mỗi giỏ. Cùng một mức tăng doanh số có thể xuất phát từ nhiều lượt mua hơn, nhiều tiền hơn trong mỗi lượt hoặc thay đổi nhóm hộ đang mua. Báo cáo chưa có traffic và số lượt khách ghé cửa hàng nên không tính conversion từ khách ghé sang khách mua.')
    p('Tháng 12 đạt 421.882,29 USD so với 385.552,25 USD của tháng 11, tăng 36.330,04 USD tương đương 9,4%. Đây là biến động trong panel, chưa phải tăng trưởng toàn chuỗi. So sánh này không kiểm soát lịch trả lương, chương trình khuyến mãi hay số ngày mở cửa; vì vậy chỉ mô tả thay đổi, chưa xác định nguyên nhân nhân quả.')
    h('Quyết định hỗ trợ')
    p('Nhóm vận hành nên kiểm tra cửa hàng và ngành hàng đóng góp vào biến động, sau đó đối chiếu lịch chương trình và cơ cấu khách. Khi áp dụng cho chuỗi thật, thêm same store sales với tập cửa hàng đủ kỳ đã chốt trước, đồng thời tách phần tăng do mở cửa hàng mới. Giá trị giỏ lớn hơn cũng chưa chứng minh tăng lãi nếu cơ cấu hàng hoặc mức giảm giá thay đổi.')
    source()

    page('04 Ngành hàng và nguyên nhân biến động')
    fig('02_bridge','Phân rã đối xứng của biến động doanh số tháng 12 so với tháng 11')
    p('Phân rã dùng doanh số bằng số giỏ nhân giá trị giỏ. Hiệu ứng số giỏ được tính bằng thay đổi số giỏ nhân trung bình giá trị giỏ của hai tháng; hiệu ứng giá trị giỏ được tính bằng thay đổi giá trị giỏ nhân trung bình số giỏ. Cách chia đối xứng phân bổ phần tương tác và bảo đảm hai hiệu ứng cộng đúng chênh lệch doanh số.')
    p('Kết quả: số giỏ đóng góp 11.696,78 USD, còn giá trị giỏ đóng góp 24.633,26 USD. Hiệu ứng giá trị giỏ chiếm khoảng 67,8% mức tăng. Đây là phân rã số học của kết quả, không phải bằng chứng việc tăng giá đã gây tăng doanh số.')
    table(['Ngành hàng','Đóng góp tăng tháng 12','Tỷ lệ mức tăng ròng'],[[row.department,num(row.delta_sales,2)+' USD',pct(row.share_of_net_change)] for row in read('department_growth_contribution',True).head(4).itertuples()],[6.6,5.5,4.9])
    p('GROCERY và DRUG GM đóng góp khoảng 67,8% mức tăng ròng. Danh sách này giúp ngành hàng xác định nơi cần xem tiếp SKU, nhóm khách và chương trình. Tỷ lệ đóng góp của một ngành có thể âm hoặc vượt 100% nếu các ngành khác giảm, nên không diễn giải như thị phần.')
    source()

    page('05 Danh mục sản phẩm và tập trung doanh số')
    fig('05_abc','Đường tích lũy doanh số mua dương sau khi xếp SKU giảm dần')
    p(f'Có {num(A["A_product_count"])} trên {num(A["product_count"])} SKU có mua dương thuộc lớp A theo ngưỡng tích lũy 80%. Lớp B tiếp tục đến 95%, phần còn lại là C. SKU làm vượt ngưỡng được giữ trong lớp trước để không bỏ sót sản phẩm nằm tại ranh giới. Phân loại dựa trên doanh số, không phải lãi gộp hoặc tốc độ quay vòng tồn kho.')
    h('Bất thường phân cấp cần xử lý trước khi dự báo nhu cầu hàng hóa')
    p(f'Nhóm mang tên COUPON/MISC ITEMS có {num(S["taxonomy_special_sales"],2)} USD. Kiểm tra product_type cho thấy xăng GASOLINE REG UNLEADED đóng góp {num(309563.54+54449.62,2)} USD trong nhóm này, ngoài ra còn có gift card và giao dịch khác. Vì thế, không thể coi toàn bộ nhãn này là coupon hoặc một ngành hàng thực phẩm đồng nhất.')
    p('Doanh nghiệp cần tách hàng hóa, nhiên liệu, dịch vụ, gift card và bút toán đặc biệt theo quy tắc kế toán và vận hành. Kết quả model đã đánh giá được giữ nguyên để bảo toàn test; việc sửa taxonomy là yêu cầu cho vòng mô hình tiếp theo, không sửa lại test rồi báo cáo như thể đã được chọn từ đầu.')
    p('ABC hỗ trợ ưu tiên rà soát độ sẵn hàng và danh mục. Để quyết định cắt SKU, cần thêm biên lợi nhuận, vai trò kéo khách, thay thế trong giỏ, hạn dùng, ràng buộc trưng bày và tồn kho. SKU doanh số thấp vẫn có thể cần thiết cho độ phủ danh mục hoặc một nhóm khách có giá trị.')
    source()

    page('06 Giá trị khách hàng và phân nhóm')
    fig('07_segments','Quy mô và tỷ trọng doanh số của các nhóm khách theo quy tắc nghiệp vụ')
    p(f'20% hộ có giá trị mua cao nhất tạo 54,6% doanh số mua dương; chỉ số tập trung Gini quan sát khoảng {num(S["gini_observed_sales"],3)}. Các kết quả này cho thấy giá trị mua phân bố không đồng đều. Chúng chưa mô tả CLV vì không có biên lợi nhuận, chi phí duy trì, thời gian sống khách hàng ngoài kỳ hay tác động của chăm sóc.')
    p('Quy tắc nhóm chủ lực dùng recency không quá 14 ngày và sales cùng frequency ở tứ phân vị trên. Nhóm giá trị cao cần kiểm tra giảm mua có recency ít nhất 28 ngày và sales ở tứ phân vị trên. Ngưỡng sales tương ứng là 2.536,15 USD, frequency là 83 giỏ trong kỳ. Đây là ngưỡng mô tả của bộ public, không phải định mức chung cho khách siêu thị Việt Nam.')
    h('Phân cụm chỉ đóng vai trò khám phá')
    p('KMeans được thử với k từ 3 đến 6 trên các biến log rồi chuẩn hóa. K bằng 3 có silhouette khoảng 0,368; ARI giữa hai seed khoảng 0,978. Cụm tương đối ổn định giữa hai khởi tạo nhưng độ tách chưa cao và có thể chủ yếu phản ánh quy mô mua. Cluster ID không phải nhãn churn; phân nhóm nghiệp vụ dễ giải thích vẫn hữu ích khi giao việc cho CRM.')
    p('Hành động phù hợp là rà soát nhóm giá trị cao đang giảm mua, xác định kênh và cửa hàng thường mua, rồi thử cách chăm sóc có đối chứng. Không dùng tổng doanh số năm để chấm điểm một thời điểm quá khứ, vì như vậy sẽ đưa thông tin tương lai vào quyết định.')
    source()

    page('07 Nhóm khách theo thời điểm xuất hiện')
    fig('08_cohorts','Hoạt động giao dịch theo nhóm tháng đầu xuất hiện trong file')
    p('Mỗi hàng gồm các hộ có tháng xuất hiện đầu tiên giống nhau; mỗi cột là số tháng tính từ tháng đó. Tỷ lệ bằng số hộ có giao dịch trong tháng tương ứng chia quy mô nhóm ban đầu. Ô tương lai không có dữ liệu được để trống thay vì điền 0. Bảng này theo dõi hoạt động quan sát, không chứng minh khách được thu hút mới đúng vào tháng đầu xuất hiện.')
    h('Thiên lệch do giới hạn cửa sổ dữ liệu')
    p('Các hộ xuất hiện ở tháng 01 có thể đã mua nhiều năm trước khi file bắt đầu. Nhóm xuất hiện cuối kỳ có ít thời gian để đánh giá hơn. Vì panel gồm hộ mua hàng thường xuyên, tỷ lệ hoạt động không thể áp dụng thẳng cho khách vãng lai hoặc mọi khách của chuỗi. Quy mô nhóm cần được đặt cạnh tỷ lệ để tránh coi biến động của nhóm nhỏ là tín hiệu chắc chắn.')
    h('Cách sử dụng tại doanh nghiệp')
    p('Nên dựng riêng cohort theo ngày đăng ký loyalty, lần mua đầu tiên xác minh được và lần tái kích hoạt. So các cohort ở cùng tuổi khách hàng và cửa sổ quan sát. Khi kết nối giao dịch xuyên cửa hàng hoặc kênh, hoạt động còn mua ở cấp chuỗi cần được tính trước khi kết luận khách đã ngừng mua.')
    p('Một hướng phân tích tiếp theo là theo dõi nhóm hàng bị giảm tham gia trong từng cohort và thời gian giữa hai lần mua. Những câu hỏi đó giúp phân biệt giảm tần suất toàn chuỗi với chuyển danh mục, nhưng vẫn cần kiểm tra tác động của mùa vụ và chương trình trước khi thiết kế can thiệp.')
    source()

    page('08 Hành vi mua xuyên cửa hàng')
    fig('09_cross_store','Phân bố số cửa hàng có giao dịch mua dương của mỗi hộ')
    c=S['cross_store']
    p(f'{num(c["multiple_store_households"])} hộ, tương đương {pct(c["share_multiple_stores"])}, có giao dịch tại nhiều hơn một cửa hàng trong năm. Trung vị là {num(c["median_stores"])} cửa hàng. Trong {num(c["q3_q4_comparable_households"])} hộ có mua ở cả quý 3 và quý 4, {num(c["q3_q4_dominant_store_changed"])} hộ đổi cửa hàng có giá trị mua cao nhất, tương đương {pct(c["q3_q4_dominant_store_changed_share"])}.')
    p('Cửa hàng chủ đạo được xác định bằng tổng sales_value mua dương trong từng quý; khi bằng nhau, mã cửa hàng làm tiêu chí phụ cố định. Phân tích chỉ xét hộ có giao dịch ở cả hai quý. Đổi cửa hàng chủ đạo không đồng nghĩa chuyển toàn bộ mua sắm, cũng chưa giải thích lý do đổi như địa điểm, khuyến mãi hoặc thay đổi sinh hoạt.')
    h('Hàm ý cho CRM và quản lý vùng')
    p('CRM tính riêng từng cửa hàng có thể gắn sai nhãn rời bỏ khi khách vẫn mua ở nơi khác trong chuỗi. Nên có ID khách toàn chuỗi, chỉ tiêu hoạt động toàn chuỗi và chỉ tiêu mức gắn bó với cửa hàng thường mua. Cần phân biệt giảm mua thật với đổi kênh, đổi điểm bán hoặc mã khách bị đứt mapping.')
    p('Khi triển khai thật, kiểm tra các hộ có số cửa hàng bất thường để phát hiện mã tài khoản dùng chung hoặc lỗi định danh. Cũng không dùng tổng doanh số panel của cửa hàng để kết luận cửa hàng đó thu hút nhiều khách hơn nếu độ phủ loyalty hay panel khác nhau.')
    source()

    page('09 Khuyến mãi và giới hạn diễn giải')
    fig('10_discount','So sánh tiền mỗi dòng có và không có discount trong cùng cặp SKU và cửa hàng')
    discount=S['discount_observational']
    p(f'Khoảng {pct(discount["positive_line_discount_share"])} dòng mua dương có ít nhất một trường discount khác 0. Trong {num(discount["paired_product_store_count"])} cặp SKU và cửa hàng có cả hai trạng thái, trung vị tỷ lệ tiền mỗi dòng có giảm giá so với không giảm là {num(discount["median_discounted_to_nondiscounted_line_value"],3)}. Khoảng tứ phân vị lần lượt là {num(discount["ratio_q25"],3)} và {num(discount["ratio_q75"],3)}.')
    p('So sánh trong cùng SKU và cửa hàng loại bớt khác biệt cơ cấu sản phẩm, nhưng chưa kiểm soát ngày, số lượng mỗi dòng, mức mua của khách, chương trình chồng nhau hoặc việc chủ động giảm giá khi nhu cầu yếu. Tiền mỗi dòng cũng không phải giá đơn vị hay nhu cầu. Vì vậy, tỷ lệ dưới 1 chưa cho phép kết luận khuyến mãi làm giảm doanh thu hoặc không hiệu quả.')
    p('Đồ thị chặn tỷ lệ ở 1/8 và 8 để quan sát phần phân bố chính; các giá trị ở hai đuôi được gom tại biên. Trung vị và tứ phân vị ở trên tính từ tỷ lệ gốc. Mỗi cặp chưa áp ngưỡng số dòng tối thiểu, nên kết quả còn nhạy với các cặp có ít giao dịch.')
    h('Thiết kế đánh giá đáng tin cậy hơn')
    p('Cần lịch giá thường và giá giảm theo thời điểm, đơn vị quy đổi, danh sách đối tượng được nhận, hỗ trợ từ nhà cung cấp, giá vốn và chi phí. Thử nghiệm phải đo cả tăng lượng bán, thay thế giữa SKU, mua sớm rồi giảm mua về sau và dịch chuyển giữa cửa hàng. Kết quả đích là lợi ích tăng thêm sau chi phí, không chỉ chênh sales giữa các dòng có và không có giảm giá.')
    source('Phân tích D2 và định nghĩa discount của nguồn [2]')

    page('10 Đánh giá chiến dịch coupon')
    fig('11_campaigns','Tỷ lệ hộ đổi coupon và khoảng Wilson 95 phần trăm theo chiến dịch đủ điều kiện')
    p('Tỷ lệ được tính bằng số hộ có assignment và có ít nhất một redemption khớp campaign chia số hộ được gán campaign. Không đếm coupon product nhiều dòng thành nhiều lần chuyển đổi. Nguồn có 2.102 dòng redemption đến cuối kỳ và không có dòng thiếu assignment tương ứng trong kiểm tra này.')
    p('Hình chỉ so các chiến dịch có cửa sổ nằm trọn trong kỳ và ít nhất 100 hộ được gán. Chiến dịch 18 có 214 trên 1.133 hộ đổi coupon, tương đương 18,9%; chiến dịch 13 có 196 trên 1.077 hộ, tương đương 18,2%. Khoảng Wilson biểu diễn bất định của tỷ lệ nhị thức, chưa điều chỉnh việc nhiều chiến dịch tác động cùng khách hoặc cách phân bổ chiến dịch không ngẫu nhiên. [5]')
    h('Vì sao chưa thể xếp hạng ROI')
    p('Chiến dịch có tỷ lệ đổi cao có thể đã nhắm đúng nhóm có xu hướng mua sẵn. Type A không cung cấp chính xác từng coupon đã gửi cho từng hộ, nên không tính conversion theo từng coupon exposure. Chiến dịch kết thúc sau 31/12 bị thiếu phần sau của cửa sổ và cần được đánh dấu, không so trực tiếp với chiến dịch đủ kỳ. [2]')
    p('Doanh nghiệp nên lưu assignment, thời điểm gửi, tiếp cận, redemption, tiền hỗ trợ và nhóm đối chứng. Nếu randomization theo cửa hàng hoặc cụm, cách tính cỡ mẫu và sai số cũng phải phản ánh cấp randomization. Tỷ lệ đổi coupon là chỉ tiêu vận hành hữu ích, nhưng chưa phải doanh thu hoặc lợi nhuận tăng thêm.')
    source('campaign_redemption của D1 và khoảng Wilson tính ở D2')

    page('11 Thiết kế bài toán dự báo')
    p('Target là tổng sales_value trong bảy ngày ngay sau thời điểm origin, tính cho 20 nhóm có doanh số cao trong 180 ngày đầu và nhóm OTHER. Dự báo được cộng trên toàn bộ cửa hàng của panel. Việc cố định từ vựng ở đầu kỳ tránh dùng doanh số tương lai để chọn nhóm hàng có vẻ quan trọng.')
    table(['Thành phần','Thiết kế đã chạy'],[
      ['Đầu vào lịch sử','Lag ngày hiện tại và các độ trễ 1 6 7 13 27 ngày'],['Đặc trưng tổng hợp','Trung bình và độ lệch chuẩn 7 14 28 56 ngày cùng tỷ lệ xu hướng'],['Thông tin lịch','Thứ trong tuần tháng và ngày trong năm của origin'],['Mô hình ML','Ridge hai cấu hình histogram gradient boosting và ExtraTrees'],['Baseline','Tổng 7 ngày trước và trung bình 28 ngày quy đổi 7 ngày'],['Validation','Ba origin 10/09 08/10 và 05/11/2017'],['Test','Bốn origin 03/12 10/12 17/12 và 24/12/2017']],[4.4,12.6])
    h('Tách thời gian và kiểm soát thông tin tương lai')
    p('Tại mỗi origin, chỉ dùng hàng train có nhãn bảy ngày đã hoàn tất đến origin. Test gồm bốn tuần mục tiêu không chồng nhau và được mở sau khi chọn champion bằng WAPE validation. Trong mỗi mốc test, mô hình dùng lịch sử mở rộng; kiểu đánh giá này gần với việc cập nhật model khi có dữ liệu mới hơn random split. [4]')
    p('Target được chia cho giá trị trung bình 28 ngày nhân bảy, chặn mẫu số tối thiểu 1. Các đặc trưng rolling chỉ dùng dữ liệu đến origin. Không đưa discount hay giá thực tế của tuần tương lai vào đầu vào. Ngày hiện tại ở đây là ngày đã hoàn tất, không phải số tiền bán dở trong ngày.')
    p('Chưa thực hiện dự báo từng SKU hoặc cửa hàng, dự báo lượng bán, mô hình tồn kho hay reconciliation phân cấp. Đó là các bài toán tiếp theo cần dữ liệu toàn chuỗi và ràng buộc nghiệp vụ; không xem việc có 457 mã cửa hàng trong nguồn là đủ để khẳng định đã giải được chúng.')
    source('Code và features của D1 cùng tài liệu đánh giá chuỗi thời gian [4]')

    page('12 So sánh các mô hình dự báo')
    fig('12_forecast_models','WAPE validation và test của các ứng viên và baseline')
    p('Trung bình 28 ngày có WAPE validation khoảng 5,39% và được chọn làm champion. Ridge đạt khoảng 6,02%, ExtraTrees 6,95%, hai cấu hình gradient boosting khoảng 8,20% và 8,31%; lặp bảy ngày trước khoảng 9,86%. Các mô hình ML đều đã được huấn luyện và lưu artifact, nhưng chưa vượt baseline theo tiêu chí chọn ban đầu.')
    table(['Phương án','WAPE test','Bias test'],[[r.model,pct(r.WAPE,2),pct(r.bias,2)] for r in read('forecast_test_metrics').itertuples()],[8.2,4.4,4.4])
    p('Ở test, champion đạt WAPE 14,99%, còn các ứng viên ML khoảng 18,86% đến 20,40%. Chênh lệch giữa validation và test cho thấy hiệu năng thay đổi theo giai đoạn. Chỉ bốn tuần cuối năm chưa đủ để khẳng định thứ hạng dài hạn. Không chọn lại một model theo kết quả test rồi trình bày test đó như một đánh giá độc lập mới.')
    p('Lựa chọn triển khai ban đầu nên giữ baseline làm phương án so sánh bắt buộc. Mô hình phức tạp chỉ đáng thay thế khi cải thiện được metric trên nhiều mốc, không gây bias bất lợi cho nhóm ưu tiên và có chi phí vận hành hợp lý.')
    source()

    page('13 Sai số theo ngành hàng và theo tuần')
    fig('13_forecast_weeks','Biến động thực tế dự báo và WAPE tại bốn origin test')
    p('Sai số chưa đồng đều theo thời điểm. WAPE ở hai mốc đầu khoảng 4,7% và 7,3%, tăng lên 22,4% và 24,9% ở hai mốc sau. Vì thế, chỉ nêu một con số 15% sẽ che mất thay đổi lớn gần cuối năm. Không có lịch khuyến mãi và ngày mở cửa đã xác minh nên chưa quy được mức tăng sai số cho một nguyên nhân cụ thể.')
    e=S['forecast'];p(f'OTHER chiếm {pct(e["OTHER_actual_share"])} doanh số test và {pct(e["OTHER_error_share"])} tổng sai số tuyệt đối. Khi cho mỗi nhóm trọng số bằng nhau, WAPE trung bình theo nhóm là {pct(e["macro_series_wape"])}; trung vị là {pct(e["median_series_wape"])}. Các metric này trả lời câu hỏi khác với WAPE toàn tập, vốn chịu ảnh hưởng lớn của nhóm có nhiều tiền bán.')
    table(['Nhóm hàng','WAPE test','Bias'],[[r.series,pct(r.WAPE),pct(r.bias)] for r in read('forecast_series_metrics').sort_values('WAPE',ascending=False).head(5).itertuples()],[9,4,4])
    p('CANDY PACKAGED có WAPE khoảng 53,4% dù không chi phối sai số tổng. BEERS ALES có bias âm khoảng 16,8%, còn SOUP có bias dương khoảng 11,5%. Đây là danh sách cần kiểm tra tính thời vụ, độ thưa và taxonomy trước khi giao forecast cho ngành hàng.')
    source()

    page('14 Bất định và giới hạn dự báo')
    fig('16_forecast_band','Dải residual heuristic và thực tế test cho nhóm OTHER')
    p('Dải dự báo dùng phân vị 90 của sai số tuyệt đối đã chuẩn hóa từ validation. Coverage test chỉ đạt 61,9% trên 84 cặp nhóm và origin. Đây là kết quả cho thấy dải đang hẹp hoặc phân bố sai số đã thay đổi, không phải một khoảng dự báo được bảo đảm bao phủ 90% trong vận hành. Các nhóm trong cùng tuần có tương quan nên 84 điểm cũng không tương đương 84 tuần độc lập.')
    h('Độ nhạy với ngày vắng bản ghi')
    sensitivity=read('forecast_test_without_assumed_zero_week');line=sensitivity[sensitivity.model.eq('mean_28_days')].iloc[0]
    p(f'Khi loại tuần mục tiêu chứa 25/12 khỏi phép đánh giá, WAPE của baseline còn {pct(line.WAPE,2)} trên 63 cặp nhóm và origin. Cách kiểm tra này cho biết kết quả nhạy với một tuần có giả định dữ liệu, nhưng không sửa được nguồn vắng và không chứng minh toàn bộ sai số của tuần đó do mất dữ liệu. Kết quả chính và độ nhạy phải được trình bày cùng nhau.')
    h('Điều kiện sử dụng trong kế hoạch tồn kho')
    p('Doanh nghiệp cần kiểm tra sai số nhiều mốc hơn, có ngày lễ và lịch chương trình, rồi đánh giá khoảng dự báo theo ngành và mức bán. Sau đó mới xem xét phương pháp interval hoặc quantile có kiểm định coverage trên các cửa sổ thời gian mới. Dự báo sales_value không được biến thẳng thành số lượng đặt hàng; cần dự báo lượng theo đơn vị thống nhất, tồn khả dụng, hàng đang về, lead time và ràng buộc đặt hàng.')
    p('Đối với mạng lưới nhiều cấp, tổng dự báo SKU và cửa hàng cần khớp các cấp vùng và chuỗi theo cách tổng hợp hoặc reconciliation được lựa chọn. Đây là thiết kế đề xuất cho dữ liệu doanh nghiệp, chưa là tính năng đã được đánh giá trong pipeline hiện tại. [4]')
    source()

    page('15 Thiết kế mô hình khách hàng')
    p('Bài toán đo khả năng không có giao dịch mua dương trong 28 ngày tiếp theo. Hộ chỉ đủ điều kiện nếu có mua dương trong 90 ngày trước origin. Định nghĩa này phù hợp một danh sách CRM cần rà soát, nhưng không đồng nghĩa khách đã rời bỏ vĩnh viễn hay không còn nhu cầu. Các hộ vắng hơn 90 ngày nằm ngoài phạm vi score và cần một quy trình tái kích hoạt riêng.')
    table(['Thành phần','Định nghĩa'],[
      ['Nhãn dương','Không có dòng mua dương từ ngày origin cộng 1 đến origin cộng 28'],['Nhãn âm','Có ít nhất một giao dịch mua dương trong đúng cửa sổ đó'],['Đặc trưng','Recency tenure quan sát lượt mua sales và đa dạng ngành 7 28 56 90 ngày cùng tỷ lệ discount'],['Ứng viên','Logistic regression histogram gradient boosting và quy tắc recency'],['Chọn model','Average precision trên snapshot validation 10/09/2017'],['Test giữ riêng','Snapshot 05/11 và 03/12/2017'],['Công suất giả định','Rà soát top 20% điểm cao nhất trong nhóm đủ điều kiện']],[4.6,12.4])
    h('Quy tắc sử dụng thời gian')
    p('Các snapshot cách nhau 28 ngày. Để train tại một origin, chỉ dùng snapshot có toàn bộ 28 ngày nhãn đã kết thúc. Model dùng cho test được fit trước origin test đầu; không dùng nhãn của hai snapshot test để chọn ứng viên. Sau đánh giá, model cuối được fit lại trên tất cả nhãn đã hoàn thành đến 31/12 để tạo danh sách score tiếp theo.')
    p('Mã khách không được đưa vào feature để ghi nhớ danh tính. Demographic không được dùng vì không có cho phần lớn hộ. Một hộ có thể xuất hiện ở nhiều snapshot vì mục tiêu là chấm điểm lại cùng khách theo thời gian; khi tính độ bất định phải nhận diện sự phụ thuộc đó, không coi mọi dòng là độc lập.')
    source('Thiết kế code và metadata mô hình D1')

    page('16 Kết quả nhận diện khách giảm mua')
    fig('17_risk_pr','Đường precision recall trên hai snapshot test gộp để mô tả')
    table(['Origin','Model','AP','Precision top 20','Recall top 20'],[[str(r.origin),('Gradient boosting' if r.model=='hist_gradient' else 'Recency'),num(r.PR_AUC_AP,3),pct(r.precision_top20),pct(r.recall_top20)] for r in read('risk_test_metrics').itertuples()],[3.0,4.7,2.3,3.5,3.5])
    p('Gradient boosting có AP validation khoảng 0,509, cao hơn logistic 0,491 và recency 0,423. Trên hai snapshot test, AP còn khoảng 0,464 và 0,452 nhưng vẫn cao hơn baseline. Precision top 20 đạt khoảng 43,4% và 45,3%, trong khi tỷ lệ nhãn dương của toàn nhóm chỉ khoảng 14,5% và 15,1%.')
    p('Ở snapshot 05/11, chọn 461 hộ tìm được 200 hộ thực tế không mua trong 28 ngày; vẫn có 261 hộ trong danh sách sẽ mua mà không cần căn cứ can thiệp. Do đó, lift khoảng ba lần thể hiện khả năng ưu tiên rà soát, chưa chứng minh 200 hộ có thể giữ lại nhờ ưu đãi. Average precision là metric xếp hạng; báo cáo dùng đúng AP của scikit learn thay vì mặc định coi đó là diện tích PR tính theo một quy tắc nội suy khác. [6]')
    source()

    page('17 Công suất chăm sóc và độ bất định')
    fig('18_risk_capacity','Đánh đổi giữa độ tập trung rủi ro và độ bao phủ khi thay công suất chọn')
    cap=read('risk_capacity',True);agg=cap[cap.model.eq('hist_gradient')].groupby('fraction')[['precision','recall','selected']].mean().reset_index()
    table(['Tỷ lệ chọn','Số hộ mỗi snapshot trung bình','Precision trung bình','Recall trung bình'],[[pct(r.fraction,0),num(r.selected,1),pct(r.precision),pct(r.recall)] for r in agg.itertuples()],[3,5.2,4.4,4.4])
    rb=S['risk_bootstrap'];ci=rb['precision_top20_difference_CI']
    p(f'Lấy mẫu lại 1.000 lần theo hộ, giữ cả các snapshot của mỗi hộ được chọn, cho chênh precision top 20 gộp giữa ML và recency khoảng {num(rb["precision_top20_difference"]*100,2)} điểm phần trăm. Khoảng percentile 95% là {num(ci[0]*100,2)} đến {num(ci[1]*100,2)} điểm phần trăm. Cách bootstrap này giữ phụ thuộc trong hộ, nhưng chỉ có điều kiện trên hai origin đang quan sát; chưa bao phủ biến động ở các tháng hoặc doanh nghiệp khác. [7]')
    p('Công suất 20% là giả định vận hành, không phải ngưỡng kinh tế tối ưu. Nếu nhóm CRM chỉ xử lý được 5%, precision có thể cao hơn nhưng bỏ sót nhiều hộ nguy cơ. Muốn đổi ngưỡng thành quyết định chi tiền cần thêm khả năng phản hồi, biên lợi nhuận và chi phí liên hệ hoặc ưu đãi.')
    source('risk_capacity và household cluster bootstrap D2')

    page('18 Giải thích và kiểm tra điểm rủi ro')
    fig('20_risk_importance','Tầm quan trọng hoán vị của các biến trên snapshot validation')
    p('Lượt mua 90 ngày, lượt mua 28 ngày, recency và độ đa dạng nhóm hàng là các biến có tín hiệu mạnh trong kiểm tra hoán vị. Khi hoán vị một biến rồi đo mức giảm AP, ta kiểm tra mức model đang dựa vào biến đó trong tập validation. Biến tương quan có thể chia sẻ tín hiệu, nên không diễn giải thứ hạng như tác động nhân quả hoặc mức đóng góp riêng hoàn toàn.')
    cal=read('risk_calibration',True);worst=(cal.observed-cal.predicted).abs().max()
    p(f'Kiểm tra theo decile cho thấy độ lệch lớn nhất giữa điểm trung bình và tỷ lệ thực tế khoảng {num(worst*100,1)} điểm phần trăm. Brier trên hai snapshot test gộp khoảng {num(S["risk_bootstrap"]["pooled_Brier_ML"],3)} cho ML và {num(S["risk_bootstrap"]["pooled_Brier_baseline"],3)} cho recency. Recency chỉ được quy đổi thành score tham chiếu, chưa phải mô hình xác suất đã hiệu chỉnh; Brier của nó cần đọc với giới hạn này.')
    h('Cách giao kết quả cho CRM')
    p('Danh sách nên kèm thời điểm score, cửa sổ dữ liệu, recency, tần suất gần đây, giá trị mua và nhãn ưu tiên để nhân sự rà soát. Model hiện chưa calibration riêng; sử dụng điểm để xếp hạng phù hợp hơn việc xem một giá trị như xác suất chính xác để định giá ưu đãi. Kiểm tra riêng từng vùng, cửa hàng thường mua và loại khách sau khi có dữ liệu toàn chuỗi.')
    p('Tần suất thấp hoặc recency cao có thể xuất phát từ chuyến đi xa, chuyển cửa hàng, đổi ID hoặc chu kỳ mua dài. Ngay cả khách có xác suất không mua cao cũng có thể ít phản hồi ưu đãi. Model hiện không ước lượng uplift, nguyên nhân giảm mua hay hiệu quả của một hành động cụ thể.')
    source('Feature importance D1 calibration D2 và tài liệu metrics [6]')

    page('19 Giỏ hàng và gợi ý mua cùng')
    fig('22_basket_models','So sánh association với popularity trên giỏ test đủ điều kiện')
    p('Quy tắc association được fit đến 03/09/2017, chọn phương án trên validation từ 04/09 đến 01/10, sau đó kiểm tra từ 02/10 đến 31/12. Từ vựng gồm 30 danh mục có nhiều giỏ nhất trong train. Chỉ giữ cặp có ít nhất 100 giỏ train và lift lớn hơn 1; điểm xếp hạng là confidence nhân log của lift.')
    p(f'Offline completion chọn một danh mục bằng hash cố định làm đầu vào và che phần còn lại của giỏ. Trên {num(B["popularity"]["evaluated_baskets"])} giỏ test có ít nhất hai danh mục trong từ vựng, popularity đạt hit ở ba gợi ý {pct(B["popularity"]["hit_at_3"])} và recall {pct(B["popularity"]["recall_at_3"])}. Association lần lượt đạt {pct(B["association"]["hit_at_3"])} và {pct(B["association"]["recall_at_3"])}. Popularity đã được chọn từ validation, không chọn lại bằng test.')
    h('Diễn giải cho ngành hàng')
    p('Lift cao cho biết cùng xuất hiện nhiều hơn so với kỳ vọng nếu hai danh mục độc lập, nhưng không bảo đảm gợi ý đúng hơn các mặt hàng phổ biến. Hit ở ba gợi ý chỉ cần một mục đúng; recall xét phần danh mục ẩn được tìm lại. Bộ test có điều kiện trên giỏ nhiều danh mục và chỉ đo hoàn thiện cùng giỏ, chưa đo mua ở lần tiếp theo hay doanh thu tăng thêm.')
    p('Có thể dùng các quy tắc ổn định làm ứng viên thử trưng bày hoặc combo sau khi ngành hàng kiểm tra tính hợp lý. Cần tránh tạo combo chỉ chuyển doanh số từ món này sang món khác hoặc tặng giảm giá cho giỏ vốn đã mua đủ. Đo tác động bằng thử nghiệm và lợi nhuận sau chi phí nếu có giá vốn.')
    source()

    page('20 Kiến trúc quy trình dữ liệu')
    fig('24_pipeline','Luồng xử lý và kiểm soát của pipeline đã triển khai')
    p('Pipeline hiện chạy local theo một lệnh và tạo mỗi run thành một bộ artifact riêng. Raw được giữ nguyên; enriched Parquet là dữ liệu chuẩn hóa; các bảng KPI, feature, metric và action được lưu CSV; business mart SQLite phục vụ truy vấn; HTML và Word là lớp trình bày. Cấu trúc này giúp đi từ một phát hiện trong báo cáo về bảng số liệu, model và phiên bản đầu vào.')
    p('Báo cáo Word được tạo bởi nhánh phân tích chuyên sâu riêng. Lệnh build_word_report.ps1 điều phối pipeline lõi, phân tích bổ sung và tạo Word; tùy chọn Render xuất ảnh kiểm tra trang. Bản diễn giải này khóa theo dấu kiểm tra của nguồn và mã đã đánh giá. Khi nguồn hoặc model đổi, bước tạo Word dừng để yêu cầu rà soát nhận định trước khi phát hành; pipeline lõi vẫn tạo artifact của lần chạy mới.')
    h('Công bố kết quả sau khi kiểm tra thành công')
    p('Input, code và config được băm để nhận diện phiên bản. Nếu không thay đổi, full run bỏ qua train lại. Một lock ngăn hai full run chồng nhau. Kết quả được viết vào staging, kiểm tra đối soát, reload model và sự tồn tại artifact; sau đó latest.json mới trỏ đến run thành công. Nếu đầu vào hoặc code đổi trong lúc chạy, pipeline từ chối công bố bộ kết quả lẫn phiên bản.')
    p('Lỗi được ghi log và manifest, còn run thành công trước đó vẫn truy cập được qua con trỏ chuẩn. Các shortcut báo cáo latest phục vụ mở nhanh; khi tích hợp hệ thống khác, nên dùng latest.json và manifest thay vì suy đoán theo tên thư mục mới nhất. Model joblib chỉ nạp từ artifact local đáng tin cậy.')
    p('Đã kiểm tra tổng tiền SQL, tái tạo dự báo và điểm rủi ro từ model lưu, reload bốn challenger, lỗi schema không ghi đè latest và giải phóng lock. Đây là kiểm tra chức năng của pipeline; chưa thay thế kiểm thử tải, bảo mật, phục hồi hạ tầng hoặc SLA của một hệ thống doanh nghiệp.')
    source('Code pipeline RUNBOOK và kiểm tra tích hợp D1')

    page('21 Mô hình dữ liệu cho chuỗi')
    fig('25_chain_architecture','Thiết kế mở rộng đề xuất cho dữ liệu POS ERP và WMS của chuỗi')
    p('Đơn vị quyết định vận hành cần đi xuống cửa hàng và SKU, nhưng trước đó phải hợp nhất khóa và định nghĩa giao dịch. POS cung cấp chi tiết hóa đơn; ERP và WMS cung cấp danh mục, giá vốn, mua hàng và kho. Dữ liệu customer cần mã ổn định toàn chuỗi để tránh gắn nhãn giảm mua khi khách chỉ đổi cửa hàng hoặc kênh.')
    table(['Đối tượng','Grain cần quản lý','Kiểm soát quan trọng'],[
      ['Giao dịch bán','Một dòng hóa đơn nguồn','Khóa toàn cục ngày kinh doanh thuế và hoàn hủy'],['Danh mục','SKU và khoảng hiệu lực','Barcode đơn vị quy đổi ngành hàng và mapping mã'],['Cửa hàng','Điểm bán và khoảng hiệu lực','Format khu vực ngày mở đóng và lịch hoạt động'],['Tồn kho','SKU địa điểm ngày hoặc sự kiện','Tồn khả dụng nhập xuất kiểm kê hủy và lô'],['Điều chuyển','Dòng phiếu cùng sự kiện nhận','Nối nơi gửi đang đi và nơi nhận'],['Giá và chương trình','SKU cửa hàng khoảng hiệu lực','Giá đã biết trước ưu đãi chồng và tài trợ']],[3.3,5.2,8.5])
    p('Điều chuyển không được tính là bán hàng. Tồn đầu cộng nhập trừ xuất phải được đối chiếu tồn cuối và điều chỉnh; sai lệch phải có nguyên nhân. Các tổ hợp ngày cửa hàng SKU không có bán cần phân biệt không kinh doanh, đóng cửa, hết hàng và thiếu nguồn. Việc điền 0 toàn bộ các tổ hợp vắng sẽ làm sai cả forecast và kế hoạch bổ sung.')
    source('Thiết kế đề xuất trong CHAIN ROLLOUT và yêu cầu nghiệp vụ của PoC')

    page('22 Vận hành tự động và giám sát')
    p('Đã có hai chế độ: full run để phân tích, đánh giá và refit; score only để dùng model đã công bố tạo dự báo, danh sách CRM và bảng gợi ý mà không train lại. Cả hai đã chạy thành công trên dữ liệu lịch sử. Script Windows Task Scheduler được cung cấp nhưng chưa đăng ký lịch nền; pipeline chưa có adapter nhận POS mới từ doanh nghiệp.')
    table(['Tình huống','Hành vi hiện tại','Bổ sung khi vận hành thật'],[
      ['Nguồn không đổi','Full run bỏ qua theo hash','Theo dõi batch đã chốt và watermark'],['Sai schema hoặc khóa','Dừng và ghi trạng thái lỗi','Người xử lý SLA và kênh cảnh báo'],['Nguồn đến muộn','Chưa tự nhận CDC','Backfill partition và ghi nhận cập nhật'],['Score dữ liệu mới','Dùng model đã lưu giữ vocabulary','Chốt ngày đầy đủ và kiểm tra phiên bản'],['Nhãn chưa hoàn tất','Không dùng để train lịch sử','Nhận nhãn thực tế theo cửa sổ 7 hoặc 28 ngày'],['Thay đổi phân bố','PSI cuối kỳ so kỳ trước','Giám sát theo nhóm và kiểm tra mùa vụ']],[3.4,6.0,7.6])
    h('Drift không đồng nghĩa model hỏng')
    p('PSI của sales theo ngày giữa 28 ngày cuối và 28 ngày trước khoảng 0,154, dưới ngưỡng heuristic 0,2 trong config. Chỉ có 28 quan sát ở mỗi cửa sổ và chưa loại mùa vụ, nên ngưỡng này là cờ rà soát. Cần phân biệt lỗi dữ liệu, thay đổi phân bố đầu vào và suy giảm hiệu năng khi đã có nhãn thực tế.')
    p('Với chuỗi thật, giám sát riêng nguồn cửa hàng chưa chốt, số dòng, tổng tiền, độ trễ, khóa không khớp, ngày vắng và tỷ lệ score được. Retrain theo lịch hoặc drift chỉ nên diễn ra cùng kiểm tra nhãn đã chín và đánh giá champion challenger. Không tự gửi khách, đổi giá hoặc đặt hàng chỉ vì một file score đã xuất thành công.')
    source('monitoring.json và các lệnh vận hành đã kiểm tra trong D1')

    page('23 Thiết kế thử nghiệm kinh doanh')
    h('Tách độ chính xác dự báo khỏi tác động của hành động')
    p('Model khách hàng có thể tìm đúng nhóm không mua nhưng không biết ưu đãi nào sẽ thay đổi hành vi. Forecast có thể giảm sai số mà vẫn chưa giảm hết hàng nếu quy trình đặt hàng hoặc lead time không đổi. Mỗi PoC cần xác định rõ đơn vị can thiệp, baseline nghiệp vụ, chỉ tiêu chính và tiêu chí không được xấu đi trước khi triển khai.')
    table(['Bài toán','Đơn vị thử nghiệm đề xuất','Chỉ tiêu chính','Điều cần kiểm soát'],[
      ['CRM','Hộ đủ điều kiện ở cùng kỳ','Mua lại và lãi tăng thêm sau chi phí','Đối chứng cùng nhóm rủi ro và không gửi chồng'],['Combo hoặc trưng bày','Cửa hàng hoặc cụm tương đồng','Giá trị hoặc lãi giỏ tăng thêm','Khách mua xuyên cửa hàng và thay thế SKU'],['Khuyến mãi','SKU cửa hàng thời gian','Lãi tăng thêm và lượng bán','Tài trợ mua sớm cannibalization và tồn'],['Dự báo cho bổ sung','Cửa hàng SKU trong phạm vi PoC','WAPE bias cùng fill rate khi đủ tồn','Quy tắc đặt hàng MOQ và lead time']],[3.1,4.4,4.7,4.8])
    h('Cỡ mẫu và thời gian quan sát')
    p('Chưa có baseline đầy đủ về biến thiên lợi nhuận, tương quan trong cửa hàng, mức tác động tối thiểu cần phát hiện và tỷ lệ phản hồi, nên báo cáo không đưa cỡ mẫu bảo đảm. Cần ước lượng các thành phần này từ dữ liệu doanh nghiệp. Với can thiệp theo cửa hàng, không coi hàng nghìn dòng hóa đơn trong cùng cửa hàng là hàng nghìn đơn vị độc lập.')
    p('Chọn trước chỉ tiêu và thời gian thử, lưu assignment, xử lý trường hợp không nhận can thiệp và báo độ phủ dữ liệu. Không kết thúc thử nghiệm chỉ khi thấy một kết quả thuận lợi. Theo dõi cả tác động sau chương trình để phát hiện mua sớm hoặc chuyển doanh số giữa các sản phẩm và điểm bán.')
    h('Điều kiện để chuyển từ PoC sang vận hành')
    p('Kết quả cần đồng thời đáp ứng chất lượng số liệu, cải thiện so baseline nghiệp vụ và tính khả thi của hành động. Người sở hữu nghiệp vụ phải chấp nhận công suất xử lý, các trường hợp ngoại lệ và cách khôi phục khi nguồn lỗi. Báo cáo offline chỉ là một phần bằng chứng trong quyết định này.')
    source('Đề xuất thiết kế áp dụng cho chuỗi và giới hạn của kết quả D1 D2')

    page('24 Lộ trình PoC và điều kiện nghiệm thu')
    fig('26_poc','Trình tự triển khai đề xuất khi có dữ liệu doanh nghiệp')
    p('Nên bắt đầu với 5 đến 10 cửa hàng có format và khu vực khác nhau cùng một nhóm hàng dữ liệu tốt. Đây là phạm vi khởi đầu để thảo luận, không phải số cửa hàng đã được khảo sát hoặc cỡ mẫu thống kê đã tính. Trước hết nhận 2 đến 4 tuần mẫu kèm tổng đối soát; sau khi cấu trúc đạt, lấy lịch sử liên tục 12 đến 24 tháng hoặc nhiều hơn khi cần mùa vụ năm.')
    table(['Giai đoạn','Sản phẩm nghiệm thu','Điều kiện chuyển bước'],[
      ['Khảo sát','Bản đồ nguồn và định nghĩa KPI','Có data owner cùng khóa và grain rõ'],['Chuẩn hóa','Mapping cùng bảng đối soát','Chênh lệch được giải thích và có ngưỡng duyệt'],['Phân tích','Dashboard và danh sách vấn đề','KPI khớp nguồn kiểm chứng được'],['Mô hình','Backtest và model card','Giữ test riêng và vượt baseline phù hợp'],['Thử nghiệp vụ','Kết quả đối chứng và chi phí','Đạt mục tiêu thống nhất trước thử'],['Vận hành','Lịch batch cùng giám sát và rollback','Có chủ xử lý lỗi và SLA']],[3.5,6.4,7.1])
    p('Ưu tiên đầu tiên là đối soát doanh thu và mapping danh mục vì hai việc này làm nền cho mọi mô hình. CRM có thể là PoC tiếp theo nếu ID toàn chuỗi ổn định. Forecast và bổ sung hàng cần tách thành hai tầng: dự đoán lượng bán rồi dùng ràng buộc kho để tính hành động. Không đặt một ngưỡng WAPE chung cho mọi ngành hoặc mọi cửa hàng.')
    source('Lộ trình đề xuất cho chuỗi bán lẻ')

    page('25 Hiệu quả kinh tế và quản trị rủi ro')
    h('Cách lập business case khi có dữ liệu doanh nghiệp')
    p('Đối với CRM, tính số khách đủ điều kiện, số khách được chọn, tỷ lệ được liên hệ, tác động tăng thêm so với đối chứng, lãi gộp từ mua tăng thêm và toàn bộ chi phí. Precision của model không được nhân trực tiếp với giá trị giỏ để gọi là lợi ích, vì nhiều khách vẫn có thể quay lại mà không cần can thiệp và nhiều khách rủi ro có thể không phản hồi.')
    p('Đối với forecast, tách tiết kiệm thời gian lập kế hoạch khỏi tác động tồn kho. Lợi ích giảm thiếu hàng hoặc hủy hàng chỉ đo được khi có tồn, đơn vị, giá vốn, hạn dùng, thời gian giao và quy tắc đặt hàng. Chi phí dự án gồm tích hợp nguồn, xử lý ngoại lệ, vận hành pipeline, bảo trì mapping, đánh giá lại và công việc phát sinh tại cửa hàng. Chưa có đủ dữ liệu để đưa ROI bằng tiền cho chuỗi cụ thể.')
    table(['Rủi ro','Dấu hiệu nhận biết','Cách kiểm soát'],[
      ['Dữ liệu rời rạc','SKU hoặc ngày kinh doanh không khớp','Mapping có hiệu lực và đối soát theo cửa hàng'],['Thiếu nguồn thành số 0','Cửa hàng đột ngột không có bản ghi','Batch status và lịch mở cửa xác minh được'],['Sai ý nghĩa target','Giá trị bán bị hiểu thành lợi nhuận hoặc lượng','Chốt định nghĩa và phân loại hàng dịch vụ'],['Sai lệch mẫu','Loyalty hoặc panel không phủ khách vãng lai','Báo độ phủ và đánh giá theo nhóm'],['Leakage hoặc chọn theo test','Metric cao bất thường hoặc sửa test nhiều lần','Đóng băng split và version model'],['Hành động bất lợi','Ưu đãi tốn tiền nhưng không tăng mua','Đối chứng phê duyệt và theo dõi chi phí']],[3.6,5.8,7.6])
    h('Quyền truy cập và trách nhiệm')
    p('ID khách nên được ẩn danh và mapping định danh được quản lý ở hệ thống có quyền phù hợp. Chỉ cấp dữ liệu chi tiết cho người cần dùng; báo cáo cấp vùng hoặc cửa hàng phải có phạm vi rõ. Lưu lịch sử model, người duyệt và hành động để truy vết. Việc đánh giá dữ liệu cá nhân và nghĩa vụ pháp lý cụ thể cần được bộ phận có thẩm quyền của doanh nghiệp xem xét khi triển khai.')
    source('Đề xuất vận hành và các khoảng trống dữ liệu đã xác định')

    page('26 Hồ sơ mô hình và tái lập')
    table(['Thuộc tính','Dự báo bán','Khách hàng','Gợi ý giỏ hàng'],[
      ['Target','Sales_value 7 ngày theo nhóm','Không mua dương trong 28 ngày','Hoàn thiện danh mục bị che trong cùng giỏ'],['Champion','Trung bình 28 ngày','Histogram gradient boosting','Popularity'],['Chọn bằng','WAPE validation ba origin','AP snapshot validation','Hit ở ba gợi ý validation'],['Test','Bốn tuần cuối năm','Hai snapshot tương lai','91 ngày cuối kỳ'],['Đầu ra','Forecast và dải heuristic','Score cùng cờ top 20%','Ba danh mục khác seed'],['Giới hạn chính','Một năm và panel thiếu bối cảnh','Chưa đo đáp ứng can thiệp','Test có điều kiện trên giỏ nhiều mục']],[3.2,4.6,4.6,4.6])
    h('Artifact và phiên bản')
    p('Run dùng trong báo cáo là '+RUN.name+'. Manifest lưu checksum đầu vào, config và phiên bản thư viện. Môi trường thực hiện dùng Python 3.12, pandas 2.2.3, scikit learn 1.6.1 và các thư viện ghi trong requirements. Bốn challenger dự báo được refit và giữ riêng phục vụ kiểm tra; không tự phục vụ chúng thay champion.')
    h('Cách chạy lại và kiểm tra')
    p('Tại thư mục dự án, chạy run_pipeline.ps1 để thực hiện toàn bộ. Chạy run_pipeline.ps1 với Mode score và AsOf 2017-12-31 để kiểm tra score độc lập trên kỳ hiện tại. Khi thay dữ liệu, chốt lại analysis_end và bảo đảm ngày cuối đã đầy đủ; không để dữ liệu lịch sử tự lấy ngày hệ thống hiện tại làm origin.')
    p('Chín kiểm tra logic bao gồm target đúng bảy ngày, feature không phụ thuộc tương lai, vocabulary cố định, cửa sổ nhãn ngày 28 và 29, loại hộ ngoài eligibility, cách tính metric và gợi ý không trùng seed. Kiểm tra tích hợp xác nhận SQL khớp tiền, model reload và score tái tạo được, lỗi schema giữ latest và giải phóng lock. Chưa có kiểm thử tải hoặc hạ tầng production.')
    p('Phân tích bổ sung D2 có script riêng, lấy run thành công làm đầu vào, xuất bảng bằng chứng và hình cho Word. Kết quả test đã có không được dùng để chọn lại champion. Việc phát hiện taxonomy bất thường được ghi thành yêu cầu cải tiến tiếp theo thay vì âm thầm sửa đầu vào của kết quả cũ.')
    p('Để tạo lại báo cáo Word theo quy trình đã đóng gói, chạy build_word_report.ps1 với tùy chọn Render. Lệnh dừng khi bước trước thất bại. Phiên bản diễn giải này gắn với kỳ public năm 2017; khi đổi nguồn hoặc kỳ phải rà soát lại nhận định và phạm vi trước khi phát hành.')
    source('Manifest code và kết quả kiểm tra chức năng D1 D2')

    page('27 Từ điển chỉ tiêu và dữ liệu cần xin')
    table(['Chỉ tiêu','Cách hiểu trong báo cáo','Giới hạn'],[
      ['Sales_value','Khoản nhà bán lẻ nhận theo nguồn','Không phải lãi hay mọi khoản khách trả'],['AOV','Sales chia số giỏ trong cùng kỳ','Giỏ phải có khóa đúng toàn hệ thống'],['Recency','Số ngày từ lần mua dương cuối','Phải tính ở đúng origin'],['WAPE','Tổng sai số tuyệt đối chia tổng thực tế','Nhóm lớn có trọng số cao'],['Bias','Tổng dự báo trừ thực tế chia tổng thực tế','Dương là dự báo cao hơn thực tế'],['AP','Average precision từ điểm xếp hạng','Đọc cùng prevalence và công suất'],['Precision top 20','Tỷ lệ nhãn dương trong 20% được chọn','Chưa phải tỷ lệ phản hồi ưu đãi'],['Recall top 20','Phần nhãn dương được tìm trong top 20','Cần đọc cùng số hộ và precision'],['Lift khách hàng','Precision của nhóm chọn chia prevalence','Khác lift liên kết giỏ hàng'],['Lift giỏ hàng','Support cùng mua chia tích support riêng','Không phải tác động nhân quả'],['Coverage dự báo','Tỷ lệ thực tế nằm trong dải dự báo','Dải hiện tại chỉ là heuristic'],['PSI','Chênh phân bố giữa hai cửa sổ','Cờ điều tra chưa là model degradation']],[3.5,7.2,6.3])
    h('Yêu cầu dữ liệu theo thứ tự ưu tiên')
    p('Gói đầu gồm POS chi tiết, products, stores, lịch mở cửa, mapping mã và tổng đối soát kế toán. Gói CRM bổ sung ID khách toàn chuỗi, ngày gia nhập và lịch tương tác. Gói forecast bổ sung assortment hiệu lực, giá, khuyến mãi đã biết trước, tình trạng hết hàng và đủ lịch sử. Gói tồn kho cần nhập xuất tồn, điều chuyển, PO, nhận hàng, lead time, MOQ, case pack, lô và hạn dùng. Gói lợi nhuận cần giá vốn hiệu lực, chi phí, tài trợ và quy tắc phân bổ.')
    p('Mỗi nguồn cần người sở hữu, vị trí hệ thống, grain, khóa, khoảng lịch sử, chu kỳ cập nhật, múi giờ và độ trễ. Xin 20 đến 100 dòng mẫu có ẩn danh cùng data dictionary trước khi trích xuất toàn bộ. Thống nhất định dạng và cách xử lý thay đổi lịch sử để tránh mỗi phòng cung cấp một định nghĩa khác nhau.')
    source('Định nghĩa nguồn [2] metric [6] và hợp đồng dữ liệu trong RUNBOOK')

    page('28 Nguồn tham khảo')
    refs=[
      ('D1','Bộ artifact tính toán chính',RUN.name+'; latest.json xác định run dùng để đối soát. Bao gồm quality, analytics, metrics, feature, score và model registry.'),
      ('D2','Phân tích chuyên sâu bổ sung','research/deep_analysis.py và outputs/word_report/deep_summary.json; có bảng tăng trưởng ngành, mua xuyên cửa hàng, taxonomy, bootstrap và hình minh họa.'),
      ('1','Complete Journey package','https://bradleyboehmke.github.io/completejourney/'),
      ('2','Complete Journey User Guide','https://bradleyboehmke.github.io/completejourney/articles/completejourney.html'),
      ('3','UCI Online Retail','https://archive.ics.uci.edu/dataset/352/online+retail'),
      ('4','Forecasting Principles and Practice','https://otexts.com/fpp3/tscv.html ; https://otexts.com/fpp3/hierarchical-forecasting.html'),
      ('5','NIST Confidence intervals for proportions','https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm'),
      ('6','Scikit learn Metrics and scoring','https://scikit-learn.org/stable/modules/model_evaluation.html'),
      ('7','SciPy Bootstrap reference','https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html'),
      ('8','Favorita Grocery Sales Forecasting','https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/data'),
      ('9','dunnhumby Source Files','https://www.dunnhumby.com/source-files/'),
    ]
    for key,title,url in refs:
        p(f'[{key}] {title}',True);pp=p(url)
        for rr in pp.runs:rr.font.size=Pt(9)
    p('Complete Journey package ghi CC0 trong DESCRIPTION; ghi công nguồn 84.51° và người duy trì Brad Boehmke cùng Steven M Mortimer. UCI Online Retail của Daqing Chen năm 2015 có DOI 10.24432/C5BW33 và giấy phép CC BY 4.0. Các bộ Favorita và dunnhumby khác được nêu như nguồn khảo sát, chưa được dùng để train trong kết quả báo cáo này.')
    p('Bootstrap D2 được thực hiện bằng lấy mẫu cụm hộ với NumPy; tài liệu SciPy được viện dẫn cho khái niệm bootstrap, không khẳng định đã gọi trực tiếp scipy.stats.bootstrap. Nguồn phương pháp giải thích metric và cách đánh giá, còn các kết quả định lượng trong báo cáo được tính từ D1 và D2.')

    page('29 Phụ lục sai số dự báo chi tiết')
    p('Bảng dưới là kết quả champion trung bình 28 ngày trên bốn origin test. WAPE và bias tính theo từng nhóm trên bốn tuần; MAE có đơn vị USD mỗi nhóm mỗi cửa sổ bảy ngày. Bảng không phải forecast SKU hoặc cửa hàng và chưa phản ánh mức thiếu hàng thực tế.')
    data=read('forecast_series_metrics').sort_values('WAPE',ascending=False)
    table(['Nhóm trong mô hình','WAPE','Bias','MAE USD'],[[r.series,pct(r.WAPE),pct(r.bias),num(r.MAE,2)] for r in data.itertuples()],[8.3,2.8,2.8,3.1])
    p('Nhóm OTHER đóng góp lớn vào tổng tiền và tổng sai số, trong khi nhóm như CANDY PACKAGED có WAPE cao. Khi triển khai ở chuỗi, nên phân nhóm đánh giá theo mức bán, ngành, cửa hàng và vòng đời SKU. Cần công bố số quan sát và độ phủ nguồn cùng từng metric, nhất là nhóm mới hoặc bán thưa.')
    source()

    page('30 Thuật ngữ chuyên môn')
    p('Các thuật ngữ dưới đây được giữ trong báo cáo để khớp tên trường và tài liệu mô hình. Phần giải thích tiếng Việt xác định cách hiểu trong nghiên cứu này.')
    table(['Thuật ngữ','Giải thích tiếng Việt'],[
      ['Panel','Nhóm hộ được theo dõi trong dữ liệu chứ không phải toàn bộ khách của chuỗi'],['SKU','Mã quản lý một mặt hàng hoặc quy cách hàng hóa'],['PoC','Thử nghiệm phạm vi nhỏ để kiểm chứng khả năng và giá trị trước triển khai'],['RFM','Nhìn khách qua độ gần của lần mua cuối tần suất và giá trị mua'],['Recency','Số ngày kể từ lần mua dương gần nhất tại mốc đang xét'],['Baseline','Phương án tham chiếu thường đơn giản để kiểm tra model mới có cải thiện hay không'],['Champion và challenger','Mô hình được chọn để sử dụng và các mô hình ứng viên đem so sánh'],['Train validation test','Tập huấn luyện tập xác thực để chọn model và tập kiểm tra giữ riêng'],['Origin và snapshot','Mốc bắt đầu dự báo hoặc thời điểm chụp lịch sử để chấm điểm khách'],['Feature và target','Đặc trưng đầu vào và đại lượng hoặc nhãn model cần dự đoán'],['Leakage','Dùng thông tin chưa có tại thời điểm quyết định làm kết quả đánh giá quá lạc quan'],['Score và calibration','Điểm dự báo và kiểm tra mức phù hợp của điểm với tỷ lệ thực tế'],['Prevalence','Tỷ lệ nhãn dương trong toàn bộ nhóm đang đánh giá'],['Bootstrap','Lấy mẫu lại để mô tả độ bất định của một thống kê'],['Grain và mapping','Đơn vị mỗi dòng dữ liệu và ánh xạ mã giữa các hệ thống'],['Watermark và backfill','Mốc dữ liệu đã xử lý và việc nạp bù hoặc tính lại lịch sử'],['Lead time và MOQ','Thời gian từ đặt tới nhận hàng và lượng đặt tối thiểu'],['Case pack và assortment','Quy cách đóng thùng và danh mục được kinh doanh tại từng cửa hàng'],['Cannibalization','Một sản phẩm hoặc điểm bán tăng nhưng lấy bớt doanh số của nơi khác'],['Uplift và ROI','Tác động tăng thêm do can thiệp và hiệu quả sau chi phí cần đo riêng']],[4.6,12.4])
    p('Tên model và mã ngành trong bảng kết quả giữ nguyên để đối chiếu artifact. Các chữ viết tắt POS ERP WMS CRM lần lượt chỉ hệ thống bán hàng quản trị nguồn lực quản lý kho và quản lý quan hệ khách hàng.')

    target=OUT/'Bao_cao_chuyen_sau_chuoi_sieu_thi.docx';doc.save(target)
    (OUT/'document_structure.json').write_text(json.dumps({'expected_pages':33,'sections':PAGES,'figures':FIGURES,'run_id':RUN.name,'path':str(target)},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'docx':str(target),'figures':len(FIGURES),'planned_pages':33}))

if __name__=='__main__':build()
