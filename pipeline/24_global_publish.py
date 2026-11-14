"""Compile independently evaluated country packages; no country silently omitted."""
import gzip,hashlib,importlib.util,json,math,shutil
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from shapely import contains_xy,get_coordinates
from shapely.geometry import mapping
from global_model import evaluate,category

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data/global';INTERIM=ROOT/'data/interim/global-185'
spec=importlib.util.spec_from_file_location('global_process',ROOT/'pipeline/23_global_process.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
spec=importlib.util.spec_from_file_location('geography_legacy',ROOT/'pipeline/21_geographic_workbench.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def write(path,obj):path.write_bytes((json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode())
def write_gz(path,obj):path.write_bytes(gzip.compress(json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode(),mtime=0))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def combined(aqua,noaa):
 rows={}
 for offset,source in [(0,aqua),(2,noaa)]:
  for r in source:
   key=tuple(r[:5]);values=rows.setdefault(key,[0,0,0,0]);values[offset]+=r[5];values[offset+1]+=r[6]
 return [list(k)+v for k,v in sorted(rows.items())]
def monthly_rows(daily):
 rows={}
 for r in daily:
  k=(r[0],r[1],r[3],r[4]);v=rows.setdefault(k,[0,0,0,0])
  for i,n in enumerate(r[5:]):v[i]+=n
 return [list(k)+v for k,v in sorted(rows.items())]
def map_extent(geom):
 coords=get_coordinates(geom);lng=np.sort(coords[:,0]%360);gaps=np.diff(np.r_[lng,lng[0]+360]);i=int(np.argmax(gaps));start=float(lng[(i+1)%len(lng)]);span=360-float(gaps[i]);start=start-360 if start>180 else start
 return [start,max(-85,float(coords[:,1].min())),start+span,min(85,float(coords[:,1].max()))]
def load_recent():
 receipts=json.loads((ROOT/'reports/month-to-date-sources.json').read_text(encoding='utf-8'));frames={}
 for sensor in ['aqua','noaa20']:
  parts=[]
  for r in receipts:
   if r['sensor']!=sensor:continue
   path=ROOT/'data/raw'/r['file'];assert sha(path)==r['sha256']
   parts.append(pd.read_csv(path,dtype={'acq_time':str,'confidence':str,'version':str}))
  frames[sensor]=legacy.filtered(pd.concat(parts,ignore_index=True),sensor)
 return receipts,frames

def main():
 inventory=json.loads((ROOT/'reports/global-source-inventory.json').read_text(encoding='utf-8'));protocol=json.loads((ROOT/'reports/global-evaluation-protocol.json').read_text(encoding='utf-8'));polygons=gp.boundaries()
 missing=[str(INTERIM/gp.slug(c)/f'{s}-{y}.json.gz') for c in inventory['countries'] for s,ys in [('aqua',range(2003,2026)),('noaa20',range(2019,2026))] for y in ys if not(INTERIM/gp.slug(c)/f'{s}-{y}.json.gz').exists()]
 if missing:raise ValueError(f'Global processing incomplete: {len(missing)} required annual results missing')
 OUT.mkdir(exist_ok=True);receipts,recent_frames=load_recent();catalog=[];features=[];all_sources=[];reconciliation=[]
 for name in inventory['countries']:
  id=gp.slug(name);folder=OUT/id;folder.mkdir(exist_ok=True);geom=polygons[name]['geometry'];sources=[];audits=[];monthly=[];daily_nov=[]
  for year in range(2003,2026):
   pieces={}
   for sensor in ['aqua','noaa20']:
    if sensor=='noaa20' and year<2019:pieces[sensor]=[];continue
    d=json.loads(gzip.decompress((INTERIM/id/f'{sensor}-{year}.json.gz').read_bytes()));sources.append(d['source']);audits.append(dict(d['audit'],filename=d['source']['filename'],sensor=sensor,year=year));pieces[sensor]=d['rows']
   rows=combined(pieces['aqua'],pieces['noaa20']);write_gz(folder/f'days-{year}.json.gz',rows);m=monthly_rows(rows);monthly.extend(m)
   daily_nov.append({'year':year,'aqua':sum(r[6] for r in rows if r[1]==11 and r[2]<=13),'noaa20':sum(r[8] for r in rows if r[1]==11 and r[2]<=13)})
   assert sum(r[5] for r in rows)==sum(r[4] for r in m);assert sum(r[6] for r in rows)==sum(r[5] for r in m);assert sum(r[7] for r in rows)==sum(r[6] for r in m);assert sum(r[8] for r in rows)==sum(r[7] for r in m)
  totals_map={}
  for r in monthly:
   k=(r[0],r[1]);values=totals_map.setdefault(k,[0,0,0,0])
   for i,n in enumerate(r[4:]):values[i]+=n
  totals=[]
  for y in range(2003,2026):
   for m in range(1,13):
    v=totals_map.get((y,m),[0,0,0,0]);totals.append(dict(year=y,month=m,raw_aqua=v[0],aqua=v[1],raw_noaa20=v[2],noaa20=v[3]))
  factors,validation=evaluate(totals,protocol)
  recent_parts=[]
  for sensor,frame in recent_frames.items():
   w,s,e,n=geom.bounds;z=frame[frame.longitude.between(w,e)&frame.latitude.between(s,n)];z=z[contains_xy(geom,z.longitude.to_numpy(),z.latitude.to_numpy())].copy();part,_,_=legacy.aggregate(z,sensor);recent_parts.append(part)
  recent=legacy.combined(recent_parts,True);write_gz(folder/'days-2026.json.gz',recent)
  baseline=[r['aqua'] for r in daily_nov if r['year']<=2017];median=float(np.median(baseline));p90=float(np.quantile(baseline,.9));aqua=sum(r[6] for r in recent);noaa=sum(r[8] for r in recent);f=factors[3]['factor'];adjusted=noaa*f if f is not None else None
  recent_check=dict(start='2026-11-01',end='2026-11-13',aqua=aqua,noaa20=noaa,adjusted=adjusted,median=median,p90=p90,aqua_ratio=aqua/median if median>0 else None,adjusted_ratio=adjusted/median if adjusted is not None and median>0 else None,aqua_category=category(aqua,median,p90),adjusted_category=category(adjusted,median,p90),candidate_only=True)
  bounds=[max(-180,math.floor(geom.bounds[0]*2)/2),max(-86,math.floor(geom.bounds[1]*2)/2),min(180,math.ceil(geom.bounds[2]*2)/2),min(86,math.ceil(geom.bounds[3]*2)/2)]
  # Tiny islands must still receive at least one display cell.
  if bounds[0]==bounds[2]:bounds[2]=min(180,bounds[2]+.5)
  if bounds[1]==bounds[3]:bounds[3]=min(86,bounds[3]+.5)
  limitations=['Aqua is a reference instrument, not a census of fires on the ground.','National screening results do not validate arbitrary subregions.','Thresholds were fixed before this global run; the original three-country results were already known.','The published history uses Aqua only when candidate calibration lacks support or fails agreement checks.','All retained thermal-source types included; detections are not distinct fires or burned area.','Cloud/overpass completeness is unknown; zero detections is not proof of no burning.','Known Aqua outage affects August–September 2020.','Historical and NRT observations use the same mapped polygon; NASA archive border/coast omissions cannot be recovered.','Only November 1–13 is provided for 2026. Recent candidate calibration is not independently validated NRT performance.','Original NASA annual source CSVs are linked directly; the global release does not duplicate every original point into monthly browser shards.']
  package={'schema':'fire-continuum-geography-v2','id':id,'name':name.replace('_',' '),'firms_name':name,'bounds':bounds,'map_bounds':map_extent(geom),'grid_degrees':.5,'years':[2003,2025],'columns':legacy.COLS,'rows':monthly,'factors':factors,'validation':validation,'primary_policy':validation['primary_policy'],'totals':totals,'baseline_years':[2003,2017],'training_years':[2019,2021],'sources':sources,'input_audit':audits,'boundary':polygons[name]['record'],'recent':{'start':'2026-11-01','end':'2026-11-13','rows':recent,'sources':receipts,'national_check':recent_check},'limits':limitations,'protocol_sha256':sha(ROOT/'reports/global-evaluation-protocol.json'),'original_point_shards':False,'daily_shards':True}
  write_gz(folder/'package.json.gz',package);write(folder/'manifest.json',{k:v for k,v in package.items() if k not in ['rows','recent','totals']})
  entry={'id':id,'name':package['name'],'firms_name':name,'bounds':bounds,'map_bounds':package['map_bounds'],'package':id+'/package.json.gz','sha256':sha(folder/'package.json.gz'),'bytes':(folder/'package.json.gz').stat().st_size,'sources':len(sources),'validation':{k:v for k,v in validation.items() if k!='rows'},'primary_policy':validation['primary_policy'],'recent':recent_check}
  catalog.append(entry);features.append({'type':'Feature','properties':{'id':id,'name':package['name'],'status':validation['status']},'geometry':mapping(geom.simplify(.04,preserve_topology=True))});all_sources+=sources
  reconciliation.append({'id':id,'annual_files':len(sources),'raw_aqua':sum(r['raw_aqua'] for r in totals),'raw_noaa20':sum(r['raw_noaa20'] for r in totals),'aqua_cell_days':sum(r['aqua'] for r in totals),'noaa20_cell_days':sum(r['noaa20'] for r in totals),'source_audit_retained':sum(r['retained_detections'] for r in audits),'boundary_or_coordinate_exclusions':sum(r['boundary_or_coordinate_exclusions'] for r in audits),'invalid_time_rows':sum(r['invalid_time_rows'] for r in audits),'package_sha256':entry['sha256']})
  assert reconciliation[-1]['raw_aqua']+reconciliation[-1]['raw_noaa20']==reconciliation[-1]['source_audit_retained']
  print('Published',len(catalog),'/ 185',name,validation['status'],round(validation['wape'],4) if validation['wape'] is not None else None,flush=True)
 legacy_catalog=json.loads((ROOT/'web/public/data/world/catalog.json').read_text(encoding='utf-8'))
 shutil.copyfile(ROOT/'web/public/data/world/global-recent.json.gz',OUT/'global-recent.json.gz')
 status_counts={s:sum(c['validation']['status']==s for c in catalog) for s in protocol['statuses']}
 result={'schema':'fire-continuum-global-catalog-v2','created_utc':datetime.now(timezone.utc).isoformat(),'countries':catalog,'country_count':len(catalog),'annual_source_files':len(all_sources),'status_counts':status_counts,'global_recent':legacy_catalog['global_recent'],'protocol':protocol,'protocol_sha256':sha(ROOT/'reports/global-evaluation-protocol.json'),'coverage_note':'185 eligible NASA country/territory archive labels; this is not every jurisdiction or every land pixel. National coefficients are not globally interchangeable. No summed global anomaly is inferred.'}
 assert len(catalog)==185 and len(all_sources)==5550
 write(OUT/'catalog.json',result);write(OUT/'coverage.geojson',{'type':'FeatureCollection','features':features});write(OUT/'evaluation-protocol.json',protocol)
 write(ROOT/'reports/global-validation.json',result);write(ROOT/'reports/global-source-manifest.json',all_sources);write(ROOT/'reports/global-reconciliation.json',reconciliation)
 print('COMPLETE',status_counts,'public MB',sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())/1e6,flush=True)
if __name__=='__main__':main()
