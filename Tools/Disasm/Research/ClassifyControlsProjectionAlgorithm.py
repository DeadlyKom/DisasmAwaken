"""Точечная публикация проекции после двух независимых числовых проверок."""
from pathlib import Path
import json
import ControlsProjectionAlgorithmFacts as facts
from ClassifyControlsTextDisplay import main

if __name__=='__main__':
    root=Path(__file__).resolve().parents[3]
    for name,count in (('ControlsBodyProjection',74592),('ControlsProjectionRatio',369151)):
        proof=json.loads((root/f'Tools/Disasm/Reports/{name}Verification.json').read_text('utf-8'))
        assert proof['passed'] and proof['total_cases']==count
        assert proof['exact_registers_except_R'] and not proof['assembly_executed']
    proof=json.loads((root/'Tools/Disasm/Reports/ControlsBodyProjectionVerification.json').read_text('utf-8'))
    proof['ratio_verification']='ControlsProjectionRatioVerification.json'
    (root/'Tools/Disasm/Reports/ControlsProjectionAlgorithmVerification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
    main(facts,'ControlsProjectionAlgorithm','ControlsBodyProjection',state_fields=())
