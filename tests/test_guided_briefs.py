import gzip,hashlib,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'web/public/data'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def test_all_185_briefings_reconcile_with_original_packages():
 m=read(D/'briefs/manifest.json');assert len(m['countries'])==185
 for c in m['countries']:
  blob=(D/f'briefs/{c["id"]}.json.gz').read_bytes();assert hashlib.sha256(blob).hexdigest()==c['sha256'];b=json.loads(gzip.decompress(blob))
  source=(D/'global'/b['source_package']).read_bytes();assert hashlib.sha256(source).hexdigest()==b['source_package_sha256'];p=json.loads(gzip.decompress(source))
  assert b['validation']==p['validation'] and b['primary_policy']==p['primary_policy']
  assert len(b['monthly'])==276 and len(b['recent'])==24 and len(b['daily_sources'])==24
  for a,t in zip(b['monthly'],p['totals']):assert a['aqua']==t['aqua'] and (a['noaa20']==t['noaa20'] if a['year']>=2019 else a['noaa20'] is None)
  latest=b['recent'][-1];assert latest['aqua']==sum(x[6] for x in p['recent']['rows']) and latest['noaa20']==sum(x[8] for x in p['recent']['rows'])
def test_new_october_evidence_retains_both_countries_and_daily_errors():
 report=read(D/'october-transfer.json');assert {c['id'] for c in report['countries']}=={'mexico','australia'}
 assert report['protocol_sha256']==hashlib.sha256((ROOT/'reports/new-observations-october-transfer-protocol.json').read_bytes()).hexdigest()
 for c in report['countries']:
  assert len(c['days'])==31 and len(c['sources'])==62
  assert c['aqua']==sum(x['aqua_cell_days'] for x in c['days'])
  for key,column in [('original_quarter','quarter_prediction'),('preselected','selected_prediction')]:
   model=c['models'][key];assert model['prediction']==pytest.approx(sum(x[column] for x in c['days']))
   assert model['daily_wape']==pytest.approx(sum(abs(x[column]-x['aqua_cell_days']) for x in c['days'])/c['aqua'])
  assert all(x['observation_coverage']=='unknown' for x in c['days'])

def test_full_masks_preserve_product_specific_classes_and_failed_timing_rule():
 report=read(D/'matched-mask-audit.json')
 assert report['time_separation_minutes']>report['declared_maximum_time_separation_minutes']
 assert report['eligible_for_matched_observation_normalization'] is False
 for p in report['products']:
  assert sum(p['class_counts'])==p['native_pixels_inside_bounds']
  blob=(D/p['native_pixel_archive']).read_bytes();assert hashlib.sha256(blob).hexdigest()==p['native_pixel_archive_sha256']
  assert p['class_counts'][4]==p['cloud_pixels'] and p['class_counts'][5]==p['clear_nonfire_land_pixels']
  if p['sensor']=='noaa20':assert p['class_counts'][2]==p['sun_glint_pixels']==264467
  else:assert p['sun_glint_pixels']==0
