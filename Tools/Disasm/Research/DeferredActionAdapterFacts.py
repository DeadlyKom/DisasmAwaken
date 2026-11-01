"""Установщики callback моделей, справки и нового предложения, без немедленного исполнения цели."""
import re
from InterfaceActionFacts import CONTRACTS as ACTION_CONTRACTS
ENTRIES=((0x79BD,'InstallShipTradeCallback','HandleItem30',0x79C0,0x79C7,'ConfirmShipModelTrade'),
 (0x7A88,'InstallHelpPanelsCallback','HandleItem09',0x7A8B,0x7A92,'OpenHelpPanels'),
 (0xAA33,'InstallMissionOfferCallback','HandleItem33',0xAA36,0xAA3D,'RefreshMissionOfferPanels'))
FUNCTIONS={a:(name,'Установка отложенной цели '+callee+' через общий обработчик активации элемента') for a,name,_,_,_,callee in ENTRIES}
RENAMES={old:name for _,name,old,_,_,_ in ENTRIES}
LABELS={('Station',internal):'BindCallback' for _,_,_,internal,_,_ in ENTRIES}
LABEL_RENAMES={name+'.Point'+format(internal,'04X'):name+'.BindCallback' for _,name,_,internal,_,_ in ENTRIES}
DOCUMENTS={('Station',a):('DeferredActionAdapters','отложенная цель, развилка геометрии и активации, внешний возврат и сохранённый SP IRQ') for a in FUNCTIONS}
CONTRACTS={};COMMENTS={};TARGETS={0xCC21:'Station.ActivateInterfaceCallback.Entry'}
for a,name,_,internal,target,callee in ENTRIES:
 parts=[list(part) for part in ACTION_CONTRACTS['Station',0xCC21]]
 parts[0][0]='HL входа не является параметром, DE индекс выбранного элемента, BC сохраняемый контекст, AF селектор общего действия'
 parts[0].append('выбранный DE-индекс присутствует в списке, устанавливаемая цель Station.'+callee+'.Entry доступна в своём банковом контексте при последующем вызове')
 parts[1][0]='NextCallback всегда получает Station.'+callee+'.Entry до проверки селектора, сама эта цель здесь не исполняется'
 parts[1]=[line.replace('HL=входной callback','HL=Station.'+callee+'.Entry').replace('HL,DE,BC и IX сохранены','HL=Station.'+callee+'.Entry, DE, BC и IX сохранены') for line in parts[1]]
 parts[1].append('после CALL общего обработчика выполняется собственный RET, SP обычного возврата входному+2')
 parts[3].append('Entry сначала делает исходный JP BindCallback, отдельный внутренний вход принимает тот же контекст')
 parts[3].append('новый callback не подменяет немедленную ветвь A=0, она по-прежнему меняет геометрию и возвращает Carry')
 CONTRACTS['Station',a]=tuple(parts)
 COMMENTS[a]=(['переход к собственному установщику callback без создания нового CPU-кадра'],None)
 COMMENTS[internal]=(['выбор отложенной цели '+callee+' вместо входного HL'],None)
 COMMENTS[internal+3]=(['передача цели общему действию, выполнение цели откладывается до внешнего вызова callback'],None)
 TARGETS[internal]='Station.'+name+'.BindCallback';TARGETS[target]='Station.'+callee+'.Entry'


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
