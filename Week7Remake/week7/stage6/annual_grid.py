"""Stage 6 exploratory hourly grid-limited *energy* model for the revised camp.

NOT a power-flow, grid-forming, native MDT/HOMER, or economically optimised EMS.
The original A/B/S3/S3-v2 source and original economics modules are unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from models.core.components import Battery
from week7.nextstage.screen import LOADS, PV_PU, WIND_PU
from week7.nextstage.fleet_feedback import EVFleetFeedback

TIERS=('c4isr','aux','ev')

@dataclass(frozen=True)
class AnnualGridCase:
    scenario:str='central'
    pv_kw:float=100.
    wind_kw:float=100.
    bess_kwh:float=450.
    grid_limit_kw:float=100.
    grid_export_limit_kw:float=0.
    reserve_soc:float=.30
    initial_soc:float=.70
    terminal_target_soc:float=.70
    terminal_management_hours:int=48
    pcs_kw:float=90.
    eta_charge:float=.8944
    eta_discharge:float=.8944
    demand_feedback:bool=True


def validate(c:AnnualGridCase):
    if c.scenario not in LOADS:raise ValueError('Invalid provisional demand scenario')
    vals=(c.pv_kw,c.wind_kw,c.bess_kwh,c.grid_limit_kw,c.grid_export_limit_kw,c.pcs_kw)
    if any(not math.isfinite(x) or x<0 for x in vals) or c.bess_kwh<=0:raise ValueError('Invalid component rating')
    if any(not math.isfinite(x) for x in (c.reserve_soc,c.initial_soc,c.terminal_target_soc,c.eta_charge,c.eta_discharge)):
        raise ValueError('Nonfinite SOC/efficiency input')
    if not 0.1<=c.reserve_soc<=.9 or not 0.1<=c.initial_soc<=.9 or not 0.1<=c.terminal_target_soc<=.9:
        raise ValueError('Invalid state-of-charge input')
    if not 0<c.eta_charge<=1 or not 0<c.eta_discharge<=1:raise ValueError('Invalid efficiency')
    if not isinstance(c.terminal_management_hours,int) or not 0<=c.terminal_management_hours<=8760:
        raise ValueError('Invalid terminal window')
    if not isinstance(c.demand_feedback,bool):raise ValueError('Invalid EV feedback switch')


def dispatch_step(c, battery, tier_loads, re_pv, re_wind, hour):
    """One-hour AC energy allocation, highest priority to critical loads.

    Battery discharge precedes grid import by design (legacy normal-year logic).
    When 100 kW grid limit cannot support loads, record *unserved* tier energy;
    never silently top up the feeder or invent generator service.
    """
    if any(not math.isfinite(x) or x<0 for x in (*tier_loads.values(),re_pv,re_wind)):
        raise ValueError('Negative/nonfinite hourly source/load')
    before=battery.soc
    battery.begin_step()
    terminal=bool(c.terminal_management_hours and hour>=8760-c.terminal_management_hours)
    battery.soc_reserve=c.terminal_target_soc if terminal else c.reserve_soc
    demand=math.fsum(tier_loads[t] for t in TIERS)
    re_available=re_pv+re_wind
    renewable_to_load=min(re_available,demand)
    shortage=demand-renewable_to_load
    from_battery=battery.discharge(shortage,dt_h=1.)
    shortage=max(0.,shortage-from_battery)
    from_grid=min(shortage,c.grid_limit_kw)
    served=demand-shortage+from_grid
    served=max(0.,min(demand,served))
    service_left=served
    allocated={}
    for t in TIERS:
        allocated[t]=min(tier_loads[t],service_left)
        service_left=max(0.,service_left-allocated[t])
    if abs(service_left)>1e-6:raise AssertionError('Tier allocation mismatch')
    unserved={t:max(0.,tier_loads[t]-allocated[t]) for t in TIERS}

    re_surplus=max(0.,re_available-renewable_to_load)
    re_charge=grid_charge=0.
    if from_battery<=1e-10:
        target_soc=c.terminal_target_soc if terminal else .90
        eligible_ac=max(0.,(target_soc-battery.soc)*c.bess_kwh/c.eta_charge)
        re_offer=min(re_surplus,c.pcs_kw,eligible_ac)
        grid_offer=(min(max(0.,eligible_ac-re_offer),max(0.,c.grid_limit_kw-from_grid),max(0.,c.pcs_kw-re_offer))
                    if terminal and sum(unserved.values())<1e-9 else 0.)
        total_charge=battery.charge(re_offer+grid_offer,dt_h=1.)
        re_charge=min(total_charge,re_offer)
        grid_charge=max(0.,total_charge-re_charge)
        re_surplus=max(0.,re_surplus-re_charge)
    exported=min(re_surplus,c.grid_export_limit_kw)
    curtailed=max(0.,re_surplus-exported)
    re_used=re_available-curtailed
    imported=from_grid+grid_charge
    charge=re_charge+grid_charge
    ac_residual=re_used+imported+from_battery-served-charge-exported
    battery_residual=(battery.soc-before)*c.bess_kwh-charge*c.eta_charge+from_battery/c.eta_discharge
    if abs(ac_residual)>1e-6 or abs(battery_residual)>1e-6:
        raise AssertionError(f'Energy balance error AC {ac_residual}, DC {battery_residual}')
    if imported>c.grid_limit_kw+1e-7 or imported>1e-8 and exported>1e-8:
        raise AssertionError('Invalid grid import or simultaneous import/export')
    if from_battery>1e-8 and charge>1e-8:raise AssertionError('Battery simultaneous direction')
    if not .1-1e-8<=battery.soc<=.9+1e-8:raise AssertionError('SOC limits')
    result={'hour_index':hour,'c4isr_required_kw':tier_loads['c4isr'],'aux_required_kw':tier_loads['aux'],
        'ev_required_kw':tier_loads['ev'],'total_required_kw':demand,
        **{t+'_served_kw':allocated[t] for t in TIERS},**{t+'_unserved_kw':unserved[t] for t in TIERS},
        'total_served_kw':served,'total_unserved_kw':sum(unserved.values()),
        'pv_available_kw':re_pv,'wind_available_kw':re_wind,'renewable_used_kw':re_used,
        'renewable_curtailed_kw':curtailed,'grid_import_kw':imported,'grid_export_kw':exported,
        'grid_to_load_kw':from_grid,'grid_to_bess_kw':grid_charge,
        'bess_charge_kw':charge,'bess_discharge_kw':from_battery,
        'battery_soc_initial':before,'battery_soc_final':battery.soc,
        'battery_loss_kwh':charge*(1-c.eta_charge)+from_battery*(1/c.eta_discharge-1),
        'ac_residual_kwh':ac_residual,'battery_residual_kwh':battery_residual,
        'grid_at_capacity':int(imported>=c.grid_limit_kw-1e-8),'terminal_management':int(terminal)}
    return result


def run_year(c:AnnualGridCase,trace:bool=False):
    validate(c)
    b=Battery(c.bess_kwh,c.pcs_kw,c.eta_charge,c.eta_discharge,.1,.9,c.reserve_soc,c.initial_soc)
    original=LOADS[c.scenario]
    fleet=EVFleetFeedback(c.scenario) if c.demand_feedback else None
    total_keys=('total_required_kw','total_served_kw','total_unserved_kw','grid_import_kw','grid_export_kw',
        'renewable_used_kw','renewable_curtailed_kw','bess_charge_kw','bess_discharge_kw','battery_loss_kwh',
        'c4isr_required_kw','c4isr_unserved_kw','aux_required_kw','aux_unserved_kw','ev_required_kw','ev_unserved_kw')
    sums={x:0. for x in total_keys}
    max_ac=max_dc=0.;peak_demand=0.;hours_ens=hours_critical=hours_grid_limit=0
    all_rows=[]
    for h in range(8760):
        ev=fleet.before_hour(h) if fleet else original.ev[h]
        req={'c4isr':original.c4isr[h],'aux':original.aux[h],'ev':ev}
        r=dispatch_step(c,b,req,c.pv_kw*PV_PU[h],c.wind_kw*WIND_PU[h],h)
        if fleet:fleet.after_hour(r['ev_served_kw'])
        for x in total_keys:sums[x]+=r[x]
        peak_demand=max(peak_demand,r['total_required_kw'])
        max_ac=max(max_ac,abs(r['ac_residual_kwh']))
        max_dc=max(max_dc,abs(r['battery_residual_kwh']))
        hours_ens+=r['total_unserved_kw']>1e-7
        hours_critical+=r['c4isr_unserved_kw']>1e-7
        hours_grid_limit+=r['grid_at_capacity']
        if trace:all_rows.append(r)
    readiness=fleet.summary() if fleet else {}
    return {'scenario':c.scenario,'pv_kw':c.pv_kw,'wind_kw':c.wind_kw,'bess_kwh':c.bess_kwh,
        'pcs_kw':c.pcs_kw,'grid_import_limit_kw':c.grid_limit_kw,'grid_export_limit_kw':c.grid_export_limit_kw,
        'hours':8760,'controller':'GRID_LIMITED_PYTHON_ENERGY_BALANCE_BESS_BEFORE_GRID',
        'ev_feedback':'DYNAMIC_MISSION_SOC' if fleet else 'FIXED_SCHEDULE',
        **{k.replace('_kw','_kwh'):v for k,v in sums.items()},
        'hours_any_unserved':hours_ens,'hours_critical_unserved':hours_critical,
        'hours_grid_at_import_limit':hours_grid_limit,'max_hourly_load_kw':peak_demand,
        'soc_initial':c.initial_soc,'soc_end':b.soc,'soc_terminal_target':c.terminal_target_soc,
        'terminal_soc_target_met':b.soc>=c.terminal_target_soc-1e-6,
        'max_hourly_ac_residual_kwh':max_ac,'max_hourly_battery_residual_kwh':max_dc,
        'nondeferrable_infrastructure_ENS_kwh':sums['c4isr_unserved_kw']+sums['aux_unserved_kw'],
        'EV_charging_slot_deficit_kwh_DEFERABLE':sums['ev_unserved_kw'],
        'hourly_requested_service_shortfall_kwh_NOT_EENS':sums['total_unserved_kw'],
        'ev_charge_demand_may_be_re_requested':True,
        'unserved_load_zero':hours_ens==0,
        'critical_aux_service_gate':'NO_INFRASTRUCTURE_SHORTFALL' if sums['c4isr_unserved_kw']+sums['aux_unserved_kw']<1e-6 else 'FAIL_INFRASTRUCTURE_SERVICE',
        'service_gate':'NO_SHORTFALL_ENERGY_ONLY' if hours_ens==0 else 'FAIL_SCHEDULED_HOURLY_REQUESTED_SERVICE_INCLUDES_DEFERRABLE_EV',
        'evidence_class':'PROVISIONAL_UNVALIDATED_PYTHON_8760H_GRID_LIMITED_ENERGY_MODEL',
        'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,**{k:v for k,v in readiness.items() if k!='end_soc_by_vehicle'}},all_rows
