"""Optional figures from re-run output (requires matplotlib). Charts are not validation."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent/'outputs'
FIG=Path(__file__).resolve().parent/'figures'
FIG.mkdir(exist_ok=True)
def records(name):
    with (OUT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
    a=records('nine_candidate_v2_168h.csv')
    fig,ax=plt.subplots(figsize=(8.4,5.6))
    for bess in (300,450,600):
        items=[r for r in a if int(float(r['bess_kwh']))==bess]
        ax.plot([float(r['capex_gbp_illustrative'])/1000 for r in items],
                [float(r['total_ENS_kwh']) for r in items],marker='o',label=f'BESS {bess} kWh')
        for r in items:
            ax.annotate(f"{int(float(r['pv_kw']))}/{int(float(r['wind_kw']))}kW",
                        (float(r['capex_gbp_illustrative'])/1000,float(r['total_ENS_kwh'])),
                        xytext=(3,4),textcoords='offset points',fontsize=8)
    ax.set(xlabel='Illustrative CAPEX (£ thousand, not verified quotes)',ylabel='Total ENS (kWh)',
           title='Central demand: 168h winter outage (S3-v2)')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(FIG/'nine_candidate_capex_vs_ENS.png',dpi=170);plt.close(fig)
    s=records('seasonal_nine_candidates_24_72_168h.csv')
    fig,ax=plt.subplots(figsize=(8.4,5.3))
    for bess in (300,450,600):
        y=[float(next(r['total_ENS_kwh'] for r in s if r['season']==season and r['requested_h']=='168' and r['pv_kw']=='100.0' and r['bess_kwh']==str(float(bess))))
           for season in ('winter','spring','summer','autumn')]
        ax.plot(('Winter','Spring','Summer','Autumn'),y,marker='o',label=f'BESS {bess} kWh')
    ax.set(xlabel='2025 168h seasonal outage start',ylabel='Total ENS (kWh)',
           title='Fixed 100kW PV + 100kW wind: seasonal BESS sensitivity')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(FIG/'four_season_bess_sensitivity.png',dpi=170);plt.close(fig)
    print('Generated',len(list(FIG.glob('*.png'))),'figures')
if __name__=='__main__':main()
