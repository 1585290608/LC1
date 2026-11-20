"""Run Stage6 annual normal-operation energy and conditional cash screen."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor
from week7.stage6.annual_grid import AnnualGridCase,run_year
from week7.stage5.economics import Sensitivity,present_value_components,read_csv,historical_parameters
from week7.stage5.preflight import check_inputs

HERE=Path(__file__).resolve().parent

def write_csv(path,rows):
    if not rows:raise ValueError('Empty output')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def calculate_normal_year_cost(m,price=.24,export_price=.05,standing_annual=730.):
    """Grid bill only; leaves unserved demand unpriced, so not a service-equivalent NPC."""
    if min(price,export_price,standing_annual)<0:raise ValueError('Negative costs')
    return {'grid_import_price_assumption_gbp_kwh':price,
        'export_price_assumption_gbp_kwh':export_price,
        'annual_import_charge_gbp':m['grid_import_kwh']*price,
        'annual_export_credit_gbp':m['grid_export_kwh']*export_price,
        'annual_standing_charge_gbp':standing_annual,
        'annual_grid_bill_gbp':m['grid_import_kwh']*price-m['grid_export_kwh']*export_price+standing_annual}

def financial_proxy(m, p=None):
    """PV of common base CAPEX/O&M/replacement and annual grid bill, NO outage stacking."""
    p=p or historical_parameters()
    capital=present_value_components(m['pv_kw'],m['wind_kw'],m['bess_kwh'],Sensitivity(),p)
    op=calculate_normal_year_cost(m,p['import_gbp_kwh'],p['export_gbp_kwh'],p['standing_gbp_day']*365)
    factor=sum((1+p['discount'])**-i for i in range(1,p['years']+1))
    # Base retained inherited DG/UPS capital and O&M; generator not operated in the normal-year model.
    return {**op,'CAPEX_gbp_illustrative':capital['capex_gbp'],
        'annual_fixed_OM_gbp':capital['fixed_OM_annual_gbp'],
        'normal_year_energy_bill_20y_PV_gbp':op['annual_grid_bill_gbp']*factor,
        'annual_normal_year_grid_plus_fixed_OM_gbp':op['annual_grid_bill_gbp']+capital['fixed_OM_annual_gbp'],
        'selected_normal_year_cash_PV_gbp_NOT_FULL_NPC':capital['base_selected_pv_gbp']+op['annual_grid_bill_gbp']*factor,
        'economic_service_gate':'PASS_ENERGY_ONLY' if m['unserved_load_zero'] else 'FAIL_UNSERVED_LOAD_SO_NOT_A_COMPARABLE_COST',
        'accounting_boundary':'CAPEX+fixed OM+replacement+initial/terminal tank inventory+repeated 2025 grid electricity bill; no outage event cash; NOT full NPC'}

def _one_case(c):
    m,_=run_year(c)
    return m

def make_output(out:Path,jobs:int=1):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pre=check_inputs()
    if not pre['all_internal_preflight_pass']:raise RuntimeError('Stage5 provenance preflight failed')
    cases=[AnnualGridCase(scenario=scen,pv_kw=rating,wind_kw=rating,bess_kwh=storage,grid_limit_kw=headroom)
           for scen in ('low','central','high') for rating in (50.,75.,100.)
           for storage in (300.,450.,600.) for headroom in (100.,150.,250.)]
    if jobs>1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            raw=list(ex.map(_one_case,cases,chunksize=2))
    else:raw=[_one_case(c) for c in cases]
    records=[{**m,**financial_proxy(m)} for m in raw]

    write_csv(out/'stage6_81_annual_grid_cases.csv',records)
    # Selective traces for auditable service/constraint examples; no per-hour output needed for all runs.
    for label,c in [('base_central_100kw',AnnualGridCase(scenario='central',pv_kw=50,wind_kw=50,bess_kwh=300,grid_limit_kw=100)),
                    ('upper_central_250kw',AnnualGridCase(scenario='central',pv_kw=100,wind_kw=100,bess_kwh=450,grid_limit_kw=250))]:
        metric,trace=run_year(c,trace=True)
        write_csv(out/f'stage6_{label}_hourly_trace.csv',trace)
        target=next(r for r in records if r['scenario']==c.scenario and r['pv_kw']==c.pv_kw and r['bess_kwh']==c.bess_kwh and r['grid_import_limit_kw']==c.grid_limit_kw)
        for key in ('grid_import_kwh','total_unserved_kwh','ev_unserved_kwh','vehicle_departures_missed'):
            if not math.isclose(float(metric[key]),float(target[key]),rel_tol=0,abs_tol=1e-7):
                raise AssertionError(f'Trace parity: {key}')
    # Compare 52 deterministic outage windows, no pretending this is probabilistic/EENS.
    s5=read_csv(HERE.parent/'stage5/outputs/stage5_conditional_economic_comparison.csv')
    summary_outage=[x for x in s5 if x['policy']=='BASE']
    combined=[]
    for a in records:
        if a['scenario']!='central':continue
        matched=[x for x in summary_outage if int(float(x['pv_kw']))==a['pv_kw'] and int(float(x['bess_kwh']))==a['bess_kwh']]
        if len(matched)!=1:raise AssertionError('Cannot join 168-hour outage metric')
        b=matched[0]
        combined.append({'pv_kw':a['pv_kw'],'wind_kw':a['wind_kw'],'bess_kwh':a['bess_kwh'],
            'assumed_grid_import_limit_kw':a['grid_import_limit_kw'],
            'annual_hourly_requested_service_shortfall_kwh_NOT_EENS':a['total_unserved_kwh'],
            'EV_deferrable_charging_shortfall_kwh':a['ev_unserved_kwh'],
            'infra_nondeferable_ENS_kwh':a['nondeferrable_infrastructure_ENS_kwh'],
            'annual_critical_unserved_kwh':a['c4isr_unserved_kwh'],
            'annual_ev_missed_missions':a['vehicle_departures_missed'],
            'normal_year_cash_PV_PROXY_NOT_NPC_gbp':a['selected_normal_year_cash_PV_gbp_NOT_FULL_NPC'],
            '52start_mean_168h_islanded_total_ENS_kwh':float(b['mean_total_ENS_kwh']),
            '52start_168h_critical_shortfall_windows':int(b['critical_shortfall_windows']),
            'not_added_costs':'Separate peacetime and outage conditions, no event probabilities and no 168h double-count assumption'})
    write_csv(out/'stage6_central_peacetime_outage_comparison.csv',combined)
    meta={'stage':6,'date':'2026-11-19','normal_year_cases':len(records),'hours_per_case':8760,
        'cases_without_any_unserved_demand':sum(x['unserved_load_zero'] for x in records),
        'cases_with_critical_shortfall':sum(x['hours_critical_unserved']>0 for x in records),
        'source_data':'PROVISIONAL 120-person camp low/central/high and seven EV archetypes, original 2025 fixed LST weather',
        'ev_charging_shortfall_caveat':'Unfulfilled EV charging in an hour may be re-requested later; summed hourly EV charging deficits are not permanent lost traction kWh or EENS',
        'annual_controller':'BESS-before-grid, 90kW PCS, DC efficiency .8944 both directions; DG disabled normal operation',
        'grid_headroom_kw':'100/150/250 are sensitivity assumptions, not network approvals',
        'annual_cost':'Normal-year economic proxy that includes grid energy, standing charge, CAPEX, fixed O&M and replacements but not 168h outage economics; not full NPC',
        'outage_score':'Stage5 52-start deterministic islanded sensitivity stored separately; not EENS',
        'native_MDT_runs':0,'native_HOMER_runs':0,'external_cross_solver_validation':'NOT_PERFORMED',
        'source_preflight_pass':True}
    (out/'stage6_run_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    files=[p for p in sorted(out.glob('stage6_*')) if p.is_file() and p.name!='stage6_sha256.csv']
    write_csv(out/'stage6_sha256.csv',[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files])
    return meta,records

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=HERE/'outputs');parser.add_argument('--jobs',type=int,default=1);args=parser.parse_args()
    meta,_=make_output(args.out,args.jobs)
    print(json.dumps(meta,indent=2))
