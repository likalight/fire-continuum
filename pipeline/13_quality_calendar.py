"""Full native FireMask and QA subsets for the fixed historical decision case."""
import argparse, base64, csv, gzip, hashlib, json, re
from datetime import date, datetime, timedelta, timezone
from importlib import import_module
from pathlib import Path
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'web/public/data'
mask_tools=import_module('12_observation_context')

def qa_counts(values):
    a=np.asarray(values)
    if not a.size or np.any(a<0) or np.any(a>6) or np.any(a!=np.floor(a)):
        raise ValueError('Unexpected daily QA value')
    a=a.astype(np.uint8)
    return {'values':np.bincount(a.ravel(),minlength=7).tolist(),
            'land_water':np.bincount((a&3).ravel(),minlength=4).tolist(),
            'representative_day_night':[int(((a&4)==0).sum()),int(((a&4)!=0).sum())]}

def layer_dates(attrs, count):
    days=attrs.get('Dates','').split()
    if len(days)!=count or len(set(days))!=count: raise ValueError('Missing or inconsistent layer Dates')
    for day in days:
        date.fromisoformat(day)
        if not attrs['StartDate']<=day<=attrs['EndDate']: raise ValueError('Layer outside granule period')
    if days!=sorted(days): raise ValueError('Unordered layer Dates')
    return days

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cached',action='store_true');args=parser.parse_args()
    from pyhdf.SD import SD,SDC
    config=json.loads((ROOT/'reports/decision_protocol.json').read_text(encoding='utf-8'))['quality']
    prior=json.loads((ROOT/'reports/quality-calendar.json').read_text()) if args.cached else None
    session=requests.Session();session.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=[429,500,502,503,504],allowed_methods=['GET'])));sources=[];days=[];pixels=[];grid=None;native_mask=None
    for start,end in config['periods']:
        if prior:entries=[s for s in prior['sources'] if s['period_start']==start]
        else:
            r=session.get('https://cmr.earthdata.nasa.gov/search/granules.json',params={'short_name':'MYD14A1','version':'061','temporal':f'{start}T00:00:00Z,{end}T23:59:59Z','bounding_box':','.join(map(str,config['bounds'])),'page_size':100},timeout=45);r.raise_for_status()
            entries=[{'granule':g['producer_granule_id'],'cmr_id':g['id'],'period_start':start,'url':next(l['href'] for l in g['links'] if l.get('rel','').endswith('/data#') and l['href'].endswith('.hdf'))} for g in r.json()['feed']['entry'] if '.h29v09.' in g['producer_granule_id']]
        if not entries:raise ValueError('No matching daily products')
        for src in entries:
            path=ROOT/'data/raw'/(src['granule']+'.hdf')
            if not path.exists():
                if args.cached:raise ValueError('Pinned input unavailable')
                r=session.get(src['url'],timeout=(20,60))
                if r.status_code!=200 or r.content[:4]!=b'\x0e\x03\x13\x01':raise RuntimeError(f'NASA access failed: HTTP {r.status_code}; response not logged')
                path.write_bytes(r.content)
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            if prior and digest!=src['sha256']:raise ValueError('Input hash changed')
            src.update(sha256=digest,bytes=path.stat().st_size);src.setdefault('retrieved_utc',datetime.now(timezone.utc).isoformat());sources.append(src)
            f=SD(str(path),SDC.READ);attrs=f.attributes();mask=f.select('FireMask').get();qa=f.select('QA').get()
            if mask.shape!=qa.shape:raise ValueError('QA and mask grids differ')
            sample=mask_tools.grid_mask(attrs['StructMetadata.0'],mask.shape[1:],config['bounds'])
            if native_mask is not None and not np.array_equal(native_mask,sample):raise ValueError('Native grid changed')
            native_mask=sample;rr,cc=np.where(sample);r0,r1,c0,c1=rr.min(),rr.max()+1,cc.min(),cc.max()+1
            if grid is None:
                structure=attrs['StructMetadata.0']
                pair=lambda n:[float(v) for v in re.search(n+r'=\(([^,]+),([^\)]+)\)',structure).groups()]
                left,top=pair('UpperLeftPointMtrs');right,bottom=pair('LowerRightMtrs')
                grid={'width':int(c1-c0),'height':int(r1-r0),'left':left+c0*(right-left)/1200,'top':top+r0*(bottom-top)/1200,'dx':(right-left)/1200,'dy':(bottom-top)/1200,'radius':6371007.181,'outside_value':255,'cells':int(sample.sum())}
            src['layer_dates']=layer_dates(attrs,mask.shape[0])
            for i,day in enumerate(src['layer_dates']):
                if not start<=day<=end:continue
                counts=mask_tools.partition(mask[i][sample]);quality=qa_counts(qa[i][sample]);days.append({'date':day,'status':'available','counts':counts,'qa':quality,'total_cells':grid['cells'],'granule':src['granule']})
                m=mask[i,r0:r1,c0:c1].copy();q=qa[i,r0:r1,c0:c1].copy();m[~sample[r0:r1,c0:c1]]=255;q[~sample[r0:r1,c0:c1]]=255
                pixels.append({'date':day,'mask':base64.b64encode(m.tobytes()).decode(),'qa':base64.b64encode(q.tobytes()).decode()})
            f.end();print('Read',src['granule'],flush=True)
    expected={str(date.fromisoformat(s)+timedelta(days=i)) for s,e in config['periods'] for i in range((date.fromisoformat(e)-date.fromisoformat(s)).days+1)}
    if len({d['date'] for d in days})!=len(days):raise ValueError('Duplicate dates')
    missing=sorted(expected-{d['date'] for d in days})
    for day in missing:days.append({'date':day,'status':'no_product','counts':None,'qa':None,'total_cells':grid['cells'],'granule':None})
    days.sort(key=lambda d:d['date']);pixels.sort(key=lambda d:d['date'])
    result={'available_days':len(pixels),'missing_dates':missing,'outage_source':'https://landweb.modaps.eosdis.nasa.gov/displayissue?id=262','date_mapping':'HDF Dates attribute per slice; never StartDate plus slice number.','product':config['product'],'bounds':config['bounds'],'classes':mask_tools.LABELS,'sources':sources,'grid':grid,'days':days,'specification':mask_tools.SPEC,'limits':['Daily composites do not measure clear-sky overpass exposure.','QA day/night describes the representative composite classification, not all observations.','Full native masks retained only for this fixed local case, not all Indonesia.','No coverage normalization or correction to the current 46.8% discrepancy.']}
    text=json.dumps(result,indent=2)+'\n'
    for path in [ROOT/'reports/quality-calendar.json',OUT/'quality-calendar.json']:path.write_text(text)
    compressed=gzip.compress(json.dumps({'grid':grid,'days':pixels},separators=(',',':')).encode(),mtime=0)
    (OUT/'quality-pixels.json.gz').write_bytes(compressed)
    with (OUT/'quality-calendar.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['date','status','total_cells']+mask_tools.LABELS+['qa_water','qa_coast','qa_land','qa_missing','qa_representative_night','qa_representative_day','granule'])
        for d in days:writer.writerow([d['date'],d['status'],d['total_cells']]+(d['counts']+d['qa']['land_water']+d['qa']['representative_day_night'] if d['counts'] is not None else ['']*16)+[d['granule']])
    print(json.dumps({'days':len(days),'sources':len(sources),'cells':grid['cells'],'pixel_archive_bytes':len(compressed)}))

if __name__=='__main__':main()
