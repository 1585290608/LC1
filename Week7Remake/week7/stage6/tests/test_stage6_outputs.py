import csv
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'outputs'

def test_feeder_sweep_is_completed_not_approved():
    with (OUT/'stage6_grid_limit_sweep_14.csv').open(newline='') as f:r=list(csv.DictReader(f))
    assert len(r)==14
    assert set(x['scenario'] for x in r)=={'central','high'}
    s=lambda scenario,limit:next(x for x in r if x['scenario']==scenario and float(x['grid_import_limit_kw'])==limit)
    assert float(s('central',175)['total_unserved_kwh'])>0
    assert float(s('central',200)['total_unserved_kwh'])<1e-6
    assert float(s('high',200)['total_unserved_kwh'])>0
    assert float(s('high',225)['total_unserved_kwh'])<1e-6

def test_price_sensitivity_does_not_simulate_fictitious_new_physics():
    with (OUT/'stage6_243_tariff_scores.csv').open(newline='') as f:r=list(csv.DictReader(f))
    assert len(r)==243
    assert {float(x['tariff_gbp_per_kwh']) for x in r}=={.168,.24,.312}
    assert all(x['comparison_note'].startswith('Only candidates meeting same service criterion') for x in r)
