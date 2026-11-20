"""Build an evidence-labelled Markdown calculation report from saved CSV/JSON outputs."""
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;O=HERE/'outputs'

def rows(name):
 with (O/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def summary(case):return json.loads((O/f'{case}_summary.json').read_text())

def f(x,places=1):return f'{float(x):,.{places}f}' if x not in (None,'') else '—'

def table(header,records):
 return '| '+' | '.join(header)+' |\n| '+' | '.join('---' for _ in header)+' |\n'+''.join('| '+' | '.join(str(x) for x in r)+' |\n' for r in records)+'\n'

def main():
 s={case:summary(case) for case in ('low','central','high')}
 parts=['# LC1 Week 7 — Load Calculation and Preliminary Screening Report\n',
 '**Report date:** 19 November 2026. **Model status:** hypothetical 120-person camp and generic vehicle archetypes. Numerical Python checks complete; no field measurement, new native MDT, or HOMER optimisation. All timestamps are source 2025 LST, `dt=1 hour`.\n',
 '## 1. Evidence and methodology\n',
 'The original source archive has 166 hashed unchanged files. Current repository regression 53/53 passes; 13 additional test instances for the Week 7 extension give **66/66 combined passes**. These are software and hourly accounting checks. Real hardware and MDT hybrid parity remain unverified.\n',
 'Load calculation (each hourly interval): `equipment_kWh = rated_kW × scenario_utilisation × schedule_indicator × 1 h`; `site_kWh = C4ISR + auxiliary + EV_charge_AC`. For each vehicle `E_trip = distance_km × traction_kWh_per_km`, `E_accepted_DC = charger_AC_kWh × 0.92`, and `SOC_after = SOC_before + E_accepted_DC / battery_capacity_kWh`. Propulsion draw occurs at the mission return hour; the departure guard checks enough pre-departure SOC for trip draw plus protected reserve.\n',
 '## 2. Proposed 120-person camp demand (not official MOD meter data)\n']
 parts.append(table(['Demand case','kWh/year','kWh/day avg','Peak kW','C4ISR MWh/year','Aux MWh/year','EV AC MWh/year'],[[a,f(x['total_kwh_year'],1),f(x['total_kwh_day_average'],1),f(x['peak_kw'],1),f(x['critical_kwh_year']/1000,1),f(x['aux_kwh_year']/1000,1),f(x['ev_grid_ac_kwh_year']/1000,2)] for a,x in s.items()]))
 parts.append('**Historical LC1:** 402,960 kWh/year, 1,104 kWh/day, 65 kW peak. The revised Central case is **not** a correction to these historical figures; it is a distinct unverified design envelope.\n')
 eq=rows('central_equipment_calculations.csv')
 parts.append('### Equipment rating and central-demand calculation\n')
 parts.append(table(['Non-duplicated category','Tier','Installed assumed kW','Annual energised h','Mean kWh/day'],[[r['category'],r['tier'],f(r['rated_kw'],1),f(r['energized_hours'],0),f(r['mean_kwh_day'],1)] for r in eq]))
 parts.append('Auxiliary central utilisation is 80% of listed site-group ratings when scheduled, and the year-average kWh/day includes actual weekday and seasonal operating hours. Source assumptions are in `config/equipment.csv`; separate heating/cooling end uses do not overlap, and C4ISR cooling is excluded from accommodation ventilation.\n')
 parts.append('## 3. Fleet and controlled charging (normal schedule only)\n')
 fleet=list(csv.DictReader((HERE/'config/fleet.csv').open(newline='',encoding='utf-8')))
 parts.append(table(['Vehicle','Role','Battery kWh','Traction kWh/km','AC charger kW','Min SOC','Mission km'],[[v['vehicle_id'],v['vehicle_class'],v['battery_kwh'],v['traction_kwh_per_km'],v['charger_ac_kw'],v['reserve_soc'],v['mission_km']] for v in fleet]))
 parts.append(table(['Case','EV AC kWh/year','EV DC kWh/year','EV traction kWh/year','Departures','Min observed precharge SOC'],[[case,f(x['ev_grid_ac_kwh_year'],1),f(x['ev_battery_dc_kwh_year'],1),f(x['ev_traction_kwh_year'],1),x['mission_departures'],f(min(x['min_soc_by_vehicle'].values()),3)] for case,x in s.items()]))
 parts.append('All seven proposed vehicles retain at least their independent mission reserve in *unconstrained normal charging* with a shared hypothetical 70 kW charger cap. The model has no OEM support evidence and **does not** couple under-supplied EV charging in islanding back to subsequent individual SOC. Thus it cannot certify mission readiness during outages.\n')
 parts.append('## 4. Reproducible original-site versus revised-site comparison\n')
 original=rows('S0_original_site_rerun_S3_dispatch.csv');rev=rows('revised_load_original_hardware_outage_matrix.csv')
 central=[r for r in rev if r['scenario']=='central']
 parts.append(table(['Outage h','Site model','C4ISR ENS kWh','Total ENS kWh','C4ISR EA %','DG fuel L','End BESS SOC'],[[r['hours_requested'],'S0 original site',f(r['critical_ENS_kwh'],1),f(r['total_ENS_kwh'],1),f(float(r['critical_EA_fraction'])*100,2),f(r['diesel_fuel_used_l'],1),f(r['bess_end_soc'],3)] for r in original]+[[r['hours_requested'],'S1 proposed 120 people',f(r['critical_ENS_kwh'],1),f(r['total_ENS_kwh'],1),f(float(r['critical_EA_fraction'])*100,2),f(r['diesel_fuel_used_l'],1),f(r['bess_end_soc'],3)] for r in central]))
 parts.append('These S0/S1 labels mean *site-load scenarios*; both use the inherited **S3 dispatch policy**, the original 50/50/300/90/100 kW equipment and the same time windows. This is not the legacy dispatch-strategy label S0. 24/72/168 are nested windows with independent initial inventories, not three independent random weather samples.\n')
 parts.append('## 5. Limited nine-point capacity screen (Central, first 168 winter hours)\n')
 cap=rows('capacity_screen_nine_options_168h.csv')
 parts.append(table(['PV/Wind kW','BESS kWh','Indicative CAPEX £','Critical EA %','Total ENS kWh','Fuel used L','Outcome'],[[f(r['pv_kw'],0)+'/'+f(r['wind_kw'],0),f(r['bess_kwh'],0),f(r['capex_gbp_illustrative'],0),f(float(r['critical_EA_fraction'])*100,2) if r['valid']=='True' else '—',f(r['total_ENS_kwh'],1),f(r['diesel_fuel_used_l'],1),r['pareto_capex_vs_total_ENS']] for r in cap]))
 parts.append('**6/9 completed.** Three candidates reached a same-hour BESS charging/discharging exception in the inherited S3 routine and were quarantined. Full errors and exact first failure hours are preserved. The Pareto flag considers illustrative **upfront CAPEX versus total 168-hour ENS only**, restricted to these completed options; there is no global optimum, year-life NPC, or independently verified OEM price.\n')
 parts.append('## 6. Central-scenario deterministic contingency screen (168 h)\n')
 stress=rows('contingency_screen_168h.csv')
 parts.append(table(['Case','C4ISR ENS kWh','Total ENS kWh','DG fuel L','End SOC'],[[r['stress_case'],f(r['critical_ENS_kwh'],1),f(r['total_ENS_kwh'],1),f(r['diesel_fuel_used_l'],1),f(r['bess_end_soc'],3)] for r in stress]))
 parts.append('Emergency DG unavailability occurs for elapsed hours 24–48 in the declared stress input. `LOW_RE_60PCT` is a constructed resource multiplier, not observed bad weather or fault frequency. No refuelling takes place. The inherited energy model assumes an energised AC reference during DG outages; its calculated renewable service does **not** establish grid-forming or black-start feasibility.\n')
 parts.append('## 7. Validation limits and priority next steps\n')
 parts.append('**Confirmed:** source-file identity and 66 software tests; hourly power/energy conservation of completed Python runs; vehicle *planned* SOC reserves, individual AC charger ratings and shared AC power; auditable tier-specific energy accounting.\n')
 parts.append('**Outstanding (mandatory for credible final sizing):** real site load references; source-aligned OEM generator/charger data; normal-grid connection adequacy; vehicle readiness feedback from microgrid `ev_unserved_kw`; controller correction of 3 quarantined cases; multi-season and probabilistic uncertainty if claims require reliability; native MDT/HOMER Pro re-runs under equivalent models; independent review of assumed AC reference and 25 kW dump sink.\n')
 parts.append('**Scope gate:** EV bidirectional supply remains **future/conditional**. Do not add hypothetical 10, 20 or 30 kW V2G contributions until real bidirectional capability and mission reserve evidence are available.\n')
 (HERE/'load_calculation_report.md').write_text('\n'.join(parts),encoding='utf-8')
 print('Wrote',HERE/'load_calculation_report.md')
if __name__=='__main__':main()
