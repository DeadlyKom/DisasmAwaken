"""Два точечно проверенных клавиатурных входа из исходного бинарного ресурса."""
import json
from importlib import import_module
from ClassifyControlsTextDisplay import ROOT
from ActionGaugeWordKeyFacts import LAYOUT
from PublishActionRawFunction import main as publish


if __name__=='__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionGaugeWordKeysVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==729088
    for start,end,name,tag in LAYOUT:
        report=dict(proof,total_cases=proof['cases_by_entry'][hex(start)],parent_total_cases=proof['total_cases'],entry=start)
        path=ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json');assert not path.exists()
        path.write_text(json.dumps(report,indent=2)+'\n','utf-8')
        path=ROOT/('Docs/'+tag+'.md');assert not path.exists()
        path.write_text('# Клавиатурный вход '+name+'\n\n['+name+'](../Source/Action/'+name+'.asm)\n\n'
            '[Общий алгоритм и точные ограничения](ActionGaugeWordKeys.md).\n\n'
            '[Отчёт проверки](../Tools/Disasm/Reports/'+tag+'Verification.json).\n','utf-8')
        publish(import_module(tag+'Facts'),tag,start,end,report['total_cases'],allow_subrange=True)
