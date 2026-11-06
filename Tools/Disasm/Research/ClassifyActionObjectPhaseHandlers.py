"""Извлечение трёх доказанных диапазонов перед общим F0F8."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main
import ActionObjectOffsetRiseFacts as rise
import ActionObjectOffsetFallFacts as fall
import ActionObjectPhaseWaitFacts as wait


if __name__ == '__main__':
    reports = ROOT/'Tools/Disasm/Reports'
    proof = json.loads((reports/'ActionObjectPhaseHandlersVerification.json').read_text(encoding='utf-8'))
    assert proof['passed'] and proof['stops_before_shared_F0F8']
    for facts, tag, start, end in ((rise, 'ActionObjectOffsetRise', 0xEF7D, 0xEF9A),
                                   (fall, 'ActionObjectOffsetFall', 0xEF9A, 0xEFB5),
                                   (wait, 'ActionObjectPhaseWait', 0xEFB5, 0xF003)):
        count = proof['cases_by_entry'][f'{start:04X}']
        classification = reports/(tag+'Classification.json')
        if classification.exists():
            previous = json.loads(classification.read_text(encoding='utf-8'))
            assert previous['passed'] and previous['confirmed_code_bytes'] == end-start
            continue
        result = dict(passed=True, total_cases=count, shared_report='Tools/Disasm/Reports/ActionObjectPhaseHandlersVerification.json')
        (reports/(tag+'Verification.json')).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        main(facts, tag, start, end, count, allow_subrange=True)
