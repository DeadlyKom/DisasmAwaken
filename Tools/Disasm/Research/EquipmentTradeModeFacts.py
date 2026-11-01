"""Два целых режима оборудования и их центрируемые кнопки."""
import re
from ModelTradeModeFacts import CONTRACTS as MODEL_CONTRACTS
FUNCTIONS={0x7B1A:('SelectEquipmentPurchase','Выбор покупки оборудования и переключение контура с продажи на покупку'),
 0x7B25:('DrawEquipmentPurchase','Центрируемая кнопка покупки оборудования с изменяемым индексом 37'),
 0x7B34:('SelectEquipmentSale','Выбор продажи оборудования и переключение контура с покупки на продажу'),
 0x7B40:('DrawEquipmentSale','Центрируемая кнопка продажи оборудования с изменяемым индексом 36')}
RENAMES={'Unknown7B1A':'SelectEquipmentPurchase','DrawItem37':'DrawEquipmentPurchase','Unknown7B34':'SelectEquipmentSale','DrawItem36':'DrawEquipmentSale'}
LABELS={}
DOCUMENTS={('Station',a):('EquipmentTradeMode','целый байт режима, подтверждённые подписи, Carry и реальное переключение контуров') for a in FUNCTIONS}
CONTRACTS={}
for address,mode,old,new in ((0x7B1A,0,36,37),(0x7B34,1,37,36)):
 CONTRACTS['Station',address]=(
  ['DE содержит индекс новой кнопки, штатно '+str(new)+', HL входа отдельного параметра не задаёт',
   'BC сохраняемый контекст, AF содержит Carry запрета действия, при Carry=1 других условий не требуется',
   'при Carry=0 доступен банк станции 0, старый Index'+str(old)+' и новый DE задают допустимые FInterfaceItem',
   'действуют договоры SwitchItemContour, DrawCenteredItem и помощников указателя, стек не перекрывает их данные'],
  ['при Carry=1 сохранены все регистры, флаги, память и порты, SP после RET равен входному+2',
   'при Carry=0 EquipmentTradeState.OwnedMode='+str(mode)+', HL и DE равны входному DE, BC сохранён',
   'у старой кнопки Index'+str(old)+' сброшен только Flags.bit0, у новой этот бит установлен, обе рамки перерисованы',
   "AF содержит A=C3 и F последнего текста, H', DE', BC', IX, IY, I, IFF и IM сохранены, L' и AF' рабочие",
   'указатель возобновлён, UpdateBlocked=0, страница не меняется, SP обычного возврата равен входному+2'],
  ["HL, DE, AF, L', AF', OwnedMode, Flags двух записей, bitmap, текстовое окно, курсор и карта владельцев"],
  ['OwnedMode является целым режимом, 0 выбирает покупку, 1 продажу, независимые биты не вводятся',
   'сама смена режима не выполняет сделку, отдельный потребитель по 71EB выбирает EventCode 5 при нуле либо 6 при ненулевом байте',
   'полный потребитель HandleEquipmentListAction и исходные события 5 и 6 проверены отдельно, сама смена режима сценарий не запускает',
   'при равных индексах общая процедура рисует запись дважды, итоговый Flags.bit0 установлен, проверки равенства здесь нет'])
for address,model,index in ((0x7B25,0x7A82,37),(0x7B40,0x7A55,36)):
 CONTRACTS['Station',address]=tuple([line.replace('Index29','Index37').replace('Index28','Index36').replace('штатно 29','штатно 37').replace('штатно 28','штатно 36') for line in part] for part in MODEL_CONTRACTS['Station',model])
 CONTRACTS['Station',address][3][-1]='рисователь не выбирает режим, отдельный вход действия кнопки меняет только байт режима'
COMMENTS={0x7B1A:(['проверка Carry общего действия до изменения режима оборудования'],'выход, если входной Carry установлен, действие запрещено'),
 0x7B1B:(['обновление целого режима оборудования, ноль выбирает покупку'],None),
 0x7B1F:(['чтение прежней кнопки продажи, DE новой кнопки покупки сохраняется'],None),
 0x7B25:(['чтение изменяемого индекса центрируемой кнопки покупки оборудования'],None),
 0x7B34:(['проверка Carry общего действия до изменения режима оборудования'],'выход, если входной Carry установлен, действие запрещено'),
 0x7B35:(['обновление целого режима оборудования, единица выбирает продажу'],None),
 0x7B3A:(['чтение прежней кнопки покупки, DE новой кнопки продажи сохраняется'],None),
 0x7B40:(['чтение изменяемого индекса центрируемой кнопки продажи оборудования'],None)}
TARGETS={0x71EC:'EquipmentTradeState.OwnedMode',0x7B26:'DrawItemState.Index37',0x7B41:'DrawItemState.Index36',
 0xA806:'Station.SwitchItemContour.Entry',0xC2DF:'Station.DrawCenteredItem.Entry'}
MODIFIED_WRITES=((0x7B1C,0x71EC,'Station',0x71EB,1,5),(0x7B37,0x71EC,'Station',0x71EB,1,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
