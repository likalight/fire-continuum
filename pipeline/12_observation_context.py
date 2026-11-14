"""Read NASA daily fire masks for a fixed case; never alter hotspot calibration.

Earthdata credentials may be read by requests from the user's existing .netrc.
No credentials, response login pages or signed redirect URLs are logged.
"""
import argparse
import csv
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
LABELS = ['Missing input', 'Not processed (obsolete)', 'Not processed', 'Non-fire water',
          'Cloud', 'Non-fire land', 'Unknown', 'Fire: low confidence',
          'Fire: nominal confidence', 'Fire: high confidence']
SPEC = 'https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MYD14A1'


def partition(values):
    a = np.asarray(values)
    if a.size == 0 or np.any(a < 0) or np.any(a > 9) or np.any(a != np.floor(a)):
        raise ValueError('Expected a nonempty mask of integer classes 0–9')
    return np.bincount(a.astype(int).ravel(), minlength=10).tolist()


def grid_mask(structure, shape, bounds):
    def pair(name):
        m = re.search(name + r'=\(([^,]+),([^\)]+)\)', structure)
        if not m:
            raise ValueError('Missing grid coordinates')
        return tuple(float(v) for v in m.groups())
    left, top = pair('UpperLeftPointMtrs')
    right, bottom = pair('LowerRightMtrs')
    ny, nx = shape
    x = left + (np.arange(nx) + .5) * (right-left) / nx
    y = top + (np.arange(ny) + .5) * (bottom-top) / ny
    lat = np.degrees(y / 6371007.181)
    lon = np.degrees(x[None, :] / (6371007.181 * np.cos(np.radians(lat[:, None]))))
    w, s, e, n = bounds
    return (lon >= w) & (lon < e) & (lat[:, None] >= s) & (lat[:, None] < n)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cached', action='store_true')
    args = parser.parse_args()
    from pyhdf.SD import SD, SDC
    protocol = json.loads((ROOT/'reports/observation_protocol.json').read_text())
    report_path = ROOT/'reports/observation-context.json'
    prior = json.loads(report_path.read_text()) if args.cached else None
    session = requests.Session()
    sources, daily, fixed_mask = [], [], None
    for start, end in protocol['periods']:
        if prior:
            entries = [s for s in prior['sources'] if s['period_start'] == start]
        else:
            r = session.get('https://cmr.earthdata.nasa.gov/search/granules.json', params={
                'short_name':'MYD14A1', 'version':'061', 'temporal':f'{start}T00:00:00Z,{end}T23:59:59Z',
                'bounding_box':','.join(map(str, protocol['bounds_west_south_east_north'])), 'page_size':20}, timeout=45)
            r.raise_for_status()
            entries = []
            for g in r.json()['feed']['entry']:
                if '.h29v09.' not in g['producer_granule_id']:
                    continue
                url = next(l['href'] for l in g['links'] if l.get('rel','').endswith('/data#') and l['href'].endswith('.hdf'))
                entries.append({'granule':g['producer_granule_id'], 'url':url, 'cmr_id':g['id'], 'period_start':start})
        if not entries:
            raise RuntimeError('No matching NASA daily granules')
        for entry in entries:
            path = ROOT/'data/raw'/(entry['granule']+'.hdf')
            if not path.exists():
                if args.cached:
                    raise RuntimeError('Pinned raw file unavailable')
                r = session.get(entry['url'], timeout=(20,60))
                if r.status_code != 200 or r.content[:4] != b'\x0e\x03\x13\x01':
                    raise RuntimeError(f'NASA product access failed (HTTP {r.status_code}); login response not saved')
                path.write_bytes(r.content)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if prior and digest != entry['sha256']:
                raise RuntimeError('Pinned source hash mismatch')
            entry.update(sha256=digest, bytes=path.stat().st_size)
            entry.setdefault('retrieved_utc',datetime.now(timezone.utc).isoformat())
            sources.append(entry)
            f = SD(str(path), SDC.READ)
            attrs = f.attributes()
            ds = f.select('FireMask')
            masks = ds.get()
            if masks.ndim != 3 or masks.shape[1:] != (1200,1200):
                raise ValueError('Unexpected NASA grid shape')
            sample = grid_mask(attrs['StructMetadata.0'], masks.shape[1:], protocol['bounds_west_south_east_north'])
            if fixed_mask is not None and not np.array_equal(sample, fixed_mask):
                raise ValueError('Grid changed between granules')
            fixed_mask = sample
            first = date.fromisoformat(attrs['StartDate'])
            for i, values in enumerate(masks):
                day = (first + timedelta(days=i)).isoformat()
                if start <= day <= end:
                    counts = partition(values[sample])
                    daily.append({'date':day, 'counts':counts, 'total_cells':int(sample.sum()), 'granule':entry['granule']})
            f.end()
    daily.sort(key=lambda r:r['date'])
    expected = {str(date.fromisoformat(start)+timedelta(days=i)) for start,end in protocol['periods'] for i in range((date.fromisoformat(end)-date.fromisoformat(start)).days+1)}
    if len(daily) != len(expected) or {r['date'] for r in daily} != expected:
        raise ValueError('Duplicate or missing daily slices')
    report = {'product':'MYD14A1.061', 'title':'Southern Kalimantan daily observation context',
              'bounds':protocol['bounds_west_south_east_north'], 'classes':LABELS,
              'grid':'Native MODIS sinusoidal; cell centres; nominal 1 km',
              'doi':'https://doi.org/10.5067/MODIS/MYD14A1.061', 'specification':SPEC,
              'sources':sources, 'days':daily, 'limitations':protocol['guardrails'],
              'protocol_sha256':hashlib.sha256((ROOT/'reports/observation_protocol.json').read_bytes()).hexdigest()}
    text = json.dumps(report,indent=2)+'\n'
    report_path.write_text(text)
    (ROOT/'web/public/data/observation-context.json').write_text(text)
    (ROOT/'web/public/data/observation_protocol.json').write_bytes((ROOT/'reports/observation_protocol.json').read_bytes())
    with (ROOT/'web/public/data/observation-context.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['date','total_cells']+LABELS+['granule'])
        for day in daily:writer.writerow([day['date'],day['total_cells']]+day['counts']+[day['granule']])
    print(json.dumps({'days':len(daily),'fixed_grid_cells':daily[0]['total_cells'],'source_files':len(sources),
                      'daily_fire_range':[min(sum(d['counts'][7:]) for d in daily),max(sum(d['counts'][7:]) for d in daily)],
                      'daily_cloud_range':[min(d['counts'][4] for d in daily),max(d['counts'][4] for d in daily)]}))


if __name__ == '__main__':
    main()
