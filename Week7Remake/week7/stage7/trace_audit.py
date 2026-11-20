"""Read-only independent re-computation of saved Stage 4/6 hourly ledgers.

Checks derive energy equations directly from recorded flows, not from the
original dispatcher residual columns. They are not an external solver check.
"""
from __future__ import annotations
import csv, math, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent


def load_rows(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def check(predicate, reason):
    if not predicate:raise AssertionError(reason)


def audit_grid_trace(path, capacity_kwh, import_limit_kw, eta_charge=.8944,eta_discharge=.8944):
    records=load_rows(path)
    check(len(records)==8760,'Grid trace needs 8760 hours')
    max_ac=max_dc=max_soc_gap=0.
    total_critical=total_ev=total_grid=0.
    old_final=None
    for h,r in enumerate(records):
        d=lambda key:float(r[key])
        check(int(r['hour_index'])==h,'Hour index continuity')
        required=sum(d(f'{x}_required_kw') for x in ('c4isr','aux','ev'))
        served=sum(d(f'{x}_served_kw') for x in ('c4isr','aux','ev'))
        unserved=sum(d(f'{x}_unserved_kw') for x in ('c4isr','aux','ev'))
        check(abs(required-served-unserved)<1e-7,'Tier load accounting')
        for x in ('c4isr','aux','ev'):
            check(d(f'{x}_required_kw')>=-1e-7,'Negative demand')
            check(d(f'{x}_served_kw')>=-1e-7 and d(f'{x}_unserved_kw')>=-1e-7,'Negative service')
            check(abs(d(f'{x}_required_kw')-d(f'{x}_served_kw')-d(f'{x}_unserved_kw'))<1e-7,'Tier mismatch')
        check(not(d('c4isr_unserved_kw')>1e-7 and
                  (d('aux_served_kw')>1e-7 or d('ev_served_kw')>1e-7)), 'Critical precedence')
        check(not(d('aux_unserved_kw')>1e-7 and d('ev_served_kw')>1e-7),'Aux priority')
        check(d('grid_import_kw')<=import_limit_kw+1e-7,'Feeder constraint')
        check(not(d('grid_import_kw')>1e-7 and d('grid_export_kw')>1e-7),'Grid directions')
        check(not(d('bess_charge_kw')>1e-7 and d('bess_discharge_kw')>1e-7),'Battery directions')
        check(d('bess_charge_kw')<=90.+1e-7 and d('bess_discharge_kw')<=90.+1e-7,'PCS cap')
        start,end=d('battery_soc_initial'),d('battery_soc_final')
        check(.1-1e-7<=start<=.9+1e-7 and .1-1e-7<=end<=.9+1e-7,'SOC safe range')
        if old_final is not None:
            max_soc_gap=max(max_soc_gap,abs(old_final-start))
            check(abs(old_final-start)<1e-7,'Battery SOC continuity')
        old_final=end
        # Independent AC and DC balance; 1h sample length.
        ac=d('renewable_used_kw')+d('grid_import_kw')+d('bess_discharge_kw')-served-d('bess_charge_kw')-d('grid_export_kw')
        dc=(end-start)*capacity_kwh-d('bess_charge_kw')*eta_charge+d('bess_discharge_kw')/eta_discharge
        loss=d('bess_charge_kw')*(1-eta_charge)+d('bess_discharge_kw')*(1/eta_discharge-1)
        check(abs(loss-d('battery_loss_kwh'))<1e-7,'Battery losses recomputed')
        check(abs(ac)<1e-7 and abs(dc)<1e-7,'AC/DC conservation')
        max_ac=max(max_ac,abs(ac)); max_dc=max(max_dc,abs(dc))
        total_critical+=d('c4isr_unserved_kw');total_ev+=d('ev_unserved_kw')
        total_grid+=d('grid_import_kw')
    return {'trace':Path(path).name,'hours':len(records),'verified':'PASS_INDEPENDENT_LEDGER_AUDIT',
            'independent_max_ac_residual_kwh':max_ac,
            'independent_max_battery_residual_kwh':max_dc,
            'max_soc_continuity_gap':max_soc_gap,
            'critical_shortfall_kwh':total_critical,
            'ev_hourly_charging_request_deficit_kwh_NOT_PERMANENT_LOSS':total_ev,
            'grid_import_kwh':total_grid,
            'native_solver_validation':False}


def audit_outage_trace(path, bess_kwh=450.,tank_l=2000.):
    records=load_rows(path)
    check(len(records)==168,'Selected 168h outage trace expected')
    old_soc=None;old_fuel=None;max_soc=max_fuel=max_ac=0.
    critical=0.;fuel_consumed=0.
    for h,r in enumerate(records):
        d=lambda key:float(r[key])
        check(int(r['elapsed_hour'])==h,'Outage elapsed hour continuity')
        # Fuel conservation from raw inventory/delivery/usage columns.
        remaining=d('fuel_final_l');start=d('fuel_initial_l')
        accepted=d('hour_start_delivery_accepted_l');burned=d('dg_fuel_consumed_l')
        error=start-burned-remaining
        max_fuel=max(max_fuel,abs(error))
        check(abs(error)<1e-7,'Diesel fuel conservation')
        check(remaining>=-1e-7 and remaining<=tank_l+1e-7,'Tank constraints')
        if old_fuel is not None:check(abs(old_fuel+accepted-start)<1e-7,'Fuel continuity with hour-start delivery')
        old_fuel=remaining
        b_start,b_end=d('soc_initial'),d('soc_final')
        if old_soc is not None:check(abs(old_soc-b_start)<1e-7,'Battery continuity')
        old_soc=b_end
        dc=(b_end-b_start)*bess_kwh - d('bess_charge_kw')*.8944 + d('bess_discharge_kw')/.8944
        max_soc=max(max_soc,abs(dc))
        check(abs(dc)<1e-6,'Battery DC conservation')
        ac=(d('pv_actual_kw')+d('wind_actual_kw')+d('dg_generated_kw')+
            d('bess_discharge_kw')+d('ups_output_kw')+d('grid_import_kw')-
            d('c4isr_served_kw')-d('aux_served_kw')-d('ev_served_kw')-
            d('bess_charge_kw')-d('ups_charge_kw')-d('grid_export_kw')-d('dg_dumped_kw'))
        max_ac=max(max_ac,abs(ac))
        check(abs(ac)<1e-6,'Outage AC conservation')
        check(not(d('bess_charge_kw')>1e-7 and d('bess_discharge_kw')>1e-7),'BESS directions')
        critical+=d('c4isr_unserved_kw');fuel_consumed+=burned
    return {'trace':Path(path).name,'hours':len(records),'verified':'PASS_INDEPENDENT_LEDGER_AUDIT',
            'independent_max_ac_residual_kwh':max_ac,
            'independent_max_battery_residual_kwh':max_soc,
            'independent_max_fuel_residual_l':max_fuel,
            'critical_shortfall_kwh':critical,'fuel_consumed_l':fuel_consumed,
            'native_solver_validation':False}


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    grid=ROOT/'week7/stage6/outputs'
    outage=ROOT/'week7/stage4/outputs'
    cases=[
        audit_grid_trace(grid/'stage6_base_central_100kw_hourly_trace.csv',300.,100.),
        audit_grid_trace(grid/'stage6_upper_central_250kw_hourly_trace.csv',450.,250.),
    ]
    cases += [audit_outage_trace(outage/name) for name in (
        'W03_PV100_W100_B450_BASE_hourly_trace.csv',
        'W03_PV100_W100_B450_DG_DOWN_H24_H48_hourly_trace.csv',
        'W03_PV100_W100_B450_REFUEL_500_H48_H96_H144_hourly_trace.csv')]
    with (out/'stage7_readonly_hourly_trace_audit.csv').open('w',newline='',encoding='utf-8') as f:
        fields=list(dict.fromkeys(key for item in cases for key in item))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cases)
    return {'audited_trace_files':len(cases),'hourly_rows':sum(x['hours'] for x in cases),
            'all_independent_ledgers_passed':True,'no_native_solver_run':True}

if __name__=='__main__':print(json.dumps(run(HERE/'outputs'),indent=2))
