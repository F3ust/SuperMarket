"""Batch snapshot inference with frozen Probit JSON, supports CSV or Parquet.
Usage: python score_probability.py --input new.csv --as-of 2018-03-31 --coverage-start 2018-01-01 --complete --output out
No model fitting, no browser file-size limit, no model files accepted from users.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np,pandas as pd
from probability_runtime import predict,FEATURES,snapshot_features
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--as-of',required=True);parser.add_argument('--coverage-start',required=True);parser.add_argument('--complete',action='store_true');parser.add_argument('--currency',choices=['USD','VND'],default='USD');parser.add_argument('--fx',type=float);parser.add_argument('--output',required=True);a=parser.parse_args()
 registry=json.loads((Path(__file__).parent/'probability_registry.json').read_text(encoding='utf-8'));path=Path(a.input);origin=pd.Timestamp(a.as_of);start=pd.Timestamp(a.coverage_start)
 if not a.complete:raise ValueError('Confirm complete source coverage with --complete; missing history is not zero.')
 if origin<pd.Timestamp(registry['trainedThrough']):raise ValueError('Scoring origin precedes model training cutoff.')
 if start>origin-pd.Timedelta(days=89):raise ValueError('At least 90 calendar days of declared source coverage required.')
 if a.currency=='VND' and (a.fx is None or not np.isfinite(a.fx) or a.fx<=0):raise ValueError('Provide explicit positive VND/USD with --fx.')
 if a.currency=='USD':a.fx=1
 fields=['line_id','date','household_id','basket_id','product_category','quantity','sales_value','retail_disc','coupon_disc','coupon_match_disc']
 df=pd.read_parquet(path) if path.suffix.lower()=='.parquet' else pd.read_csv(path,dtype={c:str for c in fields[:5]},encoding='utf-8-sig')
 if not set(fields).issubset(df):raise ValueError('Missing fields: '+str(set(fields)-set(df)))
 if df[fields].isna().any().any() or df.empty:raise ValueError('Missing values or empty file; do not impute silently.')
 if df.line_id.duplicated().any():raise ValueError('Duplicate line_id; source corrections need a new reconciled snapshot.')
 for c in ['line_id','household_id','basket_id','product_category']:df[c]=df[c].astype(str).str.strip()
 for c in ['line_id','household_id','basket_id','product_category']:
  if df[c].eq('').any():raise ValueError('Empty identifier/category after trimming.')
 for c in ['line_id','household_id','basket_id']:
  if df[c].str.fullmatch(r'\d+(\.\d+)?[eE][+-]?\d+').any():raise ValueError('Scientific-notation IDs; export as text.')
 df['date']=pd.to_datetime(df.date,format='ISO8601').dt.normalize()
 if df.date.min()<start or df.date.max()>origin:raise ValueError('Records outside declared coverage or after as-of.')
 identity=df.household_id+'|'+df.date.astype(str)
 if identity.groupby(df.basket_id).nunique().max()>1:raise ValueError('Basket key spans customers/dates; make key globally unique.')
 numeric=fields[5:]
 for c in numeric:df[c]=pd.to_numeric(df[c],errors='raise')
 if not np.isfinite(df[numeric].values).all():raise ValueError('Nonfinite numeric values.')
 if a.currency=='VND':df[['sales_value','retail_disc','coupon_disc','coupon_match_disc']]/=a.fx
 if df.sales_value.abs().gt(1e9).any() or df.quantity.abs().gt(1e7).any():raise ValueError('Check units: numeric value exceeds validation bounds.')
 features=snapshot_features(df,origin)
 if features.empty:raise ValueError('No eligible active customer.')
 result=features[['household_id','sales_28','sales_90','recency','visits_28']].copy()
 for m in registry['models']:
  p=predict(m,features)
  if m['task']=='no_purchase_28':result['p_no_purchase28']=p
  elif m['task']=='return_time_56':
   for i,h in enumerate([7,14,28,56]):result[f'p_return{h}']=p[:,:i+1].sum(axis=1)
  elif m['task']=='visits_28':
   for i,col in enumerate(['p_visits0','p_visits1','p_visits2_3','p_visits4_7','p_visits8plus']):result[col]=p[:,i]
  elif m['task']=='decline_30':result['p_decline30']=np.where(features.sales_28>0,p,np.nan)
  else:result['p_discount28']=p
 result['as_of']=a.as_of;result['model_version']=registry['version'];result['feature_version']=registry['feature_version']
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);result.sort_values('p_no_purchase28',ascending=False).to_csv(out/'probabilities.csv',index=False,encoding='utf-8-sig')
 audit={'mode':'snapshot_score_only_no_retrain','model_version':registry['version'],'model_ids':[m['model_id'] for m in registry['models']],'source_file':path.name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'as_of':a.as_of,'coverage_start':a.coverage_start,'rows':len(df),'customers_scored':len(result),'currency_input':a.currency,'fx':a.fx,'future_labels_observed':False}
 (out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(audit,ensure_ascii=True))
if __name__=='__main__':main()
