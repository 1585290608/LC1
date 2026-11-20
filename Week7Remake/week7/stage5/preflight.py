"""T17 read-only provenance, input and historical-run preflight.

This is NOT native Microgrid Design Toolkit / HOMER Pro validation.
It explicitly fails closed when authentic external exports are not supplied.
"""
from __future__ import annotations
import csv,hashlib,json,math
from datetime import datetime,timedelta
from pathlib import Path

from week7.audit.check_preservation import verify

HERE=Path(__file__).resolve().parent
EXT=HERE.parent/'stage3/external_inputs'
S4=HERE.parent/'stage4/outputs'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def csvrows(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def check_inputs():
    results=[]
    def record(name,status,detail):results.append({'check':name,'status':status,'detail':detail})
    origin=json.loads((EXT/'LC1_external_input_provenance.json').read_text(encoding='utf-8'))
    for label,filename,expected in [
        ('profile_source_hash',origin['input_profile_file'],origin['input_profile_sha256']),
        ('external_manifest_hash',origin['case_manifest_file'],origin['case_manifest_sha256']),
        ('active_fuel_curve_hash',origin['fuel_curve_file'],origin['fuel_curve_sha256'])]:
        actual=sha(EXT/filename)
        record(label,'PASS' if actual==expected else 'FAIL',f'SHA-256 {actual}')
    profiles=csvrows(EXT/origin['input_profile_file']);cases=csvrows(EXT/origin['case_manifest_file'])
    fuel_curve=csvrows(EXT/origin['fuel_curve_file'])
    ok=len(profiles)==8760
    if ok:
        for h,r in enumerate(profiles):
            expected_time=(datetime(2025,1,1)+timedelta(hours=h)).isoformat(timespec='seconds')
            if int(r['hour_index_zero_based'])!=h or r['timestamp_2025_fixed_LST']!=expected_time:ok=False;break
            for case in ('low','central','high'):
                parts=[float(r[f'{case}_{x}_kw']) for x in ('critical','aux','ev_planned')]
                total=float(r[f'{case}_total_kw'])
                if not all(math.isfinite(x) and x>=0 for x in parts) or abs(sum(parts)-total)>1e-8:ok=False;break
            if not ok:break
    record('8760_hour_fixed_LST_and_load_sums','PASS' if ok else 'FAIL',f'rows={len(profiles)}; 2025 LST; no DST correction')
    valid_cases=len(cases)==108 and len({r['case_id'] for r in cases})==108
    if valid_cases:
        valid_cases=all(0<=int(r['zero_based_start_hour'])<8760 and
              0<int(r['duration_h'])<=168 and
              int(r['zero_based_start_hour'])+int(r['duration_h'])<=8760 for r in cases)
    record('108_case_manifest','PASS' if valid_cases else 'FAIL',f'{len(cases)} rows')
    valid_curve=len(fuel_curve)==4 and [float(x['on_power_kw']) for x in fuel_curve]==[25,50,75,100]
    record('actual_archived_MDT_DERIVED_curve','PASS' if valid_curve else 'FAIL',f'{len(fuel_curve)} points, not constant 0.25 L/kWh')
    scope, checked, issues = verify()
    record('original_baseline_preserved', 'PASS' if not issues else 'FAIL',
           f'{checked-len(issues)}/{checked} matching ({scope})')
    outputs=csvrows(S4/'stage4_sha256.csv');bad_out=[]
    for r in outputs:
        f=S4/r['relative_file']
        if not f.is_file() or sha(f)!=r['sha256']:bad_out.append(r['relative_file'])
    record('stage4_output_hashes','PASS' if not bad_out else 'FAIL',f'{len(outputs)-len(bad_out)}/{len(outputs)} matching')
    full=csvrows(S4/'stage4_52start_contingency_full.csv');ev=csvrows(S4/'stage4_13start_EV_mission_feedback.csv');parity=csvrows(S4/'stage4_stage3_baseline_parity.csv')
    record('stage4_research_run_counts','PASS' if len(full)==1508 and len(ev)==52 and len(parity)==780 else 'FAIL',f'static={len(full)}, EV={len(ev)}, regression_metrics={len(parity)}')
    valid=all(r['valid']=='True' and r['status']=='PYTHON_DETERMINISTIC_SCENARIO' for r in full)
    record('stage4_scenario_self_consistency','PASS' if valid else 'FAIL','Python validity flags, not external validation')
    provenance_class='NOT_RUN_NEW_NATIVE_MDT_OR_HOMER'
    record('native_MDT_or_HOMER_new_evidence','NOT_PERFORMED', 'No user-produced authenticated native export for revised hybrid model; do not treat generic CSV as native input')
    return {'status':'T17_INTERNAL_PREFLIGHT_ONLY','source_results':results,
      'all_internal_preflight_pass':all(r['status']=='PASS' for r in results if r['status']!='NOT_PERFORMED'),
      'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,
      'provenance_class':provenance_class,'independent_external_validation':False}
