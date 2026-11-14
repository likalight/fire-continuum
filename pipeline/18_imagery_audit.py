"""Fixed six-cell independent Landsat imagery audit; no practitioner validation."""
import argparse,hashlib,json,logging,math,time,threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import requests
from shapely.geometry import box,shape

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data';RAW=ROOT/'data/raw'
STAC='https://planetarycomputer.microsoft.com/api/stac/v1'
BANDS=['swir22','nir08','red','qa_pixel','qa_radsat'];SIZE=900
logging.getLogger('rasterio').setLevel(logging.CRITICAL)
TOKEN_CACHE={};TOKEN_LOCK=threading.Lock()

def sign_asset(href):
    parsed=urlparse(href);account=parsed.netloc.split('.')[0];container=parsed.path.split('/')[1];key=(account,container)
    with TOKEN_LOCK:
        if key not in TOKEN_CACHE:
            for attempt in range(4):
                r=requests.get(f'https://planetarycomputer.microsoft.com/api/sas/v1/token/{account}/{container}',timeout=45)
                if r.status_code==200:break
                if r.status_code==429 and attempt<3:time.sleep(min(30,max(2,int(r.headers.get('Retry-After','10')))));continue
                raise RuntimeError(f'Public asset access failed: HTTP {r.status_code}')
            TOKEN_CACHE[key]=r.json()['token']
    return href+'?'+TOKEN_CACHE[key]

def select_scenes(items,bounds):
    cell=box(*bounds);selected={}
    for month in ['08','09']:
        candidates=[i for i in items if i['properties']['platform']=='landsat-8' and i['properties']['datetime'][5:7]==month and shape(i['geometry']).intersection(cell).area/cell.area>=.95]
        candidates.sort(key=lambda i:(i['properties']['eo:cloud_cover'],abs(int(i['properties']['datetime'][8:10])-15),i['id']))
        selected[month]=candidates[0] if candidates else None
    return selected

def valid_pixels(data):
    qa=data[3];sat=data[4]
    # Bits 0 through 5: fill, dilated cloud, cirrus, cloud, shadow, snow.
    valid=((qa&63)==0)&(sat==0)&np.all(data[:3]>0,axis=0)
    reflectance=data[:3].astype(np.float32)*.0000275-.2
    valid &= np.all((reflectance>=0)&(reflectance<=1),axis=0)
    return reflectance,valid

def read_band(item,band,bounds):
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.warp import transform_bounds,reproject,Resampling
    from rasterio.windows import Window,from_bounds as window_from_bounds
    href=item['assets'][band]['href']
    signed=sign_asset(href)
    try:
        with rasterio.Env(GDAL_HTTP_TIMEOUT='45',GDAL_HTTP_MAX_RETRY='2',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_LOG='NUL'):
            with rasterio.open(signed) as ds:
                b=transform_bounds('EPSG:4326',ds.crs,*bounds,densify_pts=21);w=window_from_bounds(*b,transform=ds.transform)
                left,top=math.floor(w.col_off),math.floor(w.row_off);right,bottom=math.ceil(w.col_off+w.width),math.ceil(w.row_off+w.height)
                w=Window(left,top,right-left,bottom-top);src=ds.read(1,window=w,boundless=True,fill_value=0)
                out=np.zeros((SIZE,SIZE),np.uint16)
                reproject(src,out,src_transform=ds.window_transform(w),src_crs=ds.crs,dst_transform=from_bounds(*bounds,SIZE,SIZE),dst_crs='EPSG:4326',resampling=Resampling.nearest,src_nodata=0,dst_nodata=0)
        return out
    except Exception as exc:
        # Signed URLs must never enter logs or published records.
        raise RuntimeError('Raster subset failed for '+item['id']+' '+band+' ('+type(exc).__name__+')') from None

def get_chip(item,cell,cached):
    path=RAW/f"imagery-{cell['id']}-{item['id']}.npz"
    if path.exists():
        with np.load(path) as d:data=d['data']
    else:
        if cached:raise ValueError('Pinned imagery subset absent')
        with ThreadPoolExecutor(max_workers=3) as pool:data=np.stack(list(pool.map(lambda b:read_band(item,b,cell['bounds']),BANDS)))
        np.savez_compressed(path,data=data)
    if data.shape!=(5,SIZE,SIZE):raise ValueError('Unexpected chip grid')
    prior=ROOT/'reports/imagery-audit.json'
    if cached and prior.exists():
        previous=json.loads(prior.read_text(encoding='utf-8'));expected=next((scene['subset_array_sha256'] for c in previous['cells'] if c['id']==cell['id'] for scene in c['scenes'] if scene['id']==item['id']),None)
        if expected and hashlib.sha256(data.tobytes()).hexdigest()!=expected:raise ValueError('Pinned subset array hash changed')
    meta={'id':item['id'],'date':item['properties']['datetime'],'scene_cloud_percent':item['properties']['eo:cloud_cover'],'stac_url':STAC+'/collections/landsat-c2-l2/items/'+item['id'],'platform':'landsat-8','instrument':'OLI','collection':'Landsat Collection 2 Level 2','doi':'10.5066/P9OGBGM6','assets':{b:item['assets'][b]['href'].split('?')[0] for b in BANDS},'stac_item_sha256':hashlib.sha256(json.dumps(item,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'subset_array_sha256':hashlib.sha256(data.tobytes()).hexdigest()}
    return data,meta

def render(cell,dates,arrays,valids,delta,paired):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(12,4.3),layout='constrained');extent=[cell['bounds'][0],cell['bounds'][2],cell['bounds'][1],cell['bounds'][3]]
    for ax,a,valid,label in zip(axes[:2],arrays,valids,['Before','During']):
        rgb=np.transpose(np.clip(a/.45,0,1)**.7,(1,2,0));ax.imshow(rgb,extent=extent,origin='upper')
    axes[0].set_title('Before · '+dates[0]);axes[1].set_title('During · '+dates[1])
    masked=np.ma.array(delta,mask=~paired);cmap=plt.get_cmap('RdYlBu_r').copy();cmap.set_bad('#c4c4c4');im=axes[2].imshow(masked,extent=extent,origin='upper',vmin=-.5,vmax=.5,cmap=cmap);axes[2].set_title('NBR decrease · QA-valid paired pixels');fig.colorbar(im,ax=axes[2],label='NBR(before) − NBR(during)',shrink=.75)
    for ax in axes:ax.set_xlabel('Longitude °E');ax.set_ylabel('Latitude °N');ax.tick_params(labelsize=8)
    fig.suptitle(cell['id']+' · '+cell['role']+' · Landsat 8 SWIR2 / NIR / red',fontsize=13)
    fig.text(.5,-.025,'Independent optical context; not active-fire counts. Gray change pixels fail QA/reflectance validity. Full-cell images retain clouds/haze.\nUSGS/NASA Landsat C2 L2 via Microsoft Planetary Computer. Display: reflectance ÷ 0.45, gamma 0.7; no classification is inferred from color alone.',ha='center',fontsize=8)
    path=OUT/f"imagery-{cell['id']}.png";fig.savefig(path,dpi=140,bbox_inches='tight');plt.close(fig)
    return path.name

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cached',action='store_true');args=parser.parse_args()
    protocol=json.loads((ROOT/'reports/imagery_protocol.json').read_text(encoding='utf-8'));catalog=RAW/'imagery-stac.json'
    if not catalog.exists():
        if args.cached:raise ValueError('Pinned STAC response absent')
        r=requests.post(STAC+'/search',json={'collections':['landsat-c2-l2'],'bbox':[112.5,-3.5,115.25,-2],'datetime':'2019-08-01T00:00:00Z/2019-09-30T23:59:59Z','query':{'platform':{'eq':'landsat-8'}},'limit':100},timeout=45);r.raise_for_status();catalog.write_text(json.dumps(r.json()),encoding='utf-8')
    collection=json.loads(catalog.read_text(encoding='utf-8'))
    if any(l.get('rel')=='next' for l in collection.get('links',[])):raise ValueError('Incomplete scene search pagination')
    result={'title':'Six-cell Landsat imagery audit','protocol':'imagery_protocol.json','protocol_sha256':hashlib.sha256((ROOT/'reports/imagery_protocol.json').read_bytes()).hexdigest(),'catalog_sha256':hashlib.sha256(catalog.read_bytes()).hexdigest(),'source':'USGS/NASA Landsat 8 Collection 2 Level 2, public Microsoft Planetary Computer mirror','source_access':'https://planetarycomputer.microsoft.com/docs/','qa_source':'https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands','scale_source':'https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products','processing':{'bands':BANDS,'reflectance_scale':.0000275,'reflectance_offset':-.2,'grid':'900 x 900 EPSG:4326 per exact 0.25-degree cell, nearest-neighbour resampling (about 31 m near equator)','display':'SWIR2/NIR/red reflectance divided by 0.45, clipped 0–1, gamma 0.7. Cloud/haze retained in composites; invalid paired change pixels gray.','validity':'QA_PIXEL bits 0–5 all unset, QA_RADSAT zero, nonzero input, all displayed reflectances within [0,1].','nbr':'(NIR-SWIR2)/(NIR+SWIR2); paired values require positive denominator in both dates. Main change plot/all-valid diagnostics include water; separate land median excludes QA_PIXEL water bit 7 in either date. NBR decrease is not a unique fire signature.','review_gate':'At least 20% paired QA-valid area; engineering threshold only. QA does not guarantee haze-free pixels.'},'cells':[],'limitations':['Small purposive sample, not a representative accuracy estimate.','Comparison cells have lower hotspot activity, not known absence of fire.','Scene-level cloud ranking does not guarantee clear conditions over a cell.','Reflectance QA may miss haze, smoke, and subtle cloud contamination.','Different dates and vegetation/moisture/land-use changes confound NBR changes.','A burn scar cannot establish the timestamp of active burning or validate aggregate hotspot counts.','Agent visual review is non-blinded; external practitioner validation is not conducted.']}
    for cell in protocol['candidates']+protocol['comparisons']:
        selected=select_scenes(collection['features'],cell['bounds']);row={**cell,'scenes':[]};arrays=[];valids=[];dates=[]
        for month in ['08','09']:
            item=selected[month]
            if item is None:break
            data,meta=get_chip(item,cell,args.cached);a,valid=valid_pixels(data);meta['valid_fraction']=float(valid.mean());row['scenes'].append(meta);arrays.append(a);valids.append(valid);dates.append(meta['date'][:10]);print('Read',cell['id'],item['id'],round(valid.mean(),4),flush=True)
        if len(arrays)!=2:row.update(outcome='inconclusive',reason='No eligible scene pair');result['cells'].append(row);continue
        nbrs=[]
        for a,valid in zip(arrays,valids):
            denom=a[1]+a[0];valid &= denom>0;nbrs.append(np.divide(a[1]-a[0],denom,out=np.zeros_like(denom),where=denom>0))
        paired=valids[0]&valids[1];delta=nbrs[0]-nbrs[1];n=int(paired.sum());fraction=float(paired.mean())
        # Paired metrics retain all QA-valid pixels; water-aware follow-up is explicit below.
        before_data=np.load(RAW/f"imagery-{cell['id']}-{selected['08']['id']}.npz")['data'];during_data=np.load(RAW/f"imagery-{cell['id']}-{selected['09']['id']}.npz")['data']
        land=paired&((before_data[3]&128)==0)&((during_data[3]&128)==0)
        row.update(paired_land_fraction=float(land.mean()),nbr_decrease_land_median=float(np.median(delta[land])) if land.any() else None,paired_valid_pixels=n,total_grid_pixels=SIZE*SIZE,paired_valid_fraction=fraction,qa_gate_passed=fraction>=.2,nbr_decrease_median=float(np.median(delta[paired])) if n else None,nbr_decrease_p90=float(np.quantile(delta[paired],.9)) if n else None,fraction_of_valid_pixels_decrease_gt_0_1=float((delta[paired]>.1).mean()) if n else None,preview=render(cell,dates,arrays,valids,delta,paired),outcome='inconclusive',reason='Agent review pending; quantitative NBR change alone is not a fire classification.')
        review_path=ROOT/'reports/imagery_reviews.json'
        if review_path.exists():
            reviews=json.loads(review_path.read_text(encoding='utf-8'));review=reviews.get(cell['id'])
            if review:row.update(review)
        if not row['qa_gate_passed']:row.update(outcome='inconclusive',reason='Paired QA-valid fraction is below the predefined 20% gate. '+row['reason'])
        row['preview_sha256']=hashlib.sha256((OUT/row['preview']).read_bytes()).hexdigest()
        result['cells'].append(row)
    result['outcome_counts']={name:sum(c.get('outcome')==name for c in result['cells']) for name in ['corroborated','contradicted','inconclusive']};text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    for p in [ROOT/'reports/imagery-audit.json',OUT/'imagery-audit.json']:p.write_text(text,encoding='utf-8')
    (OUT/'imagery_protocol.json').write_bytes((ROOT/'reports/imagery_protocol.json').read_bytes())
    print(json.dumps([{'id':c['id'],'paired_fraction':c.get('paired_valid_fraction'),'delta_median':c.get('nbr_decrease_median'),'outcome':c['outcome']} for c in result['cells']],indent=2),flush=True)

if __name__=='__main__':main()
