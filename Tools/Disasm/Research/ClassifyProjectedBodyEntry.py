"""Публикация обоих банковых входов по общей композиционной проверке."""
import json
from ClassifyControlsTextDisplay import ROOT, main as publish_controls
from ClassifyActionRegionType import main as publish_action
import ControlsProjectDrawBodyFacts as controls
import ActionDrawBankedBodyFacts as action


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    shared = json.loads((reports / 'ProjectedBodyEntryVerification.json').read_text(encoding='utf-8'))
    assert shared['passed'] and shared['actual_children_without_stubs']
    for tag, address in (('ControlsProjectDrawBody', 'CEFA'), ('ActionDrawBankedBody', '6C7E')):
        report = dict(passed=True, total_cases=shared['cases_by_entry'][address],
                      shared_report='Tools/Disasm/Reports/ProjectedBodyEntryVerification.json', assembly_executed=False)
        (reports / (tag + 'Verification.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    publish_controls(controls, 'ControlsProjectDrawBody', 'ProjectedBodyEntry', state_fields=())
    publish_action(action, 'ActionDrawBankedBody', 'ProjectedBodyEntry', (), include_blocks=(
        ('Includes/Const/Include.inc', 'module ActionBodyPattern', action.CONST_BLOCK),))
