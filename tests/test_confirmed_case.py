"""Guard geographic/time provenance and the narrow curated-case claim."""
import hashlib
import importlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'pipeline'))
m = importlib.import_module('19_confirmed_case')
OUT = ROOT/'web/public/data'


def test_utc_time_offsets_keep_leading_zeros_and_date_boundaries():
    assert m.parse_time('2019-09-15', '006').isoformat() == '2019-09-15T00:06:00+00:00'
    assert m.minutes_after('2019-09-15', '0622') == pytest.approx(227.15580968333333)
    assert m.minutes_after('2019-09-16', '0030') > 1200
    with pytest.raises(ValueError):m.parse_time('2019-09-15', '2460')


def test_confidence_and_half_open_date_spatial_filters_are_not_relaxed():
    frame = pd.DataFrame({'longitude':[113.85,113.95,113.9,113.9,113.9,113.9],
                          'latitude':[-3.1,-3.05,-3.0,-3.05,-3.05,-3.05],
                          'acq_date':['2019-09-15']*5+['2019-09-16'],
                          'confidence':['30','90','90','29','unknown','90']})
    assert m.filter_points(frame,'modis').index.tolist() == [0]
    frame.confidence = ['n','h','h','l','unknown','n']
    assert m.filter_points(frame,'viirs-snpp').index.tolist() == [0]


def test_pixel_aligned_crop_preserves_north_up_geolocation():
    image = np.arange(100).reshape(1,10,10)
    cropped = m.crop_bounds(image,[0,0,1,1],[.2,.3,.6,.8])
    assert cropped.shape == (1,5,4)
    assert np.array_equal(cropped,image[:,2:7,2:6])
    with pytest.raises(ValueError):m.crop_bounds(image,[0,0,1,1],[.21,.3,.6,.8])
    with pytest.raises(ValueError):m.crop_bounds(image,[0,0,1,1],[-.1,.3,.6,.8])


def test_published_sensor_counts_and_timing_are_recomputed_from_exact_points():
    case = json.loads((OUT/'confirmed-case.json').read_text(encoding='utf-8'))
    geo = json.loads((OUT/case['points']['geojson']).read_text(encoding='utf-8'))
    features = geo['features']
    counts = {key:sum(f['properties']['platform']==key for f in features) for key in case['counts']}
    assert counts == case['counts'] == {'aqua':2,'snpp':27,'terra':4,'noaa20':51}
    w,s,e,n = case['bounds']
    for f in features:
        x,y = f['geometry']['coordinates']; p = f['properties']
        assert w <= x < e and s <= y < n
        assert p['datetime'][:10] == case['date']
        stamp = p['datetime'][11:16].replace(':','')
        assert m.minutes_after(case['date'],stamp) == pytest.approx(p['minutes_after_landsat'])
    assert case['timing_test']['matching_observation_count'] == sum(abs(f['properties']['minutes_after_landsat'])<=60 for f in features) == 0
    assert case['timing_test']['predefined_window_minutes'] == 60
    for key,value in case['nearest_time_offsets_minutes'].items():
        assert value == min(abs(f['properties']['minutes_after_landsat']) for f in features if f['properties']['platform']==key)
    overlay = [f for f in features if f['properties']['platform']==case['overlay']['platform'] and f['properties']['datetime']==case['overlay']['datetime']]
    assert len(overlay) == case['overlay']['count'] == 16
    assert case['overlay']['minutes_after_landsat'] > 227


def test_render_assets_and_downloadable_provenance_are_pinned_and_unsigned():
    case = json.loads((OUT/'confirmed-case.json').read_text(encoding='utf-8'))
    assert (OUT/'confirmed-case.json').read_bytes() == (ROOT/'reports/confirmed-case.json').read_bytes()
    for name,expected in case['provenance']['asset_sha256'].items():
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest() == expected
    for name in ['confirmed-case-protocol.json','confirmed-case-search-log.json']:
        assert (OUT/name).read_bytes() == (ROOT/'reports'/name).read_bytes()
    assert hashlib.sha256((OUT/'confirmed-case-protocol.json').read_bytes()).hexdigest() == case['provenance']['protocol_sha256']
    for href in case['provenance']['band_assets'].values():
        assert urlparse(href).scheme == 'https' and not urlparse(href).query
    manifest = {r['filename']:r for r in json.loads((ROOT/'reports/source_manifest.json').read_text(encoding='utf-8'))}
    for source in case['provenance']['firms_archives']:
        assert source['sha256'] == manifest[source['file']]['sha256']
        assert source['source_url'] == manifest[source['file']]['url']


def test_curated_case_cannot_replace_or_silently_upgrade_original_audit():
    case = json.loads((OUT/'confirmed-case.json').read_text(encoding='utf-8'))
    audit = json.loads((OUT/'imagery-audit.json').read_text(encoding='utf-8'))
    search = json.loads((OUT/'confirmed-case-search-log.json').read_text(encoding='utf-8'))
    assert audit['outcome_counts'] == {'corroborated':0,'contradicted':0,'inconclusive':6}
    assert case['visual_review']['original_audit_changed'] is False
    assert case['status'] == 'curated_event_corroboration'
    assert 'outcome-informed' in case['selection_note']
    assert len([s for s in search['searches'] if 'bounds' in s]) == 3
    assert sum(s.get('selected',False) for s in search['searches']) == 1
    assert any('harmonization accuracy' in limit for limit in case['limits'])
