"""T17 independent, versioned generic interchange inputs for MDT/HOMER.

NOT a native project format, and no native model execution occurs here.
"""
from __future__ import annotations
import csv,hashlib,json
from datetime import datetime,timedelta
from pathlib import Path
from models.core.simulate import Settings
from models.islanded.fuel_models import NativeFuel
from week7.nextstage.screen import LOADS,PV_PU,WIND_PU

HERE=Path(__file__).resolve().parent

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_rows(path,rows,fields=None):
    rows=list(rows)
    if not rows and not fields:raise ValueError('CSV must have header')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

def generate(directory=HERE/'external_inputs'):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    s=Settings()
    curve=NativeFuel()
    hourly=[]
    for h in range(8760):
        dt=datetime(2025,1,1)+timedelta(hours=h)
        row={'hour_index_zero_based':h,'timestamp_2025_fixed_LST':dt.strftime('%Y-%m-%dT%H:%M:%S'),
             'pv_pu_from_original_2025':PV_PU[h], 'wind_pu_from_original_2025':WIND_PU[h]}
        for case in ('low','central','high'):
            obj=LOADS[case]
            row[f'{case}_critical_kw']=obj.c4isr[h]
            row[f'{case}_aux_kw']=obj.aux[h]
            row[f'{case}_ev_planned_kw']=obj.ev[h]
            row[f'{case}_total_kw']=obj.c4isr[h]+obj.aux[h]+obj.ev[h]
        hourly.append(row)
    load_path=directory/'LC1_reference_profiles_8760.csv'
    write_rows(load_path,hourly)
    # Original tools have their own hourly time and dispatch algorithms; verify
    # every parameter below before using outputs as a cross-tool comparison.
    windows={'winter':0,'spring':int((datetime(2025,4,1)-datetime(2025,1,1)).total_seconds()/3600),
             'summer':int((datetime(2025,7,1)-datetime(2025,1,1)).total_seconds()/3600),
             'autumn':int((datetime(2025,10,1)-datetime(2025,1,1)).total_seconds()/3600)}
    fuel_path=directory/'LC1_DG_MDTCatalogue_Fuel_Curve.csv'
    write_rows(fuel_path,[{'on_power_kw':p,'load_fraction':p/s.dg_kw,
                          'fuel_rate_litre_per_hour':curve.rate_lph(p,s.dg_kw),
                          'evidence_class':'ARCHIVED_MDT_DERIVED_NOT_OEM'} for p in (25.,50.,75.,100.)])
    cases=[]
    for season,start in windows.items():
        for dur in (24,72,168):
            for pv in (50,75,100):
                for batt in (300,450,600):
                    cases.append({'case_id':f'{season}_H{dur}_PV{pv}_W{pv}_B{batt}',
                       'season':season,'source_clock':'2025_fixed_LST','zero_based_start_hour':start,
                       'last_included_hour':start+dur-1,'duration_h':dur,'site_case':'central_provisional_120person',
                       'pv_kw':pv,'wind_kw':pv,'bess_kwh':batt,'pcs_kw':s.pcs_kw,
                       'diesel_kw':s.dg_kw,'diesel_min_operating_kw':s.dg_kw*s.dg_min_fraction,
                       'battery_initial_soc':s.initial_soc,'battery_min_soc':s.soc_min,
                       'battery_max_soc':s.soc_max,'battery_dispatch_reserve_soc':s.soc_reserve,
                       'stationary_charge_efficiency':s.eta_charge,
                       'stationary_discharge_efficiency':s.eta_discharge,
                       'diesel_initial_fuel_l':s.fuel_tank_l,
                       'diesel_fuel_model':'MDT_DERIVED_ARCHIVED_CURVE_NOT_FIXED_025',
                       'diesel_curve_filename':fuel_path.name,
                       'diesel_startup_h':s.dg_startup_h,'ups_kw':s.ups_kw,'ups_minutes':s.ups_minutes,
                       'step_h':s.dt_h,'tier_priority':'critical>aux>EV',
                       'controller':'S3_v2_research_hourly','battery_diesel_charging_allowed':True,
                       'research_ac_reference_assumed':True,
                       'homer_objective_aligned':False,'native_algorithm_equivalence_proven':False})
    cases_path=directory/'LC1_108_external_case_manifest.csv'
    write_rows(cases_path,cases)
    template_path=directory/'external_native_results_template.csv'
    write_rows(template_path,[],fields=['case_id','critical_ENS_kwh','aux_ENS_kwh','ev_ENS_kwh',
                                         'total_ENS_kwh','diesel_fuel_used_l','bess_end_soc','critical_EA_fraction'])
    src={'input_profile_file':load_path.name,'input_profile_sha256':sha256(load_path),
         'case_manifest_file':cases_path.name,'case_manifest_sha256':sha256(cases_path),
         'fuel_curve_file':fuel_path.name,'fuel_curve_sha256':sha256(fuel_path),
         'timestamp_convention':'2025 non-leap fixed local standard time, 0-based h, 1 h interval, not UK civil DST',
         'claimed_native_runs':0,'native_format_ready':False,
         'comparability_warning':'The actual DG model is the archived MDT_DERIVED piecewise SFC curve, NOT Settings.fuel_l_per_kwh=0.25. External tools need equivalent load-tier treatment, fuel law, 1h startup, reserve, dump, AC reference, EMS; generic CSV is not native MDT/HOMER format'}
    (directory/'LC1_external_input_provenance.json').write_text(json.dumps(src,indent=2),encoding='utf-8')
    attest={'source_kind':'USER_PROVIDED_NATIVE_EXPORT','software':'REPLACE_WITH_MDT_OR_HOMER',
            'tool_version':'','source_export_path':'','native_result_file_sha256':'',
            'reference_input_profile_sha256':src['input_profile_sha256'],
            'reference_case_manifest_sha256':src['case_manifest_sha256'],
            'reference_fuel_curve_sha256':src['fuel_curve_sha256'],
            'configuration_equivalence_checklist_signed_off':False,
            'note':'Set this only after actually using the external software and auditing scenario settings.'}
    (directory/'external_native_metadata_template.json').write_text(json.dumps(attest,indent=2),encoding='utf-8')
    return src

if __name__=='__main__': print(json.dumps(generate(),indent=2))
