import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from harmonize import fit_ratio,metrics,primary_sensor,sector,quarter

def test_scale_fitted_on_training_only_and_preserves_zero():
 reference=np.array([1,4,10]);sensor=reference*5
 factor=fit_ratio(reference,sensor)
 assert factor==pytest.approx(.2)
 assert 0*factor==0
 assert 50*factor==pytest.approx(10)
 # A later observation cannot alter a frozen fit.
 later=np.array([5000]);assert factor==fit_ratio(reference,sensor)

def test_metrics_reference_denominator_not_prediction():
 assert metrics([10,20],[20,40])['wape']==pytest.approx(1)
 assert metrics([0,0],[3,4])['wape'] is None

def test_invalid_training_is_rejected():
 for a,b in [([1],[0]),([-1],[2]),([np.nan],[2]),([1,2],[3])]:
  with pytest.raises(ValueError):fit_ratio(a,b)

def test_sensor_handover_never_sums_platforms():
 assert [primary_sensor(y) for y in [2003,2012,2013,2021,2022,2025]]==['aqua','aqua','snpp','snpp','noaa20','noaa20']

def test_sector_and_season_boundaries():
 np.testing.assert_array_equal(sector([107.999,108,119.999,120]),[0,1,1,2])
 np.testing.assert_array_equal(quarter([1,3,4,6,7,9,10,12]),[0,0,1,1,2,2,3,3])
