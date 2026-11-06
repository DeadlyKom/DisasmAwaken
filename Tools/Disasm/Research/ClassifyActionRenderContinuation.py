"""Выделение прямого продолжения из бинарных байтов с сохранением статуса Unknown."""
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from PublishActionRawFunction import main
from InspectZ80 import decoder
import ActionRenderContinuationFacts as facts


if __name__ == '__main__':
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    records = decoder(flat_action()).disassemble(0xE4DB, 0xE4FF, 'h')
    assert b''.join(i.bytes for i in records) == source[0x84DB:0x84FF]
    proof = dict(passed=True, total_cases=0, method='static_original_instruction_boundaries_only',
                 instructions=len(records), code_bytes=36, whole_procedure_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderContinuationVerification.json').write_bytes((json.dumps(proof, indent=2) + '\n').encode('utf-8'))
    main(facts, 'ActionRenderContinuation', 0xE4DB, 0xE4FF, 0)
