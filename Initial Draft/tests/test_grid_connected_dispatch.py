import pytest
from validation.trace_io import load
from models.core.components import Battery
from models.grid_connected.dispatch import PROTOCOL_PATH, dispatch_hour, InfeasibleAnnualCase, cases
from models.grid_connected.economics import capital,parameters,evaluate,payback_details

def protocol(reserve=.3,export=20):
    p=load(PROTOCOL_PATH);p.update(reserve=reserve,export_kw=export);return p
def battery(soc=.7,reserve=.3):return Battery(soc=soc,soc_reserve=reserve)
def req(p):return {'c4isr':p,'aux':0.,'ev':0.}
def test_terminal_replenishment_is_paid_and_respects_import_headroom():
    b=battery(.3);p=protocol();records=[dispatch_hour(req(65),0,0,b,True,p) for i in range(4)]
    assert b.soc==pytest.approx(.7)
    assert sum(r['grid_to_bess_kw'] for r in records)==pytest.approx(120/.8944)
    assert all(r['grid_import_kw']<=100 for r in records)
    assert sum(r['grid_import_kw'] for r in records)==pytest.approx(260+120/.8944)
def test_terminal_excess_inventory_serves_load_not_a_reset():
    b=battery(.9);r=dispatch_hour(req(65),0,0,b,True,protocol())
    assert b.soc==pytest.approx(.7);assert r['bess_discharge_kw']==pytest.approx(60*.8944)
    assert r['grid_import_kw']==pytest.approx(65-60*.8944)
def test_terminal_re_surplus_cannot_overfill_target_or_export_battery():
    b=battery();r=dispatch_hour(req(30),50,50,b,True,protocol())
    assert b.soc==.7;assert r['grid_export_kw']==20;assert r['renewable_curtailed_kw']==50
    assert r['bess_charge_kw']==r['bess_discharge_kw']==r['grid_import_kw']==0
def test_no_grid_charging_outside_declared_terminal_window():
    b=battery(.3);r=dispatch_hour(req(40),0,0,b,False,protocol())
    assert r['grid_to_bess_kw']==0 and b.soc==.3
def test_no_simultaneous_battery_directions_and_PCS_limit():
    b=battery(.3);r=dispatch_hour(req(0),50,50,b,False,protocol())
    assert r['bess_charge_kw']==90;assert r['bess_discharge_kw']==0
    r=dispatch_hour(req(60),0,0,b,False,protocol())
    assert r['bess_discharge_kw']>0 and r['bess_charge_kw']==0
def test_import_limit_failure_is_not_hidden():
    with pytest.raises(InfeasibleAnnualCase):dispatch_hour(req(101),0,0,battery(.7,.7),False,protocol(.7))
def test_reserve_maintains_battery_floor():
    b=battery(.7,.7);r=dispatch_hour(req(30),0,0,b,False,protocol(.7));assert b.soc==.7;assert r['grid_import_kw']==30
def test_payback_accounts_for_replacement_recrossing():
    p=payback_details([-100,80,80,-100,80],0)
    assert p['first_undiscounted_crossing_year']==pytest.approx(1.25)
    assert p['simple_payback_including_replacements_year']==pytest.approx(3.5)
    assert p['discounted_sustained_payback_year']==pytest.approx(3.5)
def test_payback_not_achieved_when_cashflows_do_not_recover():
    p=payback_details([-100]+[1]*20,.03)
    assert p['simple_payback_including_replacements_year'] is None and p['discounted_sustained_payback_year'] is None
def test_cost_boundaries_actual90PCS_and_common_backup_same():
    p=parameters();a,ca,sa=capital('HYBRID',p);b,cb,sb=capital('P0R',p)
    assert ca==529350 and cb==124000;assert sa==sb==2700
    assert next(x for x in a if x['asset']=='BESS_PCS')['CAPEX_gbp']==22500
    for asset in ('DG','UPS','Common_site','Tank_fixed','Tank_volume'):
        assert next(x for x in a if x['asset']==asset)['CAPEX_gbp']==next(x for x in b if x['asset']==asset)['CAPEX_gbp']
    assert len({x['asset'] for x in a})==len(a)
def test_NPC_cashflow_discount_and_replacements():
    p=parameters();m={'case':'TEST','kind':'P0R','grid_import_kwh':402960.,'grid_export_kwh':0.}
    r,flows,_=evaluate(m,p=p)
    annual=402960*.24+124000*.025+730
    expected=126700+annual*(1-1.03**-20)/.03+13000/1.03**12+24000/1.03**15-2700/1.03**20
    assert r['NPC_20y_gbp']==pytest.approx(expected)
    assert flows[12]['replacement_cost_gbp']==13000 and flows[15]['replacement_cost_gbp']==24000
def test_factor_actual_official_scope2_total_not_only_CO2():
    p=parameters();assert p['grid_factor_kgCO2e_kwh']==pytest.approx(.177)
    assert p['grid_factor_source']['cell']=='J3066'
    assert p['grid_factor_source']['underlying_grid_data_year']==2023
def test_study_design_is_OFAT_and_frozen_core_unchanged(baseline_core_verified):
    c=cases();assert len(c)==12;assert len({x.name for x in c})==12
