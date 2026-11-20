"""WP2 T09 / WP4 T16 conditional economic screening from Stage3/4 results.

No probabilistic outage frequency, independent field-price evidence, native MDT,
HOMER Pro or normal-operation dispatch is contained in this calculation.
The financial output is PV OF SELECTED CASH STREAMS, not an NPC.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
import csv, json, math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ECON_SOURCE = ROOT / 'models/grid_connected/config/economic-parameters.json'
SCENARIO_SOURCE = HERE / 'config/cost_scenarios.json'


def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def historical_parameters():
    p = json.loads(ECON_SOURCE.read_text(encoding='utf-8'))
    required = {'years','discount','unit_costs','OM_fraction','fuel_gbp_l','replacements','equipment'}
    if not required.issubset(p):
        raise ValueError(f'Missing inherited parameters: {required-set(p)}')
    if p['years'] <= 0 or p['discount'] <= -1 or p['fuel_gbp_l'] < 0:
        raise ValueError('Nonphysical inherited financial inputs')
    return p


@dataclass(frozen=True)
class Sensitivity:
    hypothetical_events_pa: int = 1
    trip_fee_gbp: float = 500.
    delivery_premium_gbp_per_l: float = .20
    diesel_gbp_per_l: float = 1.35
    bess_rate_multiplier: float = 1.
    shadow_critical_gbp_per_kwh: float = 0.
    shadow_noncritical_gbp_per_kwh: float = 0.

    def __post_init__(self):
        if type(self.hypothetical_events_pa) is not int or self.hypothetical_events_pa < 0:
            raise ValueError('Outage event repetition must be a nonnegative integer')
        vals=(self.trip_fee_gbp,self.delivery_premium_gbp_per_l,self.diesel_gbp_per_l,
              self.bess_rate_multiplier,self.shadow_critical_gbp_per_kwh,
              self.shadow_noncritical_gbp_per_kwh)
        if any(not math.isfinite(x) or x < 0 for x in vals) or self.bess_rate_multiplier <= 0:
            raise ValueError('Invalid price / shadow input')


def capex_detail(pv_kw, wind_kw, bess_kwh, setting:Sensitivity, p=None):
    p = p or historical_parameters()
    if min(pv_kw, wind_kw, bess_kwh) < 0:raise ValueError('Negative component capacity')
    q=p['equipment']; r=p['unit_costs']
    parts={
        'PV':pv_kw*r['pv'],
        'Wind':wind_kw*r['wind'],
        'BESS_DC':bess_kwh*r['battery_dc']*setting.bess_rate_multiplier,
        'BESS_PCS':q['pcs_kw']*r['pcs'],
        'DG':r['diesel'],
        'UPS':r['ups'],
        'Common_site':r['common_site'],
        'Tank_fixed':r['tank_fixed'],
        'Tank_volume':q['fuel_tank_l']*r['tank_per_l']
    }
    return parts


def replacement_cost_at(year:int,parts:dict,p:dict):
    total=0.
    for name,item in p['replacements'].items():
        if year==item['year']:
            if name not in parts:raise ValueError(f'Unknown replacement component {name}')
            total += parts[name]*item['fraction']
    return total


def present_value_components(pv_kw,wind_kw,bess_kwh,setting:Sensitivity,p=None):
    """20y PV including initial/terminal fuel *inventory* and selected O&M.

    Fuel inventory is purchased at year0 and recovered at year20. This assumes
    end inventory still saleable with no discount/degradation/transport cost.
    """
    p=p or historical_parameters()
    parts=capex_detail(pv_kw,wind_kw,bess_kwh,setting,p)
    installed_capex=math.fsum(parts.values())
    q=p['equipment'];fuel_inventory=q['fuel_tank_l']*setting.diesel_gbp_per_l
    fixed_om=installed_capex*p['OM_fraction']
    discounted_om=math.fsum(fixed_om/(1+p['discount'])**y for y in range(1,p['years']+1))
    discounted_replacements=math.fsum(replacement_cost_at(y,parts,p)/(1+p['discount'])**y for y in range(1,p['years']+1))
    inventory_recovery_pv=fuel_inventory/(1+p['discount'])**p['years']
    return {'capex_gbp':installed_capex,'fixed_OM_annual_gbp':fixed_om,
            'replacement_pv_gbp':discounted_replacements,'fixed_OM_pv_gbp':discounted_om,
            'fuel_inventory_gbp_at_year0':fuel_inventory,
            'fuel_inventory_recovery_pv_gbp':inventory_recovery_pv,
            'base_selected_pv_gbp':installed_capex+discounted_om+discounted_replacements+fuel_inventory-inventory_recovery_pv}


def delivery_attempts(policy_name):
    """Only approved scenario identifiers: count scheduled dispatched trips, not accepted litres."""
    mapping={'BASE':0,'REFUEL_500_H72':1,'REFUEL_500_H48_H96_H144':3}
    if policy_name not in mapping:raise ValueError(f'Policy not in economic choice set: {policy_name}')
    return mapping[policy_name]


def score_case(case:dict, setting:Sensitivity,p=None):
    p = p or historical_parameters()
    pv=float(case['pv_kw']);wind=float(case['wind_kw']);bess=float(case['bess_kwh'])
    if any(not math.isfinite(x) or x<0 for x in (pv,wind,bess)):raise ValueError('Capacity invalid')
    if int(case['window_count']) != 52:raise ValueError('All economic comparisons must use same 52 outage starts')
    total=float(case['mean_total_ENS_kwh']);critical=float(case['mean_critical_ENS_kwh'])
    fuel=float(case['mean_fuel_consumption_l']);delivered=float(case['mean_accepted_delivery_l'])
    if any(not math.isfinite(x) or x < -1e-7 for x in (total,critical,fuel,delivered)) or critical>total+1e-6:
        raise ValueError('Invalid energy/cost metrics')
    policy=case['policy'];trips=delivery_attempts(policy)
    capital=present_value_components(pv,wind,bess,setting,p)
    event_fuel_purchase=fuel*setting.diesel_gbp_per_l
    event_delivery_premium=delivered*setting.delivery_premium_gbp_per_l
    event_trip_fees=trips*setting.trip_fee_gbp
    event_cash=event_fuel_purchase+event_delivery_premium+event_trip_fees
    # Shadow energy costs are a separate preference/sensitivity, not an invoice.
    event_shadow=(critical*setting.shadow_critical_gbp_per_kwh
                 +(total-critical)*setting.shadow_noncritical_gbp_per_kwh)
    factor=math.fsum(1/(1+p['discount'])**year for year in range(1,p['years']+1))
    pv_event_cash=event_cash*setting.hypothetical_events_pa*factor
    pv_shadow=event_shadow*setting.hypothetical_events_pa*factor
    out={
        'policy':policy,'pv_kw':pv,'wind_kw':wind,'bess_kwh':bess,
        'window_count':52,'duration_h':168,
        'critical_shortfall_windows':int(case['critical_shortfall_windows']),
        'mean_critical_ENS_kwh':critical,'mean_total_ENS_kwh':total,
        'worst_total_ENS_kwh':float(case['worst_total_ENS_kwh']),
        'mean_diesel_fuel_consumption_l_per_event':fuel,
        'mean_accepted_delivery_l_per_event':delivered,'scheduled_delivery_trips_per_event':trips,
        'hypothetical_events_per_year':setting.hypothetical_events_pa,
        'trip_fee_assumption_gbp':setting.trip_fee_gbp,
        'delivery_premium_assumption_gbp_per_l':setting.delivery_premium_gbp_per_l,
        'diesel_price_assumption_gbp_per_l':setting.diesel_gbp_per_l,
        'bess_rate_multiplier':setting.bess_rate_multiplier,
        'shadow_critical_gbp_per_kwh':setting.shadow_critical_gbp_per_kwh,
        'shadow_noncritical_gbp_per_kwh':setting.shadow_noncritical_gbp_per_kwh,
        **capital,
        'mean_event_fuel_purchase_gbp':event_fuel_purchase,
        'mean_event_delivery_premium_gbp':event_delivery_premium,
        'mean_event_trip_fees_gbp':event_trip_fees,
        'mean_event_cash_gbp':event_cash,
        'mean_event_shadow_cost_gbp':event_shadow,
        'discounted_hypothetical_outage_cash_gbp':pv_event_cash,
        'selected_20y_cashflow_PV_gbp_NOT_NPC':capital['base_selected_pv_gbp']+pv_event_cash,
        'shadow_cost_PV_gbp_NOT_CASH':pv_shadow,
        'generalised_score_PV_gbp_NOT_NPC':capital['base_selected_pv_gbp']+pv_event_cash+pv_shadow,
        'claim_class':'ILLUSTRATIVE_CONDITIONAL_NOT_NPC_NOT_EENS_NOT_NATIVE_VALIDATED'
    }
    return out


def financial_years(case,setting:Sensitivity,p=None):
    p=p or historical_parameters()
    score=score_case(case,setting,p)
    parts=capex_detail(float(case['pv_kw']),float(case['wind_kw']),float(case['bess_kwh']),setting,p)
    inv=score['fuel_inventory_gbp_at_year0']
    result=[]
    for y in range(p['years']+1):
        capex=score['capex_gbp'] if y==0 else 0.
        working=inv if y==0 else 0.
        recover=inv if y==p['years'] else 0.
        om=score['fixed_OM_annual_gbp'] if y>0 else 0.
        replace_at=replacement_cost_at(y,parts,p)
        outage_event_cash=score['mean_event_cash_gbp']*setting.hypothetical_events_pa if y>0 else 0.
        shadow=score['mean_event_shadow_cost_gbp']*setting.hypothetical_events_pa if y>0 else 0.
        actual=capex+working-recover+om+replace_at+outage_event_cash
        result.append({'year':y,'capex_gbp':capex,'working_fuel_inventory_gbp':working,
              'terminal_fuel_inventory_recovery_gbp':recover,
              'fixed_OM_gbp':om,'replacement_gbp':replace_at,'hypothetical_outage_cash_gbp':outage_event_cash,
              'selected_cash_cost_gbp':actual,'selected_cash_PV_gbp':actual/(1+p['discount'])**y,
              'noncash_unserved_shadow_gbp':shadow,
              'noncash_unserved_shadow_PV_gbp':shadow/(1+p['discount'])**y})
    return result


def pareto_labels(rows):
    """Only among like-for-like 52-start cases. No probability/NPC dominance claim."""
    indices=('selected_20y_cashflow_PV_gbp_NOT_NPC','mean_total_ENS_kwh','mean_critical_ENS_kwh','critical_shortfall_windows')
    for a in rows:
        dominated=False
        for b in rows:
            if a is b:continue
            if all(float(b[k]) <= float(a[k])+1e-7 for k in indices) and any(float(b[k]) < float(a[k])-1e-7 for k in indices):
                dominated=True;break
        a['conditional_four_axis_pareto']='DOMINATED' if dominated else 'NONDOMINATED_IN_THIS_FINITE_SET'
    return rows
