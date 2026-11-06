"""Выделение целого левого обновления после точной проверки обеих его границ выхода."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main
import ActionPolygonLeftEdgeFacts as facts


if __name__=='__main__':
    path=ROOT/'Tools/Disasm/Reports/ActionPolygonEdgesVerification.json'
    proof=json.loads(path.read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==97090 and proof['whole_left_update_to_row_cycle_or_common_selector']
    selected=dict(proof,total_cases=sum(v for k,v in proof['paths'].items() if k.startswith('left')),
                  complete_source_report='Tools/Disasm/Reports/ActionPolygonEdgesVerification.json')
    selected['paths']={k:v for k,v in proof['paths'].items() if k.startswith('left')}
    (ROOT/'Tools/Disasm/Reports/ActionPolygonLeftEdgeVerification.json').write_bytes((json.dumps(selected,indent=2)+'\n').encode('utf-8'))
    main(facts,'ActionPolygonLeftEdge',0xD272,0xD3A8,48545,allow_subrange=True)
