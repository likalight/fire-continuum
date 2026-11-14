import importlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'pipeline'))
m=importlib.import_module('10_correction_trials')

def test_method_is_selected_on_development_not_current_or_audit():
 d=json.loads((ROOT/'reports/correction-trials.json').read_text(encoding='utf-8'))
 assert d['gate']['selected']==min(d['development']['results'],key=lambda k:d['development']['results'][k]['macro_wape'])
 assert d['development']['fit'][1]<d['development']['selection'][0]
 assert d['audit']['fit'][1]<d['audit']['evaluation'][0]
 now=d['current']['kalimantan']['models'];assert now[d['gate']['selected']]['relative_disagreement']>now['original']['relative_disagreement']

def test_future_values_cannot_change_fitted_coefficients():
 records=[{'region':r,'year':y,'month':month,'quarter':(month-1)//3,'aqua':10.,'noaa20':50.} for r in m.REGIONS for y in [2019,2020,2021,2024] for month in range(1,13)]
 d=pd.DataFrame(records);s=pd.DataFrame([{'sector':sec,'year':y,'quarter':q,'aqua':10.,'noaa20':50.} for sec in range(3) for y in [2019,2020,2021,2024] for q in range(4)])
 before=m.fit_models(d,d,s,[],2019,2021);d.loc[d.year==2024,'aqua']=999999;s.loc[s.year==2024,'aqua']=999999
 after=m.fit_models(d,d,s,[],2019,2021);assert before==after

def test_promotion_guardrail_rejects_a_harmed_region():
 def scores(value):return {r:{'all':{'wape':value},'same_dates':{'wape':value}} for r in m.REGIONS}
 base=scores(.4);good=scores(.3);assert m.promotion(good,base)['promote']
 good['java']['all']['wape']=.6;assert not m.promotion(good,base)['promote']

def test_daynight_counts_preserve_cell_day_totals():
 d=pd.read_csv(ROOT/'reports/daynight_counts.csv').groupby(['region','year','month','sensor']).active.sum().sort_index()
 a=pd.read_csv(ROOT/'reports/recent_window_counts.csv');a=a[a.year.ge(2019)].set_index(['region','year','month','sensor']).active.sort_index()
 pd.testing.assert_series_equal(d,a,check_dtype=False)

def test_refreshed_window_has_no_point_revisions_and_current_aqua_is_not_shifted():
 d=json.loads((ROOT/'reports/daynight-audit.json').read_text(encoding='utf-8'))
 assert all(s['added_points']==0 and s['removed_points']==0 for s in d['sources'])
 assert all(v['regions']['kalimantan']['current']['aqua']==79 for v in d['models'].values())
 # Verified observation timing is a diagnostic, not used to scale reference counts.
 times={x['sensor']:x['median_local_solar_hour_of_detected_points'] for x in d['kalimantan_detected_passage_times'] if x['year']==2026 and x['daynight']=='D'}
 assert times['aqua']-times['noaa20']>2

def test_zero_support_does_not_invent_ratio():
 import pytest
 with pytest.raises(ValueError):m.ratio(pd.DataFrame({'aqua':[5],'noaa20':[0]}))
