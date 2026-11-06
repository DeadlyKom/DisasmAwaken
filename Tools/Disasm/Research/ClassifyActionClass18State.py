"""Публикация точного переходного действия F075."""
import json
from ClassifyActionRegionType import ROOT, main
import ActionClass18StateFacts as facts


if __name__ == '__main__':
    reports = ROOT/'Tools/Disasm/Reports'
    dispatch = json.loads((reports/'ActionObjectStateDispatchVerification.json').read_text(encoding='utf-8'))
    assert dispatch['passed'] and dispatch['stopped_after_indirect_JP']
    proof = dict(passed=True, total_cases=dispatch['cases_by_entry']['F075'],
                 shared_report='Tools/Disasm/Reports/ActionObjectStateDispatchVerification.json')
    (reports/'ActionClass18StateVerification.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    main(facts, 'ActionClass18State', 'ActionObjectStateDispatch', ())
