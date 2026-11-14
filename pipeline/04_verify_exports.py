"""Independently reconcile browser exports to the pipeline's monthly ledger."""
import gzip,json,csv,io
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'web/public/data'
rows=pd.DataFrame(json.loads(gzip.decompress((out/'history.json.gz').read_bytes())),columns=['year','month','cx','cy','raw_aqua','raw_snpp','raw_noaa20','active_aqua','active_snpp','active_noaa20'])
rows['sector']=np.where((rows.cx+.5)*.25<108,0,np.where((rows.cx+.5)*.25<120,1,2))
ledger=pd.read_csv(ROOT/'reports/monthly_counts.csv')
meta=json.loads((out/'metadata.json').read_text())
checked=0
for sensor in ['aqua','snpp','noaa20']:
    sums=rows.groupby(['year','month','sector'])[[f'raw_{sensor}',f'active_{sensor}']].sum()
    for r in ledger[ledger.sensor==sensor].itertuples():
        values=sums.loc[(r.year,r.month,r.sector)] if (r.year,r.month,r.sector) in sums.index else [0,0]
        assert list(values)==[r.raw,r.active],(sensor,r.year,r.month,r.sector)
        checked+=1
validation={}
ablation={}
for sensor in ['snpp','noaa20']:
    spec=meta['validation'][sensor];a,b=spec['test_years'];sub=rows[rows.year.between(a,b)].copy()
    lookup={(f['sector'],f['quarter']):f['factor'] for f in meta['factors'][sensor]}
    sub['estimate']=sub[f'active_{sensor}']*[lookup[(s,(m-1)//3)] for s,m in zip(sub.sector,sub.month)]
    totals=sub.groupby(['year','month'])[['active_aqua','estimate']].sum()
    wape=float((totals.estimate-totals.active_aqua).abs().sum()/totals.active_aqua.sum())
    assert abs(wape-spec['national_after']['wape'])<1e-12
    validation[sensor]=wape
    training=rows[rows.year.between(*spec['train_years'])]
    simple_factor=float(training.active_aqua.sum()/training[f'active_{sensor}'].sum())
    simple=sub.groupby(['year','month'])[['active_aqua',f'active_{sensor}']].sum()
    simple_wape=float((simple[f'active_{sensor}']*simple_factor-simple.active_aqua).abs().sum()/simple.active_aqua.sum())
    ablation[sensor]={'single_factor':simple_factor,'single_factor_held_out_wape':simple_wape}
downloads=0
for file in sorted((out/'detections').glob('*.csv.gz')):
    year,month=map(int,file.name.split('.')[0].split('-'))
    sensor='aqua' if year<=2012 else 'snpp' if year<=2021 else 'noaa20'
    records=list(csv.DictReader(io.StringIO(gzip.decompress(file.read_bytes()).decode())))
    expected=int(ledger[(ledger.year==year)&(ledger.month==month)&(ledger.sensor==sensor)].raw.sum())
    assert len(records)==expected,(file.name,len(records),expected)
    assert all(r['acq_date'].startswith(f'{year}-{month:02}') for r in records)
    downloads+=1
result={'ledger_rows_reconciled':checked,'monthly_point_downloads_reconciled':downloads,'export_recomputed_held_out_wape':validation,'status':'passed'}
(ROOT/'reports/export_verification.json').write_text(json.dumps(result,indent=2))
(ROOT/'reports/ablation.json').write_text(json.dumps(ablation,indent=2))
(out/'ablation.json').write_text(json.dumps(ablation,indent=2))
print(json.dumps(result,indent=2))
