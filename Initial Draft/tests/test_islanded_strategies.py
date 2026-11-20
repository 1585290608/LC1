import json
from dataclasses import replace,asdict
import pytest
from models.islanded.fuel_models import FixedFuel,NativeFuel,ResearchDiesel,UnsupportedFuelDomain
from models.core.components import PV,Wind,Loads
from models.core.simulate import Settings,InfeasibleOperatingPoint
from models.islanded.strategies import run_case
from validation.trace_io import write
from validation.independent_energy_checks import check

def synthetic(load=15,hours=3):return PV(0,[0.]*hours),Wind(0,[0.]*hours),Loads([float(load)]*hours,[0.]*hours,[0.]*hours)
def settings(**kw):return replace(Settings(pv_kw=0,wind_kw=0,initial_soc=.1,ups_kw=0,ups_minutes=0,dg_startup_h=0),**kw)

@pytest.mark.parametrize('p,sfc',[(25,.104),(50,.082),(75,.077),(100,.074),(37.5,.093)])
def test_native_specific_curve_with_correct_units(p,sfc):
    assert NativeFuel().rate_lph(p)==pytest.approx(p*sfc*3.785411784)

def test_idle_point_not_interpolated_as_specific_consumption():
    n=NativeFuel();assert n.rate_lph(0)==0
    with pytest.raises(UnsupportedFuelDomain):n.rate_lph(10)
    assert n.definition['stored_values'][0]==.1095

def test_partial_timestep_fuel_uses_on_power_not_average():
    d=ResearchDiesel(100,.25,.25,1,0).set_fuel_model('MDT_DERIVED')
    generated=d.dispatch(15,1)
    assert d.fuel_used_l==pytest.approx(1)
    assert d.operating_duration_h==pytest.approx(1/(25*.104*3.785411784))
    assert generated==pytest.approx(25*d.operating_duration_h)
    with pytest.raises(UnsupportedFuelDomain):NativeFuel().rate_lph(generated)

@pytest.mark.parametrize('strategy',['S0','S1','S2','S3'])
def test_all_dispatch_modes_saved_balance_and_limits(tmp_path,strategy):
    rows,s=run_case(strategy,'MDT_DERIVED',3,settings=settings(),models=synthetic())
    p=tmp_path/'trace.csv';write(p,rows);a=check(p,s,'MDT_DERIVED')
    assert a['status']=='PASS'
    assert all(r['c4isr_unserved_kw']==pytest.approx(0) for r in rows)
    if strategy in ('S1','S3'):assert sum(r['dg_to_bess_kw'] for r in rows)>0
    else:assert sum(r['dg_to_bess_kw'] for r in rows)==0

def test_soc_and_pcs_limit_surplus_recovery():
    rows,s=run_case('S3','FIXED_025',1,settings=settings(initial_soc=.8999,soc_reserve=.8999,pcs_kw=2),models=synthetic())
    r=rows[0];assert r['bess_charge_kw']<=2;assert r['soc_final']<=.9+1e-12
    assert r['dg_dumped_kw']>9

def test_critical_priority_and_startup_energy_are_not_overridden():
    models=PV(0,[0.]*2),Wind(0,[0.]*2),Loads([30.]*2,[20.]*2,[10.]*2)
    rows,_=run_case('S2','FIXED_025',2,settings=settings(pcs_kw=0,dg_startup_h=1),models=models)
    assert rows[0]['c4isr_unserved_kw']==30
    assert rows[0]['dg_generated_kw']==0
    assert rows[1]['c4isr_served_kw']==30
    # Rated output limitation preserves C4 before lower tiers.
    rows,_=run_case('S3','FIXED_025',2,settings=settings(pcs_kw=0,dg_startup_h=0,dg_kw=40),models=models)
    assert rows[0]['c4isr_served_kw']==30 and rows[0]['aux_served_kw']==10 and rows[0]['ev_served_kw']==0

def test_zero_demand_shutdown_no_invented_minimum_runtime():
    m=PV(0,[0.]*3),Wind(0,[0.]*3),Loads([15.,0.,15.],[0.]*3,[0.]*3)
    rows,_=run_case('S2','FIXED_025',3,settings=settings(),models=m)
    assert [r['dg_start_command'] for r in rows]==[1,0,1]
    assert rows[1]['dg_generated_kw']==0

def test_no_automatic_sink_upsizing():
    with pytest.raises(InfeasibleOperatingPoint):run_case('S0','FIXED_025',1,settings=settings(pcs_kw=0,dg_min_fraction=.5),models=synthetic())

def test_closed_loop_fuel_exhaustion_changes_service():
    s=settings(pcs_kw=0,dg_startup_h=1)
    fixed,_=run_case('S0','FIXED_025',24,settings=s,models=synthetic(30,24),initial_fuel=100)
    native,_=run_case('S0','MDT_DERIVED',24,settings=s,models=synthetic(30,24),initial_fuel=100)
    assert sum(r['dg_fuel_consumed_l'] for r in fixed)==pytest.approx(100)
    assert sum(r['dg_fuel_consumed_l'] for r in native)==pytest.approx(100)
    assert sum(r['c4isr_unserved_kw'] for r in native)>sum(r['c4isr_unserved_kw'] for r in fixed)

def test_frozen_core_unchanged_and_s0_exact(baseline_core_verified):
    from models.core.simulate import run
    old=run([{'start':0,'duration':24}],24)
    new,_=run_case('S0','FIXED_025',24)
    for a,b in zip(old,new):
        for k in a:assert a[k]==b[k]

def test_independent_checks_reject_tampered_destination(tmp_path):
    rows,s=run_case('S3','FIXED_025',3,settings=settings(),models=synthetic())
    rows[0]['dg_dumped_kw']+=1
    p=tmp_path/'bad.csv';write(p,rows)
    with pytest.raises(AssertionError):check(p,s,'FIXED_025')
