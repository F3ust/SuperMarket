"""Score new complete data with the published models without retraining."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
import argparse,json
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import joblib
from .common import ROOT,ingest,save,write_json
from .models import forecast_frame,customer_snapshot
from .recommend import recommend

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(ROOT/'retail_pipeline/config.json'));parser.add_argument('--as-of');args=parser.parse_args()
    config=json.loads(open(args.config,encoding='utf-8').read())
    if args.as_of:config['analysis_end']=args.as_of
    root=ROOT/config['output_dir'];latest=json.loads((root/'latest.json').read_text(encoding='utf-8'));published=pd.Timestamp(config['analysis_end'])
    modeldir=__import__('pathlib').Path(latest['path'])/'models'
    forecast=joblib.load(modeldir/'sales_forecast.joblib');risk=joblib.load(modeldir/'customer_risk.joblib')
    if published<pd.Timestamp(forecast['trained_through']) or published<pd.Timestamp(risk['trained_label_end']):
        raise ValueError('Cannot use models trained after the scoring origin for a historical score')
    run=root/'scores'/datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%Y%m%d_%H%M%S_%f');run.mkdir(parents=True)
    write_json(run/'status.json',{'status':'running'})
    try:
        j,qa=ingest(config,run)
        frame,features,_,_=forecast_frame(j,config,vocabulary=forecast['category_vocabulary'])
        f=frame[frame.origin==published].copy();features=forecast['features']
        if not set(features).issubset(f):raise ValueError('Forecast schema changed')
        f['forecast']=np.maximum(0,forecast['model'].predict(f[features])*f.scale) if forecast['model'] is not None else (f.previous_7 if forecast['champion']=='last_7_days' else f.scale)
        q=forecast['residual_relative_quantile'];f['lower_heuristic']=np.maximum(0,f.forecast-q*f.scale);f['upper_heuristic']=f.forecast+q*f.scale
        f['target_start']=published+pd.Timedelta(days=1);f['target_end']=published+pd.Timedelta(days=7)
        save(f[['series','origin','forecast','lower_heuristic','upper_heuristic','target_start','target_end']],run,'forecast_next_7_days')
        customers=customer_snapshot(j,published,labeled=False)
        customers['risk_score']=risk['model'].predict_proba(customers[risk['features']])[:,1] if risk['model'] is not None else np.clip(customers.recency/90,0,1)
        customers=customers.sort_values('risk_score',ascending=False);customers['priority_top20']=np.arange(len(customers))<int(np.ceil(len(customers)*.2));save(customers,run,'customer_risk_actions')
        recommender=joblib.load(modeldir/'basket_recommender.joblib')
        recrows=[{'seed_category':seed,'rank':rank,'recommended_category':target,'champion':recommender['winner']} for seed in recommender['categories'] for rank,target in enumerate(recommend(recommender,seed),1)]
        save(pd.DataFrame(recrows),run,'category_recommendations')
        result={'status':'success','as_of':config['analysis_end'],'model_run_id':latest['run_id'],'model_train_end':forecast['trained_through'],'path':str(run),'mode':'score_only_no_retrain'}
        write_json(run/'status.json',result);temp=root/'latest_score.json.tmp';write_json(temp,result);os.replace(temp,root/'latest_score.json');print(json.dumps(result,ensure_ascii=False))
    except Exception as error:
        write_json(run/'status.json',{'status':'failed','error':str(error)});raise

if __name__=='__main__':main()
