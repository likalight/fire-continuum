import importlib,json,sys
from pathlib import Path
import numpy as np
import pytest
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
m=importlib.import_module('17_transfer_cases')

def test_category_thresholds_keep_boundary_values_on_lower_side():
    assert m.category(10,10,20)=='At or below typical'
    assert m.category(20,10,20)=='Above typical'
    assert m.category(20.01,10,20)=='Unusually high'
    assert m.category(20,0,20)=='Insufficient baseline'

def test_retrospective_gate_keeps_sparse_or_empty_samples_out():
    assert m.support(20,20,5)
    assert not m.support(0,100,10)
    assert not m.support(100,19,10)
    assert not m.support(100,100,4.99)

def test_circular_peak_and_deterministic_ties():
    assert m.peak_window([0]*12) is None
    assert m.peak_window([1]*12)==1
    assert m.peak_window([10,9,0,0,0,0,0,0,0,0,0,11])==12
    assert m.month_distance(12,1)==1
    assert m.month_distance(1,7)==6
    assert m.month_distance(None,7) is None
    with pytest.raises(ValueError):m.peak_window([1]*11)

def test_local_fit_excludes_outage_and_never_uses_audit_years():
    rows=[{'year':y,'month':mo,'aqua':2,'viirs_occupied':10} for y in range(2019,2026) for mo in range(1,13)]
    for r in rows:
        if r['year']>=2022 or r['year']==2020 and r['month'] in [8,9]:r['aqua']=99999
    fit=m.fit_local(rows)
    assert [r['months'] for r in fit]==[9,9,7,9]
    assert all(r['factor']==pytest.approx(.2) for r in fit)
    with pytest.raises(ValueError):m.fit_local([{**r,'viirs_occupied':0} for r in rows])

def test_source_filtering_retains_sensor_and_deduplicates_daily_cells(tmp_path,monkeypatch):
    folder=tmp_path/'data/raw';folder.mkdir(parents=True)
    header='latitude,longitude,acq_date,acq_time,satellite,confidence,version\n'
    body='31,75,2022-11-01,0900,A,80,6.1\n31,75,2022-11-01,0900,A,80,6.1\n31,75,2022-11-01,1000,A,80,6.1\n31,75,2022-11-02,1000,A,80,6.1\n31,75,2022-11-03,1000,T,80,6.1\n31,75,2022-11-04,1000,A,29,6.1\n31,90,2022-11-01,1000,A,80,6.1\n'
    name='modis_2022_India.csv';(folder/name).write_text(header+body)
    monkeypatch.setattr(m,'ROOT',tmp_path)
    counts,audit=m.count_source({'filename':name,'sha256':'test'},[73.8,29.5,76.9,32.6],Transformer.from_crs(4326,6933,always_xy=True))
    nov=next(r for r in counts if r['month']==11)
    assert nov['raw']==3 and nov['active']==2
    assert audit['retained_detections']==3 and audit['downloaded_rows']==7
    assert audit['sensor']=='aqua' and audit['versions']==['6.1']

def test_transfer_report_preserves_two_fixed_geographies_and_all_methods():
    report=json.loads((ROOT/'reports/transfer-cases.json').read_text(encoding='utf-8'))
    assert report['source_files']==60
    assert len(report['sources'])==60
    assert all(len(s['sha256'])==64 and s['url'].startswith(m.BASE) for s in report['sources'])
    assert [r['bounds'] for r in report['regions']]==[[73.8,29.5,76.9,32.6],[147,-38,153,-30]]
    for region in report['regions']:
        assert len(region['months'])==84 and len(region['history'])==276
        assert region['audit_years']==[2022,2025]
        assert region['transfer_sector']==(0 if region['id']=='punjab' else 2)
        assert all(len(b['samples'])==15 for b in region['baseline'])
        audit=[r for r in region['months'] if r['year']>=2022]
        for method in m.MODELS:
            metric=region['metrics'][method]
            assert metric['months']==48
            assert metric['gated_months']+metric['withheld_months']==48
            assert metric['category_correct']==sum(r['classes'][method]==r['classes']['aqua'] for r in audit if r['baseline_median']>0)
            assert metric['wape']==pytest.approx(sum(abs(r[method]-r['aqua']) for r in audit)/sum(r['aqua'] for r in audit))
        assert any(r['known_outage_warning'] for r in region['months'])
    assert (ROOT/'reports/transfer-cases.json').read_bytes()==(ROOT/'web/public/data/transfer-cases.json').read_bytes()
