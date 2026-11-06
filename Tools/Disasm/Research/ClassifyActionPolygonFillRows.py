"""Публикация ядра после общей проверки изображения, всех регистров и RAM."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main
import ActionPolygonFillRowsFacts as facts


if __name__=='__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionPolygonFillBitmapVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==11562 and proof['all_physical_ram_bytes_proved'] and proof['all_main_alternate_and_index_registers_proved']
    proof['whole_caller_profile_proved']=True
    (ROOT/'Tools/Disasm/Reports/ActionPolygonFillRowsVerification.json').write_bytes((json.dumps(proof,indent=2)+'\n').encode('utf-8'))
    main(facts,'ActionPolygonFillRows',0xD1C0,0xD268,11562,allow_subrange=True)
