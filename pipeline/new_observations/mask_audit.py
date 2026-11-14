from pathlib import Path
import json,hashlib,gzip
import numpy as np,h5py
from pyhdf.SD import SD,SDC
from common import OUT, ROOT, REPORTS, verify_input
sources=json.loads((OUT/'acquisition.json').read_text(encoding='utf-8'))+json.loads((OUT/'geolocation-acquisition.json').read_text(encoding='utf-8'))
records=[]
for sensor,fireglob,geoglob,time in [('aqua','MYD14*.hdf','MYD03*.hdf','2026-05-01T22:05:00Z'),('noaa20','VJ114*.nc','VJ103IMG*.nc','2026-05-01T20:00:00Z')]:
 fire=next(OUT.glob(fireglob));geo=next(OUT.glob(geoglob));verify_input(fire.name,fire.read_bytes());verify_input(geo.name,geo.read_bytes());all_counts=np.zeros(10,dtype=np.int64);bits=np.zeros(32,dtype=np.int64);qa_values=set();tiles={};native=[]
 if sensor=='aqua':
  f=SD(str(fire),SDC.READ);g=SD(str(geo),SDC.READ);lat=g.select('Latitude').get();lon=g.select('Longitude').get();mask=f.select('fire mask').get();qa=f.select('algorithm QA').get();assert lat.shape==lon.shape==mask.shape==qa.shape;legend=f.select('fire mask').attributes()['legend'];shape=mask.shape
 else:
  f=h5py.File(fire);g=h5py.File(geo);lat=g['geolocation_data/latitude'];lon=g['geolocation_data/longitude'];mask=f['fire mask'];qa=f['algorithm QA'];assert lat.shape==lon.shape==mask.shape==qa.shape;legend=mask.attrs['legend'][0].decode();shape=mask.shape
 for start in range(0,shape[0],256):
  end=min(start+256,shape[0]);la=lat[start:end];lo=lon[start:end];inside=(lo>=-105)&(lo<-103)&(la>=20)&(la<22);m=np.asarray(mask[start:end])[inside].astype(np.uint8);q=np.asarray(qa[start:end])[inside].astype(np.uint32)
  if not len(m):continue
  assert np.isin(m,np.arange(10)).all();all_counts+=np.bincount(m,minlength=10);qa_values.update(np.unique(q).tolist())
  for bit in range(32):bits[bit]+=np.count_nonzero(q&(1<<bit))
  rr,cc=np.where(inside)
  # Native pixel index, lat/lon, mask and complete algorithm QA retained, no reinterpretation.
  native.extend([[int(r+start),int(c),float(a),float(b),int(cl),int(v)] for r,c,a,b,cl,v in zip(rr,cc,la[inside],lo[inside],m,q)])
 payload={'sensor':sensor,'time_start':time,'bounds':[-105,20,-103,22],'columns':['native_row','native_column','latitude','longitude','fire_mask','algorithm_qa'],'rows':native}
 out=OUT/f'{sensor}-mexico-may01-native-pixels.json.gz';out.write_bytes(gzip.compress(json.dumps(payload,separators=(',',':'),allow_nan=False).encode(),mtime=0))
 if sensor=='aqua':f.end();g.end()
 else:f.close();g.close()
 records.append({'sensor':sensor,'time_start':time,'native_swath_shape':list(shape),'native_pixels_inside_bounds':int(all_counts.sum()),'class_counts':all_counts.tolist(),'class_legend':legend,'cloud_pixels':int(all_counts[4]),'clear_nonfire_land_pixels':int(all_counts[5]),'fire_pixels_all_confidences':int(all_counts[7:10].sum()),'fire_pixels_nominal_high':int(all_counts[8:10].sum()),'unprocessed_or_unclassified_pixels':int(all_counts[[0,1,6]].sum()),'sun_glint_pixels':int(all_counts[2]) if sensor=='noaa20' else 0,'obsolete_unprocessed_class2_pixels':int(all_counts[2]) if sensor=='aqua' else 0,'water_pixels':int(all_counts[3]),'qa_bit_set_counts':bits.tolist(),'qa_unique_values':len(qa_values),'qa_interpretation':'Raw complete algorithm-QA values retained per native pixel. Bit positions are not interpreted as a common cross-product coverage score.','native_pixel_archive':out.name,'native_pixel_archive_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_files':[{'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'url':next(x['url'] if 'url' in x else x['links'][0] for x in sources if (x.get('file')==p.name or x.get('id')==p.name))} for p in [fire,geo]]})
report={'schema':'fire-continuum-matched-mask-audit-v1','protocol':'protocol.json','bounds':[-105,20,-103,22],'date':'2026-05-01','status':'full_masks_obtained_but_time_match_failed','time_separation_minutes':125,'declared_maximum_time_separation_minutes':30,'eligible_for_matched_observation_normalization':False,'products':records,'limits':['The predeclared same-date pair is 125 minutes apart and fails the 30-minute timing criterion. No alternate place/date was substituted.','Counts are native pixels from different resolutions and swath footprints, not comparable areas or counts of distinct fires.','Cloud/nonfire/unprocessed partition describes these two individual swaths only, not a whole day or the entire country.','QA is retained but no paired observation denominator or coverage normalization has been estimated.','This is not independent ground truth or validation of the October country totals.'],'guide':'https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf'}
(REPORTS/'matched-mask-audit.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps([{k:v for k,v in x.items() if k in ['sensor','native_pixels_inside_bounds','cloud_pixels','clear_nonfire_land_pixels','fire_pixels_all_confidences','unprocessed_or_unclassified_pixels','water_pixels']} for x in records],indent=2))
