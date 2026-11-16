import unittest
import numpy as np
import pandas as pd
from .models import forecast_frame,customer_snapshot,classification_metrics
from .common import regression_metrics
from .recommend import recommend

def fixture():
    days=pd.date_range('2017-01-01',periods=365)
    rows=[]
    for i,date in enumerate(days):
        for category,amount in [('A',10+i),('B',20+i)]:
            rows.append({'date':date,'transaction_timestamp':date+pd.Timedelta(hours=12),'product_category':category,'sales_value':amount,'quantity':1,'household_id':'h1','basket_id':f'{i}-{category}','retail_disc':0,'coupon_disc':0,'coupon_match_disc':0})
    return pd.DataFrame(rows)

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.data=fixture();self.config={'analysis_end':'2017-12-31','forecast_categories':2}

    def test_direct_target_is_exact_next_seven_days(self):
        frame,_,_,_=forecast_frame(self.data,self.config)
        origin=pd.Timestamp('2017-09-01')
        row=frame[(frame.origin==origin)&(frame.series=='A')].iloc[0]
        expected=self.data[(self.data.date>origin)&(self.data.date<=origin+pd.Timedelta(days=7))&self.data.product_category.eq('A')].sales_value.sum()
        self.assertEqual(row.target,expected)

    def test_forecast_features_do_not_depend_on_future(self):
        a,features,_,_=forecast_frame(self.data,self.config)
        origin=pd.Timestamp('2017-09-01');changed=self.data.copy()
        changed.loc[changed.date>origin,'sales_value']*=1000
        b,features_b,_,_=forecast_frame(changed,self.config)
        self.assertEqual(features,features_b)
        pd.testing.assert_frame_equal(a.loc[a.origin==origin,features],b.loc[b.origin==origin,features])

    def test_forecast_vocabulary_is_frozen_at_scoring(self):
        changed=self.data.copy();changed.loc[changed.date>pd.Timestamp('2017-10-01'),'product_category']='NEW'
        frame,_,names,_=forecast_frame(changed,self.config,vocabulary=['A','B'])
        self.assertEqual(names,['A','B']);self.assertEqual(set(frame.series),{'A','B','OTHER'})

    def test_risk_features_do_not_depend_on_future(self):
        origin=pd.Timestamp('2017-09-01');a=customer_snapshot(self.data,origin)
        changed=self.data[self.data.date<=origin].copy();b=customer_snapshot(changed,origin)
        pd.testing.assert_frame_equal(a.drop(columns='no_purchase_next_28'),b.drop(columns='no_purchase_next_28'))
        self.assertFalse(bool(a.no_purchase_next_28.iloc[0]));self.assertTrue(bool(b.no_purchase_next_28.iloc[0]))

    def test_risk_label_includes_day28_excludes_day29(self):
        origin=pd.Timestamp('2017-09-01');history=self.data[self.data.date<=origin]
        day28=self.data[self.data.date==origin+pd.Timedelta(days=28)]
        day29=self.data[self.data.date==origin+pd.Timedelta(days=29)]
        self.assertFalse(bool(customer_snapshot(pd.concat([history,day28]),origin).no_purchase_next_28.iloc[0]))
        self.assertTrue(bool(customer_snapshot(pd.concat([history,day29]),origin).no_purchase_next_28.iloc[0]))

    def test_inactive_over90_days_not_scored(self):
        origin=pd.Timestamp('2017-12-31')
        stale=self.data[self.data.date<pd.Timestamp('2017-03-01')].copy();stale['household_id']='old'
        result=customer_snapshot(pd.concat([self.data,stale]),origin,labeled=False)
        self.assertNotIn('old',result.household_id.tolist())

    def test_wape_uses_total_weight_not_mean_percentages(self):
        result=regression_metrics([1,99],[2,90]);self.assertAlmostEqual(result['WAPE'],.1)

    def test_risk_top20_capacity_and_lift(self):
        result=classification_metrics([1,0,0,0,0],[.9,.8,.2,.1,0])
        self.assertEqual(result['precision_top20'],1);self.assertEqual(result['lift_top20'],5)

    def test_recommendation_respects_champion_and_never_recommends_seed(self):
        bundle={'lookup':{'A':['C','A','C']},'popular':['A','B','D'],'winner':'popularity'}
        self.assertEqual(recommend(bundle,'A'),['B','D'])
        bundle['winner']='association';self.assertEqual(recommend(bundle,'A'),['C','B','D'])

if __name__=='__main__':unittest.main()
