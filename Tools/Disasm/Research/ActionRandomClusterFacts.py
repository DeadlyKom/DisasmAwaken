"""Двенадцать восстановленных входов той же проверенной рекурсии, уже опубликованные имена сохранены."""
import re
from ActionRandomStreamLayout import STREAMS,DIRECT_USE_NOTES
from ActionFoldedRandomFacts import CONTRACTS as PREVIOUS_CONTRACTS

FUNCTIONS={entry:('NextRandomWord'+str(index),'Следующее слово независимого потока '+str(index)+' с физическим состоянием Stream'+str(index))
    for index,entry,_ in STREAMS if index>=3}
CONTRACTS={key:tuple([text.replace('203011','218383').replace('все четыре входа','ядро и все пятнадцать внешних входов')
    .replace('три внешних входа','пятнадцать внешних входов').replace('три исходных состояния','пятнадцать исходных состояний')
    for text in section] for section in contract) for key,contract in PREVIOUS_CONTRACTS.items()}
for index,entry,pointer in STREAMS:
    if index<3:continue
    CONTRACTS['Action',entry]=tuple([text.replace('Stream0','Stream'+str(index)).replace('потока 0','потока '+str(index))
        for text in section] for section in CONTRACTS['Action',0xEB72])
for index,entry,_ in STREAMS:
    CONTRACTS['Action',entry][3][-1]=DIRECT_USE_NOTES[index]+', полный граф, распределение и период результата не доказаны'
COMMENTS={}
for index,entry,pointer in STREAMS:
    if index<3:continue
    COMMENTS[entry]=(['Выбор рабочего альтернативного набора, основное DE и BC вызывающего вернутся после EXX общего ядра.'],None)
    COMMENTS[entry+1]=(['Выбор физического состояния Stream'+str(index)+', другие потоки этим вызовом не обновляются.'],None)


def name_operands(region,address,operation):
    if region!='Action':return operation
    if operation.startswith(('CALL ','JP ','JR ')):
        names={entry:'Action.NextRandomWord'+str(index)+'.Entry' for index,entry,_ in STREAMS}
        names[0xEC08]='Action.StepFoldedRandom.Entry'
        operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+names[int(m[1],16)] if int(m[1],16) in names else m[0],operation)
    if address in FUNCTIONS:
        index,entry,pointer=next(item for item in STREAMS if item[1]==address)
        operation=operation.replace('LD HL, #'+format(pointer,'04X'),'LD HL, @ActionRandomStreams.Stream'+str(index))
    return operation
