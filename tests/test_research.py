import base64,gzip,importlib,json,sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'pipeline'))
quality=importlib.import_module('13_quality_calendar');timing=importlib.import_module('14_time_comparison');decision=importlib.import_module('15_decision_case')

def test_partial_granule_uses_explicit_layer_dates():
 attrs={'Dates':'2020-09-03 2020-09-04','StartDate':'2020-08-28','EndDate':'2020-09-04'}
 assert quality.layer_dates(attrs,2)==['2020-09-03','2020-09-04']
 with pytest.raises(ValueError):quality.layer_dates(attrs,8)
 with pytest.raises(ValueError):quality.layer_dates({**attrs,'Dates':''},2)
 with pytest.raises(ValueError):quality.layer_dates({**attrs,'Dates':'2020-09-04 2020-09-03'},2)

def test_qa_bits_and_missing_land_class_are_retained():
 result=quality.qa_counts([0,1,2,3,4,5,6])
 assert result['land_water']==[2,2,2,1]
 assert result['representative_day_night']==[4,3]
 for invalid in [[7],[-1],[2.5],[]]:
  with pytest.raises(ValueError):quality.qa_counts(invalid)

def test_all_published_pixels_reconcile_with_daily_summaries():
 report=json.loads((ROOT/'reports/quality-calendar.json').read_text())
 pixels=json.loads(gzip.decompress((ROOT/'web/public/data/quality-pixels.json.gz').read_bytes()))
 by_date={d['date']:d for d in report['days']}
 assert len(by_date)==184 and len(pixels['days'])==report['available_days']==167
 assert report['missing_dates'][0]=='2020-08-17' and report['missing_dates'][-1]=='2020-09-02'
 assert len(report['missing_dates'])==17
 for day in pixels['days']:
  mask=np.frombuffer(base64.b64decode(day['mask']),dtype=np.uint8);qa=np.frombuffer(base64.b64decode(day['qa']),dtype=np.uint8);valid=mask!=255
  assert len(mask)==report['grid']['width']*report['grid']['height']
  assert np.array_equal(mask==255,qa==255)
  assert valid.sum()==14386
  summary=by_date[day['date']]
  assert np.bincount(mask[valid],minlength=10).tolist()==summary['counts']
  assert quality.qa_counts(qa[valid])==summary['qa']
 for day in report['missing_dates']:
  assert by_date[day]['counts'] is None and by_date[day]['qa'] is None
  assert by_date[day]['status']=='no_product'
 assert (ROOT/'reports/quality-calendar.json').read_bytes()==(ROOT/'web/public/data/quality-calendar.json').read_bytes()

def test_solar_time_wrap_and_invalid_input():
 assert timing.solar_minutes(['2330','0030'],[30,-30]).tolist()==[90,1350]
 for times in [['2400'],['1260'],['oops']]:
  with pytest.raises(ValueError):timing.solar_minutes(times,[110])

def test_support_gate_rejects_zero_or_too_few_retained_cells():
 assert not timing.support(0,0,79,718)
 assert not timing.support(0,474,79,718)
 assert not timing.support(19,100,30,100)
 assert not timing.support(40,344,79,718)
 assert timing.support(40,360,79,718)

def test_current_restricted_estimates_are_not_published():
 d=json.loads((ROOT/'reports/time-comparison.json').read_text())
 for key in ['midday','one_hour']:
  m=d['models'][key]
  assert not m['current']['support_gate_passed']
  assert m['current']['estimate'] is None and m['current']['relative_disagreement'] is None
  assert m['audit']['windows']==48
  assert all(2022<=row['year']<=2025 for row in m['audit_windows'])

def test_accumulation_marker_is_retrospective_and_nonzero():
 a=np.zeros(365);a[90]=10;a[300]=90
 assert decision.marker(a,.1)==91
 assert decision.marker(a,.2)==301
 assert decision.marker(np.zeros(365),.1) is None
 for invalid in [np.zeros(366),np.full(365,-1),np.full(365,np.nan)]:
  with pytest.raises(ValueError):decision.marker(invalid,.1)

def test_case_outage_and_candidates_remain_explicit():
 d=json.loads((ROOT/'reports/decision-case.json').read_text())
 assert d['external_user_validation']=={'status':'not_conducted','participants':0}
 assert next(c for c in d['cases'] if c['year']==2020)['coverage_warning']
 rows=d['candidates'];assert len(rows)==3
 for i,c in enumerate(rows):
  assert c['median']>=5 and min(c['aqua'],c['adjusted'])>c['p90']
  for other in rows[:i]:assert np.linalg.norm(np.array(c['centre'])-other['centre'])>=.5
 for sensor in ['aqua','snpp']:
  case=next(c for c in d['cases'] if c['year']==2019)
  assert all(m['days_from_reference_median']>0 for m in case['sensors'][sensor]['markers'].values())
