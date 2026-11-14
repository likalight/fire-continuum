"""Leakage, missingness and complete reporting in the retrospective study."""
import gzip, hashlib, json, sys
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
from correction_models import fit, predict, monthly, assess, select

def read(p):return json.loads(p.read_text(encoding='utf-8'))
P=read(ROOT/'reports/correction-study-protocol.json')
O=read(ROOT/'reports/global-evaluation-protocol.json')

def fixture():
 # Two spatial populations with opposing sensor response; all quarters supported.
 return np.array([[y,m,x,0,a,a,n,n] for y in range(2003,2026) for m in range(1,13)
                  for x,a,n in [(0,20+m,40),(1,60-m,20)]],float)

@pytest.mark.parametrize('kind',P['candidates_in_tie_order'])
def test_future_aqua_cannot_change_fit_development_score_or_predictions(kind):
 rows=fixture();changed=rows.copy();changed[changed[:,0]>=2022,4:6]*=1000
 models=[fit(r,kind,2019,2021,P,O) for r in [rows,changed]]
 assert models[0]['weights']==models[1]['weights']
 if kind=='spatial_shrink':np.testing.assert_array_equal(models[0]['spatial_factors'],models[1]['spatial_factors'])
 assert predict(rows,models[0])==predict(changed,models[1])
 dev=[]
 for r in [rows,changed]:
  m=fit(r,kind,2019,2020,P,O)
  v=assess(monthly(r),predict(r,m),2021,2021,m,O)
  dev.append(v['wape']+1-v['category_agreement'])
 assert dev[0]==dev[1]

def test_spatial_unseen_cell_uses_national_prior_without_contemporary_aqua():
 rows=fixture();m=fit(rows,'spatial_shrink',2019,2021,P,O)
 future=np.array([[2022,1,100,0,9999,9999,10,10]],float)
 assert predict(future,m)[228]==pytest.approx(10*m['weights'][0])

@pytest.mark.parametrize('kind',P['candidates_in_tie_order'])
def test_pooled_candidates_cannot_turn_missing_quarter_into_zero_or_supported(kind):
 rows=fixture();rows[(rows[:,0]>=2019)&(rows[:,0]<=2021)&(rows[:,1]<=3),6:8]=0
 m=fit(rows,kind,2019,2021,P,O)
 assert m['weights'][:3]==[None]*3
 assert predict(rows,m)[228:231]==[None]*3

def test_selection_requires_margin_complete_support_and_declared_tie_order():
 scores={k:1.0 for k in P['candidates_in_tie_order']}
 scores['month_shrink']=.91
 assert select(scores,P)=='quarter_ratio'
 scores['month_shrink']=scores['spatial_shrink']=.8
 assert select(scores,P)=='month_shrink'
 scores['annual_ratio']=None
 assert select(scores,P)=='quarter_ratio'

def test_report_has_every_trial_preserves_baseline_and_uses_only_development_selection():
 r=read(ROOT/'reports/correction-study.json');catalog=read(ROOT/'web/public/data/global/catalog.json')
 assert r['protocol_sha256']==hashlib.sha256((ROOT/'reports/correction-study-protocol.json').read_bytes()).hexdigest()
 assert len(r['countries'])==185
 assert json.loads(gzip.decompress((ROOT/'web/public/data/correction-study.json.gz').read_bytes()))==r
 entries={c['id']:c for c in catalog['countries']}
 for c in r['countries']:
  assert c['source_package_sha256']==entries[c['id']]['sha256']
  assert set(c['trials'])==set(P['candidates_in_tie_order'])
  assert c['selected_model']==select({k:v['score'] for k,v in c['development'].items()},P)
  old=c['trials']['quarter_ratio'];baseline=entries[c['id']]['validation']
  assert old['status']==baseline['status']
  assert old['wape']==pytest.approx(baseline['wape']) if baseline['wape'] is not None else old['wape'] is None
  for v in c['trials'].values():
   assert len(v['rows'])==48 and {x['year'] for x in v['rows']}=={2022,2023,2024,2025}
   if v['wape'] is not None:
    assert v['wape']==pytest.approx(sum(abs(x['aqua']-x['prediction']) for x in v['rows'])/sum(x['aqua'] for x in v['rows']))
   if v['status']=='agreement_checks_passed':
    assert v['reference_extreme_months']>=5 and not v['reasons']
 assert r['summary']['quarter_ratio']['status_counts']==catalog['status_counts']
 assert all(sum(v['status_counts'].values())==185 for v in r['summary'].values())
