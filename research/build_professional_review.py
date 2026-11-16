from pathlib import Path
import re,json,csv,hashlib,sys
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/professional_review';OUT.mkdir(exist_ok=True)
source=ROOT/'research/dashboard_professional_review.md'
content=source.read_text(encoding='utf-8').replace('Ngày tổng hợp 01 tháng 11 năm 2026.','Ngày tổng hợp 02 tháng 11 năm 2026.')
source.write_text(content,encoding='utf-8');(OUT/'Danh_gia_dashboard_DA_DE.md').write_text(content,encoding='utf-8')
items=[
('P0','DA và sponsor','Decision brief hai vai trò','Mỗi quyết định có owner, nhịp xem, lựa chọn hành động, chi phí sai và outcome đo lại.','Phỏng vấn đại diện hai vai trò','S01 S02'),
('P0','DA và Tài chính','Metric catalog có phiên bản','Mỗi KPI có công thức, grain, filter, đơn vị, kỳ, nguồn và người xác nhận; không lẫn raw và positive.','Định nghĩa doanh nghiệp','S07 S08'),
('P0','DE và chủ nguồn','Data contract POS và master','Khóa dòng ổn định, khóa giỏ toàn cục, timezone, UOM, currency, correction và coverage được chốt.','Quyền lấy nguồn','S07 S09'),
('P0','DE và Tài chính','Control totals từ nguồn','Đối soát dòng và tổng tiền với nguồn ngoài file; mọi chênh lệch có lý do hoặc chặn publish.','POS hoặc sổ đối soát','S09'),
('P0','DA và DE','Grain và cardinality khi join','Test chứng minh không nhân dòng khi nối SKU, cost, campaign; distinct count không bị cộng sai.','Khóa và lịch hiệu lực','S07'),
('P0','Vận hành và DE','Lịch nguồn và missing zero','Ngày thiếu bản ghi được xác minh bằng lịch/heartbeat; unknown không chuyển thành zero tự động.','Lịch cửa hàng và lịch ingest','S09'),
('P0','DA và Tài chính','Giới hạn thông tin tài chính','Chưa có cost/OPEX thì metric lãi ghi chưa có actual; kịch bản có nhãn và scope nhất quán.','Cost và chính sách kế toán','S16 S17'),
('P0','Frontend và DA','Contrast chữ và khả năng đọc','Computed styles của chữ thường đạt ngưỡng áp dụng WCAG AA; kiểm tra trạng thái enabled/disabled riêng.','Audit giao diện thực tế','S11'),
('P1','DE và Backend','Batch store và watermark bền vững','Đóng tab/restart worker không mất batch hoặc watermark; chỉ advance sau commit thành công.','Storage riêng tư và database','S10'),
('P1','DE','Retry backfill và crash recovery','Chạy lại không nhân giao dịch; crash giữa job không công bố kết quả dở dang; backfill tái tạo đúng version.','Batch store','S10'),
('P1','Backend và người phụ trách quyền','Danh tính và quyền theo vai trò','Có hai tài khoản thử riêng; API và export tuân scope; đổi select UI không mở rộng quyền.','Hệ thống xác thực','S06 S15'),
('P1','DA và DE','Lineage đến KPI và score','Từ một giá trị truy được batch, mapping, code, metric và model version.','Metadata store','S08 S14'),
('P1','DE và Vận hành','Incident và data observability','Có owner và hướng xử lý cho freshness, completeness, duplicate, mismatch; diễn tập một incident.','Lịch nguồn và người trực','S09'),
('P1','DS và DE','Label table theo as of và horizon','Chỉ đánh giá target đã chín; khóa khách/as-of/horizon rõ; không nhập tương lai vào feature.','Dữ liệu 28 và 56 ngày về sau','S12 S14'),
('P1','DS và DA','Calibration trên nguồn doanh nghiệp','Có reliability theo cohort, support từng bin, Brier/log loss và baseline trên dữ liệu ngoài thời gian.','Label table đủ dữ liệu','S12'),
('P1','Backend và Vận hành','Decision ledger bền vững','Lưu người quyết định, lý do, hạn, version score, hành động và outcome; giữ lịch sử sửa trạng thái.','Database và quy trình owner','S01 S15'),
('P1','DE và người phụ trách bảo mật','Chính sách file dữ liệu thật','Có thời hạn giữ, xóa, kiểm soát tải xuống và kiểm thử phục hồi; raw nhạy cảm không nhúng trong HTML.','Phân loại dữ liệu và hạ tầng','S06'),
('P2','DA và người dùng','Usability theo nhiệm vụ','Đại diện từng vai trò hoàn thành nhiệm vụ đã chốt; ghi thời gian, lỗi hiểu và câu hỏi cần trợ giúp.','Prototype và người tham gia','S01 S03'),
('P2','Frontend','Bàn phím zoom và biểu đồ thay thế','Dùng được bằng bàn phím, focus rõ, có nội dung thay thế cần thiết và tín hiệu ngoài màu sắc.','Audit accessibility','S11'),
('P2','Frontend và Backend','Latency và tải dữ liệu','Có p50 p95 trên thiết bị/mạng/dataset đại diện; ngân sách hiệu năng được nhóm phê duyệt trước tối ưu.','API và bộ đo hiệu năng','S02'),
('P2','CRM và DS','Pilot giữ chân có đối chứng','Chốt đơn vị randomization, power, outcome, guardrail và kiểm tra chất lượng thí nghiệm trước khi mở kết quả.','Consent, chi phí và label','S13'),
('P2','Tài chính và Sponsor','Đánh giá hiệu quả tăng thêm','Đối chiếu contribution tăng thêm với tổng chi phí không double count; ghi uncertainty và điều kiện dừng.','Thử nghiệm và cost đã xác nhận','S13 S16'),
('P2','Sponsor và DA','Theo dõi adoption và rà soát danh mục','Đo task completion và quyết định có outcome; rà lại màn hình ít dùng hoặc metric không còn phục vụ quyết định.','Decision ledger và usage telemetry','S01 S05'),
]
backlog=[]
for i,(priority,owner,deliverable,acceptance,dependency,refs) in enumerate(items,1):backlog.append({'id':f'UPG-{i:02d}','priority':priority,'owner_de_xuat':owner,'deliverable':deliverable,'acceptance':acceptance,'dependency':dependency,'sources':refs,'status':'Đề xuất chưa triển khai'})
with (OUT/'Backlog_nang_cap.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(backlog[0]));w.writeheader();w.writerows(backlog)
(OUT/'Backlog_nang_cap.json').write_text(json.dumps(backlog,ensure_ascii=False,indent=2),encoding='utf-8')

plt.rcParams['font.family']='Arial'
fig,ax=plt.subplots(figsize=(10,4.3));ax.set_xlim(0,10);ax.set_ylim(0,4.3);ax.axis('off')
labels=['Câu hỏi và\nhành động','Định nghĩa\nchỉ tiêu','Nguồn được\nđối soát','Phân tích\nvà model','Giao diện\ntheo vai trò','Quyết định\ncó owner','Ghi nhận\nkết quả','Đánh giá\nvà cải tiến']
positions=[(.15,2.6),(2.65,2.6),(5.15,2.6),(7.65,2.6),(7.65,.65),(5.15,.65),(2.65,.65),(.15,.65)]
for i,((x,y),label) in enumerate(zip(positions,labels)):
 ax.add_patch(FancyBboxPatch((x,y),2.15,1.12,boxstyle='round,pad=.03,rounding_size=.08',facecolor='#edf3ef',edgecolor='#9aafa2',linewidth=1))
 ax.text(x+.15,y+.88,f'{i+1:02d}',fontsize=11,color='#51705e');ax.text(x+1.08,y+.43,label,ha='center',va='center',fontsize=13,color='#1e382b',linespacing=1.4)
for i in range(7):
 x,y=positions[i];xx,yy=positions[i+1]
 if i<3:a=(x+2.2,y+.55);b=(xx-.08,yy+.55)
 elif i==3:a=(x+1.08,y-.08);b=(xx+1.08,yy+1.2)
 else:a=(x-.08,y+.55);b=(xx+2.23,yy+.55)
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,color='#6a8173',linewidth=1.2))
fig.savefig(OUT/'Quy_trinh_san_pham_du_lieu.png',dpi=220,bbox_inches='tight',facecolor='white');plt.close(fig)

doc=Document();section=doc.sections[0];section.page_width=Inches(8.5);section.page_height=Inches(11);section.top_margin=Inches(.78);section.bottom_margin=Inches(.72);section.left_margin=Inches(.82);section.right_margin=Inches(.82)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
 st=doc.styles[name];st.font.name='Arial';st.font.color.rgb=RGBColor(0,0,0);st.element.rPr.rFonts.set(qn('w:eastAsia'),'Arial')
doc.styles['Normal'].font.size=Pt(11);doc.styles['Normal'].paragraph_format.space_after=Pt(7);doc.styles['Normal'].paragraph_format.line_spacing=1.14
doc.styles['Title'].font.size=Pt(26);doc.styles['Title'].paragraph_format.space_after=Pt(14)
doc.styles['Heading 1'].font.size=Pt(17);doc.styles['Heading 1'].paragraph_format.space_before=Pt(17);doc.styles['Heading 1'].paragraph_format.space_after=Pt(8)
doc.styles['Heading 2'].font.size=Pt(13)
for name in ['Title','Subtitle','Heading 1','Heading 2','Heading 3']:
 ppr=doc.styles[name].element.pPr
 if ppr is not None:
  for border in ppr.findall(qn('w:pBdr')):ppr.remove(border)
header=section.header.paragraphs[0];header.text='RETAIL INTELLIGENCE   |   ĐÁNH GIÁ THỰC HÀNH DA VÀ DE';header.runs[0].font.size=Pt(8);header.runs[0].font.color.rgb=RGBColor(0,0,0)
footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT;footer.add_run('Trang ').font.size=Pt(9);field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
urls={m.group(1):m.group(2) for m in re.finditer(r'^\[(S\d+)\].*?(https://\S+)',content,re.M)}
def hyperlink(p,label,url):
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True));run=OxmlElement('w:r');rpr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'205B76');rpr.append(color);run.append(rpr);text=OxmlElement('w:t');text.text=label;run.append(text);h.append(run);p._p.append(h)
def rich(p,text):
 for token in re.split(r'(\*\*.*?\*\*|\[S\d+\])',text):
  if token.startswith('**'):p.add_run(token[2:-2]).bold=True
  elif re.fullmatch(r'\[S\d+\]',token):hyperlink(p,token,urls.get(token[1:-1],''))
  else:p.add_run(token)
def table(headers,rows,widths):
 t=doc.add_table(rows=1,cols=len(headers));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for col,width in zip(t.columns,widths):col.width=Inches(width)
 for c,h in zip(t.rows[0].cells,headers):c.text=h
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  for cell,value in zip(t.add_row().cells,row):cell.text=str(value)
 for i,row in enumerate(t.rows):
  for j,c in enumerate(row.cells):
   c.width=Inches(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;pr=c._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   pr.append(borders);margins=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');margins.append(e)
   pr.append(margins);shading=OxmlElement('w:shd');shading.set(qn('w:fill'),'274B5A' if i==0 else ('F1F5F7' if i%2 else 'FFFFFF'));pr.append(shading)
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.08
    for r in p.runs:r.font.size=Pt(9.5);r.font.color.rgb=RGBColor(255,255,255) if i==0 else RGBColor(0,0,0);r.bold=i==0
 doc.add_paragraph().paragraph_format.space_after=Pt(2)
 return t
for line in content.splitlines():
 if not line.strip():continue
 if line.startswith('# '):
  doc.add_paragraph(line[2:],style='Title');doc.add_paragraph('Thực hành DA DE và lộ trình nâng cấp',style='Subtitle')
 elif line.startswith('## '):
  if line.startswith('## 12 '):
   doc.add_heading('12 Danh mục nâng cấp ưu tiên',1)
   doc.add_paragraph('Backlog CSV kèm theo có 23 hạng mục, owner đề xuất, phụ thuộc, tiêu chí nghiệm thu và nguồn. Các trạng thái đều là đề xuất chưa triển khai. Bảng dưới nêu một số hạng mục cần chốt trước khi mở rộng.')
   short=[(r['id'],r['priority'],r['deliverable'],r['owner_de_xuat']) for r in backlog[:8]];table(['Mã','Ưu tiên','Đầu ra','Owner đề xuất'],short,[.65,.55,3.4,2.26])
   doc.add_heading('13 Nguồn tham khảo đã đối chiếu',1)
  else:doc.add_heading(line[3:],1)
 elif re.match(r'^\[S\d+\]',line):
  match=re.search(r'https://\S+',line);p=doc.add_paragraph();rich(p,line[:match.start()].strip()+' ');hyperlink(p,'Mở nguồn gốc',match.group(0))
 else:
  p=doc.add_paragraph();rich(p,line)
  if line.startswith('Kiến trúc đề xuất là'):
   pic=doc.add_paragraph();pic.alignment=WD_ALIGN_PARAGRAPH.CENTER;pic.add_run().add_picture(str(OUT/'Quy_trinh_san_pham_du_lieu.png'),width=Inches(6.65));pic.paragraph_format.keep_with_next=True
   cap=doc.add_paragraph('Hình 1  Quy trình đề xuất từ câu hỏi kinh doanh đến đánh giá kết quả');cap.runs[0].italic=True;cap.runs[0].font.size=Pt(9)
doc.core_properties.title='Đánh giá và lộ trình nâng cấp dashboard bán lẻ';doc.core_properties.subject='Nghiên cứu nguồn và đánh giá thực hành DA DE';doc.core_properties.author='Retail Intelligence'
path=OUT/'Danh_gia_va_lo_trinh_dashboard_DA_DE.docx';doc.save(path)
manifest={'file':str(path),'backlog_count':len(backlog),'sources':len(urls),'words_whitespace':len(content.split()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Research and proposed upgrades; no live dashboard changes performed.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(manifest,ensure_ascii=True))
