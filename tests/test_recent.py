import gzip,importlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
m=importlib.import_module('09_recent_comparison')

def test_settled_window_excludes_edge_and_delivery_dates():
    s={'retrieved_utc':'2026-11-14T07:10:00+00:00','sources':[{'global_file_date_span':['2026-11-07','2026-11-14']},{'global_file_date_span':['2026-11-07','2026-11-13']}]}
    start,end=m.date_window(s)
    assert str(start)=='2026-11-08' and str(end)=='2026-11-12'
    assert (datetime.fromisoformat(s['retrieved_utc'])-datetime(2026,11,13,tzinfo=timezone.utc)).total_seconds()>=86400

def test_too_short_or_cross_month_window_is_rejected():
    import pytest
    for dates in [['2026-11-12','2026-11-14'],['2026-10-29','2026-11-04']]:
        with pytest.raises(ValueError):m.date_window({'retrieved_utc':'2026-11-14T07:10:00+00:00','sources':[{'global_file_date_span':dates}]})

def test_cell_day_identity_and_tie_break_are_deterministic():
    d=pd.DataFrame({'acq_date':['2026-11-08','2026-11-08','2026-11-09'],'acq_time':['0100','0100','0100'],'longitude':[110.,110.00001,110.],'latitude':[-2.,-2.,-2.]})
    project=Transformer.from_crs(4326,6933,always_xy=True)
    a=m.occupied(d,project);b=m.occupied(d.iloc[::-1],project)
    assert len(a)==2 and a.longitude.tolist()==b.longitude.tolist()

def test_exported_recent_aggregates_reconcile_with_held_out_reports():
    payload=json.loads((ROOT/'reports/recent-comparison.json').read_text())
    rows=np.array(json.loads(gzip.decompress((ROOT/'web/public/data/recent-history.json.gz').read_bytes())))
    ledger=pd.read_csv(ROOT/'reports/recent_window_counts.csv')
    for key,r in payload['regions'].items():
        w,s,e,n=r['bbox'];x=(rows[:,2]+.5)*.25;y=(rows[:,3]+.5)*.25
        z=rows[(x>=w)&(x<e)&(y>=s)&(y<n)&(rows[:,0]==2026)]
        assert z[:,6].sum()==r['current']['aqua']
        assert abs(z[:,8].sum()-r['current']['adjusted'])<1e-8
        assert r['all_month_windows']['windows']==48 and r['same_calendar_dates']['windows']==4
        d=ledger[(ledger.region==key)&ledger.year.between(2022,2025)]
        a=d[d.sensor=='aqua'].sort_values(['year','month']);b=d[d.sensor=='noaa20'].sort_values(['year','month'])
        expected=abs(a.active.to_numpy()-b.adjusted.to_numpy()).sum()/a.active.sum()
        assert abs(expected-r['all_month_windows']['wape'])<1e-12
    assert set(rows[:,1])==set(range(8,13))
    assert payload['training_years'][1]<payload['test_years'][0]<2026

def test_current_points_independently_reproduce_cell_day_counts():
    snapshot=json.loads((ROOT/'web/public/data/recent.json').read_text())
    r=json.loads((ROOT/'reports/recent-comparison.json').read_text())
    project=Transformer.from_crs(4326,6933,always_xy=True)
    for sensor,column in [('aqua','aqua'),('noaa20','noaa20')]:
        points=[p for p in snapshot['records'] if p['sensor']==sensor and r['window']['start']<=p['acq_date']<=r['window']['end']]
        cells=set()
        for p in points:
            x,y=project.transform(p['longitude'],p['latitude']);cells.add((p['acq_date'],int(np.floor(x/1000)),int(np.floor(y/1000))))
        assert len(cells)==r['regions']['indonesia']['current'][column]

def test_zero_baseline_has_no_anomaly_category():
    assert m.category(100,0,10)=='Insufficient baseline'
    assert m.category(20,10,20)=='Above typical'
