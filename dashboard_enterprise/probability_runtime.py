"""Pure frozen-model runtime; no training, filesystem side effects or pickle loading."""
import numpy as np
import pandas as pd
from scipy.special import ndtr
FEATURES=['recency','visits_7','visits_28','visits_90','sales_ratio','categories_28','discount_line_share_90','aov_90']
LOG=[False,True,True,True,True,True,False,True]
def raw_matrix(f):
 a=f[FEATURES].to_numpy(dtype=float,copy=True)
 for i,log in enumerate(LOG):
  if log:a[:,i]=np.log1p(a[:,i])
 if not np.isfinite(a).all():raise ValueError('Non-finite model features')
 return a
def predict(model,f):
 x=(raw_matrix(f)-np.array(model['mean']))/np.array(model['scale']);eta=model['intercept']+x@np.array(model['coefficients'])
 if model['kind']=='binary':return ndtr(eta)
 cumulative=ndtr(np.array(model['thresholds'])[None,:]-eta[:,None])
 return np.diff(np.c_[np.zeros(len(cumulative)),cumulative,np.ones(len(cumulative))],axis=1)
def snapshot_features(df,origin):
 origin=pd.Timestamp(origin);hist=df[(df.quantity>0)&(df.sales_value>0)&(df.date<=origin)&(df.date>origin-pd.Timedelta(days=90))].copy()
 if hist.empty:return pd.DataFrame()
 f=hist.groupby('household_id').agg(last_date=('date','max'))
 f['recency']=(origin-f.last_date).dt.days
 for days in [7,28,56,90]:
  sub=hist[hist.date>origin-pd.Timedelta(days=days)]
  g=sub.groupby('household_id').agg(**{f'sales_{days}':('sales_value','sum'),f'visits_{days}':('basket_id','nunique'),f'categories_{days}':('product_category','nunique')})
  f=f.join(g).fillna({c:0 for c in g})
 f['sales_ratio']=(f.sales_28+1)/(f.sales_56/2+1)
 f['aov_90']=f.sales_90/f.visits_90.clip(lower=1)
 hist['discounted']=(hist[['retail_disc','coupon_disc','coupon_match_disc']]!=0).any(axis=1)
 f=f.join(hist.groupby('household_id').discounted.mean().rename('discount_line_share_90')).fillna({'discount_line_share_90':0})
 return f.drop(columns=['last_date']).reset_index()
