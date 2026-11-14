"""Diagnose all countries and run the predeclared retrospective study."""
import csv,gzip,hashlib,json
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import numpy as np
from correction_models import fit,predict,monthly,assess,select

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'web/public/data/global'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n',encoding='utf-8')
def run():
 protocol=read(ROOT/'reports/correction-study-protocol.json');original=read(ROOT/'reports/global-evaluation-protocol.json');catalog=read(DATA/'catalog.json');out=[];models=protocol['candidates_in_tie_order'];failure_counts=Counter();diagnostics=[]
 for entry in catalog['countries']:
  blob=(DATA/entry['package']).read_bytes();assert hashlib.sha256(blob).hexdigest()==entry['sha256'];p=json.loads(gzip.decompress(blob));rows=np.array(p['rows'],float).reshape(-1,8);totals=monthly(rows);scores={};dev={};trials={}
  for kind in models:
   m=fit(rows,kind,*protocol['selection_fit_years'],protocol,original);pred=predict(rows,m);v=assess(totals,pred,2021,2021,m,original)
   score=v['wape']+1-v['category_agreement'] if v['wape'] is not None and v['category_agreement'] is not None and v['category_months']>=protocol['minimum_development_classifiable_months'] else None
   scores[kind]=score;dev[kind]={k:v[k] for k in ['wape','category_agreement','category_months']};dev[kind]['score']=score
  chosen=select(scores,protocol)
  for kind in models:
   m=fit(rows,kind,*protocol['final_fit_years'],protocol,original);v=assess(totals,predict(rows,m),2022,2025,m,original)
   v['fit_audit']={k:m[k] for k in ['kind','fit_years','weights','support']}
   if kind=='spatial_shrink':v['fit_audit'].update(spatial_coefficients=len(m['keys']),coefficient_sha256=hashlib.sha256(m['keys'].tobytes()+m['spatial_factors'].tobytes()).hexdigest())
   trials[kind]=v
  base=trials['quarter_ratio'];old=p['validation'];assert base['status']==old['status'],entry['id']
  for field in ['wape','category_agreement','signed_bias']:
   assert (base[field] is None and old[field] is None) or abs(base[field]-old[field])<1e-10,(entry['id'],field)
  for reason in base['reasons']:failure_counts[reason]+=1
  diagnostics.append(dict(id=entry['id'],name=entry['name'],status=base['status'],reasons=base['reasons'],wape=base['wape'],category_agreement=base['category_agreement'],category_support=base['category_support'],category_recall=base['category_recall'],misclassified_months=base['misclassified_months'],near_threshold_errors=base['misclassified_within_10pct_reference_threshold'],support=base['fit_audit']['support']))
  out.append(dict(id=entry['id'],name=entry['name'],source_package_sha256=entry['sha256'],original_status=old['status'],selected_model=chosen,development=dev,trials=trials))
  if len(out)%25==0:print('Evaluated',len(out),'/185',flush=True)
 stats={}
 for kind in models+['locked_selector']:
  paired=[];status=Counter();improved=regressed=0;agreements=[];count_better=count_worse=0
  for c in out:
   base=c['trials']['quarter_ratio'];new=c['trials'][c['selected_model'] if kind=='locked_selector' else kind];status[new['status']]+=1
   if base['wape'] is not None and new['wape'] is not None:
    paired.append(base['wape']-new['wape']);count_better+=new['wape']<base['wape']-1e-10;count_worse+=new['wape']>base['wape']+1e-10
   if base['category_agreement'] is not None and new['category_agreement'] is not None:agreements.append(new['category_agreement']-base['category_agreement'])
   accepted=lambda v:v['status'] in ['agreement_checks_passed','limited_event_evidence']
   improved+=not accepted(base) and accepted(new);regressed+=accepted(base) and not accepted(new)
  rng=np.random.default_rng(20261114);d=np.array(paired);boot=np.mean(rng.choice(d,size=(2000,len(d)),replace=True),axis=1)
  stats[kind]=dict(status_counts=dict(status),newly_qualifying=improved,lost_qualifying=regressed,paired_countries=len(d),mean_wape_reduction=float(d.mean()),median_wape_reduction=float(np.median(d)),exploratory_country_bootstrap_mean_reduction_95=np.quantile(boot,[.025,.975]).tolist(),count_error_improved=count_better,count_error_worsened=count_worse,mean_category_agreement_change=float(np.mean(agreements)))
 result=dict(schema='fire-continuum-correction-study-v1',created_utc=datetime.now(timezone.utc).isoformat(),protocol=protocol,protocol_sha256=hashlib.sha256((ROOT/'reports/correction-study-protocol.json').read_bytes()).hexdigest(),original_protocol_sha256=catalog['protocol_sha256'],countries=out,summary=stats,failure_diagnosis=diagnostics,overlapping_failure_counts=dict(failure_counts),selection_counts=dict(Counter(c['selected_model'] for c in out)),limitations=['Retrospective: original evaluation outcomes were already inspected.','Selection uses 2021 only; no test-year winner substitution is allowed.','Aqua is a reference, not ground truth; no additional fire-mask coverage or independent validation is supplied.','Original production policies remain unchanged.','A country bootstrap is exploratory; spatial dependence and repeated model comparisons limit inference.'])
 write(ROOT/'reports/correction-study.json',result)
 payload=json.dumps(result,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode();(ROOT/'web/public/data/correction-study.json.gz').write_bytes(gzip.compress(payload,mtime=0))
 write(ROOT/'web/public/data/correction-study-summary.json',{k:v for k,v in result.items() if k not in ['countries','failure_diagnosis']})
 with (ROOT/'web/public/data/correction-study.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['country','candidate','selected_using_2021','status','wape','category_agreement','signed_bias','rare_months','rare_misses'])
  for c in out:
   for kind,v in c['trials'].items():w.writerow([c['name'],kind,kind==c['selected_model'],v['status'],v['wape'],v['category_agreement'],v['signed_bias'],v['reference_extreme_months'],v['missed_extreme_months']])
 print(json.dumps({'summary':stats,'selection_counts':result['selection_counts']},indent=2),flush=True)
if __name__=='__main__':run()
