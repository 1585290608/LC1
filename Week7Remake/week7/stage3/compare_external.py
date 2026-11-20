"""T17 conservative numeric comparison with *user-supplied* external exports.

Cannot verify which software produced an uploaded file. Metadata/authenticity must
be independently inspected. No synthetic 'native' result is bundled.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path

HERE=Path(__file__).resolve().parent
REFERENCE=HERE.parent/'nextstage/outputs/seasonal_nine_candidates_24_72_168h.csv'
METRICS=('critical_ENS_kwh','aux_ENS_kwh','ev_ENS_kwh',
         'total_ENS_kwh','diesel_fuel_used_l','bess_end_soc','critical_EA_fraction')

def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rows(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def case_id(r):
    return f"{r['season']}_H{int(r['requested_h'])}_PV{int(float(r['pv_kw']))}_W{int(float(r['wind_kw']))}_B{int(float(r['bess_kwh']))}"

def validate_metadata(metadata_path,native_path):
    att=json.loads(Path(metadata_path).read_text(encoding='utf-8'))
    prov=json.loads((HERE/'external_inputs/LC1_external_input_provenance.json').read_text(encoding='utf-8'))
    if att.get('source_kind')!='USER_PROVIDED_NATIVE_EXPORT':raise ValueError('Wrong provenance class')
    if att.get('software') not in ('MDT','Microgrid Design Toolkit','HOMER Pro'):
        raise ValueError('Software must be explicit MDT or HOMER Pro')
    if not att.get('tool_version') or not att.get('source_export_path'):
        raise ValueError('Native solver version/path missing')
    if not att.get('configuration_equivalence_checklist_signed_off'):
        raise ValueError('Full input/controller equivalence not attested; must remain NOT_COMPARABLE')
    if sha256(native_path)!=att.get('native_result_file_sha256'):
        raise ValueError('External export checksum does not match stated provenance')
    if prov['input_profile_sha256']!=att.get('reference_input_profile_sha256'):
        raise ValueError('Different hourly reference input profiles')
    if prov['case_manifest_sha256']!=att.get('reference_case_manifest_sha256'):
        raise ValueError('Different scenario input manifest')
    if prov['fuel_curve_sha256']!=att.get('reference_fuel_curve_sha256'):
        raise ValueError('Different archived diesel fuel curve')
    return att

def compare_numeric(reference,native):
    out=[]
    for name in METRICS:
        if name not in reference or name not in native or not str(native[name]).strip():
            out.append({'metric':name,'status':'MISSING_EXTERNAL_METRIC','python':reference.get(name,''),
                        'external':native.get(name,''),'absolute_difference':''});continue
        a=float(reference[name]);b=float(native[name]);d=abs(a-b)
        if not math.isfinite(a) or not math.isfinite(b):raise ValueError('Nonfinite numeric evidence')
        # Tight enough to identify EMS divergences, not a claim of transient equality.
        absolute=.001 if name!='bess_end_soc' and name!='critical_EA_fraction' else .0001
        tolerance=max(absolute,.001*max(abs(a),abs(b)))
        out.append({'metric':name,'status':'WITHIN_NUMERIC_TOLERANCE' if d<=tolerance else 'NUMERIC_DISAGREEMENT',
                    'python':a,'external':b,'absolute_difference':d,'allowed_difference':tolerance})
    return out

def run(native_path,metadata_path,output_dir):
    att=validate_metadata(metadata_path,native_path)
    external=rows(native_path);ref=rows(REFERENCE)
    lookup={case_id(x):x for x in ref}
    if len(lookup)!=108 or len(ref)!=108:raise ValueError('Expected exactly 108 existing reference scenarios')
    if len({x['case_id'] for x in external})!=len(external):raise ValueError('Duplicate native case IDs')
    if len(external)==0:raise ValueError('External CSV contains no cases')
    results=[]
    for item in external:
        key=item['case_id']
        if key not in lookup:raise ValueError(f'Unrecognised scenario {key}')
        results.extend([{'case_id':key,**x} for x in compare_numeric(lookup[key],item)])
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/'user_external_numeric_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['case_id','metric','status','python','external','absolute_difference','allowed_difference'])
        writer.writeheader();writer.writerows(results)
    summary={'source_class':'USER_ATTESTED_EXTERNAL_EXPORT_NOT_INDEPENDENTLY_AUTHENTICATED',
             'software_reported':att['software'],'version_reported':att['tool_version'],
             'cases_supplied':len(external),'reference_cases':108,
             'metrics_within_tolerance':sum(x['status']=='WITHIN_NUMERIC_TOLERANCE' for x in results),
             'metrics_disagree':sum(x['status']=='NUMERIC_DISAGREEMENT' for x in results),
             'metrics_missing':sum(x['status']=='MISSING_EXTERNAL_METRIC' for x in results),
             'full_hybrid_parity_claimed':False,
             'instruction':'Review native source authenticity, parameter and control equivalence before any parity claim.'}
    (output_dir/'user_external_numeric_comparison_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--out',type=Path,default=HERE/'outputs/external_compare')
    a=p.parse_args();print(json.dumps(run(a.native,a.metadata,a.out),indent=2))
