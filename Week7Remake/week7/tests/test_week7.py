"""Validation of generated inputs and numerical bookkeeping; NOT MDT or field certification."""
import csv,json,math
from collections import defaultdict,Counter
from pathlib import Path
import pytest
from week7.load_model import SCENARIOS,read_equipment,read_fleet,produce
from week7.outage_sensitivity import read_load,calculate_capex
HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'outputs'

def readcsv(path):
 with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

@pytest.mark.parametrize('scenario',list(SCENARIOS))
def test_hourly_site_power_energy_consistency(scenario):
 rows=readcsv(OUT/f'{scenario}_load_8760.csv')
 assert len(rows)==8760
 assert [int(r['hour_index']) for r in rows]==list(range(8760))
 for r in rows:
  critical=float(r['c4isr_kw']);aux=float(r['aux_kw']);ev=float(r['ev_kw']);total=float(r['total_kw'])
  assert min(critical,aux,ev)>=0
  assert abs(critical+aux+ev-total)<2e-5
  detail=sum(float(v) for k,v in r.items() if k.startswith('load_') and k.endswith('_kw'))
  assert abs(detail-critical-aux)<2e-5
 summary=json.loads((OUT/f'{scenario}_summary.json').read_text())
 assert math.isclose(sum(float(r['total_kw']) for r in rows),summary['total_kwh_year'],abs_tol=1e-3)

@pytest.mark.parametrize('scenario',list(SCENARIOS))
def test_equipment_annual_ledger(scenario):
 eq=read_equipment();report=readcsv(OUT/f'{scenario}_equipment_calculations.csv')
 assert len(eq)==len(report)==14
 assert len(set(x['category'] for x in eq))==14
 totals=defaultdict(float)
 for r in report:
  assert float(r['rated_kw'])>0
  assert 0<=float(r['energized_hours'])<=8760
  totals[r['tier']]+=float(r['energy_kwh_year'])
 s=json.loads((OUT/f'{scenario}_summary.json').read_text())
 assert math.isclose(totals['c4isr'],s['critical_kwh_year'],abs_tol=.001)
 assert math.isclose(totals['aux'],s['aux_kwh_year'],abs_tol=.001)

@pytest.mark.parametrize('scenario',list(SCENARIOS))
def test_ev_chargers_connected_and_soc_reserves(scenario):
 rows=readcsv(OUT/f'{scenario}_ev_trace_61320.csv'); assert len(rows)==7*8760
 by_hour=defaultdict(float);by_ev=defaultdict(lambda:{'charge_ac':0.,'charge_dc':0.,'traction':0.,'departures':0})
 fleet={v['vehicle_id']:v for v in read_fleet()}
 for r in rows:
  vid=r['vehicle_id'];item=by_ev[vid]
  eac=float(r['charge_ac_kwh']);edc=float(r['charge_dc_kwh']);traction=float(r['traction_kwh']);connected=int(r['connected']);soc=float(r['soc_final']);prior=float(r['soc_before_charging'])
  assert eac>=-1e-8 and eac<=float(fleet[vid]['charger_ac_kw'])+1e-7
  assert connected==1 or abs(eac)<1e-8
  assert float(fleet[vid]['reserve_soc'])-1e-8<=prior<=float(fleet[vid]['initial_soc'])+1e-8
  assert prior-1e-8<=soc<=1+1e-8
  assert math.isclose(edc,eac*.92,abs_tol=1e-8)
  by_hour[int(r['hour_index'])]+=eac
  item['charge_ac']+=eac;item['charge_dc']+=edc;item['traction']+=traction;item['departures']+=int(r['mission_departure'])
  if int(r['mission_departure']):
   mission_energy=float(fleet[vid]['mission_km'])*SCENARIOS[scenario]['mission_distance_factor']*float(fleet[vid]['traction_kwh_per_km'])
   assert prior*float(fleet[vid]['battery_kwh'])>=mission_energy+float(fleet[vid]['reserve_soc'])*float(fleet[vid]['battery_kwh'])-1e-6
 assert max(by_hour.values())<=SCENARIOS[scenario]['shared_charger_kw']+1e-7
 assert set(by_ev)==set(fleet)
 for vid,stats in by_ev.items():
  last=next(r for r in reversed(rows) if r['vehicle_id']==vid)
  initial=float(fleet[vid]['initial_soc'])*float(fleet[vid]['battery_kwh'])
  final=float(last['soc_final'])*float(fleet[vid]['battery_kwh'])
  assert math.isclose(initial+stats['charge_dc']-stats['traction'],final,abs_tol=1e-4)
 assert sum(r['departures'] for r in by_ev.values())==1513


def test_scenario_monotonic_and_revised_not_legacy():
 x=[json.loads((OUT/f'{s}_summary.json').read_text()) for s in SCENARIOS]
 assert x[0]['total_kwh_year']<x[1]['total_kwh_year']<x[2]['total_kwh_year']
 assert x[0]['peak_kw']<x[1]['peak_kw']<x[2]['peak_kw']
 assert x[1]['total_kwh_day_average']>1104


def test_capex_boundary_and_islanded_consistency():
 assert calculate_capex(50,50,300)==529350
 rows=readcsv(OUT/'capacity_screen_nine_options_168h.csv')
 assert len(rows)==9
 assert {int(float(r['bess_kwh'])) for r in rows}=={300,450,600}
 for r in rows:
  if r['valid']=='True':
   assert float(r['critical_ENS_kwh'])>=0
   assert float(r['total_ENS_kwh'])>=float(r['critical_ENS_kwh'])
   assert float(r['diesel_fuel_used_l'])<=float(r['initial_fuel_l'])+1e-5
   assert float(r['ac_residual_abs_max_kwh'])<1e-6
  else:
   assert r['status']=='QUARANTINED_INFEASIBLE_OR_FAILED'
   assert not r['critical_ENS_kwh']


def test_original_8760_not_overwritten():
 rows=readcsv(HERE.parent/'data/load.csv')
 assert len(rows)==8760
 assert math.isclose(sum(float(r['total_kw']) for r in rows),402960,abs_tol=1e-3)
 assert rows[0]['total_kw']=='38.0'


def test_deterministic_regeneration(tmp_path):
 result=produce('low',tmp_path)
 assert result==json.loads((OUT/'low_summary.json').read_text())
 assert (tmp_path/'low_load_8760.csv').read_bytes()==(OUT/'low_load_8760.csv').read_bytes()
 assert (tmp_path/'low_ev_trace_61320.csv').read_bytes()==(OUT/'low_ev_trace_61320.csv').read_bytes()
