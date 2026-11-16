"""Train/export actual Probit models with temporal validation and held-out tests.
Uploaded files never participate in this training job.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import sys,json,hashlib,warnings
import numpy as np,pandas as pd,joblib
from scipy.special import ndtr
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss,brier_score_loss,average_precision_score
P=Path(__file__).resolve().parent;ROOT=P.parent
sys.path.insert(0,str(ROOT))
from retail_pipeline.models import customer_snapshot
RUN=Path(json.loads((ROOT/'outputs/enterprise/latest.json').read_text(encoding='utf-8'))['path'])
OUT=ROOT/'outputs/probability_models';OUT.mkdir(exist_ok=True)
from probability_runtime import FEATURES,LOG,raw_matrix,predict
TASKS=[('no_purchase_28','binary','Không mua dương trong 28 ngày',28,['Có mua','Không mua']),('return_time_56','ordered','Thời gian tới lần mua tiếp theo',56,['1–7 ngày','8–14 ngày','15–28 ngày','29–56 ngày','Chưa mua trong 56 ngày']),('visits_28','ordered','Phân phối số giỏ mua dương trong 28 ngày',28,['0 giỏ','1 giỏ','2–3 giỏ','4–7 giỏ','8+ giỏ']),('decline_30','binary','Giá trị mua 28 ngày tới giảm ít nhất 30%',28,['Không đạt điều kiện giảm','Giảm ≥30%']),('discount_purchase_28','binary','Có lần mua được giảm giá trong 28 ngày',28,['Không quan sát lần mua giảm giá','Có lần mua giảm giá'])]
def snapshot(j,origin):
 origin=pd.Timestamp(origin);f=customer_snapshot(j,origin,labeled=False)
 future=j[(j.quantity>0)&(j.sales_value>0)&(j.date>origin)&(j.date<=origin+pd.Timedelta(days=56))]
 first=future.groupby('household_id').date.min();gap=(first-origin).dt.days
 f['return_time_56']=f.household_id.map(gap).map(lambda x:0 if x<=7 else 1 if x<=14 else 2 if x<=28 else 3 if x<=56 else 4).astype(int)
 fut28=future[future.date<=origin+pd.Timedelta(days=28)]
 visits=fut28.groupby('household_id').basket_id.nunique();sales=fut28.groupby('household_id').sales_value.sum()
 nextvis=f.household_id.map(visits).fillna(0);f['no_purchase_28']=(nextvis==0).astype(int)
 f['visits_28_label']=np.select([nextvis.eq(0),nextvis.eq(1),nextvis.le(3),nextvis.le(7)],[0,1,2,3],default=4).astype(int)
 f['decline_30']=(f.household_id.map(sales).fillna(0)<=f.sales_28*.7).astype(int)
 disc=fut28[(fut28[['retail_disc','coupon_disc','coupon_match_disc']]!=0).any(axis=1)].household_id.unique()
 f['discount_purchase_28']=f.household_id.isin(disc).astype(int)
 return f
def y_task(f,task):return f['visits_28_label' if task=='visits_28' else task].to_numpy(dtype=int)
def eligible(f,task):return f[f.sales_28>0].copy() if task=='decline_30' else f.copy()
def fit_model(f,task,kind):
 f=eligible(f,task);scaler=StandardScaler().fit(raw_matrix(f));x=scaler.transform(raw_matrix(f));y=y_task(f,task)
 if kind=='binary':
  # Fixed, documented L2 regularization; no test-based tuning or pseudo-calibration.
  m=sm.GLM(y,sm.add_constant(x,has_constant='add'),family=sm.families.Binomial(link=sm.families.links.Probit()))
  r=m.fit_regularized(alpha=np.r_[0,np.repeat(.001,x.shape[1])],L1_wt=0,maxiter=400,cnvrg_tol=1e-9)
  coeff=np.asarray(r.params);gradient=np.asarray(m.score(coeff))/len(y)-np.r_[0,.001*coeff[1:]]
  if np.max(np.abs(gradient))>1e-4:raise RuntimeError('Penalized Probit gradient not converged: '+task)
  probs=ndtr(coeff[0]+x@coeff[1:]);params={'intercept':float(coeff[0]),'coefficients':coeff[1:].tolist(),'fit':'GLM Binomial / Probit + fixed L2=.001','converged':True}
 else:
  m=OrderedModel(y,x,distr='probit');r=m.fit(method='bfgs',maxiter=350,disp=False,gtol=1e-5)
  converged=bool(r.mle_retvals.get('converged',False))
  if not converged:raise RuntimeError(f'Ordered Probit did not converge: {task}')
  threshold=m.transform_threshold_params(r.params)[1:-1];coef=np.asarray(r.params[:x.shape[1]])
  params={'intercept':0,'coefficients':coef.tolist(),'thresholds':threshold.tolist(),'fit':'OrderedModel / probit / BFGS MLE','converged':converged}
 return {'task':task,'kind':kind,'features':FEATURES,'log1p':LOG,'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),**params,'training_rows':len(f)},r
def metrics(y,p,kind):
 if kind=='binary':return {'log_loss':float(log_loss(y,p,labels=[0,1])),'Brier':float(brier_score_loss(y,p)),'AP':float(average_precision_score(y,p)),'observed_rate':float(y.mean()),'predicted_rate':float(p.mean()),'n':len(y)}
 onehot=np.eye(p.shape[1])[y];return {'log_loss':float(log_loss(y,p,labels=list(range(p.shape[1])))),'Brier_multiclass_sum':float(np.square(p-onehot).sum(axis=1).mean()),'n':len(y),'observed_mix':np.bincount(y,minlength=p.shape[1]).tolist(),'predicted_mix':p.mean(axis=0).tolist()}
def main():
 j=pd.read_parquet(RUN/'transactions_enriched.parquet');end=pd.Timestamp('2017-12-31')
 origins=list(pd.date_range('2017-04-09','2017-12-03',freq='28D'))+[pd.Timestamp('2017-06-18'),pd.Timestamp('2017-08-13'),pd.Timestamp('2017-10-08'),pd.Timestamp('2017-11-05')]
 origins=sorted(set(origins));frames={o:snapshot(j,o) for o in origins};validation=pd.Timestamp('2017-08-13');tests=[pd.Timestamp('2017-10-08'),pd.Timestamp('2017-11-05')]
 models=[];evaluations=[];checks=[]
 for task,kind,name,h,classes in TASKS:
  train=pd.concat([f for o,f in frames.items() if o+pd.Timedelta(days=h)<=validation],ignore_index=True)
  assert max(pd.to_datetime(train.origin))+pd.Timedelta(days=h)<=validation
  model,_=fit_model(train,task,kind);val=eligible(frames[validation],task);prior=y_task(eligible(train,task),task)
  valm=metrics(y_task(val,task),predict(model,val),kind)
  for o in tests:
   assert validation+pd.Timedelta(days=h)<=o
   f=eligible(frames[o],task);y=y_task(f,task);p=predict(model,f)
   bp=np.repeat(prior.mean(),len(y)) if kind=='binary' else np.tile(np.bincount(prior,minlength=len(classes))/len(prior),(len(y),1))
   evaluations.append({'task':task,'model':name,'origin':str(o.date()),'kind':kind,'metrics':metrics(y,p,kind),'baseline':metrics(y,bp,kind),'validation':valm})
  # Final refit only on matured targets by the fixed training cutoff.
  final=pd.concat([f for o,f in frames.items() if o+pd.Timedelta(days=h)<=end],ignore_index=True);final_model,result=fit_model(final,task,kind)
  final_model.update(name=name,horizon=h,classes=classes,trainedThrough=str(end.date()),validation_origin=str(validation.date()),test_origins=[str(t.date()) for t in tests],eligibility='Positive purchase in preceding 90 days; decline task additionally sales_28 > 0',range01=np.quantile(final[FEATURES].to_numpy(dtype=float),.01,axis=0).tolist(),range99=np.quantile(final[FEATURES].to_numpy(dtype=float),.99,axis=0).tolist())
  canonical=json.dumps(final_model,sort_keys=True,separators=(',',':')).encode();final_model['model_id']=task+'_'+hashlib.sha256(canonical).hexdigest()[:12];models.append(final_model)
  joblib.dump({'model':result,'portable':final_model,'trusted_local_only':True},OUT/(task+'.joblib'))
  sample=eligible(frames[tests[-1]],task).iloc[:40];checks.append({'task':task,'x':sample[FEATURES].values.tolist(),'expected':predict(final_model,sample).tolist()})
  print(json.dumps({'trained':task,'rows':len(final),'validation':valm},ensure_ascii=True),flush=True)
 signature=json.loads((RUN/'run_manifest.json').read_text(encoding='utf-8'))['signature']
 registry={'version':'probit_v1','source_signature':signature,'source_run':RUN.name,'trainedThrough':'2017-12-31','feature_version':'retail_90d_v1','features':FEATURES,'models':models,'evaluations':evaluations,'calibration':'No separate post-hoc calibration. Inspect held-out Brier, log loss and reliability; do not treat as guaranteed probabilities.','test_caveat':'Repeated households; 56-day test windows overlap by 28 days. Only two origins, not independent replications. Fixed model specification; no test-based selection.','provenance':'Trained only on historical Complete Journey data, no uploaded rows. Source data household panel, not full-store POS.','references':['https://www.statsmodels.org/stable/glm.html','https://www.statsmodels.org/stable/generated/statsmodels.miscmodels.ordinal_model.OrderedModel.html']}
 (OUT/'registry.json').write_text(json.dumps(registry,ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8');(P/'probability_registry.json').write_bytes((OUT/'registry.json').read_bytes())
 (OUT/'parity_cases.json').write_text(json.dumps(checks,allow_nan=False),encoding='utf-8')
 print('DONE: five trained probability models, temporal evaluation, portable coefficients and parity fixtures.',flush=True)
if __name__=='__main__':main()
