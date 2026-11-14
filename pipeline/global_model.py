"""Predeclared global calibration screens; Aqua is a reference, not ground truth."""
import numpy as np

def category(value,median,p90):
 if value is None or median is None or median<=0:return None
 return 2 if value>p90 else 1 if value>median else 0

def evaluate(monthly,protocol):
 factors=[]
 for q in range(4):
  fit=[r for r in monthly if 2019<=r['year']<=2021 and (r['month']-1)//3==q and not(r['year']==2020 and r['month'] in [8,9])]
  aqua=sum(r['aqua'] for r in fit);noaa=sum(r['noaa20'] for r in fit)
  paired=sum(r['aqua']>0 and r['noaa20']>0 for r in fit)
  rule=protocol['training_support'];supported=aqua>=rule['minimum_each_instrument_cell_days_per_quarter'] and noaa>=rule['minimum_each_instrument_cell_days_per_quarter'] and paired>=rule['minimum_paired_nonzero_months_per_quarter']
  factors.append(dict(quarter=q,factor=float(aqua/noaa) if supported else None,aqua=aqua,noaa20=noaa,paired_months=paired,training_months=len(fit),supported=supported))
 test=[];matrix=np.zeros((3,3),dtype=int);raw_matrix=np.zeros((3,3),dtype=int)
 for r in monthly:
  factor=factors[(r['month']-1)//3]['factor']
  r['adjusted']=r['noaa20']*factor if r['year']>=2019 and factor is not None else None
  if r['year']<2022:continue
  hist=[a['aqua'] for a in monthly if a['year']<=2017 and a['month']==r['month']]
  median=float(np.median(hist));p90=float(np.quantile(hist,.9));ac=category(r['aqua'],median,p90);vc=category(r['adjusted'],median,p90);rc=category(r['noaa20'],median,p90)
  if ac is not None and vc is not None:matrix[ac,vc]+=1
  if ac is not None and rc is not None:raw_matrix[ac,rc]+=1
  test.append(dict(r,median=median,p90=p90,aqua_category=ac,adjusted_category=vc))
 total=sum(r['aqua'] for r in test);complete=all(f['supported'] for f in factors)
 wape=sum(abs(r['aqua']-r['adjusted']) for r in test)/total if complete and total>0 else None
 raw_wape=sum(abs(r['aqua']-r['noaa20']) for r in test)/total if total>0 else None
 bias=sum(r['adjusted']-r['aqua'] for r in test)/total if complete and total>0 else None
 n=int(matrix.sum());agreement=float(np.trace(matrix)/n) if n else None
 class_n=matrix.sum(axis=1);recall=[float(matrix[i,i]/class_n[i]) if class_n[i]>0 else None for i in range(3)]
 supported_months=sum(r['median']>0 for r in test)
 test_rule=protocol['test_support'];checks=protocol['agreement_checks'];reasons=[]
 if not complete:reasons.append('At least one quarter lacks the predeclared overlap support.')
 if total<test_rule['minimum_total_aqua_cell_days']:reasons.append('Too few Aqua cell-days in excluded test years.')
 if supported_months<test_rule['minimum_months_with_positive_historical_median']:reasons.append('Too few test months have a positive historical median.')
 if reasons:status='insufficient_support'
 else:
  if wape>checks['maximum_wape']:reasons.append('Count disagreement exceeds 25%.')
  if abs(bias)>checks['maximum_absolute_signed_bias']:reasons.append('Absolute aggregate signed bias exceeds 15%.')
  if agreement<checks['minimum_category_agreement']:reasons.append('Category agreement is below 80%.')
  if wape>=raw_wape:reasons.append('Calibration does not improve count disagreement over unadjusted cell-days.')
  if any(class_n[i]>=5 and recall[i]<.7 for i in range(3)):reasons.append('Recall is below 70% for a category with at least five reference months.')
  if reasons:status='mixed_or_poor_agreement'
  elif class_n[2]<5:status='limited_event_evidence';reasons.append('Fewer than five Aqua above-p90 test months; rare-category performance is not established.')
  else:status='agreement_checks_passed';reasons.append('All predeclared national agreement checks passed; this is not ground-truth or operational validation.')
 primary='aqua_only' if status in ['insufficient_support','mixed_or_poor_agreement'] else 'aqua_then_adjusted_noaa20'
 annual=[]
 for y in range(2022,2026):
  rr=[r for r in test if r['year']==y];den=sum(r['aqua'] for r in rr)
  annual.append({'year':y,'wape':sum(abs(r['adjusted']-r['aqua']) for r in rr)/den if complete and den else None})
 return factors,dict(years=[2022,2025],months=48,wape=wape,unadjusted_wape=raw_wape,signed_bias=bias,category_agreement=agreement,category_months=n,positive_baseline_months=supported_months,total_aqua_cell_days=total,confusion_matrix=matrix.tolist(),unadjusted_confusion_matrix=raw_matrix.tolist(),category_support=class_n.tolist(),category_recall=recall,reference_extreme_months=int(class_n[2]),missed_extreme_months=int(class_n[2]-matrix[2,2]),status=status,reasons=reasons,primary_policy=primary,annual=annual,rows=test)
