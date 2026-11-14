"""Common-grid activity and transparent overlap calibration; never infer distinct fires."""
import numpy as np

def fit_ratio(reference, sensor):
    reference,sensor=np.asarray(reference,float),np.asarray(sensor,float)
    if reference.shape!=sensor.shape or not np.isfinite(reference).all() or not np.isfinite(sensor).all():
        raise ValueError('Paired finite training arrays required')
    if (reference<0).any() or (sensor<0).any() or sensor.sum()<=0:
        raise ValueError('Nonnegative counts and nonempty sensor training required')
    return float(reference.sum()/sensor.sum())

def metrics(reference, estimate):
    y,p=np.asarray(reference,float),np.asarray(estimate,float)
    den=float(y.sum())
    return {'months':len(y),'mae':float(np.mean(abs(p-y))),'wape':float(np.sum(abs(p-y))/den) if den else None,
            'relative_bias':float((p-y).sum()/den) if den else None,
            'correlation':float(np.corrcoef(y,p)[0,1]) if len(y)>2 and np.std(y)>0 and np.std(p)>0 else None}

def quarter(month):return (np.asarray(month)-1)//3

def sector(lon):return np.where(np.asarray(lon)<108,0,np.where(np.asarray(lon)<120,1,2))

def primary_sensor(year):return 'aqua' if year<=2012 else ('snpp' if year<=2021 else 'noaa20')
