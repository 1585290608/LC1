"""Additional WP2/4/5 integrity and external validation gate tests."""
from __future__ import annotations
import csv,json,math
from pathlib import Path
import pytest
from week7.stage3.compare_external import compare_numeric,validate_metadata,METRICS
from week7.stage3.external_protocol import sha256
from week7.nextstage.screen import PV_PU,WIND_PU

HERE=Path(__file__).resolve().parents[1]

def csvrows(p):
    with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def test_52_week_duration_grid_and_physical_checks():
    rows=csvrows(HERE/'outputs/weekly_52_starts_full.csv')
    assert len(rows)==52*3*9==1404
    assert len({r['case_id'] for r in rows})==1404
    assert all(r['valid']=='True' and r['status']=='PYTHON_SCREEN_COMPLETE' for r in rows)
    assert all(float(r['max_AC_residual_kwh'])<1e-6 for r in rows)
    assert all(float(r['max_battery_residual_kwh'])<1e-6 for r in rows)
    assert all(float(r['bess_same_hour_both_directions'])==0 for r in rows)
    assert all(float(r['fuel_end_l'])>=-1e-7 for r in rows)
    assert all(0<=float(r['critical_EA_fraction'])<=1.000000001 for r in rows)
    assert all(int(r['completed_h'])==int(r['requested_h']) for r in rows)
    for duration in (24,72,168):
        indexes={int(r['start_hour']) for r in rows if int(r['requested_h'])==duration}
        assert indexes=={168*i for i in range(52)}

def test_summary_math_against_raw():
    raw=csvrows(HERE/'outputs/weekly_52_starts_full.csv')
    summ=csvrows(HERE/'outputs/weekly_52_starts_summary.csv')
    assert len(summ)==27
    for s in summ:
        subset=[r for r in raw if int(r['requested_h'])==int(s['duration_h'])
                and int(float(r['pv_kw']))==int(s['pv_kw'])
                and int(float(r['bess_kwh']))==int(s['bess_kwh'])]
        assert len(subset)==52
        assert float(s['total_ENS_mean_kwh_per_window'])==pytest.approx(
            sum(float(r['total_ENS_kwh']) for r in subset)/52,abs=1e-7)
        assert int(s['critical_shortfall_window_count'])==sum(float(r['critical_ENS_kwh'])>1e-7 for r in subset)
        assert float(s['critical_EA_worst_percent'])==pytest.approx(min(100*float(r['critical_EA_fraction']) for r in subset),abs=1e-7)

def test_external_profiles_are_8760_and_input_hashes_match():
    d=HERE/'external_inputs';r=csvrows(d/'LC1_reference_profiles_8760.csv')
    assert len(r)==len(PV_PU)==len(WIND_PU)==8760
    assert all(int(x['hour_index_zero_based'])==i for i,x in enumerate(r))
    assert float(r[0]['pv_pu_from_original_2025'])==pytest.approx(PV_PU[0])
    assert float(r[-1]['wind_pu_from_original_2025'])==pytest.approx(WIND_PU[-1])
    for x in (r[0],r[8760-1]):
        assert float(x['central_total_kw'])==pytest.approx(sum(float(x[f'central_{y}_kw']) for y in ('critical','aux','ev_planned')),abs=1e-6)
    prov=json.loads((d/'LC1_external_input_provenance.json').read_text(encoding='utf-8'))
    assert sha256(d/prov['input_profile_file'])==prov['input_profile_sha256']
    assert sha256(d/prov['case_manifest_file'])==prov['case_manifest_sha256']
    assert sha256(d/prov['fuel_curve_file'])==prov['fuel_curve_sha256']
    assert 'NOT_FIXED_025' in csvrows(d/'LC1_108_external_case_manifest.csv')[0]['diesel_fuel_model']
    cases=csvrows(d/'LC1_108_external_case_manifest.csv')
    assert len(cases)==108 and len({r['case_id'] for r in cases})==108

def test_untouched_external_native_template_has_no_results():
    template=csvrows(HERE/'external_inputs/external_native_results_template.csv')
    assert template==[]
    with pytest.raises(ValueError):
        validate_metadata(HERE/'external_inputs/external_native_metadata_template.json',
                          HERE/'external_inputs/external_native_results_template.csv')

def test_external_comparator_can_identify_disagreement():
    expected={k:'1.0' for k in METRICS}
    native={k:'1.0' for k in METRICS}
    native['total_ENS_kwh']='2.0'
    result=compare_numeric(expected,native)
    assert len(result)==len(METRICS)
    assert sum(r['status']=='NUMERIC_DISAGREEMENT' for r in result)==1
    assert next(r for r in result if r['metric']=='total_ENS_kwh')['status']=='NUMERIC_DISAGREEMENT'

def test_metadata_explicitly_zero_new_native_runs():
    meta=json.loads((HERE/'outputs/weekly_52_starts_metadata.json').read_text())
    assert meta['case_count']==1404 and meta['valid_count']==1404
    assert meta['native_MDT_runs_new']==meta['HOMER_runs_new']==0
    assert meta['max_bess_bidirectional_count']==0
