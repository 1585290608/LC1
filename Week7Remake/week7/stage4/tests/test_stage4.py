"""Stage4 checks: deterministic paired results, fuel ledger, input gates, reproducibility.
These are software/model tests, not native MDT/HOMER or real-site validation.
"""
from __future__ import annotations
import csv,json
from collections import defaultdict
import pytest
from pathlib import Path
from week7.stage4.contingency import run,Delivery
from week7.stage4.run_study import CANDIDATES,POLICIES,SECONDARY,FLEET_POLICIES

OUT=Path(__file__).resolve().parents[1]/'outputs'

def rows(filename):
    with (OUT/filename).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def test_expected_matrix_and_ids():
    data=rows('stage4_52start_contingency_full.csv')
    expected=52*(len(POLICIES)+2*len(SECONDARY))
    assert expected==1508==len(data)
    assert len({r['scenario_id'] for r in data})==len(data)
    assert {r['policy'] for r in data}=={a for a,_ in POLICIES}
    assert all(r['valid']=='True' and int(r['completed_hours'])==168 for r in data)

def test_energy_balance_and_fuel_conservation_on_every_case():
    for r in rows('stage4_52start_contingency_full.csv'):
        assert abs(float(r['max_AC_residual_kwh']))<1e-8
        assert abs(float(r['max_battery_residual_kwh']))<1e-8
        assert abs(float(r['max_step_fuel_residual_l']))<1e-8
        assert abs(float(r['fuel_ledger_residual_l']))<1e-8
        assert 0<=float(r['fuel_end_l'])<=2000+1e-7
        assert float(r['fuel_delivered_l'])>=0
        assert float(r['fuel_delivery_unaccepted_l'])>=0
        assert float(r['battery_soc_min'])>=.1-1e-8
        assert float(r['critical_ENS_kwh'])>=-1e-8
        assert float(r['total_ENS_kwh'])+1e-8>=float(r['critical_ENS_kwh'])

def test_paired_baseline_matches_stage3_and_all_rows():
    parity=rows('stage4_stage3_baseline_parity.csv')
    assert len(parity)==3*52*5==780
    assert max(abs(float(r['diff'])) for r in parity)<1e-7
    matrix=rows('stage4_52start_contingency_full.csv')
    assert len([r for r in matrix if r['policy']=='BASE'])==3*52

def test_scenario_summary_exact_from_raw():
    matrix=rows('stage4_52start_contingency_full.csv')
    summaries=rows('stage4_52start_contingency_summary.csv')
    assert len(summaries)==len(POLICIES)+2*len(SECONDARY)
    for s in summaries:
        selected=[r for r in matrix if r['policy']==s['policy'] and r['pv_kw']==s['pv_kw'] and r['bess_kwh']==s['bess_kwh']]
        assert len(selected)==52
        assert float(s['mean_total_ENS_kwh'])==pytest.approx(sum(float(r['total_ENS_kwh']) for r in selected)/52,abs=1e-7)
        assert int(s['critical_shortfall_windows'])==sum(float(r['critical_ENS_kwh'])>1e-7 for r in selected)
        assert float(s['mean_accepted_delivery_l'])==pytest.approx(sum(float(r['fuel_delivered_l']) for r in selected)/52,abs=1e-7)

def test_delivery_budget_and_unaccepted_tank_capacity():
    result,_,events=run(start=0,deliveries=(Delivery(0,500.),Delivery(2,500.)),hours=24)
    assert result['valid']
    assert len(events)==2
    assert events[0]['accepted_l']==0. # full 2000 L tank at outage initiation
    assert events[0]['unaccepted_l']==500.
    assert all(0<=e['fuel_after_delivery_l']<=2000 for e in events)
    assert sum(e['accepted_l'] for e in events)==pytest.approx(result['fuel_delivered_l'])

def test_reject_invalid_or_ambiguous_delivery():
    with pytest.raises(ValueError):run(start=0,deliveries=(Delivery(72,100),Delivery(72,50)))
    with pytest.raises(ValueError):run(start=0,deliveries=(Delivery(169,100),))
    with pytest.raises(ValueError):run(start=0,deliveries=(Delivery(72,-100),))
    with pytest.raises(ValueError):run(start=0,initial_fuel_l=2001.)

def test_reject_invalid_forced_outage_and_soc_settings():
    with pytest.raises(ValueError):run(start=0,dg_off_periods=((48,24),))
    with pytest.raises(ValueError):run(start=0,dg_off_periods=((-1,24),))
    with pytest.raises(ValueError):run(start=0,reserve_soc=.95)
    with pytest.raises(ValueError):run(start=0,stop_soc=-.1)

def test_exact_24h_dg_off_is_honoured():
    result,trace,_=run(start=0,dg_off_periods=((24,48),),save_trace=True)
    assert result['valid'] and result['generator_forced_off_hours']==24
    assert len(trace)==168
    assert all(row['dg_generated_kw']<1e-10 for row in trace[24:48])
    assert all(row['forced_dg_off']==1 for row in trace[24:48])
    assert all(row['forced_dg_off']==0 for row in trace[:24]+trace[48:])

def test_stable_replay_matches_saved_cases():
    matrix=rows('stage4_52start_contingency_full.csv')
    lookup={(r['start_hour'],r['policy']):r for r in matrix if float(r['pv_kw'])==100 and float(r['bess_kwh'])==450}
    for st,policy,kwargs in [(336,'BASE',{}),(336,'REFUEL_500_H72',{'deliveries':(Delivery(72,500),)}),
                             (6720,'DG_DOWN_H24_H48',{'dg_off_periods':((24,48),)})]:
        r,_,_=run(start=st,**kwargs)
        historic=lookup[str(st),policy]
        assert r['total_ENS_kwh']==pytest.approx(float(historic['total_ENS_kwh']),abs=1e-9)
        assert r['critical_ENS_kwh']==pytest.approx(float(historic['critical_ENS_kwh']),abs=1e-9)
        assert r['fuel_end_l']==pytest.approx(float(historic['fuel_end_l']),abs=1e-9)

def test_fleet_feedback_is_unidirectional_and_ready_metrics():
    matrix=rows('stage4_13start_EV_mission_feedback.csv')
    assert len(matrix)==len(FLEET_POLICIES)*13==52
    assert all(r['feedback_model']=='EV_DYNAMIC_MISSION_CONSTRAINED' for r in matrix)
    assert all(r['valid']=='True' for r in matrix)
    assert all(int(r['vehicle_departures_completed'])+int(r['vehicle_departures_missed'])==int(r['vehicle_opportunities']) for r in matrix)
    assert all(float(r['minimum_vehicle_end_soc'])>=.1-1e-7 for r in matrix)
    assert all(r['fleet_soc_boundary'].startswith('Only EV propulsion') for r in matrix)

def test_summary_metadata_and_native_validation_boundary():
    m=json.loads((OUT/'stage4_summary_metadata.json').read_text())
    assert m['simulation_count']==1508 and m['mission_feedback_count']==52
    assert m['paired_baseline_checks']==780
    assert m['native_MDT_runs_new']==m['HOMER_runs_new']==0
    assert m['max_ac_residual_kwh']<1e-8 and m['max_fuel_ledger_residual_l']<1e-8
    assert m['no_probability_or_EENS'] and m['fuel_transfer']

def test_no_energy_is_ever_invented_by_early_refuel():
    baseline,_,_=run(start=0,hours=24)
    refill,_,_=run(start=0,hours=24,deliveries=(Delivery(0,500),))
    assert refill['fuel_delivered_l']==0
    assert refill['total_ENS_kwh']==pytest.approx(baseline['total_ENS_kwh'],abs=1e-9)
