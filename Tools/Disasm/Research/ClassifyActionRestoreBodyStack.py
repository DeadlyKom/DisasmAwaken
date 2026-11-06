"""Замена ровно трёх исходных байтов настоящей инструкцией LD SP,nn."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main
import ActionRestoreBodyStackFacts as facts


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    proof = json.loads((reports / 'ActionPrepareBodyTransformVerification.json').read_text(encoding='utf-8'))
    assert proof['passed'] and proof['restored_SP_at_6AB0'] and proof['no_cpu_stack_writes']
    (reports / 'ActionRestoreBodyStackVerification.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    main(facts, 'ActionRestoreBodyStack', 0x6AAD, 0x6AB0, proof['total_cases'])
