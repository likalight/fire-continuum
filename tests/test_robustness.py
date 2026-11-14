import importlib,sys,json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
module=importlib.import_module('05_robust_validation')

def test_range_quantile_uses_finite_sample_rank():
    assert module.finite_quantile(range(1,11))==10
    assert module.finite_quantile([1,2,3]) is None

def test_excluded_region_cannot_influence_training_factor():
    records=[{'lon':100.,'lat':0.,'sector':s,'quarter':q,'aqua':10.,'snpp':50.} for s in range(3) for q in range(4)]
    records += [{'lon':112.,'lat':0.,'sector':s,'quarter':q,'aqua':99999.,'snpp':1.} for s in range(3) for q in range(4)]
    d=pd.DataFrame(records);outside=d[~module.select(d,[108,-5,120,4.5])]
    factors,fallback=module.fit(outside,'snpp')
    assert fallback==0 and all(abs(v-.2)<1e-12 for v in factors.values())

def test_original_sensitivity_reproduces_original_pipeline():
    a=json.loads((ROOT/'reports/sensitivity.json').read_text())
    original=next(v for v in a['configurations'] if v['config']=='original_1000m')
    expected=json.loads((ROOT/'reports/validation.json').read_text())
    for sensor in ['snpp','noaa20']:
        assert abs(original['sensors'][sensor]['wape']-expected[sensor]['national_after']['wape'])<1e-12

def test_range_evaluation_is_after_calibration_and_case_not_fit():
    r=json.loads((ROOT/'reports/robustness.json').read_text())
    for v in r['sensors'].values():
        z=v['empirical_range'];assert z['evaluation_years'][0]>z['calibration_years'][1]
        assert z['evaluation_months']==12*(z['evaluation_years'][1]-z['evaluation_years'][0]+1)
    assert all(x['year']>r['case']['training_years'][1] for x in r['case']['samples'])

def test_sensitivity_preserves_elevated_claim_but_not_extreme():
    configs=json.loads((ROOT/'reports/sensitivity.json').read_text())['configurations']
    assert len(configs)==6
    assert all(v['case'][0]['adjusted']>v['case'][0]['median'] and v['case'][0]['aqua']>v['case'][0]['median'] for v in configs)
    assert sum(v['case'][0]['adjusted_above_p90'] for v in configs)==1
