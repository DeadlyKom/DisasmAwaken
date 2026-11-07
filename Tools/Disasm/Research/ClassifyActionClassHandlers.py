"""Защищённая публикация восьми подтверждённых обработчиков в порядке зависимостей."""
import importlib
import json
from CheckIntro import ROOT
from ActionAdditionalClassFacts import ENTRIES
from PublishActionRawFunction import main


if __name__=='__main__':
    for kind in (2,5,8,7,6,1,4,3):
        tag=f'ActionClass{kind}Link'
        proof=json.loads((ROOT/f'Tools/Disasm/Reports/{tag}Verification.json').read_text('utf-8'))
        facts=importlib.import_module(tag+'Facts')
        main(facts,tag,*ENTRIES[kind],proof['total_cases'],allow_subrange=True)
