"""Pinned, date-matched month-to-date NRT diagnostic; never an observation denominator.

Uses authorized Earthdata access through requests/netrc. Credentials are never emitted.
No fitting: original Indonesia NOAA-20 sector/quarter coefficients are frozen.
"""
import gzip
import hashlib
import importlib.util
import io
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer
from shapely import contains_xy
from shapely.geometry import shape
from shapely.ops import unary_union
from harmonize import sector, quarter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'web/public/data'
RAW = ROOT / 'data/raw'
REPORTS = ROOT / 'reports'
START, END = date(2026, 11, 1), date(2026, 11, 13)
DIRECTORIES = {
    'aqua': 'https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/modis-c6.1/Global/',
    'noaa20': 'https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/noaa-20-viirs-c2/Global/',
}
spec = importlib.util.spec_from_file_location('recent_helpers', ROOT / 'pipeline/09_recent_comparison.py')
recent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recent)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def dates():
    return [START + timedelta(days=i) for i in range((END-START).days+1)]


def validate_daily(data, expected):
    """An empty but well-formed file is available; an absent/HTML file is not zero."""
    d = pd.read_csv(io.BytesIO(data), dtype={'acq_time': str, 'confidence': str, 'version': str})
    required = {'latitude', 'longitude', 'acq_date', 'acq_time', 'satellite', 'confidence', 'version'}
    if not required.issubset(d.columns):
        raise ValueError('Daily response is not a supported FIRMS table')
    if len(d) and not pd.to_datetime(d.acq_date).dt.date.eq(expected).all():
        raise ValueError('Daily file contains observations outside its declared UTC date')
    return d


def fetch_daily():
    jobs = []
    for sensor, directory in DIRECTORIES.items():
        with requests.Session() as session:
            response = session.get(directory, timeout=90)
            response.raise_for_status()
        links = sorted(set(urljoin(directory, u) for u in re.findall(r'href=[\"\']([^\"\']+)', response.text)))
        for day in dates():
            suffix = f'_{day.year}{day.timetuple().tm_yday:03d}.txt'
            found = [u for u in links if u.startswith(directory) and u.endswith(suffix)]
            jobs.append((sensor, day, found[0] if len(found) == 1 else None))

    def get(job):
        sensor, day, url = job
        item = {'sensor': sensor, 'date': str(day), 'url': url, 'status': 'unavailable'}
        if url is None:
            item['reason'] = 'Daily file not advertised by official NASA directory'
            return item, None
        path = RAW / f'mtd-{sensor}-{day}.txt'
        receipt = RAW / f'mtd-{sensor}-{day}.receipt.json'
        try:
            if path.exists() and receipt.exists():
                data = path.read_bytes()
                previous = json.loads(receipt.read_text(encoding='utf-8'))
                if digest(data) != previous['sha256']:
                    raise ValueError('Pinned daily source hash differs from receipt')
                item.update(previous)
            else:
                with requests.Session() as session:
                    response = session.get(url, timeout=120)
                    response.raise_for_status()
                    data = response.content
                validate_daily(data, day)
                item.update({'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'sha256': digest(data), 'bytes': len(data)})
                path.write_bytes(data)
                save_json(receipt, item)
            frame = validate_daily(data, day)
            item.update({'status': 'available', 'file': path.name, 'rows': len(frame), 'versions': sorted(frame.version.dropna().unique().tolist()), 'satellites': sorted(frame.satellite.astype(str).unique().tolist())})
            print('Daily source', sensor, str(day), len(frame), flush=True)
            return item, frame
        except Exception as exc:
            # Exception strings may contain redirected credential URLs. Record only class.
            item['reason'] = type(exc).__name__ + ': source retrieval/validation failed'
            return item, None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(get, jobs))
    ledger = [item for item, _ in results]
    save_json(REPORTS / 'month-to-date-sources.json', ledger)
    if any(frame is None for _, frame in results):
        raise RuntimeError('Incomplete source-date ledger: comparison withheld; inspect month-to-date-sources.json')
    return ledger, {sensor: pd.concat([frame for item, frame in results if item['sensor'] == sensor], ignore_index=True) for sensor in DIRECTORIES}


def clean(d, sensor, polygon):
    d = d.copy()
    if sensor == 'aqua':
        d = d[d.satellite.astype(str).str.upper().isin(['A', 'AQUA']) & pd.to_numeric(d.confidence, errors='coerce').ge(30)]
    else:
        d = d[d.confidence.str.lower().isin(['n', 'h', 'nominal', 'high'])]
    d = d.copy()
    d['acq_time'] = d.acq_time.astype(str).str.replace(':', '', regex=False).str.zfill(4)
    dt = pd.to_datetime(d.acq_date)
    d['month'], d['day'] = dt.dt.month, dt.dt.day
    d = d[d.day.between(START.day, END.day)]
    d = d[contains_xy(polygon, d.longitude.to_numpy(), d.latitude.to_numpy())].copy()
    d = d.drop_duplicates(['latitude', 'longitude', 'acq_date', 'acq_time', 'satellite'])
    d['cx'] = np.floor(d.longitude/.25).astype(int)
    d['cy'] = np.floor(d.latitude/.25).astype(int)
    return d


def main():
    meta_bytes = (OUT / 'metadata.json').read_bytes()
    meta = json.loads(meta_bytes)
    protocol = {
        'specified_before_new_results': True,
        'prior_information': 'Original monthly, Nov 8–12 snapshot, and external transfer results were seen. NOAA-20 Nov 1 file access was probed. This is an exploratory diagnostic, not a new untouched final benchmark.',
        'window': {'start': str(START), 'end': str(END), 'reason': 'Month start through last completed UTC day at the 14 November 2026 snapshot; not chosen by outcome.'},
        'sources': 'One global FIRMS daily file per sensor per date. Require all 26 valid tables before publishing the comparison. A present file is not proof of complete satellite observations.',
        'reference': 'Aqua 2003–2017 identical calendar dates, fixed median and 90th percentile. Retain 2003–2025 history and NOAA-20 2019–2025.',
        'calibration': 'Freeze original Indonesia NOAA-20 sector/quarter factors fitted 2019–2021; never refit on this window.',
        'frozen_model_sha256': digest(meta_bytes),
        'tests': 'All 48 month-start days 1–13 windows in 2022–2025, separately four November windows; publish all five predefined Indonesia regions. Leave one date out of current and historical windows together.',
        'geography': 'Apply identical existing Indonesia polygon to global NRT and Indonesia country archives. Coarse display/region assignment at 0.25 degree cell centres. Archive country assignment can exclude coastal detections before this mask.',
        'limits': 'NRT versus standard processing is unvalidated. No cloud/overpass denominator, no uncertainty interval, no forecast, no claim of distinct fires or area burned. No 2026 annual continuity implied.'
    }
    protocol_path = REPORTS / 'month-to-date-protocol.json'
    if protocol_path.exists():
        previous = json.loads(protocol_path.read_text(encoding='utf-8'))
        if previous != protocol:
            raise ValueError('Pinned protocol/model changed; inspect before rerunning')
    else:
        save_json(protocol_path, protocol)
    source_ledger, current = fetch_daily()
    factors = {(f['sector'], f['quarter']): f['factor'] for f in meta['factors']['noaa20']}
    single = sum(f['reference_total'] for f in meta['factors']['noaa20']) / sum(f['sensor_total'] for f in meta['factors']['noaa20'])
    boundary_bytes = (RAW / 'boundary.geojson').read_bytes()
    polygon = unary_union([shape(f['geometry']) for f in json.loads(boundary_bytes)['features']])
    project = Transformer.from_crs(4326, 6933, always_xy=True)
    sources = json.loads((REPORTS / 'source_manifest.json').read_text(encoding='utf-8'))
    inputs = [(s, int(s['filename'].split('_')[1]), 'aqua' if s['filename'].startswith('modis') else 'noaa20') for s in sources if s['filename'].startswith('modis') or (s['filename'].startswith('viirs-jpss1') and int(s['filename'].split('_')[1]) >= 2019)]
    assert len(inputs) == 30
    spatial, regional, audits, point_frames = [], [], [], []
    for src, year, sensor in inputs + [(None, START.year, 'aqua'), (None, START.year, 'noaa20')]:
        if src:
            path = RAW / src['filename']
            data = path.read_bytes()
            if len(data) != int(src['size']) or digest(data) != src['sha256']:
                raise ValueError('Historical source changed: ' + path.name)
            frame = pd.read_csv(io.BytesIO(data), dtype={'acq_time': str, 'confidence': str, 'version': str})
        else:
            frame = current[sensor]
        d = clean(frame, sensor, polygon)
        u = recent.occupied(d, project)
        u['adjusted'] = 1.0 if sensor == 'aqua' else [factors[(int(s), int(q))] for s, q in zip(sector(u.longitude), quarter(u.month))]
        if src is None:
            points = d.copy(); points['sensor'] = sensor; point_frames.append(points)
            for item in source_ledger:
                if item['sensor'] == sensor:
                    day = date.fromisoformat(item['date']).day
                    item['retained_detections'] = int(d.day.eq(day).sum())
                    item['occupied_cell_days'] = int(u.day.eq(day).sum())
        for key, bbox in recent.REGIONS.items():
            r, a = recent.select(d, bbox), recent.select(u, bbox)
            for month in (range(1, 13) if src else [START.month]):
                sub = a[a.month == month]
                regional.append({'region': key, 'year': year, 'month': month, 'sensor': sensor, 'raw': int(r.month.eq(month).sum()), 'active': len(sub), 'adjusted': float(sub.adjusted.sum())})
        r = d[d.month == START.month].groupby(['day', 'cx', 'cy']).size().rename('raw')
        a = u[u.month == START.month].groupby(['day', 'cx', 'cy']).agg(active=('gx', 'size'), adjusted=('adjusted', 'sum'))
        z = pd.concat([r, a], axis=1).fillna(0).reset_index(); z['year'] = year; z['sensor'] = sensor; spatial.append(z)
        audits.append({'file': src['filename'] if src else 'daily NRT:' + sensor, 'year': year, 'sensor': sensor, 'retained_detections': len(d), 'active_cell_days': len(u), 'versions': sorted(frame.version.dropna().unique().tolist()), 'sha256': src['sha256'] if src else None})
        print('Historical match', sensor, year, len(d), flush=True)
    ledger = pd.DataFrame(regional)
    ledger.to_csv(REPORTS / 'month-to-date-window-counts.csv', index=False)
    detail = pd.concat(spatial, ignore_index=True)
    raw = detail.pivot(index=['year', 'day', 'cx', 'cy'], columns='sensor', values='raw').reindex(columns=['aqua', 'noaa20']).fillna(0)
    active = detail.pivot(index=['year', 'day', 'cx', 'cy'], columns='sensor', values='active').reindex(columns=['aqua', 'noaa20']).fillna(0)
    adjusted = detail.pivot(index=['year', 'day', 'cx', 'cy'], columns='sensor', values='adjusted').reindex(columns=['noaa20']).fillna(0)
    rows = np.column_stack([raw.index.to_frame(index=False).values, raw.values, active.values, adjusted.values]).tolist()
    reports = {}
    for key, bbox in recent.REGIONS.items():
        d = ledger[ledger.region == key]
        wide = d.pivot(index=['year', 'month'], columns='sensor', values='active').reset_index()
        wide = wide.merge(d[d.sensor == 'noaa20'][['year', 'month', 'adjusted']], on=['year', 'month'], how='left')
        wide['single'] = wide.noaa20 * single
        test = wide[wide.year.between(2022, 2025)]
        matched = test[test.month == START.month]
        baseline = wide[wide.year.between(2003, 2017)].groupby('month').aqua.agg(median='median', p90=lambda x: x.quantile(.9))
        def comparisons(z):
            return [{'year': int(r.year), 'month': int(r.month), 'aqua': int(r.aqua), 'noaa20': int(r.noaa20), 'adjusted': float(r.adjusted), 'aqua_category': recent.category(r.aqua, baseline.loc[r.month, 'median'], baseline.loc[r.month, 'p90']), 'adjusted_category': recent.category(r.adjusted, baseline.loc[r.month, 'median'], baseline.loc[r.month, 'p90'])} for r in z.itertuples()]
        comp = comparisons(test); valid = [r for r in comp if r['aqua_category'] != 'Insufficient baseline']
        now = comparisons(wide[wide.year == START.year])[0]
        now['median'] = float(baseline.loc[START.month, 'median']); now['p90'] = float(baseline.loc[START.month, 'p90'])
        sd = recent.select(detail, bbox); sensitivity = []
        for omit in range(START.day, END.day + 1):
            sub = sd[sd.day != omit]
            aqua = sub[sub.sensor == 'aqua'].groupby('year').active.sum().reindex(range(2003, 2018), fill_value=0)
            med, p90 = float(aqua.median()), float(aqua.quantile(.9)); n = sub[sub.year == START.year]
            sensitivity.append({'omitted_day': omit, 'median': med, 'p90': p90, 'aqua_category': recent.category(n[n.sensor == 'aqua'].active.sum(), med, p90), 'adjusted_category': recent.category(n[n.sensor == 'noaa20'].adjusted.sum(), med, p90)})
        reports[key] = {'bbox': bbox, 'all_month_windows': recent.score(test), 'same_calendar_dates': recent.score(matched), 'category_agreement': {'agree': sum(r['aqua_category'] == r['adjusted_category'] for r in valid), 'eligible': len(valid)}, 'matched_years': comparisons(matched), 'current': now, 'leave_one_day_out': sensitivity}
    payload = {'schema_version': 1, 'status': 'provisional', 'window': {'start': str(START), 'end': str(END), 'days': len(dates()), 'month': START.month, 'start_day': START.day, 'end_day': END.day}, 'retrieved_utc': max(s['retrieved_utc'] for s in source_ledger), 'baseline_years': [2003, 2017], 'historical_years': [2003, 2025], 'noaa20_historical_years': [2019, 2025], 'training_years': [2019, 2021], 'test_years': [2022, 2025], 'daily_sources': source_ledger, 'sources': source_ledger, 'historical_sources': [s for s, _, _ in inputs], 'source_availability': {'expected': 26, 'available': len(source_ledger), 'observation_coverage_known': False}, 'frozen_model_sha256': digest(meta_bytes), 'boundary_sha256': digest(boundary_bytes), 'protocol': protocol, 'regions': reports, 'columns': ['year', 'day', 'longitude_cell', 'latitude_cell', 'aqua_detections', 'noaa20_detections', 'aqua_cell_days', 'noaa20_cell_days', 'adjusted_noaa20_cell_days'], 'limits': ['Provisional NRT-to-standard comparison; processing continuity is unvalidated.', 'All 26 daily files are available. This does not establish complete satellite observations, clear-sky coverage or all fires detected.', 'Month-to-date means 1–13 November 2026 only; 14 November is excluded and no other 2026 months are represented.', 'All thermal source types retained; detections and occupied cell-days are neither distinct fires nor area burned.', 'Frozen monthly calibration is evaluated on shorter windows; residuals are diagnostics, not a confidence interval.', 'Current inter-sensor agreement is not independent ground truth; only four same-calendar held-out years are available.', 'Country archive assignment may omit coastal records before the identical polygon mask.', 'Missing dates outside this pinned snapshot are unavailable, never zeros. This is not an automatically refreshed live feed.']}
    history = gzip.compress(json.dumps(rows, separators=(',', ':'), allow_nan=False).encode(), mtime=0)
    points = pd.concat(point_frames, ignore_index=True).drop(columns=['cx', 'cy', 'month', 'day'])
    points_bytes = gzip.compress(points.to_csv(index=False).encode(), mtime=0)
    payload['history_sha256'] = digest(history); payload['detections_sha256'] = digest(points_bytes)
    payload['snapshot_sha256'] = payload['detections_sha256']
    for target in [REPORTS / 'month-to-date.json', OUT / 'month-to-date.json']:
        save_json(target, payload)
    (OUT / 'month-to-date-history.json.gz').write_bytes(history)
    (OUT / 'month-to-date-detections.csv.gz').write_bytes(points_bytes)
    save_json(OUT / 'month-to-date-protocol.json', protocol)
    save_json(REPORTS / 'month-to-date-sources.json', source_ledger)
    save_json(REPORTS / 'month-to-date-input-audit.json', audits)
    print(json.dumps({k: {'current': v['current'], 'heldout_wape': v['same_calendar_dates']['wape']} for k, v in reports.items()}, indent=2), flush=True)


if __name__ == '__main__':
    main()
