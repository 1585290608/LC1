"""Transparent 2025 LST-load scenarios and individual mission-constrained EV charging.
All assumptions are proposed research inputs, NOT verified MOD site/OEM data.
No vehicle-to-grid discharge implemented.  One-hour time step: kW*1h = kWh.
"""
from __future__ import annotations
import argparse,csv,json,math
from dataclasses import dataclass
from datetime import datetime,timedelta
from pathlib import Path

HERE=Path(__file__).resolve().parent
DATE0=datetime(2025,1,1)
SCENARIOS={
 'low':{'aux_utilisation':0.65,'mission_distance_factor':0.80,'shared_charger_kw':70.},
 'central':{'aux_utilisation':0.80,'mission_distance_factor':1.00,'shared_charger_kw':70.},
 'high':{'aux_utilisation':1.00,'mission_distance_factor':1.25,'shared_charger_kw':70.},
}
EPS=1e-8

def read_equipment():
 with (HERE/'config/equipment.csv').open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def read_fleet():
 with (HERE/'config/fleet.csv').open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def scheduled_hours(name,dt):
 h=dt.hour;m=dt.month
 # All interval labels begin at the stated integer hour on the source LST clock.
 rules={
  'C4ISR_and_command':lambda:True,
  'Medical_and_emergency_refrigeration':lambda:True,
  'C4ISR_cooling':lambda:True,
  'Perimeter_security_lighting':lambda:h>=18 or h<6,
  'Accommodation_ventilation':lambda:True,
  'Accommodation_socket_loads':lambda:6<=h<9 or 17<=h<24 or 0<=h<2,
  'Accommodation_lighting':lambda:6<=h<9 or 18<=h<23,
  'Catering_electric_cooking':lambda:6<=h<9 or 11<=h<14 or 17<=h<19,
  'Workshops_and_maintenance':lambda:9<=h<15 and dt.weekday()<5,
  'Laundry':lambda:13<=h<17,
  'Water_pumping_and_treatment':lambda:7<=h<10 or 18<=h<21,
  'Common_area_lighting':lambda:7<=h<12 or 16<=h<21,
  'Space_heating_electric':lambda:m in (10,11,12,1,2,3,4) and (h>=17 or h<5) or m in (5,9) and (h>=18 or h<2),
  'Summer_cooling_noncritical':lambda:m in (6,7,8) and 10<=h<20,
 }
 if name not in rules:raise ValueError(f'Unknown equipment category {name}')
 return rules[name]()

@dataclass
class EV:
 id:str; kind:str; cap:float; consumption:float; rate:float;reserve:float;soc:float;dep:int;arr:int;km:float;days:frozenset[int]
 connected:bool=True;away_energy_kwh:float=0.;mission_count:int=0
 def mission_today(self,dt):return dt.weekday() in self.days

def initialise_fleet():
 res=[]
 for r in read_fleet():
  res.append(EV(r['vehicle_id'],r['vehicle_class'],float(r['battery_kwh']),float(r['traction_kwh_per_km']),float(r['charger_ac_kw']),float(r['reserve_soc']),float(r['initial_soc']),int(r['departure_hour']),int(r['arrival_hour']),float(r['mission_km']),frozenset(int(x) for x in r['mission_weekdays'].split(';'))))
 assert len(res)==7 and len({v.id for v in res})==7
 return res

def next_departure(v,dt):
 for delta in range(8):
  date=dt.date()+timedelta(days=delta)
  next_dt=datetime.combine(date,datetime.min.time()).replace(hour=v.dep)
  if next_dt>dt and next_dt.weekday() in v.days:return next_dt
 return None

def produce(scenario:str,output:Path):
 if scenario not in SCENARIOS:raise ValueError('Unknown load case')
 opt=SCENARIOS[scenario];output.mkdir(parents=True,exist_ok=True)
 eq=read_equipment();fleet=initialise_fleet();charging_efficiency=0.92;target_soc=0.90
 hourly=[];trace=[];departures=0;energy_on_missions=0.;ac_charging=0.;equipment_summary={x['category']:{'tier':x['tier'],'rated_kw':float(x['rated_kw']),'energized_hours':0,'energy_kwh':0.} for x in eq}
 for h in range(8760):
  dt=DATE0+timedelta(hours=h);base={'c4isr':0.,'aux':0.};details={}
  for x in eq:
   name=x['category'];load=(float(x['rated_kw'])* (1.0 if x['tier']=='c4isr' else opt['aux_utilisation'])) if scheduled_hours(name,dt) else 0.
   base[x['tier']]+=load;details[name]=round(load,6);equipment_summary[name]['energized_hours']+=int(scheduled_hours(name,dt));equipment_summary[name]['energy_kwh']+=load
  # Return before departures; kWh spent on missions is deducted at return.
  hour_activity={}
  for v in fleet:
   a={'mission_departure':False,'mission_return':False,'traction_kwh':0.,'charge_ac_kwh':0.}
   if not v.connected and dt.hour==v.arr and v.mission_today(dt):
    v.soc-=v.away_energy_kwh/v.cap;energy_on_missions+=v.away_energy_kwh
    a['traction_kwh']=v.away_energy_kwh;a['mission_return']=True;v.away_energy_kwh=0.;v.connected=True
    if v.soc<v.reserve-EPS:raise ValueError(f'{scenario} {dt} mission reserve violated {v.id}')
   if v.connected and dt.hour==v.dep and v.mission_today(dt):
    need=v.km*opt['mission_distance_factor']*v.consumption
    if v.soc*v.cap+EPS<need+v.reserve*v.cap:
     raise ValueError(f'{scenario} {dt} failed departure: {v.id}: stock {v.soc*v.cap:.2f}, needs {need+v.reserve*v.cap:.2f}')
    v.connected=False;v.away_energy_kwh=need;v.mission_count+=1;departures+=1;a['mission_departure']=True
   hour_activity[v.id]=a
  connected=sorted((v for v in fleet if v.connected),key=lambda v:(next_departure(v,dt) or datetime.max,v.id))
  spare=opt['shared_charger_kw']
  for v in fleet:hour_activity[v.id]['soc_before_charging']=v.soc
  for v in connected:
   needed_ac=max(0.,(target_soc-v.soc)*v.cap/charging_efficiency)
   charge=min(v.rate,spare,needed_ac)
   v.soc+=charge*charging_efficiency/v.cap;spare-=charge
   ac_charging+=charge;hour_activity[v.id]['charge_ac_kwh']=charge
   if v.soc>target_soc+EPS:raise AssertionError('Overcharged EV')
  ev_kw=sum(hour_activity[v.id]['charge_ac_kwh'] for v in fleet)
  if ev_kw>opt['shared_charger_kw']+EPS:raise AssertionError('EV shared feeder overload')
  row={'hour_index':h,'timestamp_LST':dt.isoformat(),'c4isr_kw':round(base['c4isr'],6),'aux_kw':round(base['aux'],6),'ev_kw':round(ev_kw,6),'total_kw':round(base['c4isr']+base['aux']+ev_kw,6),**{'load_'+name+'_kw':value for name,value in details.items()}}
  hourly.append(row)
  for v in fleet:
   a=hour_activity[v.id]
   trace.append({'hour_index':h,'timestamp_LST':dt.isoformat(),'vehicle_id':v.id,'connected':int(v.connected),'soc_before_charging':round(a['soc_before_charging'],9),'soc_final':round(v.soc,9),'battery_kwh':v.cap,'charger_limit_ac_kw':v.rate,'charge_ac_kwh':round(a['charge_ac_kwh'],9),'charge_dc_kwh':round(a['charge_ac_kwh']*charging_efficiency,9),'mission_departure':int(a['mission_departure']),'mission_return':int(a['mission_return']),'traction_kwh':round(a['traction_kwh'],9),'mission_reserve_soc':v.reserve})
  if abs(row['c4isr_kw']+row['aux_kw']+row['ev_kw']-row['total_kw'])>1e-5:raise AssertionError('Hourly sum mismatch')
 # End-of-year fleet stock identity, all missions completed before end-of-year.
 for v in fleet:
  if not v.connected or v.away_energy_kwh>EPS:raise AssertionError('Unfinished mission at year end')
  trace_ev=[t for t in trace if t['vehicle_id']==v.id]
  initial=float(next(r['initial_soc'] for r in read_fleet() if r['vehicle_id']==v.id))*v.cap
  final=v.soc*v.cap
  charge=sum(t['charge_dc_kwh'] for t in trace_ev);traction=sum(t['traction_kwh'] for t in trace_ev)
  if abs(initial+charge-traction-final)>1e-5:raise AssertionError(f'EV stock ledger {v.id}')
 with (output/f'{scenario}_equipment_calculations.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,['category','tier','rated_kw','energized_hours','energy_kwh_year','mean_kwh_day','status']);w.writeheader()
  for name,info in equipment_summary.items():w.writerow({'category':name,'tier':info['tier'],'rated_kw':info['rated_kw'],'energized_hours':info['energized_hours'],'energy_kwh_year':round(info['energy_kwh'],6),'mean_kwh_day':round(info['energy_kwh']/365,6),'status':'PROVISIONAL_NOT_SITE_VERIFIED'})
 with (output/f'{scenario}_load_8760.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,hourly[0].keys());w.writeheader();w.writerows(hourly)
 with (output/f'{scenario}_ev_trace_61320.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,trace[0].keys());w.writeheader();w.writerows(trace)
 metrics={'scenario':scenario,'status':'MODELLED_ASSUMPTIONS_NOT_SITE_MEASUREMENTS','hours':len(hourly),'fleet_vehicle_count':len(fleet),'timestamp_basis':'2025 source LST (fixed hourly clock, not DST civil clock)','site_population_assumed':120,'critical_kwh_year':round(sum(r['c4isr_kw'] for r in hourly),6),'aux_kwh_year':round(sum(r['aux_kw'] for r in hourly),6),'ev_grid_ac_kwh_year':round(ac_charging,6),'ev_battery_dc_kwh_year':round(ac_charging*charging_efficiency,6),'ev_traction_kwh_year':round(energy_on_missions,6),'mission_departures':departures,'total_kwh_year':round(sum(r['total_kw'] for r in hourly),6),'total_kwh_day_average':round(sum(r['total_kw'] for r in hourly)/365,6),'peak_kw':max(r['total_kw'] for r in hourly),'ev_shared_charger_kw':opt['shared_charger_kw'],'ev_charging_efficiency_assumed':charging_efficiency,'min_soc_by_vehicle':{v.id:min(t['soc_before_charging'] for t in trace if t['vehicle_id']==v.id) for v in fleet},'end_soc_by_vehicle':{v.id:round(v.soc,6) for v in fleet},'no_V2G':'EV charging demand only; EV discharge is propulsion only'}
 (output/f'{scenario}_summary.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
 return metrics

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'outputs');args=p.parse_args()
 for case in SCENARIOS:print(json.dumps(produce(case,args.output),indent=2))
if __name__=='__main__':main()
