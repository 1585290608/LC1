"""Focused deterministic emergency cases, using frozen Draft3A physics/EMS."""
from dataclasses import dataclass,asdict,replace
from datetime import datetime,timedelta
from pathlib import Path
import json,math
from ..core.components import Battery,UPS,EPS
from ..core.simulate import Settings,build_model,event_metrics
from .fuel_models import ResearchDiesel
from .service_dispatch import instrumented_s0,instrumented_s3
ROOT=Path(__file__).resolve().parents[1]
@dataclass(frozen=True)
class Scenario:
    id:str
    groups:str
    system:str='HYBRID'
    start:int=0
    hours:int=168
    fuel:float=2000.
    soc:float=.7
    re_scale:float=1.
    dg_off_start:int=-1
    dg_off_end:int=-1
    reused:bool=False
def scenarios():
    result=[]
    for season,month in [('Winter',1),('Spring',4),('Summer',7),('Autumn',10)]:
        start=int((datetime(2025,month,1)-datetime(2025,1,1)).total_seconds()/3600)
        for system in ['P0R','HYBRID']:
            groups='C1;C2' if month==1 else 'C1'
            if month==1 and system=='HYBRID':groups+=';C3'
            result.append(Scenario(f'C1_{season}_{system}',groups,system,start,reused=month==1 and system=='HYBRID'))
    for fuel in (500,1000):
        for system in ['P0R','HYBRID']:result.append(Scenario(f'C2_F{fuel}_{system}','C2',system,fuel=fuel))
    for soc in (.3,.5):result.append(Scenario(f'C3_SOC{int(soc*100)}_HYBRID','C3',soc=soc))
    for system in ['P0R','HYBRID']:
        result.append(Scenario(f'C4_CONTROL_{system}','C4',system,hours=336))
        result.append(Scenario(f'C4_STRESS_{system}','C4',system,hours=336,re_scale=.6,dg_off_start=48,dg_off_end=72))
    return result
def settings(case):
    return replace(Settings(),pv_kw=50.*case.re_scale if case.system=='HYBRID' else 0.,wind_kw=50.*case.re_scale if case.system=='HYBRID' else 0.,pcs_kw=90. if case.system=='HYBRID' else 0.,initial_soc=case.soc if case.system=='HYBRID' else .7,allow_dg_to_bess=case.system=='HYBRID')
def should_inhibit_charge(s,b,d,pv,wind,loads,h,controller,dt=1.):
    """Preemptive whole-hour single-direction safeguard, no hidden fuel or energy changes."""
    if not s.allow_dg_to_bess or not d.enabled or d.fuel_l<=EPS:return False
    gap=max(0.,sum(loads.required(h).values())-pv.available(h)-wind.available(h))
    can_cover=gap<=min(b.pcs_kw,max(0.,(b.soc-s.soc_reserve)*b.energy_kwh*b.eta_discharge/dt))+EPS
    committed=controller['committed']
    if gap<=EPS:return False
    if committed and b.soc>=controller['stop_soc']-EPS and can_cover:committed=False
    elif not committed and (b.soc<=s.soc_reserve+EPS or not can_cover):committed=True
    if not committed:return False
    delay=0. if d.running else d.start_remaining_h if d.state=='STARTING' else d.startup_delay_h
    available=max(0.,dt-delay);on=min(d.rated_kw,max(d.min_kw,gap))
    return available>EPS and d.fuel_l+1e-9<d.fuel_rate_lph(on)*available
def run(case):
    s=settings(case);pv,wind,loads=build_model(s);b=Battery(s.battery_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,s.initial_soc)
    d=ResearchDiesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,True).set_fuel_model('MDT_DERIVED');d.fuel_l=case.fuel
    ups=UPS(s.ups_kw,s.ups_minutes).energy_kwh;controller={'committed':False,'stop_soc':.6};rows=[];segments=[]
    try:
        for elapsed in range(case.hours):
            h=case.start+elapsed;available=not(case.dg_off_start<=elapsed<case.dg_off_end)
            if not available:d.stop()
            d.enabled=available
            guard=should_inhibit_charge(s,b,d,pv,wind,loads,h,controller)
            effective=replace(s,allow_dg_to_bess=False) if guard else s
            if case.system=='HYBRID':r,ups=instrumented_s3(pv,wind,loads,b,d,ups,h,True,1.,effective,controller,segments)
            else:r,ups=instrumented_s0(pv,wind,loads,b,d,ups,h,True,1.,effective,segments)
            r.update(t_start_h=h,t_end_h=h+1,timestamp_LST=(datetime(2025,1,1)+timedelta(hours=h)).isoformat(),dg_profile=json.dumps(d.profile,separators=(',',':')),dg_start_command=d.last_start_command,committed=controller['committed'],elapsed_h=elapsed,DG_available=available,DG_charge_inhibited_fuel_guard=guard,bess_present=case.system=='HYBRID',effective_DG_charge_permission=effective.allow_dg_to_bess)
            rows.append(r)
    except Exception as error:error.partial_records=rows;error.partial_segments=segments;raise
    cfg={'scenario':asdict(case),'settings':asdict(s),'fuel_model':'MDT_DERIVED','strategy':'S3' if case.system=='HYBRID' else 'S0','initial_fuel_l':case.fuel,'initial_SOC_active':case.soc if case.system=='HYBRID' else None,'BESS_active_capacity_kwh':300 if case.system=='HYBRID' else 0,'UPS_initial_AC_kwh':7.5,'DG_initial':'OFF_COLD','startup_h':1,'time_standard':'2025 source LST, hour0=Jan1T00:00; not civilBST','DG_failure_return':'Cold; original1h startup on next command','re_scaling':'Runtime availability multiplier, rawNASA and normalized files unchanged','P0R_inactive_battery':'PCS0 internal scaffolding, no activeBESS or storedenergy service credit'}
    return rows,segments,cfg
def imported_ledger(rows):
    result=[]
    for r in rows:
        result.append({'hour_index':r['hour_index'],'offset_start_h':0.,'offset_end_h':r['dt_h'],'duration_h':r['dt_h'],'dg_on_kw':r['dg_generated_kw'],'UPS_kw':r['ups_output_kw'],'ledger_basis':'DERIVED_EXISTING_HOURLY_AVERAGE_NOT_NEW_NATIVE_OR_SUBSTEP_OBSERVATION',**{t+k:r[t+k] for t in ['c4isr','aux','ev'] for k in ['_required_kw','_served_kw','_unserved_kw']}})
    return result
def metrics(rows,segments,cfg):
    c=cfg['scenario'];duration=c['hours'];m=event_metrics(rows,[{'id':c['id'],'start':c['start'],'duration':duration}])[0]
    total=lambda k:math.fsum(r[k]*r['dt_h'] for r in rows)
    m.update(scenario=c['id'],groups=c['groups'],system=c['system'],fuel_model='MDT_DERIVED',strategy=cfg['strategy'],initial_fuel_l=c['fuel'],initial_SOC=c['soc'] if c['system']=='HYBRID' else '',re_scale=c['re_scale'],DG_unavailable_elapsed_start_h=c['dg_off_start'] if c['dg_off_start']>=0 else '',DG_unavailable_elapsed_end_h=c['dg_off_end'] if c['dg_off_end']>=0 else '',start_timestamp_LST=rows[0]['timestamp_LST'],end_timestamp_exclusive_LST=(datetime(2025,1,1)+timedelta(hours=c['start']+duration)).isoformat(),reused_existing_case=c['reused'],grid_import_kwh=total('grid_import_kw'),grid_export_kwh=total('grid_export_kw'),pv_generated_used_kwh=total('pv_actual_kw'),wind_generated_used_kwh=total('wind_actual_kw'),renewable_generation_used_kwh=total('pv_actual_kw')+total('wind_actual_kw'),renewable_curtailed_kwh=total('renewable_curtailed_kw'),bess_charge_ac_kwh=total('bess_charge_kw'),bess_discharge_ac_kwh=total('bess_discharge_kw'),UPS_output_kwh=total('ups_output_kw'),DG_operating_h=math.fsum(r['dg_operating_duration_h'] for r in rows),DG_start_commands=sum(r['dg_start_command'] for r in rows),fuel_guard_hours=sum(bool(r.get('DG_charge_inhibited_fuel_guard',False)) for r in rows),status='PENDING_INDEPENDENT_VALIDATION')
    if c['system']=='P0R':
        for key in ['soc_initial','soc_final','soc_min','soc_max']:m[key]=''
    first=next((r for r in rows if r['c4isr_unserved_kw']>1e-7),None)
    piece=next((r for r in segments if r['c4isr_unserved_kw']>1e-7),None)
    m.update(first_critical_shortfall_elapsed_lower_h=first['t_start_h']-c['start'] if first else '',first_critical_shortfall_elapsed_upper_h=first['t_end_h']-c['start'] if first else '',first_critical_shortfall_model_segment_h=(piece['hour_index']-c['start']+piece['offset_start_h']) if piece else '',first_critical_shortfall_source_timestamp_LST=first['timestamp_LST'] if first else '',critical_shortfall_status='OBSERVED_IN_ENERGY_MODEL' if first else 'NONE_WITHIN_WINDOW_RIGHT_CENSORED',critical_energy_equivalent_h=m['c4_served_kwh']/30.,critical_shortfall_outer_hours=sum(r['dt_h'] for r in rows if r['c4isr_unserved_kw']>1e-7))
    exhaustion=next((r['t_start_h']-c['start']+b for r in rows if r['fuel_final_l']<=1e-9 and r['fuel_initial_l']>1e-9 for a,b,p in json.loads(r['dg_profile']) if p>0),None)
    m['fuel_exhaustion_elapsed_h']=exhaustion if exhaustion is not None else '';m['fuel_exhaustion_status']='EXHAUSTED' if exhaustion is not None else 'NOT_EXHAUSTED_WITHIN_WINDOW'
    return m
