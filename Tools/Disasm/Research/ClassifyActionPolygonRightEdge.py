"""Выделение правого обновления с явно обозначенным последовательным общим хвостом."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main
import ActionPolygonRightEdgeFacts as facts


if __name__=='__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionPolygonEdgesVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==97090
    selected=dict(proof,total_cases=sum(v for k,v in proof['paths'].items() if k.startswith('right')),
                  complete_source_report='Tools/Disasm/Reports/ActionPolygonEdgesVerification.json')
    selected['paths']={k:v for k,v in proof['paths'].items() if k.startswith('right')}
    (ROOT/'Tools/Disasm/Reports/ActionPolygonRightEdgeVerification.json').write_bytes((json.dumps(selected,indent=2)+'\n').encode('utf-8'))
    main(facts,'ActionPolygonRightEdge',0xD3AD,0xD4C1,48545,allow_subrange=True)
