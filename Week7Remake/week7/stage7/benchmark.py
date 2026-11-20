"""Analytical micro-benchmarks for LC1 power/energy component semantics.

The reference values are independently derived from closed-form energy equations,
not by copying the internal dispatch result. They are *not* native MDT/HOMER runs.
"""
from __future__ import annotations
import csv
import json
import math
from dataclasses import replace
from pathlib import Path
from models.core.components import Battery, Diesel
from week7.stage6.annual_grid import AnnualGridCase, dispatch_step

STAGE = Path(__file__).resolve().parent

# Units explicit: each 1h step has numeric kW equal to kWh in that hour.
# 0.25 L/kWh is an intentional *test fixture*, NOT the MDT_DERIVED production curve.
REFERENCE = {
    'DG_24H_STARTUP': {
        'generated_kwh': 920.0, 'fuel_used_l': 230.0, 'critical_ENS_kwh': 40.0,
    },
    'DG_24H_FUEL_LIMIT': {
        'generated_kwh': 500.0, 'fuel_used_l': 125.0, 'critical_ENS_kwh': 700.0,
    },
    'PV_WIND_24H_PRIORITY': {
        'critical_ENS_kwh': 90.0, 'aux_ENS_kwh': 270.0,
        'total_ENS_kwh': 360.0, 'curtailed_kwh': 60.0,
    },
    'BESS_1H_DISCHARGE': {
        'discharged_ac_kwh': 36.0, 'end_soc': 0.3,
        'critical_ENS_kwh': 14.0, 'battery_loss_kwh': 4.0,
    },
    'BESS_1H_RE_CHARGE': {
        'charged_ac_kwh': 40.0, 'end_soc': 0.66,
        'curtailed_kwh': 20.0, 'battery_loss_kwh': 4.0,
    },
    'GRID_1H_PRIORITY': {
        'critical_ENS_kwh': 0.0, 'aux_ENS_kwh': 20.0,
        'ev_request_shortfall_kwh': 10.0, 'grid_import_kwh': 30.0,
    }
}


def battery(c):
    return Battery(c.bess_kwh, c.pcs_kw, c.eta_charge, c.eta_discharge,
                   .1, .9, c.reserve_soc, c.initial_soc)


def execute_fixture(case_id: str) -> dict[str,float]:
    if case_id=='DG_24H_STARTUP':
        dg=Diesel(rated_kw=100.,min_load_fraction=.25,
                  fuel_l_per_kwh=.25,tank_l=2000.,startup_delay_h=1.)
        energies=[dg.dispatch(40.,dt_h=1.) for _ in range(24)]
        return {'generated_kwh':sum(energies),'fuel_used_l':2000.-dg.fuel_l,
                'critical_ENS_kwh':24*40.-sum(energies)}
    if case_id=='DG_24H_FUEL_LIMIT':
        dg=Diesel(rated_kw=100.,min_load_fraction=.25,
                  fuel_l_per_kwh=.25,tank_l=125.,startup_delay_h=0.)
        energies=[dg.dispatch(50.,dt_h=1.) for _ in range(24)]
        return {'generated_kwh':sum(energies),'fuel_used_l':125.-dg.fuel_l,
                'critical_ENS_kwh':24*50.-sum(energies)}
    if case_id=='PV_WIND_24H_PRIORITY':
        c=AnnualGridCase(bess_kwh=100.,pcs_kw=0.,initial_soc=.3,grid_limit_kw=0.)
        b=battery(c)
        rows=[]
        for h in range(24):
            pv=30. if 10<=h<16 else 0.
            r=dispatch_step(c,b,{'c4isr':20.,'aux':15.,'ev':0.},pv,15.,h)
            rows.append(r)
        return {'critical_ENS_kwh':sum(r['c4isr_unserved_kw'] for r in rows),
                'aux_ENS_kwh':sum(r['aux_unserved_kw'] for r in rows),
                'total_ENS_kwh':sum(r['total_unserved_kw'] for r in rows),
                'curtailed_kwh':sum(r['renewable_curtailed_kw'] for r in rows)}
    if case_id=='BESS_1H_DISCHARGE':
        c=AnnualGridCase(bess_kwh=100.,pcs_kw=40.,initial_soc=.7,grid_limit_kw=0.,
                         eta_charge=.9,eta_discharge=.9)
        r=dispatch_step(c,battery(c),{'c4isr':50.,'aux':0.,'ev':0.},0.,0.,0)
        return {'discharged_ac_kwh':r['bess_discharge_kw'],'end_soc':r['battery_soc_final'],
                'critical_ENS_kwh':r['c4isr_unserved_kw'],'battery_loss_kwh':r['battery_loss_kwh']}
    if case_id=='BESS_1H_RE_CHARGE':
        c=AnnualGridCase(bess_kwh=100.,pcs_kw=40.,initial_soc=.3,grid_limit_kw=0.,
                         eta_charge=.9,eta_discharge=.9)
        r=dispatch_step(c,battery(c),{'c4isr':20.,'aux':0.,'ev':0.},80.,0.,0)
        return {'charged_ac_kwh':r['bess_charge_kw'],'end_soc':r['battery_soc_final'],
                'curtailed_kwh':r['renewable_curtailed_kw'],'battery_loss_kwh':r['battery_loss_kwh']}
    if case_id=='GRID_1H_PRIORITY':
        c=AnnualGridCase(bess_kwh=100.,pcs_kw=0.,initial_soc=.3,grid_limit_kw=30.)
        r=dispatch_step(c,battery(c),{'c4isr':40.,'aux':30.,'ev':10.},20.,0.,0)
        return {'critical_ENS_kwh':r['c4isr_unserved_kw'],'aux_ENS_kwh':r['aux_unserved_kw'],
                'ev_request_shortfall_kwh':r['ev_unserved_kw'],'grid_import_kwh':r['grid_import_kw']}
    raise ValueError(f'Unknown benchmark: {case_id}')


def rows():
    result=[]
    for case_id, metrics in REFERENCE.items():
        actual=execute_fixture(case_id)
        if set(actual)!=set(metrics):raise AssertionError(f'Metric shape mismatch {case_id}')
        for name, expected in metrics.items():
            measured=actual[name]
            tolerance=max(1e-8,abs(expected)*1e-9)
            result.append({'case_id':case_id,'metric':name,'reference_value':expected,
                           'python_value':measured,'unit':('fraction' if name=='end_soc' else
                                  'L' if name.endswith('_l') else 'kWh'),
                           'absolute_error':abs(measured-expected),'tolerance':tolerance,
                           'status':'PASS_ANALYTIC' if abs(measured-expected)<=tolerance else 'FAIL_ANALYTIC',
                           'evidence_class':'INDEPENDENT_CLOSED_FORM_FIXTURE_NOT_NATIVE_SOLVER'})
    return result



def fixture_input_rows():
    """Vendor-neutral hourly input schedule; does not encode native UI controls."""
    definitions={
        'DG_24H_STARTUP':(24,40.,0.,0.,0.,0.,0.,100.,2000.,1.,.25,100.,0.,.3,.3,.8944,.8944),
        'DG_24H_FUEL_LIMIT':(24,50.,0.,0.,0.,0.,0.,100.,125.,0.,.25,100.,0.,.3,.3,.8944,.8944),
        'PV_WIND_24H_PRIORITY':(24,20.,15.,0.,0.,15.,0.,0.,0.,0.,.25,100.,0.,.3,.3,.8944,.8944),
        'BESS_1H_DISCHARGE':(1,50.,0.,0.,0.,0.,0.,0.,0.,0.,.25,100.,40.,.7,.3,.9,.9),
        'BESS_1H_RE_CHARGE':(1,20.,0.,0.,80.,0.,0.,0.,0.,0.,.25,100.,40.,.3,.3,.9,.9),
        'GRID_1H_PRIORITY':(1,40.,30.,10.,20.,0.,30.,0.,0.,0.,.25,100.,0.,.3,.3,.8944,.8944),
    }
    fields=('hours','critical_kw','aux_kw','ev_kw','pv_available_kw',
            'wind_available_kw','grid_import_limit_kw','DG_rated_kw','fuel_initial_l',
            'DG_start_delay_h','DG_constant_fuel_l_per_kwh','BESS_capacity_kwh',
            'BESS_PCS_kw','BESS_initial_soc','BESS_reserve_soc','eta_ch','eta_dis')
    out=[]
    for case,vals in definitions.items():
        inputs=dict(zip(fields,vals))
        for h in range(inputs['hours']):
            row={'case_id':case,'hour_index':h,**inputs}
            if case=='PV_WIND_24H_PRIORITY':row['pv_available_kw']=30. if 10<=h<16 else 0.
            out.append(row)
    return out

def run(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    results=rows()
    path=out/'stage7_closed_form_benchmark.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=results[0].keys());writer.writeheader();writer.writerows(results)
    fixture=fixture_input_rows()
    with (out/'stage7_component_fixture_inputs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fixture[0].keys());w.writeheader();w.writerows(fixture)
    success=all(x['status']=='PASS_ANALYTIC' for x in results)
    summary={'benchmarks':len(REFERENCE),'metric_comparisons':len(results),'fixture_hourly_input_rows':len(fixture),
             'passed':sum(x['status']=='PASS_ANALYTIC' for x in results),
             'failed':sum(x['status']=='FAIL_ANALYTIC' for x in results),
             'test_fixture_DG_fuel_l_per_kwh':0.25,
             'production_curve_is_not_tested_here':True,
             'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,
             'external_validation_completed':False}
    (out/'stage7_benchmark_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    if not success:raise AssertionError('Analytic benchmark mismatch')
    return summary

if __name__=='__main__':
    print(json.dumps(run(STAGE/'outputs'),indent=2))
