"""Stage6 bounded tariff WHAT-IF and figures; reads existing simulated outputs."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from week7.stage5.economics import read_csv
from week7.stage6.run_study import write_csv,calculate_normal_year_cost

HERE=Path(__file__).resolve().parent

def process(out):
    out=Path(out)
    rows=read_csv(out/'stage6_81_annual_grid_cases.csv')
    sweep=read_csv(out/'stage6_grid_limit_sweep_14.csv')
    prices=[]
    for x in rows:
        for p in (.168,.24,.312):
            op=calculate_normal_year_cost({'grid_import_kwh':float(x['grid_import_kwh']),
                    'grid_export_kwh':float(x['grid_export_kwh'])},price=p,
                    export_price=.05,standing_annual=730)
            prices.append({'scenario':x['scenario'],'pv_kw':x['pv_kw'],'wind_kw':x['wind_kw'],
                    'bess_kwh':x['bess_kwh'],'grid_import_limit_kw':x['grid_import_limit_kw'],
                    'annual_hourly_requested_service_shortfall_kwh_NOT_EENS':x['total_unserved_kwh'],
                    'normal_year_energy_service_met':x['unserved_load_zero'],
                    'tariff_gbp_per_kwh':p,'annual_grid_bill_gbp':op['annual_grid_bill_gbp'],
                    'assumed_20y_PV_grid_bill_gbp':op['annual_grid_bill_gbp']*sum((1.03)**(-y) for y in range(1,21)),
                    'comparison_note':'Only candidates meeting same service criterion may be compared on grid bill; no outage cost or actual tariff'})
    write_csv(out/'stage6_243_tariff_scores.csv',prices)
    fig,ax=plt.subplots(figsize=(9,5.5))
    for sc in ('central','high'):
        group=[r for r in sweep if r['scenario']==sc]
        ax.plot([float(r['grid_import_limit_kw']) for r in group],
                [float(r['total_unserved_kwh'])/1000 for r in group],marker='o',label=f'{sc.title()} — hourly requested-service shortfall')
    ax.set(xlabel='Hypothetical grid import limit (kW)',ylabel='Sum of hourly unserved requests (MWh, NOT EENS)',
           title='100 kW PV + 100 kW Wind + 450 kWh BESS: import limit screen')
    ax.grid(True,alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(HERE/'figures/stage6_grid_limit_service_sensitivity.png',dpi=175);plt.close(fig)
    comp=read_csv(out/'stage6_central_peacetime_outage_comparison.csv')
    group=[r for r in comp if float(r['assumed_grid_import_limit_kw'])==250]
    fig,ax=plt.subplots(figsize=(9,6))
    for r in group:
        x=float(r['normal_year_cash_PV_PROXY_NOT_NPC_gbp'])/1e6
        y=float(r['52start_mean_168h_islanded_total_ENS_kwh'])
        ax.scatter(x,y,s=35)
        ax.annotate(f"{int(float(r['pv_kw']))}/{int(float(r['wind_kw']))}/{int(float(r['bess_kwh']))}",(x,y),xytext=(5,5),textcoords='offset points',fontsize=8)
    ax.set(xlabel='Selected normal-year 20y cash PV proxy (£m; NOT NPC)',
           ylabel='Mean total ENS in separate islanded 168h windows (kWh)',
           title='Serviced central-load 250 kW assumed grid limit: two independent objectives')
    ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(HERE/'figures/stage6_normal_cost_vs_outage_ENS.png',dpi=175);plt.close(fig)
    return len(prices)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=HERE/'outputs');args=parser.parse_args()
    print('tariff scores:',process(args.out))
