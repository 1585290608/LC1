"""Transparent20year real-GBP cashflow model. No tariffs/quotes invented as evidence."""
from pathlib import Path
import json,math
PARAMETERS_PATH=Path(__file__).resolve().parent / "config" / "economic-parameters.json"
def parameters():return json.loads(PARAMETERS_PATH.read_text())
def capital(kind,p=None):
    p=p or parameters();q=p['equipment'];rates=p['unit_costs'];items=[]
    def add(asset,amount,unit,rate,scope):items.append({'asset':asset,'quantity':amount,'unit':unit,'unit_cost_gbp':rate,'CAPEX_gbp':amount*rate,'scope':scope,'status':'ASSUMPTION_ONLY_NOT_QUOTATION'})
    if kind=='HYBRID':
        add('PV',q['pv_kw'],'kWp_DC',rates['pv'],'PV assembly including PV inverter, excluding common site works')
        add('Wind',q['wind_kw'],'kW',rates['wind'],'Turbine/conversion assembly, excluding common site works')
        add('BESS_DC',q['battery_kwh'],'kWh',rates['battery_dc'],'DC battery/racks/BMS only; excludes standalone PCS')
        add('BESS_PCS',q['pcs_kw'],'kW',rates['pcs'],'Standalone BESS PCS; not counted in DC battery cost')
    if kind in ('P0R','HYBRID'):
        add('DG',1,'100kW_unit',rates['diesel'],'One100kW backup generator')
        add('UPS',1,'30kW_15min_system',rates['ups'],'Separate7.5kWh AC ideal support; no BESS capacity overlap')
        add('Common_site',1,'site_allowance',rates['common_site'],'Same civils/switchgear/installation allowance in P0R and hybrid')
        add('Tank_fixed',1,'system',rates['tank_fixed'],'Tank fixed infrastructure, excludes fuel')
        add('Tank_volume',q['fuel_tank_l'],'L_capacity',rates['tank_per_l'],'Tank capacity allowance, not diesel inventory')
    capex=math.fsum(x['CAPEX_gbp'] for x in items);stock=q['fuel_tank_l']*p['fuel_gbp_l'] if kind!='P0' else 0.
    return items,capex,stock
def annual_cost(metrics,price=None,p=None):
    p=p or parameters();price=p['import_gbp_kwh'] if price is None else price
    _,capex,stock=capital(metrics['kind'],p)
    purchase=metrics['grid_import_kwh']*price;revenue=metrics['grid_export_kwh']*p['export_gbp_kwh'];om=capex*p['OM_fraction'];standing=p['standing_gbp_day']*365
    return {'annual_purchase_gbp':purchase,'annual_conditional_export_revenue_gbp':revenue,'annual_OM_gbp':om,'annual_standing_gbp':standing,'annual_operating_cost_gbp':purchase-revenue+om+standing,'CAPEX_gbp':capex,'fuel_working_inventory_gbp':stock,'initial_cash_outflow_gbp':capex+stock,'annual_operational_CO2e_kg':metrics['grid_import_kwh']*p['grid_factor_kgCO2e_kwh'],'CO2e_boundary':'Location-based Scope2 purchased electricity; no export offset, T&D/WTT/embodied emissions excluded; DG off'}
def cashflows(metrics,price=None,p=None):
    p=p or parameters();annual=annual_cost(metrics,price,p);items,capex,stock=capital(metrics['kind'],p);costs={x['asset']:x['CAPEX_gbp'] for x in items};records=[]
    for year in range(p['years']+1):
        replacement=0.;details=[]
        for asset,rule in p['replacements'].items():
            if year==rule['year'] and asset in costs:replacement+=costs[asset]*rule['fraction'];details.append(asset)
        investment=capex if year==0 else 0.;fuel_in=stock if year==0 else 0.;recovery=stock if year==p['years'] else 0.;operating=annual['annual_operating_cost_gbp'] if year else 0.
        cost=investment+fuel_in+operating+replacement-recovery
        records.append({'year':year,'equipment_CAPEX_gbp':investment,'fuel_inventory_purchase_gbp':fuel_in,'operating_cost_gbp':operating,'replacement_cost_gbp':replacement,'replacement_assets':';'.join(details),'fuel_inventory_recovery_gbp':recovery,'net_cost_gbp':cost,'discount_factor':(1+p['discount'])**(-year),'discounted_cost_gbp':cost/(1+p['discount'])**year})
    return records,annual
def payback_details(incremental,discount):
    """Positive cashflow = comparator cost minus project cost, year0 includes investment.
    Interpolation is an accounting convention between year-end observations, not a payment schedule.
    Sustained payback requires every later saved cumulative cashflow to remain nonnegative.
    """
    def calc(values):
        cumul=[];a=0.
        for x in values:a+=x;cumul.append(a)
        first=next((i for i in range(1,len(values)) if cumul[i]>=-1e-9 and cumul[i-1]<-1e-9),None)
        sustained=next((i for i in range(1,len(values)) if cumul[i]>=-1e-9 and all(v>=-1e-9 for v in cumul[i:])),None)
        def when(i):return (i-1)+(-cumul[i-1])/values[i] if i is not None and values[i]>0 and cumul[i-1]<0 else float(i) if i is not None else None
        return when(first),when(sustained),cumul
    first,simple,cum=calc(incremental);dfirst,discounted,dcum=calc([v/(1+discount)**y for y,v in enumerate(incremental)])
    return {'first_undiscounted_crossing_year':first,'simple_payback_including_replacements_year':simple,'first_discounted_crossing_year':dfirst,'discounted_sustained_payback_year':discounted,'undiscounted_cumulative':cum,'discounted_cumulative':dcum}
def evaluate(metrics,price=None,p=None,comparator_metrics=None):
    p=p or parameters();flows,annual=cashflows(metrics,price,p)
    npc=math.fsum(r['discounted_cost_gbp'] for r in flows)
    result={**metrics,**annual,'import_price_gbp_kwh':p['import_gbp_kwh'] if price is None else price,'NPC_20y_gbp':npc,'comparison':'P0R same electricity price/export assumptions, no outages'}
    increments=[]
    if metrics['kind']=='HYBRID' and comparator_metrics:
        ref,_=cashflows(comparator_metrics,price,p);incs=[r['net_cost_gbp']-c['net_cost_gbp'] for r,c in zip(ref,flows)]
        pb=payback_details(incs,p['discount']);result.update({k:v for k,v in pb.items() if 'cumulative' not in k})
        result['NPC_saving_vs_P0R_gbp']=math.fsum(r['discounted_cost_gbp'] for r in ref)-npc
        result['annual_operating_saving_vs_P0R_gbp']=ref[1]['operating_cost_gbp']-annual['annual_operating_cost_gbp']
        result['incremental_initial_cash_gbp']=annual['initial_cash_outflow_gbp']-ref[0]['net_cost_gbp']
        savings=result['annual_operating_saving_vs_P0R_gbp'];result['naive_CAPEX_over_annual_saving_year']=result['incremental_initial_cash_gbp']/savings if savings>0 else None
        for y,x in enumerate(incs):increments.append({'year':y,'incremental_net_cashflow_gbp':x,'discounted_incremental_cashflow_gbp':x/(1+p['discount'])**y,'cumulative_gbp':pb['undiscounted_cumulative'][y],'discounted_cumulative_gbp':pb['discounted_cumulative'][y]})
    else:
        for key in ['first_undiscounted_crossing_year','simple_payback_including_replacements_year','first_discounted_crossing_year','discounted_sustained_payback_year','NPC_saving_vs_P0R_gbp','annual_operating_saving_vs_P0R_gbp','incremental_initial_cash_gbp','naive_CAPEX_over_annual_saving_year']:result[key]=None
    result['payback_status']='ACHIEVED_WITHIN_20Y' if result['discounted_sustained_payback_year'] is not None else 'NOT_APPLICABLE' if metrics['kind']!='HYBRID' else 'NOT_ACHIEVED_WITHIN_20Y'
    return result,flows,increments
