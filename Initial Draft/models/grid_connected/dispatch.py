"""Isolated P1/P3 annual self-consumption extension, reusing frozen Draft2 battery physics."""
from pathlib import Path
from datetime import datetime,timedelta
import json,math
from dataclasses import dataclass,asdict
from ..core.components import Battery
from ..core.simulate import Settings,build_model
PROTOCOL_PATH=Path(__file__).resolve().parent / "config" / "annual-dispatch.json"
class InfeasibleAnnualCase(RuntimeError):pass
@dataclass(frozen=True)
class Case:
    name:str
    kind:str='HYBRID'
    reserve:float=.3
    export_kw:float=0.
    wind_scale:float=1.
def cases():
    result=[Case('P0_GRID_ONLY','P0'),Case('P0R_GRID_DG_UPS','P0R')]
    for export in (0,20):
        for reserve in (.3,.5,.7):result.append(Case(('P1' if reserve==.3 else 'P3')+f'_E{export}_R{int(reserve*100)}',reserve=reserve,export_kw=export))
        for scale in (.6,.8):result.append(Case(f'SENS_WIND{int(scale*100)}_E{export}_R30',export_kw=export,wind_scale=scale))
    return result

def dispatch_hour(req,pv_available,wind_available,battery,terminal,protocol):
    grid=protocol['grid'];s=protocol['battery'];load=sum(req.values());re=pv_available+wind_available;re_load=min(re,load)
    deficit=max(0.,load-re_load);surplus=max(0.,re-re_load);initial_soc=battery.soc if battery else None
    dis=charge=re_charge=grid_charge=0.
    if battery:
        battery.begin_step();battery.soc_reserve=s['terminal_soc'] if terminal else protocol['reserve']
        dis=battery.discharge(deficit,allow_reserve=False,dt_h=1.);deficit-=dis
    if deficit>grid['import_limit_kw']+1e-9:raise InfeasibleAnnualCase('Load exceeds finite grid import headroom')
    grid_load=deficit
    if battery and dis<=1e-10:
        ceiling=s['terminal_soc'] if terminal else s['soc_max']
        needed=max(0.,(ceiling-battery.soc)*battery.energy_kwh/battery.eta_charge)
        re_offer=min(surplus,battery.pcs_kw,needed)
        grid_offer=min(max(0.,needed-re_offer),max(0.,grid['import_limit_kw']-grid_load),max(0.,battery.pcs_kw-re_offer)) if terminal else 0.
        charge=battery.charge(re_offer+grid_offer,dt_h=1.)
        re_charge=min(charge,re_offer);grid_charge=charge-re_charge;surplus-=re_charge
    export=min(surplus,protocol['export_kw']);curtail=surplus-export
    pv_curt=curtail*pv_available/re if re else 0.;wind_curt=curtail-pv_curt
    actual_pv=pv_available-pv_curt;actual_wind=wind_available-wind_curt;imported=grid_load+grid_charge
    ac=actual_pv+actual_wind+imported+dis-load-charge-export
    dc=((battery.soc-initial_soc)*battery.energy_kwh-charge*battery.eta_charge+dis/battery.eta_discharge) if battery else 0.
    if max(abs(ac),abs(dc))>1e-7:raise AssertionError('Annual AC/DC accounting failed')
    if imported>grid['import_limit_kw']+1e-8 or imported>1e-8 and export>1e-8:raise InfeasibleAnnualCase('Invalid grid import/export')
    if dis>1e-9 and charge>1e-9:raise InfeasibleAnnualCase('Simultaneous battery directions')
    r={'pv_available_kw':pv_available,'wind_available_kw':wind_available,'pv_actual_kw':actual_pv,'wind_actual_kw':actual_wind,'renewable_curtailed_kw':curtail,'re_to_load_kw':re_load,'re_to_bess_kw':re_charge,'grid_to_load_kw':grid_load,'grid_to_bess_kw':grid_charge,'grid_import_kw':imported,'grid_export_kw':export,'bess_charge_kw':charge,'bess_discharge_kw':dis,'soc_initial':initial_soc if battery else '', 'soc_final':battery.soc if battery else '', 'battery_delta_stored_kwh':(battery.soc-initial_soc)*battery.energy_kwh if battery else 0.,'battery_loss_kwh':charge*(1-s['eta_charge'])+dis*(1/s['eta_discharge']-1),'terminal_management':terminal,'active_discharge_floor':battery.soc_reserve if battery else '', 'AC_residual_kwh':ac,'DC_residual_kwh':dc,'dg_generated_kw':0.,'dg_fuel_consumed_l':0.,'ups_output_kw':0.}
    for tier,value in req.items():r.update({tier+'_required_kw':value,tier+'_served_kw':value,tier+'_unserved_kw':0.})
    return r

def run(case,protocol=None):
    p=json.loads(PROTOCOL_PATH.read_text()) if protocol is None else json.loads(json.dumps(protocol))
    if case.kind not in ('P0','P0R','HYBRID') or not .1<=case.reserve<=.7 or not 0<=case.export_kw<=20 or not 0<=case.wind_scale<=1:raise ValueError('Outside declared case domain')
    p.update(reserve=case.reserve,export_kw=case.export_kw)
    hw=p['hardware'];bs=p['battery'];s=Settings(pv_kw=hw['pv_kw'] if case.kind=='HYBRID' else 0,wind_kw=hw['wind_kw'] if case.kind=='HYBRID' else 0)
    pv,wind,loads=build_model(s)
    b=Battery(hw['battery_kwh'],hw['pcs_kw'],bs['eta_charge'],bs['eta_discharge'],bs['soc_min'],bs['soc_max'],case.reserve,bs['initial_soc']) if case.kind=='HYBRID' else None
    rows=[];hours=p['time']['hours']
    for h in range(hours):
        terminal=bool(b and h>=hours-p['terminal_policy']['last_hours'])
        try:r=dispatch_hour(loads.required(h),pv.available(h),wind.available(h)*case.wind_scale,b,terminal,p)
        except Exception as error:
            error.partial_records=rows
            raise
        rows.append({'hour_index':h,'t_start_h':h,'t_end_h':h+1,'dt_h':1.,'timestamp_LST':(datetime(2025,1,1)+timedelta(hours=h)).isoformat(),**r})
    if b and abs(b.soc-bs['terminal_soc'])>1e-9:
        error=InfeasibleAnnualCase('TerminalSOC not attained by paid feasible dispatch; no reset allowed');error.partial_records=rows
        raise error
    total=lambda k:math.fsum(r[k] for r in rows)
    metrics={'case':case.name,'kind':case.kind,'reserve_soc':case.reserve if b else '', 'export_limit_kw':case.export_kw if b else 0.,'wind_scale':case.wind_scale if b else 0.,'hours':hours,'status':'PENDING_INDEPENDENT_CHECK','soc_initial':rows[0]['soc_initial'],'soc_final':rows[-1]['soc_final'],'soc_min':min([r['soc_initial'] for r in rows]+[r['soc_final'] for r in rows]) if b else '', 'soc_max':max(r['soc_final'] for r in rows) if b else ''}
    for name,key in [('grid_import_kwh','grid_import_kw'),('grid_export_kwh','grid_export_kw'),('renewable_curtailment_kwh','renewable_curtailed_kw'),('pv_generated_kwh','pv_actual_kw'),('wind_generated_kwh','wind_actual_kw'),('bess_charge_ac_kwh','bess_charge_kw'),('bess_discharge_ac_kwh','bess_discharge_kw'),('grid_to_bess_kwh','grid_to_bess_kw'),('terminal_grid_to_bess_kwh','grid_to_bess_kw'),('battery_loss_kwh','battery_loss_kwh')]:metrics[name]=total(key)
    metrics['dg_generated_kwh']=total('dg_generated_kw');metrics['fuel_consumed_l']=total('dg_fuel_consumed_l');metrics['load_required_kwh']=sum(total(t+'_required_kw') for t in ('c4isr','aux','ev'))
    for t in ('c4isr','aux','ev'):metrics[t+'_ENS_kwh']=total(t+'_unserved_kw')
    return rows,metrics,{'case':asdict(case),'protocol':p,'terminal_actual_change_dc_kwh':(b.soc-bs['initial_soc'])*hw['battery_kwh'] if b else None,'software':'Draft3B annual extension; frozen Draft2 Battery reused; no native solver'}
