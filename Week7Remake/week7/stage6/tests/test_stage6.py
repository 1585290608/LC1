"""Stage6 regression gates for provisional annual grid-limited energy model."""
import csv,math,copy
from pathlib import Path
import pytest
from models.core.components import Battery
from week7.stage6.annual_grid import AnnualGridCase,dispatch_step,validate,run_year
from week7.stage6.run_study import calculate_normal_year_cost,financial_proxy
from week7.stage5.preflight import check_inputs

OUT=Path(__file__).resolve().parents[1]/'outputs'

def battery(c):
    return Battery(c.bess_kwh,c.pcs_kw,c.eta_charge,c.eta_discharge,.1,.9,c.reserve_soc,c.initial_soc)

def test_scarcity_priority_critical_before_other():
    c=AnnualGridCase(initial_soc=.3,grid_limit_kw=100)
    r=dispatch_step(c,battery(c),{'c4isr':120.,'aux':30.,'ev':20.},0.,0.,0)
    assert math.isclose(r['c4isr_unserved_kw'],20)
    assert math.isclose(r['aux_unserved_kw'],30)
    assert math.isclose(r['ev_unserved_kw'],20)
    assert math.isclose(r['grid_import_kw'],100)
    assert math.isclose(r['total_unserved_kw'],70)


def test_renewables_charge_avoids_grid_when_not_terminal():
    c=AnnualGridCase(grid_limit_kw=100,grid_export_limit_kw=20)
    b=battery(c)
    r=dispatch_step(c,b,{'c4isr':20.,'aux':0.,'ev':0.},80.,30.,0)
    assert r['grid_import_kw']==0
    assert r['bess_charge_kw']>0
    assert r['battery_soc_final']>r['battery_soc_initial']
    assert r['bess_discharge_kw']==0
    assert abs(r['ac_residual_kwh'])<1e-7


def test_no_battery_discharge_below_reserve():
    c=AnnualGridCase(initial_soc=.3,grid_limit_kw=0.)
    b=battery(c)
    r=dispatch_step(c,b,{'c4isr':25,'aux':0,'ev':0},0,0,0)
    assert r['bess_discharge_kw']==0
    assert b.soc==pytest.approx(.3)
    assert r['c4isr_unserved_kw']==pytest.approx(25)


def test_re_and_grid_served_priority_full():
    c=AnnualGridCase(initial_soc=.3,grid_limit_kw=60)
    r=dispatch_step(c,battery(c),{'c4isr':40,'aux':50,'ev':30},30,0,1)
    assert r['total_served_kw']==pytest.approx(90)
    assert r['c4isr_unserved_kw']==0
    assert r['aux_unserved_kw']==0
    assert r['ev_unserved_kw']==pytest.approx(30)


def test_battery_energy_conservation_and_import_ceiling():
    c=AnnualGridCase(grid_limit_kw=40)
    b=battery(c)
    before=b.soc
    r=dispatch_step(c,b,{'c4isr':50,'aux':10,'ev':15},0,0,0)
    assert r['grid_import_kw']<=40
    assert abs(r['battery_residual_kwh'])<1e-7
    assert b.soc<=before
    assert r['bess_charge_kw']==0


def test_grid_charge_only_terminal_when_service_met():
    c=AnnualGridCase(initial_soc=.5,terminal_target_soc=.7,grid_limit_kw=100)
    b=battery(c)
    before=dispatch_step(c,b,{'c4isr':0.,'aux':0.,'ev':0.},0.,0.,0)
    assert before['grid_to_bess_kw']==0
    last=dispatch_step(c,b,{'c4isr':0.,'aux':0.,'ev':0.},0.,0.,8759)
    assert last['grid_to_bess_kw']>0
    assert last['grid_import_kw']<=100


def test_reject_invalid_component_capacity_and_soc():
    for kw in ({'grid_limit_kw':-1},{'bess_kwh':0},{'eta_charge':0},{'reserve_soc':1.1},
               {'terminal_management_hours':8761},{'scenario':'not-a-scenario'}):
        with pytest.raises(ValueError):validate(AnnualGridCase(**kw))


def test_negative_hourly_solar_or_load_rejected():
    c=AnnualGridCase()
    for l,pv,wind in [({'c4isr':-1,'aux':0,'ev':0},0,0),({'c4isr':0,'aux':0,'ev':0},-1,0)]:
        with pytest.raises(ValueError):dispatch_step(c,battery(c),l,pv,wind,0)


def test_annual_bill_credits_export_exactly_once():
    m={'grid_import_kwh':1000.,'grid_export_kwh':100.}
    x=calculate_normal_year_cost(m,price=.24,export_price=.05,standing_annual=730)
    assert x['annual_grid_bill_gbp']==pytest.approx(965)


def test_cost_proxy_unserved_not_comparable():
    m={'pv_kw':100.,'wind_kw':100.,'bess_kwh':450.,'grid_import_kwh':1000.,'grid_export_kwh':0.,'unserved_load_zero':False}
    x=financial_proxy(m)
    assert x['economic_service_gate']=='FAIL_UNSERVED_LOAD_SO_NOT_A_COMPARABLE_COST'
    assert 'selected_normal_year_cash_PV_gbp_NOT_FULL_NPC' in x


def test_source_preflight_preserved_without_native_claim():
    p=check_inputs()
    assert p['all_internal_preflight_pass']
    assert p['new_native_MDT_runs']==p['new_HOMER_Pro_runs']==0
    assert not p['independent_external_validation']


def test_saved_annual_results_all_have_correct_hour_count_and_physical_ledger():
    with (OUT/'stage6_81_annual_grid_cases.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==81
    assert all(int(r['hours'])==8760 for r in rows)
    assert all(float(r['max_hourly_ac_residual_kwh'])<1e-6 for r in rows)
    assert all(float(r['max_hourly_battery_residual_kwh'])<1e-6 for r in rows)
    assert all(int(r['vehicle_departures_missed'])>=0 for r in rows)
    assert all(r['service_gate'].startswith('FAIL_') or r['service_gate'].startswith('NO_') for r in rows)
    assert all(int(r['hours_any_unserved'])==0 for r in rows if float(r['grid_import_limit_kw'])==250)


def test_grid_limit_and_demand_evidence_not_provenance():
    with (OUT/'stage6_81_annual_grid_cases.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert {float(x['grid_import_limit_kw']) for x in rows}=={100.,150.,250.}
    assert {x['scenario'] for x in rows}=={'low','central','high'}
    assert all(x['evidence_class'].startswith('PROVISIONAL_UNVALIDATED') for x in rows)


def test_traced_hourly_ledgers_reproduce_annual_sum():
    with (OUT/'stage6_base_central_100kw_hourly_trace.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==8760
    total=sum(float(x['total_unserved_kw']) for x in rows)
    grid=sum(float(x['grid_import_kw']) for x in rows)
    assert all(float(x['grid_import_kw'])<=100+1e-7 for x in rows)
    with (OUT/'stage6_81_annual_grid_cases.csv').open(newline='') as f:
        sample=next(x for x in csv.DictReader(f) if x['scenario']=='central' and float(x['grid_import_limit_kw'])==100 and float(x['pv_kw'])==50 and float(x['bess_kwh'])==300)
    assert total==pytest.approx(float(sample['total_unserved_kwh']),abs=1e-6)
    assert grid==pytest.approx(float(sample['grid_import_kwh']),abs=1e-6)
