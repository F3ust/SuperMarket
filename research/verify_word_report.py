from pathlib import Path
from zipfile import ZipFile
import hashlib,json
from lxml import etree
import fitz
from docx import Document

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/word_report';RENDER=OUT/'render'
document_path=OUT/'Bao_cao_chuyen_sau_chuoi_sieu_thi.docx'
old=json.loads((RENDER/'reviewed_first_render_hashes.json').read_text(encoding='utf-8'))
new={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in RENDER.glob('page-*.png')}
changed=sorted([k for k,v in new.items() if old.get(k)!=v],key=lambda x:int(x.split('-')[1].split('.')[0]))
pdf=fitz.open(RENDER/'Bao_cao_chuyen_sau_chuoi_sieu_thi.pdf');doc=Document(document_path)
assert len(pdf)==33 and len(new)==33
assert all('Trang '+str(i+1) in page.get_text() for i,page in enumerate(pdf))
assert all(len(page.get_text())>300 for page in pdf)
with ZipFile(document_path) as archive:
    styles=etree.fromstring(archive.read('word/styles.xml'));body=etree.fromstring(archive.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
assert not styles.xpath('//w:style[@w:styleId="Title"]//w:pBdr',namespaces=ns)
anchors=body.xpath('//w:hyperlink/@w:anchor',namespaces=ns);bookmarks=body.xpath('//w:bookmarkStart/@w:name',namespaces=ns)
assert len(anchors)==30 and set(anchors).issubset(bookmarks)
assert len(doc.inline_shapes)==18 and len(doc.tables)==19
for shape in doc.inline_shapes:
    assert shape.width<=doc.sections[0].page_width-doc.sections[0].left_margin-doc.sections[0].right_margin
for page in pdf:
    for block in page.get_text('dict')['blocks']:
        if block['type']!=0:continue
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                assert x0>=0 and x1<=page.rect.width+1 and y0>=0 and y1<=page.rect.height+1
text=' '.join(p.text for p in doc.paragraphs)+' '.join(c.text for t in doc.tables for row in t.rows for c in row.cells)
assert '4.594.146,32' in text and '61,9%' in text and '364.013,16' in text
assert ':codex-file-citation' not in text and 'turn7search' not in text
result={'pages':len(pdf),'figures':len(doc.inline_shapes),'tables':len(doc.tables),'words_whitespace':len(text.split()),'toc_links':len(anchors),'checks':'structure, page fields, page bounds, key figures and numbers passed','initial_render_pages_visually_reviewed':32,'unchanged_pages_reuse_identical_reviewed_images':33-len(changed),'pages_requiring_final_visual_review':changed,'final_sha256':hashlib.sha256(document_path.read_bytes()).hexdigest()}
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
