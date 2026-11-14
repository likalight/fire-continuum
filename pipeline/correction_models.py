"""Finite retrospective candidates. No evaluation-year Aqua enters fitting."""
import numpy as np

def training_mask(rows, first, last):
 return (rows[:,0]>=first)&(rows[:,0]<=last)&~((rows[:,0]==2020)&np.isin(rows[:,1],[8,9]))

def monthly(rows):
 result=np.zeros((276,4),float)
 if len(rows):np.add.at(result,(rows[:,0].astype(int)-2003)*12+rows[:,1].astype(int)-1,rows[:,4:8])
 return result

def weighted_median(values,weights):
 order=np.argsort(values,kind='stable');v=values[order];w=weights[order]
 return float(v[np.searchsorted(np.cumsum(w),w.sum()/2,side='left')])

def fit(rows,kind,first,last,protocol,original):
 totals=monthly(rows);years=2003+np.arange(276)//12;months=np.arange(276)%12+1
 mask=(years>=first)&(years<=last)&~((years==2020)&np.isin(months,[8,9]));q=(months-1)//3
 factors=[];support=[]
 for k in range(4):
  z=totals[mask&(q==k)];a=z[:,1].sum();n=z[:,3].sum();paired=int(((z[:,1]>0)&(z[:,3]>0)).sum());rule=original['training_support']
  ok=a>=rule['minimum_each_instrument_cell_days_per_quarter'] and n>=rule['minimum_each_instrument_cell_days_per_quarter'] and paired>=rule['minimum_paired_nonzero_months_per_quarter']
  factors.append(float(a/n) if ok else None);support.append(dict(aqua=float(a),noaa20=float(n),paired_months=paired,supported=bool(ok)))
 weights=[factors[k//3] for k in range(12)]
 if kind=='annual_ratio':
  z=totals[mask];den=z[:,3].sum();f=float(z[:,1].sum()/den) if den else None;weights=[f if factors[k//3] is not None else None for k in range(12)]
 elif kind=='month_shrink':
  for m in range(1,13):
   if factors[(m-1)//3] is None:continue
   z=totals[mask&(months==m)];quarter=totals[mask&(q==(m-1)//3)];prior=protocol['month_shrink_prior_months']
   weights[m-1]=float((z[:,1].sum()+prior*quarter[:,1].mean())/(z[:,3].sum()+prior*quarter[:,3].mean()))
 elif kind=='robust_quarter':
  for k in range(4):
   z=totals[mask&(q==k)&(totals[:,3]>0)]
   if factors[k] is not None:weights[k*3:k*3+3]=[weighted_median(z[:,1]/z[:,3],z[:,3])]*3
 elif kind not in ['quarter_ratio','spatial_shrink']:raise ValueError(kind)
 model=dict(kind=kind,fit_years=[first,last],weights=weights,support=support)
 if kind=='spatial_shrink':
  z=rows[training_mask(rows,first,last)];keys=((z[:,2].astype(int)+360)*344+z[:,3].astype(int)+172)*4+(z[:,1].astype(int)-1)//3
  keys,inv=np.unique(keys,return_inverse=True);a=np.bincount(inv,weights=z[:,5]);n=np.bincount(inv,weights=z[:,7]);prior=protocol['spatial_shrink_prior_noaa_cell_days']
  national=np.array([factors[int(k)%4] if factors[int(k)%4] is not None else np.nan for k in keys]);model['keys']=keys;model['spatial_factors']=(a+prior*national)/(n+prior)
 return model

def predict(rows,model):
 total=monthly(rows);weights=np.array([np.nan if f is None else f for f in model['weights']]);pred=total[:,3]*np.tile(weights,23)
 if model['kind']=='spatial_shrink':
  keys=((rows[:,2].astype(int)+360)*344+rows[:,3].astype(int)+172)*4+(rows[:,1].astype(int)-1)//3
  trained=model['keys'];idx=np.searchsorted(trained,keys);f=weights[rows[:,1].astype(int)-1].copy();valid=idx<len(trained)
  if len(trained):valid&=trained[np.minimum(idx,len(trained)-1)]==keys
  f[valid]=model['spatial_factors'][idx[valid]]
  pred=np.zeros(276);np.add.at(pred,(rows[:,0].astype(int)-2003)*12+rows[:,1].astype(int)-1,rows[:,7]*f)
  pred[np.tile(np.isnan(weights),23)]=np.nan
 return [float(x) if np.isfinite(x) else None for x in pred]

def classify(v,median,p90):
 return None if v is None or median<=0 else 2 if v>p90 else 1 if v>median else 0

def assess(totals,predictions,first,last,model,original):
 matrix=np.zeros((3,3),int);records=[];a_total=0;absolute=0;signed=0;raw_error=0;complete=True;positive=0;near=0;wrong=0
 for y in range(first,last+1):
  for m in range(1,13):
   i=(y-2003)*12+m-1;a=float(totals[i,1]);n=float(totals[i,3]);v=predictions[i];hist=totals[:180,1].reshape(15,12)[:,m-1];median=float(np.median(hist));p90=float(np.quantile(hist,.9));ac=classify(a,median,p90);vc=classify(v,median,p90)
   a_total+=a;raw_error+=abs(a-n);positive+=median>0
   if v is None:complete=False
   else:absolute+=abs(v-a);signed+=v-a
   if ac is not None and vc is not None:
    matrix[ac,vc]+=1
    if ac!=vc:
     wrong+=1;near+=min(abs(a-median)/max(1,median),abs(a-p90)/max(1,p90))<=.1
   records.append(dict(year=y,month=m,aqua=a,noaa20=n,prediction=v,median=median,p90=p90,aqua_category=ac,predicted_category=vc))
 n=int(matrix.sum());support=matrix.sum(axis=1).tolist();recall=[float(matrix[i,i]/support[i]) if support[i] else None for i in range(3)]
 wape=absolute/a_total if complete and a_total else None;bias=signed/a_total if complete and a_total else None;agreement=float(np.trace(matrix)/n) if n else None;raw_wape=raw_error/a_total if a_total else None
 reasons=[];rule=original['test_support'];checks=original['agreement_checks']
 if not all(x['supported'] for x in model['support']):reasons.append('quarter_support')
 if a_total<rule['minimum_total_aqua_cell_days']:reasons.append('test_count_support')
 if positive<rule['minimum_months_with_positive_historical_median']:reasons.append('baseline_support')
 if reasons:status='insufficient_support'
 else:
  if wape is None or wape>checks['maximum_wape']:reasons.append('wape')
  if bias is None or abs(bias)>checks['maximum_absolute_signed_bias']:reasons.append('signed_bias')
  if agreement is None or agreement<checks['minimum_category_agreement']:reasons.append('category_agreement')
  if wape is None or raw_wape is None or wape>=raw_wape:reasons.append('no_count_improvement')
  if any(s>=5 and recall[i]<checks['minimum_recall_for_each_category_with_at_least_five_reference_months'] for i,s in enumerate(support)):reasons.append('category_recall')
  if reasons:status='mixed_or_poor_agreement'
  elif support[2]<checks['minimum_above_p90_reference_months_for_full_pass']:status='limited_event_evidence'
  else:status='agreement_checks_passed'
 return dict(wape=wape,signed_bias=bias,category_agreement=agreement,raw_wape=raw_wape,category_months=n,category_support=support,category_recall=recall,confusion_matrix=matrix.tolist(),status=status,reasons=reasons,reference_extreme_months=support[2],missed_extreme_months=support[2]-int(matrix[2,2]),misclassified_months=wrong,misclassified_within_10pct_reference_threshold=near,rows=records)

def select(scores,protocol):
 order=protocol['candidates_in_tie_order'];base=scores[order[0]]
 if any(scores[k] is None for k in order):return order[0]
 best=min(order,key=lambda k:scores[k])
 return best if scores[best]<base*(1-protocol['minimum_relative_selection_score_improvement']) else order[0]
