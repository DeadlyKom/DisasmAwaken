"""Публикация общих растровых фаз по совокупности ранее выполненных моделей, без новой сборки."""
import json
import ControlsCircleKernelsFacts as facts
from ClassifyControlsTextDisplay import ROOT,main

if __name__=='__main__':
    stems=('ControlsCircleHalf','ControlsClippedCircleHalf','ControlsCircleInteriorFull','ControlsPushSpans')
    proofs=[json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'Verification.json')).read_text('utf-8')) for stem in stems]
    assert all(p['passed'] and not p['assembly_executed'] for p in proofs)
    assert proofs[0]['all_valid_x_y_pairs_both_directions']
    assert proofs[1]['original_EXX_active_exit_preserved']
    assert proofs[3]['all_three_original_copies'] and proofs[3]['real_row_helpers_without_stubs']
    report=dict(passed=True,method='aggregation_of_actual_original_byte_execution_reports',
        total_cases=sum(p['total_cases'] for p in proofs),reports=['Tools/Disasm/Reports/'+stem+'Verification.json' for stem in stems],
        entry_states_restricted_to_documented_initializers=True,arbitrary_internal_entry_states_exhausted=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleKernelsVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    main(facts,'ControlsCircleKernels','ControlsCircleKernels',state_fields=facts.STATE_FIELDS)
