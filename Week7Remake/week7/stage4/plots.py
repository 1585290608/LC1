"""Reproducible descriptive (not probabilistic) Stage4 figures."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'outputs'
FIG=ROOT/'figures'

def read(name):
    with (DATA/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    d=[r for r in read('stage4_52start_contingency_summary.csv') if float(r['pv_kw'])==100 and float(r['bess_kwh'])==450]
    idx={r['policy']:r for r in d}
    policies=[('BASE','No fuel arrival'),('REFUEL_500_H72','+500 L at 72 h'),
              ('REFUEL_1000_H72','+1,000 L at 72 h'),('REFUEL_500_H48_H96_H144','+500 L × 3'),
              ('REFUEL_MISS_H96','Miss 96 h delivery'),('DG_DOWN_H24_H48','DG offline 24 h'),
              ('DG_DOWN_H24_H48_REFUEL_MULTI','DG offline + 3 deliveries')]
    labels=[x[1] for x in policies]
    values=[int(idx[x[0]]['critical_shortfall_windows']) for x in policies]
    fig,ax=plt.subplots(figsize=(10.5,5.1))
    bars=ax.barh(range(len(labels)),values)
    ax.invert_yaxis();ax.set_yticks(range(len(labels)),labels)
    ax.set_xlim(0,52);ax.set_xlabel('168-hour windows with Critical ENS (out of 52)')
    ax.set_title('LC1 Stage 4 — Deterministic fuel/availability sensitivity')
    for bar,n in zip(bars,values):ax.text(n+.45,bar.get_y()+bar.get_height()/2,str(n),va='center',fontsize=10)
    ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    fig.text(.02,.01,'Illustrative 2025 weather starts · PV 100 / wind 100 kW · BESS 450 kWh · not event probabilities',fontsize=8)
    fig.subplots_adjust(left=.26,bottom=.13,right=.93)
    fig.savefig(FIG/'fuel_supply_critical_shortfall_windows.png',dpi=170);plt.close(fig)

    cases=['BASE','REFUEL_500_H72','REFUEL_500_H48_H96_H144','DG_DOWN_H24_H48','DG_DOWN_H0_H72']
    labels=['Baseline','500 L @ 72 h','500 L @ 48/96/144 h','DG off 24–48 h','DG off 0–72 h']
    ens=[float(idx[k]['mean_total_ENS_kwh']) for k in cases]
    crit=[float(idx[k]['mean_critical_ENS_kwh']) for k in cases]
    fig,ax=plt.subplots(figsize=(10,5.0))
    x=list(range(len(cases)))
    ax.bar([i-.18 for i in x],ens,width=.35,label='Mean total ENS')
    ax.bar([i+.18 for i in x],crit,width=.35,label='Mean critical ENS')
    ax.set_xticks(x,labels,rotation=12,ha='right');ax.set_ylabel('Mean unserved energy per 168-hour outage (kWh)')
    ax.legend();ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    ax.set_title('Conditional supply strategies — 52 paired outage starts')
    fig.text(.01,.01,'Not EENS: no probability distribution or outage incidence has been established',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1))
    fig.savefig(FIG/'paired_mean_ENS_stress.png',dpi=170);plt.close(fig)

if __name__=='__main__':main()
