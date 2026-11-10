"""Isolated Draft1 repair, preserving RE/battery/on-demand-DG/critical-UPS order.
Zero request stops DG. AC reference, ideal UPS and dump sink are assumptions.
No hardware, voltage, frequency or electrical transient certification.
"""
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime,timedelta
import csv,math
from .components import PV,Wind,Loads,Diesel,Battery,UPS,EPS,duration
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'data';TIERS=('c4isr','aux','ev')
class InfeasibleOperatingPoint(RuntimeError):pass
@dataclass
class Settings:
    pv_kw:float=50.;wind_kw:float=50.;battery_kwh:float=300.;pcs_kw:float=90.;initial_soc:float=.7;soc_min:float=.1;soc_max:float=.9;soc_reserve:float=.3;eta_charge:float=.8944;eta_discharge:float=.8944
    dg_kw:float=100.;dg_min_fraction:float=.25;fuel_l_per_kwh:float=.25;fuel_tank_l:float=2000.;dg_startup_h:float=1.;dg_enabled:bool=True
    ups_kw:float=30.;ups_minutes:float=15.;dt_h:float=1.;allow_dg_to_bess:bool=False;dg_bess_connection_assumed:bool=True
    dump_load_assumed:bool=True;dump_rating_kw:float=25.;ac_reference_assumed:bool=True
def read_col(name,idx):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
    if rows and not rows[0][idx].replace('.','').replace('-','').isdigit():rows=rows[1:]
    return [float(r[idx]) for r in rows]
def build_model(s=None):
    s=s or Settings();return PV(s.pv_kw,read_col('v6_solar_pu_index_value.csv',1)),Wind(s.wind_kw,read_col('v6_wind_pu_index_value.csv',1)),Loads(read_col('v6_C4ISR_kw_index_value.csv',1),read_col('v6_Auxiliary_kw_index_value.csv',1),read_col('v6_EV_charging_kw_index_value.csv',1))
def serve(req,served,power,tiers=TIERS):
    used=0.
    for t in tiers:
        take=min(max(0.,req[t]-served[t]),max(0.,power-used));served[t]+=take;used+=take
    return used
def step(pv,wind,loads,battery,diesel,ups_energy,h,islanded,dt_h=1.,settings=None):
    s=settings or Settings();dt=duration(dt_h);battery.begin_step()
    initial_soc=battery.soc;initial_fuel=diesel.fuel_l;initial_ups=ups_energy
    if not -EPS<=initial_fuel<=diesel.tank_l+EPS:raise ValueError('Fuel inventory exceeds configured capacity')
    req=loads.required(h)
    if any(not math.isfinite(v) or v<0 for v in req.values()):raise ValueError('Invalid demand')
    pv_av,wind_av=pv.available(h),wind.available(h)
    if min(pv_av,wind_av)<0 or not math.isfinite(pv_av+wind_av):raise ValueError('Invalid renewable profile')
    renewable=pv_av+wind_av;usable=renewable if not islanded or s.ac_reference_assumed else 0.
    base={t:0. for t in TIERS};re_to_load=serve(req,base,usable);gap=sum(req.values())-sum(base.values())
    batt_dis=battery.discharge(gap,allow_reserve=islanded,dt_h=dt);serve(req,base,batt_dis);gap=max(0.,sum(req.values())-sum(base.values()))
    if islanded and diesel.enabled and diesel.fuel_l>EPS and gap>EPS and gap<diesel.min_kw-EPS and not s.dump_load_assumed and not(s.allow_dg_to_bess and s.dg_bess_connection_assumed):raise InfeasibleOperatingPoint('DG request below minimum, no permitted charge/dump sink')
    if islanded:generated=diesel.dispatch(gap,dt)
    else:diesel.stop();diesel.profile=[(0.,dt,0.)];diesel.output_on_kw=0.;diesel.operating_duration_h=0.;diesel.fuel_used_l=0.;generated=0.
    delivered={t:base[t]*dt for t in TIERS};dg_delivered_e=dg_bess_e=dg_dump_e=ups_e=ups_on_h=0.;grid_import_to_load=0.
    if not islanded:
        extra=dict(base);grid_import_to_load=serve(req,extra,gap);delivered={t:extra[t]*dt for t in TIERS}
    else:
        for start,end,on_power in diesel.profile:
            span=end-start
            if span<=EPS:continue
            instant=dict(base);dg_to_load=serve(req,instant,on_power);dg_delivered_e+=dg_to_load*span
            for t in TIERS:delivered[t]+=(instant[t]-base[t])*span
            critical_gap=max(0.,req['c4isr']-instant['c4isr']);ups_power=min(critical_gap,s.ups_kw)
            if ups_power>EPS and ups_energy>EPS:
                on_time=min(span,ups_energy/ups_power);e=ups_power*on_time;ups_energy-=e;ups_e+=e;ups_on_h+=on_time;delivered['c4isr']+=e
            surplus=max(0.,on_power-dg_to_load)
            if surplus>EPS and s.allow_dg_to_bess and s.dg_bess_connection_assumed and batt_dis<=EPS:
                charge=battery.charge(surplus,dt_h=span);dg_bess_e+=charge*span;surplus-=charge
            if surplus>EPS:
                if not s.dump_load_assumed or surplus>s.dump_rating_kw+EPS:raise InfeasibleOperatingPoint(f'DG surplus {surplus}kW exceeds supported sink')
                dg_dump_e+=surplus*span
    re_remaining=max(0.,usable-re_to_load);re_bess=0.
    if re_remaining>EPS and batt_dis<=EPS:re_bess=battery.charge(re_remaining,dt_h=dt);re_remaining-=re_bess
    ups_charge=grid_ups=re_ups=0.
    if not islanded:
        capacity=s.ups_kw*s.ups_minutes/60.;ups_charge=max(0.,min(s.ups_kw,(capacity-ups_energy)/dt));re_ups=min(re_remaining,ups_charge);re_remaining-=re_ups;grid_ups=ups_charge-re_ups;ups_energy+=ups_charge*dt
    export=re_remaining if not islanded else 0.;curtail=renewable-usable+(re_remaining if islanded else 0.)
    pv_curt=curtail*pv_av/renewable if renewable else 0.;wind_curt=curtail-pv_curt;pv_actual=pv_av-pv_curt;wind_actual=wind_av-wind_curt
    charge_e=re_bess*dt+dg_bess_e;grid_import=grid_import_to_load+grid_ups;served_total=sum(delivered.values())/dt
    dg_to_load=dg_delivered_e/dt;dg_to_bess=dg_bess_e/dt;dumped=dg_dump_e/dt
    ac_res=(pv_actual+wind_actual+generated+grid_import+batt_dis+ups_e/dt-served_total-charge_e/dt-ups_charge-export-dumped)*dt
    dc_delta=(battery.soc-initial_soc)*battery.energy_kwh;dc_expected=charge_e*battery.eta_charge-batt_dis*dt/battery.eta_discharge
    expected_fuel=sum(diesel.fuel_rate_lph(power)*(end-start) for start,end,power in diesel.profile if power>0)
    fuel_used=initial_fuel-diesel.fuel_l;fuel_res=fuel_used-expected_fuel;dg_res=generated*dt-dg_delivered_e-dg_bess_e-dg_dump_e;ups_res=ups_energy-initial_ups-ups_charge*dt+ups_e
    if max(abs(ac_res),abs(dc_delta-dc_expected),abs(fuel_res),abs(dg_res),abs(ups_res))>1e-7:raise AssertionError('Full-system accounting fails')
    if battery.soc<s.soc_min-1e-9 or battery.soc>s.soc_max+1e-9:raise AssertionError('SOC outside bounds')
    if charge_e>EPS and batt_dis>EPS:raise AssertionError('Simultaneous battery charge/discharge')
    r={'hour_index':h,'dt_h':dt,'islanded':bool(islanded),'pv_available_kw':pv_av,'wind_available_kw':wind_av,'pv_actual_kw':pv_actual,'wind_actual_kw':wind_actual,'renewable_curtailed_kw':curtail,
       're_to_load_kw':re_to_load,'re_to_bess_kw':re_bess,'re_to_ups_kw':re_ups,'dg_generated_kw':generated,'dg_delivered_kw':dg_to_load,'dg_to_bess_kw':dg_to_bess,'dg_to_ups_kw':0.,'dg_dumped_kw':dumped,
       'dg_on_power_kw':diesel.output_on_kw,'dg_operating_duration_h':diesel.operating_duration_h,'dg_state':diesel.state,'dg_fuel_consumed_l':fuel_used,'dg_fuel_remaining_l':diesel.fuel_l,
       'bess_discharge_kw':batt_dis,'bess_charge_kw':charge_e/dt,'battery_loss_kwh':charge_e*(1-battery.eta_charge)+batt_dis*dt*(1/battery.eta_discharge-1),'soc_initial':initial_soc,'soc_final':battery.soc,'battery_delta_stored_kwh':dc_delta,
       'fuel_initial_l':initial_fuel,'fuel_final_l':diesel.fuel_l,'configured_fuel_capacity_l':diesel.tank_l,'ups_initial_kwh':initial_ups,'ups_final_kwh':ups_energy,'ups_output_kw':ups_e/dt,'ups_operating_duration_h':ups_on_h,'ups_charge_kw':ups_charge,
       'grid_import_kw':grid_import,'grid_export_kw':export,'AC_residual_kwh':ac_res,'battery_residual_kwh':dc_delta-dc_expected,'fuel_residual_l':fuel_res,'DG_destination_residual_kwh':dg_res,'UPS_residual_kwh':ups_res}
    for tier in TIERS:
        served=delivered[tier]/dt;unserved=max(0.,req[tier]-served)
        if served>req[tier]+1e-9:raise AssertionError('Served demand exceeded')
        for key,value in [('required_kw',req[tier]),('served_kw',served),('unserved_kw',unserved)]:r[tier+'_'+key]=value
    return r,ups_energy
def run(events,hours=8760,settings=None):
    s=settings or Settings();dt=duration(s.dt_h)
    if abs(1/dt-round(1/dt))>1e-9:raise ValueError('Timestep must divide1hour')
    for e in events:
        if e['start']<0 or e['duration']<=0 or e['start']+e['duration']>hours or abs(e['start']/dt-round(e['start']/dt))>1e-8 or abs(e['duration']/dt-round(e['duration']/dt))>1e-8:raise ValueError('Event must be within run and aligned to timestep boundaries')
    pv,wind,loads=build_model(s);battery=Battery(s.battery_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,s.initial_soc);diesel=Diesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,s.dg_enabled)
    ups=UPS(s.ups_kw,s.ups_minutes).energy_kwh;records=[]
    for h in range(hours):
        for part in range(round(1/dt)):
            start=h+part*dt;islanded=any(e['start']<=start<e['start']+e['duration'] for e in events)
            r,ups=step(pv,wind,loads,battery,diesel,ups,h,islanded,dt,s);r['t_start_h']=start;r['t_end_h']=start+dt;r['timestamp_LST']=(datetime(2025,1,1)+timedelta(hours=start)).isoformat();records.append(r)
    return records
def event_metrics(records,events):
    result=[]
    for e in events:
        sub=[r for r in records if e['start']-EPS<=r['t_start_h']<e['start']+e['duration']-EPS]
        if not sub or abs(sum(r['dt_h'] for r in sub)-e['duration'])>1e-7:raise ValueError('Event window missing/unaligned')
        total=lambda key:sum(r[key]*r['dt_h'] for r in sub)
        r={'event_id':e['id'],'start_index':e['start'],'end_index_exclusive':e['start']+e['duration'],'duration_h':sum(x['dt_h'] for x in sub),
           'soc_initial':sub[0]['soc_initial'],'soc_final':sub[-1]['soc_final'],'soc_min':min([sub[0]['soc_initial']]+[x['soc_final'] for x in sub]),'soc_max':max([sub[0]['soc_initial']]+[x['soc_final'] for x in sub]),
           'fuel_initial_l':sub[0]['fuel_initial_l'],'fuel_final_l':sub[-1]['fuel_final_l'],'fuel_consumed_l':sum(x['dg_fuel_consumed_l'] for x in sub),
           'dg_generated_kwh':total('dg_generated_kw'),'dg_delivered_kwh':total('dg_delivered_kw'),'dg_to_bess_kwh':total('dg_to_bess_kw'),'dg_dumped_kwh':total('dg_dumped_kw'),'grid_import_kwh':total('grid_import_kw'),'grid_export_kwh':total('grid_export_kw'),
           'max_AC_residual_kwh':max(abs(x['AC_residual_kwh']) for x in sub)}
        if r['fuel_initial_l']>sub[0]['configured_fuel_capacity_l']+EPS:raise AssertionError('Invented initial fuel')
        for tier,name in [('c4isr','c4'),('aux','aux'),('ev','ev')]:
            required=total(tier+'_required_kw');served=total(tier+'_served_kw');ens=total(tier+'_unserved_kw')
            if abs(required-served-ens)>1e-7:raise AssertionError('Tier energy fails')
            r.update({name+'_required_kwh':required,name+'_served_kwh':served,name+'_ens_kwh':ens,name+'_ea_percent':100*served/required if required else None})
        result.append(r)
    return result
