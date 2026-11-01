"""Кнопки продажи/покупки, собственный тип и межбанковый сброс строки просмотра."""
import re
FUNCTIONS={0x7A24:('SelectSaleMode','Выбор продажи собственного корабля либо скимера с возвратом к покупке при типе FF'),
 0x7A55:('DrawSaleModeButton','Центрируемая кнопка продажи с изменяемым индексом FInterfaceItem 28'),
 0x7A64:('SelectPurchaseMode','Выбор каталога покупки, сброс строки просмотра и переключение контура кнопок'),
 0x7A82:('DrawPurchaseModeButton','Центрируемая кнопка покупки с изменяемым индексом FInterfaceItem 29')}
RENAMES={'Unknown7A24':'SelectSaleMode','DrawItem28':'DrawSaleModeButton','Unknown7A64':'SelectPurchaseMode','DrawItem29':'DrawPurchaseModeButton'}
LABELS={('Station',0x7A44):'CheckOwnedType',('Station',0x7A78):'ApplyMode'}
LABEL_RENAMES={'SelectSaleMode.Point7A44':'SelectSaleMode.CheckOwnedType','SelectPurchaseMode.Point7A78':'SelectPurchaseMode.ApplyMode'}
DOCUMENTS={('Station',a):('ModelTradeMode','исходные кнопки продажи и покупки, FF собственного типа, банк 4 и общий вход') for a in FUNCTIONS}
CONTRACTS={}
for address,sale in ((0x7A24,True),(0x7A64,False)):
 CONTRACTS['Station',address]=(
  ['DE содержит индекс выбранной новой кнопки, штатно '+('28' if sale else '29')+', HL входа отдельного параметра не задаёт',
   'BC сохраняемый контекст, AF содержит Carry запрета действия, при Carry=1 других условий не требуется',
   'при Carry=0 банк станции 0 выбран, CurrentPage=10 либо 18, реальные переключения банка не заблокированы',
   'D3D загружен в банк 4, RowOperand доступен, обе записи кнопок удовлетворяют SwitchItemContour и DrawCenteredItem',
   'Selector и текущие собственные типы доступны, допустимость последующего 3D-показа обеспечивает вызывающий код'],
  ['при входном Carry=1 сохранены все регистры, флаги, память, страницы и порты, SP после RET входному+2',
   'при Carry=0 RowOperand банка 4=0, PendingRedraw=1, банк возвращён в 0 с сохранением экранного бита',
   'HL и DE содержат индекс новой кнопки, BC сохранён, AF содержит A=C3 и F последнего текстового прохода SwitchItemContour',
   "H', DE', BC', IX, IY, I, IFF и IM сохранены, L' и AF' рабочие по SwitchItemContour",
   'у старой кнопки сброшен только Flags.bit0, у новой установлен, обе рамки перерисованы, UpdateBlocked=0',
   'SP обычного возврата входному+2, собственного немедленного 3D-кадра нет, запрос обслужит последующий периодический проход'],
  ["HL, DE, AF, L', AF', RowOperand банка 4, PendingRedraw, OwnedMode, Flags двух кнопок, bitmap, курсор и карта владельцев"],
  ['OwnedMode является целым режимом, здесь записываются только 0 покупки либо 1 продажи, независимые флаговые биты не вводятся',
   'SelectRamBank объединяет весь аргумент со старшими битами тени, страницы 10/18 переходят в 14/1C и обратно',
   'договоры указателя и центрируемых элементов сохраняются, модель не объявляет независимый oracle всего итогового bitmap'])
CONTRACTS['Station',0x7A24][1].insert(2,'Selector=0 читает CurrentModels.ShipIndex, любое ненулевое значение читает SkimmerIndex, FF принудительно выбирает покупку')
CONTRACTS['Station',0x7A24][1].insert(3,'при типе не FF OwnedMode=1, старый индекс берётся из DrawItemState.Index29, новый из входного DE, при FF старый Index28 и новый Index29')
CONTRACTS['Station',0x7A64][1].insert(2,'OwnedMode=0, старый индекс всегда DrawItemState.Index28, новый индекс равен входному DE')
CONTRACTS['Station',0x7A64][3].extend(['ApplyMode по 7A78 принимает DE новой кнопки, обходит RET C, не сбрасывает RowOperand и PendingRedraw',
 'в ApplyMode HL заменяется Index28, OwnedMode=0 и выполняется тот же SwitchItemContour, этот хвост использует SelectSaleMode при собственном FF'])
for address,index,name in ((0x7A55,28,'продажи'),(0x7A82,29,'покупки')):
 CONTRACTS['Station',address]=(
  ['активный Entry содержит LD HL с подготовленным DrawItemState.Index'+str(index)+', либо временный C9',
   'при активном коде запись FInterfaceItem и шрифт удовлетворяют DrawCenteredItem, индекс штатно '+str(index)],
  ['при активном коде HL содержит загруженный индекс, DE и BC сохранены, AF содержит A=C3 и F последнего текста DrawCenteredItem',
   "H', DE', BC', IX, IY, I, IFF и IM сохранены, L' и AF' рабочие по центрируемому рисователю",
   'зарегистрированы рамка и bitmap кнопки '+name+', окно и курсор согласно DrawCenteredItem, отдельного кадра CALL нет',
   'при временном C9 сохранены все регистры, флаги и память, SP после обычного RET входному+2'],
  ["HL, AF, L', AF', bitmap, окно, курсор и карта владельцев при активном коде"],
  ['исходная подпись взята из CenterTextBase E4AA, её нельзя отождествлять с CaptionTextBase E399',
   'рисователь не выбирает режим, отдельный вход действия кнопки меняет режим и подготовку просмотра'])
COMMENTS={
 0x7A24:(['проверка Carry общего обработчика кнопки до любых изменений режима'],'выход, если входной Carry установлен, действие запрещено'),
 0x7A25:(['выбор реального банка 4 перед сбросом существующего операнда номера модели'],None),
 0x7A2A:(['обновление строки будущего просмотра нулём, это байт кода D3D банка 4'],None),
 0x7A2E:(['возврат банка станции 0 с сохранением бита экранной страницы'],None),
 0x7A33:(['установка отложенного запроса, 3D-кадр здесь не исполняется'],None),
 0x7A38:(['проверка полного селектора, ноль относится к собственному кораблю, прочие байты к скимеру'],None),
 0x7A3F:([],'переход, если Selector равен нулю, проверить прочитанный ShipIndex'),
 0x7A41:(['чтение собственного скимера для любого ненулевого Selector'],None),
 0x7A44:(['проверка FF собственного типа через исходный байтовый INC'],None),
 0x7A45:(['сохранение входного нового индекса и чтение ключа кнопки покупки'],None),
 0x7A4A:([],'переход, если собственный тип равен FF, выбрать покупку через общий хвост'),
 0x7A4C:(['обновление полного байта режима, единица выбирает продажу собственного объекта'],None),
 0x7A51:(['подготовка старой кнопки покупки и входного нового индекса продажи'],None),
 0x7A55:(['чтение изменяемого индекса кнопки Продажа перед хвостовым рисованием'],None),
 0x7A64:([],'выход, если входной Carry установлен, действие запрещено'),
 0x7A65:(['выбор банка 4 для сброса будущей строки просмотра'],None),
 0x7A6A:(['обновление только RowOperand, остальные байты D3D не меняются'],None),
 0x7A6E:(['возврат банка станции с сохранённым экранным битом'],None),
 0x7A73:(['установка запроса периодического обновления'],None),
 0x7A78:(['ApplyMode обходит защиту Carry и сброс строки, ноль выбирает каталог покупки'],None),
 0x7A7C:(['чтение старого индекса кнопки продажи, DE новой кнопки передаётся без изменения'],None),
 0x7A82:(['чтение изменяемого индекса кнопки Покупка перед хвостовым рисованием'],None)}
TARGETS={0x6396:'Station.SelectRamBank.Entry',0xE146:'D3DPreviewState.RowOperand',0x68EB:'ShipPanelState.PendingRedraw',0x6906:'ShipPanelState.Selector',
 0x9849:'CurrentModels.ShipIndex',0x984A:'CurrentModels.SkimmerIndex',0x7A44:'Station.SelectSaleMode.CheckOwnedType',0x7A83:'DrawItemState.Index29',
 0x7A78:'Station.SelectPurchaseMode.ApplyMode',0x79DD:'ShipPanelState.OwnedMode',0xA806:'Station.SwitchItemContour.Entry',0x7A56:'DrawItemState.Index28',
 0xC2DF:'Station.DrawCenteredItem.Entry'}
MODIFIED_WRITES=((0x7A2B,0xE146,'D3D',0xE145,1,4),(0x7A35,0x68EB,'Station',0x68EA,1,5),(0x7A4E,0x79DD,'Station',0x79DC,1,5),
 (0x7A6B,0xE146,'D3D',0xE145,1,4),(0x7A75,0x68EB,'Station',0x68EA,1,5),(0x7A79,0x79DD,'Station',0x79DC,1,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation.replace('LD A, #14','LD A, @ShipPreviewConst.PreviewPage').replace('LD A, #10','LD A, @StationIrqConst.StationPage')
