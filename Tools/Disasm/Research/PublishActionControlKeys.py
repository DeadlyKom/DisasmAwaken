"""Шесть отдельно проверяемых публикаций оригинальных клавиатурных входов без массового экспорта."""
import json
from importlib import import_module
from ClassifyControlsTextDisplay import ROOT
from ActionControlKeyLayout import ENTRIES
from PublishActionRawFunction import main as publish


if __name__=='__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionControlKeysVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==393216
    for start,name,tag,*_ in ENTRIES:
        report=dict(proof,total_cases=proof['cases_by_entry'][tag],parent_total_cases=proof['total_cases'],entry=start)
        assert report['total_cases']==65536
        report_path=ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json')
        assert not report_path.exists()
        report_path.write_text(json.dumps(report,indent=2)+'\n','utf-8')
        path=ROOT/('Docs/'+tag+'.md');assert not path.exists()
        path.write_text('# Клавиатурный вход '+name+'\n\n['+name+'](../Source/Action/'+name+'.asm)\n\n'
            '[Общий алгоритм, границы и проверка](ActionControlKeys.md).\n\n'
            '[Отчёт 65536 сценариев](../Tools/Disasm/Reports/'+tag+'Verification.json).\n','utf-8')
        publish(import_module(tag+'Facts'),tag,start,start+35,65536,allow_subrange=True)
