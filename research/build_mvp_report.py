"""Build the final bilingual MVP proposal (Word): analysis, website, models, architecture and delivery plan."""
from pathlib import Path
import json, math
from PIL import Image
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/website_report'
SHOTS = OUT / '_build/shots'
CROPS = OUT / '_build/crops'
CROPS.mkdir(exist_ok=True)
RUN = Path(json.loads((ROOT / 'outputs/enterprise/latest.json').read_text(encoding='utf-8'))['path'])
INS = json.loads((ROOT / 'dashboard_enterprise/insights.json').read_text(encoding='utf-8'))
FC = json.loads((RUN / 'forecast_summary.json').read_text(encoding='utf-8'))
RK = json.loads((RUN / 'risk_summary.json').read_text(encoding='utf-8'))
AS = json.loads((RUN / 'association_metrics.json').read_text(encoding='utf-8'))
AN = json.loads((RUN / 'analytics_summary.json').read_text(encoding='utf-8'))
REG = json.loads((ROOT / 'dashboard_enterprise/probability_registry.json').read_text(encoding='utf-8'))
SEG = pd.read_csv(RUN / 'segment_summary.csv')

NAVY, TEAL, AMBER, GRAY = RGBColor(0x10, 0x24, 0x3D), RGBColor(0x0F, 0x7C, 0x78), RGBColor(0xD1, 0x9A, 0x2B), RGBColor(0x6C, 0x7C, 0x8F)
LANG = 'vi'


def T(vi, en):
    return en if LANG == 'en' else vi


def fmt(v, d=0):
    from decimal import Decimal, ROUND_HALF_UP
    v = float(Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))
    s = f'{v:,.{d}f}'
    return s if LANG == 'en' else s.replace(',', 'X').replace('.', ',').replace('X', '.')


def pct(v, d=1):
    return fmt(v * 100, d) + '%'


g, c, b, st, br = INS['gross_to_net'], INS['customers'], INS['basket'], INS['stores'], INS['brand']
disc = g['gross'] - g['net']


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)


def borders(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr()
    tb = tcPr.find(qn('w:tcBorders'))
    if tb is None:
        tb = OxmlElement('w:tcBorders')
        tcPr.append(tb)
    for edge in ('top', 'left', 'bottom', 'right'):
        spec = kw.get(edge)
        el = OxmlElement(f'w:{edge}')
        if spec:
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), str(spec[0]))
            el.set(qn('w:color'), spec[1])
        else:
            el.set(qn('w:val'), 'nil')
        tb.append(el)


def margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    m = OxmlElement('w:tcMar')
    for k, v in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        e = OxmlElement(f'w:{k}')
        e.set(qn('w:w'), str(v))
        e.set(qn('w:type'), 'dxa')
        m.append(e)
    tcPr.append(m)


def build(lang):
    global LANG
    LANG = lang
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.8)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.different_first_page_header_footer = True
    st_ = doc.styles
    for name in ['Normal', 'Heading 1', 'Heading 2', 'Heading 3', 'Caption', 'List Bullet', 'Title']:
        s = st_[name]
        s.font.name = 'Calibri'
        s._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Calibri')
    st_['Normal'].font.size = Pt(10.5)
    st_['Normal'].font.color.rgb = RGBColor(0x2B, 0x3A, 0x4D)
    st_['Normal'].paragraph_format.line_spacing = 1.2
    st_['Normal'].paragraph_format.space_after = Pt(6)
    for name, size, before in (('Heading 1', 20, 0), ('Heading 2', 14, 14), ('Heading 3', 11.5, 10)):
        h = st_[name]
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = NAVY if name != 'Heading 3' else TEAL
        h.paragraph_format.space_before = Pt(before)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
    st_['Caption'].font.size = Pt(8.5)
    st_['Caption'].font.italic = True
    st_['Caption'].font.color.rgb = GRAY
    st_['List Bullet'].paragraph_format.space_after = Pt(3)
    doc.core_properties.title = T('Retail Intelligence – Đề xuất MVP', 'Retail Intelligence – MVP Proposal')
    doc.core_properties.author = ''

    hp = sec.header.paragraphs[0]
    r = hp.add_run('RETAIL INTELLIGENCE  ·  ' + T('ĐỀ XUẤT MVP', 'MVP PROPOSAL'))
    r.font.size, r.font.color.rgb, r.bold = Pt(8), GRAY, True
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = fp.add_run(T('Bảo mật  ·  Trang ', 'Confidential  ·  Page '))
    r.font.size, r.font.color.rgb = Pt(8), GRAY
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    fp._p.append(fld)

    def P(text, bold=False, italic=False, size=None, color=None, align=None, after=None):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
        if align:
            p.alignment = align
        if after is not None:
            p.paragraph_format.space_after = Pt(after)
        return p

    def H1(text):
        doc.add_page_break()
        p = doc.add_paragraph(text, style='Heading 1')
        pPr = p._p.get_or_add_pPr()
        bd = OxmlElement('w:pBdr')
        bt = OxmlElement('w:bottom')
        bt.set(qn('w:val'), 'single')
        bt.set(qn('w:sz'), '12')
        bt.set(qn('w:color'), '0F7C78')
        bt.set(qn('w:space'), '4')
        bd.append(bt)
        pPr.append(bd)

    def bullets(items):
        for t in items:
            doc.add_paragraph(t, style='List Bullet')

    def callout(title, text, fill='E2F1F0', bar='0F7C78'):
        t = doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = t.rows[0].cells[0]
        shade(cell, fill)
        borders(cell, left=(24, bar))
        margins(cell, 120, 120, 200, 160)
        cell.text = ''
        p = cell.paragraphs[0]
        r = p.add_run(title)
        r.bold, r.font.size, r.font.color.rgb = True, Pt(10.5), NAVY
        p.paragraph_format.space_after = Pt(3)
        p2 = cell.add_paragraph()
        r2 = p2.add_run(text)
        r2.font.size = Pt(10)
        p2.paragraph_format.space_after = Pt(0)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def tiles(items):
        t = doc.add_table(rows=1, cols=len(items))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        w = 17.0 / len(items)
        for i, (v, label, sub) in enumerate(items):
            cell = t.rows[0].cells[i]
            cell.width = Cm(w)
            shade(cell, 'F2F5F9')
            borders(cell, top=(18, '0F7C78'), right=(12, 'FFFFFF'))
            margins(cell, 120, 120, 140, 100)
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(label.upper())
            r.font.size, r.font.color.rgb, r.bold = Pt(7.5), GRAY, True
            p2 = cell.add_paragraph()
            p2.paragraph_format.space_after = Pt(0)
            r = p2.add_run(v)
            r.font.size, r.font.color.rgb, r.bold = Pt(19), TEAL, True
            p3 = cell.add_paragraph()
            p3.paragraph_format.space_after = Pt(0)
            r = p3.add_run(sub)
            r.font.size, r.font.color.rgb = Pt(8), GRAY
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def table(headers, rows, widths, align_right=()):
        t = doc.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        for i, h in enumerate(headers):
            cell = t.rows[0].cells[i]
            shade(cell, '10243D')
            borders(cell)
            margins(cell, 70, 70, 100, 100)
            cell.text = ''
            r = cell.paragraphs[0].add_run(h)
            r.bold, r.font.size, r.font.color.rgb = True, Pt(9), RGBColor(255, 255, 255)
            if i in align_right:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        for n, row in enumerate(rows):
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cell = cells[i]
                shade(cell, 'FFFFFF' if n % 2 == 0 else 'F6F8FB')
                borders(cell, bottom=(4, 'E1E7EF'))
                margins(cell, 60, 60, 100, 100)
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                cell.text = ''
                r = cell.paragraphs[0].add_run(str(v))
                r.font.size = Pt(9.5)
                if i == 0:
                    r.bold = True
                    r.font.color.rgb = NAVY
                if i in align_right:
                    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def shot(key, caption, y0=190, y1=None):
        im = Image.open(SHOTS / f'{lang}_{key}.png').convert('RGB')
        w, h = im.size
        y1 = min(h, y1 or h)
        pieces = max(1, math.ceil((y1 - y0) / 1150))
        step = math.ceil((y1 - y0) / pieces)
        for i in range(pieces):
            crop = im.crop((244, y0 + i * step, w, min(y1, y0 + (i + 1) * step)))
            path = CROPS / f'{lang}_{key}_{i + 1}.png'
            crop.save(path, optimize=True)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(path), width=Cm(16.6))
        cap = doc.add_paragraph(T('Ảnh chụp màn hình', 'Screenshot') if caption.startswith('5.') or caption[:1].isdigit() else caption, style='Caption')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ------------------------------------------------------------ cover
    cov = doc.add_table(rows=1, cols=1)
    cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = cov.rows[0].cells[0]
    shade(cell, '0D1B2E')
    borders(cell)
    margins(cell, 900, 900, 500, 500)
    cell.text = ''
    p = cell.paragraphs[0]
    r = p.add_run('RETAIL INTELLIGENCE')
    r.bold, r.font.size, r.font.color.rgb = True, Pt(11), RGBColor(0x7F, 0xDC, 0xD3)
    p.paragraph_format.space_after = Pt(30)
    p = cell.add_paragraph()
    r = p.add_run(T('Nền tảng phân tích và dự báo\ncho chuỗi bán lẻ', 'Analytics and Forecasting Platform\nfor Retail Chains'))
    r.bold, r.font.size, r.font.color.rgb = True, Pt(30), RGBColor(255, 255, 255)
    p.paragraph_format.space_after = Pt(14)
    p = cell.add_paragraph()
    r = p.add_run(T('Đề xuất triển khai MVP', 'MVP Proposal'))
    r.font.size, r.font.color.rgb = Pt(16), RGBColor(0xB9, 0xC9, 0xDC)
    p.paragraph_format.space_after = Pt(120)
    p = cell.add_paragraph()
    r = p.add_run(T('Phân tích dữ liệu  ·  Dashboard điều hành  ·  Mô hình dự báo  ·  Lộ trình 90 ngày', 'Data analysis  ·  Executive dashboard  ·  Predictive models  ·  90-day roadmap'))
    r.font.size, r.font.color.rgb = Pt(10.5), RGBColor(0x7F, 0xDC, 0xD3)
    doc.add_paragraph()
    P(T('Tháng 11/2026', 'November 2026'), bold=True, color=NAVY, size=11, after=2)
    P(T('Tài liệu bảo mật – chỉ dành cho đối tác được chỉ định', 'Confidential – for the designated recipient only'), color=GRAY, size=9)

    # ------------------------------------------------------------ 1 executive summary
    H1(T('1. Tóm tắt điều hành', '1. Executive Summary'))
    P(T('Chuỗi bán lẻ đang có dữ liệu giao dịch nhưng thiếu một lớp phân tích thống nhất để trả lời nhanh ba câu hỏi: doanh thu đến từ đâu, chiết khấu có đang làm mất biên lợi nhuận không, và khách hàng nào cần được ưu tiên giữ chân. '
        'Retail Intelligence là một nền tảng đã chạy được trên dữ liệu thật, gồm dashboard điều hành, bộ phân tích thương mại và các mô hình dự báo, sẵn sàng để triển khai thành MVP trên dữ liệu của doanh nghiệp.',
        'Retail chains hold transaction data but lack a single analytical layer to answer three questions quickly: where revenue comes from, whether discounting is eroding margin, and which customers to prioritise for retention. '
        'Retail Intelligence is a working platform, proven on real transaction data, combining an executive dashboard, commercial analytics and predictive models, ready to be deployed as an MVP on the client\'s data.'))
    tiles([
        (fmt(1468773), T('Dòng giao dịch', 'Transaction lines'), T('đã đối soát, FY2017', 'reconciled, FY2017')),
        ('USD ' + fmt(g['net'] / 1e6, 2) + 'M', T('Doanh thu thuần', 'Net sales'), T('doanh thu gộp ', 'gross sales ') + fmt(g['gross'] / 1e6, 2) + 'M'),
        (pct(g['rate']), T('Tỷ lệ chiết khấu', 'Discount rate'), 'USD ' + fmt(disc / 1000) + 'K'),
        (pct(c['top10']), T('Top 10% hộ khách', 'Top 10% households'), T('trên doanh thu thuần', 'of net sales')),
    ])
    doc.add_heading(T('Những phát hiện chính', 'Key findings'), level=2)
    best = max([d for d in INS['departments'] if d['share'] >= .03 and d['growth'] is not None], key=lambda d: d['growth'])
    bullets([
        T(f"Chiết khấu bằng {pct(g['rate'])} doanh thu gộp (USD {fmt(disc / 1000)}K); {pct(g['retail'] / disc, 0)} đến từ thẻ thành viên và {pct(g['promo_line_share'], 0)} dòng hàng có chiết khấu. Mỗi 1 điểm % chiết khấu tương đương khoảng USD {fmt(g['gross'] * .01 / 1000)}K trên mẫu khảo sát.",
          f"Discounts equal {pct(g['rate'])} of gross sales (USD {fmt(disc / 1000)}K); {pct(g['retail'] / disc, 0)} comes from the loyalty card and {pct(g['promo_line_share'], 0)} of lines carry a discount. Each 1 pp of discount rate is worth about USD {fmt(g['gross'] * .01 / 1000)}K on the sample."),
        T(f"Doanh thu tập trung vào nhóm khách lớn: top 10% hộ tạo {pct(c['top10'])}, top 20% tạo {pct(c['top20'])}; 50% hộ thấp nhất chỉ {pct(c['bottom50'])}.",
          f"Revenue is concentrated: the top 10% of households generate {pct(c['top10'])}, the top 20% generate {pct(c['top20'])}; the bottom 50% only {pct(c['bottom50'])}."),
        T(f"Hàng nhãn riêng chiếm {pct(g['private_share'])} doanh thu với tỷ lệ chiết khấu {pct(br['private_rate'])}, thấp hơn {pct(br['national_rate'])} của thương hiệu quốc gia: đòn bẩy cải thiện cơ cấu biên.",
          f"Private label is {pct(g['private_share'])} of net sales with a {pct(br['private_rate'])} discount rate, below {pct(br['national_rate'])} for national brands: a margin-mix lever."),
        T(f"Giỏ có coupon chỉ chiếm {pct(b['coupon_share'])} số giỏ nhưng có giá trị bình quân USD {fmt(b['coupon_aov'], 2)}, gấp {fmt(b['coupon_aov'] / b['plain_aov'], 1)} lần giỏ thường.",
          f"Coupon baskets are only {pct(b['coupon_share'])} of baskets but average USD {fmt(b['coupon_aov'], 2)}, {fmt(b['coupon_aov'] / b['plain_aov'], 1)}x standard baskets."),
        T(f"Mô hình rủi ro rời bỏ bắt được khoảng 60% khách ngừng mua trong top 20% điểm, gấp 3 lần chọn ngẫu nhiên; dự báo doanh thu 7 ngày đạt WAPE {pct(FC['test_metrics'][0]['WAPE'])}.",
          f"The churn model captures about 60% of lapsing households in the top 20% of scores, 3x random selection; the 7-day sales forecast reaches a WAPE of {pct(FC['test_metrics'][0]['WAPE'])}."),
    ])
    callout(T('Đề xuất', 'Proposal'),
            T('Triển khai MVP trong 90 ngày trên dữ liệu của doanh nghiệp: kết nối dữ liệu POS, xây lớp chỉ tiêu tài chính, chạy lại các mô hình trên dữ liệu thật và đo hiệu quả bằng thử nghiệm có đối chứng. Quy trình vận hành và cơ chế kiểm soát được nêu ở mục 7; phạm vi, đầu vào dữ liệu và tiêu chí nghiệm thu ở mục 8.',
              'Deploy an MVP within 90 days on the client\'s data: connect POS data, build the financial KPI layer, re-run the models on real data and measure impact through controlled experiments. The operating process and controls are set out in section 7; scope, data inputs and acceptance criteria in section 8.'))

    # ------------------------------------------------------------ 2 value proposition
    H1(T('2. Giá trị mang lại', '2. Value Delivered'))
    P(T('Nền tảng gồm bốn lớp năng lực, mỗi lớp trả lời một nhóm câu hỏi quản trị và có đầu ra cụ thể.', 'The platform has four capability layers, each answering a group of management questions with a concrete output.'))
    table([T('Năng lực', 'Capability'), T('Câu hỏi quản trị', 'Management question'), T('Đầu ra', 'Output')], [
        [T('Phân tích hiệu quả kinh doanh', 'Performance analytics'), T('Doanh thu tăng từ đâu? Chiết khấu ảnh hưởng thế nào? Ngành và cửa hàng nào dẫn dắt?', 'Where does growth come from? How does discounting affect results? Which departments and stores lead?'), T('Cầu nối doanh thu, doanh thu gộp sang thuần, cơ cấu ngành, hiệu quả cửa hàng', 'Revenue bridge, gross-to-net, department mix, store performance')],
        [T('Phân tích khách hàng và giỏ hàng', 'Customer and basket analytics'), T('Khách nào tạo giá trị? Giữ chân ra sao? Mua kèm gì?', 'Which customers create value? How well are they retained? What is bought together?'), T('RFM, đường tập trung, cohort, quy tắc mua kèm, khuyến mãi', 'RFM, concentration curve, cohorts, association rules, promotions')],
        [T('Mô hình dự báo', 'Predictive models'), T('Doanh thu tuần tới? Khách nào có nguy cơ ngừng mua?', 'Next week\'s sales? Which customers are at risk of lapsing?'), T('Dự báo 7 ngày, điểm rủi ro rời bỏ, 5 mô hình Probit chấm điểm dữ liệu mới', '7-day forecast, churn risk score, 5 Probit models to score new data')],
        [T('Mô phỏng tài chính', 'Financial simulation'), T('Biên giảm 1 điểm thì cần bán thêm bao nhiêu? Vốn tồn kho nhạy thế nào?', 'If margin falls 1 pt, how much extra sales are needed? How sensitive is inventory capital?'), T('Độ nhạy biên và doanh thu, điểm hòa vốn, vốn lưu động', 'Margin and sales sensitivity, break-even, working capital')],
    ], [3.8, 6.8, 6.4])
    doc.add_heading(T('Độ nhạy giá trị trên dữ liệu khảo sát', 'Value sensitivity on the survey data'), level=2)
    P(T('Các con số dưới đây là phép tính độ nhạy trên mẫu hộ được theo dõi, nhằm minh họa quy mô đòn bẩy; không phải cam kết kết quả.', 'The figures below are sensitivity calculations on the tracked household sample to illustrate the size of each lever; they are not commitments of results.'), italic=True, color=GRAY, size=9.5)
    top_hh = c['top10'] * g['net']
    table([T('Đòn bẩy', 'Lever'), T('Phép tính', 'Calculation'), T('Giá trị (USD)', 'Value (USD)')], [
        [T('Chiết khấu', 'Discounting'), T('Giảm 1 điểm % tỷ lệ chiết khấu trên doanh thu gộp', 'Reduce discount rate by 1 pp on gross sales'), fmt(g['gross'] * .01)],
        [T('Giữ chân khách lớn', 'Top-decile retention'), T('Giữ thêm 1% doanh thu của top 10% hộ', 'Retain an extra 1% of top-decile revenue'), fmt(top_hh * .01)],
        [T('Cơ cấu nhãn riêng', 'Private-label mix'), T('Chuyển 1 điểm % doanh thu từ thương hiệu quốc gia sang nhãn riêng: giảm chiết khấu', 'Shift 1 pp of sales from national to private label: discount saving'), fmt(g['net'] * .01 * (br['national_rate'] - br['private_rate']) / (1 - br['national_rate']))],
    ], [3.8, 9.2, 4], align_right=(2,))

    # ------------------------------------------------------------ 3 data
    H1(T('3. Nền tảng dữ liệu', '3. Data Foundation'))
    P(T('Bản chứng minh năng lực dùng bộ dữ liệu công khai Complete Journey (siêu thị Mỹ, năm 2017). Mọi chỉ tiêu được tính lại từ toàn bộ dòng giao dịch và đối soát với tổng tiền gốc.', 'The proof of capability uses the public Complete Journey dataset (US grocery retailer, 2017). Every KPI is recomputed from all transaction lines and reconciled to the raw totals.'))
    q = INS['quality']
    table([T('Hạng mục', 'Item'), T('Giá trị', 'Value')], [
        [T('Dòng giao dịch trong phạm vi', 'Transaction lines in scope'), fmt(1468773)],
        [T('Hộ khách / cửa hàng / giỏ hàng', 'Households / stores / baskets'), f"{fmt(q['households'])} / {fmt(q['stores'])} / {fmt(q['baskets'])}"],
        [T('Doanh thu thuần thô', 'Raw net sales'), 'USD ' + fmt(g['net'], 2)],
        [T('Doanh thu gộp (trước chiết khấu)', 'Gross sales (before discounts)'), 'USD ' + fmt(g['gross'], 2)],
        [T('Dòng ngoài kỳ (loại khỏi phạm vi)', 'Out-of-period lines (excluded)'), fmt(q['out_of_scope'])],
        [T('Dòng thiếu ánh xạ SKU', 'Lines without SKU mapping'), f"{fmt(q['unmatched'])} ({pct(q['unmatched_rate'], 2)})"],
        [T('Dòng trùng lặp', 'Duplicate lines'), '0'],
        [T('Ngày không có bản ghi', 'Day without records'), '2017-12-25'],
    ], [9, 8], align_right=(1,))
    callout(T('Phạm vi sử dụng', 'Scope of use'),
            T('Dữ liệu là mẫu hộ được theo dõi, không phải doanh thu toàn chuỗi. Các chỉ tiêu cần giá vốn, chi phí vận hành, tồn kho và công nợ (biên gộp, EBITDA, vòng quay tồn, CCC, LFL) sẽ được tính khi có dữ liệu của doanh nghiệp.',
              'The data is a tracked household sample, not total chain revenue. KPIs that require cost of goods, operating costs, inventory and payables (gross margin, EBITDA, inventory turns, CCC, LFL) are computed once the client\'s data is connected.'), fill='FBF1DC', bar='D19A2B')

    # ------------------------------------------------------------ 4 insights
    H1(T('4. Phân tích dữ liệu: các phát hiện thương mại', '4. Data Analysis: Commercial Insights'))
    P(T('Phần này tóm tắt các phân tích có thể thực hiện ngay từ dữ liệu giao dịch. Mỗi phát hiện gắn với một câu hỏi quản trị và một hành động đề xuất.', 'This section summarises the analyses that can be produced directly from transaction data. Each finding is tied to a management question and a recommended action.'))
    shot('overview', T('Tổng quan điều hành: chỉ tiêu chính và tám phát hiện', 'Executive summary: headline KPIs and eight findings'), y1=1190)
    doc.add_heading(T('4.1 Doanh thu thuần và chiết khấu', '4.1 Net sales and discounting'), level=2)
    P(T(f"Doanh thu gộp USD {fmt(g['gross'] / 1e6, 2)}M giảm còn USD {fmt(g['net'] / 1e6, 2)}M sau chiết khấu. Thẻ thành viên là nguồn chiết khấu chính (USD {fmt(g['retail'] / 1000)}K), coupon nhà sản xuất USD {fmt(g['coupon'] / 1000)}K và coupon đối ứng USD {fmt(g['match'] / 1000)}K. "
        f"Chiết khấu sâu nhất ở nhóm thịt và hải sản đóng gói (23–25%) so với 16,9% của GROCERY.",
        f"Gross sales of USD {fmt(g['gross'] / 1e6, 2)}M fall to USD {fmt(g['net'] / 1e6, 2)}M after discounts. The loyalty card is the main source (USD {fmt(g['retail'] / 1000)}K), manufacturer coupons USD {fmt(g['coupon'] / 1000)}K and coupon match USD {fmt(g['match'] / 1000)}K. "
        f"Discounting is deepest in fresh and packaged meat (23–25%) versus 16.9% for GROCERY."))
    shot('netsales', T('Doanh thu thuần và chiết khấu: cầu nối gộp sang thuần, theo ngành và theo hộ', 'Net sales and discounts: gross-to-net bridge, by department and by household'), y1=1360)
    callout(T('Hành động đề xuất', 'Recommended action'), T('Rà soát độ sâu chiết khấu theo ngành và thiết kế thử nghiệm có đối chứng để xác định chiết khấu nào tạo thêm giỏ hàng, chiết khấu nào chỉ làm giảm biên.', 'Review discount depth by department and run controlled tests to separate discounts that create incremental baskets from those that only reduce margin.'))
    doc.add_heading(T('4.2 Tăng trưởng và mùa vụ', '4.2 Growth and seasonality'), level=2)
    dm = INS['monthly']
    P(T(f"Tháng 12 đạt USD {fmt(dm[-1]['net'])} (+{pct(dm[-1]['net'] / dm[-2]['net'] - 1)} so với tháng 11). Ngày cao điểm {INS['days']['top'][0][0]} đạt USD {fmt(INS['days']['top'][0][1])}, gấp {fmt(INS['days']['top'][0][1] / INS['days']['mean'], 1)} lần ngày bình quân. "
        f"Trong quý 4 so với quý 1, DRUG GM tăng 15,7% và DELI tăng 15,9%, trong khi MEAT-PCKGD giảm 1,2%.",
        f"December reached USD {fmt(dm[-1]['net'])} (+{pct(dm[-1]['net'] / dm[-2]['net'] - 1)} vs November). The peak day {INS['days']['top'][0][0]} reached USD {fmt(INS['days']['top'][0][1])}, {fmt(INS['days']['top'][0][1] / INS['days']['mean'], 1)}x the average day. "
        f"In Q4 vs Q1, DRUG GM grew 15.7% and DELI 15.9%, while MEAT-PCKGD fell 1.2%."))
    shot('growth', T('Phân tích doanh thu: cầu nối, tăng trưởng ngành, mùa vụ', 'Revenue analysis: bridge, department growth, seasonality'), y1=1340)
    doc.add_heading(T('4.3 Khách hàng và giỏ hàng', '4.3 Customers and baskets'), level=2)
    P(T(f"Chi tiêu bình quân mỗi hộ USD {fmt(c['mean'])} (trung vị USD {fmt(c['median'])}). {fmt(INS['frequency'][-1]['households'])} hộ mua từ 40 giỏ mỗi năm tạo {pct(INS['frequency'][-1]['share'], 0)} doanh thu. "
        f"Giỏ từ 21 dòng hàng trở lên chiếm {pct((INS['basket_bands'][4]['baskets'] + INS['basket_bands'][5]['baskets']) / b['count'], 0)} số giỏ nhưng {pct(INS['basket_bands'][4]['share'] + INS['basket_bands'][5]['share'], 0)} doanh thu.",
        f"Mean spend per household is USD {fmt(c['mean'])} (median USD {fmt(c['median'])}). {fmt(INS['frequency'][-1]['households'])} households with 40+ baskets a year generate {pct(INS['frequency'][-1]['share'], 0)} of sales. "
        f"Baskets of 21+ lines are {pct((INS['basket_bands'][4]['baskets'] + INS['basket_bands'][5]['baskets']) / b['count'], 0)} of baskets but {pct(INS['basket_bands'][4]['share'] + INS['basket_bands'][5]['share'], 0)} of net sales."))
    shot('loyalty', T('Kinh tế khách hàng và giỏ hàng', 'Customer and basket economics'), y1=1360)
    doc.add_heading(T('4.4 Hiệu quả cửa hàng', '4.4 Store performance'), level=2)
    P(T(f"Trong {st['active_hh20']} cửa hàng có từ 20 hộ trở lên, doanh thu trên mỗi hộ có trung vị USD {fmt(st['per_hh_median'])}, từ USD {fmt(st['per_hh_p10'])} (P10) đến USD {fmt(st['per_hh_p90'])} (P90), chênh {fmt(st['per_hh_p90'] / st['per_hh_p10'], 1)} lần. Đây là danh sách ưu tiên để rà soát danh mục hàng và khuyến mãi.",
        f"Across the {st['active_hh20']} stores with 20+ households, median sales per household is USD {fmt(st['per_hh_median'])}, ranging from USD {fmt(st['per_hh_p10'])} (P10) to USD {fmt(st['per_hh_p90'])} (P90), a {fmt(st['per_hh_p90'] / st['per_hh_p10'], 1)}x spread. This is the priority list for range and promotion review."))

    # ------------------------------------------------------------ 5 website (deep dive)
    H1(T('5. Hệ thống dashboard: diễn giải chi tiết từng phần', '5. The Dashboard: A Component-by-Component Reading Guide'))
    P(T('Dashboard chạy trực tiếp trên trình duyệt, không cần máy chủ, có hai ngôn ngữ (Tiếng Việt và English) và bộ lọc theo kỳ, cửa hàng, ngành hàng, nhóm hàng và nhãn hàng. Mười bốn màn hình được chia thành bốn nhóm. Với mỗi màn hình, phần này giải thích từng thành phần: nó đo cái gì, tính như thế nào, giá trị đang hiển thị nói lên điều gì và nên ra quyết định gì từ đó.',
        'The dashboard runs directly in the browser with no server, in two languages (Vietnamese and English), with filters for period, store, department, category and brand. Its fourteen screens are organised in four groups. For each screen this section explains every component: what it measures, how it is calculated, what the displayed value says, and which decision it supports.'))
    table([T('Nhóm', 'Group'), T('Màn hình', 'Screens'), T('Người dùng chính', 'Primary users')], [
        [T('Hiệu quả kinh doanh', 'Performance'), T('Tổng quan điều hành · Phân tích doanh thu · Doanh thu thuần và chiết khấu · Cơ cấu ngành hàng · Hiệu quả cửa hàng', 'Executive summary · Revenue analysis · Net sales and discounts · Merchandise mix · Store performance'), T('Ban điều hành, tài chính, ngành hàng', 'Executives, finance, merchandising')],
        [T('Khách hàng', 'Customers'), T('Kinh tế khách hàng và giỏ hàng · Giá trị khách hàng (RFM) · Phân tích giỏ hàng', 'Customer and basket economics · Customer value (RFM) · Basket analytics'), T('Marketing, CRM', 'Marketing, CRM')],
        [T('Mô hình dự báo', 'Predictive models'), T('Dự báo doanh thu · Rủi ro rời bỏ · Chấm điểm dữ liệu mới', 'Sales forecast · Churn risk · Score new data'), T('Kế hoạch, CRM, phân tích dữ liệu', 'Planning, CRM, data analytics')],
        [T('Tài chính và dữ liệu', 'Finance and data'), T('Lợi nhuận và vốn lưu động · Giao dịch chi tiết · Chất lượng dữ liệu và định nghĩa', 'Profitability and working capital · Transaction explorer · Data quality and definitions'), T('Tài chính, kiểm soát nội bộ, IT', 'Finance, internal control, IT')],
    ], [3.6, 9.4, 4])
    callout(T('Cách đọc bảng giải thích', 'How to read the explanation tables'),
            T('Mỗi bảng có bốn cột: Thành phần (tên trên màn hình), Định nghĩa và cách tính, Giá trị minh họa (số đang hiển thị trên dữ liệu 2017) và Ý nghĩa và quyết định (điều người dùng nên rút ra và làm tiếp).',
              'Each table has four columns: Component (name on screen), Definition and calculation, Illustrative value (the figure displayed on the 2017 data) and Meaning and decision (what the user should conclude and do next).'))

    def deep(key, title, purpose, comps, reading, y1=1340, shots=True):
        doc.add_heading(title, level=2)
        P(purpose, italic=True, color=GRAY, size=10).paragraph_format.keep_with_next = True
        if shots:
            shot(key, T('Ảnh chụp màn hình', 'Screenshot'), y1=y1)
        table([T('Thành phần', 'Component'), T('Định nghĩa và cách tính', 'Definition and calculation'), T('Giá trị minh họa', 'Illustrative value'), T('Ý nghĩa và quyết định', 'Meaning and decision')], comps, [2.9, 5.1, 3.2, 5.8])
        if reading:
            callout(T('Cách đọc tổng hợp', 'Putting it together'), reading, fill='F2F5F9', bar='10243D')

    mo = INS['monthly']
    dec, nov = mo[-1], mo[-2]
    vol = (dec['baskets'] - nov['baskets']) * (dec['net'] / dec['baskets'] + nov['net'] / nov['baskets']) / 2
    tick = (dec['net'] / dec['baskets'] - nov['net'] / nov['baskets']) * (dec['baskets'] + nov['baskets']) / 2
    deps = INS['departments']
    gd = deps[0]
    wh = INS['weekday_hour']
    cells = sorted(((v, d_, h_) for d_, row in enumerate(wh) for h_, v in enumerate(row)), reverse=True)[:3]
    wk_names = [T('T2', 'Mon'), T('T3', 'Tue'), T('T4', 'Wed'), T('T5', 'Thu'), T('T6', 'Fri'), T('T7', 'Sat'), T('CN', 'Sun')]
    gdp = sorted([d_ for d_ in deps if d_['share'] >= .03], key=lambda d_: d_['rate'], reverse=True)
    grow = sorted([d_ for d_ in deps if d_['share'] >= .03 and d_['growth'] is not None], key=lambda d_: d_['growth'])
    fb = INS['frequency']
    bb = INS['basket_bands']
    nb = INS['discount_bands']

    deep('overview', T('5.1 Tổng quan điều hành', '5.1 Executive Summary'),
         T('Màn hình mở đầu cho cuộc họp điều hành: kết quả của kỳ, những phát hiện quan trọng nhất và mức sẵn sàng của các chỉ tiêu tài chính.', 'The opening screen for executive meetings: the period result, the most important findings and the readiness of financial KPIs.'), [
        [T('Dòng tiêu đề (hero)', 'Headline banner'), T('Câu kết luận tự sinh: doanh thu thuần của kỳ chọn và thay đổi so với kỳ lịch liền trước cùng độ dài.', 'Auto-generated sentence: net sales for the selected period and the change versus the immediately preceding period of equal length.'), T(f"USD {fmt(dec['net'])}, +{pct(dec['net'] / nov['net'] - 1)}", f"USD {fmt(dec['net'])}, +{pct(dec['net'] / nov['net'] - 1)}"), T('Cho biết ngay kỳ này tăng hay giảm. Tháng 12 có Giáng sinh nên mức tăng chưa chắc bền vững.', 'States at once whether the period grew or fell. December includes Christmas, so the increase may not be sustainable.')],
        [T('Doanh thu thuần', 'Net sales'), T('Tổng sales_value của mọi dòng trong kỳ và bộ lọc: số tiền doanh nghiệp thực nhận sau chiết khấu.', 'Sum of sales_value over all lines in the period and filters: the amount the retailer actually receives after discounts.'), 'USD ' + fmt(dec['net']), T('Chỉ tiêu nền của mọi phân tích; không phải lợi nhuận.', 'The base of every analysis; it is not profit.')],
        [T('Số giỏ', 'Baskets'), T('Số mã giỏ hàng khác nhau (basket_id): mỗi giỏ là một lần đi mua.', 'Number of distinct basket IDs: each basket is one shopping trip.'), fmt(dec['baskets']), T('Đo lưu lượng giao dịch, độc lập với giá trị mỗi lần mua.', 'Measures transaction traffic, independent of value per trip.')],
        ['AOV', T('Doanh thu thuần chia số giỏ.', 'Net sales divided by baskets.'), 'USD ' + fmt(dec['net'] / dec['baskets'], 2), T('AOV tăng khi khách mua nhiều hàng hơn mỗi lần hoặc mua hàng giá cao hơn.', 'AOV rises when shoppers buy more per trip or buy higher-priced goods.')],
        [T('Hộ hoạt động / Doanh thu trên hộ', 'Active households / Sales per household'), T('Số hộ có ít nhất một dòng mua dương; doanh thu chia số hộ.', 'Households with at least one positive purchase; sales divided by households.'), f"{fmt(2057)} / USD {fmt(dec['net'] / 2057)}", T('Cho biết nhu cầu tăng nhờ nhiều khách hơn hay khách chi nhiều hơn.', 'Shows whether demand grows through more customers or higher spend per customer.')],
        [T('Tỷ lệ chiết khấu FY', 'FY discount rate'), T('Tổng chiết khấu (thẻ, coupon, coupon đối ứng) chia doanh thu gộp, cả năm.', 'Total discounts (loyalty, coupon, coupon match) divided by gross sales, full year.'), pct(g['rate']), T('Đo mức doanh nghiệp "trả lại" khách trên mỗi đồng doanh thu gộp; mỗi điểm % tương đương USD 54 nghìn.', 'Measures how much the retailer gives back per dollar of gross sales; each point is worth about USD 54K.')],
        [T('Tám phát hiện chính', 'Eight key findings'), T('Mỗi thẻ gồm chỉ số lớn, câu kết luận và hàm ý. Toàn bộ được tính từ dữ liệu, không nhập tay.', 'Each card has a headline number, a conclusion and an implication, all computed from the data rather than typed in.'), T('Ví dụ: top 10% hộ = 35,1% doanh thu', 'e.g. top 10% households = 35.1% of sales'), T('Danh sách ưu tiên điều tra: tập trung khách, chiết khấu, nhãn riêng, giỏ lớn, ngành, mùa vụ, cửa hàng, mô hình.', 'A priority list for investigation: concentration, discounting, private label, large baskets, categories, seasonality, stores, models.')],
        [T('Doanh thu thuần theo tháng + tỷ lệ chiết khấu', 'Monthly net sales + discount rate'), T('Cột là doanh thu thuần từng tháng; đường là tỷ lệ chiết khấu trên doanh thu gộp (trục phải).', 'Bars are monthly net sales; the line is the discount rate on gross sales (right axis).'), T(f"Chiết khấu dao động {pct(min(m['rate'] for m in mo))}–{pct(max(m['rate'] for m in mo))}", f"Discount rate ranges {pct(min(m['rate'] for m in mo))}–{pct(max(m['rate'] for m in mo))}"), T('Nếu doanh thu tăng cùng lúc chiết khấu tăng, tăng trưởng có thể được "mua" bằng khuyến mãi; ở đây tỷ lệ khá ổn định.', 'If sales rise while discounting also rises, growth may have been "bought" with promotions; here the rate is fairly stable.')],
        [T('Mức sẵn sàng chỉ tiêu tài chính', 'Financial KPI readiness'), T('Bảng liệt kê chỉ tiêu, trạng thái (Có / Cần dữ liệu) và dữ liệu doanh nghiệp cần cung cấp.', 'Table of KPIs, status (Available / Input required) and the client data needed.'), T('2 chỉ tiêu có, 5 cần dữ liệu', '2 available, 5 require input'), T('Là danh sách yêu cầu dữ liệu cho giai đoạn MVP: giá vốn, OPEX, tồn kho, công nợ, lịch mở cửa.', 'It doubles as the data request list for the MVP: cost, OPEX, inventory, payables, trading calendar.')],
    ], T('Đọc từ trên xuống: kết quả kỳ, rồi tám phát hiện để chọn nơi cần đào sâu, rồi biểu đồ theo tháng để kiểm tra tính bền vững, cuối cùng là bảng dữ liệu còn thiếu.', 'Read top to bottom: the period result, then the eight findings to choose where to dig deeper, then the monthly chart to test sustainability, and finally the table of missing data.'))

    deep('growth', T('5.2 Phân tích doanh thu', '5.2 Revenue Analysis'),
         T('Trả lời hai câu hỏi: tăng trưởng đến từ đâu và có mang tính mùa vụ hay không.', 'Answers two questions: where growth comes from and how seasonal it is.'), [
        [T('Thay đổi tuyệt đối', 'Absolute change'), T('Doanh thu kỳ chọn trừ doanh thu kỳ trước.', 'Selected-period sales minus prior-period sales.'), 'USD ' + fmt(dec['net'] - nov['net'], 2), T('Quy mô thay đổi bằng tiền; so sánh tháng 12 với tháng 11.', 'The change in money terms; December versus November.')],
        [T('Hiệu ứng số giỏ', 'Basket-count effect'), T('(Số giỏ kỳ này − kỳ trước) × trung bình hai AOV. Phân rã đối xứng: phần tương tác chia đều.', '(Baskets now − baskets before) × the average of the two AOVs. Symmetric decomposition: the interaction is split evenly.'), 'USD ' + fmt(vol, 2), T(f"Chiếm {pct(vol / (dec['net'] - nov['net']), 0)} mức tăng: thêm {fmt(dec['baskets'] - nov['baskets'])} lượt mua.", f"{pct(vol / (dec['net'] - nov['net']), 0)} of the increase: {fmt(dec['baskets'] - nov['baskets'])} more trips.")],
        [T('Hiệu ứng giá trị giỏ', 'Ticket-size effect'), T('(AOV kỳ này − kỳ trước) × trung bình hai số giỏ.', '(AOV now − AOV before) × the average of the two basket counts.'), 'USD ' + fmt(tick, 2), T(f"Chiếm {pct(tick / (dec['net'] - nov['net']), 0)}: khách mua nhiều hơn mỗi lần. Có thể do cơ cấu hàng, giá hoặc khuyến mãi, cần điều tra thêm.", f"{pct(tick / (dec['net'] - nov['net']), 0)}: shoppers buy more per trip. It may reflect mix, price or promotions and needs investigation.")],
        [T('Cầu nối doanh thu', 'Revenue bridge'), T('Biểu đồ thác nước: cột xanh dương là kỳ trước và kỳ chọn; cột xanh lá là phần tăng; cột đỏ là phần giảm. Trục được cắt để thấy rõ chênh lệch.', 'Waterfall chart: blue bars are the prior and selected periods; green is an increase; red a decrease. The axis is truncated so the difference is visible.'), '—', T('Hình ảnh hóa việc tăng trưởng do lượng hay do giá trị.', 'Visualises whether growth is driven by volume or value.')],
        [T('Tăng trưởng ngành Q4 so với Q1', 'Department growth Q4 vs Q1'), T('(Doanh thu Q4 / doanh thu Q1) − 1 cho ngành chiếm từ 1% doanh thu.', '(Q4 sales / Q1 sales) − 1 for departments with at least 1% of sales.'), T(f"{grow[-1]['name']} {pct(grow[-1]['growth'])}; {grow[0]['name']} {pct(grow[0]['growth'])}", f"{grow[-1]['name']} {pct(grow[-1]['growth'])}; {grow[0]['name']} {pct(grow[0]['growth'])}"), T('Chỉ ra ngành đang lên và ngành chững lại để điều chỉnh không gian kệ và khuyến mãi.', 'Identifies rising and stalling departments to adjust shelf space and promotions.')],
        [T('Chỉ số doanh thu ngành theo tháng', 'Department sales index by month'), T('Doanh thu từng tháng của ngành chia trung bình tháng của chính ngành đó. 1,0 là mức trung bình; xanh lá là cao hơn, đỏ là thấp hơn.', 'Each month\'s department sales divided by that department\'s monthly average. 1.0 is average; green is above, red below.'), '—', T('Phát hiện mùa vụ riêng từng ngành (ví dụ nhiên liệu, hàng quà tặng) mà tổng doanh thu che khuất.', 'Reveals department-specific seasonality (e.g. fuel, gifting) hidden by total sales.')],
        [T('Doanh thu theo tuần', 'Weekly net sales'), T('Tổng doanh thu từng tuần trong năm (bỏ tuần 1 không đủ ngày).', 'Total sales for each week of the year (week 1, which is incomplete, is excluded).'), T(f"Đỉnh ngày {INS['days']['top'][0][0]}", f"Peak day {INS['days']['top'][0][0]}"), T(f"Ngày thấp nhất {INS['days']['low'][0][0]} (USD {fmt(INS['days']['low'][0][1])}); tuần lễ quyết định kế hoạch nhân sự và tồn kho.", f"Lowest day {INS['days']['low'][0][0]} (USD {fmt(INS['days']['low'][0][1])}); holiday weeks drive staffing and inventory plans.")],
        [T('Mật độ theo thứ và giờ', 'Weekday-hour density'), T('Bản đồ nhiệt doanh thu 7 thứ × 24 giờ; ô đậm là doanh thu cao.', 'Heatmap of sales across 7 weekdays × 24 hours; darker cells mean higher sales.'), T(f"Cao nhất: {wk_names[cells[0][1]]} {cells[0][2]}h, {wk_names[cells[1][1]]} {cells[1][2]}h", f"Highest: {wk_names[cells[0][1]]} {cells[0][2]}h, {wk_names[cells[1][1]]} {cells[1][2]}h"), T('Cuối tuần và buổi chiều tối dẫn dắt doanh thu; ít giao dịch từ nửa đêm đến sáng.', 'Weekends and early evenings drive sales; very few transactions from midnight to morning.')],
    ], T('Bắt đầu từ cầu nối để biết tăng trưởng do lượng hay giá trị, kiểm tra ngành nào đóng góp, rồi dùng mùa vụ và thứ–giờ để lập kế hoạch vận hành.', 'Start with the bridge to see whether growth is volume or value, check which departments contribute, then use seasonality and weekday-hour patterns for operations planning.'), y1=1340)

    deep('netsales', T('5.3 Doanh thu thuần và chiết khấu', '5.3 Net Sales and Discounts'),
         T('Tách doanh thu gộp, chiết khấu và doanh thu thuần để thấy chương trình khuyến mãi đang tiêu tốn bao nhiêu.', 'Separates gross sales, discounts and net sales to show how much the promotional programme costs.'), [
        [T('Doanh thu gộp', 'Gross sales'), T('Doanh thu thuần cộng chiết khấu thẻ thành viên, coupon nhà sản xuất và coupon đối ứng.', 'Net sales plus loyalty, manufacturer coupon and coupon-match discounts.'), 'USD ' + fmt(g['gross']), T('Giá trị hàng hóa theo giá niêm yết trước khuyến mãi.', 'Value of goods at shelf price before promotions.')],
        [T('Tổng chiết khấu', 'Total discounts'), T('Tổng ba loại chiết khấu.', 'Sum of the three discount types.'), 'USD ' + fmt(disc) + f" ({pct(g['rate'])})", T('Mỗi điểm % tương đương khoảng USD 54 nghìn; là đòn bẩy biên lợi nhuận lớn nhất nếu giảm được phần không tạo thêm giỏ hàng.', 'Each point is worth about USD 54K; the largest margin lever if the portion that creates no incremental baskets can be reduced.')],
        [T('Chiết khấu thẻ thành viên', 'Loyalty discount'), T('Giảm giá áp dụng cho khách có thẻ (retail_disc).', 'Discount applied to card holders (retail_disc).'), f"USD {fmt(g['retail'])} ({pct(g['retail'] / disc, 0)})", T('Gần như toàn bộ chi phí khuyến mãi nằm ở chương trình thẻ, nên tối ưu thẻ là ưu tiên.', 'Almost the entire promotion cost sits in the card programme, so optimising it is the priority.')],
        [T('Tỷ lệ dòng có chiết khấu', 'Promoted-line rate'), T('Số dòng hàng có chiết khấu dương chia tổng số dòng.', 'Lines with a positive discount divided by all lines.'), pct(g['promo_line_share'], 0), T('Hơn một nửa dòng hàng đang được khuyến mãi: giá "bình thường" ít khi là giá khách trả.', 'More than half of the lines are promoted: the "regular" price is rarely what the customer pays.')],
        [T('Cầu nối gộp sang thuần', 'Gross-to-net bridge'), T('Thác nước: doanh thu gộp, trừ chiết khấu thẻ, coupon, coupon đối ứng, ra doanh thu thuần.', 'Waterfall: gross sales less loyalty, coupon and coupon-match discounts, ending at net sales.'), f"{fmt(g['gross'] / 1e6, 2)}M → {fmt(g['net'] / 1e6, 2)}M", T('Cho thấy quy mô từng nguồn chiết khấu; coupon nhà sản xuất nhỏ nhưng gắn với giỏ lớn.', 'Shows the size of each discount source; manufacturer coupons are small but linked to large baskets.')],
        [T('Tỷ lệ chiết khấu theo tháng', 'Monthly discount rate'), T('Cột gộp và thuần, đường là tỷ lệ chiết khấu.', 'Bars for gross and net, line for the discount rate.'), T(f"Thấp nhất {pct(min(m['rate'] for m in mo))}, cao nhất {pct(max(m['rate'] for m in mo))}", f"Low {pct(min(m['rate'] for m in mo))}, high {pct(max(m['rate'] for m in mo))}"), T('Biến động nhỏ cho thấy khuyến mãi được duy trì đều, không theo đợt.', 'Small variation shows promotions run steadily rather than in bursts.')],
        [T('Tỷ lệ chiết khấu theo ngành', 'Discount rate by department'), T('Chiết khấu chia doanh thu gộp của từng ngành; đường chấm là mức trung bình toàn bộ.', 'Discounts divided by each department\'s gross sales; the dotted line is the overall average.'), T(f"{gdp[0]['name']} {pct(gdp[0]['rate'])}, {gdp[1]['name']} {pct(gdp[1]['rate'])}, GROCERY {pct(gd['rate'])}", f"{gdp[0]['name']} {pct(gdp[0]['rate'])}, {gdp[1]['name']} {pct(gdp[1]['rate'])}, GROCERY {pct(gd['rate'])}"), T('Nhóm thịt chiết khấu sâu nhất: cần kiểm tra biên gộp thực của nhóm này và độ nhạy giá của khách.', 'Meat is discounted deepest: check its true gross margin and customer price sensitivity.')],
        [T('Độ sâu chiết khấu theo hộ', 'Household discount depth'), T('Chia hộ thành nhóm theo tỷ lệ chiết khấu họ nhận; hiển thị chi tiêu bình quân mỗi hộ.', 'Groups households by the discount rate they receive and shows average spend per household.'), T(f"{nb[2]['band']}: USD {fmt(nb[2]['spend'])}/hộ; {nb[4]['band']}: USD {fmt(nb[4]['spend'])}/hộ", f"{nb[2]['band']}: USD {fmt(nb[2]['spend'])}/HH; {nb[4]['band']}: USD {fmt(nb[4]['spend'])}/HH"), T('Hộ nhận chiết khấu cao không phải hộ chi nhiều nhất: nhóm 10–15% có chi tiêu lớn nhất, nhóm trên 20% thấp hơn rõ rệt.', 'Households receiving the deepest discounts are not the highest spenders: the 10–15% group spends most, the 20%+ group clearly less.')],
        [T('Nhãn riêng và thương hiệu quốc gia', 'Private label vs national brands'), T('Doanh thu, tỷ trọng và tỷ lệ chiết khấu của từng loại nhãn.', 'Net sales, share and discount rate for each brand type.'), T(f"{pct(br['private_rate'])} so với {pct(br['national_rate'])}", f"{pct(br['private_rate'])} vs {pct(br['national_rate'])}"), T('Nhãn riêng bán được với ít chiết khấu hơn: tăng tỷ trọng nhãn riêng cải thiện biên mà không cần giảm giá thêm.', 'Private label sells with less discounting: raising its share improves margin without deeper price cuts.')],
    ], T('So sánh ba lớp: quy mô chiết khấu (cầu nối), nơi chiết khấu sâu (ngành) và ai nhận chiết khấu (hộ). Từ đó quyết định chương trình nào cần thử nghiệm đối chứng trước.', 'Compare three layers: the size of discounting (bridge), where it is deepest (department) and who receives it (household). Then decide which programme to test first with a control group.'), y1=1360)

    deep('catalog', T('5.4 Cơ cấu ngành hàng', '5.4 Merchandise Mix'),
         T('Cho biết danh mục sản phẩm tập trung vào đâu và SKU nào là xương sống của doanh thu.', 'Shows where the range is concentrated and which SKUs form the backbone of sales.'), [
        [T('SKU phát sinh', 'Active SKUs'), T('Số mã hàng có ít nhất một giao dịch trong kỳ.', 'SKUs with at least one transaction in the period.'), T('25.217 (tháng 12)', '25,217 (December)'), T('Không phải số mã đang kinh doanh; chỉ là mã có bán.', 'Not the number of listed items, only items that sold.')],
        [T('SKU hạng A', 'Class A SKUs'), T('Sắp SKU theo doanh thu giảm dần; hạng A là nhóm đầu đạt 80% doanh thu tích lũy.', 'SKUs sorted by sales; Class A is the top group reaching 80% of cumulative sales.'), T('8.070 SKU (≈ 32%)', '8,070 SKUs (≈ 32%)'), T('Cần ưu tiên tồn kho và vị trí kệ. Phần còn lại (B, C) là đuôi dài.', 'Prioritise stock and shelf position. The rest (B, C) is the long tail.')],
        [T('Nhóm sản phẩm', 'Product categories'), T('Số nhóm hàng (product_category) khác nhau.', 'Number of distinct product categories.'), '288', T('Độ rộng danh mục; dùng để đánh giá phân mảnh.', 'Breadth of the range; used to assess fragmentation.')],
        [T('Doanh thu theo ngành', 'Net sales by department'), T('Thanh ngang doanh thu của các ngành lớn nhất.', 'Horizontal bars for the largest departments.'), T(f"GROCERY {pct(gd['share'])} cả năm", f"GROCERY {pct(gd['share'])} for the year"), T('Mức phụ thuộc vào một ngành; doanh thu lớn không đồng nghĩa lợi nhuận lớn.', 'Dependence on one department; large sales do not imply large profit.')],
        [T('Đường Pareto SKU', 'SKU Pareto curve'), T('Trục ngang là thứ hạng SKU, trục dọc là % doanh thu tích lũy.', 'Horizontal axis is SKU rank, vertical axis is cumulative % of sales.'), '—', T('Đường càng cong thì doanh thu càng tập trung vào ít SKU; xác định nhóm SKU cần giữ chắc.', 'The more curved, the more sales sit in few SKUs; identifies the SKUs to protect.')],
        [T('Nhóm COUPON/MISC ITEMS', 'COUPON/MISC ITEMS category'), T('Nhóm kỹ thuật trong nguồn dữ liệu, chứa chủ yếu nhiên liệu cùng thẻ quà tặng.', 'A technical category in the source data containing mostly fuel plus gift cards.'), T('USD 31.878 trong tháng 12; xăng ≈ 364 nghìn USD cả năm', 'USD 31,878 in December; fuel ≈ USD 364K for the year'), T('Không so sánh với ngành thực phẩm; tách riêng khi đánh giá hiệu quả danh mục.', 'Do not compare with food departments; separate it when assessing category performance.')],
        [T('Danh sách SKU', 'SKU list'), T('Bảng SKU có tìm kiếm, lọc theo hạng ABC, hiển thị tối đa 200 dòng và xuất được.', 'Searchable SKU table filterable by ABC class, up to 200 rows, exportable.'), '—', T('Dùng để rà soát danh mục theo SKU cụ thể.', 'Used to review the range SKU by SKU.')],
    ], T('ABC chỉ phản ánh doanh thu. Khi có giá vốn, cùng bảng này sẽ cho biết SKU nào tạo lãi gộp thực sự.', 'ABC reflects sales only. Once cost data arrives, the same view will show which SKUs actually create gross profit.'), y1=1340)

    sd = INS['stores']
    deep('stores', T('5.5 Hiệu quả cửa hàng', '5.5 Store Performance'),
         T('So sánh cửa hàng theo quy mô, khách và giá trị giỏ, và cho biết khi nào khách mua.', 'Compares stores by scale, customers and basket value, and shows when customers shop.'), [
        [T('Top cửa hàng theo doanh thu', 'Top stores by net sales'), T('12 cửa hàng có doanh thu cao nhất trong kỳ.', 'The 12 stores with the highest sales in the period.'), T('Cửa hàng 367: USD 12.670 (3,0%)', 'Store 367: USD 12,670 (3.0%)'), T('Doanh thu phân tán: cửa hàng đầu bảng chỉ chiếm 3% trong tháng 12.', 'Sales are spread out: the top store has only 3% in December.')],
        [T('Số hộ so với giá trị giỏ', 'Households vs basket value'), T('Mỗi điểm là một cửa hàng: trục ngang số hộ, trục dọc AOV, kích thước là doanh thu.', 'Each point is a store: horizontal axis households, vertical axis AOV, size is sales.'), T('181 cửa hàng trong kỳ', '181 stores in period'), T('Điểm cao và lệch phải là cửa hàng đông khách và giỏ lớn; điểm sát trục tung chỉ có rất ít hộ trong mẫu.', 'High and right-leaning points have many customers and large baskets; points hugging the vertical axis have very few households in the sample.')],
        [T('Doanh thu theo thứ', 'Net sales by weekday'), T('Tổng doanh thu mỗi thứ trong tuần của kỳ chọn.', 'Total sales per weekday in the selected period.'), T('Thứ 7 và Chủ nhật cao nhất', 'Saturday and Sunday highest'), T('Căn cứ xếp ca và bổ sung hàng cuối tuần.', 'Basis for shift planning and weekend replenishment.')],
        [T('Doanh thu theo giờ', 'Net sales by hour'), T('Tổng doanh thu theo giờ giao dịch.', 'Total sales by transaction hour.'), T('Đỉnh khoảng 20–22 giờ', 'Peak around 20–22h'), T('Giờ giao dịch không phải lưu lượng khách thật; dùng để định hướng nhân sự khi có dữ liệu cửa hàng.', 'Transaction hour is not true footfall; use it to guide staffing until store data is available.')],
        [T('Cầu nối doanh thu', 'Net sales bridge'), T('Phân rã thay đổi doanh thu thành số giỏ và giá trị giỏ.', 'Splits the change in sales into basket count and basket value.'), '—', T('Giống màn hình Phân tích doanh thu nhưng áp dụng cho bộ lọc cửa hàng đang chọn.', 'Same as the Revenue Analysis screen but applied to the selected store filter.')],
        [T('Năng suất trên mỗi hộ (cả năm)', 'Sales per household (full year)'), T('Doanh thu cửa hàng chia số hộ mua tại cửa hàng; xét cửa hàng có từ 20 hộ.', 'Store sales divided by households shopping there; stores with at least 20 households.'), T(f"Trung vị USD {fmt(sd['per_hh_median'])}; P10 {fmt(sd['per_hh_p10'])}; P90 {fmt(sd['per_hh_p90'])}", f"Median USD {fmt(sd['per_hh_median'])}; P10 {fmt(sd['per_hh_p10'])}; P90 {fmt(sd['per_hh_p90'])}"), T(f"Chênh {fmt(sd['per_hh_p90'] / sd['per_hh_p10'], 1)} lần giữa nhóm mạnh và yếu: danh sách cửa hàng cần rà soát danh mục và khuyến mãi.", f"A {fmt(sd['per_hh_p90'] / sd['per_hh_p10'], 1)}x gap between strong and weak: the list of stores for range and promotion review.")],
        [T('Bảng cửa hàng', 'Store table'), T('Doanh thu, giỏ, hộ, AOV và tỷ trọng; chọn mã cửa hàng để áp bộ lọc.', 'Sales, baskets, households, AOV and share; select a store ID to apply the filter.'), '—', T('Cách nhanh nhất để đi từ so sánh cửa hàng sang phân tích riêng một cửa hàng.', 'The fastest way from a store comparison to a single-store analysis.')],
    ], T('Lưu ý quan trọng: dữ liệu là mẫu hộ, nên 20% cửa hàng lớn nhất chiếm 92% doanh thu mẫu không có nghĩa chuỗi tập trung như vậy. Khi có POS toàn chuỗi, các chỉ số này được tính lại.', 'Important: the data is a household sample, so the top 20% of stores holding 92% of sample sales does not mean the chain is that concentrated. These measures are recomputed once full-chain POS is connected.'), y1=1340)

    ls = INS['basket']
    deep('loyalty', T('5.6 Kinh tế khách hàng và giỏ hàng', '5.6 Customer and Basket Economics'),
         T('Cho thấy doanh thu phụ thuộc vào ai và vào kiểu giỏ hàng nào.', 'Shows who and which type of basket the revenue depends on.'), [
        [T('Chi tiêu trên hộ', 'Spend per household'), T('Tổng chi tiêu mua dương của hộ trong năm; trung bình và trung vị.', 'Total positive spend per household in the year; mean and median.'), f"USD {fmt(c['mean'])} / {fmt(c['median'])}", T('Trung bình cao hơn trung vị cho thấy một nhóm hộ chi rất lớn kéo mức trung bình lên.', 'A mean above the median shows a group of very large spenders pulling the average up.')],
        [T('Top 10% / Top 20% hộ', 'Top 10% / top 20% of households'), T('Tỷ trọng doanh thu của nhóm hộ chi nhiều nhất.', 'Share of sales from the biggest-spending households.'), f"{pct(c['top10'])} / {pct(c['top20'])}", T('Mức phụ thuộc vào khách lớn: mất một phần nhỏ khách top ảnh hưởng lớn đến doanh thu.', 'Dependence on large customers: losing a small part of the top tier hits sales hard.')],
        [T('Đường Lorenz', 'Lorenz curve'), T('Trục ngang là % hộ (từ lớn nhất), trục dọc là % doanh thu tích lũy; đường chéo là phân phối đều.', 'Horizontal axis is % of households (largest first), vertical is cumulative % of sales; the diagonal is perfect equality.'), T('Hệ số Gini 0,52', 'Gini coefficient 0.52'), T('Đường càng cong khỏi đường chéo thì càng tập trung. Gini 0,52 là mức tập trung vừa phải.', 'The further the curve bows from the diagonal, the more concentrated. A Gini of 0.52 is moderate concentration.')],
        [T('Tần suất mua', 'Purchase frequency'), T('Số hộ và % doanh thu theo nhóm số giỏ mỗi năm.', 'Households and % of sales by number of baskets per year.'), T(f"{fmt(fb[-1]['households'])} hộ mua từ 40 giỏ = {pct(fb[-1]['share'], 0)} doanh thu", f"{fmt(fb[-1]['households'])} households with 40+ baskets = {pct(fb[-1]['share'], 0)} of sales"), T('Khách mua thường xuyên là cốt lõi: tăng tần suất của nhóm 20–39 giỏ là cơ hội tăng trưởng gần nhất.', 'Frequent shoppers are the core: raising the frequency of the 20–39 basket group is the nearest growth opportunity.')],
        [T('Hộ mới và hộ quay lại', 'New vs returning households'), T('Mỗi tháng: hộ lần đầu có mua trong dữ liệu (mới) và hộ đã mua trước đó (quay lại). Tháng 1 là điểm khởi đầu nên bỏ qua.', 'Each month: households buying for the first time in the data (new) and those who bought before (returning). January is the start of the data and is ignored.'), T(f"Tháng 2: {fmt(mo[1]['new_hh'])} mới; tháng 12: {fmt(dec['new_hh'])} mới", f"February: {fmt(mo[1]['new_hh'])} new; December: {fmt(dec['new_hh'])} new"), T('Gần như không có khách mới: tăng trưởng đến từ nhóm khách hiện hữu; mẫu hộ cố định nên không dùng để đo thu hút khách.', 'Almost no new customers: growth comes from existing customers; the panel is fixed so it cannot measure acquisition.')],
        [T('Quy mô giỏ hàng', 'Basket size'), T('Chia giỏ theo số dòng hàng; so sánh % số giỏ với % doanh thu.', 'Baskets grouped by number of lines; compares % of baskets with % of sales.'), T(f"21+ dòng: {pct((bb[4]['baskets'] + bb[5]['baskets']) / ls['count'], 0)} giỏ, {pct(bb[4]['share'] + bb[5]['share'], 0)} doanh thu", f"21+ lines: {pct((bb[4]['baskets'] + bb[5]['baskets']) / ls['count'], 0)} of baskets, {pct(bb[4]['share'] + bb[5]['share'], 0)} of sales"), T('Giỏ "mua sắm cả tuần" là động lực doanh thu; giỏ 1–5 dòng nhiều về số lượng nhưng đóng góp thấp.', 'Full-shop baskets drive sales; 1–5 line baskets are numerous but contribute little.')],
        [T('Giỏ có coupon và giỏ thường', 'Coupon vs standard baskets'), T('So sánh tỷ trọng, AOV và số dòng hàng.', 'Compares share, AOV and lines per basket.'), T(f"AOV USD {fmt(ls['coupon_aov'], 2)} so với {fmt(ls['plain_aov'], 2)}", f"AOV USD {fmt(ls['coupon_aov'], 2)} vs {fmt(ls['plain_aov'], 2)}"), T('Khách dùng coupon mua nhiều hơn gấp 2,6 lần, nhưng chưa chứng minh coupon làm họ mua nhiều hơn (có thể chỉ là khách vốn mua nhiều dùng coupon).', 'Coupon users spend 2.6x more, but this does not prove coupons cause higher spend (big spenders may simply use coupons more).')],
    ], T('Chiến lược giữ chân nên nhắm vào top decile và nhóm 20–39 giỏ; đo coupon bằng thử nghiệm đối chứng thay vì so sánh trực tiếp hai nhóm giỏ.', 'Retention strategy should target the top decile and the 20–39 basket group; measure coupons with a controlled test rather than comparing the two basket groups directly.'), y1=1360)

    cl = pd.read_csv(RUN / 'cluster_profiles.csv')
    coh = pd.read_csv(RUN / 'observed_cohorts.csv')
    jan = coh[(coh.first_observed_month == '2017-01') & (coh.age_month >= 1)]
    deep('customers', T('5.7 Giá trị khách hàng (RFM)', '5.7 Customer Value (RFM)'),
         T('Phân khúc khách theo hành vi mua và theo dõi khả năng giữ chân.', 'Segments customers by purchase behaviour and tracks retention.'), [
        ['Recency', T('Số ngày từ lần mua cuối đến cuối kỳ.', 'Days from the last purchase to the end of the period.'), T('Trung vị 3 ngày (tháng 12)', 'Median 3 days (December)'), T('Khách mua rất gần đây: hầu hết khách trong mẫu còn hoạt động; recency tăng dần là tín hiệu rời bỏ.', 'Most customers in the sample are still active; rising recency is a churn signal.')],
        ['Frequency', T('Số giỏ có mua dương của hộ trong kỳ.', 'Number of baskets with positive purchases per household in the period.'), '—', T('Trục ngang của biểu đồ giá trị–tần suất.', 'The horizontal axis of the value–frequency chart.')],
        ['Monetary', T('Tổng giá trị mua dương của hộ trong kỳ.', 'Total positive purchase value per household in the period.'), '—', T('Trục dọc của biểu đồ giá trị–tần suất; hộ góc trên bên phải là khách chủ lực.', 'The vertical axis of the value–frequency chart; households in the upper right are the core customers.')],
        [T('Hộ mua đa cửa hàng', 'Multi-store households'), T('Tỷ lệ hộ mua tại từ 2 cửa hàng trở lên trong phạm vi chọn.', 'Share of households shopping at 2+ stores within the selected scope.'), T(f"{pct(c['multi_store'], 0)} (cả năm); trung vị 4 cửa hàng", f"{pct(c['multi_store'], 0)} (full year); median 4 stores"), T('Khách không trung thành với một cửa hàng: đánh giá cửa hàng theo từng khách dễ gây hiểu lầm; cần phân tích theo mạng lưới.', 'Customers are not loyal to a single store: assessing stores customer by customer is misleading; analyse at network level.')],
        [T('Phân khúc doanh nghiệp', 'Business segments'), T('Quy tắc từ RFM: khách chủ lực, mua thường xuyên, giá trị cao đang giảm mua, mới, còn lại.', 'RFM-based rules: core customers, frequent buyers, high-value declining, new, other.'), T(f"Chủ lực: {fmt(SEG.households[1])} hộ = {pct(SEG.sales_share[1])} doanh thu", f"Core: {fmt(SEG.households[1])} households = {pct(SEG.sales_share[1])} of sales"), T('Nhóm "giá trị cao, giảm mua" nhỏ (13 hộ) nhưng là danh sách chăm sóc ưu tiên.', 'The "high value, declining" group is small (13 households) but is the priority care list.')],
        [T('Phân khúc K-means', 'K-means clusters'), T('Thuật toán gom hộ thành k nhóm theo hành vi; k chọn bằng silhouette, kiểm tra độ ổn định bằng ARI.', 'The algorithm groups households into k clusters by behaviour; k is chosen by silhouette and stability is tested with ARI.'), T(f"k = 3; silhouette {fmt(AN['clustering']['silhouette'], 2)}; ARI {fmt(AN['clustering']['seed_stability_ARI'], 2)}", f"k = 3; silhouette {fmt(AN['clustering']['silhouette'], 2)}; ARI {fmt(AN['clustering']['seed_stability_ARI'], 2)}"), T(f"Ba nhóm: gắn bó ({fmt(cl.households[1])} hộ, {pct(cl.sales[1] / cl.sales.sum(), 0)} doanh thu), trung bình ({fmt(cl.households[0])} hộ), nguội dần ({fmt(cl.households[2])} hộ, recency {fmt(cl.mean_recency[2], 0)} ngày).", f"Three groups: engaged ({fmt(cl.households[1])} households, {pct(cl.sales[1] / cl.sales.sum(), 0)} of sales), moderate ({fmt(cl.households[0])}), fading ({fmt(cl.households[2])}, recency {fmt(cl.mean_recency[2], 0)} days).")],
        [T('Cohort giữ chân', 'Cohort retention'), T('Với nhóm hộ xuất hiện lần đầu cùng một tháng, % hộ còn mua ở các tháng sau.', 'For households first seen in the same month, the % still buying in later months.'), T(f"Nhóm tháng 1: {pct(jan.active_rate.mean(), 0)} còn hoạt động", f"January cohort: {pct(jan.active_rate.mean(), 0)} still active"), T('Giữ chân cao do mẫu gồm hộ mua thường xuyên; khi có dữ liệu thật, đường này là thước đo sức khỏe khách hàng.', 'High retention reflects a panel of frequent shoppers; on real data this line becomes the customer health gauge.')],
    ], T('Dùng RFM để biết ai là khách giá trị, K-means để thiết kế chăm sóc theo nhóm và cohort để theo dõi giữ chân theo thời gian.', 'Use RFM to know who the valuable customers are, K-means to design care by group, and cohorts to track retention over time.'), y1=1340)

    ar = pd.read_csv(RUN / 'association_rules.csv')
    ci = pd.read_csv(ROOT / 'outputs/word_report/campaign_intervals.csv')
    ca = ci.groupby('campaign_type').agg(n=('campaign_id', 'size'), hh=('assigned_households', 'sum'), red=('redeeming_assigned_households', 'sum'))
    deep('basket', T('5.8 Phân tích giỏ hàng', '5.8 Basket Analytics'),
         T('Tìm các nhóm hàng hay được mua cùng nhau và đo phản hồi của chiến dịch coupon.', 'Finds categories frequently bought together and measures the response to coupon campaigns.'), [
        ['Support', T('Tỷ lệ giỏ chứa cả hai nhóm hàng A và B.', 'Share of baskets containing both categories A and B.'), T(f"{pct(ar.train_support[0])} (thịt nguội → bánh mì)", f"{pct(ar.train_support[0])} (deli meats → bread)"), T('Cặp càng phổ biến thì tác động đến doanh thu càng lớn.', 'The more common the pair, the larger the revenue impact.')],
        ['Confidence', T('Trong giỏ có A thì bao nhiêu % có thêm B.', 'Of baskets containing A, the % that also contain B.'), T(f"{pct(ar.test_confidence[0])} (kiểm thử)", f"{pct(ar.test_confidence[0])} (test)"), T('Cho biết độ tin cậy của quy tắc; giá trị tương tự giữa huấn luyện và kiểm thử là dấu hiệu ổn định.', 'Gauges the reliability of the rule; similar values in training and test indicate stability.')],
        ['Lift', T('Confidence chia xác suất B xuất hiện nói chung.', 'Confidence divided by the overall probability of B.'), T(f"{fmt(ar.test_lift[0], 2)} (thịt nguội → bánh mì); cao nhất {fmt(ar.test_lift.max(), 2)}", f"{fmt(ar.test_lift[0], 2)} (deli meats → bread); max {fmt(ar.test_lift.max(), 2)}"), T('Lift > 1: mua cùng nhiều hơn ngẫu nhiên. Dùng để bố trí kệ gần nhau hoặc khuyến mãi chéo, sau khi thử nghiệm.', 'Lift above 1: bought together more than by chance. Use it for adjacent shelving or cross-promotion after testing.')],
        [T('Bảng quy tắc', 'Rules table'), T(f"{fmt(len(ar))} quy tắc có ít nhất 100 giỏ huấn luyện và lift > 1, xếp theo confidence × log(lift).", f"{fmt(len(ar))} rules with at least 100 training baskets and lift above 1, ranked by confidence × log(lift)."), '812', T('Quy tắc được chọn trên dữ liệu huấn luyện; dữ liệu kiểm thử chỉ để kiểm tra độ ổn định.', 'Rules are selected on training data; the test data only checks stability.')],
        [T('Hit@3 và Recall@3', 'Hit@3 and Recall@3'), T('Ẩn một nhóm hàng trong giỏ, gợi ý 3 nhóm; Hit@3 là % giỏ có gợi ý đúng, Recall@3 là % nhóm ẩn tìm lại được.', 'Hide one category in a basket and recommend 3; Hit@3 is the % of baskets with a correct recommendation, Recall@3 the % of hidden categories recovered.'), f"{pct(AS['popularity']['hit_at_3'])} / {pct(AS['popularity']['recall_at_3'])}", T('Đo khả năng hoàn thiện giỏ hàng, không phải dự đoán lần mua tiếp theo.', 'Measures basket completion, not next-purchase prediction.')],
        [T('So sánh mô hình', 'Model comparison'), T('Hit@3 của quy tắc kết hợp so với xếp hạng theo độ phổ biến.', 'Hit@3 of association rules versus popularity ranking.'), f"{pct(AS['association']['hit_at_3'])} vs {pct(AS['popularity']['hit_at_3'])}", T('Phương án đơn giản thắng nên được chọn làm cơ sở; luật kết hợp dùng để giải thích và thử nghiệm trưng bày.', 'The simple approach wins and is the baseline; association rules are used for explanation and display experiments.')],
        [T('Chiến dịch coupon', 'Coupon campaigns'), T('Với mỗi chiến dịch, % hộ được giao chiến dịch có đổi coupon, kèm khoảng tin cậy.', 'For each campaign, the % of assigned households that redeemed, with a confidence interval.'), T(f"Loại A: {pct(ca.red['Type A'] / ca.hh['Type A'])}; B: {pct(ca.red['Type B'] / ca.hh['Type B'])}; C: {pct(ca.red['Type C'] / ca.hh['Type C'])}", f"Type A: {pct(ca.red['Type A'] / ca.hh['Type A'])}; B: {pct(ca.red['Type B'] / ca.hh['Type B'])}; C: {pct(ca.red['Type C'] / ca.hh['Type C'])}"), T('Tỷ lệ đổi, không phải hiệu quả tăng thêm: chưa có nhóm đối chứng.', 'A redemption rate, not incremental impact: there is no control group.')],
    ], T('Luật mua kèm cho ý tưởng trưng bày; hiệu quả thương mại phải được xác nhận bằng thử nghiệm đối chứng.', 'Association rules provide display ideas; commercial impact must be confirmed with controlled tests.'), y1=1340)

    fn = pd.read_csv(RUN / 'forecast_next_7_days.csv')
    fe = pd.read_csv(ROOT / 'outputs/word_report/forecast_error_contribution.csv')
    deep('forecast', T('5.9 Dự báo doanh thu', '5.9 Sales Forecast'),
         T('Dự báo doanh thu 7 ngày tới theo nhóm hàng và cho thấy mức tin cậy của dự báo.', 'Forecasts sales for the next 7 days by category group and shows how reliable the forecast is.'), [
        ['WAPE', T('Tổng sai số tuyệt đối chia tổng thực tế (không phải trung bình phần trăm từng nhóm).', 'Total absolute error divided by total actual (not an average of group percentages).'), f"{pct(FC['test_metrics'][0]['WAPE'], 2)} (test); {pct(FC['validation_leaderboard'][0]['WAPE'], 2)} (validation)", T('Dự báo lệch trung bình khoảng 15% doanh thu thực; test cao hơn validation vì có giai đoạn Giáng sinh.', 'Forecasts miss actual sales by about 15% on average; test is higher than validation because it contains the Christmas period.')],
        ['Bias', T('(Dự báo − thực tế) chia tổng thực tế.', '(Forecast − actual) divided by total actual.'), pct(FC['test_metrics'][0]['bias'], 2), T('Âm nhẹ: dự báo thấp hơn thực tế khoảng 1,5%; không có thiên lệch hệ thống đáng kể.', 'Slightly negative: forecasts are about 1.5% below actual; no material systematic bias.')],
        ['Coverage', T('% giá trị thực nằm trong dải dự báo (dải mục tiêu 90%).', '% of actual values falling inside the forecast band (target 90%).'), pct(FC['interval_empirical_test_coverage']), T('Dải còn hẹp: chưa dùng để cam kết mức phục vụ tồn kho; cần hiệu chỉnh khi có dữ liệu SKU.', 'The band is too narrow: do not use it to commit inventory service levels; recalibrate once SKU data is available.')],
        [T('Dự báo 7 ngày tới', 'Next 7-day forecast'), T('Tổng dự báo 01–07/01/2018 của 20 nhóm hàng và nhóm còn lại, kèm dải dưới và trên.', 'Total forecast for 1–7 January 2018 across 20 category groups plus the remainder, with lower and upper bands.'), 'USD ' + fmt(fn.forecast.sum()), T('Là dự báo tham khảo ở mức nhóm hàng của mẫu hộ, chưa phải kế hoạch mua hàng.', 'A reference forecast at category-group level for the household sample, not yet a purchasing plan.')],
        [T('Dự báo so với thực tế', 'Forecast vs actual'), T('Bốn tuần kiểm thử: đường thực tế và đường dự báo của mô hình được chọn.', 'Four test weeks: the actual line versus the selected model\'s forecast.'), T('Lệch lớn nhất tuần 24/12', 'Largest miss in week of 24 Dec'), T('Mô hình khó bắt các đỉnh và đáy lễ hội; cần biến lịch lễ khi có dữ liệu nhiều năm.', 'The model struggles with holiday peaks and troughs; holiday calendar features are needed once multi-year data is available.')],
        [T('Quyết định lựa chọn mô hình', 'Model selection panel'), T('Mô hình được chọn trên validation, không chọn lại theo kết quả kiểm thử.', 'The model is selected on validation and never re-selected on test results.'), T('Champion: trung bình 28 ngày', 'Champion: 28-day mean'), T('Nguyên tắc chống "nhìn trộm" kết quả kiểm thử.', 'A safeguard against peeking at the test results.')],
        [T('Đóng góp vào sai số', 'Error contribution'), T('Mỗi nhóm hàng chiếm bao nhiêu % tổng sai số tuyệt đối.', 'The % of total absolute error contributed by each group.'), T(f"OTHER {pct(fe.error_share[0])}; {fe.series[2]} {pct(fe.error_share[2])}", f"OTHER {pct(fe.error_share[0])}; {fe.series[2]} {pct(fe.error_share[2])}"), T('Nhóm OTHER (60% doanh thu) chi phối sai số; CANDY - PACKAGED có WAPE 53%: cần xử lý riêng.', 'The OTHER group (60% of sales) dominates error; CANDY - PACKAGED has a 53% WAPE and needs separate handling.')],
        [T('Bảng kết quả theo mô hình', 'Results by model'), T('Sáu mô hình ứng viên với WAPE validation, test, bias và vai trò.', 'Six candidate models with validation WAPE, test WAPE, bias and role.'), '6', T('Minh bạch toàn bộ phương án đã thử, không chỉ phương án thắng.', 'Full transparency on every approach tried, not only the winner.')],
    ], T('Dùng dự báo để định hướng kế hoạch; kiểm tra bảng sai số theo nhóm trước khi tin vào từng nhóm cụ thể.', 'Use the forecast to guide planning; check the error table by group before trusting any specific group.'), y1=1340)

    rc_ = pd.read_csv(ROOT / 'outputs/word_report/risk_capacity.csv')
    cal = pd.read_csv(ROOT / 'outputs/word_report/risk_calibration.csv')
    fi = pd.read_csv(RUN / 'risk_feature_importance.csv')
    ml20 = rc_[(rc_.model == 'hist_gradient') & (abs(rc_.fraction - .2) < 1e-9)]
    deep('risk', T('5.10 Rủi ro rời bỏ', '5.10 Churn Risk'),
         T('Xếp thứ tự khách có khả năng không mua trong 28 ngày tới để CRM ưu tiên chăm sóc.', 'Ranks customers likely not to buy in the next 28 days so CRM can prioritise outreach.'), [
        [T('Nhãn mục tiêu', 'Target label'), T('Hộ có mua trong 90 ngày trước mốc chấm điểm nhưng không mua dương trong 28 ngày sau.', 'A household that bought in the 90 days before the scoring date but did not buy in the following 28 days.'), T('Tỷ lệ nền 14,8%', 'Base rate 14.8%'), T('Không đồng nghĩa rời bỏ vĩnh viễn; chỉ là gián đoạn mua.', 'Does not mean permanent churn; only a gap in purchasing.')],
        ['Average precision', T('Diện tích dưới đường precision–recall; thước đo chất lượng xếp hạng.', 'Area under the precision–recall curve; a measure of ranking quality.'), T('0,456 so với 0,380 (recency)', '0.456 vs 0.380 (recency)'), T('Mô hình xếp hạng tốt hơn quy tắc đơn giản; khác biệt có ý nghĩa thống kê (khoảng tin cậy 95% của chênh AP: 0,053–0,098).', 'The model ranks better than the simple rule; the difference is statistically meaningful (95% CI of the AP difference: 0.053–0.098).')],
        ['Precision', T('Trong số khách được chọn, % thực sự không mua.', 'Of the customers selected, the % who really did not buy.'), T('44,3%', '44.3%'), T('Cứ 100 khách liên hệ có khoảng 44 khách thực sự có nguy cơ; phần còn lại vẫn mua, nên chi phí ưu đãi cần cân nhắc.', 'Out of 100 customers contacted, about 44 are genuinely at risk; the rest would have bought anyway, so incentive cost needs care.')],
        ['Recall', T('Trong tất cả khách thực sự không mua, % được bắt trong nhóm chọn.', 'Of all customers who really did not buy, the % captured in the selected group.'), T('59,9%', '59.9%'), T('Chọn 20% khách bắt được gần 60% khách ngừng mua.', 'Selecting 20% of customers captures nearly 60% of those who stop buying.')],
        ['Lift', T('Precision chia tỷ lệ nền.', 'Precision divided by the base rate.'), T('3,00x', '3.00x'), T('Gấp 3 lần chọn ngẫu nhiên.', 'Three times random selection.')],
        [T('Thanh chọn mức chọn', 'Selection slider'), T('Thay đổi % khách chọn (5%–50%) để xem đánh đổi precision và recall.', 'Change the % of customers selected (5%–50%) to see the precision–recall trade-off.'), T('5%: precision 57%; 50%: recall 93%', '5%: precision 57%; 50%: recall 93%'), T('Chọn ít thì chính xác nhưng bỏ sót; chọn nhiều thì bắt đủ nhưng tốn chi phí. Mức chọn tối ưu phụ thuộc chi phí ưu đãi và giá trị khách.', 'Selecting few is precise but misses lapsers; selecting many captures more but costs more. The optimum depends on incentive cost and customer value.')],
        [T('Tầm quan trọng của biến', 'Feature importance'), T('Mức giảm chất lượng (AP) khi xáo trộn ngẫu nhiên từng biến trên tập validation.', 'The drop in quality (AP) when each variable is randomly shuffled on the validation set.'), T(f"{fi.feature[0]} {fmt(fi.importance_mean[0], 3)}; {fi.feature[1]}; {fi.feature[2]}", f"{fi.feature[0]} {fmt(fi.importance_mean[0], 3)}; {fi.feature[1]}; {fi.feature[2]}"), T('Mô hình chủ yếu dựa vào tần suất và độ gần đây của lần mua: hợp lý về mặt kinh doanh, dễ giải thích với CRM.', 'The model relies mainly on purchase frequency and recency: sensible commercially and easy to explain to CRM.')],
        [T('Hiệu chỉnh theo decile', 'Decile calibration'), T('Chia khách thành 10 nhóm theo điểm; so xác suất dự đoán với tỷ lệ không mua thực tế.', 'Splits customers into 10 groups by score; compares predicted probability with the actual no-purchase rate.'), T(f"Decile cao nhất: dự đoán {pct(cal.predicted.iloc[-1], 0)}, thực tế {pct(cal.observed.iloc[-1], 0)}", f"Top decile: predicted {pct(cal.predicted.iloc[-1], 0)}, actual {pct(cal.observed.iloc[-1], 0)}"), T('Điểm số khớp tốt với thực tế ở nhóm rủi ro cao; dùng điểm để xếp hạng.', 'Scores align well with reality in the high-risk groups; use the score for ranking.')],
        [T('Danh sách khách ưu tiên', 'Priority customer list'), T('Danh sách hộ kèm điểm rủi ro, xuất được cho CRM.', 'List of households with risk scores, exportable for CRM.'), '—', T('Mọi liên hệ đều qua người phê duyệt; hệ thống không tự gửi ưu đãi.', 'Every contact goes through an approver; the system never sends offers automatically.')],
    ], T('Chọn mức chọn theo ngân sách ưu đãi; đo uplift bằng nhóm đối chứng trước khi mở rộng.', 'Set the selection size by incentive budget; measure uplift with a control group before scaling.'), y1=1340)

    deep('inference', T('5.11 Chấm điểm dữ liệu mới', '5.11 Score New Data'),
         T('Cho phép doanh nghiệp tự chạy bộ mô hình Probit trên dữ liệu của mình ngay trong trình duyệt.', 'Lets the client run the Probit model suite on its own data directly in the browser.'), [
        [T('Năm bước', 'Five steps'), T('CSV và ánh xạ cột → kiểm tra dữ liệu → dựng biến 90 ngày → chạy Probit → kết quả và kiểm toán.', 'CSV and column mapping → data validation → 90-day features → Probit scoring → results and audit.'), '5', T('Luồng giống quy trình sản xuất, giúp doanh nghiệp thử trước khi tích hợp.', 'Mirrors the production flow so the client can trial it before integration.')],
        [T('Chế độ nạp', 'Load mode'), T('Snapshot độc lập đủ 90 ngày, hoặc nối thêm sau dữ liệu nền đến 31/12/2017.', 'A standalone 90-day snapshot, or an append after the base data through 31 Dec 2017.'), '—', T('Snapshot không ghép với dữ liệu cũ; mã giỏ và khách trùng nội dung không bị nhân đôi.', 'A snapshot is not merged with old data; baskets and customers with identical content are not duplicated.')],
        [T('Kiểm tra dữ liệu', 'Data validation'), T('Kiểm tra cột bắt buộc, kiểu dữ liệu, độ phủ ngày, trùng lặp và khai báo bao phủ đầy đủ.', 'Checks required columns, data types, date coverage, duplicates and a confirmation of full coverage.'), '—', T('Dữ liệu không đạt sẽ bị chặn và nêu lý do, không chấm điểm âm thầm.', 'Failing data is blocked with the reason rather than scored silently.')],
        [T('Năm xác suất đầu ra', 'Five probability outputs'), T('Không mua trong 28 ngày; thời điểm quay lại; số giỏ 28 ngày tới; chi tiêu giảm từ 30%; mua có giảm giá.', 'No purchase in 28 days; return timing; basket count over the next 28 days; spend drop of 30% or more; discounted purchase.'), '5', T('Mỗi xác suất phục vụ một quyết định: giữ chân, kế hoạch, cảnh báo, khuyến mãi.', 'Each probability serves a decision: retention, planning, early warning, promotions.')],
        [T('Hồ sơ mô hình', 'Model card'), T('Phiên bản, ngày huấn luyện, biến, hệ số, ngưỡng, kết quả kiểm thử và giới hạn.', 'Version, training date, features, coefficients, thresholds, test results and limitations.'), T('Huấn luyện đến 31/12/2017', 'Trained through 31 Dec 2017'), T('Cho phép kiểm toán trước khi sử dụng.', 'Enables audit before use.')],
        [T('Xuất kết quả và kiểm toán', 'Export and audit'), T('CSV xác suất theo hộ cùng bản ghi kiểm toán số dòng hợp lệ, dòng loại và tham số.', 'CSV of probabilities per household plus an audit record of valid lines, excluded lines and parameters.'), '—', T('Đảm bảo kết quả truy vết được về dữ liệu đầu vào.', 'Ensures results are traceable to the input data.')],
    ], T('Mô hình không được huấn luyện lại khi tải file: chỉ chấm điểm. Áp dụng cho doanh nghiệp mới cần pilot để xác nhận.', 'Models are not retrained on upload: they only score. Applying them to a new business needs a pilot to confirm.'), y1=1340)

    deep('finance', T('5.12 Lợi nhuận và vốn lưu động', '5.12 Profitability and Working Capital'),
         T('Mô phỏng độ nhạy lợi nhuận và vốn tồn kho khi chưa có dữ liệu chi phí thực; mọi tham số do người dùng nhập.', 'Simulates profit and inventory-capital sensitivity before actual cost data exists; every parameter is a user input.'), [
        [T('Biên lợi nhuận gộp', 'Gross margin'), T('Giả định % doanh thu còn lại sau giá vốn.', 'Assumed % of sales remaining after cost of goods.'), '25%', T('Thay bằng biên thực theo ngành khi có giá vốn.', 'Replace with actual margin by department once cost data exists.')],
        [T('Chi phí biến đổi', 'Variable cost'), T('Giả định % doanh thu cho chi phí biến đổi (ví dụ thanh toán, bao bì, nhân công theo ca).', 'Assumed % of sales for variable costs (e.g. payments, packaging, shift labour).'), '8%', T('Cùng với biên gộp tạo ra tỷ lệ đóng góp.', 'Together with gross margin it determines the contribution margin.')],
        [T('Chi phí cố định', 'Fixed costs'), T('Giả định bằng 12% doanh thu tháng gốc (thuê mặt bằng, lương cố định).', 'Assumed at 12% of the base-month sales (rent, fixed payroll).'), 'USD 50.626', T('Không đổi khi doanh thu thay đổi trong ngắn hạn.', 'Does not change with sales in the short term.')],
        [T('Tỷ lệ đóng góp', 'Contribution margin'), T('Biên gộp trừ chi phí biến đổi, trừ mức giảm biên giả định.', 'Gross margin less variable cost, less the assumed margin erosion.'), T('16% = 25% − 8% − 1 điểm', '16% = 25% − 8% − 1 pt'), T('Mỗi USD doanh thu thêm đóng góp 0,16 USD để bù chi phí cố định.', 'Each extra dollar of sales contributes 0.16 to cover fixed costs.')],
        [T('Kết quả sau chi phí cố định', 'Result after fixed costs'), T('Doanh thu mô phỏng × tỷ lệ đóng góp − chi phí cố định.', 'Simulated sales × contribution margin − fixed costs.'), T('USD 20.250 (−844 so với nền)', 'USD 20,250 (−844 vs base)'), T('Không phải EBITDA. Cho thấy giảm biên 1 điểm làm mất 844 USD dù doanh thu tăng 5%.', 'Not EBITDA. Shows that a 1-point margin drop costs USD 844 even with 5% higher sales.')],
        [T('Doanh thu hòa vốn', 'Break-even sales'), T('Chi phí cố định chia tỷ lệ đóng góp.', 'Fixed costs divided by contribution margin.'), 'USD 316.413', T('Doanh thu tối thiểu để không lỗ; so với doanh thu hiện tại cho biết "đệm an toàn".', 'The minimum sales to avoid a loss; compared with current sales it gives the safety cushion.')],
        [T('Tăng trưởng cần để giữ lãi', 'Growth to hold profit'), T('Tỷ lệ đóng góp nền chia tỷ lệ đóng góp mới, trừ 1.', 'Base contribution margin divided by new contribution margin, minus 1.'), '6,3%', T('Giảm biên 1 điểm đòi hỏi tăng doanh thu 6,3% để giữ lãi: chiết khấu sâu phải tạo đủ giỏ hàng bù lại.', 'A 1-point margin cut needs 6.3% more sales to hold profit: deeper discounts must generate enough extra baskets.')],
        [T('Bảng độ nhạy', 'Sensitivity grid'), T('Kết quả sau chi phí cố định theo thay đổi doanh thu (cột) và thay đổi biên (hàng).', 'Result after fixed costs by change in sales (columns) and change in margin (rows).'), '—', T('Trả lời nhanh "nếu biên giảm x và doanh thu tăng y thì sao".', 'Answers "what if margin drops x and sales rise y" at a glance.')],
        [T('Vốn tồn kho giải phóng', 'Inventory capital released'), T('Giá vốn mỗi ngày × số ngày tồn giảm.', 'Cost of goods per day × reduction in inventory days.'), T('USD 71.448 = 10.206,83 × 7 ngày', 'USD 71,448 = 10,206.83 × 7 days'), T('Độ nhạy cơ học: không khẳng định dòng tiền thực; cần giữ mức phục vụ và công nợ. CCC = DIO + DSO − DPO.', 'A mechanical sensitivity: not a cash-flow claim; service levels and payables must hold. CCC = DIO + DSO − DPO.')],
    ], T('Khi có giá vốn và chi phí thật, các tham số mặc định được thay bằng dữ liệu của doanh nghiệp và màn hình này trở thành bảng điều hành lợi nhuận.', 'Once real cost and expense data is connected, the defaults are replaced by client data and this screen becomes the profit control panel.'), y1=1340)

    deep('quality', T('5.13 Chất lượng dữ liệu và định nghĩa; 5.14 Giao dịch chi tiết', '5.13 Data Quality and Definitions; 5.14 Transaction Explorer'),
         T('Hai màn hình tạo niềm tin: một nêu rõ dữ liệu sạch đến đâu, một cho phép truy từng dòng giao dịch.', 'Two screens that create trust: one states how clean the data is, the other lets users trace every transaction line.'), [
        [T('Phạm vi và đối soát', 'Scope and reconciliation'), T('Số dòng, hộ, cửa hàng, giỏ; tổng tiền gốc đối chiếu với tổng sau xử lý.', 'Lines, households, stores, baskets; raw totals reconciled with processed totals.'), T('1.468.773 dòng; USD 4.594.146', '1,468,773 lines; USD 4,594,146'), T('Mọi chỉ tiêu trên dashboard đều quay về tổng này; lệch tổng là cờ dừng.', 'Every dashboard figure ties back to this total; a mismatch is a stop signal.')],
        [T('Dòng ngoài kỳ, thiếu SKU, không dương', 'Out-of-period, unmapped, non-positive lines'), T('Các dòng bị loại hoặc giữ riêng, kèm lý do.', 'Lines excluded or kept apart, with reasons.'), T('534 / 4.833 (0,33%) / 11.266', '534 / 4,833 (0.33%) / 11,266'), T('Không loại âm thầm: mỗi ngoại lệ có bảng riêng để bộ phận nghiệp vụ xử lý.', 'Nothing is dropped silently: each exception has its own table for business follow-up.')],
        [T('Ngày không có bản ghi', 'Day without records'), T('Phát hiện khoảng trống trên lịch giao dịch.', 'Detects gaps in the transaction calendar.'), '2017-12-25', T('Không kết luận là cửa hàng đóng cửa hay không có nhu cầu; cần xác minh với nguồn.', 'No conclusion that stores were closed or demand was nil; verify with the source.')],
        [T('Định nghĩa chỉ tiêu', 'KPI definitions'), T('Bảng định nghĩa từng chỉ tiêu dùng trong hệ thống.', 'A table defining every KPI used in the system.'), T('12 định nghĩa', '12 definitions'), T('Cơ sở thống nhất cách tính giữa tài chính, kinh doanh và IT.', 'The basis for aligning calculations across finance, commercial and IT.')],
        [T('Giao dịch chi tiết', 'Transaction explorer'), T('Tìm kiếm và phân trang toàn bộ dòng giao dịch khớp bộ lọc; xuất CSV.', 'Search and page through every transaction line matching the filters; export CSV.'), T('129.553 dòng trong tháng 12', '129,553 lines in December'), T('Cho phép chứng minh bất kỳ con số nào bằng dòng giao dịch gốc.', 'Lets users prove any number with the underlying transaction lines.')],
    ], T('Hai màn hình này là nền tảng cho niềm tin: số liệu không chỉ đẹp mà còn truy vết được.', 'These two screens underpin trust: the numbers are not only presentable but traceable.'), shots=True, y1=1340)

    # ------------------------------------------------------------ 6 models
    H1(T('6. Mô hình dự báo và chấm điểm', '6. Predictive Models'))
    P(T('Mọi mô hình tuân thủ cùng một quy trình: chia dữ liệu theo thời gian, chọn mô hình trên tập validation, đánh giá một lần trên tập kiểm thử và luôn so sánh với một phương án cơ sở đơn giản. Mô hình chỉ được dùng khi vượt cơ sở.',
        'All models follow one protocol: time-based splits, model selection on a validation set, a single evaluation on the test set, and comparison against a simple baseline. A model is used only if it beats the baseline.'))
    doc.add_heading(T('6.1 Dự báo doanh thu theo nhóm hàng', '6.1 Sales forecast by category group'), level=2)
    names = {'mean_28_days': T('Trung bình 28 ngày (được chọn)', '28-day mean (selected)'), 'hist_gradient_small': 'Gradient boosting (S)', 'hist_gradient_medium': 'Gradient boosting (M)', 'ridge': 'Ridge', 'extra_trees': 'Extra Trees', 'last_7_days': T('Lặp 7 ngày trước', 'Last-7-day repeat')}
    val = {x['model']: x for x in FC['validation_leaderboard']}
    rows = [[names.get(x['model'], x['model']), pct(val[x['model']]['WAPE'], 2) if x['model'] in val else '–', pct(x['WAPE'], 2), pct(x['bias'], 2)] for x in FC['test_metrics']]
    table([T('Mô hình', 'Model'), 'WAPE validation', 'WAPE test', 'Bias'], rows, [7, 3.4, 3.3, 3.3], align_right=(1, 2, 3))
    P(T(f"Mô hình đơn giản (trung bình 28 ngày) đạt WAPE {pct(FC['test_metrics'][0]['WAPE'])} trên kiểm thử, tốt hơn các mô hình máy học ({pct(min(x['WAPE'] for x in FC['test_metrics'][1:]))} đến {pct(max(x['WAPE'] for x in FC['test_metrics'][1:]))}). Kết luận: ở mức nhóm hàng và với 12 tháng dữ liệu, độ phức tạp thêm chưa tạo lợi thế; mô hình sẽ được huấn luyện lại ở mức SKU–cửa hàng khi có đủ lịch sử và dữ liệu tồn kho.",
        f"The simple 28-day mean reaches a test WAPE of {pct(FC['test_metrics'][0]['WAPE'])}, better than the machine-learning models ({pct(min(x['WAPE'] for x in FC['test_metrics'][1:]))} to {pct(max(x['WAPE'] for x in FC['test_metrics'][1:]))}). Conclusion: at category-group level with 12 months of data, extra complexity does not add value; models will be retrained at SKU-store level once sufficient history and inventory data are available."))
    shot('forecast', T('Dự báo doanh thu: so sánh mô hình và dự báo 7 ngày', 'Sales forecast: model comparison and 7-day forecast'), y0=190, y1=1340)
    doc.add_heading(T('6.2 Rủi ro rời bỏ khách hàng', '6.2 Customer churn risk'), level=2)
    tm = [x for x in RK['test_metrics']]
    ml = [x for x in tm if x['model'] == 'hist_gradient']
    rc = [x for x in tm if x['model'] == 'recency_rule']
    avg = lambda arr, k: sum(x[k] for x in arr) / len(arr)
    table([T('Chỉ tiêu (top 20% điểm, 2 mốc kiểm thử)', 'Metric (top 20% of scores, 2 test origins)'), T('Mô hình gradient boosting', 'Gradient boosting model'), T('Quy tắc recency', 'Recency rule')], [
        ['ROC AUC', fmt(avg(ml, 'ROC_AUC'), 3), fmt(avg(rc, 'ROC_AUC'), 3)],
        ['Average precision', fmt(avg(ml, 'PR_AUC_AP'), 3), fmt(avg(rc, 'PR_AUC_AP'), 3)],
        ['Precision', pct(avg(ml, 'precision_top20')), pct(avg(rc, 'precision_top20'))],
        ['Recall', pct(avg(ml, 'recall_top20')), pct(avg(rc, 'recall_top20'))],
        ['Lift', fmt(avg(ml, 'lift_top20'), 2) + 'x', fmt(avg(rc, 'lift_top20'), 2) + 'x'],
    ], [8, 4.5, 4.5], align_right=(1, 2))
    P(T('Nhãn là hộ có mua trong 90 ngày trước nhưng không mua trong 28 ngày sau mốc chấm điểm. Mô hình hơn quy tắc recency ở mọi chỉ tiêu và ổn định ở hai mốc kiểm thử. Bước tiếp theo là thử nghiệm có nhóm đối chứng để đo mức tăng thực của hoạt động giữ chân.',
        'The label is a household that bought in the prior 90 days but not in the 28 days after the scoring date. The model beats the recency rule on every metric and is stable across both test origins. The next step is a controlled test to measure the true uplift of retention actions.'))
    doc.add_heading(T('6.3 Gợi ý mua kèm và phân khúc khách hàng', '6.3 Basket recommendations and customer segments'), level=2)
    P(T(f"Đã khai thác 812 quy tắc mua kèm. Trên {fmt(AS['association']['evaluated_baskets'])} giỏ kiểm thử, phương án phổ biến (popularity) đạt Hit@3 {pct(AS['popularity']['hit_at_3'])}, nhỉnh hơn quy tắc kết hợp {pct(AS['association']['hit_at_3'])}; vì vậy phương án phổ biến được chọn làm cơ sở. "
        f"Phân khúc K-means chọn k = {AN['clustering']['selected_k']} (silhouette {fmt(AN['clustering']['silhouette'], 3)}, độ ổn định ARI {fmt(AN['clustering']['seed_stability_ARI'], 3)}).",
        f"812 association rules were mined. On {fmt(AS['association']['evaluated_baskets'])} test baskets, the popularity approach achieves Hit@3 of {pct(AS['popularity']['hit_at_3'])}, slightly above association rules at {pct(AS['association']['hit_at_3'])}; popularity is therefore used as the baseline. "
        f"K-means segmentation selects k = {AN['clustering']['selected_k']} (silhouette {fmt(AN['clustering']['silhouette'], 3)}, stability ARI {fmt(AN['clustering']['seed_stability_ARI'], 3)})."))
    segname = {0: T('Giá trị cao, cần kiểm tra giảm mua', 'High value, declining'), 1: T('Khách hàng chủ lực', 'Core customers'), 2: T('Mua thường xuyên', 'Frequent buyers'), 3: T('Mới xuất hiện', 'Newly observed'), 4: T('Nhóm còn lại', 'Other')}
    table([T('Phân khúc', 'Segment'), T('Số hộ', 'Households'), T('Doanh thu (USD)', 'Net sales (USD)'), T('Tỷ trọng', 'Share')],
          [[segname[i], fmt(r.households), fmt(r.sales), pct(r.sales_share)] for i, r in SEG.iterrows()], [6.4, 3.2, 4.2, 3.2], align_right=(1, 2, 3))
    doc.add_heading(T('6.4 Bộ năm mô hình Probit', '6.4 Five Probit models'), level=2)
    P(T('Bộ mô hình Probit đã huấn luyện đến 31/12/2017 chấm điểm dữ liệu mới và trả về xác suất liên tục. Mỗi mô hình được so với phương án cơ sở bằng log-loss.', 'The Probit suite, trained through 31 December 2017, scores new data and returns continuous probabilities. Each model is compared with a baseline on log-loss.'))
    ev = {}
    for e in REG['evaluations']:
        ev.setdefault(e['model'], []).append(e)
    mt = {'Không mua dương trong 28 ngày': T('Không mua trong 28 ngày', 'No purchase in 28 days'), 'Thời gian tới lần mua tiếp theo': T('Thời gian đến lần mua tiếp theo', 'Time to next purchase'), 'Phân phối số giỏ mua dương trong 28 ngày': T('Phân phối số giỏ trong 28 ngày', 'Basket count in 28 days'), 'Giá trị mua 28 ngày tới giảm ít nhất 30%': T('Chi tiêu giảm từ 30% trở lên', 'Spend drop of 30% or more'), 'Có lần mua được giảm giá trong 28 ngày': T('Có mua giảm giá trong 28 ngày', 'Discounted purchase in 28 days')}
    rows = []
    for k, arr in ev.items():
        m_ = sum(x['metrics']['log_loss'] for x in arr) / len(arr)
        b_ = sum(x['baseline']['log_loss'] for x in arr) / len(arr)
        rows.append([mt.get(k, k), arr[0]['kind'].capitalize(), fmt(m_, 3), fmt(b_, 3), pct(1 - m_ / b_, 0)])
    table([T('Mô hình', 'Model'), T('Loại', 'Type'), 'Log-loss', T('Log-loss cơ sở', 'Baseline log-loss'), T('Cải thiện', 'Improvement')], rows, [6.2, 2.4, 2.6, 3.2, 2.6], align_right=(2, 3, 4))
    callout(T('Quản trị mô hình', 'Model governance'), T('Hai mốc kiểm thử chồng lấn 28 ngày nên chưa phải hai lần lặp độc lập. Mô hình được giữ cố định, không chọn lại theo kết quả kiểm thử; mọi áp dụng cho doanh nghiệp mới cần pilot trước khi dùng để quyết định ngân sách.', 'The two test origins overlap by 28 days and are not independent replications. Models are frozen and not reselected on test results; any application to a new business requires a pilot before budget decisions.'), fill='FBF1DC', bar='D19A2B')

    # ------------------------------------------------------------ 6 (cont.) AI deep dive
    doc.add_heading(T('6.5 Từ câu hỏi kinh doanh đến mô hình', '6.5 From Business Question to Model'), level=2)
    P(T('Mỗi mô hình được thiết kế ngược từ một quyết định cụ thể. Bảng dưới đây cho biết mô hình trả lời câu hỏi gì, dự đoán đại lượng nào, đánh giá bằng chỉ tiêu nào và so với phương án cơ sở nào.',
        'Each model is designed backwards from a specific decision. The table shows the question it answers, the quantity it predicts, the metric used to judge it and the baseline it must beat.'))
    table([T('Mô hình', 'Model'), T('Câu hỏi kinh doanh', 'Business question'), T('Đại lượng dự đoán', 'Predicted quantity'), T('Chỉ tiêu và cơ sở', 'Metric and baseline')], [
        [T('Dự báo doanh thu', 'Sales forecast'), T('Doanh thu 7 ngày tới của từng nhóm hàng là bao nhiêu?', 'How much will each category group sell over the next 7 days?'), T('Tổng doanh thu 7 ngày của 20 nhóm hàng lớn nhất và nhóm còn lại (21 chuỗi), mỗi tuần một mốc', 'Total 7-day sales for the 20 largest category groups plus the remainder (21 series), one origin per week'), T('WAPE; cơ sở: trung bình 28 ngày và lặp 7 ngày trước', 'WAPE; baselines: 28-day mean and last-7-day repeat')],
        [T('Rủi ro rời bỏ', 'Churn risk'), T('Khách nào có khả năng không quay lại trong 28 ngày?', 'Which customers are unlikely to return within 28 days?'), T('Xác suất hộ không có lần mua dương nào trong 28 ngày sau mốc, trong nhóm đã mua trong 90 ngày trước', 'Probability that a household makes no positive purchase in the 28 days after the origin, among those who bought in the prior 90 days'), T('Average precision, precision/recall/lift ở top 20%; cơ sở: quy tắc recency', 'Average precision, precision/recall/lift at top 20%; baseline: recency rule')],
        [T('Gợi ý mua kèm', 'Basket recommendation'), T('Nên gợi ý nhóm hàng nào cho giỏ đang có?', 'Which categories should be suggested for the basket at hand?'), T('Nhóm hàng bị ẩn trong giỏ có từ 2 nhóm trở lên', 'A category hidden from baskets with two or more categories'), T('Hit@3, Recall@3; cơ sở: độ phổ biến', 'Hit@3, Recall@3; baseline: popularity')],
        [T('Phân khúc khách hàng', 'Customer segmentation'), T('Có những kiểu hành vi mua nào?', 'What distinct buying behaviours exist?'), T('Nhóm theo recency, tần suất, giá trị, độ rộng nhóm hàng (học không giám sát)', 'Groups by recency, frequency, value and category breadth (unsupervised)'), T('Silhouette và độ ổn định ARI', 'Silhouette and ARI stability')],
        [T('Bộ năm mô hình Probit', 'Five-model Probit suite'), T('Mức độ gián đoạn, thay đổi chi tiêu và độ nhạy khuyến mãi của khách ra sao?', 'How exposed is a customer to a lapse, a spend drop or promotion sensitivity?'), T('Năm xác suất liên tục trên tám biến lịch sử 90 ngày', 'Five continuous probabilities from eight 90-day history features'), T('Log-loss so với phương án cơ sở tỷ lệ nền', 'Log-loss versus a base-rate baseline')],
    ], [2.8, 4.0, 5.6, 4.6])

    doc.add_heading(T('6.6 Biến đầu vào và chống rò rỉ dữ liệu', '6.6 Inputs and Leakage Control'), level=2)
    P(T('Rủi ro lớn nhất của mô hình dự báo là "rò rỉ": vô tình dùng thông tin của tương lai khi huấn luyện, làm kết quả thử nghiệm đẹp hơn thực tế. Hệ thống chặn rò rỉ bằng thiết kế dữ liệu và bằng kiểm thử tự động.',
        'The biggest risk in predictive modelling is leakage: unintentionally using future information during training, which makes test results look better than reality. The system blocks leakage by data design and by automated tests.'))
    table([T('Mô hình', 'Model'), T('Nhóm biến', 'Feature groups'), T('Nguyên tắc thời gian', 'Timing rule')], [
        [T('Dự báo doanh thu', 'Sales forecast'), T('Thứ trong tuần, tháng, ngày trong năm, mã chuỗi; doanh thu trễ (0, 1, 6, 7, 13, 27 ngày), trung bình và độ lệch chuẩn trượt 7/14/28/56 ngày, tổng 7 ngày trước, xu hướng 7/28; mục tiêu chuẩn hóa bằng trung bình 28 ngày × 7', 'Weekday, month, day of year, series code; lagged sales (0, 1, 6, 7, 13, 27 days), rolling mean and standard deviation over 7/14/28/56 days, prior 7-day total, 7/28 trend; the target is normalised by the 28-day mean × 7'), T('Chỉ dùng dữ liệu đến hết ngày gốc; nhãn là đúng 7 ngày kế tiếp', 'Only data up to the origin date; the label is exactly the next 7 days')],
        [T('Rủi ro rời bỏ', 'Churn risk'), T('17 biến: số lần mua, doanh thu và số nhóm hàng trong 7, 28, 56, 90 ngày; recency; thời gian quan sát; tỷ lệ dòng có chiết khấu 90 ngày; AOV 90 ngày; tỷ số doanh thu', '17 features: visits, sales and categories over 7, 28, 56 and 90 days; recency; observed tenure; 90-day discounted-line share; 90-day AOV; sales ratio'), T('Biến tính đến mốc chấm điểm; nhãn nằm trong 28 ngày sau mốc; hộ không mua quá 90 ngày không được chấm điểm', 'Features computed up to the scoring date; the label sits in the 28 days after; households inactive over 90 days are not scored')],
        [T('Gợi ý mua kèm', 'Basket recommendation'), T('Cặp nhóm hàng đồng xuất hiện trong giỏ; từ vựng nhóm hàng cố định', 'Category pairs co-occurring in baskets; a frozen category vocabulary'), T('Quy tắc học đến 03/09; chọn mô hình 04/09–01/10; kiểm thử 02/10–31/12', 'Rules learnt through 3 Sep; model chosen 4 Sep–1 Oct; test 2 Oct–31 Dec')],
        [T('Bộ Probit', 'Probit suite'), T('Tám biến lịch sử 90 ngày: recency, số lần mua 7/28/90 ngày, tỷ lệ doanh thu, số nhóm hàng 28 ngày, tỷ lệ dòng chiết khấu 90 ngày, AOV 90 ngày', 'Eight 90-day history features: recency, visits over 7/28/90 days, sales ratio, categories in 28 days, 90-day discounted-line share, 90-day AOV'), T('Cố định đến 31/12/2017; không huấn luyện lại khi nạp dữ liệu', 'Frozen through 31 Dec 2017; not retrained when data is uploaded')],
    ], [3.0, 8.0, 6.0])
    P(T('Chín kiểm thử tự động chạy cùng quy trình, nhằm bảo đảm các nguyên tắc trên không bị phá vỡ khi mã nguồn thay đổi:', 'Nine automated tests run with the process to make sure these rules are never broken when the code changes:'), bold=True)
    bullets([
        T('Nhãn dự báo đúng bằng tổng 7 ngày kế tiếp.', 'The forecast label equals exactly the next seven days.'),
        T('Biến dự báo và biến rủi ro không phụ thuộc dữ liệu tương lai (hai kiểm thử).', 'Forecast and risk features do not depend on future data (two tests).'),
        T('Từ vựng nhóm hàng của dự báo được đóng băng khi chấm điểm.', 'The forecast category vocabulary is frozen at scoring time.'),
        T('Nhãn rủi ro bao gồm ngày thứ 28 và loại ngày thứ 29.', 'The risk label includes day 28 and excludes day 29.'),
        T('Hộ không hoạt động quá 90 ngày không được chấm điểm.', 'Households inactive for over 90 days are not scored.'),
        T('WAPE tính theo tổng trọng số, không lấy trung bình phần trăm.', 'WAPE is computed on total weight, not as an average of percentages.'),
        T('Công suất top 20% và lift được tính đúng.', 'Top-20% capacity and lift are computed correctly.'),
        T('Gợi ý tôn trọng mô hình đã chọn và không bao giờ gợi ý chính nhóm hàng đã có.', 'Recommendations respect the selected model and never suggest the seed category itself.'),
    ])

    doc.add_heading(T('6.7 Giao thức huấn luyện, chọn và đánh giá', '6.7 Training, Selection and Evaluation Protocol'), level=2)
    P(T('Mọi mô hình dùng chia dữ liệu theo thời gian (không xáo trộn ngẫu nhiên), nhiều mốc đánh giá và một tập kiểm thử chỉ chạm một lần. Mô hình thắng được huấn luyện lại trên toàn bộ nhãn đã hoàn tất trước khi dùng để chấm điểm.',
        'All models use time-based splits (never random shuffling), several evaluation origins and a test set touched once. The winning model is retrained on all completed labels before it is used for scoring.'))
    table([T('Mô hình', 'Model'), T('Huấn luyện', 'Training'), T('Validation (chọn mô hình)', 'Validation (selection)'), T('Kiểm thử (đánh giá một lần)', 'Test (single evaluation)'), T('Ứng viên', 'Candidates')], [
        [T('Dự báo doanh thu', 'Sales forecast'), T('Các mốc trước validation', 'Origins before validation'), '10/09, 08/10, 05/11', '03/12, 10/12, 17/12, 24/12', T('4 mô hình ML + 2 cơ sở', '4 ML models + 2 baselines')],
        [T('Rủi ro rời bỏ', 'Churn risk'), T('Mốc trước validation', 'Origins before validation'), '10/09', '05/11, 03/12', T('Gradient boosting, logistic, quy tắc recency', 'Gradient boosting, logistic, recency rule')],
        [T('Gợi ý mua kèm', 'Recommendation'), T('Đến 03/09', 'Through 3 Sep'), '04/09–01/10', '02/10–31/12', T('Luật kết hợp, độ phổ biến', 'Association rules, popularity')],
    ], [3.0, 3.4, 3.4, 3.8, 3.4])
    P(T('Sau khi chọn, mô hình được huấn luyện lại trên toàn bộ nhãn đã hoàn tất đến cuối kỳ và lưu cùng danh sách biến, từ vựng, ngày huấn luyện và phiên bản; các mô hình ứng viên còn lại cũng được lưu để so sánh về sau.',
        'After selection, the model is retrained on every completed label to the end of the period and stored with its feature list, vocabulary, training date and version; the remaining candidates are kept for later comparison.'))

    doc.add_heading(T('6.8 Kiểm tra độ bền của kết luận', '6.8 Stress-Testing the Conclusions'), level=2)
    rb = json.loads((ROOT / 'outputs/word_report/deep_summary.json').read_text(encoding='utf-8'))['risk_bootstrap']
    mon = json.loads((RUN / 'monitoring.json').read_text(encoding='utf-8'))
    table([T('Kiểm tra', 'Check'), T('Phương pháp', 'Method'), T('Kết quả', 'Result'), T('Ý nghĩa', 'Interpretation')], [
        [T('Mô hình rủi ro hơn quy tắc recency có chắc chắn không?', 'Is the churn model reliably better than the recency rule?'), T('Bootstrap 1.000 lần theo hộ trên hai mốc kiểm thử', '1,000 household-level bootstrap replications over both test origins'), T(f"Chênh AP +{fmt(rb['AP_difference'], 3)} (KTC 95%: {fmt(rb['AP_difference_CI'][0], 3)}–{fmt(rb['AP_difference_CI'][1], 3)}); chênh precision top 20% +{fmt(rb['precision_top20_difference'] * 100, 1)} điểm % (KTC {fmt(rb['precision_top20_difference_CI'][0] * 100, 1)}–{fmt(rb['precision_top20_difference_CI'][1] * 100, 1)})", f"AP difference +{fmt(rb['AP_difference'], 3)} (95% CI {fmt(rb['AP_difference_CI'][0], 3)}–{fmt(rb['AP_difference_CI'][1], 3)}); top-20% precision gap +{fmt(rb['precision_top20_difference'] * 100, 1)} pp (CI {fmt(rb['precision_top20_difference_CI'][0] * 100, 1)}–{fmt(rb['precision_top20_difference_CI'][1] * 100, 1)})"), T('Khoảng tin cậy không chứa 0: lợi thế của mô hình không phải do may mắn mẫu.', 'The interval excludes zero: the advantage is not a sampling accident.')],
        [T('Điểm số có phản ánh xác suất thật không?', 'Do scores reflect true probabilities?'), T('Chia 10 nhóm theo điểm, so dự đoán và thực tế', 'Ten score deciles, predicted versus actual'), T('Nhóm cao nhất: dự đoán 49%, thực tế 53%', 'Top decile: predicted 49%, actual 53%'), T('Điểm số xếp hạng đúng và gần với tần suất thực; chưa hiệu chỉnh riêng nên chỉ dùng để xếp thứ tự.', 'Scores rank correctly and are close to true frequency; not separately calibrated, so use for ranking.')],
        [T('Dự báo có bị sai lệch tại tuần lễ hội?', 'Does the forecast fail in holiday weeks?'), T('So sánh WAPE từng mốc kiểm thử và loại tuần có ngày vắng bản ghi', 'Compare WAPE by test origin and exclude the week with the missing day'), T('WAPE theo nhóm–tuần: 4,7% và 7,3% ở hai tuần đầu, 22,4% và 24,9% ở hai tuần sát Giáng sinh; loại tuần chứa 25/12, WAPE cơ sở là 12,35%', 'Group-week WAPE: 4.7% and 7.3% in the first two weeks, 22.4% and 24.9% in the two weeks before Christmas; excluding the week containing 25 Dec, baseline WAPE is 12.35%'), T('Sai số tập trung ở tuần lễ: cần biến lịch lễ và dữ liệu nhiều năm.', 'Error concentrates in holiday weeks: holiday calendar features and multi-year data are needed.')],
        [T('Dải dự báo có đủ rộng không?', 'Is the forecast band wide enough?'), T('Tỷ lệ giá trị thật nằm trong dải', 'Share of actuals inside the band'), T('61,9% so với mục tiêu 90%', '61.9% versus a 90% target'), T('Dải còn hẹp; không dùng để cam kết mức phục vụ tồn kho.', 'The band is too narrow; do not use it to commit inventory service levels.')],
        [T('Dữ liệu có đổi phân phối?', 'Has the data distribution shifted?'), T('PSI doanh thu ngày: 28 ngày cuối so với 28 ngày trước', 'PSI of daily sales: last 28 days versus the prior 28'), T(f"PSI {fmt(mon['daily_sales_PSI'], 3)} so với ngưỡng 0,2: không cảnh báo", f"PSI {fmt(mon['daily_sales_PSI'], 3)} versus a 0.2 threshold: no warning"), T('Phân phối ổn định; cờ chỉ để điều tra, không tự huấn luyện lại.', 'The distribution is stable; the flag prompts investigation and never triggers retraining on its own.')],
    ], [3.8, 3.8, 5.0, 4.4])

    doc.add_heading(T('6.9 Giải thích mô hình cho người dùng nghiệp vụ', '6.9 Explaining Models to Business Users'), level=2)
    bullets([
        T('Mô hình dự báo chọn phương án đơn giản nhất thắng được các mô hình phức tạp: người dùng có thể tự kiểm lại bằng một phép trung bình.', 'The forecast uses the simplest approach that beat the complex models, so users can check it themselves with a simple average.'),
        T('Mô hình rủi ro dựa chủ yếu vào số lần mua 90 ngày, số lần mua 28 ngày và recency: những tín hiệu mà đội CRM đã quen dùng, vì vậy kết quả dễ được chấp nhận.', 'The churn model relies mainly on 90-day visits, 28-day visits and recency, signals CRM teams already use, so results are easy to accept.'),
        T('Mỗi dự đoán đi kèm hồ sơ mô hình: biến, ngày huấn luyện, kết quả kiểm thử và giới hạn.', 'Every prediction comes with a model card: features, training date, test results and limitations.'),
        T('Mô hình không tự hành động: danh sách khách và dự báo luôn đi qua người phê duyệt.', 'Models never act on their own: customer lists and forecasts always pass through an approver.'),
    ])

    doc.add_heading(T('6.10 Giới hạn đã biết và cách xử lý trong MVP', '6.10 Known Limitations and How the MVP Addresses Them'), level=2)
    table([T('Giới hạn', 'Limitation'), T('Hệ quả', 'Consequence'), T('Cách xử lý trong MVP', 'MVP mitigation')], [
        [T('Dữ liệu là mẫu hộ một năm', 'One year of household-panel data'), T('Chưa bắt được mùa vụ nhiều năm; kết quả không đại diện toàn chuỗi', 'Cannot capture multi-year seasonality; results do not represent the whole chain'), T('Huấn luyện lại trên 24 tháng POS toàn chuỗi', 'Retrain on 24 months of full-chain POS')],
        [T('Hai mốc kiểm thử rủi ro chồng lấn', 'Two overlapping churn test origins'), T('Chưa phải hai lần lặp độc lập', 'Not two independent replications'), T('Backtest nhiều mốc trên dữ liệu doanh nghiệp', 'Multi-origin backtests on client data')],
        [T('Chưa có dữ liệu giá vốn, tồn kho', 'No cost or inventory data'), T('Không tính được lợi nhuận, ROI và mức phục vụ', 'Profit, ROI and service level cannot be computed'), T('Bổ sung ở giai đoạn 1; mô hình tồn kho ở giai đoạn 2', 'Added in phase 1; inventory modelling in phase 2')],
        [T('Chưa có nhóm đối chứng cho khuyến mãi', 'No control group for promotions'), T('Chỉ đo tỷ lệ đổi, chưa đo hiệu quả tăng thêm', 'Only redemption is measured, not incremental impact'), T('Thử nghiệm có đối chứng ở giai đoạn 3', 'Controlled experiments in phase 3')],
        [T('Dải dự báo hẹp', 'Narrow forecast band'), T('Không dùng cho cam kết dịch vụ', 'Not usable for service commitments'), T('Hiệu chỉnh dải trên dữ liệu SKU–cửa hàng', 'Recalibrate bands on SKU-store data')],
    ], [4.6, 6.0, 6.4])

    # ------------------------------------------------------------ 7 end-to-end & trust
    H1(T('7. Quy trình end-to-end và cơ chế tạo niềm tin', '7. End-to-End Process and Trust Mechanisms'))
    P(T('Một nền tảng phân tích chỉ được dùng lâu dài khi người dùng tin rằng số liệu đúng, mô hình không đổi ngầm và có ai đó chịu trách nhiệm khi có sự cố. Phần này mô tả toàn bộ chuỗi vận hành từ dữ liệu đến quyết định và các cơ chế kiểm soát ở từng bước.',
        'An analytics platform stays in use only when people trust that the figures are right, the models do not change silently, and someone is accountable when something goes wrong. This section describes the full chain from data to decision and the controls at each step.'))

    doc.add_heading(T('7.1 Mười bước từ dữ liệu đến quyết định', '7.1 Ten Steps from Data to Decision'), level=2)
    table([T('Bước', 'Step'), T('Việc thực hiện', 'What happens'), T('Kiểm soát', 'Control'), T('Đầu ra', 'Output')], [
        [T('1. Tiếp nhận', '1. Ingest'), T('Đọc giao dịch, danh mục sản phẩm, chiến dịch; ghi dấu kiểm tra (checksum) của mọi nguồn', 'Read transactions, product master and campaigns; record a checksum for every source'), T('Nguồn gốc không bị sửa; mã định danh giữ dạng văn bản', 'Source is never altered; identifiers kept as text'), T('Bản chụp dữ liệu có dấu kiểm tra', 'Checksummed data snapshot')],
        [T('2. Cổng chất lượng', '2. Quality gates'), T('Kiểm tra cột, ID rỗng, số không hợp lệ, trùng lặp, khóa xung đột, ngày thiếu, tỷ lệ ghép SKU', 'Check columns, empty IDs, invalid numbers, duplicates, conflicting keys, missing dates and SKU join rate'), T('Vi phạm là dừng, không công bố', 'A breach stops the run; nothing is published'), T('Báo cáo chất lượng', 'Quality report')],
        [T('3. Đối soát', '3. Reconciliation'), T('Tổng thô = dòng dương + dòng loại; tổng theo tháng = tổng chi tiết', 'Raw total = positive lines + excluded lines; monthly totals = detailed totals'), T('Lệch tổng là lỗi', 'A total mismatch is an error'), T('Bảng đối soát', 'Reconciliation table')],
        [T('4. Làm giàu', '4. Enrichment'), T('Ghép danh mục sản phẩm, ngành, nhãn hàng; tách dòng không dương và dòng thiếu SKU thành bảng riêng', 'Join product, department and brand; route non-positive and unmapped lines to separate tables'), T('Ngoại lệ có bảng riêng để nghiệp vụ xử lý', 'Exceptions have their own tables for business follow-up'), T('Dữ liệu giao dịch đã làm giàu', 'Enriched transaction data')],
        [T('5. Phân tích', '5. Analytics'), T('Chỉ tiêu tháng/ngày, doanh thu gộp sang thuần, RFM, ABC, cohort, K-means, quy tắc mua kèm', 'Monthly/daily KPIs, gross-to-net, RFM, ABC, cohorts, K-means, association rules'), T('Mọi con số truy về dòng giao dịch', 'Every figure traces to transaction lines'), T('Kho chỉ tiêu', 'KPI mart')],
        [T('6. Huấn luyện và chọn mô hình', '6. Train and select'), T('Chia theo thời gian, huấn luyện, chọn trên validation, đánh giá kiểm thử một lần, huấn luyện lại trên toàn bộ nhãn', 'Time-based splits, training, selection on validation, a single test evaluation, refit on all labels'), T('Không chọn lại theo kiểm thử; luôn có cơ sở', 'No reselection on test; always a baseline'), T('Hồ sơ và sổ đăng ký mô hình', 'Model cards and registry')],
        [T('7. Chấm điểm', '7. Scoring'), T('Dùng mô hình đã lưu để dự báo và chấm điểm rủi ro mà không huấn luyện lại', 'Use the stored models to forecast and score risk without retraining'), T('Không chấm điểm quá khứ trước ngày huấn luyện; yêu cầu đủ lịch sử và ngày hoàn tất', 'No scoring of dates before the training date; requires enough history and a completed day'), T('Danh sách khách và dự báo', 'Customer lists and forecasts')],
        [T('8. Giám sát', '8. Monitoring'), T('So phân phối doanh thu 28 ngày gần nhất với 28 ngày trước (PSI), theo dõi chất lượng dữ liệu', 'Compare the latest 28-day sales distribution with the prior 28 days (PSI) and track data quality'), T('Cờ điều tra, không tự huấn luyện lại', 'An investigation flag, never automatic retraining'), T('Báo cáo giám sát', 'Monitoring report')],
        [T('9. Công bố', '9. Publish'), T('Chỉ khi toàn bộ bước trước thành công mới cập nhật con trỏ "bản mới nhất"; lỗi được ghi riêng', 'The "latest" pointer moves only when every previous step succeeds; failures are logged separately'), T('Không bao giờ công bố kết quả dở dang', 'A half-finished result is never published'), T('Bản phát hành có chữ ký', 'Signed release')],
        [T('10. Quyết định', '10. Decision'), T('Dashboard, bảng xuất và báo cáo; người có thẩm quyền phê duyệt trước mọi hành động ra thị trường', 'Dashboard, exports and reports; an authorised approver signs off before any market-facing action'), T('Con người trong vòng quyết định', 'Human in the loop'), T('Quyết định có ghi nhận', 'Recorded decision')],
    ], [2.6, 6.4, 4.4, 3.6])

    doc.add_heading(T('7.2 Cổng chất lượng: khi nào hệ thống dừng', '7.2 Quality Gates: When the System Stops'), level=2)
    P(T('Nguyên tắc chủ đạo là dừng sớm và nói rõ lý do thay vì cho ra con số đáng ngờ. Hệ thống dừng khi:', 'The guiding principle is to stop early and say why rather than output a doubtful number. The system stops when:'))
    bullets([
        T('thiếu cột bắt buộc, ID rỗng, số không hữu hạn, dòng trùng nguyên văn, khóa sản phẩm trùng hoặc giỏ hàng xung đột;', 'a required column is missing, IDs are empty, numbers are non-finite, lines are exact duplicates, product keys repeat or baskets conflict;'),
        T('tỷ lệ dòng không ghép được SKU vượt ngưỡng cấu hình (hiện 2%; thực tế 0,33%) hoặc có thời điểm giao dịch không hợp lệ (ngưỡng 0%);', 'the share of lines without a SKU mapping exceeds the configured limit (2%; actual 0.33%) or any timestamp is invalid (limit 0%);'),
        T('lịch có ngày vắng không được khai báo; ngày vắng được khai báo (25/12/2017) chỉ mô tả số tiền quan sát, không chứng minh không có nhu cầu;', 'the calendar has an undeclared gap; a declared gap (25 Dec 2017) describes observed sales only and does not prove an absence of demand;'),
        T('không đủ lịch sử hoặc ngày cuối chưa hoàn tất; đối soát tổng không khớp.', 'there is not enough history, the last day is incomplete, or totals fail to reconcile.'),
    ])
    P(T('Dòng có số lượng hoặc doanh thu không dương không bị coi là gian lận mà được giữ riêng để giải thích; dòng thiếu SKU có bảng riêng để bộ phận danh mục xử lý.', 'Lines with non-positive quantity or sales are not treated as fraud but kept apart for explanation; unmapped lines have their own table for the merchandising team.'))

    doc.add_heading(T('7.3 Tính toàn vẹn và khả năng truy vết', '7.3 Integrity and Traceability'), level=2)
    table([T('Cơ chế', 'Mechanism'), T('Cách hoạt động', 'How it works'), T('Bằng chứng trong bản này', 'Evidence in this build')], [
        [T('Chữ ký bản phát hành', 'Release signature'), T('Mỗi lần chạy tạo mã băm từ dữ liệu đầu vào, mã nguồn và cấu hình; dashboard và các kết quả của lần chạy mang cùng mã', 'Each run hashes the input data, code and configuration; the dashboard and every output of the run carry the same hash'), T('Mã bản chạy 20261101_211545_762551_356e56a9 hiển thị ở chân dashboard', 'Run ID 20261101_211545_762551_356e56a9 shown in the dashboard footer')],
        [T('Không chạy lại khi không đổi', 'Skip when unchanged'), T('Nếu dữ liệu, mã và cấu hình không đổi thì kết quả cũ được giữ, tránh khác biệt không giải thích được', 'If data, code and configuration are unchanged the previous result is kept, avoiding unexplained differences'), T('Cơ chế chạy một lệnh có tùy chọn bắt buộc chạy lại', 'One-command run with a force option')],
        [T('Sổ ghi phiên bản', 'Version record'), T('Ghi phiên bản thư viện, thời gian chạy và các kiểm tra đã đạt', 'Records library versions, run times and the checks passed'), T('Mỗi lần chạy có tệp ghi riêng', 'A record file for every run')],
        [T('Công bố chỉ khi thành công', 'Publish only on success'), T('Lỗi được ghi cùng nhật ký chi tiết; con trỏ bản mới nhất không đổi', 'Failures are logged with a detailed trace; the latest pointer does not move'), T('Các lần chạy lỗi đầu tiên được giữ riêng, không lẫn vào bản phát hành', 'Early failed runs are kept apart and never mixed into releases')],
        [T('Khóa chống chạy chồng', 'Run lock'), T('Một tiến trình huấn luyện tại một thời điểm', 'One training process at a time'), T('Chấm điểm chạy độc lập, không ghi đè mô hình', 'Scoring runs independently and never overwrites a model')],
        [T('Dashboard truy về dòng gốc', 'Dashboard-to-source tracing'), T('Chức năng tra cứu giao dịch cho phép kiểm chứng bất kỳ con số nào', 'The transaction explorer lets users verify any number'), T('Tổng 1.468.773 dòng, USD 4.594.146,32 khớp nguồn', '1,468,773 lines and USD 4,594,146.32 match the source')],
    ], [3.6, 7.4, 6.0])

    doc.add_heading(T('7.4 Nhịp vận hành định kỳ', '7.4 Operating Cadence'), level=2)
    table([T('Tần suất', 'Frequency'), T('Hoạt động', 'Activity'), T('Người thực hiện', 'Owner')], [
        [T('Hằng ngày', 'Daily'), T('Nhận dữ liệu sau khi POS chốt ngày, chạy cổng chất lượng, cập nhật chỉ tiêu và chấm điểm', 'Ingest after the POS day close, run the quality gates, refresh KPIs and score'), T('Kỹ thuật dữ liệu', 'Data engineering')],
        [T('Hằng tuần', 'Weekly'), T('Huấn luyện lại khi có đủ nhãn mới; đối chiếu dự báo và điểm rủi ro đã xuất với thực tế khi nhãn đã chín (7 ngày cho dự báo, 28 ngày cho rủi ro)', 'Retrain when enough new labels exist; compare issued forecasts and risk scores with actuals once labels mature (7 days for forecast, 28 days for churn)'), T('Phân tích dữ liệu', 'Analytics')],
        [T('Hằng tháng', 'Monthly'), T('Họp rà soát chỉ tiêu, ngoại lệ dữ liệu và kết quả thử nghiệm', 'Review KPIs, data exceptions and experiment results'), T('Tài chính, kinh doanh, CRM', 'Finance, commercial, CRM')],
        [T('Hằng quý', 'Quarterly'), T('Đánh giá mô hình ứng viên so với mô hình đang dùng (champion–challenger); thay đổi chỉ khi vượt qua đánh giá theo thời gian và được nghiệp vụ duyệt', 'Evaluate challengers against the live model (champion–challenger); change only after passing time-based evaluation and business sign-off'), T('Hội đồng mô hình', 'Model committee')],
    ], [2.8, 10.2, 4.0])

    doc.add_heading(T('7.5 Giám sát liên tục', '7.5 Continuous Monitoring'), level=2)
    table([T('Chỉ số giám sát', 'Monitored metric'), T('Ngưỡng', 'Threshold'), T('Giá trị hiện tại', 'Current value'), T('Hành động khi vượt ngưỡng', 'Action when breached')], [
        [T('Tổng tiền và số dòng so với nguồn', 'Totals and row counts versus source'), T('Không lệch', 'No variance'), T('Khớp', 'Matched'), T('Dừng, điều tra với chủ sở hữu dữ liệu', 'Stop and investigate with the data owner')],
        [T('Tỷ lệ dòng thiếu ánh xạ SKU', 'Share of lines without SKU mapping'), '≤ 2%', '0,33%' if LANG == 'vi' else '0.33%', T('Dừng và bổ sung danh mục', 'Stop and complete the product master')],
        [T('PSI doanh thu ngày (28 so với 28 ngày)', 'Daily-sales PSI (28 vs 28 days)'), '< 0,2' if LANG == 'vi' else '< 0.2', '0,154' if LANG == 'vi' else '0.154', T('Điều tra mùa vụ và dữ liệu; chưa tự huấn luyện lại', 'Investigate seasonality and data; no automatic retraining')],
        [T('WAPE dự báo so với cơ sở trên nhãn đã chín', 'Forecast WAPE versus baseline on matured labels'), T('Không kém cơ sở', 'Not worse than baseline'), T('WAPE 14,99%', 'WAPE 14.99%'), T('Đưa mô hình ứng viên vào đánh giá', 'Trigger a challenger evaluation')],
        [T('Precision và lift top 20% của mô hình rủi ro', 'Churn model precision and lift at top 20%'), T('Lift từ 2,5 lần', 'Lift of at least 2.5x'), T('3,0 lần', '3.0x'), T('Huấn luyện lại và đánh giá lại', 'Retrain and re-evaluate')],
        [T('Độ phủ dải dự báo', 'Forecast band coverage'), T('Tiến gần 90%', 'Approach 90%'), '61,9%' if LANG == 'vi' else '61.9%', T('Hiệu chỉnh dải trên dữ liệu SKU–cửa hàng', 'Recalibrate bands on SKU-store data')],
        [T('Độ trễ chốt dữ liệu và tính sẵn sàng', 'Data-close latency and availability'), T('Theo thỏa thuận dịch vụ', 'Per service agreement'), T('Áp dụng ở triển khai thật', 'Applies in live deployment'), T('Cảnh báo cho kỹ thuật dữ liệu', 'Alert data engineering')],
    ], [5.4, 3.2, 3.2, 5.2])

    doc.add_heading(T('7.6 Vai trò và trách nhiệm', '7.6 Roles and Responsibilities'), level=2)
    table([T('Vai trò', 'Role'), T('Trách nhiệm chính', 'Primary responsibilities')], [
        [T('Chủ sở hữu dữ liệu', 'Data owner'), T('Chốt định nghĩa nguồn, xác nhận ngoại lệ và phê duyệt thay đổi cấu trúc dữ liệu', 'Define sources, confirm exceptions and approve data-structure changes')],
        [T('Tài chính / kế toán quản trị', 'Finance / management accounting'), T('Chốt định nghĩa chỉ tiêu, cung cấp giá vốn và chi phí, đối soát với sổ sách', 'Fix KPI definitions, supply cost and expense data, reconcile to the ledger')],
        [T('Phân tích dữ liệu', 'Analytics'), T('Vận hành quy trình, huấn luyện và đánh giá mô hình, soạn hồ sơ mô hình', 'Operate the process, train and evaluate models, maintain model cards')],
        [T('Kinh doanh và CRM', 'Commercial and CRM'), T('Dùng kết quả, thiết kế thử nghiệm có đối chứng, phê duyệt hành động ra thị trường', 'Use the results, design controlled experiments and approve market-facing actions')],
        [T('Công nghệ thông tin và an toàn thông tin', 'IT and information security'), T('Hạ tầng, phân quyền, nhật ký truy cập, sao lưu và khôi phục', 'Infrastructure, access control, access logs, backup and recovery')],
        [T('Hội đồng mô hình', 'Model committee'), T('Quyết định thay đổi mô hình đang dùng dựa trên bằng chứng', 'Decide changes to the live model on evidence')],
    ], [5, 12])

    doc.add_heading(T('7.7 Bảo mật và quyền riêng tư', '7.7 Security and Privacy'), level=2)
    bullets([
        T('Dữ liệu khách hàng dùng mã định danh; khi cần ẩn danh, mã được băm với khóa bí mật do doanh nghiệp quản lý bên ngoài hệ thống phân tích.', 'Customer data uses identifiers; where anonymisation is needed, IDs are hashed with a secret managed by the client outside the analytics system.'),
        T('Dashboard xử lý dữ liệu ngay trong trình duyệt; tệp tải lên chỉ nằm trong bộ nhớ của phiên làm việc và không được gửi đi.', 'The dashboard processes data inside the browser; uploaded files stay in session memory and are never transmitted.'),
        T('Tệp mô hình chỉ được nạp từ nguồn nội bộ đáng tin cậy.', 'Model files are loaded only from trusted internal sources.'),
        T('Hệ thống không tự gửi ưu đãi, đổi giá, đặt hàng hay tác động vào POS; mọi hành động cần người phê duyệt và đồng ý sử dụng dữ liệu của khách hàng.', 'The system never sends offers, changes prices, places orders or touches the POS; every action needs an approver and customer-data consent.'),
        T('Khi triển khai thật: phân quyền theo vai trò, nhật ký truy cập, mã hóa lưu trữ và quy trình khôi phục.', 'In live deployment: role-based access, access logs, encryption at rest and a recovery procedure.'),
    ])

    doc.add_heading(T('7.8 Vì sao có thể tin cậy', '7.8 Why It Can Be Trusted'), level=2)
    table([T('Mối quan tâm của người dùng', 'User concern'), T('Cơ chế bảo đảm', 'Assurance mechanism'), T('Bằng chứng', 'Evidence')], [
        [T('"Con số này có đúng không?"', '"Is this number right?"'), T('Đối soát tổng, cổng chất lượng, tra cứu đến dòng giao dịch', 'Total reconciliation, quality gates, drill-down to transaction lines'), T('Khớp 1.468.773 dòng và USD 4.594.146,32', 'Matches 1,468,773 lines and USD 4,594,146.32')],
        [T('"Mô hình có tốt thật không?"', '"Is the model really good?"'), T('Chia theo thời gian, kiểm thử một lần, so với cơ sở, khoảng tin cậy bootstrap', 'Time-based splits, a single test pass, comparison with baselines, bootstrap intervals'), T('Rủi ro: lift 3,0 lần, hơn recency với KTC 95% không chứa 0', 'Churn: 3.0x lift, beats recency with a 95% CI excluding zero')],
        [T('"Mô hình có nhìn trộm tương lai không?"', '"Does the model peek at the future?"'), T('Biến chỉ tính đến mốc gốc, chín kiểm thử tự động', 'Features computed only to the origin, nine automated tests'), T('Các kiểm thử về rò rỉ và nhãn đều đạt', 'Leakage and label tests all pass')],
        [T('"Mô hình có đổi ngầm không?"', '"Does the model change silently?"'), T('Chữ ký bản phát hành, sổ đăng ký mô hình, thay đổi qua champion–challenger và duyệt nghiệp vụ', 'Release signature, model registry, changes via champion–challenger and business sign-off'), T('Mỗi mô hình lưu ngày huấn luyện, biến và phiên bản', 'Each model stores its training date, features and version')],
        [T('"Có ai chịu trách nhiệm không?"', '"Is anyone accountable?"'), T('Vai trò rõ ràng, con người phê duyệt mọi hành động', 'Clear roles, a human approves every action'), T('Mục 7.6', 'Section 7.6')],
        [T('"Dữ liệu của tôi có an toàn không?"', '"Is my data safe?"'), T('Xử lý cục bộ, mã băm, không tự động tác động hệ thống', 'Local processing, hashing, no automatic system actions'), T('Mục 7.7', 'Section 7.7')],
    ], [4.4, 7.0, 5.6])

    doc.add_heading(T('7.9 Kịch bản sự cố và phản ứng', '7.9 Incident Scenarios and Responses'), level=2)
    table([T('Sự cố', 'Incident'), T('Phát hiện bằng', 'Detected by'), T('Phản ứng', 'Response')], [
        [T('Dữ liệu đến trễ hoặc thiếu ngày', 'Late or missing data'), T('Cổng lịch giao dịch và đối soát tổng', 'Calendar gate and total reconciliation'), T('Dừng công bố, thông báo chủ sở hữu dữ liệu, giữ bản trước', 'Stop publication, notify the data owner, keep the previous release')],
        [T('Mã SKU mới chưa có trong danh mục', 'New SKUs missing from the product master'), T('Tỷ lệ dòng thiếu ánh xạ', 'Unmapped-line rate'), T('Đưa vào bảng ngoại lệ; dừng nếu vượt 2%', 'Route to the exceptions table; stop above 2%')],
        [T('Mô hình kém đi', 'Model degradation'), T('Đối chiếu trên nhãn đã chín và PSI', 'Matured-label comparison and PSI'), T('Đánh giá mô hình ứng viên; quay về mô hình cơ sở nếu cần', 'Evaluate challengers; fall back to the baseline if needed')],
        [T('Lỗi trong quá trình chạy', 'Run failure'), T('Nhật ký và tệp lỗi riêng', 'Run log and dedicated failure record'), T('Giữ nguyên bản phát hành trước, sửa và chạy lại', 'Keep the previous release, fix and rerun')],
        [T('Tranh cãi về một con số', 'Dispute over a figure'), T('Chữ ký bản phát hành và tra cứu giao dịch', 'Release signature and transaction explorer'), T('Truy về dòng gốc và định nghĩa chỉ tiêu', 'Trace to source lines and the KPI definition')],
    ], [4.6, 5.0, 7.4])

    doc.add_heading(T('7.10 Duy trì giá trị lâu dài', '7.10 Sustaining Value Over Time'), level=2)
    P(T('Giá trị bền vững đến từ một vòng lặp, không phải một lần triển khai:', 'Lasting value comes from a loop, not a one-off deployment:'))
    table([T('Vòng lặp', 'Loop step'), T('Nội dung', 'Content')], [
        [T('1. Quan sát', '1. Observe'), T('Dashboard cập nhật hằng ngày, các phát hiện tự động nêu điểm cần chú ý', 'The dashboard refreshes daily and automated findings flag what needs attention')],
        [T('2. Giả thuyết', '2. Hypothesise'), T('Biến phát hiện thành giả thuyết kinh doanh kèm chỉ tiêu thành công', 'Turn each finding into a business hypothesis with a success metric')],
        [T('3. Thử nghiệm', '3. Test'), T('Thử nghiệm có nhóm đối chứng cho khuyến mãi, giữ chân, trưng bày', 'Controlled tests for promotions, retention and display')],
        [T('4. Quyết định', '4. Decide'), T('Mở rộng, chỉnh hoặc dừng dựa trên mức tăng gia tăng sau chi phí', 'Scale, adjust or stop based on incremental uplift after cost')],
        [T('5. Học lại', '5. Relearn'), T('Kết quả thử nghiệm quay về làm nhãn mới để huấn luyện lại mô hình', 'Experiment results return as new labels to retrain the models')],
    ], [4, 13])

    # ------------------------------------------------------------ 7 architecture & roadmap
    H1(T('8. Kiến trúc triển khai và lộ trình MVP 90 ngày', '8. Deployment Architecture and 90-Day MVP Roadmap'))
    doc.add_heading(T('8.1 Kiến trúc', '8.1 Architecture'), level=2)
    table([T('Lớp', 'Layer'), T('Thành phần', 'Components'), T('Nguyên tắc', 'Principle')], [
        [T('Nguồn dữ liệu', 'Data sources'), T('POS, danh mục sản phẩm, thẻ thành viên, khuyến mãi; sau đó giá vốn, tồn kho, công nợ', 'POS, product master, loyalty, promotions; later cost, inventory, payables'), T('Hợp đồng dữ liệu có chủ sở hữu từng nguồn', 'Data contract with an owner per source')],
        [T('Xử lý và kiểm soát', 'Processing and controls'), T('Làm sạch, đối soát tổng tiền, kiểm tra trùng lặp và ánh xạ SKU; chỉ công bố khi vượt cổng kiểm tra', 'Cleansing, total reconciliation, duplicate and SKU-mapping checks; publish only after quality gates pass'), T('Không công bố số liệu khi đối soát thất bại', 'No publication when reconciliation fails')],
        [T('Phân tích và mô hình', 'Analytics and models'), T('Kho chỉ tiêu, RFM, phân khúc, dự báo, rủi ro rời bỏ, Probit', 'KPI mart, RFM, segmentation, forecast, churn risk, Probit'), T('Validation trước kiểm thử; luôn có phương án cơ sở', 'Validation before test; always a baseline')],
        [T('Trình bày', 'Presentation'), T('Dashboard hai ngôn ngữ, xuất bảng, chấm điểm dữ liệu mới', 'Bilingual dashboard, table export, scoring of new data'), T('Mọi con số truy được về dòng giao dịch', 'Every figure traceable to transaction lines')],
        [T('Vận hành', 'Operations'), T('Lịch chạy định kỳ, giám sát độ lệch dữ liệu và hiệu năng mô hình', 'Scheduled runs, monitoring of data drift and model performance'), T('Con người phê duyệt mọi hành động ra thị trường', 'Human approval for every market-facing action')],
    ], [3.4, 8.4, 5.2])
    doc.add_heading(T('8.2 Lộ trình', '8.2 Roadmap'), level=2)
    table([T('Giai đoạn', 'Phase'), T('Thời gian', 'Timing'), T('Hoạt động', 'Activities'), T('Kết quả bàn giao', 'Deliverables')], [
        [T('0. Khởi động', '0. Mobilise'), T('Tuần 1–2', 'Weeks 1–2'), T('Khảo sát nguồn dữ liệu, chốt định nghĩa chỉ tiêu, hợp đồng dữ liệu và đầu mối', 'Source discovery, KPI definitions, data contract and owners'), T('Đặc tả dữ liệu, danh sách chỉ tiêu', 'Data specification, KPI list')],
        [T('1. Nền tảng dữ liệu', '1. Data foundation'), T('Tuần 3–6', 'Weeks 3–6'), T('Kết nối POS, đối soát, dựng kho chỉ tiêu và dashboard trên dữ liệu thật', 'Connect POS, reconcile, build KPI mart and dashboard on real data'), T('Dashboard vận hành, báo cáo đối soát', 'Live dashboard, reconciliation report')],
        [T('2. Mô hình', '2. Models'), T('Tuần 7–10', 'Weeks 7–10'), T('Huấn luyện dự báo SKU–cửa hàng, rủi ro rời bỏ, phân tích chiết khấu trên dữ liệu doanh nghiệp', 'Train SKU-store forecast, churn risk and discount analytics on client data'), T('Hồ sơ mô hình, kết quả kiểm thử', 'Model cards, test results')],
        [T('3. Pilot và đo lường', '3. Pilot and measurement'), T('Tuần 11–13', 'Weeks 11–13'), T('Thử nghiệm có đối chứng cho giữ chân và khuyến mãi; lập business case', 'Controlled tests for retention and promotions; business case'), T('Báo cáo hiệu quả, đề xuất mở rộng', 'Impact report, scale-up recommendation')],
    ], [3.3, 2.4, 7.2, 4.1])
    doc.add_heading(T('8.3 Đầu vào cần từ doanh nghiệp', '8.3 Inputs required from the client'), level=2)
    bullets([
        T('Giao dịch POS theo dòng (ngày, giờ, cửa hàng, giỏ, SKU, số lượng, tiền, chiết khấu) tối thiểu 24 tháng.', 'Line-level POS transactions (date, hour, store, basket, SKU, quantity, amount, discounts) for at least 24 months.'),
        T('Giá vốn theo SKU–ngày, rebate nhà cung cấp và chi phí vận hành theo cửa hàng.', 'Cost of goods by SKU-day, vendor rebates and operating costs by store.'),
        T('Tồn kho, hết hàng, đơn mua và thời gian giao hàng; công nợ phải thu, phải trả.', 'Inventory, stock-outs, purchase orders and lead times; receivables and payables.'),
        T('Lịch mở cửa, diện tích cửa hàng, ngân sách và kế hoạch khuyến mãi; mã thành viên và đồng ý sử dụng dữ liệu khách hàng.', 'Trading calendar, store area, budgets and promotion calendar; loyalty IDs and customer-data consent.'),
    ])
    doc.add_heading(T('8.4 Tiêu chí nghiệm thu MVP', '8.4 MVP acceptance criteria'), level=2)
    table([T('Tiêu chí', 'Criterion'), T('Ngưỡng', 'Threshold')], [
        [T('Đối soát doanh thu với sổ sách', 'Revenue reconciliation to the ledger'), T('Chênh lệch không quá ngưỡng do hai bên thống nhất', 'Variance within a threshold agreed by both parties')],
        [T('Độ phủ ánh xạ SKU', 'SKU mapping coverage'), T('Từ 99,5% dòng giao dịch', 'At least 99.5% of transaction lines')],
        [T('Mô hình dự báo', 'Forecast model'), T('Vượt phương án cơ sở trên tập kiểm thử theo thời gian', 'Beats the baseline on a time-based test set')],
        [T('Mô hình rủi ro rời bỏ', 'Churn model'), T('Lift top 20% từ 2,5 lần trên tập kiểm thử', 'Top-20% lift of at least 2.5x on the test set')],
        [T('Thử nghiệm giữ chân', 'Retention experiment'), T('Có nhóm đối chứng và đo được mức tăng gia tăng', 'Includes a control group with measurable incremental uplift')],
    ], [8, 9])
    callout(T('Giả định và điều kiện', 'Assumptions and conditions'), T('Kết quả trong tài liệu này dựa trên dữ liệu công khai của một siêu thị Mỹ năm 2017 và chỉ nhằm chứng minh năng lực. Hiệu quả trên doanh nghiệp cụ thể phải được xác nhận bằng pilot trên dữ liệu thật.', 'Results in this document are based on public 2017 data from a US grocery retailer and serve to demonstrate capability. Impact for a specific business must be confirmed by a pilot on real data.'), fill='F2F5F9', bar='10243D')

    # ------------------------------------------------------------ 8 glossary
    H1(T('Phụ lục. Thuật ngữ và định nghĩa chỉ tiêu', 'Appendix. Glossary and KPI Definitions'))
    table([T('Chỉ tiêu', 'KPI'), T('Định nghĩa', 'Definition')], [
        [T('Doanh thu thuần', 'Net sales'), T('Số tiền doanh nghiệp thực nhận trên mỗi dòng, sau chiết khấu.', 'Amount received per line after discounts.')],
        [T('Doanh thu gộp', 'Gross sales'), T('Doanh thu thuần cộng chiết khấu thẻ thành viên, coupon và coupon đối ứng.', 'Net sales plus loyalty, coupon and coupon-match discounts.')],
        [T('Tỷ lệ chiết khấu', 'Discount rate'), T('Tổng chiết khấu chia doanh thu gộp.', 'Total discounts divided by gross sales.')],
        ['AOV', T('Doanh thu thuần chia số giỏ hàng.', 'Net sales divided by number of baskets.')],
        [T('Hộ hoạt động', 'Active household'), T('Hộ có ít nhất một dòng mua dương trong kỳ.', 'Household with at least one positive purchase line in the period.')],
        ['RFM', T('Recency (ngày từ lần mua cuối), Frequency (số giỏ), Monetary (chi tiêu).', 'Recency (days since last purchase), Frequency (baskets), Monetary (spend).')],
        ['Lift', T('Xác suất mua cặp hàng so với kỳ vọng nếu độc lập; lớn hơn 1 là liên kết dương.', 'Co-purchase probability versus independence; above 1 is positive association.')],
        ['WAPE', T('Tổng sai số tuyệt đối chia tổng thực tế; thấp hơn là tốt hơn.', 'Total absolute error divided by total actual; lower is better.')],
        ['Bias', T('(Dự báo trừ thực tế) chia tổng thực tế; dương là dự báo cao hơn thực tế.', '(Forecast minus actual) divided by total actual; positive means above actual.')],
        ['Precision / Recall', T('Tỷ lệ chọn đúng trong nhóm được chọn / tỷ lệ khách ngừng mua được bắt.', 'Hit rate within the selected group / share of lapsing customers captured.')],
        [T('Điểm hòa vốn', 'Break-even'), T('Chi phí cố định chia tỷ lệ đóng góp.', 'Fixed costs divided by contribution margin.')],
        ['CCC', 'DIO + DSO − DPO'],
        ['LFL', T('Doanh thu cùng cửa hàng so với cùng kỳ.', 'Like-for-like sales versus the same period.')],
        ['PSI', T('Chỉ số ổn định dân số: đo mức thay đổi phân phối giữa hai khoảng thời gian; trên 0,2 là cờ điều tra.', 'Population stability index: measures the shift in a distribution between two periods; above 0.2 is an investigation flag.')],
        [T('Rò rỉ dữ liệu', 'Data leakage'), T('Dùng thông tin của tương lai khi huấn luyện, làm kết quả kiểm thử đẹp hơn thực tế.', 'Using future information during training, making test results look better than reality.')],
        ['Champion–challenger', T('Mô hình đang dùng (champion) liên tục được so với mô hình ứng viên (challenger); chỉ thay khi ứng viên thắng qua đánh giá theo thời gian.', 'The live model (champion) is continuously compared with a candidate (challenger); replaced only when the candidate wins a time-based evaluation.')],
        [T('Hiệu chỉnh (calibration)', 'Calibration'), T('Mức độ khớp giữa xác suất dự đoán và tần suất thực tế.', 'How closely predicted probabilities match observed frequencies.')],
        ['Probit', T('Mô hình thống kê trả xác suất liên tục cho một sự kiện.', 'A statistical model returning a continuous probability for an event.')],
        ['Bootstrap', T('Lấy mẫu lặp có hoàn lại để ước lượng khoảng tin cậy.', 'Repeated resampling with replacement to estimate confidence intervals.')],
    ], [4, 13])

    out = OUT / ('Retail_Intelligence_MVP_Proposal_' + lang.upper() + '.docx')
    doc.save(out)
    return out


if __name__ == '__main__':
    for lg in ('vi', 'en'):
        print(build(lg))
