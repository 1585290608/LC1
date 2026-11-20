"""Reproducible Stage7 outputs, strictly derived from historical immutable results."""
from __future__ import annotations
import hashlib,csv,json
from pathlib import Path
from week7.stage7 import benchmark,trace_audit,native_handoff,cash_ledger
HERE=Path(__file__).resolve().parent

def run():
    parts={'analytic':benchmark.run(HERE/'outputs'),
           'independent_trace_audit':trace_audit.run(HERE/'outputs'),
           'HOMER_load_handoff':native_handoff.run(HERE/'external_handoff'),
           'economic_replay':cash_ledger.replay(HERE/'outputs')}
    meta={'stage':7,'research_date':'2026-11-19',
          'evidence_class':'INTERNAL_CLOSED_FORM_AND_READONLY_LEDGER_VALIDATION_NO_NATIVE',
          'new_native_MDT_runs':0,'new_HOMER_Pro_runs':0,
          'external_cross_solver_validation_performed':False,
          'previous_software_comparison':'HISTORICAL_DG_ONLY_24H_NOT_HYBRID',
          'original_project_files_modified':False,'results':parts}
    (HERE/'outputs/stage7_run_summary.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    files=[*HERE.glob('outputs/*'),*HERE.glob('external_handoff/*')]
    files=[x for x in files if x.is_file() and x.name!='stage7_output_SHA256.csv']
    with (HERE/'outputs/stage7_output_SHA256.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['relative_file','sha256']);w.writeheader()
        for x in sorted(files):w.writerow({'relative_file':x.relative_to(HERE).as_posix(),
                                             'sha256':hashlib.sha256(x.read_bytes()).hexdigest()})
    return meta
if __name__=='__main__':
    d=run()
    print(json.dumps(d,indent=2))
