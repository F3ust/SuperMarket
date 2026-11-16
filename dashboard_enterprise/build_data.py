"""Bundle every in-scope transaction and model artifact for an offline dashboard."""
from pathlib import Path
import json,gzip,base64,hashlib,shutil
import pandas as pd
import numpy as np
import joblib

ROOT=Path(__file__).resolve().parents[1];PROJECT=Path(__file__).parent
RUN=Path(json.loads((ROOT/'outputs/enterprise/latest.json').read_text(encoding='utf-8'))['path'])
def clean(v):
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,list):return [clean(x) for x in v]
    if isinstance(v,(np.integer,np.floating)):v=v.item()
    if isinstance(v,float) and not np.isfinite(v):return None
    return v
def read(name):
    p=RUN/(name+'.csv');return clean(pd.read_csv(p).replace({np.nan:None}).to_dict('records')) if p.exists() else []
def load(name):return json.loads((RUN/(name+'.json')).read_text(encoding='utf-8'))
def main():
    j=pd.read_parquet(RUN/'transactions_enriched.parquet');qa=load('quality')
    dictionaries={}
    for key in ['store_id','household_id','basket_id','product_id','department','product_category','brand']:
        j[key]=j[key].astype(str);dictionaries[key]=sorted(j[key].unique().tolist())
    columns={};chunks=[];offset=0
    def add(name,values,dtype):
        nonlocal offset
        pad=(-offset)%4
        if pad:chunks.append(b'\0'*pad);offset+=pad
        arr=np.asarray(values,dtype=dtype);raw=arr.tobytes()
        columns[name]={'offset':offset,'dtype':np.dtype(dtype).name,'length':len(arr)};chunks.append(raw);offset+=len(raw)
    add('day',(j.date-pd.Timestamp('2017-01-01')).dt.days,'<u2')
    for name,source,dtype in [('store','store_id','<u2'),('customer','household_id','<u2'),('basket','basket_id','<u4'),('sku','product_id','<u4'),('dept','department','u1'),('category','product_category','<u2'),('brand','brand','u1')]:
        add(name,pd.Categorical(j[source],categories=dictionaries[source]).codes,dtype)
    for name,source in [('sales','sales_value'),('retailDiscount','retail_disc'),('couponDiscount','coupon_disc'),('matchDiscount','coupon_match_disc')]:
        cents=np.rint(j[source].to_numpy()*100)
        assert np.max(np.abs(cents))<2**31
        add(name,cents,'<i4')
    add('quantity',j.quantity.to_numpy(),'<f4');add('hour',j.transaction_timestamp.dt.hour,'u1')
    binary=b''.join(chunks);packed=gzip.compress(binary,compresslevel=9,mtime=0)
    money=int(np.rint(j.sales_value.to_numpy()*100).sum());assert abs(money/100-qa['raw_sales'])<.005
    sku=j.drop_duplicates('product_id').set_index('product_id')
    product_meta=[]
    for key in dictionaries['product_id']:
        row=sku.loc[key]
        product_meta.append([str(row.get('product_type','') or ''),str(row.get('package_size','') or ''),dictionaries['department'].index(row.department),dictionaries['product_category'].index(row.product_category),dictionaries['brand'].index(row.brand)])
    result={'meta':{'name':'Complete Journey','runId':RUN.name,'signature':json.loads((RUN/'run_manifest.json').read_text(encoding='utf-8'))['signature'],'dateOrigin':'2017-01-01','dateEnd':'2017-12-31','rows':len(j),'sourceRows':qa['source_rows'],'currency':'USD','rawSalesCents':money,'missingDays':[358],'rawBinaryBytes':len(binary),'compressedBytes':len(packed),'compressedSHA256':hashlib.sha256(packed).hexdigest(),'dateNote':'25/12/2017 không có bản ghi. Không suy diễn đây là ngày không có nhu cầu. 534 dòng của phần ngày 01/01/2018 nằm ngoài kỳ đã chốt.'},'columns':columns,'dictionaries':dictionaries,'productMeta':product_meta,'packed':base64.b64encode(packed).decode(),'quality':qa}
    for name in ['analytics_summary','forecast_summary','risk_summary','association_metrics','monitoring']:
        result[name]=load(name)
    for name in ['monthly_kpis','sales_bridge','department_monthly','product_abc','segment_summary','customer_segments','observed_cohorts','customer_risk_actions','forecast_validation_leaderboard','forecast_test_metrics','forecast_test_predictions','forecast_test_without_assumed_zero_week','forecast_series_metrics','forecast_test_intervals','forecast_next_7_days','risk_validation_leaderboard','risk_test_metrics','risk_test_predictions','risk_feature_importance','association_rules','campaign_redemption','business_insights_actions','cluster_selection','cluster_profiles']:
        result[name]=read(name)
    for name in ['campaign_intervals','risk_calibration','risk_capacity','forecast_error_contribution','department_growth_contribution','coupon_misc_taxonomy']:
        p=ROOT/'outputs/word_report'/(name+'.csv')
        if p.exists():result[name]=clean(pd.read_csv(p).replace({np.nan:None}).to_dict('records'))
    result['deep_summary']=json.loads((ROOT/'outputs/word_report/deep_summary.json').read_text(encoding='utf-8'))
    assert result['deep_summary']['source_signature']==result['meta']['signature'], 'Deep analysis snapshot mismatch; regenerate analysis and report first.'
    assert result['deep_summary']['run_id']==RUN.name, 'Deep analysis run mismatch.'
    result['basketModel']=joblib.load(RUN/'models/basket_recommender.joblib')
    result['uci_profile']=json.loads((ROOT/'outputs/profile.json').read_text(encoding='utf-8'))['online_retail']
    # Inventory is an explicit sandbox. Daily demand starts from observed per-SKU units.
    positive=j[(j.quantity>0)&(j.sales_value>0)&~j.department.isin(['FUEL','MISCELLANEOUS','UNKNOWN'])]
    recent=positive[positive.date>=pd.Timestamp('2017-12-04')]
    top=recent.groupby('product_id').sales_value.sum().nlargest(15).index
    sims=[]
    for idx,product in enumerate(top):
        frame=recent[recent.product_id==product];daily=frame.quantity.sum()/28
        sims.append({'sku':product,'type':str(sku.loc[product].product_type),'pack':str(sku.loc[product].package_size),'dailyObservedUnits':round(float(daily),2),'stockAssumed':round(daily*(2+idx%5)),'inboundAssumed':0,'leadAssumed':3+idx%3,'reviewDays':7,'bufferDays':2,'casePackAssumed':6,'MOQAssumed':6})
    result['inventorySandbox']=sims
    document=ROOT/'outputs/word_report/Bao_cao_chuyen_sau_chuoi_sieu_thi.docx'
    result['reportDocBase64']=base64.b64encode(document.read_bytes()).decode()
    # Compress descriptive/model JSON separately; keep the full fact columns in a worker.
    transaction_data=result.pop('packed');document_data=result.pop('reportDocBase64')
    result.pop('product_abc',None)  # Recomputed across all selected facts by the browser worker.
    metadata=json.dumps(clean(result),ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
    compressed_metadata=gzip.compress(metadata,compresslevel=9,mtime=0)
    bundle={'meta':result['meta'],'metadataGzip':base64.b64encode(compressed_metadata).decode(),'transactionsGzip':transaction_data,'reportDocBase64':document_data}
    (PROJECT/'bundle.json').write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf-8')
    (PROJECT/'data_manifest.json').write_text(json.dumps(result['meta'],ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'rows':len(j),'binaryBytes':len(binary),'gzipBytes':len(packed),'metadataGzip':len(compressed_metadata),'bundleBytes':(PROJECT/'bundle.json').stat().st_size}))

if __name__=='__main__':main()
