"""T17 HOMER load inputs and manually attested external benchmark comparison.

Load files contain one number per hour, kW, without a header. These are not
native solver projects; never mark any result as native until supplied by user.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
from week7.stage7.benchmark import REFERENCE, rows as benchmark_rows

HERE=Path(__file__).resolve().parent
PROFILE=HERE.parent/'stage3/external_inputs/LC1_reference_profiles_8760.csv'


def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_homer_inputs(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with PROFILE.open(newline='',encoding='utf-8-sig') as f: source=list(csv.DictReader(f))
    if len(source)!=8760:raise ValueError('Input profile must have exactly 8760 rows')
    specs={
        'low_total_planned':'low_total_kw',
        'central_total_planned':'central_total_kw',
        'high_total_planned':'high_total_kw',
        'central_C4ISR_only':'central_critical_kw',
    }
    exported=[]
    for label,field in specs.items():
        vals=[float(row[field]) for row in source]
        if any(not math.isfinite(x) or x<0 for x in vals):raise ValueError(f'Invalid load {label}')
        target=out/f'HOMER_hourly_{label}_8760.txt'
        target.write_text(''.join(f'{v:.12f}\n' for v in vals),encoding='ascii')
        lines=target.read_text(encoding='ascii').splitlines()
        if len(lines)!=8760 or any(not math.isfinite(float(x)) or float(x)<0 for x in lines):
            raise AssertionError('Time series not HOMER-compatible single column')
        # The writer uses fixed precision; manifest describes *exported* totals.
        exported_vals=list(map(float,lines))
        exported.append({'file':target.name,'origin_column':field,'rows':8760,'unit':'kW',
                         'reference_year':'2025 fixed local standard time',
                         'year_start':'2025-01-01 00:00','mean_kw':math.fsum(exported_vals)/8760,
                         'annual_energy_kwh':math.fsum(exported_vals),
                         'peak_kw':max(exported_vals),'sha256':sha256(target),
                         'model_equivalence':'FIXED_PLANNED_EV_LOAD_ONLY_NO_DYNAMIC_SOC_NO_CONTROLLER_PARITY'})
    manifest=out/'stage7_HOMER_import_manifest.csv'
    with manifest.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=exported[0].keys());w.writeheader();w.writerows(exported)
    return exported


def make_template(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fixture=HERE/'outputs/stage7_closed_form_benchmark.csv'
    if not fixture.exists():raise FileNotFoundError('First run benchmark module')
    target=out/'USER_FILL_native_component_results_template.csv'
    with target.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['case_id','metric','unit','external_value'])
        w.writeheader()
        for x in benchmark_rows():
            w.writerow({'case_id':x['case_id'],'metric':x['metric'],'unit':x['unit'],'external_value':''})
    metadata={
        'source_kind':'USER_PROVIDED_NATIVE_EXPORT',
        'software':'', 'software_version':'',
        'native_project_filename':'',
        'native_results_sha256':'',
        'reference_fixture_sha256':sha256(fixture),
        'controller_and_component_parameters_equivalent':False,
        'units_and_timebase_checked':False,
        'native_export_original_path':'',
        'case_scope':'ONLY_TESTED_ANALYTIC_MICRO_BENCHMARKS',
        'not_valid_for_full_168h_or_8760h_hybrid_parity':True,
        'remarks':'Set booleans true only after checking source native software, timestamps, charge/discharge semantics, startup and fuel model.'}
    (out/'USER_FILL_native_provenance_template.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    return metadata


def compare_external(native_csv, metadata_json, output_dir):
    att=json.loads(Path(metadata_json).read_text(encoding='utf-8'))
    if att.get('source_kind')!='USER_PROVIDED_NATIVE_EXPORT':raise ValueError('External provenance class required')
    if att.get('software') not in ('MDT','Microgrid Design Toolkit','HOMER Pro'):
        raise ValueError('Unsupported/unspecified solver')
    if not att.get('software_version') or not att.get('native_project_filename') or not att.get('native_export_original_path'):
        raise ValueError('Native software/version/project/export path must be identified')
    if not att.get('controller_and_component_parameters_equivalent') or not att.get('units_and_timebase_checked'):
        raise ValueError('Input/controller equivalence not signed off; NOT_COMPARABLE')
    fixture=HERE/'outputs/stage7_closed_form_benchmark.csv'
    if att.get('reference_fixture_sha256')!=sha256(fixture):raise ValueError('Reference fixture hash mismatch')
    if att.get('native_results_sha256')!=sha256(native_csv):raise ValueError('Native export file hash mismatch')
    with Path(native_csv).open(newline='',encoding='utf-8-sig') as f: supplied=list(csv.DictReader(f))
    known={(cid,m) for cid,metrics in REFERENCE.items() for m in metrics}
    external={}
    for r in supplied:
        key=(r['case_id'],r['metric'])
        if key not in known or key in external:raise ValueError('Unknown/duplicate metric in external export')
        if r.get('external_value','').strip():
            v=float(r['external_value'])
            if not math.isfinite(v):raise ValueError('Nonfinite native result')
            expected_unit='fraction' if key[1]=='end_soc' else 'L' if key[1].endswith('_l') else 'kWh'
            if r.get('unit')!=expected_unit:raise ValueError('Unit mismatch')
            external[key]=v
    results=[]
    for row in benchmark_rows():
        key=(row['case_id'],row['metric']);value=external.get(key)
        tol=float(row['tolerance']);ref=float(row['reference_value'])
        diff=abs(value-ref) if value is not None else None
        results.append({'case_id':key[0],'metric':key[1],'reference_analytical':ref,
                        'external_reported':value if value is not None else '',
                        'unit':row['unit'],'absolute_difference':diff if diff is not None else '',
                        'numeric_tolerance':tol,
                        'comparison_status':('MISSING_NATIVE_METRIC' if value is None else
                            'WITHIN_NUMERIC_TOLERANCE' if diff<=tol else 'NUMERIC_DISAGREEMENT')})
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/'external_component_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=results[0].keys());w.writeheader();w.writerows(results)
    summary={'results':len(results),'within_tolerance':sum(r['comparison_status']=='WITHIN_NUMERIC_TOLERANCE' for r in results),
             'numeric_disagreement':sum(r['comparison_status']=='NUMERIC_DISAGREEMENT' for r in results),
             'missing':sum(r['comparison_status']=='MISSING_NATIVE_METRIC' for r in results),
             'claimed_solver':att['software'],'version':att['software_version'],
             'external_native_origin_independently_verified':False,
             'full_LC1_hybrid_dispatch_parity':False,
             'evidence_class':'USER_ATTESTED_EXTERNAL_COMPARISON_REQUIRES_SOURCE_REVIEW'}
    (output_dir/'external_component_comparison_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return summary


def run(out):
    rows=write_homer_inputs(out)
    meta=make_template(out)
    return {'HOMER_single_column_8760h_inputs':len(rows),'all_8760_rows':True,
            'external_result_template_rows':sum(len(v) for v in REFERENCE.values()),
            'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--native',type=Path);parser.add_argument('--metadata',type=Path)
    parser.add_argument('--out',type=Path,default=HERE/'external_handoff')
    args=parser.parse_args()
    print(json.dumps(compare_external(args.native,args.metadata,args.out) if args.native and args.metadata else run(args.out),indent=2))
