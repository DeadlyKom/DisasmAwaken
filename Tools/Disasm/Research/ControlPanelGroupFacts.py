"""Продажа текущей строки и открытие исходных групп интерфейса без немедленного рисования."""
from DrawAdapterFacts import CONTRACTS as DRAW_CONTRACTS
from StoredPointControlFacts import CONTRACTS as CONTROL_CONTRACTS
FUNCTIONS={
 0x7DF1:('OpenShipPanels','Сброс выбора и восстановление шести корабельных панелей в исходном порядке'),
 0x7DE7:('HandleShipControl','Подготовка отложенного callback открытия корабельных панелей'),
 0x7E19:('DrawShipControl','Рисование управляющего элемента корабля через изменяемый индекс 7'),
 0x7E1F:('ResetShipPanelSelection','Сброс режима списка, рамок выбора и первого компонента индекса банка 4'),
 0x7D63:('SellCurrentCargo','Продажа текущей строки груза событием 11 с принудительным выбором строки 0 после перерисовки'),
 0x7D77:('DrawSellControl','Рисование управляющего элемента продажи через изменяемый индекс 35'),
 0x7D87:('OpenContractPanels','Восстановление границ и порядка панелей контракта 31, 33, 32'),
 0x7DA9:('OpenTradePanels','Восстановление границ управляющего элемента продажи и товарной панели'),
 0x7DC5:('OpenEquipmentPanels','Сброс индекса текста оснащения и восстановление панелей 39, 36, 37, 38'),
 0x7D59:('HandleSellControl','Подготовка отложенного callback продажи текущей строки'),
 0x7D7D:('HandleContractsControl','Подготовка отложенного callback открытия панелей контракта'),
 0x7D9F:('HandleTradeControl','Подготовка отложенного callback открытия товарных панелей'),
 0x7DBB:('HandleEquipmentControl','Подготовка отложенного callback открытия панелей оснащения')}
TARGETS={0x7DE7:(0x7DF1,'OpenShipPanels'),0x7D59:(0x7D63,'SellCurrentCargo'),0x7D7D:(0x7D87,'OpenContractPanels'),0x7D9F:(0x7DA9,'OpenTradePanels'),0x7DBB:(0x7DC5,'OpenEquipmentPanels')}
GROUPS={0x7DF1:((0x7A15,0x7A82,0x7A55,0x67E0,0x6945,0x6877),'30, 29, 28, 25, 27, 26'),0x7D87:((0x6FC5,0xAA4F,0xAA85),'31, 33, 32'),0x7DA9:((0x7D77,0x7071),'35, 34'),0x7DC5:((0x6AB6,0x7B40,0x7B25,0x7227),'39, 36, 37, 38')}
DOCUMENTS={('Station',a):('ControlPanelGroups','продажа выбранного груза, отложенные callback и порядок групп панелей') for a in FUNCTIONS}
LABELS={('Station',a+3):'Action' for a in TARGETS}
LABELS['Station',0x7D76]='Finish'
CONTRACTS={('Station',a):DRAW_CONTRACTS['Station',a] for a in (0x7D77,0x7E19)}
COMMENTS={}
for a,(_,target) in TARGETS.items():
 base=CONTROL_CONTRACTS['Station',0x7B57]
 CONTRACTS['Station',a]=tuple([s.replace('ToggleStoredMapPoint',target).replace('операция списка','действие callback') for s in part] for part in base)
 COMMENTS[a]=(['передача с внешней трёхбайтовой обёртки во вход Action'],None)
 COMMENTS[a+3]=(['сохранение адреса '+target+' через общий обработчик, прямого вызова действия здесь нет'],None)
CONTRACTS['Station',0x7D63]=(
 ['ScriptSelection.CargoRow содержит индекс текущего товара либо FF, после него расположен исходный байт CD',
  'на активной строке действуют договоры RunTradeEventAndRedraw и исходного торгового сценария события 11'],
 ['при CargoRow=FF HL равен слову из адреса CargoRow, в исходном коде CDFF, DE и BC сохранены, AF=FF6A',
  'при активной строке событие TradeEvent.SellCurrent выполняется до конца общего обновления, затем CargoRow=0 и A=0',
  'F активного пути остаётся от RunTradeEventAndRedraw, остальные регистры принадлежат его договору',
  'на пропуске все альтернативные и индексные регистры сохранены, SP обычного возврата равен входному SP+2'],
 ['на активном пути HL, DE, BC, AF и рабочие регистры вызываемого сценария и перерисовки'],
 ['исходный LD HL читает два байта, проверяется только L, соседний CD не является частью индекса',
  'продаётся текущий вид груза, перебора всех товаров здесь нет',
  'после успеха, штрафа или отказа сценария строка всё равно становится нулевой',
  'поле ограничения продажи проверяет исходный сценарий, этот callback самостоятельно флаговые биты не фильтрует'])
COMMENTS.update({0x7D63:(['чтение исходного слова с номером строки в L и соседним кодом инструкции в H'],None),
 0x7D68:(['проверка отсутствия выбранной строки'],None),
 0x7D69:([], 'переход, если CargoRow равен FF, продажу и перерисовку пропустить'),
 0x7D6C:(['выбор события продажи всего количества текущего вида груза'],None),
 0x7D71:(['установка строки 0 независимо от результата сценария после общего обновления'],None),
 0x7D77:(['чтение изменяемого индекса управляющего элемента продажи, C9 отключает этот вход'],None)})
for a,(targets,order) in GROUPS.items():
 CONTRACTS['Station',a]=(
  ['каждый исходный рисователь содержит актуальный индекс по адресу Entry+1, список и FInterfaceItem допустимы по договору RestoreItemBounds',
   'имеется место в списке рисования, сохранённые поля геометрии подготовлены'],
  ['границы восстановлены последовательно для элементов '+order+', EventEnabled каждого обработанного элемента равен нулю',
   'HL - сохранённый в списке рисователь последнего ключа либо переданный исходный адрес при отсутствии ключа',
   'DE - индекс последнего рисователя, BC сохранён, AF - A последняя SavedHeight, F=A4',
   'все альтернативные и индексные регистры сохранены, SP обычного возврата равен входному SP+2',
   ('EquipmentInfoState.TextIndex сброшен в ноль перед обработкой панелей' if a==0x7DC5 else 'параметры текстовых выборок этим входом не меняются')],
  ['HL, DE, AF'],
  ['каждый RestoreItemBounds переносит первое совпадение индекса в конец списка, существующий адрес-алиас сохраняется',
   'немедленного рисования нет, C9 отключённого рисователя не заменяется на 21, индекс по Entry+1 читается и при C9',
   'последний RestoreItemBounds вызван хвостовым JP, его RET использует исходный адрес возврата'])
 offset=4 if a in (0x7DC5,0x7DF1) else 0
 if a==0x7DC5:COMMENTS[a]=(['сброс индекса LF-текста описания оснащения перед открытием группы'],None)
 for i,target in enumerate(targets):COMMENTS[a+offset+6*i]=(['восстановление следующей панели в исходной последовательности '+order],None)

CONTRACTS['Station',0x7E1F]=(
 ['AF - A сохраняемый селектор корабельных панелей, рабочие индексы DrawItemState.Index28 и Index29 допустимы',
  'тень CurrentPage и аппаратный порт согласованы, bit5 снят, CPU-стек вне сменяемого окна'],
 ['HL - адрес FInterfaceItem.Flags элемента Index28, DE и BC сохранены',
  'AF - A=(прежняя CurrentPage AND F8) OR 10, F от логического OR итоговой страницы',
  'ShipPanelState.Selector получает входной A, PendingRedraw=1, OwnedMode=0, PanelHoverState.ShipsRow=FF',
  'бит InterfaceFlags.FrameBit у Index29 установлен, затем у Index28 сброшен, прочие биты сохранены',
  'байт E146 именно банка 4 равен нулю, итоговый банк 0 с сохранёнными старшими управляющими разрядами',
  'альтернативные и индексные регистры, I и IFF сохранены, SP обычного возврата равен входному SP+2'],
 ['HL, AF'],
 ['при одинаковых индексах последующий RES выигрывает, итоговый бит 0 сброшен',
  'Selector не нормализуется до 0 или 1, все входные байты записываются без проверки',
  'PendingRedraw является операндом периодического входа 68EA, ненулевое значение выбирает обновление через 68CC',
  'OwnedMode выбирает источник списка, ноль использует таблицу доступности системы, ненулевое значение использует текущие индексы 9849 или 984A',
  'назначение всех категорий Selector и полного алгоритма банка 4 этим договором не объявляется установленным',
  'вызов не рисует экран, прежний номер банка не восстанавливается'])
COMMENTS.update({0x7E1F:(['сохранение полного селектора списка без нормализации'],None),
 0x7E22:(['запрос отложенного обновления периодическим входом 68EA'],None),
 0x7E27:(['отмена прежней полосы наведения списка кораблей'],None),
 0x7E2C:(['выбор доступного в системе списка вместо текущего владения'],None),
 0x7E30:(['расчёт адреса флагов управляющего элемента 29 для установки формы рамки'],None),
 0x7E3A:(['расчёт адреса флагов управляющего элемента 28 для сброса формы рамки'],None),
 0x7E44:(['выбор банка 4 для сброса его первого компонента индекса'],None),
 0x7E4D:(['возврат в банк станционного кода с сохранением старших разрядов страницы'],None)})

ship=list(CONTRACTS['Station',0x7DF1])
ship[0]=['условия ResetShipPanelSelection, актуальные индексы рисователей и сохранённые границы всех шести панелей',*ship[0]]
ship[1]=[line for line in ship[1] if 'параметры текстовых выборок' not in line]+['перед восстановлением выполнен ResetShipPanelSelection с A=0, его изменения режима, рамок и банка 4 сохранены']
ship[3]=[*ship[3],'ResetShipPanelSelection вызывается до обхода списка, режим и рамки меняются даже у отключённых рисователей']
CONTRACTS['Station',0x7DF1]=tuple(ship)
COMMENTS[0x7DF1]=(['выбор селектора 0 и сброс корабельного списка до восстановления границ'],None)
COMMENTS[0x7E19]=(['чтение изменяемого индекса управляющего элемента корабля, C9 отключает этот вход'],None)

def name_operands(region,address,operation):
 if region!='Station':return operation
 for value,name in ((0x6906,'Selector'),(0x68EB,'PendingRedraw'),(0x79DD,'OwnedMode')):
  operation=operation.replace('(#'+format(value,'04X')+')','(@ShipPanelState.'+name+')')
 operation=operation.replace('(#6ACC)','(@EquipmentInfoState.TextIndex)')
 if address==0x7E1F:
  operation=operation.replace('(#7A83)','(@DrawItemState.Index29)').replace('(#7A56)','(@DrawItemState.Index28)').replace('LD A, #04','LD A, @FInterfaceItem.Flags').replace('SET 0, (HL)','SET @InterfaceFlags.FrameBit, (HL)').replace('RES 0, (HL)','RES @InterfaceFlags.FrameBit, (HL)')
 if address in TARGETS:
  value,name=TARGETS[address]
  operation=operation.replace('LD HL, #'+format(value,'04X'),'LD HL, @Station.'+name+'.Entry')
 if address==0x7D63:operation=operation.replace('LD A, #0B','LD A, @TradeEvent.SellCurrent')
 if address in GROUPS:
  operation=operation.replace('CALL #CBA9','CALL @Station.RestoreItemBounds.Entry').replace('JP #CBA9','JP @Station.RestoreItemBounds.Entry')
  from Knowledge import FUNCTIONS as KNOWN
  for value in GROUPS[address][0]:
   fallback={0x6FC5:'DrawItem31',0xAA4F:'DrawItem33',0xAA85:'DrawItem32',0x6AB6:'DrawItem39',0x7B40:'DrawItem36',0x7B25:'DrawItem37',0x7227:'DrawItem38',0x7A15:'DrawItem30',0x7A82:'DrawItem29',0x7A55:'DrawItem28',0x67E0:'DrawItem25',0x6945:'DrawItem27',0x6877:'DrawItem26'}
   name=KNOWN['Station'][value][0] if value in KNOWN['Station'] else fallback[value]
   operation=operation.replace('LD HL, #'+format(value,'04X'),'LD HL, @Station.'+name+'.Entry')
 return operation
