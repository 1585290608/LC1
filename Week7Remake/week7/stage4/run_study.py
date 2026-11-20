"""Run Stage4 T10/T16: deterministic, paired 52-start stress tests.

Not a probability model or HOMER/MDT native simulator. External deliveries are
hypothetical and instantaneous at the start of their specified hours.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,statistics,math
from collections import defaultdict
from pathlib import Path
from week7.stage4.contingency import Delivery,run
from week7.stage3.weekly_scan import percentile_nearest

ROOT=Path(__file__).resolve().parent
STARTS=[i*168 for i in range(52)]
FLEET_STARTS=[i*168 for i in range(0,52,4)]
CANDIDATES=[(75.,75.,450.),(100.,100.,450.),(100.,100.,600.)]
POLICIES=[
 ('BASE',{}),
 ('REFUEL_500_H72',{'deliveries':(Delivery(72,500.),)}),
 ('REFUEL_1000_H72',{'deliveries':(Delivery(72,1000.),)}),
 ('REFUEL_500_H48_H96_H144',{'deliveries':tuple(Delivery(i,500.) for i in (48,96,144))}),
 ('REFUEL_500_H96_DELAYED',{'deliveries':(Delivery(96,500.),)}),
 ('REFUEL_MISS_H48',{'deliveries':(Delivery(96,500.),Delivery(144,500.))}),
 ('REFUEL_MISS_H96',{'deliveries':(Delivery(48,500.),Delivery(144,500.))}),
 ('REFUEL_MISS_H144',{'deliveries':(Delivery(48,500.),Delivery(96,500.))}),
 ('DG_DOWN_H24_H48',{'dg_off_periods':((24,48),)}),
 ('DG_DOWN_H0_H72',{'dg_off_periods':((0,72),)}),
 ('DG_DOWN_H24_H48_REFUEL_H72',{'dg_off_periods':((24,48),),'deliveries':(Delivery(72,500.),)}),
 ('DG_DOWN_H24_H48_REFUEL_MULTI',{'dg_off_periods':((24,48),),'deliveries':tuple(Delivery(i,500.) for i in (48,96,144))}),
 ('SOC_DISPATCH_RESERVE_20',{'reserve_soc':.2}),
 ('SOC_DISPATCH_RESERVE_40',{'reserve_soc':.4}),
 ('DG_STOP_SOC_50',{'stop_soc':.5}),
 ('DG_STOP_SOC_70',{'stop_soc':.7}),
 ('DG_TO_BESS_DISABLED',{'allow_dg_to_bess':False}),
]
SECONDARY={'BASE','REFUEL_500_H72','REFUEL_500_H48_H96_H144','DG_DOWN_H24_H48','DG_DOWN_H0_H72','SOC_DISPATCH_RESERVE_40'}
FLEET_POLICIES={'BASE','REFUEL_500_H72','DG_DOWN_H24_H48','REFUEL_500_H48_H96_H144'}


def write_csv(path,rows):
    if not rows:raise ValueError('No rows')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def get_summary(rows):
    groups=defaultdict(list)
    for r in rows:groups[(r['policy'],r['pv_kw'],r['wind_kw'],r['bess_kwh'])].append(r)
    result=[]
    for (policy,pv,wind,bess),sub in sorted(groups.items(), key=lambda kv:(kv[0][1],kv[0][3],kv[0][0])):
        base={r['start_hour']:r for r in groups['BASE',pv,wind,bess]}
        assert len(sub)==52 and all(r['valid'] for r in sub),f'Incomplete: {policy} {pv} {bess}'
        ens=[r['total_ENS_kwh'] for r in sub]
        crit=[r['critical_ENS_kwh'] for r in sub]
        fuel=[r['fuel_consumed_l'] for r in sub]
        delta=[base[r['start_hour']]['total_ENS_kwh']-r['total_ENS_kwh'] for r in sub]
        critdelta=[base[r['start_hour']]['critical_ENS_kwh']-r['critical_ENS_kwh'] for r in sub]
        result.append({
            'policy':policy,'pv_kw':pv,'wind_kw':wind,'bess_kwh':bess,'duration_h':168,'window_count':len(sub),
            'mean_total_ENS_kwh':statistics.mean(ens),'median_total_ENS_kwh':statistics.median(ens),
            'p90_total_ENS_kwh':percentile_nearest(ens,.9),'worst_total_ENS_kwh':max(ens),
            'mean_critical_ENS_kwh':statistics.mean(crit),'worst_critical_ENS_kwh':max(crit),
            'critical_shortfall_windows':sum(c>1e-7 for c in crit),
            'fuel_depletion_windows':sum(r['fuel_end_l']<=1e-6 for r in sub),
            'mean_fuel_consumption_l':statistics.mean(fuel),
            'mean_accepted_delivery_l':statistics.mean(r['fuel_delivered_l'] for r in sub),
            'mean_unaccepted_delivery_l':statistics.mean(r['fuel_delivery_unaccepted_l'] for r in sub),
            'mean_saved_total_ENS_vs_base_kwh':statistics.mean(delta),
            'mean_saved_critical_ENS_vs_base_kwh':statistics.mean(critdelta),
            'improved_total_ENS_window_count':sum(x>1e-7 for x in delta),
            'worsened_total_ENS_window_count':sum(x< -1e-7 for x in delta),
            'equal_total_ENS_window_count':sum(abs(x)<=1e-7 for x in delta),
            'classification':'PAIRED_DETERMINISTIC_CONDITIONAL_2025_NOT_PROBABILITY',
        })
    return result


def run_all(out=ROOT/'outputs'):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[];traces={};deliveries=[];failures=[]
    for pv,wind,bess in CANDIDATES:
        for name,kwargs in POLICIES:
            if (pv,wind,bess)!=(100.,100.,450.) and name not in SECONDARY:continue
            for st in STARTS:
                save=(pv,wind,bess)==(100.,100.,450.) and st==336 and name in {'BASE','REFUEL_500_H48_H96_H144','DG_DOWN_H24_H48'}
                r,trace,events=run(start=st,hours=168,pv_kw=pv,wind_kw=wind,bess_kwh=bess,
                                   save_trace=save,**kwargs)
                r['policy']=name;r['window_id']=f'W{st//168+1:02d}'
                r['scenario_id']=f'{r["window_id"]}_PV{int(pv)}_W{int(wind)}_B{int(bess)}_{name}'
                if not r['valid']:
                    failures.append(r);continue
                rows.append(r)
                for d in events:
                    deliveries.append({'scenario_id':r['scenario_id'],**d})
                if save:
                    traces[r['scenario_id']]=trace
    if failures:
        write_csv(out/'QUARANTINED.csv',failures)
        raise RuntimeError(f'{len(failures)} stress scenarios invalid; see QUARANTINED.csv')
    write_csv(out/'stage4_52start_contingency_full.csv',rows)
    summary=get_summary(rows)
    write_csv(out/'stage4_52start_contingency_summary.csv',summary)
    if deliveries:write_csv(out/'stage4_accepted_refuel_events.csv',deliveries)
    for key,trace in traces.items():write_csv(out/f'{key}_hourly_trace.csv',trace)

    fleet=[]
    for st in FLEET_STARTS:
        for name,kwargs in POLICIES:
            if name not in FLEET_POLICIES:continue
            r,_,_=run(start=st,hours=168,pv_kw=100.,wind_kw=100.,bess_kwh=450.,
                      fleet_feedback=True,**kwargs)
            if not r['valid']:raise RuntimeError(f'Dynamic fleet invalid: {name} hour {st}: {r["errors"]}')
            # Stable schema: dictionary-valued end_soc is serialized as JSON.
            r['end_soc_by_vehicle']=json.dumps(r['end_soc_by_vehicle'],sort_keys=True)
            r['policy']=name;r['window_id']=f'W{st//168+1:02d}'
            fleet.append(r)
    write_csv(out/'stage4_13start_EV_mission_feedback.csv',fleet)

    # Strict comparison to stored Stage3 weekly baseline: same hardware/controller.
    stage3=ROOT.parent/'stage3/outputs/weekly_52_starts_full.csv'
    with stage3.open(newline='',encoding='utf-8') as f:old=list(csv.DictReader(f))
    lookup={(float(x['pv_kw']),float(x['wind_kw']),float(x['bess_kwh']),int(x['start_hour'])):x
            for x in old if int(x['requested_h'])==168}
    discrepancy=[]
    for r in rows:
        if r['policy']!='BASE':continue
        old=lookup[r['pv_kw'],r['wind_kw'],r['bess_kwh'],r['start_hour']]
        for before,after in [('total_ENS_kwh','total_ENS_kwh'),('critical_ENS_kwh','critical_ENS_kwh'),
                             ('diesel_fuel_used_l','fuel_consumed_l'),('fuel_end_l','fuel_end_l'),
                             ('bess_end_soc','battery_soc_final')]:
            diff=float(old[before])-float(r[after])
            discrepancy.append({'scenario_id':r['scenario_id'],'metric':before,'diff':diff})
            if abs(diff)>1e-7:raise AssertionError(f'Stage3 baseline mismatch {r["scenario_id"]} {before}: {diff}')
    write_csv(out/'stage4_stage3_baseline_parity.csv',discrepancy)

    meta={'study':'LC1 Stage4 52-start conditional stress tests','status':'EXPLORATORY_PYTHON_SCREENING',
          'simulation_count':len(rows),'all_valid':True,'paired_baseline_checks':len(discrepancy),
          'mission_feedback_count':len(fleet),'native_MDT_runs_new':0,'HOMER_runs_new':0,
          'hour_count_per_run':168,'weather':'archived 2025 LST profiles',
          'representative_site':'provisional 120-person camp and 7 EV archetypes',
          'fuel_transfer':'hour-start instantaneous replenishment, no travel/weather/access constraints or delivery failure probabilities',
          'no_probability_or_EENS':'52 deterministic starts not outage frequency or expected annual unserved energy',
          'no_cost_optimisation':'CAPEX illustrative; no resupply or generator repair cost',
          'max_ac_residual_kwh':max(abs(r['max_AC_residual_kwh']) for r in rows),
          'max_battery_residual_kwh':max(abs(r['max_battery_residual_kwh']) for r in rows),
          'max_fuel_ledger_residual_l':max(abs(r['fuel_ledger_residual_l']) for r in rows),
          'baseline_parity_max_diff':max(abs(d['diff']) for d in discrepancy),
          'substantive_limit':'Dispatch reserve SOC is an EMS threshold, not guaranteed minimum in all DG backup states; 10% absolute SOC limit enforced',
         }
    (out/'stage4_summary_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    checksum=[]
    for f in sorted(out.glob('*')):
        if f.is_file() and f.name!='stage4_sha256.csv':checksum.append({'relative_file':f.name,'sha256':sha(f)})
    write_csv(out/'stage4_sha256.csv',checksum)
    return meta,summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'outputs');args=p.parse_args()
    meta,_=run_all(args.out);print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
