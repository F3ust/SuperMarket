"""Derive full-year commercial insights from the enriched transactions and embed them in bundle.json.

Run after build_data.py and before build_html.py: python build_insights.py
"""
from pathlib import Path
import json, gzip, base64
import numpy as np
import pandas as pd

PROJECT = Path(__file__).parent
ROOT = PROJECT.parent
RUN = Path(json.loads((ROOT / 'outputs/enterprise/latest.json').read_text(encoding='utf-8'))['path'])


def r(v, d=2):
    return None if v is None or not np.isfinite(v) else round(float(v), d)


def main():
    j = pd.read_parquet(RUN / 'transactions_enriched.parquet')
    j['month'] = j.date.dt.strftime('%Y-%m')
    disc = ['retail_disc', 'coupon_disc', 'coupon_match_disc']
    j['gross'] = j.sales_value + j[disc].sum(axis=1)
    j['disc'] = j[disc].sum(axis=1)
    j['promo_line'] = j.disc > 0
    j['private'] = j.brand == 'Private'
    out = {}

    tot = j[['gross', 'sales_value', 'retail_disc', 'coupon_disc', 'coupon_match_disc', 'disc']].sum()
    out['gross_to_net'] = {'gross': r(tot.gross), 'retail': r(tot.retail_disc), 'coupon': r(tot.coupon_disc),
                           'match': r(tot.coupon_match_disc), 'net': r(tot.sales_value), 'rate': r(tot.disc / tot.gross, 4),
                           'promo_line_share': r(j.promo_line.mean(), 4),
                           'private_share': r(j.loc[j.private, 'sales_value'].sum() / tot.sales_value, 4)}

    first = j[j.sales_value > 0].groupby('household_id').month.min()
    m = j.groupby('month').agg(net=('sales_value', 'sum'), gross=('gross', 'sum'), retail=('retail_disc', 'sum'),
                               coupon=('coupon_disc', 'sum'), match=('coupon_match_disc', 'sum'),
                               baskets=('basket_id', 'nunique'), households=('household_id', 'nunique'),
                               units=('quantity', 'sum'), lines=('sales_value', 'size'))
    m['private'] = j[j.private].groupby('month').sales_value.sum() / m.net
    m['rate'] = (m.gross - m.net) / m.gross
    m['aov'] = m.net / m.baskets
    m['lines_per_basket'] = m.lines / m.baskets
    act = j[j.sales_value > 0].groupby('month').household_id.agg(lambda s: set(s))
    new_hh, rep_hh = {}, {}
    for mo, hs in act.items():
        n = int((first.reindex(list(hs)) == mo).sum())
        new_hh[mo], rep_hh[mo] = n, len(hs) - n
    m['new_hh'] = pd.Series(new_hh)
    m['repeat_hh'] = pd.Series(rep_hh)
    out['monthly'] = [{'month': k, **{c: r(v, 4 if c in ('rate', 'private') else 2) for c, v in row.items()}}
                      for k, row in m.iterrows()]

    d = j.groupby('department').agg(net=('sales_value', 'sum'), gross=('gross', 'sum'), lines=('sales_value', 'size'),
                                    baskets=('basket_id', 'nunique'))
    d['rate'] = (d.gross - d.net) / d.gross
    d['share'] = d.net / d.net.sum()
    q1 = j[j.date < '2017-04-01'].groupby('department').sales_value.sum()
    q4 = j[j.date >= '2017-10-01'].groupby('department').sales_value.sum()
    d['q1'], d['q4'] = q1, q4
    d['growth'] = (d.q4 / d.q1 - 1).replace([np.inf, -np.inf], np.nan)
    d['private'] = j[j.private].groupby('department').sales_value.sum() / d.net
    d = d.sort_values('net', ascending=False)
    out['departments'] = [{'name': k, **{c: r(v, 4 if c in ('rate', 'share', 'growth', 'private') else 2) for c, v in row.items()}}
                          for k, row in d.head(14).iterrows()]
    dm = j[j.department.isin(d.head(8).index)].pivot_table(index='department', columns='month', values='sales_value', aggfunc='sum')
    dm = dm.reindex(d.head(8).index)
    out['dept_month'] = {'depts': list(dm.index), 'months': list(dm.columns), 'z': [[r(x) for x in row] for row in dm.values]}

    wk = j.assign(wd=j.date.dt.dayofweek, hr=j.transaction_timestamp.dt.hour).pivot_table(
        index='wd', columns='hr', values='sales_value', aggfunc='sum').reindex(index=range(7), columns=range(24)).fillna(0)
    out['weekday_hour'] = [[r(x, 0) for x in row] for row in wk.values]

    pos = j[j.sales_value > 0]
    hh = pos.groupby('household_id').agg(net=('sales_value', 'sum'), baskets=('basket_id', 'nunique'),
                                         stores=('store_id', 'nunique'), disc=('disc', 'sum'), gross=('gross', 'sum')).sort_values('net', ascending=False)
    cum = hh.net.cumsum() / hh.net.sum()
    n = len(hh)
    out['customers'] = {
        'households': n, 'mean': r(hh.net.mean()), 'median': r(hh.net.median()),
        'top1': r(cum.iloc[int(n * .01) - 1], 4), 'top5': r(cum.iloc[int(n * .05) - 1], 4),
        'top10': r(cum.iloc[int(n * .10) - 1], 4), 'top20': r(cum.iloc[int(n * .20) - 1], 4),
        'bottom50': r(1 - cum.iloc[int(n * .5) - 1], 4),
        'lorenz': [[i / 20, r(cum.iloc[max(0, int(n * i / 20) - 1)], 4)] for i in range(1, 21)],
        'multi_store': r((hh.stores > 1).mean(), 4)}
    bins = [0, 1, 4, 9, 19, 39, 10 ** 6]
    labels = ['1', '2–4', '5–9', '10–19', '20–39', '40+']
    hh['band'] = pd.cut(hh.baskets, bins=bins, labels=labels)
    g = hh.groupby('band', observed=False).agg(households=('net', 'size'), net=('net', 'sum'))
    out['frequency'] = [{'band': k, 'households': int(v.households), 'share': r(v.net / hh.net.sum(), 4)} for k, v in g.iterrows()]
    hh['disc_rate'] = hh.disc / hh.gross
    hh['dband'] = pd.cut(hh.disc_rate, bins=[-1, .05, .10, .15, .20, .30, 1], labels=['<5%', '5–10%', '10–15%', '15–20%', '20–30%', '30%+'])
    g = hh.groupby('dband', observed=False).agg(households=('net', 'size'), net=('net', 'sum'), baskets=('baskets', 'sum'))
    out['discount_bands'] = [{'band': k, 'households': int(v.households), 'share': r(v.net / hh.net.sum(), 4),
                              'spend': r(v.net / v.households if v.households else 0)} for k, v in g.iterrows()]

    bk = pos.groupby('basket_id').agg(net=('sales_value', 'sum'), lines=('sales_value', 'size'), units=('quantity', 'sum'),
                                      disc=('disc', 'sum'), coupon=('coupon_disc', 'sum'), match=('coupon_match_disc', 'sum'))
    bk['band'] = pd.cut(bk.lines, bins=[0, 1, 5, 10, 20, 40, 10 ** 6], labels=['1', '2–5', '6–10', '11–20', '21–40', '41+'])
    g = bk.groupby('band', observed=False).agg(baskets=('net', 'size'), net=('net', 'sum'))
    out['basket_bands'] = [{'band': k, 'baskets': int(v.baskets), 'share': r(v.net / bk.net.sum(), 4), 'aov': r(v.net / v.baskets if v.baskets else 0)} for k, v in g.iterrows()]
    cp = (bk.coupon + bk.match) > 0
    out['basket'] = {'count': int(len(bk)), 'aov': r(bk.net.mean()), 'median': r(bk.net.median()), 'lines': r(bk.lines.mean()),
                     'units': r(bk.units.mean()), 'coupon_share': r(cp.mean(), 4), 'coupon_aov': r(bk.net[cp].mean()),
                     'plain_aov': r(bk.net[~cp].mean()), 'coupon_lines': r(bk.lines[cp].mean()), 'plain_lines': r(bk.lines[~cp].mean())}

    st = pos.groupby('store_id').agg(net=('sales_value', 'sum'), households=('household_id', 'nunique'), baskets=('basket_id', 'nunique')).sort_values('net', ascending=False)
    sc = st.net.cumsum() / st.net.sum()
    st['per_hh'] = st.net / st.households
    big = st[st.households >= 20]
    out['stores'] = {'count': int(len(st)), 'top10pct': r(sc.iloc[int(len(st) * .1) - 1], 4), 'top20pct': r(sc.iloc[int(len(st) * .2) - 1], 4),
                     'top5': r(sc.iloc[4], 4), 'active_hh20': int(len(big)), 'per_hh_median': r(big.per_hh.median()),
                     'per_hh_p10': r(big.per_hh.quantile(.1)), 'per_hh_p90': r(big.per_hh.quantile(.9)),
                     'weak': [{'store': k, 'net': r(v.net), 'households': int(v.households), 'per_hh': r(v.per_hh)}
                              for k, v in big.sort_values('per_hh').head(5).iterrows()],
                     'strong': [{'store': k, 'net': r(v.net), 'households': int(v.households), 'per_hh': r(v.per_hh)}
                                for k, v in big.sort_values('per_hh', ascending=False).head(5).iterrows()]}

    day = j.groupby('date').sales_value.sum()
    day = day[day.index != '2017-12-25']
    wkly = j.groupby('week').sales_value.sum()
    out['weekly'] = [[int(k), r(v, 0)] for k, v in wkly.items() if 1 <= k <= 52]
    out['days'] = {'top': [[d_.strftime('%Y-%m-%d'), r(v, 0)] for d_, v in day.nlargest(5).items()],
                   'low': [[d_.strftime('%Y-%m-%d'), r(v, 0)] for d_, v in day.nsmallest(5).items()],
                   'mean': r(day.mean(), 0)}

    priv = j.groupby(['private']).agg(net=('sales_value', 'sum'), gross=('gross', 'sum'))
    out['brand'] = {'private_net': r(priv.loc[True, 'net']), 'national_net': r(priv.loc[False, 'net']),
                    'private_rate': r(1 - priv.loc[True, 'net'] / priv.loc[True, 'gross'], 4),
                    'national_rate': r(1 - priv.loc[False, 'net'] / priv.loc[False, 'gross'], 4)}

    q = json.loads((RUN / 'quality.json').read_text(encoding='utf-8'))
    out['quality'] = {'households': q['households'], 'stores': q['stores'], 'baskets': q['basket_count'], 'out_of_scope': q['out_of_scope_rows'],
                      'unmatched': q['unmatched_product_rows'], 'unmatched_rate': q['unmatched_product_rate'], 'excluded': q['model_excluded_rows']}

    bundle_path = PROJECT / 'bundle.json'
    bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
    meta = json.loads(gzip.decompress(base64.b64decode(bundle['metadataGzip'])).decode('utf-8'))
    meta['insights'] = out
    raw = json.dumps(meta, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    bundle['metadataGzip'] = base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0)).decode()
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')
    (PROJECT / 'insights.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'gross_to_net': out['gross_to_net'], 'customers': {k: v for k, v in out['customers'].items() if k != 'lorenz'},
                      'basket': out['basket'], 'stores': {k: v for k, v in out['stores'].items() if k not in ('weak', 'strong')},
                      'brand': out['brand'], 'days': out['days']}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
