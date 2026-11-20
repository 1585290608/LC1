"""Research-stage figures from generated numerical CSVs; never imply field validation."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
OUT=HERE/'outputs';FIG=HERE/'figures';FIG.mkdir(exist_ok=True)

def read(name):
 with (OUT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
 rows=read('central_load_8760.csv')[:168]
 x=list(range(168));crit=[float(r['c4isr_kw']) for r in rows];aux=[float(r['aux_kw']) for r in rows];ev=[float(r['ev_kw']) for r in rows]
 fig,ax=plt.subplots(figsize=(11,4.3))
 ax.stackplot(x,crit,aux,ev,labels=['Critical C4ISR','Auxiliary','EV charging'],alpha=.82)
 ax.set(xlabel='Elapsed hour from 2025-01-01 00:00 (source LST)',ylabel='Demand (kW)',title='Provisional 120-person camp: Central hourly demand (first 168 h)')
 ax.legend(loc='upper right');ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(FIG/'central_first_168h_load_tiers.png',dpi=160);plt.close(fig)
 rows=read('capacity_screen_nine_options_168h.csv')
 fig,ax=plt.subplots(figsize=(9.5,5))
 for r in rows:
  tag=f"{int(float(r['pv_kw']))}/{int(float(r['wind_kw']))} PV/Wind, {int(float(r['bess_kwh']))} BESS"
  c=float(r['capex_gbp_illustrative'])/1000
  if r['valid']=='True':
   ens=float(r['total_ENS_kwh']);ax.scatter(c,ens,marker='o');ax.annotate(tag,(c,ens),xytext=(5,5),textcoords='offset points',fontsize=7)
  else:
   ax.scatter(c,0,marker='x')
 ax.set(xlabel='Illustrative equipment CAPEX (GBP 1,000; not 20-y NPC)',ylabel='Total ENS in one 168-h winter case (kWh)',title='Preliminary nine-option screening: quarantined cases shown as x at y=0')
 ax.grid(alpha=.25);fig.tight_layout();fig.savefig(FIG/'limited_capacity_capex_vs_ens.png',dpi=160);plt.close(fig)
 rows=read('central_ev_trace_61320.csv');rows=[r for r in rows if r['vehicle_id']=='ML01' and int(r['hour_index'])<168]
 fig,ax=plt.subplots(figsize=(10,3.5));x=[int(r['hour_index']) for r in rows]
 ax.plot(x,[100*float(r['soc_before_charging']) for r in rows],label='Before charging')
 ax.plot(x,[100*float(r['soc_final']) for r in rows],label='After charging',alpha=.8)
 ax.axhline(25,linestyle='--',label='Protected mission SOC floor (25%)')
 ax.set(xlabel='Hour (source LST)',ylabel='SOC (%)',title='Illustrative Medium Logistics EV ML01: planned week-one charging and missions')
 ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(FIG/'medium_ev_illustrative_soc_first_week.png',dpi=160);plt.close(fig)
 print('Three figures created under',FIG)
if __name__=='__main__':main()
