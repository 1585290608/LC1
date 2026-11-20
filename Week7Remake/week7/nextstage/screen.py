"""Versioned WP2/WP4 numerical screening, separate from frozen Week7 outputs.
No native MDT or HOMER Pro runs. Costs are illustrative CAPEX only, not NPC.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from dataclasses import replace
from week7.outage_sensitivity import read_load, calculate_capex, pareto_status,write_csv
from week7.nextstage.dispatcher import instrumented_s3
from week7.nextstage.fleet_feedback import EVFleetFeedback
from models.core.components import Battery,Loads,PV,Wind,UPS
from models.core.simulate import Settings,read_col
from models.islanded.fuel_models import ResearchDiesel

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PV_PU=read_col('v6_solar_pu_index_value.csv',1)
WIND_PU=read_col('v6_wind_pu_index_value.csv',1)
if len(PV_PU)!=8760 or len(WIND_PU)!=8760:raise ValueError('Bad renewable inputs')
LOADS={k:read_load(k) for k in ('low','central','high')}


def simulate(case='central',pv_kw=50.,wind_kw=50.,bess_kwh=300.,start=0,hours=168,
             initial_soc=.7,fuel_l=2000.,dg_off=None,renewable_multiplier=1.,
             fleet_feedback=False,save_trace=False):
    if start<0 or hours<1 or start+hours>8760:raise ValueError('Window outside source year')
    if not 0<=fuel_l<=2000:raise ValueError('Exceeds actual 2000L tank assumption')
    s=replace(Settings(),pv_kw=pv_kw,wind_kw=wind_kw,battery_kwh=bess_kwh,
              pcs_kw=90.,fuel_tank_l=2000.,initial_soc=initial_soc,allow_dg_to_bess=True)
    pv=PV(pv_kw,[p*renewable_multiplier for p in PV_PU])
    wind=Wind(wind_kw,[p*renewable_multiplier for p in WIND_PU])
    bat=Battery(bess_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,s.initial_soc)
    diesel=ResearchDiesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,True).set_fuel_model('MDT_DERIVED')
    diesel.fuel_l=fuel_l
    ups=UPS(s.ups_kw,s.ups_minutes).energy_kwh
    controller={'committed':False,'stop_soc':.6}
    original=LOADS[case]
    loads=Loads(original.c4isr,original.aux,list(original.ev))
    fleet=EVFleetFeedback(case) if fleet_feedback else None
    if fleet:fleet.precondition(start)
    trace=[];errors=[]
    totals={x:0. for x in ('c4isr_required_kw','c4isr_unserved_kw','aux_unserved_kw','ev_unserved_kw','dg_fuel_consumed_l')}
    max_ac=max_dc=0.;charge_discharge_count=0
    for elapsed in range(hours):
        h=start+elapsed
        enabled=(dg_off is None or not(dg_off[0]<=elapsed<dg_off[1]))
        if not enabled:diesel.stop()
        diesel.enabled=enabled
        try:
            if fleet:loads.ev[h]=fleet.before_hour(h)
            r,ups=instrumented_s3(pv,wind,loads,bat,diesel,ups,h,True,1.,s,controller)
            if fleet:fleet.after_hour(r['ev_served_kw'])
            for key in totals:totals[key]+=r[key]
            max_ac=max(max_ac,abs(r['AC_residual_kwh']))
            max_dc=max(max_dc,abs(r['battery_residual_kwh']))
            if r['bess_charge_kw']>1e-7 and r['bess_discharge_kw']>1e-7:charge_discharge_count+=1
            if save_trace:trace.append({'elapsed_hour':elapsed,'hour_index':h,**r})
        except (ValueError,AssertionError,RuntimeError) as e:
            errors.append({'elapsed_hour':elapsed,'hour_index':h,'error':type(e).__name__,'message':str(e)})
            break
    valid=not errors
    result={'scenario':case,'feedback_model':'EV_DYNAMIC_MISSION_CONSTRAINED' if fleet else 'EV_SCHEDULED_STATIC',
            'pv_kw':pv_kw,'wind_kw':wind_kw,'bess_kwh':bess_kwh,'pcs_kw':90.,'dg_kw':100.,
            'start_hour':start,'requested_h':hours,'completed_h':sum(1 for _ in range(hours)) if valid else elapsed,
            'initial_soc':initial_soc,'initial_fuel_l':fuel_l,
            'controller':'S3_v2_fuel_exhaustion_anticipatory_no_same_hour_charging',
            'valid':valid,'status':'PYTHON_SCREEN_COMPLETE' if valid else 'QUARANTINED',
            'critical_required_kwh':totals['c4isr_required_kw'] if valid else None,
            'critical_ENS_kwh':totals['c4isr_unserved_kw'] if valid else None,
            'aux_ENS_kwh':totals['aux_unserved_kw'] if valid else None,
            'ev_ENS_kwh':totals['ev_unserved_kw'] if valid else None,
            'total_ENS_kwh':sum(totals[t+'_unserved_kw'] for t in ('c4isr','aux','ev')) if valid else None,
            'critical_EA_fraction':(1-totals['c4isr_unserved_kw']/totals['c4isr_required_kw']) if valid and totals['c4isr_required_kw']>0 else None,
            'diesel_fuel_used_l':totals['dg_fuel_consumed_l'] if valid else None,
            'fuel_end_l':diesel.fuel_l if valid else None,'bess_end_soc':bat.soc if valid else None,
            'capex_gbp_illustrative':calculate_capex(pv_kw,wind_kw,bess_kwh),
            'max_AC_residual_kwh':max_ac,'max_battery_residual_kwh':max_dc,
            'bess_same_hour_both_directions':charge_discharge_count,
            'issues':errors,'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,
            'dispatch_limitations':'Assumed AC reference, idealised DG fuel, hourly EMS; not electrical/transient certification.'}
    if fleet:result.update(fleet.summary())
    return result,trace,(fleet.rows if fleet and save_trace else None)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'outputs')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    nine=[]
    for pv_kw in (50.,75.,100.):
        for bess in (300.,450.,600.):
            m,_,_=simulate(pv_kw=pv_kw,wind_kw=pv_kw,bess_kwh=bess)
            nine.append(m)
    pareto_status(nine)
    write_csv(out/'nine_candidate_v2_168h.csv',nine)
    seasonal=[]
    # Four fixed weather months on the original 2025 LST weather series.
    from datetime import datetime
    starts={x:int((datetime(2025,m,1)-datetime(2025,1,1)).total_seconds()/3600)
            for x,m in [('winter',1),('spring',4),('summer',7),('autumn',10)]}
    for season,start in starts.items():
        for duration in (24,72,168):
            for pv_kw in (50.,75.,100.):
                for bess in (300.,450.,600.):
                    m,_,_=simulate(pv_kw=pv_kw,wind_kw=pv_kw,bess_kwh=bess,start=start,hours=duration)
                    m['season']=season;seasonal.append(m)
    write_csv(out/'seasonal_nine_candidates_24_72_168h.csv',seasonal)
    # Mission readiness is measured by re-dispatching EV charging hours as a
    # feedback-controlled load, NOT using the perfect-grid pre-generated EV SOC.
    vehicle=[]
    for season,start in starts.items():
        for duration in (24,72,168):
            for pv_kw,bess in [(50.,300.),(75.,450.),(100.,450.),(100.,600.)]:
                m,trace,fleettrace=simulate(pv_kw=pv_kw,wind_kw=pv_kw,bess_kwh=bess,start=start,hours=duration,fleet_feedback=True,save_trace=(season=='winter' and duration==168 and pv_kw==50))
                m['season']=season;vehicle.append(m)
                if trace:write_csv(out/'winter_168h_original_equipment_plant_trace.csv',trace)
                if fleettrace:write_csv(out/'winter_168h_original_equipment_EV_trace.csv',fleettrace)
    write_csv(out/'mission_readiness_feedback_matrix.csv',vehicle)
    contingencies=[]
    for label,kw in [('BASE',{}),('FUEL_500L',{'fuel_l':500.}),('DG_OFF_H24_TO_H48',{'dg_off':(24,48)}),
                      ('LOW_RE_60PCT',{'renewable_multiplier':.6}),('INITIAL_BESS_SOC_30PCT',{'initial_soc':.3}),
                      ('FUEL_500L_AND_DG_OFF',{'fuel_l':500.,'dg_off':(24,48)})]:
        m,_,_=simulate(**kw);m['stress_case']=label;contingencies.append(m)
    write_csv(out/'contingency_v2_168h.csv',contingencies)
    # Distinguish vehicle readiness impacts from demand-only contingency ENS.
    dynamic_contingencies=[]
    for label,kw in [('BASE',{}),('FUEL_500L',{'fuel_l':500.}),('DG_OFF_H24_TO_H48',{'dg_off':(24,48)}),
                      ('LOW_RE_60PCT',{'renewable_multiplier':.6}),('INITIAL_BESS_SOC_30PCT',{'initial_soc':.3}),
                      ('FUEL_500L_AND_DG_OFF',{'fuel_l':500.,'dg_off':(24,48)})]:
        m,_,_=simulate(fleet_feedback=True,**kw)
        m['stress_case']=label;dynamic_contingencies.append(m)
    write_csv(out/'contingency_dynamic_EV_mission_readiness_168h.csv',dynamic_contingencies)
    # Preliminary 100 kW grid import ceiling diagnostic, excluding BESS/generator
    # dispatch: this is NOT a solved grid-connected load-flow.
    import_limit=100.
    import_diagnostic=[]
    for case in ('low','central','high'):
        demand=LOADS[case]
        raw=[max(0.,demand.c4isr[h]+demand.aux[h]+demand.ev[h]-50*PV_PU[h]-50*WIND_PU[h]) for h in range(8760)]
        import_diagnostic.append({'scenario':case,'assumed_import_limit_kw':import_limit,
            'max_required_import_kw_before_dispatch':max(raw),
            'hours_exceeding_import_limit_before_dispatch':sum(v>import_limit+1e-7 for v in raw),
            'unserved_if_only_GRID_and_PV50_WIND50_kwh':sum(max(0.,v-import_limit) for v in raw),
            'status':'SCREENING_ONLY_no_BESS_no_DG_no_grid_forming_or_power_flow'})
    write_csv(out/'preliminary_grid_import_limit_diagnostic.csv',import_diagnostic)
    summary={'class':'RESEARCH_SIMULATION_NOT_NATIVE_MDT_HOMER_OR_REAL_DEPLOYMENT',
             'nine_candidate_cases':len(nine),'nine_candidate_valid':sum(x['valid'] for x in nine),
             'seasonal_cases':len(seasonal),'seasonal_valid':sum(x['valid'] for x in seasonal),
             'dynamic_fleet_cases':len(vehicle),'dynamic_fleet_valid':sum(x['valid'] for x in vehicle),
             'stress_cases':len(contingencies),'stress_valid':sum(x['valid'] for x in contingencies),
             'dynamic_stress_cases':len(dynamic_contingencies),'dynamic_stress_valid':sum(x['valid'] for x in dynamic_contingencies),
             'bess_simultaneous_hourly_count':sum(x['bess_same_hour_both_directions'] for x in nine+seasonal+vehicle+contingencies+dynamic_contingencies),
             'native_MDT_cross_validation':0,'HOMER_Pro_reoptimisation':0,
             'quarantined':[{'case':r['scenario'],'start':r['start_hour'],'hours':r['requested_h'],'pv':r['pv_kw'],'bess':r['bess_kwh'],'issues':r['issues']} for r in nine+seasonal+vehicle+contingencies+dynamic_contingencies if not r['valid']]}
    (out/'summary_v2.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='quarantined'},indent=2))
if __name__=='__main__':main()
