"""Integration checks for the latest successful local run (no external writes)."""
from pathlib import Path
import json,sqlite3,subprocess,sys,tempfile
import numpy as np
import pandas as pd
import joblib
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
latest=json.loads((ROOT/'outputs/enterprise/latest.json').read_text(encoding='utf-8'))
run=Path(latest['path']);manifest=json.loads((run/'run_manifest.json').read_text(encoding='utf-8'))
assert manifest['status']=='success'
qa=json.loads((run/'quality.json').read_text(encoding='utf-8'))
with sqlite3.connect(run/'business_mart.sqlite') as db:
    assert np.isclose(db.execute('SELECT SUM(sales) FROM monthly_kpis').fetchone()[0],qa['raw_sales'])
    assert db.execute('SELECT COUNT(*) FROM customer_risk_actions').fetchone()[0]>2000
forecast=joblib.load(run/'models/sales_forecast.joblib');risk=joblib.load(run/'models/customer_risk.joblib')
assert len(list((run/'models/challengers').glob('forecast_*.joblib')))==4
for path in (run/'models/challengers').glob('*.joblib'):assert joblib.load(path)['model'] is not None
features=pd.read_parquet(run/'forecast_features.parquet')
out=pd.read_csv(run/'forecast_next_7_days.csv').sort_values('series')
frame=features[features.origin==pd.Timestamp(forecast['trained_through'])].sort_values('series')
pred=forecast['model'].predict(frame[forecast['features']])*frame.scale if forecast['model'] is not None else (frame.previous_7 if forecast['champion']=='last_7_days' else frame.scale)
assert np.allclose(np.maximum(0,pred),out.forecast)
actions=pd.read_csv(run/'customer_risk_actions.csv')
prob=risk['model'].predict_proba(actions[risk['features']])[:,1] if risk['model'] is not None else np.clip(actions.recency/90,0,1)
assert np.allclose(prob,actions.risk_score)
assert actions.priority_top20.sum()==int(np.ceil(len(actions)*.2))
report=(run/'report.html').read_text(encoding='utf-8')
class ScriptSources(HTMLParser):
    def __init__(self):super().__init__();self.sources=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script' and dict(attrs).get('src'):self.sources.append(dict(attrs)['src'])
parser=ScriptSources();parser.feed(report);assert not parser.sources
assert 'Độ nhạy' in report and 'Plotly.newPlot' in report and 'Phương pháp' in report
# Fail closed on invalid schema and preserve the previous success pointer.
with tempfile.TemporaryDirectory(prefix='pipeline-verification-',dir=ROOT/'outputs') as tmp:
    temp=Path(tmp);src=temp/'source';dst=temp/'result';src.mkdir();dst.mkdir()
    pd.DataFrame({'household_id':['x']}).to_csv(src/'transactions.csv',index=False)
    pd.DataFrame({'product_id':['x'],'department':['X'],'product_category':['X'],'brand':['X']}).to_csv(src/'products.csv',index=False)
    config=json.loads((ROOT/'retail_pipeline/config.json').read_text(encoding='utf-8'));config['input_dir']=str(src);config['output_dir']=str(dst)
    configfile=temp/'config.json';configfile.write_text(json.dumps(config),encoding='utf-8')
    marker=dst/'latest.json';marker.write_text(json.dumps({'signature':'previous','status':'success','path':'prior-good-output'}))
    original=marker.read_bytes()
    result=subprocess.run([sys.executable,'-m','retail_pipeline.run','--config',str(configfile)],cwd=ROOT,capture_output=True)
    assert result.returncode==1,result.stdout
    assert marker.read_bytes()==original
    assert (dst/'last_failure.json').exists() and not (dst/'pipeline.lock').exists()
print(json.dumps({'status':'passed','checks':['SQL reconciliation','4 trained challenger artifacts reload','forecast score reproducibility','risk score reproducibility and capacity','offline report presence','schema failure preserves previous latest and releases lock'],'run_id':latest['run_id']},ensure_ascii=False))
