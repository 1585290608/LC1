"""Matched islanded experiments; chronological piecewise DG profiles are retained."""
from dataclasses import asdict,replace
from datetime import datetime,timedelta
import json
from ..core.components import Battery,UPS
from ..core.simulate import Settings,build_model,step,event_metrics,EPS
from .commitment import committed_step
from .fuel_models import ResearchDiesel

def run_case(strategy='S0',fuel_model='FIXED_025',hours=168,settings=None,start=0,models=None,initial_fuel=None):
    if strategy not in ('S0','S1','S2','S3'):raise ValueError(strategy)
    s=replace(settings or Settings(),allow_dg_to_bess=strategy in ('S1','S3'))
    pv,wind,loads=models or build_model(s)
    b=Battery(s.battery_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,s.initial_soc)
    d=ResearchDiesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,s.dg_enabled).set_fuel_model(fuel_model)
    if initial_fuel is not None:d.fuel_l=initial_fuel
    ups=UPS(s.ups_kw,s.ups_minutes).energy_kwh
    controller={'committed':False,'stop_soc':.6};rows=[]
    for h in range(start,start+hours):
        fn=committed_step if strategy in ('S2','S3') else step
        kwargs={'controller':controller} if strategy in ('S2','S3') else {}
        r,ups=fn(pv,wind,loads,b,d,ups,h,True,s.dt_h,s,**kwargs)
        r.update(t_start_h=h,t_end_h=h+s.dt_h,timestamp_LST=(datetime(2025,1,1)+timedelta(hours=h)).isoformat(),dg_profile=json.dumps(d.profile,separators=(',',':')),dg_start_command=d.last_start_command,committed=controller['committed'])
        rows.append(r)
    return rows,asdict(s)

def summary(rows,strategy,fuel_model,settings):
    start=rows[0]['t_start_h'];hours=sum(r['dt_h'] for r in rows)
    m=event_metrics(rows,[{'id':'D0','start':start,'duration':hours}])[0]
    m.update(strategy=strategy,fuel_model=fuel_model,status='PENDING_INDEPENDENT_CHECK',dg_operating_h=sum(r['dg_operating_duration_h'] for r in rows),dg_start_commands=sum(r['dg_start_command'] for r in rows))
    spans=[]
    for r in rows:
        for a,b,p in json.loads(r['dg_profile']):
            if p>EPS:
                a+=r['t_start_h'];b+=r['t_start_h']
                if spans and abs(spans[-1][1]-a)<1e-9:spans[-1][1]=b
                else:spans.append([a,b])
    m['dg_generation_starts']=len(spans)
    m['dg_generation_stops']=sum(b<rows[-1]['t_end_h']-EPS for a,b in spans)
    m['fuel_exhaustion_time_h']=next((r['t_start_h']+b for r in rows if r['fuel_final_l']<=EPS and r['fuel_initial_l']>EPS for a,b,p in json.loads(r['dg_profile']) if p>EPS),'')
    total=lambda k:sum(r[k]*r['dt_h'] for r in rows)
    m.update(bess_charge_ac_kwh=total('bess_charge_kw'),bess_discharge_ac_kwh=total('bess_discharge_kw'),battery_loss_kwh=sum(r['battery_loss_kwh'] for r in rows),renewable_curtailment_kwh=total('renewable_curtailed_kw'),pv_actual_kwh=total('pv_actual_kw'),wind_actual_kwh=total('wind_actual_kw'),critical_energy_equivalent_h=m['c4_served_kwh']/30.,critical_shortage_outer_interval_h=sum(r['dt_h'] for r in rows if r['c4isr_unserved_kw']>1e-8))
    return m
