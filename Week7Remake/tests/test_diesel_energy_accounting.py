import math
import pytest
from dataclasses import replace
from models.core.components import Diesel,Battery,PV,Wind,Loads
from models.core.simulate import Settings,step,run,event_metrics,InfeasibleOperatingPoint
def fixture(c4=15,aux=0,ev=0,renewable=0,soc=.1,running=True,**changes):
    s=replace(Settings(ups_kw=0.,ups_minutes=0.),**changes)
    pv=PV(renewable,[1.]*8760);wind=Wind(0.,[0.]*8760);loads=Loads([float(c4)]*8760,[float(aux)]*8760,[float(ev)]*8760)
    b=Battery(s.energy_kwh if hasattr(s,'energy_kwh') else s.battery_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,soc)
    d=Diesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,s.dg_enabled);d.running=running
    return s,pv,wind,loads,b,d
def tick(f,dt=1,ups=0,island=True):
    s,pv,w,l,b,d=f;return step(pv,w,l,b,d,ups,0,island,dt,s)
def test_A_minimum_generated_not_overwritten_by_delivered():
    f=fixture();r,_=tick(f)
    assert (r['dg_generated_kw'],r['dg_delivered_kw'],r['dg_dumped_kw'])==pytest.approx((25,15,10))
    assert r['dg_fuel_consumed_l']==pytest.approx(6.25)
    assert r['DG_destination_residual_kwh']==pytest.approx(0,abs=1e-9)
def test_B_full_load_limit():
    r,_=tick(fixture(c4=150));assert r['dg_generated_kw']==100;assert r['c4isr_unserved_kw']==50
def test_C_partial_final_fuel_preserves_minimum_on_power_and_destinations():
    f=fixture();f[-1].fuel_l=1.;r,_=tick(f)
    assert r['dg_on_power_kw']==25;assert r['dg_operating_duration_h']==pytest.approx(.16)
    assert (r['dg_generated_kw'],r['dg_delivered_kw'],r['dg_dumped_kw'])==pytest.approx((4,2.4,1.6))
    assert r['dg_fuel_consumed_l']==pytest.approx(1);assert r['fuel_final_l']==0
    assert r['c4isr_unserved_kw']==pytest.approx(12.6)
def test_D_one_hour_startup_and_actual_UPS_energy():
    f=fixture(c4=30,running=False,ups_kw=30.,ups_minutes=15.)
    r,u=tick(f,ups=7.5)
    assert r['dg_generated_kw']==r['dg_fuel_consumed_l']==0
    assert r['ups_operating_duration_h']==pytest.approx(.25);assert r['ups_output_kw']==7.5
    assert r['c4isr_unserved_kw']==pytest.approx(22.5);assert u==0
    q,u=tick(f,ups=u);assert q['dg_generated_kw']==30;assert q['c4isr_unserved_kw']==0
    grid,u=tick(f,ups=u,island=False);assert u==pytest.approx(7.5);assert grid['grid_import_kw']==pytest.approx(37.5)
def test_D_fractional_timestep_startup_and_zero_demand_shutdown():
    d=Diesel()
    assert [d.dispatch(15,.25) for _ in range(4)]==[0,0,0,0]
    assert d.dispatch(15,.25)==25
    assert d.dispatch(0,.25)==0 and d.state=='OFF'
    assert d.dispatch(15,.25)==0
def test_E_battery_energy_power_efficiency_bounds():
    b=Battery(soc=.89);b.begin_step();p=b.charge(500,dt_h=.5)
    assert p<=90;assert b.soc==pytest.approx(.9)
    assert p*.5*.8944==pytest.approx(3)
    b.begin_step();p=b.discharge(500,True,.5);assert p<=90
    assert (.9-b.soc)*300==pytest.approx(p*.5/.8944)
    low=Battery(soc=.1);assert low.discharge(100,True,.25)==0
def test_E_DG_charges_only_when_explicitly_permitted_and_connected():
    default,_=tick(fixture());assert default['dg_to_bess_kw']==0 and default['dg_dumped_kw']==10
    allowed,_=tick(fixture(allow_dg_to_bess=True));assert allowed['dg_to_bess_kw']==10;assert allowed['soc_final']>.1
    limited,_=tick(fixture(allow_dg_to_bess=True,pcs_kw=5));assert limited['dg_to_bess_kw']==5 and limited['dg_dumped_kw']==5
    disconnected,_=tick(fixture(allow_dg_to_bess=True,dg_bess_connection_assumed=False));assert disconnected['dg_to_bess_kw']==0
def test_F_connected_import_export_no_diesel_or_simultaneous_flows():
    deficit,_=tick(fixture(c4=30,soc=.3),island=False)
    assert deficit['grid_import_kw']==30 and deficit['grid_export_kw']==0 and deficit['dg_generated_kw']==0
    surplus,_=tick(fixture(c4=30,renewable=100,soc=.9),island=False)
    assert surplus['grid_export_kw']==70 and surplus['grid_import_kw']==0
def test_G_island_has_zero_grid_exchange():
    for renewable in [0,200]:
        r,_=tick(fixture(c4=30,renewable=renewable,soc=.9))
        assert r['grid_import_kw']==r['grid_export_kw']==0
def test_H_critical_first_under_shortage():
    r,_=tick(fixture(c4=30,aux=15,ev=20,dg_kw=40))
    assert (r['c4isr_served_kw'],r['aux_served_kw'],r['ev_served_kw'])==(30,10,0)
def test_I_initial_states_are_pre_dispatch_and_event_indices_exact():
    e=[{'id':'E24','start':0,'duration':24}];records=run(e,hours=24);m=event_metrics(records,e)[0]
    assert m['soc_initial']==.7 and m['fuel_initial_l']==2000
    assert records[0]['soc_final']==pytest.approx(.7171302035194412)
    assert m['start_index']==0 and m['end_index_exclusive']==24
    assert m['fuel_initial_l']<=records[0]['configured_fuel_capacity_l']
    assert 'c4_ens_kwh' in m and 'c4_eens_kwh' not in m
def test_J_full_8760h_balances_each_interval():
    records=run([{'id':'E168','start':0,'duration':168}])
    assert len(records)==8760
    for r in records:
        dt=r['dt_h'];served=sum(r[t+'_served_kw'] for t in ['c4isr','aux','ev'])
        independent=(r['pv_actual_kw']+r['wind_actual_kw']+r['dg_generated_kw']+r['grid_import_kw']+r['bess_discharge_kw']+r['ups_output_kw']-served-r['bess_charge_kw']-r['ups_charge_kw']-r['grid_export_kw']-r['dg_dumped_kw'])*dt
        assert abs(independent)<1e-7
        assert r['dg_generated_kw']*dt==pytest.approx(r['dg_on_power_kw']*r['dg_operating_duration_h'],abs=1e-8)
        assert r['fuel_initial_l']-r['fuel_final_l']==pytest.approx(.25*r['dg_generated_kw']*dt,abs=1e-8)
        for t in ['c4isr','aux','ev']:assert r[t+'_required_kw']==pytest.approx(r[t+'_served_kw']+r[t+'_unserved_kw'],abs=1e-9)
def test_K_zero_RE_empty_fuel_min_SOC_unavailable_source():
    for unavailable in ['EMPTY','DISABLED']:
        f=fixture(c4=30,dg_enabled=unavailable!='DISABLED')
        if unavailable=='EMPTY':f[-1].fuel_l=0
        r,_=tick(f);assert r['dg_generated_kw']==0 and r['c4isr_unserved_kw']==30
    r,_=tick(fixture(c4=30,renewable=200,soc=.9));assert r['renewable_curtailed_kw']==170 and r['pv_actual_kw']==30
def test_K_minimum_surplus_without_sink_is_infeasible():
    f=fixture(dump_load_assumed=False)
    before=f[-1].fuel_l
    with pytest.raises(InfeasibleOperatingPoint):tick(f)
    assert f[-1].fuel_l==before
    with pytest.raises(InfeasibleOperatingPoint):tick(fixture(allow_dg_to_bess=True,pcs_kw=0,dump_load_assumed=False))
def test_invalid_fuel_and_event_alignment_are_rejected():
    f=fixture();f[-1].fuel_l=2001
    with pytest.raises(ValueError):tick(f)
    with pytest.raises(ValueError):run([{'id':'unaligned','start':.5,'duration':1}],hours=2)
