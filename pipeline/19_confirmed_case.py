"""Curated Landsat/FIRMS event demonstration, explicitly not an accuracy test.

Run from the repository: python pipeline/19_confirmed_case.py [--cached]
Raw NASA FIRMS archives must already exist (pipeline/01_download.py).
Optional raster/display dependencies: requirements-imagery.txt.
"""
import argparse
import hashlib
import importlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
OUT = ROOT / 'web/public/data'
REPORTS = ROOT / 'reports'
SCENE = 'LC08_L2SP_118062_20190915_02_T1'
DATE = '2019-09-15'
LANDSAT_TIME = '2019-09-15T02:34:50.651419Z'
CONTEXT_BOUNDS = [113.75, -3.25, 114.0, -3.0]
BOUNDS = [113.85, -3.10, 113.95, -3.00]
BANDS = ['swir22', 'swir16', 'blue', 'red', 'green', 'qa_pixel', 'qa_radsat']
STAC = 'https://planetarycomputer.microsoft.com/api/stac/v1'
NASA = 'https://science.nasa.gov/earth/earth-observatory/smoke-blankets-borneo-145614/'
QA_SOURCE = 'https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands'
SCALE_SOURCE = 'https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products'
SENSOR_KEYS = {'modis': {'Aqua': 'aqua', 'Terra': 'terra'},
               'viirs-snpp': {'N': 'snpp'}, 'viirs-jpss1': {'N20': 'noaa20'}}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_time(date, hhmm):
    """FIRMS integer HHMM is UTC, including leading-zero morning passes."""
    value = str(hhmm).strip().zfill(4)
    if not value.isdigit() or len(value) != 4:
        raise ValueError('Invalid FIRMS HHMM')
    return datetime.strptime(date + value, '%Y-%m-%d%H%M').replace(tzinfo=timezone.utc)


def minutes_after(date, hhmm, reference=LANDSAT_TIME):
    return (parse_time(date, hhmm) - datetime.fromisoformat(reference.replace('Z', '+00:00'))).total_seconds() / 60


def filter_points(frame, sensor, bounds=BOUNDS, date=DATE):
    """Same UTC date; half-open longitude/latitude bounds; unchanged confidence rules."""
    west, south, east, north = bounds
    spatial = frame.longitude.ge(west) & frame.longitude.lt(east) & frame.latitude.ge(south) & frame.latitude.lt(north)
    confidence = (pd.to_numeric(frame.confidence, errors='coerce').ge(30) if sensor == 'modis'
                  else frame.confidence.astype(str).str.lower().isin(['n', 'h']))
    return frame[spatial & confidence & frame.acq_date.eq(date)].copy()


def crop_bounds(data, source_bounds, target_bounds):
    """Exact pixel-aligned subwindow; refuses silently rounded geographic edges."""
    west, south, east, north = source_bounds
    tw, ts, te, tn = target_bounds
    if not (west <= tw < te <= east and south <= ts < tn <= north):
        raise ValueError('Crop outside source grid')
    height, width = data.shape[-2:]
    edges = [(tw-west)/(east-west)*width, (te-west)/(east-west)*width,
             (north-tn)/(north-south)*height, (north-ts)/(north-south)*height]
    if any(abs(v-round(v)) > 1e-7 for v in edges):
        raise ValueError('Crop edges do not align to the existing grid')
    left, right, top, bottom = map(lambda v: int(round(v)), edges)
    return data[:, top:bottom, left:right]


def read_scene(cached):
    catalog = RAW / 'imagery-stac.json'
    item = None
    if catalog.exists():
        item = next((i for i in json.loads(catalog.read_text(encoding='utf-8'))['features'] if i['id'] == SCENE), None)
    if item is None:
        if cached:
            raise ValueError('Pinned scene catalog absent')
        import requests
        response = requests.get(f'{STAC}/collections/landsat-c2-l2/items/{SCENE}', timeout=45)
        response.raise_for_status()
        item = response.json()
    if item['id'] != SCENE or item['properties']['datetime'] != LANDSAT_TIME:
        raise ValueError('Unexpected scene identity or acquisition time')
    path = RAW / 'confirmed-search-west-river.npz'
    if path.exists():
        data = np.load(path)['data']
    else:
        if cached:
            raise ValueError('Pinned Landsat subset absent')
        imagery = importlib.import_module('18_imagery_audit')
        with ThreadPoolExecutor(max_workers=3) as pool:
            data = np.stack(list(pool.map(lambda band: imagery.read_band(item, band, CONTEXT_BOUNDS), BANDS)))
        np.savez_compressed(path, data=data)
    if data.shape != (7, 900, 900):
        raise ValueError('Unexpected source grid shape')
    previous = REPORTS / 'confirmed-case.json'
    digest = hashlib.sha256(data.tobytes()).hexdigest()
    if cached and previous.exists():
        expected = json.loads(previous.read_text(encoding='utf-8'))['provenance']
        if digest != expected['context_array_sha256']:
            raise ValueError('Pinned subset array changed')
        if hashlib.sha256(json.dumps(item,sort_keys=True,separators=(',',':')).encode()).hexdigest() != expected['stac_item_sha256']:
            raise ValueError('Pinned scene metadata changed')
    return item, data, crop_bounds(data, CONTEXT_BOUNDS, BOUNDS)


def load_points():
    records, sources = [], []
    manifest = {r['filename']:r for r in json.loads((REPORTS/'source_manifest.json').read_text(encoding='utf-8'))}
    for sensor, platforms in SENSOR_KEYS.items():
        path = RAW / f'{sensor}_2019_Indonesia.csv'
        digest = sha(path)
        if digest != manifest[path.name]['sha256']:
            raise ValueError('FIRMS archive hash differs from download manifest')
        frame = pd.read_csv(path, dtype={'acq_time': str, 'confidence': str, 'version': str})
        selected = filter_points(frame, sensor)
        sources.append({'file': path.name, 'sha256': digest, 'rows': len(frame),
                        'source_url': manifest[path.name]['url']})
        for index, row in selected.iterrows():
            key = platforms.get(str(row.satellite))
            if key is None:
                raise ValueError('Unexpected source platform')
            stamp = parse_time(DATE, row.acq_time)
            records.append({'id': f'{sensor}:{int(index)+2}', 'source_file': path.name,
                            'source_csv_line': int(index)+2, 'sensor': sensor, 'platform': key,
                            'satellite': str(row.satellite), 'longitude': float(row.longitude),
                            'latitude': float(row.latitude), 'datetime': stamp.isoformat().replace('+00:00', 'Z'),
                            'minutes_after_landsat': minutes_after(DATE, row.acq_time),
                            'confidence': str(row.confidence), 'frp_mw': float(row.frp),
                            'daynight': str(row.daynight), 'version': str(row.version),
                            'type': str(row.get('type', '')),
                            'scan_km': float(row.scan), 'track_km': float(row.track)})
    return sorted(records, key=lambda r: (r['datetime'], r['platform'], r['id'])), sources


def render(data, records):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    display = data[:5].astype(np.float32)*.0000275-.2
    rgb = lambda indices: np.transpose(np.clip(display[indices]/.45, 0, 1)**.7, (1, 2, 0))
    natural, swir = rgb([3, 4, 2]), rgb([0, 1, 2])
    plt.imsave(OUT/'confirmed-case-natural.png', natural)
    plt.imsave(OUT/'confirmed-case-swir.png', swir)
    extent = [BOUNDS[0], BOUNDS[2], BOUNDS[1], BOUNDS[3]]
    nearest = min(r['minutes_after_landsat'] for r in records if r['minutes_after_landsat'] >= 0)
    closest = [r for r in records if r['minutes_after_landsat'] == nearest]
    # Transparent point layer: same grid, point centres only, no implied pixel footprints.
    fig = plt.figure(figsize=(3.6, 3.6), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(BOUNDS[0], BOUNDS[2]); ax.set_ylim(BOUNDS[1], BOUNDS[3])
    ax.scatter([r['longitude'] for r in closest], [r['latitude'] for r in closest],
               facecolors='none', edgecolors='#ffffff', s=36, linewidths=1.1)
    ax.axis('off'); fig.savefig(OUT/'confirmed-case-overlay.png', transparent=True, dpi=100); plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.7), layout='constrained')
    for ax, image, title in zip(axes, [natural, swir, swir],
                               ['Landsat natural color · 02:34:50 UTC', 'Landsat SWIR 7 / 6 / 2 · same scene', 'NOAA-20 point centres · 06:22 UTC']):
        ax.imshow(image, extent=extent, origin='upper', interpolation='nearest'); ax.set_title(title, fontsize=10)
        ax.set_xlabel('Longitude °E'); ax.set_ylabel('Latitude °N'); ax.tick_params(labelsize=8)
    axes[2].scatter([r['longitude'] for r in closest], [r['latitude'] for r in closest], facecolors='none', edgecolors='white', s=30, linewidths=1)
    fig.suptitle('15 September 2019 · Southern Borneo · Curated event corroboration', fontsize=14)
    fig.text(.5, -.10, 'Same place and UTC date; nearest FIRMS pass is 3 h 47 m later. White rings are observation centres, not fire perimeters.\nUSGS/NASA Landsat C2 L2 + NASA FIRMS. Smoke remains visible; this display does not validate counts, anomaly size, or model accuracy.', ha='center', fontsize=9)
    fig.savefig(OUT/'confirmed-case-panel.png', dpi=150, bbox_inches='tight'); plt.close(fig)
    return len(closest)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--cached', action='store_true'); args = parser.parse_args()
    item, context, data = read_scene(args.cached)
    records, sources = load_points()
    counts = {key: sum(r['platform'] == key for r in records) for key in ['aqua', 'snpp', 'terra', 'noaa20']}
    offsets = {key: min((abs(r['minutes_after_landsat']) for r in records if r['platform'] == key), default=None) for key in counts}
    colocated = [r for r in records if abs(r['minutes_after_landsat']) <= 60]
    overlay_count = render(data, records)
    features = [{'type': 'Feature', 'id': r['id'], 'geometry': {'type': 'Point', 'coordinates': [r['longitude'], r['latitude']]},
                 'properties': {k:v for k,v in r.items() if k not in ['longitude', 'latitude']}} for r in records]
    (OUT/'confirmed-case-points.geojson').write_text(json.dumps({'type':'FeatureCollection','bbox':BOUNDS,'features':features},indent=2,allow_nan=False)+'\n',encoding='utf-8')
    pd.DataFrame(records).to_csv(OUT/'confirmed-case-points.csv', index=False)
    assets = {k:'confirmed-case-'+k+'.png' for k in ['natural','swir','overlay','panel']}
    result = {
        'title': 'A real fire, seen by a different instrument', 'date': DATE, 'bounds': BOUNDS,
        'status': 'curated_event_corroboration', 'scene': {'id':SCENE,'datetime':LANDSAT_TIME,'platform':'Landsat 8','instrument':'OLI','product':'USGS Landsat Collection 2 Level 2','doi':'10.5066/P9OGBGM6'},
        'images': assets, 'counts': counts, 'nearest_time_offsets_minutes': offsets,
        'claim': 'Landsat shows a coherent bright shortwave-infrared front and a westward pale plume; NASA independently documented active fires in this scene. Later same-date FIRMS observations occupy the same small area. Together these corroborate burning at this place and date.',
        'selection_note': 'Retrospective, outcome-informed demonstration selected from a NASA-documented event after inspecting three regions. It is separate from the fixed six-cell audit, whose six outcomes remain inconclusive.',
        'limits': ['No FIRMS observation is within the predefined ±60-minute window. Nearest is NOAA-20, 3 h 47 m after Landsat; this is not simultaneous validation.',
                   'Does not validate hotspot totals, anomaly magnitude, harmonization accuracy, fire perimeter, burned area, or absence of fire.',
                   'Point centres represent different sensor footprints and acquisition times; detections are not distinct fires. Do not sum satellites.',
                   'SWIR image is a qualitative display of Level 2 data, not a calibrated active-fire classification. Fire emission, smoke, saturation and atmospheric correction can distort surface-reflectance values.',
                   'AI-assisted, non-blinded visual interpretation; no external practitioner review or representative accuracy estimate.'],
        'source_urls': [NASA, f'{STAC}/collections/landsat-c2-l2/items/{SCENE}', 'https://firms.modaps.eosdis.nasa.gov/country/', QA_SOURCE, SCALE_SOURCE],
        'visual_review': {'outcome':'corroborated_burning_at_place_and_date_only','reviewer':'AI-assisted non-blinded visual review',
                          'observations':['A bright pink/orange coherent front lies near 113.927°E, 3.025°S in the SWIR composite.','The same natural-color window contains a pale plume extending westward from this area; much ground detail is obscured.','NOAA-20 centres from 06:22 UTC lie along and near the bright SWIR front; the passes are 227.16 minutes apart.'],
                          'original_audit_changed':False},
        'timing_test': {'predefined_window_minutes':60,'matching_observation_count':len(colocated),'outcome':'No near-simultaneous match','date_basis':'UTC'},
        'overlay': {'file':assets['overlay'],'platform':'noaa20','datetime':'2019-09-15T06:22:00Z','count':overlay_count,'minutes_after_landsat':offsets['noaa20'],'meaning':'White rings: NOAA-20 observation centres, not perimeters or footprints; 3 h 47 m later.'},
        'passes': [{'platform':key,'datetime':stamp,'observations':sum(r['platform']==key and r['datetime']==stamp for r in records),'minutes_after_landsat':next(r['minutes_after_landsat'] for r in records if r['platform']==key and r['datetime']==stamp)} for key,stamp in sorted(set((r['platform'],r['datetime']) for r in records))],
        'points': {'geojson':'confirmed-case-points.geojson','csv':'confirmed-case-points.csv','filters':'MODIS confidence >=30; VIIRS nominal/high; same UTC date; west/south inclusive, east/north exclusive bounds. Raw source lines retained.'},
        'processing': {'bands':BANDS,'grid':{'crs':'EPSG:4326','width':360,'height':360,'bounds':BOUNDS,'north_up':True,'sampling':'Pixel-aligned 360×360 crop of a 900×900 nearest-neighbour 0.25-degree scene subset (~31 m grid; OLI native optical resolution 30 m).'},
                       'natural_bands':[4,3,2],'swir_bands':[7,6,2],'display':'DN × 0.0000275 − 0.2; divide by 0.45; clip [0,1]; gamma 0.7. Identical fixed per-channel scale for both images. Clouds/haze and saturation retained for inspection; no quantitative reflectance inference over combustion.',
                       'qa_cloud_or_related_fraction':float(((data[5]&63)!=0).mean()),'qa_any_radsat_flag_fraction':float((data[6]!=0).mean()),'qa_swir_saturation_fraction':float(((data[6]&96)!=0).mean()),'qa_note':'QA bits are diagnostics, not a guarantee of smoke-free observation; saturation flags do not measure fire extent.'},
        'provenance': {'protocol':'confirmed-case-protocol.json','protocol_sha256':sha(REPORTS/'confirmed-case-protocol.json'),'search_log':'confirmed-case-search-log.json',
                       'context_bounds':CONTEXT_BOUNDS,'context_array_sha256':hashlib.sha256(context.tobytes()).hexdigest(),'crop_array_sha256':hashlib.sha256(data.tobytes()).hexdigest(),
                       'stac_item_sha256':hashlib.sha256(json.dumps(item,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'band_assets':{b:item['assets'][b]['href'].split('?')[0] for b in BANDS},
                       'firms_archives':sources,'asset_sha256':{name:sha(OUT/name) for name in list(assets.values())+['confirmed-case-points.geojson','confirmed-case-points.csv']},
                       'reproduce':'python pipeline/19_confirmed_case.py --cached (remove --cached to retrieve the pinned public Landsat subset if absent; FIRMS annual archives must already exist)'}
    }
    payload=json.dumps(result,indent=2,allow_nan=False)+'\n'
    for path in [REPORTS/'confirmed-case.json',OUT/'confirmed-case.json']:path.write_text(payload,encoding='utf-8')
    for name in ['confirmed-case-protocol.json','confirmed-case-search-log.json']:(OUT/name).write_bytes((REPORTS/name).read_bytes())
    print(json.dumps({'counts':counts,'nearest_minutes':offsets,'within_60_minutes':len(colocated),'overlay_points':overlay_count,'qa':result['processing']},indent=2))


if __name__ == '__main__':
    main()
