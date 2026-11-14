"""Release-level integrity: every entry, no cherry-picked omissions."""
import gzip,hashlib,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'web/public/data/global'
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def test_all_185_entries_and_5550_unique_sources_are_accounted_for():
 c=read(DATA/'catalog.json');sources=read(ROOT/'reports/global-source-manifest.json');inventory=read(ROOT/'reports/global-source-inventory.json')
 assert len(c['countries'])==185 and len(sources)==5550
 assert len({x['id'] for x in c['countries']})==185
 assert len({x['filename'] for x in sources})==5550
 assert {x['firms_name'] for x in c['countries']}==set(inventory['countries'])
 assert sum(c['status_counts'].values())==185
 assert c['protocol_sha256']==hashlib.sha256((ROOT/'reports/global-evaluation-protocol.json').read_bytes()).hexdigest()
 assert len(read(DATA/'coverage.geojson')['features'])==185
 assert len(read(ROOT/'reports/global-reconciliation.json'))==185

def test_every_country_package_reconciles_and_preserves_failed_models():
 c=read(DATA/'catalog.json')
 for entry in c['countries']:
  blob=(DATA/entry['package']).read_bytes();assert hashlib.sha256(blob).hexdigest()==entry['sha256']
  p=json.loads(gzip.decompress(blob));assert len(p['sources'])==30
  a=np.asarray(p['rows'],dtype=np.int64).reshape(-1,8)
  for total in p['totals']:
   z=a[(a[:,0]==total['year'])&(a[:,1]==total['month'])]
   assert z[:,4:].sum(axis=0).tolist()==[total[k] for k in ['raw_aqua','aqua','raw_noaa20','noaa20']]
  for y in range(2003,2027):assert (DATA/entry['id']/f'days-{y}.json.gz').exists()
  v=p['validation'];failed=v['status'] in ['mixed_or_poor_agreement','insufficient_support']
  assert (p['primary_policy']=='aqua_only')==failed
  assert all(f['factor'] is None or f['factor']>0 for f in p['factors'])
  if any(f['factor'] is None for f in p['factors']):assert v['wape'] is None and failed
  if v['wape'] is not None:
   expected=sum(abs(t['aqua']-t['adjusted']) for t in v['rows'])/sum(t['aqua'] for t in v['rows'])
   assert abs(expected-v['wape'])<1e-12
  if not failed:
   assert v['wape']<=.25 and abs(v['signed_bias'])<=.15 and v['category_agreement']>=.8
   assert v['wape']<v['unadjusted_wape']
   assert all(n<5 or recall>=.7 for n,recall in zip(v['category_support'],v['category_recall']))
  if v['status']=='agreement_checks_passed':assert v['reference_extreme_months']>=5
  if v['status']=='limited_event_evidence':assert v['reference_extreme_months']<5
