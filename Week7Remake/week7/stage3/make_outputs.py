"""Generate traceable WP5 comparison and figures from Stage3 CSVs.
No direct native software calls and no source modifications.
"""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
from datetime import datetime,timedelta
from week7.outage_sensitivity import calculate_capex

HERE=Path(__file__).resolve().parent
OUT=HERE/'outputs'; DOC=HERE/'docs'; FIG=HERE/'figures'

def readcsv(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def make():
    FIG.mkdir(exist_ok=True);DOC.mkdir(exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    summary=readcsv(OUT/'weekly_52_starts_summary.csv')
    y=[r for r in summary if r['duration_h']=='168']
    # Two distinct figures, no ad hoc colour coding of numeric validation status.
    fig,ax=plt.subplots(figsize=(9,5.4))
    for pv in (50,75,100):
        rows=sorted([r for r in y if int(r['pv_kw'])==pv],key=lambda r:float(r['bess_kwh']))
        cap=[calculate_capex(pv,pv,float(r['bess_kwh']))/1000 for r in rows]
        vals=[float(r['total_ENS_mean_kwh_per_window']) for r in rows]
        ax.plot(cap,vals,'o-',label=f'{pv} kW PV / {pv} kW Wind')
        for x,v,r in zip(cap,vals,rows):ax.annotate(f"{r['bess_kwh']} kWh",(x,v),xytext=(5,6),textcoords='offset points',fontsize=8)
    ax.set_xlabel('Illustrative capital cost (£ thousand) — not NPC')
    ax.set_ylabel('Mean total ENS per 168 h window (kWh)')
    ax.set_title('LC1: 52 equally spaced outage starts (2025 provisional central load)')
    ax.grid(alpha=.25);ax.legend(fontsize=9)
    fig.text(.01,.012,'Research-only Python screening; no outage probabilities, no native MDT/HOMER/field validation.',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(FIG/'52week_capex_vs_mean_ENS.png',dpi=180,bbox_inches='tight');plt.close(fig)

    fig,ax=plt.subplots(figsize=(9,5.4))
    labels=[f"{int(r['pv_kw'])}/{int(r['wind_kw'])}\n{int(r['bess_kwh'])}" for r in y]
    counts=[int(r['critical_shortfall_window_count']) for r in y]
    bars=ax.bar(range(len(y)),counts)
    for bar,count in zip(bars,counts):
        ax.text(bar.get_x()+bar.get_width()/2,count+.35,str(count),ha='center',va='bottom',fontsize=9)
    ax.set_xticks(range(len(y)),labels)
    ax.set_ylim(0,58);ax.set_ylabel('168 h windows with Critical ENS > 0 (of 52)')
    ax.set_xlabel('PV kW / Wind kW (top)  |  Stationary BESS kWh (bottom)')
    ax.set_title('LC1: Critical shortfall conditional on outage start (NOT failure probability)')
    ax.grid(axis='y',alpha=.2)
    fig.text(.01,.012,'52 systematically spaced 2025 starting times, all reset to 70% BESS SOC / 2000 L fuel; no EENS.',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(FIG/'52week_critical_shortfall_count.png',dpi=180,bbox_inches='tight');plt.close(fig)

    old=readcsv(HERE.parent/'outputs/S0_original_site_rerun_S3_dispatch.csv')
    s0=next(r for r in old if r['hours_requested']=='168')
    oldnew=readcsv(HERE.parent/'nextstage/outputs/nine_candidate_v2_168h.csv')
    s1=next(r for r in oldnew if r['pv_kw']=='50.0' and r['bess_kwh']=='300.0')
    text=[
    '# T19 — S0/S1/S4 Research Comparison (Version 0.3)',
    '',
    '**Evidence:** numerical Python simulation only, provisional 120-person load, 2025 fixed LST; not MOD measured data or HOMER/MDT re-optimisation.',
    '',
    '## A. Historical-demand S0 compared with revised-demand S1',
    '',
    'The common hardware and Jan 1–7 window are used; **demand changed**, so differences measure the modelled consequence of a new load assumption, not a measured efficiency improvement.',
    '',
    '| Indicator (same 168 h start) | S0 original demand | S1 provisional central demand |',
    '|---|---:|---:|',
    f"| PV / Wind / BESS | 50 / 50 kW / 300 kWh | 50 / 50 kW / 300 kWh |",
    f"| Critical ENS (kWh) | {float(s0['critical_ENS_kwh']):,.1f} | {float(s1['critical_ENS_kwh']):,.1f} |",
    f"| Total ENS (kWh) | {float(s0['total_ENS_kwh']):,.1f} | {float(s1['total_ENS_kwh']):,.1f} |",
    f"| Diesel use (L) | {float(s0['diesel_fuel_used_l']):,.1f} | {float(s1['diesel_fuel_used_l']):,.1f} |",
    f"| Critical EA | {float(s0['critical_EA_fraction'])*100:.2f}% | {float(s1['critical_EA_fraction'])*100:.2f}% |",
    '',
    'S0 was independently replayed in the previous phase using the historical S3 dispatch, while S1 here is the isolated S3-v2 repair. Other than the documented fuel-exhaustion charge-direction safeguard, the six previously valid candidate outcomes matched prior screening within 1e-6. Therefore **demand changes dominate the comparison, but it is not a pure controlled treatment on identical controller code**. The result remains a research model comparison.',
    '',
    '## B. Extended candidate comparison: 52 weekly outage starts',
    '',
    'Every result below is for a **168-hour** independent outage initialisation under identical 2,000 L initial diesel fuel, 70% BESS SOC and static central EV charging demand. `Mean` is per simulated window, not probability-weighted EENS. CAPEX assumes indicative coefficients from `week7/outage_sensitivity.py`, not a vendor quote or net present cost.',
    '',
    '| PV / Wind (kW) | BESS (kWh) | Indicative CAPEX (£) | Mean Total ENS (kWh) | p90 Total ENS (kWh) | Worst Critical EA | Critical-shortfall windows (of 52) |',
    '|---:|---:|---:|---:|---:|---:|---:|']
    for r in y:
        pv=int(r['pv_kw']);bess=int(r['bess_kwh'])
        text.append(f"| {pv} / {pv} | {bess} | {calculate_capex(pv,pv,bess):,.0f} | {float(r['total_ENS_mean_kwh_per_window']):,.1f} | {float(r['total_ENS_p90_kwh_per_window']):,.1f} | {float(r['critical_EA_worst_percent']):.2f}% | {int(r['critical_shortfall_window_count'])} |")
    text.extend(['',
    'The 24h and 72h groups produced zero Critical ENS in each of the 52 aligned starts, but noncritical ENS remains. For 168h, even the 100/100 kW, 600 kWh configuration experiences **15 of 52** intervals with nonzero Critical ENS, at a worst-window Critical EA of approximately **75.10%**. In all those 15 windows the diesel fuel stock was exhausted in the model. These are conditional counterfactual results, not observations of 15 actual outages.',
    '',
    'The 100/100/600 option gives lower descriptive **mean total ENS** than 100/100/450 (719.0 vs 767.0 kWh/window), but costs approximately £60,000 more in indicative stationary-storage CAPEX. The 600 kWh alternative does **not** eliminate the same 15 critical-shortfall windows. No unique economic/resilience optimal capacity is selected.',
    '',
    '## C. EV and S2/S3 scope separation',
    '',
    '- **S1 dynamic fleet charging:** inherited previous-phase result for Jan 168 h: 50/50/300 gives 28 completed of 29 planned mission opportunities; 75/75/450, 100/100/450 and 100/100/600 each show 29/29 in that particular window. These outcomes depend on provisional vehicle sizes/routes and served charging.',
    '- **S2 single emergency vehicle V2B**: no execution or quantified benefit. OEM + charger + island/grid-forming proof missing.',
    '- **S3 mission-constrained fleet V2M**: no execution or quantified benefit; EV propulsion reserve is enforced for charging/mission readiness but no V2B discharge algorithm is switched on.',
    '- **S4 extra stationary BESS, no V2B:** capacity alternatives are in the 52-week table, with an assumed fixed 90 kW PCS and no lifecycle battery wear pricing.',
    '',
    '## D. Interpreting the result for the dissertation',
    '',
    'The central research finding is sensitivity to **site-demand assumptions, outage start, diesel fuel availability and dispatch**, not evidence of an installed design or an economically optimal microgrid. In particular, the previous four-season 100% critical EA for some candidates is a statement about those four windows only, not a year-round guarantee.',
    '',
    'Figures: `week7/stage3/figures/52week_capex_vs_mean_ENS.png` and `52week_critical_shortfall_count.png` (research-only, non-native).',
    '',
    '## E. Unresolved comparisons',
    '',
    'No genuine new native MDT/HOMER Pro runs; no site energy telemetry; no OEM V2B/V2M evidence; no probabilistic EENS; no NPC or full network voltage/frequency/UPS ride-through assessment. All future doctoral/supervisor-quality conclusions require these caveats.',
    ''])
    (DOC/'T19_results_comparison.md').write_text('\n'.join(text),encoding='utf-8')

    status=readcsv(HERE.parent/'nextstage/task_status.csv')
    updates={
        'T09':('ADVANCED_PYTHON_NONOPTIMAL','9 capacities + 4-season 108 cases + 52-start 1404 cases; no NPC or HOMER optimisation'),
        'T15':('ADVANCED_PYTHON','52 starts x 24/72/168h x 9 candidates = 1404; independent initialisation'),
        'T16':('PARTIAL','Scenario ENS, conditional distribution, EA/fuel; no EENS/NPC'),
        'T17':('PREFLIGHT_READY_NATIVE_PENDING','Generic 8760h reference, 108-case manifest and actual archived fuel curve; no new native MDT/HOMER runs'),
        'T18':('DRAFT_COMPLETED_UNAPPROVED','EN3400_methodology_draft_v0.3.md; requires supervisor and source signoff'),
        'T19':('DRAFT_COMPARISON_COMPLETED','S0/S1/S4 numerical comparison and 52-start figures; S2/S3 not simulated'),
        'T20':('AWAITING_SUPERVISOR_REVIEW','Decision handoff D1-D9 prepared; no approval recorded'),
    }
    for row in status:
        if row['task'] in updates:
            row['status'],row['evidence_or_next_gate']=updates[row['task']]
    with (DOC/'WP0_WP5_task_status_stage3.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,list(status[0]));w.writeheader();w.writerows(status)

    pre=readcsv(HERE/'external_inputs/LC1_DG_MDTCatalogue_Fuel_Curve.csv')
    findings=[
    '# Stage 3 — Validation and Audit Results',
    '',
    '- **Frozen archive:** original 166-file SHA256 baseline remains separately checked with `python week7/audit/check_preservation.py`.',
    '- **Python tests:** all 84 collected test instances pass (78 previously reported + 6 new Stage3 tests). Tests confirm code and numerical accounting only.',
    '- **Extended deterministic studies:** 1,404 valid of 1,404; max AC residual '+f"{max(float(x['max_AC_residual_kwh']) for x in readcsv(OUT/'weekly_52_starts_full.csv')):.3g}"+' kWh; no same-hour BESS dual operation; fuel inventory nonnegative.',
    '- **External tool comparability:** Week7 new MDT runs = 0, HOMER Pro runs = 0. The profiles, actual archived diesel fuel model and 108-case manifest are *generic interchange inputs* only.',
    '',
    '## Historical MDT scope',
    '',
    'Historical saved comparison `validation/diesel-energy-accounting/native-mdt-diesel-comparison.csv` demonstrates DG-only, 24 h controlled parity for generated kWh, service and fuel under matched archived catalogue assumptions; its source records are inherited, not rerun here. No new native solver results have been provided and full microgrid parity remains unverified.',
    '',
    '## Active diesel model mapping (important T17 audit finding)',
    '',
    'S3-v2 calls `ResearchDiesel.set_fuel_model(\'MDT_DERIVED\')`. This bypasses the `Settings.fuel_l_per_kwh = 0.25` fixed default. Correct external reference fuel values, at generator ON output:',
    '',
    '| ON power (kW) | Actual archived-model fuel rate (L/h) |',
    '|---:|---:|']
    for r in pre:findings.append(f"| {float(r['on_power_kw']):.0f} | {float(r['fuel_rate_litre_per_hour']):.4f} |")
    findings.extend(['',
    'This curve is archived catalogue-derived, not new manufacturer validation. Idle and generator output below 25 kW are deliberately not extrapolated.',
    '',
    '## Open evidence gaps',
    '',
    '1. Site/camp infrastructure and vehicle values are unverified provisional assumptions; approval needed.',
    '2. 100 kW grid-import assumption has not been established from an actual Sennybridge connection study.',
    '3. External MDT/HOMER project/runtime settings and authentic output files are absent: new cross-tool parity cannot be claimed.',
    '4. The 52 equal-spaced weather windows do not estimate EENS, failure probabilities, weather extremes outside 2025, or 168h sustained reliability under fuel-delivery uncertainty.',
    '5. No voltage, frequency, network load-flow, grid-forming, UPS transfer, earthing, protection or OEM vehicle bidirectional evidence.',
    '6. CAPEX is illustrative; comprehensive NPC requires fuel price, tariffs, O&M, replacement, outage valuation and lifecycle definitions.',
    '',
    '## Evidence labels for dissertation graphics',
    '',
    '`EXPLORATORY_PYTHON_SCREENING` for all new figures and numerical results; `HISTORICAL_DG_ONLY_PARITY` for the preserved 24h native comparison; `NOT_VALIDATED_NATIVE` for the new hybrid models and sizing conclusions; `NOT_IMPLEMENTED` for S2/S3 emergency EV discharge.',
    ''])
    (DOC/'T17_validation_gap_update.md').write_text('\n'.join(findings),encoding='utf-8')
    artifacts=[*sorted(OUT.glob('weekly_52*')),*sorted(FIG.glob('*.png')),*sorted(DOC.glob('*')),*sorted((HERE/'external_inputs').glob('*'))]
    hashes=[{'relative_path':str(p.relative_to(HERE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_bytes':p.stat().st_size} for p in artifacts if p.is_file()]
    with (OUT/'stage3_artifact_sha256.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,['relative_path','sha256','size_bytes']);w.writeheader();w.writerows(hashes)
    print(json.dumps({'figures':len(list(FIG.glob('*.png'))),'tracked_stage3_artifacts':len(hashes),'dynamic_outage_studies_not_repeated':True},indent=2))

if __name__=='__main__':make()
