"""Focused assumed import-capacity sensitivity (not a network connection application)."""
from __future__ import annotations
import argparse
from pathlib import Path
from week7.stage6.annual_grid import AnnualGridCase,run_year
from week7.stage6.run_study import write_csv,financial_proxy
HERE=Path(__file__).resolve().parent

def sweep(out):
    rows=[]
    for scenario in ('central','high'):
        for lim in (100.,125.,150.,175.,200.,225.,250.):
            c=AnnualGridCase(scenario=scenario,pv_kw=100.,wind_kw=100.,bess_kwh=450.,grid_limit_kw=lim)
            metrics,_=run_year(c)
            rows.append({**metrics,**financial_proxy(metrics)})
    write_csv(Path(out)/'stage6_grid_limit_sweep_14.csv',rows)
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE/'outputs');args=p.parse_args()
    for x in sweep(args.out):print(x['scenario'],x['grid_import_limit_kw'],round(x['total_unserved_kwh'],2),x['hours_any_unserved'],x['vehicle_departures_missed'])
