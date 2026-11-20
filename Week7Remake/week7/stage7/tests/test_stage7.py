"""Stage 7 independent analytical and reproducibility gates (no native software)."""
from __future__ import annotations
import csv, json,math
from pathlib import Path
import pytest
from week7.stage7.benchmark import REFERENCE,rows,execute_fixture,fixture_input_rows,run as run_bench
from week7.stage7.trace_audit import audit_grid_trace,audit_outage_trace
from week7.stage7.native_handoff import write_homer_inputs,make_template,compare_external,sha256
from week7.stage7.cash_ledger import replay

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parents[1]


def test_all_six_closed_form_fixtures_match_equations():
    result=rows()
    assert len(REFERENCE)==6 and len(result)==22
    assert all(r['status']=='PASS_ANALYTIC' for r in result)


def test_24h_diesel_1h_startup_and_constant_load():
    m=execute_fixture('DG_24H_STARTUP')
    assert m['generated_kwh']==pytest.approx(40*(24-1))
    assert m['fuel_used_l']==pytest.approx(40*23*.25)
    assert m['critical_ENS_kwh']==pytest.approx(40)


def test_diesel_limited_by_fuel_not_by_made_up_runtime():
    m=execute_fixture('DG_24H_FUEL_LIMIT')
    assert m['generated_kwh']==pytest.approx(125/.25)
    assert m['critical_ENS_kwh']==pytest.approx(24*50-125/.25)


def test_priority_bench_critical_and_aux_shortfall():
    m=execute_fixture('PV_WIND_24H_PRIORITY')
    assert m['critical_ENS_kwh']==pytest.approx(18*5)
    assert m['aux_ENS_kwh']==pytest.approx(18*15)
    assert m['curtailed_kwh']==pytest.approx(6*10)


def test_bess_one_hour_round_trip_loss_not_ignored():
    m=execute_fixture('BESS_1H_DISCHARGE')
    assert m['discharged_ac_kwh']==pytest.approx((.7-.3)*100*.9)
    assert m['battery_loss_kwh']==pytest.approx(36/.9-36)
    n=execute_fixture('BESS_1H_RE_CHARGE')
    assert n['end_soc']==pytest.approx(.3+40*.9/100)
    assert n['battery_loss_kwh']==pytest.approx(40*(1-.9))


def test_grid_priority_serve_c4isr_first():
    m=execute_fixture('GRID_1H_PRIORITY')
    assert m['grid_import_kwh']==pytest.approx(30)
    assert m['critical_ENS_kwh']==pytest.approx(0)
    assert m['aux_ENS_kwh']==pytest.approx(20)
    assert m['ev_request_shortfall_kwh']==pytest.approx(10)


def test_saved_grid_traces_independent_reconciliation():
    out=ROOT/'week7/stage6/outputs'
    a=audit_grid_trace(out/'stage6_base_central_100kw_hourly_trace.csv',300,100)
    b=audit_grid_trace(out/'stage6_upper_central_250kw_hourly_trace.csv',450,250)
    assert a['hours']==b['hours']==8760
    assert a['independent_max_ac_residual_kwh']<1e-7
    assert b['independent_max_battery_residual_kwh']<1e-7


def test_outage_trace_with_delivery_does_not_double_count_fuel():
    path=ROOT/'week7/stage4/outputs/W03_PV100_W100_B450_REFUEL_500_H48_H96_H144_hourly_trace.csv'
    result=audit_outage_trace(path)
    assert result['hours']==168 and result['independent_max_fuel_residual_l']<1e-7


def test_homer_annual_single_column_energy_is_correct(tmp_path):
    items=write_homer_inputs(tmp_path)
    assert len(items)==4
    for item in items:
        text=(tmp_path/item['file']).read_text().splitlines()
        assert len(text)==8760
        assert all(len(s.split(','))==1 and float(s)>=0 for s in text)
        assert sum(map(float,text))==pytest.approx(item['annual_energy_kwh'],abs=1e-6)
        assert sha256(tmp_path/item['file'])==item['sha256']
    assert all('NO_DYNAMIC_SOC' in item['model_equivalence'] for item in items)


def test_native_template_contains_no_fabricated_outputs(tmp_path):
    t=make_template(tmp_path)
    assert not t['controller_and_component_parameters_equivalent']
    assert t['software']==''
    with (tmp_path/'USER_FILL_native_component_results_template.csv').open() as f:
        rs=list(csv.DictReader(f))
    assert len(rs)==22 and all(r['external_value']=='' for r in rs)


def test_native_comparison_rejects_unattested_input(tmp_path):
    t=make_template(tmp_path)
    native=tmp_path/'USER_FILL_native_component_results_template.csv'
    md=tmp_path/'metadata.json';md.write_text(json.dumps(t))
    with pytest.raises(ValueError):compare_external(native,md,tmp_path/'comp')


def test_native_comparison_rejects_forged_hash_even_with_self_attestation(tmp_path):
    t=make_template(tmp_path)
    native=tmp_path/'USER_FILL_native_component_results_template.csv'
    t.update(software='HOMER Pro',software_version='UNTESTED',native_project_filename='hypothetical',
             native_export_original_path='unverified',controller_and_component_parameters_equivalent=True,
             units_and_timebase_checked=True,native_results_sha256='BADHASH')
    md=tmp_path/'metadata.json';md.write_text(json.dumps(t))
    with pytest.raises(ValueError,match='hash'):compare_external(native,md,tmp_path/'comp')


def test_cash_ledger_replays_only_service_matched_cases(tmp_path):
    info=replay(tmp_path)
    assert info['cases']==27 and info['ledger_year_rows']==27*21
    assert info['max_absolute_20y_PV_difference_gbp']<1e-6
    with (tmp_path/'stage7_selected_costs_year_by_year_567.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert all(float(r['outage_fuel_and_logistics_gbp_EXCLUDED'])==0 for r in rows)
    assert all(float(r['ENS_shadow_price_gbp_EXCLUDED'])==0 for r in rows)


def test_readonly_archival_files_are_not_replaced_in_stage7():
    assert (ROOT/'week7/audit/baseline_sha256.csv').exists()
    assert (ROOT/'week7/stage6/outputs/stage6_81_annual_grid_cases.csv').exists()
    assert (ROOT/'week7/stage5/outputs/stage5_conditional_economic_comparison.csv').exists()


def test_vendor_neutral_fixture_rows_match_six_benchmarks():
    rs=fixture_input_rows()
    assert len(rs)==75
    assert {x['case_id'] for x in rs}==set(REFERENCE)
    pv=[x for x in rs if x['case_id']=='PV_WIND_24H_PRIORITY']
    assert len(pv)==24 and sum(r['pv_available_kw'] for r in pv)==180
    assert all(r['wind_available_kw']==15 for r in pv)
    dg=[x for x in rs if x['case_id']=='DG_24H_STARTUP']
    assert len(dg)==24 and all(x['DG_start_delay_h']==1 for x in dg)
