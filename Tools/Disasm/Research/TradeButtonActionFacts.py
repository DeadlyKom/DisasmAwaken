"""Кнопки режимов, активация и последовательное исполнение четырёх существующих продолжений."""
import re
import ModelTradeModeFacts as MODEL
import EquipmentTradeModeFacts as EQUIPMENT
ENTRIES=((0x7A1B,'HandleShipSaleButton','HandleItem28',0x7A1E,0x7A24,'SelectSaleMode',28),
 (0x7A5B,'HandleShipPurchaseButton','HandleItem29',0x7A5E,0x7A64,'SelectPurchaseMode',29),
 (0x7B11,'HandleEquipmentPurchaseButton','HandleItem37',0x7B14,0x7B1A,'SelectEquipmentPurchase',37),
 (0x7B2B,'HandleEquipmentSaleButton','HandleItem36',0x7B2E,0x7B34,'SelectEquipmentSale',36))
IN_PLACE={target for _,_,_,_,target,_,_ in ENTRIES}
FUNCTIONS={a:(name,'Установка callback и последовательный вход в '+callee+' после общего действия кнопки') for a,name,_,_,_,callee,_ in ENTRIES}
for module in (MODEL,EQUIPMENT):FUNCTIONS.update({a:description for a,description in module.FUNCTIONS.items() if a in IN_PLACE})
RENAMES={old:name for _,name,old,_,_,_,_ in ENTRIES}
LABELS=dict(MODEL.LABELS)
LABELS.update({('Station',internal):'BindAndSelect' for _,_,_,internal,_,_,_ in ENTRIES})
LABEL_RENAMES={name+'.Point'+format(internal,'04X'):name+'.BindAndSelect' for _,name,_,internal,_,_,_ in ENTRIES}
CONTINUATIONS={a:target for a,_,_,_,target,_,_ in ENTRIES}
CONTINUATION_SCOPES={a:'activate_callback_then_immediate_mode_continuation' for a in CONTINUATIONS}
DOCUMENTS={('Station',a):('TradeButtonActions','установка цели и немедленное продолжение, Carry события и жёсткий порядок include') for a,_,_,_,_,_,_ in ENTRIES}
for module in (MODEL,EQUIPMENT):DOCUMENTS.update({key:value for key,value in module.DOCUMENTS.items() if key[1] in IN_PLACE})
CONTRACTS={};COMMENTS={};TARGETS={0xCC21:'Station.ActivateInterfaceCallback.Entry'}
for module in (MODEL,EQUIPMENT):
 CONTRACTS.update({key:tuple(list(part) for part in value) for key,value in module.CONTRACTS.items() if key[1] in IN_PLACE})
 COMMENTS.update(module.COMMENTS)
for a,name,_,internal,target,callee,key in ENTRIES:
 CONTRACTS['Station',a]=(
  ['HL входа не параметр, DE индекс новой кнопки, штатно '+str(key)+', BC сохраняемый контекст, AF полный селектор',
   'выбранная кнопка уже присутствует в списке, IX и FlagsCache подготовлены по договору ActivateInterfaceCallback',
   'действует договор '+callee+', индекс второй кнопки и её физическая FInterfaceItem доступны',
   'станционный банк выбран, для корабельного режима доступен D3D 4, геометрия и IRQ удовлетворяют общим помощникам'],
  ['NextCallback всегда получает Station.'+callee+'.Entry до проверки селектора общего действия',
   'выполнен ActivateInterfaceCallback, при ненулевом A активный Callback установлен в ту же цель по договору ActivateItem',
   'после возврата общего обработчика последовательно исполняется Station.'+callee+'.Entry без JP или нового CALL',
   'при Carry общего обработчика продолжение сразу возвращается, режим и контуры им не меняются',
   'для ненулевого селектора Carry берётся из InterfaceState.EventCode.bit7, новая цель ещё не вызывалась механизмом callback',
   'при нулевом селекторе общий путь геометрии возвращает Carry=1, следующее продолжение режима не действует',
   'при разрешённом продолжении его полный договор определяет режим, контуры, bitmap и регистры, повторной активации нет',
   'HL, DE, BC, AF, альтернативные и индексные пары соответствуют общему действию и фактически исполненному продолжению',
   'IY, I, IFF и IM сохранены при договорах помощников и IRQ, SP после конечного возврата входному+2'],
  ["HL, DE, AF, L', AF', IX по геометрии, callback, список, режим, контуры и экран по разрешённому продолжению"],
  ['include установщика (0) и '+callee+'.asm (1) обязаны идти подряд, собственной инструкции перехода между ними нет',
   'адрес продолжения одновременно сохранён как отложенная цель, это не отменяет его немедленное последовательное исполнение',
   'исходный JP BindAndSelect не создаёт нового CPU-кадра, внутренний вход имеет тот же договор',
   'модель сравнивает все селекторы с композицией настоящих помощников и независимо проверяет режим и callback',
   'проверка полного bitmap отсутствует, путь немедленного продолжения не является доказательством нативной игры'])
 COMMENTS[a]=(['переход к установке цели и последующему выбору режима без нового CPU-кадра'],None)
 COMMENTS[internal]=(['выбор адреса '+callee+' как следующего callback'],None)
 COMMENTS[internal+3]=(['активация кнопки, её выходной Carry проверит физически следующее продолжение режима'],None)
 TARGETS[internal]='Station.'+name+'.BindAndSelect';TARGETS[target]='Station.'+callee+'.Entry'
MODIFIED_WRITES=MODEL.MODIFIED_WRITES+EQUIPMENT.MODIFIED_WRITES


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 if address in IN_PLACE:
  return EQUIPMENT.name_operands(region,address,MODEL.name_operands(region,address,operation))
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
