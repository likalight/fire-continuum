import importlib,json,sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'pipeline'));m=importlib.import_module('16_decision_benchmark')

def test_categories_use_strict_thresholds():
 assert [m.category(x,10,20) for x in [0,10,11,20,21]]==[0,0,1,1,2]
 assert m.category(0,0,0)==0
 for args in [(1,20,10),(-1,10,20),(np.nan,10,20)]:
  with pytest.raises(ValueError):m.category(*args)

def test_peak_handles_wrap_zero_ties_and_validation():
 a=[8,0,0,0,0,0,0,0,0,0,7,9]
 assert m.peak(a)==11 and m.circular_error(12,1)==1
 assert m.peak([1]*12)==1 and m.peak([0]*12) is None
 with pytest.raises(ValueError):m.peak([1]*11)

def test_confusion_and_balanced_accuracy_do_not_hide_rare_class():
 rows=[{'reference_class':0,'classes':{'released':0},'aqua':1,'values':{'released':1}} for _ in range(9)]
 rows.append({'reference_class':2,'classes':{'released':0},'aqua':10,'values':{'released':1}})
 s=m.score(rows,'released');assert s['agreement']==.9 and s['balanced_accuracy']==.5 and s['missed_above_p90']==1
 assert m.score([],'released')['agreement'] is None

def test_benchmark_split_gate_and_failure_counts_are_published():
 d=json.loads((ROOT/'reports/decision-benchmark.json').read_text())
 assert len(d['records'])==710 and len(d['annual_windows'])==55
 for r in d['records']:
  assert r['year']>= (2018 if r['sensor']=='snpp' else 2022)
  assert not (r['year']==2020 and r['month'] in [8,9])
  assert r['supported']==(r['median']>=5 and r['aqua']>=20 and r['viirs']>=20)
 for sensor,result in d['results'].items():
  rows=[r for r in d['records'] if r['sensor']==sensor]
  assert result['withheld']+result['retained']==len(rows)
  for name,metrics in result['methods'].items():assert metrics['all']==m.score(rows,name)
 assert d['results']['noaa20']['methods']['released']['all']['missed_above_p90']==3
 assert d['results']['noaa20']['methods']['single_factor']['all']['missed_above_p90']==1
 assert (ROOT/'reports/decision-benchmark.json').read_bytes()==(ROOT/'web/public/data/decision-benchmark.json').read_bytes()
