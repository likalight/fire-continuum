"""Decision-level comparisons of frozen harmonization methods. No test-set tuning."""
import csv,gzip,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'web/public/data'
LABELS=['At or below median','Above median','Above historical p90']
METHODS=['raw','common_grid','single_factor','released']

def category(value,median,p90):
    if not np.isfinite([value,median,p90]).all() or min(value,median,p90)<0 or p90<median:raise ValueError('Invalid category inputs')
    return 2 if value>p90 else 1 if value>median else 0

def peak(values):
    a=np.asarray(values,float)
    if len(a)!=12 or not np.isfinite(a).all() or (a<0).any():raise ValueError('Expected twelve nonnegative monthly values')
    if a.sum()==0:return None
    return int(np.argmax([sum(a[(i+j)%12] for j in range(3)) for i in range(12)]))+1

def circular_error(a,b):
    return min(abs(a-b),12-abs(a-b)) if a is not None and b is not None else None

def score(rows,method):
    matrix=np.zeros((3,3),int)
    for r in rows:matrix[r['reference_class'],r['classes'][method]]+=1
    total=int(matrix.sum());recalls=[float(matrix[i,i]/matrix[i].sum()) for i in range(3) if matrix[i].sum()]
    ref=sum(r['aqua'] for r in rows)
    return {'n':total,'agreement':float(np.trace(matrix)/total) if total else None,'balanced_accuracy':float(np.mean(recalls)) if recalls else None,'confusion':matrix.tolist(),'above_p90_precision':float(matrix[2,2]/matrix[:,2].sum()) if matrix[:,2].sum() else None,'above_p90_recall':float(matrix[2,2]/matrix[2].sum()) if matrix[2].sum() else None,'false_above_p90':int(matrix[:2,2].sum()),'missed_above_p90':int(matrix[2,:2].sum()),'wape':float(sum(abs(r['values'][method]-r['aqua']) for r in rows)/ref) if ref else None}

def main():
    protocol=json.loads((ROOT/'reports/decision_benchmark_protocol.json').read_text(encoding='utf-8-sig'))
    raw=(OUT/'history.json.gz').read_bytes();meta=json.loads((OUT/'metadata.json').read_text())
    d=pd.DataFrame(json.loads(gzip.decompress(raw)),columns=['year','month','cx','cy','raw_aqua','raw_snpp','raw_noaa20','aqua','snpp','noaa20'])
    d['lon']=(d.cx+.5)*.25;d['lat']=(d.cy+.5)*.25;d['sector']=np.where(d.lon<108,0,np.where(d.lon<120,1,2));d['quarter']=(d.month-1)//3
    records=[];annual=[];results={}
    for sensor,spec in protocol['sensors'].items():
        fit=d[d.year.between(*spec['fit'])];simple=float(fit.aqua.sum()/fit[sensor].sum())
        factors={(v['sector'],v['quarter']):v['factor'] for v in meta['factors'][sensor]}
        sensor_rows=[];sensor_peaks=[]
        for region,bounds in protocol['regions'].items():
            w,s,e,n=bounds;local=d[d.lon.ge(w)&d.lon.lt(e)&d.lat.ge(s)&d.lat.lt(n)].copy()
            local['released']=local[sensor]*[factors[(s,q)] for s,q in zip(local.sector,local.quarter)]
            index=pd.MultiIndex.from_product([range(2003,2026),range(1,13)],names=['year','month'])
            counts=local.groupby(['year','month'])[['aqua',sensor,'raw_'+sensor,'released']].sum().reindex(index,fill_value=0)
            for year in range(spec['audit'][0],spec['audit'][1]+1):
                year_rows=[]
                for month in range(1,13):
                    if year==2020 and month in [8,9]:continue
                    a=counts.loc[(year,month)];baseline=counts.loc[(slice(2003,2017),month),'aqua'].to_numpy();median=float(np.median(baseline));p90=float(np.quantile(baseline,.9))
                    values={'raw':float(a['raw_'+sensor]),'common_grid':float(a[sensor]),'single_factor':float(a[sensor]*simple),'released':float(a.released)}
                    r={'sensor':sensor,'region':region,'year':year,'month':month,'aqua':int(a.aqua),'viirs':int(a[sensor]),'median':median,'p90':p90,'reference_class':category(a.aqua,median,p90),'values':values,'classes':{k:category(v,median,p90) for k,v in values.items()},'supported':bool(median>=5 and a.aqua>=20 and a[sensor]>=20)}
                    sensor_rows.append(r);year_rows.append(r)
                if len(year_rows)==12:
                    reference=peak([r['aqua'] for r in year_rows]);starts={k:peak([r['values'][k] for r in year_rows]) for k in METHODS}
                    sensor_peaks.append({'sensor':sensor,'region':region,'year':year,'aqua_start':reference,'method_starts':starts,'circular_start_error':{k:circular_error(reference,v) for k,v in starts.items()}})
        gate=[r for r in sensor_rows if r['supported']]
        metrics={}
        for method in METHODS:
            errors=[p['circular_start_error'][method] for p in sensor_peaks if p['circular_start_error'][method] is not None]
            metrics[method]={'all':score(sensor_rows,method),'supported':score(gate,method),'critical_window':{'years':len(errors),'mean_start_error_months':float(np.mean(errors)) if errors else None,'exact_fraction':float(np.mean(np.array(errors)==0)) if errors else None},'regions':{region:score([r for r in sensor_rows if r['region']==region],method) for region in protocol['regions']}}
        results[sensor]={'fit':spec['fit'],'audit':spec['audit'],'single_factor':simple,'evaluated':len(sensor_rows),'retained':len(gate),'withheld':len(sensor_rows)-len(gate),'retained_fraction':len(gate)/len(sensor_rows),'methods':metrics};records.extend(sensor_rows);annual.extend(sensor_peaks)
    report={'title':'Does a seasonal conclusion survive changing satellites?','classes':LABELS,'protocol':'decision_benchmark_protocol.json','source_history_sha256':hashlib.sha256(raw).hexdigest(),'frozen_model_sha256':hashlib.sha256((OUT/'metadata.json').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((ROOT/'reports/decision_benchmark_protocol.json').read_bytes()).hexdigest(),'source_manifest':'sources.json','results':results,'records':records,'annual_windows':annual,'limits':[protocol['sequence'],protocol['gate'],protocol['aggregation'],protocol['comparison']]}
    text=json.dumps(report,indent=2,allow_nan=False)+'\n'
    for path in [ROOT/'reports/decision-benchmark.json',OUT/'decision-benchmark.json']:path.write_text(text,encoding='utf-8')
    (OUT/'decision_benchmark_protocol.json').write_bytes((ROOT/'reports/decision_benchmark_protocol.json').read_bytes())
    with (OUT/'decision-benchmark.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['sensor','region','year','month','aqua','viirs_cell_days','median','p90','aqua_category','supported']+METHODS+[m+'_category' for m in METHODS])
        for r in records:writer.writerow([r['sensor'],r['region'],r['year'],r['month'],r['aqua'],r['viirs'],r['median'],r['p90'],LABELS[r['reference_class']],r['supported']]+[r['values'][m] for m in METHODS]+[LABELS[r['classes'][m]] for m in METHODS])
    print(json.dumps({k:{'evaluated':v['evaluated'],'retained':v['retained'],'models':{m:{'agreement':x['all']['agreement'],'supported':x['supported']['agreement'],'balanced':x['all']['balanced_accuracy'],'peak':x['critical_window']} for m,x in v['methods'].items()}} for k,v in results.items()},indent=2))
if __name__=='__main__':main()
