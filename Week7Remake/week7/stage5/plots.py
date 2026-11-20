"""Stage5 diagnostic figures (illustrative screening; not validated designs)."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent

def draw(out=HERE/'figures',data=HERE/'outputs'):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=Path(data)
    a=pd.read_csv(data/'stage5_conditional_economic_comparison.csv')
    fig,ax=plt.subplots(figsize=(10.5,6.2))
    policies=list(a.policy.unique());marks=['o','s','^']
    for j,policy in enumerate(policies):
        sub=a[a.policy==policy]
        ax.scatter(sub['selected_20y_cashflow_PV_gbp_NOT_NPC']/1e6,
                   sub['mean_total_ENS_kwh'],s=70,marker=marks[j],label=policy.replace('_',' '))
        for _,r in sub.iterrows():
            ax.annotate(f"{int(r.pv_kw)}/{int(r.wind_kw)}/{int(r.bess_kwh)}",(r.selected_20y_cashflow_PV_gbp_NOT_NPC/1e6,r.mean_total_ENS_kwh),xytext=(5,6),textcoords='offset points',fontsize=7)
    ax.set_xlabel('PV of selected cash streams (£million over 20 years; NOT NPC)')
    ax.set_ylabel('Mean Total ENS per 168-hour outage (kWh; 52 fixed starts)')
    ax.set_title('LC1 Stage 5: Conditional Cost–Resilience Screening')
    ax.grid(alpha=.25);ax.legend(loc='upper right',fontsize=8)
    fig.text(.04,.018,'Source: archived Stage3/4 Python scenarios + inherited cost assumptions. No external validation; no failure probabilities.',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1));fig.savefig(out/'stage5_cost_resilience_conditional.png',dpi=155);plt.close(fig)
    win=pd.read_csv(data/'stage5_sensitivity_winner_counts.csv')
    group=win.groupby(['shadow_case','pv_kw','bess_kwh','policy'],as_index=False)['wins_in_assumption_grid'].sum()
    fig,ax=plt.subplots(figsize=(10,5.5))
    names=[];vals=[]
    for _,r in group.iterrows():
        names.append(f"{r.shadow_case}\n{int(r.pv_kw)}/{int(r.bess_kwh)} · {('3 refuels' if 'H48_H96_H144' in r.policy else 'no refuels')}")
        vals.append(int(r.wins_in_assumption_grid))
    ax.barh(names,vals)
    ax.set_xlabel('Count of assumption combinations ranked first (each shadow case has 162)')
    ax.set_title('Economic ranking changes under hypothetical unserved-load valuations')
    ax.grid(axis='x',alpha=.2)
    for i,n in enumerate(vals):ax.text(n+1,i,str(n),va='center')
    ax.set_xlim(0,max(vals)*1.17)
    fig.text(.03,.01,'Not an objective best design. Shadow prices are hypothetical; delivery and generator reliability are not evidenced.',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(out/'stage5_shadow_price_rank_sensitivity.png',dpi=155);plt.close(fig)
    return [out/'stage5_cost_resilience_conditional.png',out/'stage5_shadow_price_rank_sensitivity.png']

if __name__=='__main__':draw()
