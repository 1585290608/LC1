"""Build Stage5 audit, conditional cost screening and sensitivity output.

Usage: python -m week7.stage5.run_study [--out DIRECTORY]
Inputs are imported Stage3/4 reports; no source modifications or native runs.
"""
from __future__ import annotations
from pathlib import Path
import argparse,csv,hashlib,itertools,json,math,statistics
from week7.stage5.economics import (Sensitivity,historical_parameters,score_case,
    financial_years,pareto_labels,read_csv,SCENARIO_SOURCE)
from week7.stage5.preflight import check_inputs

HERE=Path(__file__).resolve().parent
S3=HERE.parent/'stage3/outputs'
S4=HERE.parent/'stage4/outputs'

def write_csv(path,rows):
    if not rows:raise ValueError(f'No data: {path}')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='raise');w.writeheader();w.writerows(rows)

def cases_aligned():
    """Use all nine preserved 52-start BASE + 3 candidates' two fuel policies."""
    stage3=read_csv(S3/'weekly_52_starts_summary.csv')
    selected=[]
    for x in stage3:
        if int(x['duration_h'])!=168:continue
        selected.append({'policy':'BASE','pv_kw':float(x['pv_kw']),'wind_kw':float(x['wind_kw']),
           'bess_kwh':float(x['bess_kwh']),'window_count':int(x['windows']),
           'mean_total_ENS_kwh':float(x['total_ENS_mean_kwh_per_window']),
           'mean_critical_ENS_kwh':None, # from full 52-window data
           'worst_total_ENS_kwh':float(x['total_ENS_worst_kwh_per_window']),
           'critical_shortfall_windows':int(x['critical_shortfall_window_count']),
           'mean_fuel_consumption_l':float(x['diesel_fuel_mean_l_per_window']),
           'mean_accepted_delivery_l':0.})
    full=read_csv(S3/'weekly_52_starts_full.csv')
    if len(full)!=1404 or len(selected)!=9:raise ValueError('Expected archived 1404 Stage3 runs / 9 168h candidates')
    for r in selected:
        sample=[float(x['critical_ENS_kwh']) for x in full if int(x['requested_h'])==168 and float(x['pv_kw'])==r['pv_kw'] and float(x['bess_kwh'])==r['bess_kwh']]
        if len(sample)!=52:raise ValueError('52-start case mismatch')
        r['mean_critical_ENS_kwh']=statistics.mean(sample)
    stage4=read_csv(S4/'stage4_52start_contingency_summary.csv')
    other_policies={'REFUEL_500_H72','REFUEL_500_H48_H96_H144'}
    for x in stage4:
        if x['policy'] not in other_policies:continue
        selected.append({k:(float(x[k]) if k in ('pv_kw','wind_kw','bess_kwh','mean_total_ENS_kwh','mean_critical_ENS_kwh','worst_total_ENS_kwh','mean_fuel_consumption_l','mean_accepted_delivery_l') else int(x[k]) if k in ('window_count','critical_shortfall_windows') else x[k]) for k in
                ['policy','pv_kw','wind_kw','bess_kwh','window_count','mean_total_ENS_kwh','mean_critical_ENS_kwh','worst_total_ENS_kwh','critical_shortfall_windows','mean_fuel_consumption_l','mean_accepted_delivery_l']})
    if len(selected)!=15:raise ValueError(f'Expected 9 baseline + 6 fuel cases, got {len(selected)}')
    keys={(x['policy'],x['pv_kw'],x['wind_kw'],x['bess_kwh']) for x in selected}
    if len(keys)!=15:raise ValueError('Duplicate candidate/policy')
    # Parity gate: Stage3 and Stage4 BASE match for selected three capacities.
    for r in selected:
        if r['policy']!='BASE':continue
        checks=[x for x in stage4 if x['policy']=='BASE' and float(x['pv_kw'])==r['pv_kw'] and float(x['bess_kwh'])==r['bess_kwh']]
        if not checks:continue
        if len(checks)!=1 or abs(float(checks[0]['mean_total_ENS_kwh'])-r['mean_total_ENS_kwh'])>1e-7:
            raise AssertionError('Stage3/Stage4 baseline not comparable')
    return selected


def get_config():return json.loads(SCENARIO_SOURCE.read_text(encoding='utf-8'))

def baseline_setting(cfg):
    b=cfg['baseline'];p=historical_parameters()
    return Sensitivity(hypothetical_events_pa=b['hypothetical_outage_events_per_year'],
        trip_fee_gbp=b['delivery_dispatch_fee_gbp_per_attempt'],
        delivery_premium_gbp_per_l=b['fuel_logistics_premium_gbp_per_accepted_l'],
        diesel_gbp_per_l=p['fuel_gbp_l'],
        bess_rate_multiplier=b['battery_cost_multiplier'],
        shadow_critical_gbp_per_kwh=b['critical_unserved_shadow_gbp_per_kwh'],
        shadow_noncritical_gbp_per_kwh=b['noncritical_unserved_shadow_gbp_per_kwh'])


def sensitivity_settings(cfg):
    s=cfg['sensitivity']
    shadows={'NO_PENALTY':(0.,0.),'EXAMPLE_10_100':(100.,10.),'EXAMPLE_25_250':(250.,25.)}
    for n,fee,premium,fuel,batt,tag in itertools.product(
        s['hypothetical_outage_events_per_year'],
        s['delivery_dispatch_fee_gbp_per_attempt'],
        s['fuel_logistics_premium_gbp_per_accepted_l'],
        s['fuel_price_gbp_per_l'],
        s['battery_cost_multiplier'],s['shadow_case']):
        critical,noncritical=shadows[tag]
        yield tag,Sensitivity(n,fee,premium,fuel,batt,critical,noncritical)


def make_output(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    preflight=check_inputs()
    if not preflight['all_internal_preflight_pass']:
        raise RuntimeError('T17 source integrity preflight failed: '+str(preflight['source_results']))
    (out/'stage5_T17_preflight.json').write_text(json.dumps(preflight,indent=2),encoding='utf-8')
    write_csv(out/'stage5_T17_preflight.csv',preflight['source_results'])
    cases=cases_aligned();conf=get_config();param=historical_parameters();baseline=baseline_setting(conf)
    scored=pareto_labels([score_case(c,baseline,param) for c in cases])
    write_csv(out/'stage5_conditional_economic_comparison.csv',scored)
    years=[]
    for candidate in cases:
        if (candidate['pv_kw'],candidate['wind_kw'],candidate['bess_kwh']) not in ((100.,100.,450.),(100.,100.,600.)):continue
        if candidate['policy'] not in ('BASE','REFUEL_500_H72','REFUEL_500_H48_H96_H144'):continue
        for yr in financial_years(candidate,baseline,param):
            years.append({'case_id':f"PV{int(candidate['pv_kw'])}_W{int(candidate['wind_kw'])}_B{int(candidate['bess_kwh'])}_{candidate['policy']}",**yr})
    write_csv(out/'stage5_year_by_year_cost_ledger.csv',years)
    variations=[];ranking={}
    for i,(tag,setting) in enumerate(sensitivity_settings(conf)):
        vs=[score_case(c,setting,param) for c in cases]
        leader=min(vs,key=lambda x:x['generalised_score_PV_gbp_NOT_NPC'])
        ranking.setdefault((leader['pv_kw'],leader['wind_kw'],leader['bess_kwh'],leader['policy'],tag),0)
        ranking[(leader['pv_kw'],leader['wind_kw'],leader['bess_kwh'],leader['policy'],tag)]+=1
        # retain all scenario scores, so price assumptions are reproducible
        for x in vs:
            variations.append({'sensitivity_id':f'C{i:04d}','shadow_case':tag,
                'pv_kw':x['pv_kw'],'wind_kw':x['wind_kw'],'bess_kwh':x['bess_kwh'],'policy':x['policy'],
                'events_pa':setting.hypothetical_events_pa,'trip_fee_gbp':setting.trip_fee_gbp,
                'delivery_premium_gbp_per_l':setting.delivery_premium_gbp_per_l,
                'diesel_gbp_per_l':setting.diesel_gbp_per_l,'battery_multiplier':setting.bess_rate_multiplier,
                'selected_cash_PV_gbp_NOT_NPC':x['selected_20y_cashflow_PV_gbp_NOT_NPC'],
                'shadow_PV_gbp_NOT_CASH':x['shadow_cost_PV_gbp_NOT_CASH'],
                'generalised_score_PV_gbp_NOT_NPC':x['generalised_score_PV_gbp_NOT_NPC'],
                'winner_in_finite_choice_set':int(x is leader)})
    write_csv(out/'stage5_cost_sensitivity_full.csv',variations)
    ranks=[{'pv_kw':pv,'wind_kw':wind,'bess_kwh':batt,'policy':policy,'shadow_case':tag,
            'wins_in_assumption_grid':n} for (pv,wind,batt,policy,tag),n in sorted(ranking.items())]
    write_csv(out/'stage5_sensitivity_winner_counts.csv',ranks)
    # 100/100/450 baseline and added 150 kWh cost comparison.
    selected={(x['pv_kw'],x['wind_kw'],x['bess_kwh'],x['policy']):x for x in scored}
    pair=[]
    for name,k0,k1 in [
      ('Increase stationary BESS by 150 kWh, no refuel',(100.,100.,450.,'BASE'),(100.,100.,600.,'BASE')),
      ('Add one 500 L delivery instead of extra 150 kWh',(100.,100.,600.,'BASE'),(100.,100.,450.,'REFUEL_500_H72')),
      ('Add three 500 L deliveries instead of extra 150 kWh',(100.,100.,600.,'BASE'),(100.,100.,450.,'REFUEL_500_H48_H96_H144')),
      ('Increase PV and wind by 25 kW each, three deliveries',(75.,75.,450.,'REFUEL_500_H48_H96_H144'),(100.,100.,450.,'REFUEL_500_H48_H96_H144'))]:
        a=selected[k0];b=selected[k1]
        pair.append({'comparison':name,'first':str(k0),'second':str(k1),
          'delta_CAPEX_gbp_second_minus_first':b['capex_gbp']-a['capex_gbp'],
          'delta_selected_cash_PV_gbp_second_minus_first':b['selected_20y_cashflow_PV_gbp_NOT_NPC']-a['selected_20y_cashflow_PV_gbp_NOT_NPC'],
          'delta_mean_total_ENS_kwh_second_minus_first':b['mean_total_ENS_kwh']-a['mean_total_ENS_kwh'],
          'delta_mean_critical_ENS_kwh_second_minus_first':b['mean_critical_ENS_kwh']-a['mean_critical_ENS_kwh'],
          'delta_critical_shortfall_windows_second_minus_first':b['critical_shortfall_windows']-a['critical_shortfall_windows'],
          'scope':'CONDITIONAL_SCORES_AND_ENS_ONLY_NO_ACTUAL_NPC'})
    write_csv(out/'stage5_key_option_pairs.csv',pair)
    meta={'run_type':'VERSIONED_POSTPROCESS_OF_ARCHIVED_STAGE3_STAGE4_RESULTS',
       'evidence':'CONDITIONAL_2025_52_START_EXPLORATORY',
       'economic_candidates':len(cases),'baseline_scored_candidates':len(scored),
       'sensitivity_grid_assumptions':len(variations)//len(cases),'sensitivity_scored_cases':len(variations),
       'years':param['years'],'real_discount_rate':param['discount'],
       'unserved_cost_is_shadow_not_cash':True,
       'annual_event_count_is_hypothetical_not_failure_frequency':True,
       'cost_scope':'PV of selected CAPEX, O&M, replacements, fuel consumed and scheduled delivery costs; no normal-operation load/dispatch or electricity revenue; NOT NPC',
       'source_unit_prices':'INHERITED_PROJECT_ASSUMPTIONS_UNVERIFIED_NOT_SUPPLIER_QUOTATIONS',
       'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,
       'external_cross_validation':'NOT_PERFORMED',
       't17_internal_preflight':preflight['all_internal_preflight_pass'],
       'disclaimers':conf['warnings']}
    (out/'stage5_run_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    return meta,scored,pair,ranks

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=HERE/'outputs');args=parser.parse_args()
    meta,_,_,_=make_output(args.out)
    print(json.dumps(meta,indent=2))
