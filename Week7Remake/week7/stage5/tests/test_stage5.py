"""Unit tests for conditional cost ledger; all values illustrative, not native data."""
from __future__ import annotations
from dataclasses import replace
import copy,math,pytest
from week7.stage5.economics import (Sensitivity,capex_detail,delivery_attempts,
    financial_years,historical_parameters,present_value_components,replacement_cost_at,
    score_case,pareto_labels)
from week7.stage5.preflight import check_inputs
from week7.stage5.run_study import cases_aligned,baseline_setting,get_config


def sample_case(policy='BASE'):
    return {'pv_kw':100.,'wind_kw':100.,'bess_kwh':450.,'window_count':52,
        'policy':policy,'mean_total_ENS_kwh':700.,'mean_critical_ENS_kwh':100.,
        'worst_total_ENS_kwh':1800.,'critical_shortfall_windows':15,
        'mean_fuel_consumption_l':2000.,'mean_accepted_delivery_l':450. if policy!='BASE' else 0.}


def test_original_unmodified_capex_formula():
    p=historical_parameters();s=Sensitivity()
    assert math.isclose(sum(capex_detail(100,100,450,s,p).values()),852200)
    assert math.isclose(sum(capex_detail(100,100,600,s,p).values()),912200)


def test_150kwh_increment_only_battery():
    p=historical_parameters();s=Sensitivity();a=sum(capex_detail(100,100,450,s,p).values())
    b=sum(capex_detail(100,100,600,s,p).values())
    assert b-a==150*p['unit_costs']['battery_dc']


def test_bess_price_increase_is_monotonic():
    p=historical_parameters();a=present_value_components(75,75,450,Sensitivity(bess_rate_multiplier=.7),p)
    b=present_value_components(75,75,450,Sensitivity(bess_rate_multiplier=1.3),p)
    assert b['capex_gbp']>a['capex_gbp'] and b['base_selected_pv_gbp']>a['base_selected_pv_gbp']


def test_no_double_count_fuel_on_delivered_litres():
    x=score_case(sample_case('REFUEL_500_H72'),Sensitivity(trip_fee_gbp=500,delivery_premium_gbp_per_l=.2,diesel_gbp_per_l=1.35))
    assert math.isclose(x['mean_event_fuel_purchase_gbp'],2700.)
    assert math.isclose(x['mean_event_delivery_premium_gbp'],90.)
    assert math.isclose(x['mean_event_trip_fees_gbp'],500.)
    assert math.isclose(x['mean_event_cash_gbp'],3290.)


def test_trip_fee_for_rejected_fuel_still_charged():
    a=sample_case('REFUEL_500_H48_H96_H144');a['mean_accepted_delivery_l']=0
    x=score_case(a,Sensitivity())
    assert x['scheduled_delivery_trips_per_event']==3
    assert x['mean_event_trip_fees_gbp']==1500.


def test_unserved_shadow_is_noncash():
    a=score_case(sample_case(),Sensitivity())
    b=score_case(sample_case(),Sensitivity(shadow_critical_gbp_per_kwh=100,shadow_noncritical_gbp_per_kwh=10))
    assert math.isclose(a['selected_20y_cashflow_PV_gbp_NOT_NPC'],b['selected_20y_cashflow_PV_gbp_NOT_NPC'])
    assert b['shadow_cost_PV_gbp_NOT_CASH']>0


def test_no_events_have_no_outage_operating_cost():
    a=score_case(sample_case(),Sensitivity(hypothetical_events_pa=0))
    assert a['discounted_hypothetical_outage_cash_gbp']==0
    assert a['generalised_score_PV_gbp_NOT_NPC']==a['base_selected_pv_gbp']


def test_cashflow_reconciles_to_pv():
    s=Sensitivity();c=sample_case();x=score_case(c,s)
    yrs=financial_years(c,s)
    assert len(yrs)==21
    assert math.isclose(sum(y['selected_cash_PV_gbp'] for y in yrs),x['selected_20y_cashflow_PV_gbp_NOT_NPC'],abs_tol=1e-6)
    assert yrs[0]['hypothetical_outage_cash_gbp']==0 and yrs[-1]['terminal_fuel_inventory_recovery_gbp']==2700


def test_replacement_years_match_inherited_not_oem():
    p=historical_parameters();parts=capex_detail(100,100,450,Sensitivity(),p)
    assert replacement_cost_at(1,parts,p)==0
    assert replacement_cost_at(12,parts,p)>0
    assert replacement_cost_at(15,parts,p)>0


def test_invalid_sensitivity_rejected():
    for kw in ({'diesel_gbp_per_l':-1},{'trip_fee_gbp':float('inf')},{'hypothetical_events_pa':-1},{'bess_rate_multiplier':0}):
        with pytest.raises(ValueError):Sensitivity(**kw)


def test_invalid_provenance_mismatch_rejected():
    a=sample_case();a['window_count']=51
    with pytest.raises(ValueError):score_case(a,Sensitivity())


def test_invalid_ens_mismatch_rejected():
    a=sample_case();a['mean_critical_ENS_kwh']=1000
    with pytest.raises(ValueError):score_case(a,Sensitivity())


def test_only_whitelisted_refuel_policies():
    assert delivery_attempts('BASE')==0
    assert delivery_attempts('REFUEL_500_H72')==1
    assert delivery_attempts('REFUEL_500_H48_H96_H144')==3
    with pytest.raises(ValueError):delivery_attempts('DG_DOWN_H24_H48')


def test_pareto_obvious_dominance():
    a={'selected_20y_cashflow_PV_gbp_NOT_NPC':100,'mean_total_ENS_kwh':20,'mean_critical_ENS_kwh':5,'critical_shortfall_windows':3}
    b={'selected_20y_cashflow_PV_gbp_NOT_NPC':120,'mean_total_ENS_kwh':30,'mean_critical_ENS_kwh':6,'critical_shortfall_windows':4}
    result=pareto_labels([a,b]);assert result[0]['conditional_four_axis_pareto'].startswith('NONDOMINATED') and result[1]['conditional_four_axis_pareto']=='DOMINATED'


def test_all_15_candidates_derived_from_reproducible_sources():
    c=cases_aligned();assert len(c)==15 and len([x for x in c if x['policy']=='BASE'])==9
    assert all(x['window_count']==52 for x in c)


def test_preflight_includes_native_unperformed_gate():
    r=check_inputs();assert r['all_internal_preflight_pass']
    assert r['new_native_MDT_runs']==r['new_HOMER_Pro_runs']==0
    assert not r['independent_external_validation']
    assert any(x['status']=='NOT_PERFORMED' for x in r['source_results'])
