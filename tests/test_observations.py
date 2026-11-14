import importlib
import json
import sys
from pathlib import Path
import numpy as np
import pytest
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
m=importlib.import_module('12_observation_context')

def test_mask_partition_preserves_missing_cloud_and_low_confidence():
    counts=m.partition([0,0,4,5,7,8,9])
    assert sum(counts)==7
    assert counts[0]==2 and counts[4]==1 and counts[7]==1
    with pytest.raises(ValueError):m.partition([10])
    with pytest.raises(ValueError):m.partition([1.5])

def test_native_grid_selection_matches_independent_proj_transform():
    structure='UpperLeftPointMtrs=(12231455.716333,0.000000) LowerRightMtrs=(13343406.236000,-1111950.519667)'
    mask=m.grid_mask(structure,(1200,1200),[113,-3,114,-2])
    yy,xx=np.indices((1200,1200))
    x=12231455.716333+(xx+.5)*(13343406.236000-12231455.716333)/1200
    y=(yy+.5)*(-1111950.519667)/1200
    t=Transformer.from_crs('+proj=sinu +R=6371007.181 +units=m +no_defs','EPSG:4326',always_xy=True)
    lon,lat=t.transform(x,y)
    expected=(lon>=113)&(lon<114)&(lat>=-3)&(lat<-2)
    assert np.array_equal(mask,expected)
    assert int(mask.sum())==14386

def test_published_days_form_complete_fixed_grid_partition():
    d=json.loads((ROOT/'reports/observation-context.json').read_text())
    assert len(d['days'])==16
    assert len({day['date'] for day in d['days']})==16
    assert {day['total_cells'] for day in d['days']}=={14386}
    for day in d['days']:
        assert len(day['counts'])==10 and sum(day['counts'])==day['total_cells']
    assert len(d['sources'])==3
    assert all(len(s['sha256'])==64 for s in d['sources'])
    assert (ROOT/'reports/observation-context.json').read_bytes()==(ROOT/'web/public/data/observation-context.json').read_bytes()
