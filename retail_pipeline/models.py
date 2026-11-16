import json
import numpy as np
import pandas as pd
import joblib
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingRegressor, ExtraTreesRegressor, HistGradientBoostingClassifier
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss
from sklearn.inspection import permutation_importance
from .common import save,write_json,regression_metrics

def forecast_frame(j,config,vocabulary=None):
    end=pd.Timestamp(config['analysis_end']);start=j.date.min()
    # Vocabulary frozen in early history, before all validation and test origins.
    selection_end=start+pd.Timedelta(days=179)
    names=vocabulary if vocabulary is not None else j[j.date<=selection_end].groupby('product_category').sales_value.sum().nlargest(config['forecast_categories']).index.tolist()
    z=j.copy();z['series']=z.product_category.where(z.product_category.isin(names),'OTHER')
    days=pd.date_range(start,end);daily=z.groupby(['series','date']).sales_value.sum().unstack('series').reindex(days,fill_value=0).fillna(0)
    daily=daily.reindex(columns=sorted(names+['OTHER']),fill_value=0)
    if (daily<0).any().any(): raise ValueError('Negative daily series totals require an explicit net-return forecast policy')
    frames=[]
    for name in sorted(daily.columns):
        y=daily[name].clip(lower=0)
        f=pd.DataFrame({'origin':days,'series':name,'dayofweek':days.dayofweek,'month':days.month,'dayofyear':days.dayofyear})
        f['series_code']=sorted(daily.columns).index(name)
        for lag in [0,1,6,7,13,27]: f[f'lag_{lag}']=y.shift(lag).values
        for window in [7,14,28,56]:
            roll=y.rolling(window,min_periods=window)
            f[f'mean_{window}']=roll.mean().values; f[f'std_{window}']=roll.std().values
        f['previous_7']=y.rolling(7).sum().values
        f['scale']=(y.rolling(28).mean()*7).clip(lower=1).values
        f['trend_7_28']=(f.mean_7+1)/(f.mean_28+1)
        f['target']=y.iloc[::-1].shift(1).rolling(7,min_periods=7).sum().iloc[::-1].values
        f['history_days']=(days-start).days
        frames.append(f)
    frame=pd.concat(frames,ignore_index=True)
    frame=pd.get_dummies(frame,columns=['series_code'],dtype=float)
    features=[c for c in frame if c not in ['origin','series','target','history_days']]
    frame=frame[frame.history_days>=83].copy()
    return frame,features,names,daily

def train_forecast(j,config,out):
    frame,features,names,daily=forecast_frame(j,config)
    end=pd.Timestamp(config['analysis_end']);h=7
    test_origins=[end-pd.Timedelta(days=v) for v in [28,21,14,7]]
    val_origins=[test_origins[0]-pd.Timedelta(days=v) for v in [84,56,28]]
    candidates={'ridge':make_pipeline(StandardScaler(),Ridge(alpha=100)),
        'hist_gradient_small':HistGradientBoostingRegressor(max_iter=160,max_leaf_nodes=7,learning_rate=.05,l2_regularization=10,early_stopping=False,random_state=42),
        'hist_gradient_medium':HistGradientBoostingRegressor(max_iter=160,max_leaf_nodes=15,learning_rate=.05,l2_regularization=20,early_stopping=False,random_state=42),
        'extra_trees':ExtraTreesRegressor(n_estimators=160,max_depth=12,min_samples_leaf=8,n_jobs=2,random_state=42)}
    predrows=[]
    for origin in val_origins:
        tr=frame[(frame.origin+pd.Timedelta(days=h)<=origin)&frame.target.notna()];te=frame[frame.origin==origin]
        assert tr.origin.max()+pd.Timedelta(days=h)<=origin
        for name,template in candidates.items():
            model=clone(template).fit(tr[features],tr.target/tr.scale)
            pred=np.maximum(0,model.predict(te[features])*te.scale)
            for series,y,p,scale in zip(te.series,te.target,pred,te.scale):predrows.append([origin,series,name,y,p,scale])
        for name,values in [('last_7_days',te.previous_7),('mean_28_days',te.scale)]:
            for series,y,p,scale in zip(te.series,te.target,values,te.scale):predrows.append([origin,series,name,y,p,scale])
    vp=pd.DataFrame(predrows,columns=['origin','series','model','actual','prediction','scale'])
    leaderboard=pd.DataFrame([{'model':name,**regression_metrics(g.actual,g.prediction)} for name,g in vp.groupby('model')]).sort_values('WAPE')
    champion=leaderboard.iloc[0].model
    save(vp,out,'forecast_validation_predictions');save(leaderboard,out,'forecast_validation_leaderboard')
    # Frozen champion choice; independent expanding training at each test origin.
    testrows=[];test_models=[champion,'last_7_days','mean_28_days']+list(candidates)
    for origin in test_origins:
        tr=frame[(frame.origin+pd.Timedelta(days=h)<=origin)&frame.target.notna()];te=frame[frame.origin==origin]
        for name in dict.fromkeys(test_models):
            if name in candidates:
                fit=clone(candidates[name]).fit(tr[features],tr.target/tr.scale)
                prediction=np.maximum(0,fit.predict(te[features])*te.scale)
            else:prediction=te.previous_7 if name=='last_7_days' else te.scale
            for series,y,p in zip(te.series,te.target,prediction):testrows.append([origin,series,name,y,p])
    tp=pd.DataFrame(testrows,columns=['origin','series','model','actual','prediction'])
    scores=pd.DataFrame([{'model':name,**regression_metrics(g.actual,g.prediction)} for name,g in tp.groupby('model')]).sort_values('WAPE');save(scores,out,'forecast_test_metrics');save(tp,out,'forecast_test_predictions')
    assumed=pd.to_datetime(config.get('observed_zero_transaction_dates',[]))
    clean=tp[~tp.origin.map(lambda o:any(o<d<=o+pd.Timedelta(days=h) for d in assumed))]
    sensitivity=pd.DataFrame([{'model':name,**regression_metrics(g.actual,g.prediction),'series_origin_rows':len(g)} for name,g in clean.groupby('model')]);save(sensitivity,out,'forecast_test_without_assumed_zero_week')
    selected_val=vp[vp.model==champion];q=float(np.quantile(np.abs(selected_val.actual-selected_val.prediction)/selected_val.scale,.9,method='higher'))
    selected_test=tp[tp.model==champion].merge(frame[['origin','series','scale']],on=['origin','series'],validate='one_to_one')
    selected_test['lower']=np.maximum(0,selected_test.prediction-q*selected_test.scale);selected_test['upper']=selected_test.prediction+q*selected_test.scale
    coverage=float(selected_test.actual.between(selected_test.lower,selected_test.upper).mean())
    save(selected_test,out,'forecast_test_intervals')
    byseries=pd.DataFrame([{'series':series,**regression_metrics(g.actual,g.prediction)} for series,g in selected_test.groupby('series')]);save(byseries,out,'forecast_series_metrics')
    train=frame[frame.target.notna()&(frame.origin+pd.Timedelta(days=h)<=end)];latest=frame[frame.origin==end]
    fit=clone(candidates[champion]).fit(train[features],train.target/train.scale) if champion in candidates else None
    # Preserve trained challengers for audit/research; champion still chosen only on validation.
    (out/'models'/'challengers').mkdir(exist_ok=True)
    for candidate_name,template in candidates.items():
        challenger=clone(template).fit(train[features],train.target/train.scale)
        joblib.dump({'model':challenger,'features':features,'category_vocabulary':names,'target_scale':'target / max(1, mean_28_days*7)','selection_status':'research challenger, not production champion'},out/'models'/'challengers'/f'forecast_{candidate_name}.joblib')
    pred=np.maximum(0,fit.predict(latest[features])*latest.scale) if fit is not None else (latest.previous_7 if champion=='last_7_days' else latest.scale)
    future=latest[['series','origin','scale']].copy();future['forecast']=np.asarray(pred);future['lower_heuristic']=np.maximum(0,future.forecast-q*future.scale);future['upper_heuristic']=future.forecast+q*future.scale
    future['target_start']=end+pd.Timedelta(days=1);future['target_end']=end+pd.Timedelta(days=h);save(future,out,'forecast_next_7_days')
    joblib.dump({'model':fit,'champion':champion,'features':features,'category_vocabulary':names,'horizon_days':h,'trained_through':str(end.date()),'residual_relative_quantile':q,'target':'next 7 days observed panel sales_value; not units or full-store demand'},out/'models'/'sales_forecast.joblib')
    # Independent driver diagnostics after champion has already been selected.
    if fit is not None:
        diagnostic_origin=val_origins[-1];tr=frame[frame.origin+pd.Timedelta(days=h)<=diagnostic_origin];te=frame[frame.origin==diagnostic_origin]
        diagnostic=clone(candidates[champion]).fit(tr[features],tr.target/tr.scale)
        importance=permutation_importance(diagnostic,te[features],te.target/te.scale,scoring='neg_mean_absolute_error',n_repeats=5,random_state=42,n_jobs=1)
        save(pd.DataFrame({'feature':features,'importance_mean':importance.importances_mean,'importance_std':importance.importances_std}).sort_values('importance_mean',ascending=False),out,'forecast_feature_importance')
    result={'champion_selected_on_validation':champion,'validation_origins':[str(v.date()) for v in val_origins],'test_origins':[str(v.date()) for v in test_origins],'test_metrics':scores.to_dict('records'),'validation_leaderboard':leaderboard.to_dict('records'),'interval_empirical_test_coverage':coverage,'interval_label':'Heuristic 90th percentile relative residual band, not formal calibrated prediction interval. 63 validation series-origin observations; correlated groups.','vocabulary_selection_end':str((j.date.min()+pd.Timedelta(days=179)).date()),'series_count':daily.shape[1],'training_rows_final':len(train),'feature_count':len(features),'scope':'All panel sales_value summed across stores, 20 early-history top categories + OTHER. Next 7 calendar days, expanding origin evaluation.'}
    write_json(out/'forecast_summary.json',result)
    frame.to_parquet(out/'forecast_features.parquet',index=False)
    return result

def customer_snapshot(j,origin,horizon=28,labeled=True):
    pos=j[(j.quantity>0)&(j.sales_value>0)]
    hist=pos[pos.date<=origin];recent=hist[hist.date>origin-pd.Timedelta(days=90)]
    eligible=recent.household_id.unique()
    allhist=hist.groupby('household_id').agg(last_date=('date','max'),first_date=('date','min'))
    f=pd.DataFrame(index=pd.Index(eligible,name='household_id')).join(allhist)
    f['recency']=(origin-f.last_date).dt.days;f['observed_tenure']=(origin-f.first_date).dt.days
    for window in [7,28,56,90]:
        sub=hist[hist.date>origin-pd.Timedelta(days=window)]
        values=sub.groupby('household_id').agg(**{f'sales_{window}':('sales_value','sum'),f'visits_{window}':('basket_id','nunique'),f'categories_{window}':('product_category','nunique')})
        f=f.join(values).fillna({c:0 for c in values})
    f['aov_90']=f.sales_90/f.visits_90.clip(lower=1)
    f['sales_ratio']=(f.sales_28+1)/(f.sales_56/2+1)
    sub=recent.copy();sub['discounted']=(sub[['retail_disc','coupon_disc','coupon_match_disc']]!=0).any(axis=1)
    f=f.join(sub.groupby('household_id').discounted.mean().rename('discount_line_share_90')).fillna({'discount_line_share_90':0})
    if labeled:
        future=pos[(pos.date>origin)&(pos.date<=origin+pd.Timedelta(days=horizon))]
        f['no_purchase_next_28']=~f.index.isin(future.household_id.unique())
    f['origin']=origin
    return f.drop(columns=['last_date','first_date']).reset_index()

def classification_metrics(y,p):
    y=np.asarray(y).astype(int);p=np.asarray(p);n=max(1,int(np.ceil(len(y)*.2)))
    order=np.argsort(-p,kind='stable');base=float(y.mean());prec=float(y[order[:n]].mean())
    return {'PR_AUC_AP':float(average_precision_score(y,p)),'ROC_AUC':float(roc_auc_score(y,p)) if len(set(y))>1 else None,'Brier':float(brier_score_loss(y,p)),'prevalence':base,'precision_top20':prec,'recall_top20':float(y[order[:n]].sum()/y.sum()) if y.sum() else None,'lift_top20':prec/base if base else None,'n':len(y)}

def train_customer_risk(j,config,out):
    end=pd.Timestamp(config['analysis_end']);h=28
    origins=[end-pd.Timedelta(days=v) for v in [252,224,196,168,140,112,84,56,28]]
    data=pd.concat([customer_snapshot(j,o) for o in origins],ignore_index=True)
    features=[c for c in data if c not in ['household_id','origin','no_purchase_next_28']]
    valid=origins[-4] # 112 days before end; test remains last two snapshots.
    tr=data[data.origin+pd.Timedelta(days=h)<=valid];va=data[data.origin==valid]
    candidates={'logistic':make_pipeline(StandardScaler(),LogisticRegression(C=.1,max_iter=1000,random_state=42)),
        'hist_gradient':HistGradientBoostingClassifier(max_iter=120,max_leaf_nodes=7,learning_rate=.05,l2_regularization=20,early_stopping=False,random_state=42)}
    assert tr.origin.max()+pd.Timedelta(days=h)<=valid
    leaderboard=[];val_predictions=[]
    for name in ['recency_rule']+list(candidates):
        model=clone(candidates[name]).fit(tr[features],tr.no_purchase_next_28) if name in candidates else None
        prob=model.predict_proba(va[features])[:,1] if model is not None else np.clip(va.recency/90,0,1)
        leaderboard.append({'model':name,**classification_metrics(va.no_purchase_next_28,prob)})
        val_predictions.append(pd.DataFrame({'household_id':va.household_id,'model':name,'actual':va.no_purchase_next_28,'score':prob}))
    lb=pd.DataFrame(leaderboard).sort_values('PR_AUC_AP',ascending=False);champion=lb.iloc[0].model
    save(lb,out,'risk_validation_leaderboard');save(pd.concat(val_predictions),out,'risk_validation_predictions')
    firsttest=origins[-2];train=data[data.origin+pd.Timedelta(days=h)<=firsttest]
    model=clone(candidates[champion]).fit(train[features],train.no_purchase_next_28) if champion in candidates else None
    records=[];tests=[]
    for origin in origins[-2:]:
        te=data[data.origin==origin]
        for name in dict.fromkeys([champion,'recency_rule']):
            prob=model.predict_proba(te[features])[:,1] if name==champion and model is not None else np.clip(te.recency/90,0,1)
            records.append({'origin':str(origin.date()),'model':name,**classification_metrics(te.no_purchase_next_28,prob)})
            tests.append(pd.DataFrame({'household_id':te.household_id,'origin':origin,'model':name,'actual':te.no_purchase_next_28,'score':prob}))
    save(pd.DataFrame(records),out,'risk_test_metrics');save(pd.concat(tests),out,'risk_test_predictions')
    final=clone(candidates[champion]).fit(data[features],data.no_purchase_next_28) if champion in candidates else None
    latest=customer_snapshot(j,end,labeled=False)
    latest['risk_score']=final.predict_proba(latest[features])[:,1] if final is not None else np.clip(latest.recency/90,0,1)
    latest=latest.sort_values('risk_score',ascending=False);latest['priority_top20']=np.arange(len(latest))<int(np.ceil(len(latest)*.2));save(latest,out,'customer_risk_actions')
    if champion in candidates:
        modelval=clone(candidates[champion]).fit(tr[features],tr.no_purchase_next_28)
        imp=permutation_importance(modelval,va[features],va.no_purchase_next_28,scoring='average_precision',n_repeats=5,random_state=42)
        save(pd.DataFrame({'feature':features,'importance_mean':imp.importances_mean,'importance_std':imp.importances_std}).sort_values('importance_mean',ascending=False),out,'risk_feature_importance')
    joblib.dump({'model':final,'champion':champion,'features':features,'label':'No observed positive purchase in next 28 days among households active in previous 90 days','trained_label_end':str(end.date()),'not_causal':'Risk does not estimate treatment responsiveness or incremental value'},out/'models'/'customer_risk.joblib')
    data.to_parquet(out/'risk_features_labeled.parquet',index=False)
    result={'champion_selected_on_validation':champion,'validation_origin':str(valid.date()),'test_origins':[str(v.date()) for v in origins[-2:]],'final_label_end':str(end.date()),'validation_leaderboard':lb.to_dict('records'),'test_metrics':records,'scored_households':len(latest),'all_observed_households':j.household_id.nunique(),'not_scored_inactive_over_90_days':j.household_id.nunique()-len(latest),'policy':'Rank top 20% for review; no automatic messages. Brier reported; probabilities not separately calibrated. Repeated households across snapshots are expected, evaluated by calendar origin.'}
    write_json(out/'risk_summary.json',result)
    return result
