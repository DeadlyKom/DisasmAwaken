"""Два установщика открытия панелей через существующий механизм завершающего callback."""
import re
from DeferredActionAdapterFacts import CONTRACTS as ADAPTER_CONTRACTS
ENTRIES=((0x7AA4,'InstallGalaxyNewsCallback','HandleItem02',0x7AA7,0x7AAE,'OpenGalaxyNewsPanel'),
 (0x7ABA,'InstallMapPanelsCallback','HandleItem03',0x7ABD,0x7AC4,'OpenMapPanelGroup'))
FUNCTIONS={a:(name,'Установка отложенного открытия через '+target) for a,name,_,_,_,target in ENTRIES}
RENAMES={old:name for _,name,old,_,_,_ in ENTRIES}
LABELS={('Station',internal):'BindCallback' for _,_,_,internal,_,_ in ENTRIES}
LABEL_RENAMES={name+'.Point'+format(internal,'04X'):name+'.BindCallback' for _,name,_,internal,_,_ in ENTRIES}
DOCUMENTS={('Station',a):('DeferredActionAdapters','исходная цель открытия, геометрический путь и отложенный вызов') for a in FUNCTIONS}
CONTRACTS={};COMMENTS={};TARGETS={0xCC21:'Station.ActivateInterfaceCallback.Entry'}
for a,name,_,internal,target,callee in ENTRIES:
 CONTRACTS['Station',a]=tuple([line.replace('ConfirmShipModelTrade',callee) for line in part] for part in ADAPTER_CONTRACTS['Station',0x79BD])
 COMMENTS[a]=(['переход к установщику открытия через '+callee+' без нового CPU-кадра'],None)
 COMMENTS[internal]=(['выбор отложенной цели '+callee+' вместо входного HL'],None)
 COMMENTS[internal+3]=(['сохранение цели и общая развилка геометрии либо активации, открытие здесь не исполняется'],None)
 TARGETS[internal]='Station.'+name+'.BindCallback';TARGETS[target]='Station.'+callee+'.Entry'


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
