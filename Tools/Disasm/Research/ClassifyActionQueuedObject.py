"""Снятие Unknown после проверки стыков всей цепочки и обеих ветвей рисования."""
import json
from ClassifyActionRegionType import main
from ClassifyControlsTextDisplay import ROOT
import ActionQueuedObjectFacts as facts


if __name__=='__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionRenderContinuationCompositionVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==1920 and all(proof['paths'].get(path,0) for path in ('inside','clipped','projection_reject','common_outside'))
    (ROOT/'Tools/Disasm/Reports/ActionQueuedObjectVerification.json').write_bytes((json.dumps(proof,indent=2)+'\n').encode('utf-8'))
    main(facts,'ActionQueuedObject','ActionQueuedObject',())
