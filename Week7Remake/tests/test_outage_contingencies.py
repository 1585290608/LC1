from dataclasses import replace
import json,math
import pytest
from models.core.components import Battery,PV,Wind,Loads
from models.core.simulate import DATA, Settings
from models.islanded.fuel_models import ResearchDiesel
from models.islanded.contingencies import Scenario,run,scenarios,should_inhibit_charge
from models.islanded.service_dispatch import instrumented_s3,instrumented_s0
def test_scenario_design_dates_reuse_and_controlled_factors():
    cases=scenarios();assert len(cases)==18 and sum(c.reused for c in cases)==1
    starts={c.start for c in cases if c.groups.startswith('C1')};assert starts=={0,2160,4344,6552}
    for c in cases:
        if 'STRESS' in c.id:assert (c.hours,c.re_scale,c.dg_off_start,c.dg_off_end)==(336,.6,48,72)
def test_exact_ideal_UPS_bookkeeping_is_not_instant_DG_start():
    s=Settings(pcs_kw=0);d=ResearchDiesel().set_fuel_model('MDT_DERIVED');b=Battery(pcs_kw=0);segments=[]
    r,stock=instrumented_s0(PV(0,[0.]),Wind(0,[0.]),Loads([30.],[8.],[0.]),b,d,7.5,0,True,1,s,segments)
    assert r['dg_generated_kw']==0 and r['c4isr_unserved_kw']==22.5 and stock==0
    assert segments[0]['offset_end_h']==.25 and segments[1]['c4isr_unserved_kw']==30
def test_fuel_depletion_guard_keeps_hourly_battery_directions_feasible():
    s=Settings(initial_soc=.1,ups_kw=0,ups_minutes=0,dg_startup_h=0,allow_dg_to_bess=True)
    pv=PV(0,[0.]);wind=Wind(0,[0.]);loads=Loads([15.],[0.],[0.]);b=Battery(soc=.1);d=ResearchDiesel(startup_delay_h=0).set_fuel_model('MDT_DERIVED');d.fuel_l=1;controller={'committed':True,'stop_soc':.6}
    assert should_inhibit_charge(s,b,d,pv,wind,loads,0,controller)
    segments=[];r,_=instrumented_s3(pv,wind,loads,b,d,0,0,True,1,replace(s,allow_dg_to_bess=False),controller,segments)
    assert r['dg_to_bess_kw']==0 and r['dg_fuel_consumed_l']==pytest.approx(1) and r['dg_dumped_kw']>0
    assert r['dg_operating_duration_h']<1 and abs(r['AC_residual_kwh'])<1e-8
def test_no_guard_change_when_fuel_sustains_operation():
    s=Settings(allow_dg_to_bess=True);d=ResearchDiesel().set_fuel_model('MDT_DERIVED');d.running=True
    assert not should_inhibit_charge(s,Battery(soc=.1),d,PV(0,[0.]),Wind(0,[0.]),Loads([15.],[0.],[0.]),0,{'committed':True,'stop_soc':.6})
def test_DG_disabled_retains_fuel_and_cold_restarts():
    d=ResearchDiesel().set_fuel_model('MDT_DERIVED');d.running=True;d.stop();d.enabled=False
    assert d.dispatch(30)==0 and d.fuel_l==2000 and d.state=='DISABLED'
    d.enabled=True;assert d.dispatch(30)==0 and d.last_start_command==1
    assert d.dispatch(30)>0
def test_priority_service_ledger_before_lower_tiers():
    s=Settings(pcs_kw=0,ups_kw=0,ups_minutes=0,dg_kw=40,dg_startup_h=0)
    d=ResearchDiesel(rated_kw=40,startup_delay_h=0).set_fuel_model('FIXED_025');segments=[]
    r,_=instrumented_s0(PV(0,[0.]),Wind(0,[0.]),Loads([30.],[15.],[20.]),Battery(pcs_kw=0),d,0,0,True,1,s,segments)
    assert segments[0]['c4isr_served_kw']==30 and segments[0]['aux_served_kw']==10 and segments[0]['ev_served_kw']==0
def test_profile_scaling_and_availability_do_not_mutate_raw_input():
    from validation.trace_io import sha
    p=DATA/'v6_wind_pu_index_value.csv';before=sha(p)
    c=Scenario('TEST','TEST',hours=2,re_scale=.6,dg_off_start=0,dg_off_end=1)
    rows,segments,cfg=run(c);assert sha(p)==before
    assert rows[0]['DG_available'] is False and rows[0]['dg_generated_kw']==0
    assert cfg['scenario']['re_scale']==.6
