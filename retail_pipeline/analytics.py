from collections import Counter
from itertools import combinations
import hashlib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from .common import ROOT, save, read_table, write_json

def analyze(j,config,out):
    positive=j[(j.quantity>0)&(j.sales_value>0)].copy()
    j['month']=j.date.dt.to_period('M').astype(str)
    baskets=j.groupby('basket_id').agg(sales=('sales_value','sum'),date=('date','first'),household_id=('household_id','first'),store_id=('store_id','first'),distinct_products=('product_id','nunique')).reset_index()
    monthly=j.groupby('month').agg(sales=('sales_value','sum'),baskets=('basket_id','nunique'),households=('household_id','nunique')).reset_index()
    monthly['aov']=monthly.sales/monthly.baskets
    monthly['sales_mom']=monthly.sales.pct_change()
    save(monthly,out,'monthly_kpis')
    daily=baskets.groupby('date').agg(sales=('sales','sum'),baskets=('basket_id','size'),households=('household_id','nunique')).reset_index()
    daily=daily.set_index('date').reindex(pd.date_range(j.date.min(),config['analysis_end']),fill_value=0).rename_axis('date').reset_index()
    save(daily,out,'daily_kpis')
    dept=j.groupby(['month','department']).sales_value.sum().reset_index(name='sales'); save(dept,out,'department_monthly')
    brand=j.groupby('brand').agg(sales=('sales_value','sum'),lines=('product_id','size')).reset_index(); brand['share']=brand.sales/brand.sales.sum();save(brand,out,'brand_mix')
    store=j.groupby('store_id').agg(panel_sales=('sales_value','sum'),observed_households=('household_id','nunique'),observed_baskets=('basket_id','nunique')).reset_index().sort_values('panel_sales',ascending=False); save(store,out,'store_panel_coverage')
    timing=j.groupby([j.date.dt.day_name().rename('weekday'),j.transaction_timestamp.dt.hour.rename('hour')]).agg(sales=('sales_value','sum'),baskets=('basket_id','nunique')).reset_index();save(timing,out,'weekday_hour')
    products=positive.groupby('product_id').agg(sales=('sales_value','sum'),baskets=('basket_id','nunique'),days_sold=('date','nunique'),category=('product_category','first'),brand=('brand','first')).reset_index().sort_values('sales',ascending=False)
    # Allocate class using cumulative share before the current item, including crossing item.
    products['cumulative_share']=products.sales.cumsum()/products.sales.sum()
    before=products.cumulative_share-products.sales/products.sales.sum()
    products['ABC']=np.select([before<.8,before<.95],['A','B'],default='C');save(products,out,'product_abc')
    bridge=[]
    for i in range(1,len(monthly)):
        a,b=monthly.iloc[i-1],monthly.iloc[i]
        bridge.append({'month':b.month,'previous':a.month,'sales_delta':b.sales-a.sales,'basket_count_effect':(b.baskets-a.baskets)*(a.aov+b.aov)/2,'basket_value_effect':(b.aov-a.aov)*(a.baskets+b.baskets)/2})
    bridge=pd.DataFrame(bridge); assert np.allclose(bridge.sales_delta,bridge.basket_count_effect+bridge.basket_value_effect);save(bridge,out,'sales_bridge')
    active=baskets.assign(month=lambda d:d.date.dt.to_period('M'))[['household_id','month']].drop_duplicates()
    first=active.groupby('household_id').month.min().rename('first_observed_month')
    active=active.join(first,on='household_id');active['age_month']=active.month.astype('int64')-active.first_observed_month.astype('int64')
    cohort=active.groupby(['first_observed_month','age_month']).household_id.nunique().reset_index(name='active_households')
    sizes=first.value_counts();cohort['cohort_size']=cohort.first_observed_month.map(sizes);cohort['active_rate']=cohort.active_households/cohort.cohort_size
    cohort['first_observed_month']=cohort.first_observed_month.astype(str);save(cohort,out,'observed_cohorts')
    end=pd.Timestamp(config['analysis_end'])
    cust=positive.groupby('household_id').agg(sales=('sales_value','sum'),frequency=('basket_id','nunique'),last_date=('date','max'),first_date=('date','min'),categories=('product_category','nunique')).reset_index()
    cust['recency']=(end-cust.last_date).dt.days
    m75=cust.sales.quantile(.75); f75=cust.frequency.quantile(.75)
    cust['segment']=np.select([(cust.recency>=28)&(cust.sales>=m75),(cust.recency<=14)&(cust.sales>=m75)&(cust.frequency>=f75),(end-cust.first_date).dt.days<=30,cust.frequency>=f75],['Giá trị cao, cần kiểm tra giảm mua','Khách hàng chủ lực','Mới xuất hiện trong dữ liệu','Mua thường xuyên'],default='Nhóm còn lại')
    x=StandardScaler().fit_transform(np.log1p(cust[['sales','frequency','recency','categories']]))
    silhouettes=[]
    for k in [3,4,5,6]:
        model=KMeans(k,random_state=config['random_seed'],n_init=10).fit(x)
        silhouettes.append({'k':k,'silhouette':silhouette_score(x,model.labels_,sample_size=min(1000,len(x)),random_state=42)})
    best=max(silhouettes,key=lambda z:z['silhouette']);km=KMeans(best['k'],random_state=42,n_init=10).fit(x)
    cust['cluster']=km.labels_
    stability=adjusted_rand_score(km.labels_,KMeans(best['k'],random_state=7,n_init=10).fit_predict(x))
    save(cust,out,'customer_segments');save(pd.DataFrame(silhouettes),out,'cluster_selection')
    segments=cust.groupby('segment').agg(households=('household_id','size'),sales=('sales','sum'),mean_recency=('recency','mean'),mean_frequency=('frequency','mean')).reset_index();segments['sales_share']=segments.sales/segments.sales.sum();save(segments,out,'segment_summary')
    clusters=cust.groupby('cluster').agg(households=('household_id','size'),sales=('sales','sum'),mean_recency=('recency','mean'),mean_frequency=('frequency','mean')).reset_index();save(clusters,out,'cluster_profiles')
    # Observational, not promotional causal uplift. Signs are retained in summaries.
    positive['discounted']=(positive[['retail_disc','coupon_disc','coupon_match_disc']]!=0).any(axis=1)
    promo=positive.groupby('discounted').agg(lines=('product_id','size'),sales=('sales_value','sum'),retail_disc=('retail_disc','sum'),coupon_disc=('coupon_disc','sum'),coupon_match_disc=('coupon_match_disc','sum')).reset_index();save(promo,out,'discount_descriptive')
    bycat=positive.groupby(['product_category','discounted']).agg(lines=('product_id','size'),sales=('sales_value','sum')).reset_index();save(bycat,out,'discount_category')
    campaign_result=campaign_analysis(config,out,end,j.date.min())
    result={'clustering':{'selected_k':best['k'],'silhouette':best['silhouette'],'seed_stability_ARI':float(stability),'meaning':'Unsupervised descriptive clusters; no business outcome accuracy.'},'high_value_threshold':float(m75),'frequent_threshold':float(f75),'top20_sales_share':float(cust.nlargest(int(np.ceil(len(cust)*.2)),'sales').sales.sum()/cust.sales.sum()),'A_product_count':int(products.ABC.eq('A').sum()),'product_count':len(products),'campaigns':campaign_result}
    write_json(out/'analytics_summary.json',result)
    return result

def campaign_analysis(config,out,end,start):
    src=ROOT/config['input_dir']
    assignments=read_table(src,'campaigns',False);desc=read_table(src,'campaign_descriptions',False);redemptions=read_table(src,'coupon_redemptions',False)
    if any(x is None for x in [assignments,desc,redemptions]): return {'available':False,'reason':'Missing campaign assignment/description/redemption table'}
    for frame in [assignments,desc,redemptions]:
        for col in ['household_id','campaign_id','coupon_upc']:
            if col in frame:frame[col]=frame[col].astype('string')
    if assignments.duplicated(['campaign_id','household_id']).any() or desc.campaign_id.duplicated().any():raise ValueError('Duplicate campaign dimension keys')
    redemptions['redemption_date']=pd.to_datetime(redemptions.redemption_date)
    redemptions=redemptions[redemptions.redemption_date<=end]
    recipients=assignments.groupby('campaign_id').household_id.nunique().rename('assigned_households')
    matched=redemptions.merge(assignments,on=['campaign_id','household_id'],how='inner',validate='many_to_one')
    redeemed=matched.groupby('campaign_id').household_id.nunique().rename('redeeming_assigned_households')
    campaigns=desc.merge(recipients,on='campaign_id',how='left').merge(redeemed,on='campaign_id',how='left')
    campaigns['redeeming_assigned_households']=campaigns.redeeming_assigned_households.fillna(0)
    campaigns['household_redemption_rate']=campaigns.redeeming_assigned_households/campaigns.assigned_households
    campaigns['window_fully_observed']=(pd.to_datetime(campaigns.start_date)>=start)&(pd.to_datetime(campaigns.end_date)<=end)
    save(campaigns.sort_values('household_redemption_rate',ascending=False),out,'campaign_redemption')
    return {'available':True,'redemption_rows':len(redemptions),'unassigned_redemption_rows':len(redemptions)-len(matched),'note':'Household-level redemption, not coupon impression conversion or incremental ROI. Type A individual coupon exposure is unavailable.'}

def association_model(j,config,out):
    end=pd.Timestamp(config['analysis_end']);split=end-pd.Timedelta(days=91);train_end=split-pd.Timedelta(days=28)
    pos=j[(j.quantity>0)&(j.sales_value>0)]
    train=pos[pos.date<=train_end];validation=pos[(pos.date>train_end)&(pos.date<=split)];test=pos[pos.date>split]
    counts=train.loc[train.product_category.ne('UNKNOWN'),['basket_id','product_category']].drop_duplicates().product_category.value_counts()
    categories=set(counts.head(30).index)
    def baskets(df):
        return df[df.product_category.isin(categories)].groupby('basket_id').product_category.agg(lambda v:sorted(set(v)))
    tr=baskets(train);te=baskets(test)
    def count(groups):
        one=Counter();two=Counter()
        for values in groups:
            one.update(values);two.update(combinations(values,2))
        return one,two
    one,two=count(tr);one_test,two_test=count(te)
    n=train.basket_id.nunique();nt=test.basket_id.nunique();rows=[]
    for (a,b),v in two.items():
        lift=v*n/(one[a]*one[b])
        if v<100 or lift<=1:continue
        for source,target in [(a,b),(b,a)]:
            vtest=two_test.get(tuple(sorted([a,b])),0)
            rows.append({'A':source,'B':target,'train_pair_baskets':v,'train_support':v/n,'train_confidence':v/one[source],'train_lift':lift,'test_pair_baskets':vtest,'test_confidence':vtest/one_test[source] if one_test[source] else np.nan,'test_lift':vtest*nt/(one_test[source]*one_test[target]) if one_test[source]*one_test[target] else np.nan,'rank_score':(v/one[source])*np.log(lift)})
    rules=pd.DataFrame(rows).sort_values('rank_score',ascending=False);save(rules,out,'association_rules')
    lookup={a:g.sort_values('rank_score',ascending=False).B.tolist() for a,g in rules.groupby('A')}
    popular=counts.head(30).index.tolist()
    def evaluate(groups):
        metrics={'association':[],'popularity':[]};coverage=set()
        for basket_id,values in groups.items():
            if len(values)<2:continue
            index=int(hashlib.sha256(str(basket_id).encode()).hexdigest()[:8],16)%len(values)
            seed=values[index];hidden=set(values)-{seed}
            rec=list(dict.fromkeys(lookup.get(seed,[])+popular));rec=[v for v in rec if v!=seed][:3]
            pop=[v for v in popular if v!=seed][:3];coverage.update(rec)
            for name,pred in [('association',rec),('popularity',pop)]:metrics[name].append([int(bool(hidden&set(pred))),len(hidden&set(pred))/len(hidden)])
        summary={name:{'hit_at_3':float(np.mean([v[0] for v in values])),'recall_at_3':float(np.mean([v[1] for v in values])),'evaluated_baskets':len(values)} for name,values in metrics.items()}
        return summary,len(coverage)/len(categories)
    val_result,_=evaluate(baskets(validation));winner='association' if val_result['association']['hit_at_3']>val_result['popularity']['hit_at_3'] else 'popularity'
    result,coverage=evaluate(te)
    result.update({'train_end':str(train_end.date()),'validation_start':str((train_end+pd.Timedelta(days=1)).date()),'validation_end':str(split.date()),'validation_metrics':val_result,'test_start':str((split+pd.Timedelta(days=1)).date()),'test_end':str(end.date()),'recommended_category_coverage':coverage,'evaluation':'One deterministically masked category as seed, other observed top-30 categories hidden. Eligible multi-category baskets only; same-basket completion, not future-purchase prediction.','winner_selected_on_validation':winner,'winner':winner})
    write_json(out/'association_metrics.json',result)
    import joblib
    joblib.dump({'lookup':lookup,'popular':popular,'categories':sorted(categories),'train_end':str(train_end.date()),'winner':winner},out/'models'/'basket_recommender.joblib')
    return result
