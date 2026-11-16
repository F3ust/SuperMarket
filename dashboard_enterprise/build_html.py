from pathlib import Path
import json,hashlib,zipfile,base64,io
from plotly.offline import get_plotlyjs
P=Path(__file__).parent
delivery=P.parent/'outputs/dashboard_html';delivery.mkdir(exist_ok=True)
archive_bytes=io.BytesIO()
with zipfile.ZipFile(archive_bytes,'w',compression=zipfile.ZIP_DEFLATED) as archive:
    for name in ['probability_registry.json','probability_runtime.py','score_probability.py','UPLOAD_GUIDE.md']:
        archive.write(P/name,name)
    archive.write(P/'examples/snapshot_90d_public_demo.csv','snapshot_90d_public_demo.csv')
    archive.writestr('schema.csv','line_id,date,household_id,basket_id,product_category,quantity,sales_value,retail_disc,coupon_disc,coupon_match_disc\n')
    archive.writestr('requirements.txt','numpy>=1.26\npandas>=2.2\nscipy>=1.13\npyarrow>=17\n')
package=archive_bytes.getvalue();(delivery/'Bo_model_Probit_va_cham_diem.zip').write_bytes(package)
template=(P/'src/index.html').read_text(encoding='utf-8')
parts={'/*__STYLE__*/':(P/'src/styles.css').read_text(encoding='utf-8'),'/*__PLOTLY__*/':get_plotlyjs(),'/*__DATA__*/':(P/'bundle.json').read_text(encoding='utf-8'),'/*__WORKER__*/':json.dumps((P/'src/probability-worker.js').read_text(encoding='utf-8')+'\n'+(P/'src/worker.js').read_text(encoding='utf-8'),ensure_ascii=False),'/*__APP__*/':(P/'src/app.js').read_text(encoding='utf-8').replace('boot().catch(showError);',(P/'src/business.js').read_text(encoding='utf-8')+'\n'+(P/'src/dict.js').read_text(encoding='utf-8')+'\n'+(P/'src/insight.js').read_text(encoding='utf-8')+'\nconst PROBIT_REGISTRY='+ (P/'probability_registry.json').read_text(encoding='utf-8')+';\nconst PROBIT_PACKAGE='+json.dumps(base64.b64encode(package).decode())+';\n'+(P/'src/upload.js').read_text(encoding='utf-8')+'\nboot().catch(showError);')}
for token,text in parts.items():
    template=template.replace(token,text.replace('</script','<\\/script'))
out=P/'dist/index.html';out.parent.mkdir(exist_ok=True);out.write_text(template,encoding='utf-8')
target=delivery/'Dashboard_chuoi_sieu_thi.html';target.write_bytes(out.read_bytes())
guide=delivery/'Huong_dan_dashboard.md';guide.write_bytes((P/'BUSINESS_GUIDE.md').read_bytes())
with zipfile.ZipFile(delivery/'Dashboard_chuoi_sieu_thi.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    z.write(target,target.name)
    z.write(guide,guide.name)
    z.write(P/'UPLOAD_GUIDE.md','Huong_dan_upload_va_Probit.md')
(delivery/'Huong_dan_upload_va_Probit.md').write_bytes((P/'UPLOAD_GUIDE.md').read_bytes())
print(json.dumps({'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'path':str(target)},ensure_ascii=True))
