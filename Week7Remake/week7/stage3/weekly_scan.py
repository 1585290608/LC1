"""Deterministic WP2/WP4 52-start, 24/72/168-hour screening.

These are equal-spaced *counterfactual outage starts*, NOT probabilistic
frequency estimates or EENS. Each outage resets fuel and initial BESS SOC.
The original 2025 weather and demand profiles are preserved unchanged.
"""
from __future__ import annotations
import argparse,csv,json,statistics,math
from pathlib import Path
from collections import defaultdict
from week7.nextstage.screen import simulate

ROOT=Path(__file__).resolve().parent

def write_csv(path,rows):
    if not rows:raise ValueError('No rows')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def percentile_nearest(values,p):
    if not values:raise ValueError('No values')
    x=sorted(values)
    return x[max(0,math.ceil(p*len(x))-1)]

def generate(output=ROOT/'outputs'):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    result=[]
    # 52 disjoint 7-day weather blocks; last block ends before the year boundary.
    starts=[168*i for i in range(52)]
    for duration in (24,72,168):
        for start in starts:
            for pv in (50.,75.,100.):
                for bess in (300.,450.,600.):
                    r,_,_=simulate(case='central',pv_kw=pv,wind_kw=pv,bess_kwh=bess,
                                   start=start,hours=duration,initial_soc=.7,fuel_l=2000.)
                    r['window_id']=f'W{start//168+1:02d}'
                    r['window_index']=start//168+1
                    r['case_id']=f'W{start//168+1:02d}_H{duration:03d}_PV{int(pv):03d}_W{int(pv):03d}_B{int(bess):03d}'
                    if not r['valid']:
                        raise RuntimeError(f'Screen quarantined: {r["case_id"]}: {r["issues"]}')
                    result.append(r)
    write_csv(output/'weekly_52_starts_full.csv',result)
    groups=defaultdict(list)
    for r in result:groups[(int(r['requested_h']),int(r['pv_kw']),int(r['bess_kwh']))].append(r)
    summary=[]
    for (duration,pv,bess),rows in sorted(groups.items()):
        ens=[r['total_ENS_kwh'] for r in rows]
        critical=[r['critical_ENS_kwh'] for r in rows]
        ea=[r['critical_EA_fraction']*100 for r in rows]
        fuels=[r['diesel_fuel_used_l'] for r in rows]
        summary.append({'duration_h':duration,'pv_kw':pv,'wind_kw':pv,'bess_kwh':bess,
                        'windows':len(rows), 'total_ENS_mean_kwh_per_window':statistics.mean(ens),
                        'total_ENS_median_kwh_per_window':statistics.median(ens),
                        'total_ENS_p90_kwh_per_window':percentile_nearest(ens,.9),
                        'total_ENS_worst_kwh_per_window':max(ens),
                        'critical_ENS_worst_kwh_per_window':max(critical),
                        'critical_EA_worst_percent':min(ea),
                        'critical_shortfall_window_count':sum(x>1e-7 for x in critical),
                        'diesel_fuel_mean_l_per_window':statistics.mean(fuels),
                        'fuel_depletion_window_count':sum(r['fuel_end_l']<1e-6 for r in rows),
                        'input_class':'CENTRAL_PROVISIONAL',
                        'method':'52_ALIGNED_STARTS_NOT_EENS_NOT_RANDOM_PROBABILITY'})
    write_csv(output/'weekly_52_starts_summary.csv',summary)
    metadata={'outage_starts':52,'durations_h':[24,72,168],
              'candidate_count':9,'case_count':len(result),
              'valid_count':sum(bool(r['valid']) for r in result),
              'max_ac_residual_kwh':max(r['max_AC_residual_kwh'] for r in result),
              'max_battery_residual_kwh':max(r['max_battery_residual_kwh'] for r in result),
              'max_bess_bidirectional_count':max(r['bess_same_hour_both_directions'] for r in result),
              'source_clock':'2025 fixed LST 8760 hours, no UK civil DST',
              'outage_start_hours':starts,
              'interpretation':'Not EENS, no event frequency or probabilities; each window resets battery SOC to 0.7 and fuel to 2000 L',
              'native_MDT_runs_new':0,'HOMER_runs_new':0}
    (output/'weekly_52_starts_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return summary,metadata

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'outputs')
    args=p.parse_args();_,meta=generate(args.output);print(json.dumps(meta,indent=2))
