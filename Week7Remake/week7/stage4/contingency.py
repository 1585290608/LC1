"""Versioned T10/T16 contingency dispatch: fuel deliveries, forced DG outages,
reserve and controller settings. Original S3/S3-v2 remain unmodified.

All events are deterministic counterfactuals. Hour-start refills, absent road
access and zero delivery emissions are explicitly NOT engineering assurances.
No event probabilities, EENS, reliability MTBF, native MDT or HOMER runs.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
import math
from week7.nextstage.screen import PV_PU,WIND_PU,LOADS
from week7.nextstage.dispatcher import instrumented_s3
from week7.outage_sensitivity import calculate_capex
from week7.nextstage.fleet_feedback import EVFleetFeedback
from models.core.components import Battery, Loads, PV, Wind, UPS
from models.core.simulate import Settings
from models.islanded.fuel_models import ResearchDiesel

@dataclass(frozen=True)
class Delivery:
    hour: int  # relative to start of outage
    requested_l: float


def _validate(start,hours,initial_fuel_l,deliveries,dg_off_periods,reserve_soc,stop_soc):
    if not isinstance(start,int) or not isinstance(hours,int) or start<0 or hours<=0 or start+hours>8760:
        raise ValueError('Outage start/duration must be integer hours within 8760')
    if not math.isfinite(initial_fuel_l) or not 0<=initial_fuel_l<=2000:
        raise ValueError('Initial fuel must fit the 2000 L tank')
    if not 0.1<=reserve_soc<=0.9 or not 0.1<=stop_soc<=0.9:
        raise ValueError('SOC settings outside physical bounds')
    for event in deliveries:
        if not isinstance(event.hour,int) or not 0<=event.hour<hours or not math.isfinite(event.requested_l) or event.requested_l<=0:
            raise ValueError('Invalid hour-start delivery event')
    if len(set(e.hour for e in deliveries))!=len(deliveries):raise ValueError('Duplicate refuelling hour')
    for a,b in dg_off_periods:
        if not isinstance(a,int) or not isinstance(b,int) or not 0<=a<b<=hours:
            raise ValueError('Invalid DG forced-outage interval')


def run(*, start:int, hours:int=168, pv_kw:float=100.,wind_kw:float=100.,bess_kwh:float=450.,
        initial_fuel_l:float=2000., deliveries:tuple[Delivery,...]=(),
        dg_off_periods:tuple[tuple[int,int],...]=(), reserve_soc:float=.30,
        stop_soc:float=.60,allow_dg_to_bess:bool=True,
        renewable_multiplier:float=1.,case:str='central', save_trace:bool=False, fleet_feedback:bool=False):
    _validate(start,hours,initial_fuel_l,deliveries,dg_off_periods,reserve_soc,stop_soc)
    if case not in LOADS:raise ValueError('Unknown load scenario')
    if min(pv_kw,wind_kw,bess_kwh)<0 or renewable_multiplier<0:raise ValueError('Negative hardware/resource')
    s=replace(Settings(),pv_kw=pv_kw,wind_kw=wind_kw,battery_kwh=bess_kwh,
              pcs_kw=90.,fuel_tank_l=2000.,initial_soc=.70,allow_dg_to_bess=allow_dg_to_bess,
              soc_reserve=reserve_soc)
    pv=PV(pv_kw,[p*renewable_multiplier for p in PV_PU]);wind=Wind(wind_kw,[w*renewable_multiplier for w in WIND_PU])
    battery=Battery(bess_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,s.initial_soc)
    diesel=ResearchDiesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,True).set_fuel_model('MDT_DERIVED')
    diesel.fuel_l=initial_fuel_l
    ups=UPS(s.ups_kw,s.ups_minutes).energy_kwh
    control={'committed':False,'stop_soc':stop_soc}
    original=LOADS[case];loads=Loads(original.c4isr,original.aux,list(original.ev))
    fleet=EVFleetFeedback(case) if fleet_feedback else None
    if fleet:fleet.precondition(start)
    arrivals={e.hour:e.requested_l for e in deliveries}
    keys=('c4isr_required_kw','c4isr_unserved_kw','aux_unserved_kw','ev_unserved_kw','dg_fuel_consumed_l')
    totals={k:0. for k in keys};max_ac=max_battery=max_fuel=0.;accepted_total=rejected_total=0.
    delivery_events=[];trace=[];errors=[];starts=0;dg_run_hours=0.;min_soc=1.;max_soc=0.;
    for elapsed in range(hours):
        hour=start+elapsed
        if elapsed in arrivals:
            requested=arrivals[elapsed];headroom=max(0.,s.fuel_tank_l-diesel.fuel_l)
            accepted=min(requested,headroom);rejected=requested-accepted
            diesel.fuel_l+=accepted;accepted_total+=accepted;rejected_total+=rejected
            delivery_events.append({'elapsed_hour':elapsed,'requested_l':requested,'accepted_l':accepted,
                                     'unaccepted_l':rejected,'fuel_after_delivery_l':diesel.fuel_l})
        forced_off=any(a<=elapsed<b for a,b in dg_off_periods)
        if forced_off:diesel.stop()
        diesel.enabled=not forced_off
        try:
            if fleet:loads.ev[hour]=fleet.before_hour(hour)
            row,ups=instrumented_s3(pv,wind,loads,battery,diesel,ups,hour,True,1.,s,control)
            if fleet:fleet.after_hour(row['ev_served_kw'])
            for k in keys:totals[k]+=row[k]
            max_ac=max(max_ac,abs(row['AC_residual_kwh']))
            max_battery=max(max_battery,abs(row['battery_residual_kwh']))
            max_fuel=max(max_fuel,abs(row['fuel_residual_l']))
            min_soc=min(min_soc,row['soc_final']);max_soc=max(max_soc,row['soc_final'])
            starts+=diesel.last_start_command
            dg_run_hours+=row['dg_operating_duration_h']
            if save_trace:
                trace.append({'elapsed_hour':elapsed,'forced_dg_off':int(forced_off),
                              'hour_start_delivery_accepted_l':delivery_events[-1]['accepted_l'] if elapsed in arrivals else 0.,
                              **row})
        except (ValueError,AssertionError,RuntimeError) as exc:
            errors.append({'elapsed_hour':elapsed,'global_hour':hour,'type':type(exc).__name__,'detail':str(exc)})
            break
    valid=not errors
    fuel_accounting=initial_fuel_l+accepted_total-totals['dg_fuel_consumed_l']-diesel.fuel_l
    if valid and abs(fuel_accounting)>1e-6:
        valid=False;errors.append({'type':'FuelLedgerError','detail':f'{fuel_accounting} L'})
    if valid and (min_soc<s.soc_min-1e-8 or max_soc>s.soc_max+1e-8):
        valid=False;errors.append({'type':'SOCBoundsError','detail':f'{min_soc},{max_soc}'})
    critical=totals['c4isr_unserved_kw'];aux=totals['aux_unserved_kw'];ev=totals['ev_unserved_kw']
    result={
        'case':case,'feedback_model':'EV_DYNAMIC_MISSION_CONSTRAINED' if fleet else 'EV_SCHEDULED_STATIC', 'start_hour':start,'hours':hours,'pv_kw':pv_kw,'wind_kw':wind_kw,'bess_kwh':bess_kwh,
        'initial_soc':.70,'initial_fuel_l':initial_fuel_l,'reserve_soc':reserve_soc,
        'dg_stop_soc':stop_soc,'dg_to_bess_allowed':allow_dg_to_bess,
        'dg_forced_off_periods':repr(dg_off_periods),'delivery_schedule':repr([(e.hour,e.requested_l) for e in deliveries]),
        'valid':valid,'status':'PYTHON_DETERMINISTIC_SCENARIO' if valid else 'QUARANTINED',
        'completed_hours':hours if valid else elapsed,
        'critical_required_kwh':totals['c4isr_required_kw'] if valid else None,
        'critical_ENS_kwh':critical if valid else None,'aux_ENS_kwh':aux if valid else None,
        'ev_ENS_kwh':ev if valid else None,'total_ENS_kwh':critical+aux+ev if valid else None,
        'critical_EA_fraction':(1-critical/totals['c4isr_required_kw']) if valid and totals['c4isr_required_kw']>0 else None,
        'fuel_consumed_l':totals['dg_fuel_consumed_l'],'fuel_delivered_l':accepted_total,
        'fuel_delivery_unaccepted_l':rejected_total,'fuel_end_l':diesel.fuel_l,
        'fuel_ledger_residual_l':fuel_accounting,'delivery_event_count':len(delivery_events),
        'generator_forced_off_hours':sum(any(a<=x<b for a,b in dg_off_periods) for x in range(hours)),
        'dg_operating_hours':dg_run_hours,'generator_start_commands':starts,
        'battery_soc_final':battery.soc,'battery_soc_min':min_soc if valid else None,
        'max_AC_residual_kwh':max_ac,'max_battery_residual_kwh':max_battery,'max_step_fuel_residual_l':max_fuel,
        'capex_gbp_illustrative':calculate_capex(pv_kw,wind_kw,bess_kwh),
        'errors':errors,'evidence_label':'EXPLORATORY_PYTHON_SCREENING','new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,
    }
    if fleet:result.update(fleet.summary())
    return result,trace,delivery_events
