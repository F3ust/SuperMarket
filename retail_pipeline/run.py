"""python -m retail_pipeline.run [--force] [--config path]"""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('MKL_NUM_THREADS','2')
import argparse,json,shutil,traceback,sys,platform,logging,sqlite3
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from contextlib import closing
import numpy as np
import pandas as pd
import sklearn,joblib,plotly
from .common import ROOT,ingest,input_signature,write_json
from .analytics import analyze,association_model
from .models import train_forecast,train_customer_risk
from .report import monitor,build_report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',default=str(ROOT/'retail_pipeline/config.json'));parser.add_argument('--force',action='store_true');args=parser.parse_args()
    config_path=Path(args.config).resolve();config=json.loads(config_path.read_text(encoding='utf-8'))
    if config['forecast_horizon_days']!=7 or config['risk_inactive_days']!=28 or config['risk_eligible_lookback_days']!=90 or config['top_customer_fraction']!=.2:raise ValueError('This evaluated implementation requires horizon=7, inactivity=28, eligibility=90 and selection fraction=.2. Revalidate code and metrics to change these policies.')
    output=ROOT/config['output_dir'];output.mkdir(parents=True,exist_ok=True)
    signature,inputs=input_signature(config,config_path)
    latest=output/'latest.json'
    if latest.exists() and not args.force and json.loads(latest.read_text(encoding='utf-8'))['signature']==signature:
        print(json.dumps({'status':'skipped_unchanged','latest':str(latest)},ensure_ascii=False));return 0
    lock=output/'pipeline.lock'
    try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError: raise RuntimeError('Pipeline lock exists; check live process before removing stale lock')
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    now=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'));run_id=now.strftime('%Y%m%d_%H%M%S_%f')+'_'+signature[:8]
    stage=output/('pending_'+run_id);stage.mkdir();(stage/'models').mkdir()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(stage/'pipeline.log',encoding='utf-8')],force=True)
    manifest={'run_id':run_id,'status':'running','started_at':now.isoformat(),'signature':signature,'inputs':inputs,'config':config,'versions':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'sklearn':sklearn.__version__,'joblib':joblib.__version__,'plotly':plotly.__version__}}
    try:
        logging.info('1/7 Ingest, validate, reconcile');j,qa=ingest(config,stage)
        logging.info('2/7 Business analytics and segmentation');analytics=analyze(j,config,stage)
        logging.info('3/7 Sales forecasting: train/validation/future holdout/refit');forecast=train_forecast(j,config,stage)
        logging.info('4/7 Customer non-purchase model: temporal validation/test/refit');risk=train_customer_risk(j,config,stage)
        logging.info('5/7 Basket rules and masked-basket holdout');association=association_model(j,config,stage)
        logging.info('6/7 Monitoring and offline report');monitoring=monitor(j,config,stage)
        build_report(stage,config,qa,analytics,forecast,risk,association,monitoring,manifest)
        registry={'run_id':run_id,'sales_forecast':forecast,'customer_risk':risk,'basket_recommender':association,'models_trusted_local_only':True,'deployment_status':'Offline validated demo, no POS integration or external customer actions'}
        write_json(stage/'models'/'model_registry.json',registry)
        logging.info('7/7 Artifact verification before publication')
        with closing(sqlite3.connect(stage/'business_mart.sqlite')) as database:
            for table in ['monthly_kpis','daily_kpis','department_monthly','brand_mix','product_abc','segment_summary','customer_segments','customer_risk_actions','forecast_next_7_days','business_insights_actions','campaign_redemption']:
                source=stage/f'{table}.csv'
                if source.exists():
                    columns=pd.read_csv(source,nrows=0).columns
                    ids={c:'string' for c in ['household_id','store_id','basket_id','product_id','campaign_id'] if c in columns}
                    pd.read_csv(source,dtype=ids).to_sql(table,database,index=False,if_exists='replace')
            sqltotal=database.execute('SELECT SUM(sales) FROM monthly_kpis').fetchone()[0]
            assert np.isclose(sqltotal,qa['raw_sales'])
        monthly=pd.read_csv(stage/'monthly_kpis.csv');assert np.isclose(monthly.sales.sum(),qa['raw_sales'])
        assert np.isclose(j.sales_value.sum(),pd.read_parquet(stage/'transactions_enriched.parquet',columns=['sales_value']).sales_value.sum())
        for name in ['sales_forecast','customer_risk','basket_recommender']: assert joblib.load(stage/'models'/f'{name}.joblib')
        assert (stage/'report.html').stat().st_size>10000
        manifest.update(status='success',finished_at=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),checks={'money_reconciliation':'passed','join_cardinality':'passed','model_reload':'passed','artifact_presence':'passed'})
        write_json(stage/'run_manifest.json',manifest)
        # Refuse to publish results if code, config or source was edited mid-run.
        if input_signature(config,config_path)[0]!=signature:raise RuntimeError('Input/code/config changed during run; rerun for a consistent snapshot')
        # Close Windows file handles before renaming the staging folder.
        logging.info('Run completed successfully: %s',run_id);logging.shutdown()
        published=output/run_id;stage.rename(published)
        # latest.json is the authoritative commit pointer; reports replaced before it.
        for name,target in [('report.html','latest_report.html'),('report.md','latest_report.md')]:
            temp=output/(target+'.tmp');shutil.copy2(published/name,temp);os.replace(temp,output/target)
        tmp=output/'latest.json.tmp';write_json(tmp,{'run_id':run_id,'path':str(published),'signature':signature,'status':'success'});os.replace(tmp,latest)
        print(json.dumps({'status':'success','run_id':run_id,'report':str(output/'latest_report.html')},ensure_ascii=False));return 0
    except Exception as error:
        logging.exception('Pipeline failed; previous latest output retained')
        manifest.update(status='failed',error=str(error),traceback=traceback.format_exc());write_json(stage/'run_manifest.json',manifest);write_json(output/'last_failure.json',{'run_id':run_id,'error':str(error),'path':str(stage)})
        return 1
    finally:
        logging.shutdown();lock.unlink(missing_ok=True)

if __name__=='__main__':sys.exit(main())
