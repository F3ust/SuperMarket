from __future__ import annotations
import json, hashlib, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/vendor'))

def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)), encoding='utf-8')

def save(df, directory, name):
    path = Path(directory) / f'{name}.csv'
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path

def read_table(directory, stem, required=True):
    directory = Path(directory)
    csv = directory / (stem + '.csv')
    if csv.exists():
        ids = ['household_id','store_id','basket_id','product_id','campaign_id','coupon_upc']
        columns = pd.read_csv(csv,nrows=0).columns
        return pd.read_csv(csv, dtype={c:'string' for c in ids if c in columns})
    import pyreadr
    for ext in ['.rds','.rda']:
        path = directory / (stem + ext)
        if path.exists():
            return next(iter(pyreadr.read_r(str(path)).values()))
    if required:
        raise FileNotFoundError(f'Missing {stem}.csv/.rds/.rda in {directory}')
    return None

def input_signature(config, config_path):
    paths = sorted((ROOT/config['input_dir']).glob('*'))
    paths += sorted(Path(__file__).parent.glob('*.py')) + [Path(config_path)]
    parts=[]
    for p in paths:
        if p.is_file() and p.suffix.lower() in ['.rds','.rda','.csv','.py','.json']:
            parts.append({'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    payload=json.dumps(parts,sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest(),parts

def ingest(config, directory):
    raw=read_table(ROOT/config['input_dir'],'transactions')
    products=read_table(ROOT/config['input_dir'],'products')
    required={'household_id','store_id','basket_id','product_id','quantity','sales_value','transaction_timestamp','retail_disc','coupon_disc','coupon_match_disc'}
    missing=required-set(raw.columns)
    if missing: raise ValueError(f'Missing transaction columns: {sorted(missing)}')
    if not {'product_id','department','product_category','brand'}.issubset(products.columns):
        raise ValueError('Products requires product_id, department, product_category, brand')
    for c in ['household_id','store_id','basket_id','product_id']:
        raw[c]=raw[c].astype('string').str.strip()
        if raw[c].isna().any() or raw[c].eq('').any(): raise ValueError(f'Empty transaction key {c}')
    products['product_id']=products.product_id.astype('string').str.strip()
    if products.product_id.isna().any() or products.product_id.eq('').any() or products.product_id.duplicated().any():
        raise ValueError('Product master key must be populated and unique')
    raw['transaction_timestamp']=pd.to_datetime(raw.transaction_timestamp,errors='coerce')
    invalid_rate=raw.transaction_timestamp.isna().mean()
    if invalid_rate>config['max_invalid_timestamp_rate']: raise ValueError('Invalid transaction timestamps')
    for c in ['quantity','sales_value','retail_disc','coupon_disc','coupon_match_disc']:
        raw[c]=pd.to_numeric(raw[c],errors='coerce')
        if not np.isfinite(raw[c]).all(): raise ValueError(f'Non-finite numeric data in {c}')
    if raw.duplicated().any(): raise ValueError('Exact duplicate transaction rows; resolve source provenance before processing')
    end=pd.Timestamp(config['analysis_end'])
    # Last source date is incomplete unless a later calendar date is present.
    if end>=raw.transaction_timestamp.max().normalize():
        raise ValueError('analysis_end must precede last observed source calendar day; ensure complete-day coverage')
    raw['date']=raw.transaction_timestamp.dt.normalize()
    t=raw[raw.date<=end].copy()
    if t.empty or (end-t.date.min()).days<330: raise ValueError('At least 331 calendar days required for configured model evaluation')
    if t.date.max()!=end: raise ValueError('No source transactions on configured analysis_end')
    if t.groupby('basket_id')[['store_id','household_id']].nunique().max().max()>1:
        raise ValueError('basket_id must be globally unique to one household and store; create a composite ID in source adapter')
    j=t.merge(products,on='product_id',how='left',validate='many_to_one',indicator=True)
    unmatched=j._merge.eq('left_only')
    if unmatched.mean()>config['max_unmatched_product_rate']: raise ValueError('Unmatched product rate exceeds configured quality gate')
    save(j.loc[unmatched,['product_id']].value_counts().rename('lines').reset_index(),directory,'unmatched_products')
    for c in ['product_category','department','brand']: j[c]=j[c].astype('string').fillna('UNKNOWN')
    good=(j.quantity>0)&(j.sales_value>0)
    save(j.loc[~good,['basket_id','product_id','date','quantity','sales_value']],directory,'model_excluded_lines')
    qa={'source_rows':len(raw),'in_scope_rows':len(j),'out_of_scope_rows':len(raw)-len(j),'start':str(t.date.min().date()),'end':str(end.date()),'raw_sales':float(j.sales_value.sum()),'positive_sales':float(j.loc[good,'sales_value'].sum()),'excluded_model_sales':float(j.loc[~good,'sales_value'].sum()),'model_excluded_rows':int((~good).sum()),'unmatched_product_rows':int(unmatched.sum()),'unmatched_product_rate':float(unmatched.mean()),'unknown_category_rows':int(j.product_category.eq('UNKNOWN').sum()),'basket_count':j.basket_id.nunique(),'households':j.household_id.nunique(),'stores':j.store_id.nunique(),'numeric_gate':'passed','join_gate':'passed','duplicates':0,'calendar_missing_days':int(len(pd.date_range(t.date.min(),end).difference(t.date.unique())))}
    assert np.isclose(qa['raw_sales'],qa['positive_sales']+qa['excluded_model_sales'])
    absent=pd.date_range(t.date.min(),end).difference(t.date.unique())
    allowed=pd.DatetimeIndex(pd.to_datetime(config.get('observed_zero_transaction_dates',[])))
    if len(absent.difference(allowed)): raise ValueError(f'Unacknowledged absent calendar dates: {absent.difference(allowed).tolist()}')
    qa['zero_transaction_dates_assumption']=[str(d.date()) for d in absent]
    qa['calendar_note']='Explicitly configured dates treated as zero observed panel receipts only, not proof of zero customer demand or store closure.'
    j.drop(columns='_merge').to_parquet(Path(directory)/'transactions_enriched.parquet',index=False)
    write_json(Path(directory)/'quality.json',qa)
    return j.drop(columns='_merge'),qa

def regression_metrics(y,p):
    y=np.asarray(y); p=np.asarray(p)
    return {'WAPE':float(np.abs(y-p).sum()/np.abs(y).sum()),'MAE':float(np.abs(y-p).mean()),'RMSE':float(np.sqrt(np.mean((y-p)**2))),'bias':float((p-y).sum()/np.abs(y).sum())}

def md_table(df, maxrows=12):
    x=df.head(maxrows).copy()
    for c in x.select_dtypes('number'): x[c]=x[c].map(lambda v:f'{v:,.4f}' if abs(v)<10 else f'{v:,.2f}')
    return '| '+' | '.join(map(str,x.columns))+' |\n|'+'|'.join(['---']*len(x.columns))+'|\n'+'\n'.join('| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in x.itertuples(index=False,name=None))
