"""Два списка пяти позиций, отдельные рисователи без дискового действия."""
import re
FUNCTIONS={0x7492:('DrawSaveSlotPanel','Рамка и пять строк выбора позиции записи, без выполнения дискового протокола'),
 0x751B:('DrawLoadSlotPanel','Рамка и пять строк выбора позиции чтения, без выполнения дискового протокола')}
RENAMES={'DrawItem43':'DrawSaveSlotPanel','DrawItem44':'DrawLoadSlotPanel'}
LABELS={}
DOCUMENTS={('Station',a):('SaveSlots','пять физических строк, сброс наведения и отделение рисунка от дискового действия') for a in FUNCTIONS}
CONTRACTS={}
for address,index,operand,hover,text,end in ((0x7492,43,'SaveIndex','ToPositionRow','SaveOptions','DE8F'),(0x751B,44,'LoadIndex','FromPositionRow','LoadOptions','DECB')):
 CONTRACTS['Station',address]=(
  ['активный LD HL содержит SaveSlotState.'+operand+', штатно '+str(index)+', либо первый байт заменён на C9',
   'при активном коде действуют договоры DrawCaptionItem и PrintText, шрифт и таблицы подготовлены, банк станции 0 выбран',
   'FInterfaceItem имеет допустимую геометрию, индексная пара доступна, HALT рамки получает корректный IRQ с сохранением контекста'],
  ['при активном коде зарегистрированы рамка и заголовок, PanelHoverState.'+hover+'=FF, Style=0',
   'из SaveSlotText.'+text+' печатаются пять исходных CR-строк с видимыми номерами 1..5, последняя завершается LF',
   'HL содержит продолжение PrintText, DE и BC сохранены, AF статус текста, при полном выводе HL='+end+', AF=0A4A',
   "HL', DE', BC' сохранены, AF' определяется DrawCaptionItem, IX, IY, I, IFF и IM сохранены при договоре IRQ",
   'обычный RET даёт SP входному+2, страницы 10 и 18 сохраняют экранный бит, никакой DOS-вызов здесь не исполняется',
   'при временном C9 сохранены все регистры, флаги, память и страницы, строка наведения не сбрасывается'],
  ["HL, AF, AF', bitmap, текстовое окно, курсор, операнды рисования и байт прежней строки при активном коде"],
  ['исходный хвостовой JP PrintText использует внешний CPU-возврат без нового CALL',
   'пять видимых подписей не заменяют байтовую формулу имени в обработчике действия, возврат наведения зависит от фактического попадания',
   'модель сверяет весь bitmap тела независимым текстовым и глифовым алгоритмом, bitmap рамки проверяется отдельным договором'])
COMMENTS={0x7492:(['чтение изменяемого индекса панели позиций записи'],None),0x7498:(['обновление строки наведения в FF после нового фона'],None),
 0x749D:(['запрет автоматического переноса коротких строк выбора'],None),0x74A1:(['чтение пяти CR-строк В позицию 1..5 для хвостовой печати'],None),
 0x751B:(['чтение изменяемого индекса панели позиций чтения'],None),0x7521:(['обновление строки наведения в FF после нового фона'],None),
 0x7526:(['запрет автоматического переноса коротких строк выбора'],None),0x752A:(['чтение пяти CR-строк С позиции 1..5 для хвостовой печати'],None)}
TARGETS={0xC287:'Station.DrawCaptionItem.Entry',0x7489:'PanelHoverState.ToPositionRow',0x7512:'PanelHoverState.FromPositionRow',
 0xBD26:'TextWindow.Style',0xDE53:'SaveSlotText.SaveOptions',0xDE8F:'SaveSlotText.LoadOptions',0xBD08:'Station.PrintText.Entry'}
MODIFIED_WRITES=((0x749A,0x7489,'Station',0x7488,1,5),(0x7523,0x7512,'Station',0x7511,1,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
