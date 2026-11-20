"""WP2/WP4 verification - numerical/software checks, not native MDT validation."""
import csv,json,math
from collections import defaultdict
from pathlib import Path
import pytest
from week7.nextstage.screen import simulate,PV_PU,WIND_PU
from week7.nextstage.fleet_feedback import EVFleetFeedback
from week7.nextstage.dispatcher import instrumented_s3
from week7.outage_sensitivity import calculate_capex

HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'outputs'


def csvread(name):
    with (OUT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def test_previous_three_quarantined_are_now_completed():
    rows=csvread('nine_candidate_v2_168h.csv')
    assert len(rows)==9 and all(x['valid']=='True' for x in rows)
    for pv,bess in [(50,450),(75,300),(75,450)]:
        rec=next(x for x in rows if float(x['pv_kw'])==pv and float(x['bess_kwh'])==bess)
        assert int(rec['completed_h'])==168 and rec['status']=='PYTHON_SCREEN_COMPLETE'
        assert float(rec['bess_same_hour_both_directions'])==0
        assert float(rec['max_AC_residual_kwh'])<1e-6
        assert float(rec['max_battery_residual_kwh'])<1e-6


def test_v2_does_not_regress_six_previously_completed_candidates():
    old=list(csv.DictReader((HERE.parent/'outputs'/'capacity_screen_nine_options_168h.csv').open()))
    new=csvread('nine_candidate_v2_168h.csv')
    for prior in old:
        if prior['valid']!='True':continue
        newer=next(x for x in new if x['pv_kw']==prior['pv_kw'] and x['bess_kwh']==prior['bess_kwh'])
        for k in ['critical_ENS_kwh','total_ENS_kwh','diesel_fuel_used_l','bess_end_soc']:
            assert math.isclose(float(prior[k]),float(newer[k]),rel_tol=0,abs_tol=1e-6),(prior['pv_kw'],prior['bess_kwh'],k)


@pytest.mark.parametrize('filename,expected',[
    ('nine_candidate_v2_168h.csv',9),
    ('seasonal_nine_candidates_24_72_168h.csv',108),
    ('mission_readiness_feedback_matrix.csv',48),
    ('contingency_v2_168h.csv',6),
    ('contingency_dynamic_EV_mission_readiness_168h.csv',6),
])
def test_all_generated_screens_pass_physical_ledgers(filename,expected):
    rows=csvread(filename)
    assert len(rows)==expected
    for x in rows:
        assert x['valid']=='True' and x['status']=='PYTHON_SCREEN_COMPLETE'
        assert int(x['completed_h'])==int(x['requested_h'])
        assert float(x['bess_same_hour_both_directions'])==0
        assert float(x['max_AC_residual_kwh'])<1e-6
        assert float(x['max_battery_residual_kwh'])<1e-6
        assert float(x['initial_soc'])>=.3
        assert -1e-6<=float(x['fuel_end_l'])<=float(x['initial_fuel_l'])+1e-6
        assert 0<=float(x['critical_EA_fraction'])<=1+1e-9
        assert float(x['total_ENS_kwh'])>=float(x['critical_ENS_kwh'])-1e-7
        assert abs(float(x['critical_required_kwh']) * (1-float(x['critical_EA_fraction']))-float(x['critical_ENS_kwh']))<1e-6
        if x['feedback_model']=='EV_DYNAMIC_MISSION_CONSTRAINED':
            op=int(x['vehicle_opportunities']);good=int(x['vehicle_departures_completed']);miss=int(x['vehicle_departures_missed'])
            assert good+miss==op
            assert (0<=float(x['mission_readiness_fraction'])<=1) if op else x['mission_readiness_fraction']==''
            assert float(x['minimum_vehicle_end_soc'])>=.2-1e-9
            assert abs(float(x['ev_ENS_kwh'])-float(x['ev_charging_ENS_ac_kwh']))<1e-6


def test_vehicle_feedback_matches_original_week7_demand_when_fully_supplied():
    base=list(csv.DictReader((HERE.parent/'outputs'/'central_load_8760.csv').open()))
    fleet=EVFleetFeedback('central')
    for h in range(8760):
        req=fleet.before_hour(h)
        assert math.isclose(req,float(base[h]['ev_kw']),abs_tol=2e-6)
        fleet.after_hour(req)
    assert fleet.missed==0 and fleet.completed==1513
    assert math.isclose(fleet.traction_kwh,40442.,abs_tol=1e-5)
    assert fleet.unserved_ac_kwh==0
    assert max(abs(v.soc-.9) for v in fleet.vehicles)<1e-9


def test_ev_charging_blackout_causes_mission_readiness_failure_without_reserve_breach():
    fleet=EVFleetFeedback('central')
    # No charging available for a whole 15-day outage, even if charging is requested.
    for h in range(360):
        fleet.before_hour(h)
        fleet.after_hour(0.)
    assert fleet.missed>0
    assert fleet.opportunities==fleet.missed+fleet.completed
    assert all(v.soc>=v.reserve-1e-9 for v in fleet.vehicles)
    assert all(float(r['charging_served_ac_kwh'])==0 for r in fleet.rows)
    assert all(float(r['charging_requested_ac_kwh'])<=float(next(v.rate for v in fleet.vehicles if v.id==r['vehicle_id']))+1e-9 for r in fleet.rows)


def test_dynamic_trace_EV_energy_conservation_by_vehicle_and_hour():
    fleet=csvread('winter_168h_original_equipment_EV_trace.csv')
    plant=csvread('winter_168h_original_equipment_plant_trace.csv')
    assert len(fleet)==168*7 and len(plant)==168
    by_hour=defaultdict(list);by_vehicle=defaultdict(list)
    for row in fleet:
        by_hour[int(row['hour_index'])].append(row)
        by_vehicle[row['vehicle_id']].append(row)
        assert float(row['soc_end'])>=float(row['mission_reserve_soc'])-1e-8
        assert 0<=float(row['charging_served_ac_kwh'])<=float(row['charging_requested_ac_kwh'])+1e-9
        assert float(row['charging_requested_ac_kwh'])-float(row['charging_served_ac_kwh'])==pytest.approx(float(row['charging_unserved_ac_kwh']),abs=1e-8)
        if row['connected']=='0':assert abs(float(row['charging_served_ac_kwh']))<1e-8
    assert set(by_hour)==set(range(168))
    for p in plant:
        h=int(p['hour_index']); rows=by_hour[h]
        assert sum(float(r['charging_requested_ac_kwh']) for r in rows)==pytest.approx(float(p['ev_required_kw']),abs=1e-6)
        assert sum(float(r['charging_served_ac_kwh']) for r in rows)==pytest.approx(float(p['ev_served_kw']),abs=1e-6)
        assert sum(float(r['charging_unserved_ac_kwh']) for r in rows)==pytest.approx(float(p['ev_unserved_kw']),abs=1e-6)
        assert float(p['bess_charge_kw'])*float(p['bess_discharge_kw'])==pytest.approx(0,abs=1e-8)
    from week7.load_model import read_fleet
    initial={r['vehicle_id']:float(r['initial_soc'])*float(r['battery_kwh']) for r in read_fleet()}
    for vid,rs in by_vehicle.items():
        capacity=float(next(v['battery_kwh'] for v in read_fleet() if v['vehicle_id']==vid))
        remaining=initial[vid]+sum(float(r['charging_served_ac_kwh'])*.92-float(r['traction_kwh']) for r in rs)
        # Unfinished routes are possible in arbitrary stop-hours; here h=168 is end of 7 days.
        assert remaining==pytest.approx(float(rs[-1]['soc_end'])*capacity,abs=1e-6)
    assert sum(int(r['mission_missed']) for r in fleet)==1


def test_dynamic_results_reproduce_direct_run():
    recorded=next(r for r in csvread('mission_readiness_feedback_matrix.csv') if r['season']=='winter' and r['requested_h']=='168' and r['pv_kw']=='50.0' and r['bess_kwh']=='300.0')
    now,_,_=simulate(fleet_feedback=True)
    assert now['vehicle_departures_missed']==1
    assert now['total_ENS_kwh']==pytest.approx(float(recorded['total_ENS_kwh']),abs=1e-6)
    assert now['mission_readiness_fraction']==pytest.approx(28/29,abs=1e-10)


def test_no_unsupported_native_validation_claim():
    s=json.loads((OUT/'summary_v2.json').read_text())
    assert s['native_MDT_cross_validation']==0 and s['HOMER_Pro_reoptimisation']==0
    assert s['bess_simultaneous_hourly_count']==0 and not s['quarantined']
