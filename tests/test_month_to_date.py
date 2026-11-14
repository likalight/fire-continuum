import gzip
import importlib
import io
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline'))
m = importlib.import_module('20_month_to_date')


def test_daily_validation_rejects_html_and_wrong_date_but_accepts_empty_table():
    header = b'latitude,longitude,acq_date,acq_time,satellite,confidence,version\n'
    assert m.validate_daily(header, date(2026, 11, 1)).empty
    with pytest.raises(ValueError):
        m.validate_daily(b'<html>Sign in</html>', date(2026, 11, 1))
    with pytest.raises(ValueError):
        m.validate_daily(header + b'-2,110,2026-11-02,1300,Aqua,80,6.1NRT\n', date(2026, 11, 1))


def test_source_ledger_covers_every_day_sensor_without_equating_to_observations():
    p = json.loads((ROOT / 'web/public/data/month-to-date.json').read_text())
    pairs = {(r['sensor'], r['date']) for r in p['daily_sources']}
    assert len(pairs) == len(p['daily_sources']) == 26
    assert pairs == {(sensor, str(day)) for sensor in ('aqua', 'noaa20') for day in m.dates()}
    assert all(r['status'] == 'available' and len(r['sha256']) == 64 for r in p['daily_sources'])
    assert p['source_availability']['observation_coverage_known'] is False
    assert p['frozen_model_sha256'] == m.digest((ROOT / 'web/public/data/metadata.json').read_bytes())
    assert p['snapshot_sha256'] == p['detections_sha256']


def test_current_original_points_independently_reproduce_activity_and_frozen_estimate():
    p = json.loads((ROOT / 'web/public/data/month-to-date.json').read_text())
    data = (ROOT / 'web/public/data/month-to-date-detections.csv.gz').read_bytes()
    assert m.digest(data) == p['detections_sha256']
    d = pd.read_csv(io.BytesIO(gzip.decompress(data)), dtype={'acq_time': str})
    assert d.acq_date.min() >= '2026-11-01' and d.acq_date.max() <= '2026-11-13'
    model = json.loads((ROOT / 'web/public/data/metadata.json').read_text())
    factors = {(f['sector'], f['quarter']): f['factor'] for f in model['factors']['noaa20']}
    transform = Transformer.from_crs(4326, 6933, always_xy=True)
    for sensor in ('aqua', 'noaa20'):
        cells = {}
        for row in d[d.sensor == sensor].sort_values(['acq_time', 'longitude', 'latitude']).itertuples():
            x, y = transform.transform(row.longitude, row.latitude)
            key = (row.acq_date, int(np.floor(x/1000)), int(np.floor(y/1000)))
            cells.setdefault(key, row.longitude)
        assert len(cells) == p['regions']['indonesia']['current'][sensor]
        if sensor == 'noaa20':
            estimate = sum(factors[(0 if lon < 108 else 1 if lon < 120 else 2, 3)] for lon in cells.values())
            assert estimate == pytest.approx(p['regions']['indonesia']['current']['adjusted'])


def test_sparse_history_reproduces_regions_baseline_and_heldout_error():
    p = json.loads((ROOT / 'web/public/data/month-to-date.json').read_text())
    blob = (ROOT / 'web/public/data/month-to-date-history.json.gz').read_bytes()
    assert m.digest(blob) == p['history_sha256']
    rows = np.array(json.loads(gzip.decompress(blob)))
    ledger = pd.read_csv(ROOT / 'reports/month-to-date-window-counts.csv')
    for key, region in p['regions'].items():
        w, s, e, n = region['bbox']; x = (rows[:, 2]+.5)*.25; y = (rows[:, 3]+.5)*.25
        selected = rows[(x >= w) & (x < e) & (y >= s) & (y < n)]
        now = selected[selected[:, 0] == 2026]
        assert now[:, 6].sum() == region['current']['aqua']
        assert now[:, 8].sum() == pytest.approx(region['current']['adjusted'])
        baseline = [selected[selected[:, 0] == year, 6].sum() for year in range(2003, 2018)]
        assert np.median(baseline) == region['current']['median']
        assert np.quantile(baseline, .9) == region['current']['p90']
        d = ledger[(ledger.region == key) & ledger.year.between(2022, 2025)]
        a = d[d.sensor == 'aqua'].sort_values(['year', 'month']).active.to_numpy()
        b = d[d.sensor == 'noaa20'].sort_values(['year', 'month']).adjusted.to_numpy()
        assert abs(a-b).sum()/a.sum() == pytest.approx(region['all_month_windows']['wape'])
        assert region['same_calendar_dates']['windows'] == 4
        assert region['all_month_windows']['windows'] == 48
        assert len(region['leave_one_day_out']) == 13
        for omission in region['leave_one_day_out']:
            kept = selected[selected[:, 1] != omission['omitted_day']]
            baseline = [kept[kept[:, 0] == year, 6].sum() for year in range(2003, 2018)]
            median, p90 = np.median(baseline), np.quantile(baseline, .9)
            current = kept[kept[:, 0] == 2026]
            assert median == omission['median'] and p90 == omission['p90']
            assert m.recent.category(current[:, 6].sum(), median, p90) == omission['aqua_category']
            assert m.recent.category(current[:, 8].sum(), median, p90) == omission['adjusted_category']
