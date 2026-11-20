"""Preliminary, deterministic WP2/WP4 screening using original LC1 Python physics.
NOT HOMER capacity optimisation and NOT native MDT cross-validation.
Same 2025 source-LST weather, outage start, 70% initial SOC, 2000L fuel and S3 policy.
Scaling PV and wind capacities assumes their *normalised* profiles remain applicable.
"""
from __future__ import annotations
import argparse,csv,json,math
from dataclasses import asdict,replace
from pathlib import Path
from models.core.components import Battery,Loads,PV,Wind,UPS
from models.core.simulate import Settings,read_col,InfeasibleOperatingPoint
from models.islanded.fuel_models import ResearchDiesel
from models.islanded.service_dispatch import instrumented_s3

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent
COSTS={'pv_per_kw':1257.,'wind_per_kw':4000.,'battery_dc_per_kwh':400.,'pcs_per_kw':250.,'dg_100kw':30000.,'ups_30kw':20000.,'fixed_installation':60000.,'tank_fixed':8000.,'tank_per_l':3.}


def read_load(case):
 with (HERE/'outputs'/f'{case}_load_8760.csv').open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
 assert len(rows)==8760
 return Loads([float(r['c4isr_kw']) for r in rows],[float(r['aux_kw']) for r in rows],[float(r['ev_kw']) for r in rows])

def calculate_capex(pv,wind,bess,pcs=90):
 return pv*COSTS['pv_per_kw']+wind*COSTS['wind_per_kw']+bess*COSTS['battery_dc_per_kwh']+pcs*COSTS['pcs_per_kw']+COSTS['dg_100kw']+COSTS['ups_30kw']+COSTS['fixed_installation']+COSTS['tank_fixed']+2000*COSTS['tank_per_l']

def run(case,load,pv_pu,wind_pu,pv_kw=50.,wind_kw=50.,bess_kwh=300.,start=0,hours=168,fuel_l=2000.,dg_off_start=None,dg_off_end=None,renewable_multiplier=1.,save_trace=False):
 s=replace(Settings(),pv_kw=float(pv_kw),wind_kw=float(wind_kw),battery_kwh=float(bess_kwh),pcs_kw=90.,fuel_tank_l=2000.,initial_soc=.7,allow_dg_to_bess=True)
 pv=PV(s.pv_kw,[p*renewable_multiplier for p in pv_pu]);wind=Wind(s.wind_kw,[p*renewable_multiplier for p in wind_pu]);b=Battery(s.battery_kwh,s.pcs_kw,s.eta_charge,s.eta_discharge,s.soc_min,s.soc_max,s.soc_reserve,s.initial_soc)
 d=ResearchDiesel(s.dg_kw,s.dg_min_fraction,s.fuel_l_per_kwh,s.fuel_tank_l,s.dg_startup_h,True).set_fuel_model('MDT_DERIVED');d.fuel_l=fuel_l
 ups=UPS(s.ups_kw,s.ups_minutes).energy_kwh
 controller={'committed':False,'stop_soc':.6};rows=[];issues=[]
 for elapsed in range(hours):
  h=start+elapsed;enabled=not(dg_off_start is not None and dg_off_start<=elapsed<dg_off_end)
  if not enabled:d.stop()
  d.enabled=enabled
  try:
   r,ups=instrumented_s3(pv,wind,load,b,d,ups,h,True,1.,s,controller)
  except (ValueError,AssertionError,RuntimeError) as exc:
   issues.append({'elapsed_hour':elapsed,'hour_index':h,'error':type(exc).__name__,'message':str(exc)})
   break
  r['elapsed_hour']=elapsed;r['hour_index']=h;r['generator_available']=int(enabled)
  rows.append(r)
 valid=len(rows)==hours
 def total(key):return math.fsum(r[key] for r in rows)
 req={t:total(t+'_required_kw') for t in ('c4isr','aux','ev')};ens={t:total(t+'_unserved_kw') for t in req}
 result={'scenario':case,'pv_kw':pv_kw,'wind_kw':wind_kw,'bess_kwh':bess_kwh,'pcs_kw':90.,'dg_kw':100.,'start_index':start,'hours_requested':hours,'hours_completed':len(rows),'initial_soc':.7,'initial_fuel_l':fuel_l,'fuel_model':'MDT_DERIVED_ARCHIVED_CATALOGUE_NOT_OEM','strategy':'S3_existing_LC1','status':'NUMERICAL_SCREENING_COMPLETED' if valid else 'QUARANTINED_INFEASIBLE_OR_FAILED','valid':valid,'critical_required_kwh':req['c4isr'] if valid else None,'critical_ENS_kwh':ens['c4isr'] if valid else None,'aux_ENS_kwh':ens['aux'] if valid else None,'ev_ENS_kwh':ens['ev'] if valid else None,'total_ENS_kwh':sum(ens.values()) if valid else None,'critical_EA_fraction':(1-ens['c4isr']/req['c4isr']) if valid and req['c4isr'] else None,'diesel_fuel_used_l':total('dg_fuel_consumed_l') if valid else None,'fuel_end_l':d.fuel_l if valid else None,'bess_end_soc':b.soc if valid else None,'capex_gbp_illustrative':calculate_capex(pv_kw,wind_kw,bess_kwh),'ac_residual_abs_max_kwh':max((abs(r['AC_residual_kwh']) for r in rows),default=None),'issues':issues,'new_native_MDT_comparisons':0,'stated_limitations':'Hourly energy-balance simulation; assumed AC reference and 25kW dump; no equipment or grid-forming validation'}
 return result,rows if save_trace else None

def pareto_status(results):
 # 2D CAPEX-vs-total outage ENS; no economic NPC or OEM pricing asserted.
 valid=[r for r in results if r['valid']]
 for r in results:
  if not r['valid']:r['pareto_capex_vs_total_ENS']='INELIGIBLE_NOT_VALID'
  else:
   dominated=any(q is not r and q['capex_gbp_illustrative']<=r['capex_gbp_illustrative']+1e-8 and q['total_ENS_kwh']<=r['total_ENS_kwh']+1e-8 and (q['capex_gbp_illustrative']<r['capex_gbp_illustrative']-1e-8 or q['total_ENS_kwh']<r['total_ENS_kwh']-1e-8) for q in valid)
   r['pareto_capex_vs_total_ENS']='DOMINATED' if dominated else 'NONDOMINATED_IN_NINE_OPTIONS_ONLY'
 return results

def write_csv(path,entries):
 if not entries:return
 keys=[k for k in entries[0] if k!='issues']
 with path.open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,keys,extrasaction='ignore');writer.writeheader()
  for r in entries:writer.writerow({k:(json.dumps(r[k]) if isinstance(r.get(k),(dict,list)) else r.get(k)) for k in keys})

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'outputs');args=p.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
 pv_pu=read_col('v6_solar_pu_index_value.csv',1);wind_pu=read_col('v6_wind_pu_index_value.csv',1)
 if len(pv_pu)!=8760 or len(wind_pu)!=8760:raise ValueError('Weather not 8760h')
 loads={case:read_load(case) for case in ('low','central','high')}
 # T08: original equipment, all new 120-person demand profiles, 3 outage durations
 baseline=[]
 for case in ('low','central','high'):
  for duration in (24,72,168):
   m,trace=run(case,loads[case],pv_pu,wind_pu,hours=duration,save_trace=(case=='central' and duration==168))
   baseline.append(m)
   if trace:write_csv(out/'central_original_hardware_168h_hourly_trace.csv',trace)
 write_csv(out/'revised_load_original_hardware_outage_matrix.csv',baseline)
 # WP0/S0: re-evaluate ORIGINAL 8760-hour site load with the same S3 dispatch policy, not the old dispatch S0 policy.
 original=Loads(read_col('v6_C4ISR_kw_index_value.csv',1),read_col('v6_Auxiliary_kw_index_value.csv',1),read_col('v6_EV_charging_kw_index_value.csv',1))
 original_site=[]
 for duration in (24,72,168):
  m,_=run('S0_original_site_load__S3_dispatch',original,pv_pu,wind_pu,hours=duration)
  original_site.append(m)
 write_csv(out/'S0_original_site_rerun_S3_dispatch.csv',original_site)
 # T09: three PV/wind configurations x 300/450/600 kWh, exact same load and 168h weather.
 comparison=[]
 for pvwind in (50.,75.,100.):
  for bess in (300.,450.,600.):
   m,_=run('central',loads['central'],pv_pu,wind_pu,pv_kw=pvwind,wind_kw=pvwind,bess_kwh=bess)
   comparison.append(m)
 pareto_status(comparison)
 write_csv(out/'capacity_screen_nine_options_168h.csv',comparison)
 (out/'capacity_quarantined_issue_details.json').write_text(json.dumps([{'scenario':r['scenario'],'pv_kw':r['pv_kw'],'wind_kw':r['wind_kw'],'bess_kwh':r['bess_kwh'],'issues':r['issues']} for r in comparison if not r['valid']],indent=2),encoding='utf-8')
 # T10: explicit finite fuel, one generator outage, and severe RE assumptions.
 stresses=[]
 for label,kw in [('BASE',{}),('FUEL_500L',{'fuel_l':500.}),('DG_OFF_H24_TO_H48',{'dg_off_start':24,'dg_off_end':48}),('LOW_RE_60PCT',{'renewable_multiplier':.6}),('FUEL_500_AND_DG_OFF',{'fuel_l':500.,'dg_off_start':24,'dg_off_end':48})]:
  m,_=run('central',loads['central'],pv_pu,wind_pu,**kw)
  m['stress_case']=label;stresses.append(m)
 write_csv(out/'contingency_screen_168h.csv',stresses)
 summary={'version':'W7_PRELIMINARY_SCREENING','status':'NUMERICAL_RESULTS_ONLY','native_MDT_executions':0,'homer_executions':0,'baseline_checked':len(baseline),'original_site_reruns':len(original_site),'capacity_candidates':len(comparison),'contingency_cases':len(stresses),'capacity_valid':sum(x['valid'] for x in comparison),'capacity_invalid':sum(not x['valid'] for x in comparison),'baseline_valid':sum(x['valid'] for x in baseline),'contingency_valid':sum(x['valid'] for x in stresses),'cost_boundary':'Illustrative source config 2026 GBP CAPEX only, no lifecycle NPC, no pricing verification','critical_note':'No EV V2G support is credited; energy model assumes AC reference during DG downtime and is not physical certification'}
 (out/'screening_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
