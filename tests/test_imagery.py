import hashlib,importlib,json,sys
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
from shapely.geometry import box,mapping
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'pipeline'));m=importlib.import_module('18_imagery_audit')

def test_qa_masks_reject_cloud_saturation_fill_and_reflectance_range():
 a=np.full((5,1,10),10000,dtype=np.uint16);a[3:]=0
 for i in range(6):a[3,0,i]=1<<i
 a[4,0,6]=1;a[0,0,7]=0;a[0,0,8]=50000
 refl,valid=m.valid_pixels(a)
 assert valid.tolist()==[[False]*9+[True]]
 assert np.isclose(refl[0,0,9],.075)

def test_scene_selection_is_fixed_by_footprint_cloud_then_date():
 def scene(id,date,cloud,bounds=[112,-4,114,-2]):return {'id':id,'geometry':mapping(box(*bounds)),'properties':{'platform':'landsat-8','datetime':date+'T00:00:00Z','eo:cloud_cover':cloud}}
 items=[scene('cloudy','2019-09-15',80),scene('clear','2019-09-07',10),scene('nearer','2019-09-14',10),scene('partial','2019-09-15',0,[112,-4,112.5,-3.5]),scene('before','2019-08-14',20)]
 result=m.select_scenes(items,[112.75,-3.5,113,-3.25])
 assert result['09']['id']=='nearer' and result['08']['id']=='before'

def test_all_six_outcomes_images_dates_and_unsigned_sources_are_retained():
 d=json.loads((ROOT/'reports/imagery-audit.json').read_text())
 assert len(d['cells'])==6 and sum(c['role']=='candidate' for c in d['cells'])==3
 assert d['outcome_counts']=={'corroborated':0,'contradicted':0,'inconclusive':6}
 for c in d['cells']:
  assert c['outcome']=='inconclusive' and c['reason']
  assert c['qa_gate_passed']==(c['paired_valid_fraction']>=.2)
  assert c['paired_valid_pixels']/c['total_grid_pixels']==c['paired_valid_fraction']
  assert hashlib.sha256((ROOT/'web/public/data'/c['preview']).read_bytes()).hexdigest()==c['preview_sha256']
  assert [s['date'][5:7] for s in c['scenes']]==['08','09']
  assert all(s['platform']=='landsat-8' for s in c['scenes'])
  for s in c['scenes']:
   assert len(s['subset_array_sha256'])==64
   for url in s['assets'].values():assert urlparse(url).scheme=='https' and not urlparse(url).query
  if c['role']=='comparison':assert c['aqua']<=c['median'] and c['adjusted']<=c['median']
 assert (ROOT/'reports/imagery-audit.json').read_bytes()==(ROOT/'web/public/data/imagery-audit.json').read_bytes()
