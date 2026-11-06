"""Последовательная публикация шести проверенных переходников в пределах одного заполнителя."""
import importlib,json
from ClassifyControlsTextDisplay import ROOT
from CheckActionPolygonBridges import SPECS
from ActionPolygonBridgeFacts import SPECS as DETAILS
from PublishActionRawFunction import main


if __name__=='__main__':
    for tag,start,stop,cases in SPECS:
        end,name,description=DETAILS[tag][1:4]
        document=ROOT/('Docs/'+tag+'.md')
        text=('# '+description+'\n\n['+name+'](../Source/Action/'+name+'.asm) содержит исходные байты '+format(start,'04X')+'..'+format(end-1,'04X')+' банка 0. Полный регистровый договор и условия временного стека приведены в исходнике. Это переходник [линейной заливки](ActionPolygonFill.md), его назначение ограничено переносом индекса либо восстановлением контекста.\n\n'
            '[Проверка](../Tools/Disasm/Research/CheckActionPolygonBridges.py) прошла '+str(cases)+' сценариев, [отчёт](../Tools/Disasm/Reports/'+tag+'Verification.json). Сверены регистры кроме R и отсутствие записей RAM. Для оборачивания левого индекса исчерпаны все байты индекса и флагов, для верхней левой обёртки все альтернативные A и основные F. Расширенные байты локальной проверки не объявляются штатными игровыми индексами. Сборка, IRQ и нативное исполнение не выполнялись.\n')
        assert not document.exists()
        document.write_bytes(text.encode('utf-8'))
        main(importlib.import_module(tag+'Facts'),tag,start,end,cases,allow_subrange=True)
