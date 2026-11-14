from pathlib import Path
import json,gzip,hashlib,sys,collections
import numpy as np
from common import OUT, ROOT, REPORTS, verify_input;sys.path.insert(0,str(ROOT/'pipeline'))
from correction_models import fit
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
study=read(ROOT/'reports/correction-study.json');protocol=read(ROOT/'reports/correction-study-protocol.json');original=read(ROOT/'reports/global-evaluation-protocol.json');catalog=read(ROOT/'web/public/data/global/catalog.json');countries=[]
for name in ['Mexico','Australia']:
 id=name.lower();p=json.loads(gzip.decompress((ROOT/f'web/public/data/global/{id}/package.json.gz').read_bytes()));new=json.loads(gzip.decompress((OUT/f'{id}-october2026.json.gz').read_bytes()));c=next(x for x in study['countries'] if x['id']==id)
 oldrows=np.array(p['rows'],float);daily=np.array(new['rows'],float).reshape(-1,9);selected=fit(oldrows,c['selected_model'],2019,2021,protocol,original)
 originalfactor=p['factors'][3]['factor'];selectedfactor=selected['weights'][9]
 assert selected['weights']==c['trials'][c['selected_model']]['fit_audit']['weights']
 if c['selected_model']=='spatial_shrink':assert hashlib.sha256(selected['keys'].tobytes()+selected['spatial_factors'].tobytes()).hexdigest()==c['trials'][c['selected_model']]['fit_audit']['coefficient_sha256']
 def prediction(z,model):
  if model=='quarter_ratio':return float(z[:,8].sum()*originalfactor) if originalfactor is not None else None
  if selectedfactor is None:return None
  if c['selected_model']!='spatial_shrink':return float(z[:,8].sum()*selectedfactor)
  lookup=dict(zip(selected['keys'],selected['spatial_factors']));keys=((z[:,3].astype(int)+360)*344+z[:,4].astype(int)+172)*4+3
  return float(sum(n*lookup.get(k,selectedfactor) for n,k in zip(z[:,8],keys)))
 history=[t['aqua'] for t in p['totals'] if t['month']==10 and 2003<=t['year']<=2017];median=float(np.median(history));p90=float(np.quantile(history,.9));category=lambda v:None if v is None or median<=0 else 'above_p90' if v>p90 else 'above_median' if v>median else 'at_or_below_median'
 days=[]
 for day in range(1,32):
  z=daily[daily[:,2]==day];days.append({'date':f'2026-10-{day:02d}','aqua_status':'source_available','noaa20_status':'source_available','aqua_raw':int(z[:,5].sum()),'aqua_cell_days':int(z[:,6].sum()),'noaa20_raw':int(z[:,7].sum()),'noaa20_cell_days':int(z[:,8].sum()),'quarter_prediction':prediction(z,'quarter_ratio'),'selected_prediction':prediction(z,'selected'),'observation_coverage':'unknown'})
 aqua=sum(x['aqua_cell_days'] for x in days);noaa=sum(x['noaa20_cell_days'] for x in days);models={}
 for key,col in [('original_quarter','quarter_prediction'),('preselected','selected_prediction')]:
  est=sum(x[col] for x in days) if all(x[col] is not None for x in days) else None
  models[key]={'kind':'quarter_ratio' if key=='original_quarter' else c['selected_model'],'prediction':est,'period_absolute_relative_difference':abs(est-aqua)/aqua if est is not None and aqua>0 else None,'signed_relative_difference':(est-aqua)/aqua if est is not None and aqua>0 else None,'daily_wape':sum(abs(x[col]-x['aqua_cell_days']) for x in days)/aqua if est is not None and aqua>0 else None,'category':category(est),'same_category_as_aqua':category(est)==category(aqua) if median>0 and est is not None else None}
 # The new reference values cannot enter predictions: perturb all Aqua columns.
 perturbed=daily.copy();perturbed[:,5:7]*=999;assert prediction(perturbed,'selected')==prediction(daily,'selected')
 countries.append({'id':id,'name':name,'start':'2026-10-01','end':'2026-10-31','baseline':{'years':[2003,2017],'same_month':10,'median':median,'p90':p90,'aqua_october_counts':history},'aqua':aqua,'noaa20':noaa,'aqua_category':category(aqua),'aqua_ratio':aqua/median if median>0 else None,'models':models,'days':days,'input_audit':new['audit'],'source_package_sha256':hashlib.sha256((ROOT/f'web/public/data/global/{id}/package.json.gz').read_bytes()).hexdigest(),'original_primary_policy':p['primary_policy'],'selected_in_2021':c['selected_model'],'sources':new['sources']})
report={'schema':'fire-continuum-october-transfer-v1','protocol':read(OUT/'october-transfer-protocol.json'),'protocol_sha256':hashlib.sha256((OUT/'october-transfer-protocol.json').read_bytes()).hexdigest(),'original_correction_study_protocol_sha256':study['protocol_sha256'],'countries':countries,'limits':['One October cannot establish year-round accuracy, category recall, or a national full pass.','These are newly inspected observations for frozen models, not blind validation of the complete development process.','NRT versus science-archive processing differs. Aqua is a reference, not independent ground truth.','January-August 2026 remain unavailable through checked daily and yearly country routes.','All 31 daily source files per sensor are present; actual cloud-free overpass completeness remains unknown.'],'availability_audit':{'checked_country_archive':'https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt','annual_2026_files_advertised':0,'nrt_directory_start':'2026-09-15','nrt_directory_end':'2026-11-14','complete_month_selected':'October 2026','countries_processed':['Mexico','Australia']}}
(REPORTS/'october-transfer.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps([{k:v for k,v in c.items() if k in ['name','aqua','noaa20','aqua_category','models']} for c in countries],indent=2))
