"""Independent year-by-year replay of Stage 6 partial cost present value.

No outage event, ENS shadow price or diesel resupply is added to normal-year
cash flows; prevents accidental double counting until event frequency resolved.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
from week7.stage5.economics import read_csv,Sensitivity,historical_parameters,capex_detail,replacement_cost_at
HERE=Path(__file__).resolve().parent
MAIN=HERE.parent/'stage6/outputs/stage6_81_annual_grid_cases.csv'


def replay(out):
    p=historical_parameters(); r=read_csv(MAIN);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    candidates=[x for x in r if float(x['grid_import_limit_kw'])==250 and x['unserved_load_zero']=='True']
    if len(candidates)!=27:raise ValueError(f'Expected exactly 27 fully served 250kW screen cases, found {len(candidates)}')
    ledger=[];compare=[]
    for x in candidates:
        parts=capex_detail(float(x['pv_kw']),float(x['wind_kw']),float(x['bess_kwh']),Sensitivity(),p)
        capex=math.fsum(parts.values());om=capex*p['OM_fraction'];annual_grid_bill=float(x['annual_grid_bill_gbp'])
        inventory=p['equipment']['fuel_tank_l']*p['fuel_gbp_l']
        total_pv=0.
        k=f"{x['scenario']}_PV{int(float(x['pv_kw']))}_W{int(float(x['wind_kw']))}_B{int(float(x['bess_kwh']))}_G250"
        for year in range(0,p['years']+1):
            replacement=replacement_cost_at(year,parts,p) if year>0 else 0.
            initial_capex=capex if year==0 else 0.
            fixed_om=om if year>0 else 0.
            grid_bill=annual_grid_bill if year>0 else 0.
            initial_inventory=inventory if year==0 else 0.
            recovered=-inventory if year==p['years'] else 0.
            cost=math.fsum([initial_capex,fixed_om,grid_bill,replacement,initial_inventory,recovered])
            pv=cost/(1+p['discount'])**year;total_pv+=pv
            ledger.append({'case_id':k,'year':year,'initial_CAPEX_gbp':initial_capex,'fixed_OM_gbp':fixed_om,
                           'normal_grid_bill_gbp':grid_bill,'scheduled_replacements_gbp':replacement,
                           'initial_fuel_working_inventory_gbp':initial_inventory,
                           'terminal_inventory_recovery_gbp':recovered,
                           'outage_fuel_and_logistics_gbp_EXCLUDED':0,
                           'ENS_shadow_price_gbp_EXCLUDED':0,
                           'undiscounted_selected_cashflow_gbp':cost,
                           'discount_factor':(1+p['discount'])**(-year),
                           'selected_cashflow_PV_gbp_NOT_NPC':pv})
        recorded=float(x['selected_normal_year_cash_PV_gbp_NOT_FULL_NPC'])
        if abs(total_pv-recorded)>1e-6:raise AssertionError(f'Cash ledger mismatch for {k}: {total_pv-recorded}')
        compare.append({'case_id':k,'scenario':x['scenario'],'grid_limit_kw':250,
                        'annual_bill_gbp':annual_grid_bill,'initial_CAPEX_gbp':capex,
                        'recomputed_20y_selected_cash_PV_gbp':total_pv,
                        'stage6_reported_cash_PV_gbp':recorded,
                        'absolute_PV_gap_gbp':abs(total_pv-recorded),
                        'outage_events_counted_in_cash_PV':0,
                        'full_NPC':False,'only_economically_comparable_if_service_met':True})
    def dump(path,rows):
        with (out/path).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    dump('stage7_selected_costs_year_by_year_567.csv',ledger)
    dump('stage7_27_service_matched_cash_replay.csv',compare)
    return {'cases':len(compare),'ledger_year_rows':len(ledger),'max_absolute_20y_PV_difference_gbp':max(x['absolute_PV_gap_gbp'] for x in compare),
            'native_homer_npc_comparable':False,'outage_events_counted':0}

if __name__=='__main__':print(json.dumps(replay(HERE/'outputs'),indent=2))
