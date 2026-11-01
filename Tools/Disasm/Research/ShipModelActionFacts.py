"""Выбор модели, закрытие пяти связанных панелей и развилки действия списка."""
import re
FUNCTIONS={0x6774:('HandleShipModelAction','Развилка действия списка моделей после перерисовки, выбор строки либо закрытие группы'),
 0x6780:('DropShipDetailPanels','Отключение периодического просмотра и последовательное удаление пяти связанных панелей'),
 0x67A9:('ShipModelChoice','Пустая ветвь действия и отдельное применение выбранной строки с отложенной перерисовкой')}
RENAMES={'Unknown6774':'HandleShipModelAction','Unknown6780':'DropShipDetailPanels','Unknown67A9':'ShipModelChoice'}
LABELS={('Station',0x67AA):'ApplyChoice',('Station',0x67BC):'ReturnBank0'}
LABEL_RENAMES={'ShipModelChoice.Point67AA':'ShipModelChoice.ApplyChoice','ShipModelChoice.Point67BC':'ShipModelChoice.ReturnBank0'}
CONTINUATIONS={0x6774:0x6780}
DOCUMENTS={('Station',a):('ShipModelActions','единица после RepaintAndFlag, строка FF, сброс описания, пять ключей и физический хвост удаления') for a in FUNCTIONS}
CONTRACTS={('Station',0x6774):(
 ['HL запасной рисователь текущего элемента, DE его индекс, BC контекст RepaintAndFlag',
  'AF содержит полный селектор для RepaintAndFlag, IX и состояние указателя удовлетворяют TrackItemGeometry',
  'выполняются договоры перерисовки и закрытия по строке, для выбора доступны параметры ShipModelChoice.ApplyChoice'],
 ['при Carry RepaintAndFlag возвращается его контекст без дальнейших действий',
  'при Carry=0 и его A=1 выполняется ShipModelChoice.ApplyChoice после DEC A, входной A не принимается за номер модели',
  'иначе CloseMenuOnRow сравнивает только символьные Y, при несовпадении возвращается его A и F с Z=0',
  'при совпадении строк текущий элемент удаляется помощником, затем последовательно выполняется DropShipDetailPanels',
  'HL, DE, BC, AF, альтернативные и индексные регистры соответствуют выбранному помощнику, SP после возврата входному+2'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, геометрия, список, экран и параметры по фактически исполненной ветви"],
 ['последний JR NZ оставляет физическое продолжение в следующем файле только при Z=1, порядок двух include жёсткий',
  'единица относится к A, возвращённому RepaintAndFlag, перерисовка с Carry=1 подавляет последующий выбор и закрытие',
  'проверены все селекторы, обе строки, FF и обычный выбор, а также настоящая предварительная перерисовка с IM2 в HALT',
  'интерактивное перетаскивание и произвольные внешние callback имеют собственные договоры, единый полный игровой поток не доказан']),
 ('Station',0x6780):(
 ['HL заменяется адресом EmptyCallback, DE последовательно получает пять изменяемых индексов, BC сохраняется',
  'AF задаёт начальный Carry для пустого списка, список и хвосты доступны по договору DropItemDraw',
  'DrawItemState.Index30, PreviewIndex, ModelDescriptionState.ItemIndex, Index28 и Index29 содержат читаемые слова'],
 ['HL=EmptyCallback.Entry, DE последний прочитанный Index29, BC сохранён',
  'AF=0044 при найденном последнем ключе, иначе A=0,F=42 OR Carry последнего сравнения, пустой список сохраняет Carry',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены",
  'MenuCommandState.PeriodicCall=EmptyCallback.Entry, пять первых совпадений ключей удаляются в исходном порядке',
  'EventEnabled становится нулём при любом найденном ключе, при отсутствии всех ключей сохраняется',
  'bitmap, карта владельцев и геометрия здесь не перерисовываются, SP после возврата входному+2'],
 ['HL, DE, AF, список с физическими хвостами, PeriodicCall и EventEnabled'],
 ['порядок ключей соответствует панелям 30, 26, 27, 28, 29 в штатной конфигурации, сами индексы не зашиты в инструкциях',
  'текущая панель списка 25 этим входом не удаляется, в действии перед ним её условно удаляет CloseMenuOnRow',
  'каждое совпадение переносит ровно 128 байтов и может затронуть данные после ограничителя',
  'равные ключи выполняют несколько последовательных удалений, временный C9 чужого адреса не мешает сравнению индекса']),
 ('Station',0x67A9):(
 ['Entry не принимает параметров и сразу возвращается, ApplyChoice является отдельным входом по 67AA',
  'HL, DE, BC исходный контекст экранного обновления ApplyChoice, AF в нём не является параметром',
  'PanelHoverState.ShipsRow содержит полный байт строки, код и слова описания доступны для записи',
  'выполняются договоры BeginScreenUpdate, EndScreenUpdate, указателя и переключения банка без аппаратной блокировки'],
 ['Entry сохраняет все регистры, флаги и память, SP после RET равен входному+2',
  'ApplyChoice возвращает HL=0, DE и BC сохранены, AF=010C',
  "HL', DE', BC', IX и IY ApplyChoice сохранены, AF' зависит от ResumePointer, I и IFF сохраняются",
  'при ShipsRow!=FF в банк 4 записан байт RowOperand, при FF прежний байт сохранён',
  'всё слово ModelDescriptionState.TopRow обнулено даже при FF, PendingRedraw=1',
  'CurrentPage=10, выбран банк станции 0 и базовый экран, UpdateBlocked=0, SP после RET входному+2'],
 ["HL, AF, AF' по указателю, RowOperand банка 4 при непустой строке, TopRow, PendingRedraw, состояние экранного обновления"],
  ['номер строки не ограничивается числом моделей, FF только запрещает конкретную запись, допустимость других значений обеспечивает вызывающий код',
   'BeginScreenUpdate и EndScreenUpdate выполняются даже при FF, периодический callback здесь не меняется',
   'модель не рисуется немедленно, ненулевой PendingRedraw обслуживается последующим AnimateShipPreview',
   'проверены все строки и два прежних байта модели, обе страницы, полное слово сброса и точная последовательность OUT'])}
COMMENTS={
 0x6774:(['выполнение общего действия перерисовки до решения о выборе строки и закрытии'],None),
 0x6777:([],'выход, если RepaintAndFlag вернул Carry=1, дальнейшее действие подавлено'),
 0x6778:(['проверка единицы именно в A, возвращённом RepaintAndFlag'],None),
 0x6779:([],'переход, если возвращённый A был равен 1, применить выбранную строку'),
 0x677B:(['условное удаление текущей панели при совпадении символьных строк указателя и текстового начала'],None),
 0x677E:([],'переход, если строки не совпали, вернуть управление без удаления связанных панелей'),
 0x6780:(['отключение будущего периодического просмотра до удаления панелей'],None),
 0x6786:(['чтение и удаление первого ключа группы, в штатной таблице панель 30'],None),
 0x678D:(['чтение и удаление ключа корабельного просмотра'],None),
 0x6794:(['чтение и удаление ключа описания модели'],None),
 0x679B:(['чтение и удаление ключа панели 28'],None),
 0x67A2:(['чтение последнего ключа панели 29 перед хвостовым DropItemDraw'],None),
 0x67A9:(['пустая ветвь действия, применение выбранной строки начинается отдельно в ApplyChoice'],None),
 0x67AA:(['сохранение базового экрана в банке 7 и начало скрытого обновления состояния выбора'],None),
 0x67AD:(['выбор банка 4 перед изменением операнда номера модели'],None),
 0x67B2:(['чтение выбранной строки и проверка числового маркера отсутствия FF'],None),
 0x67B7:([],'переход, если строка равна FF, сохранить прежний номер модели'),
 0x67B9:(['запись строки в существующий операнд LD A по E146 именно банка 4'],None),
 0x67BC:(['возврат окна RAM в банк станции 0 при сохранённом скрытом экране'],None),
 0x67C1:(['обнуление всего 16-битного начала описания независимо от наличия выбранной строки'],None),
 0x67C7:(['возобновление указателя и возврат видимого базового экрана'],None),
 0x67CA:(['установка отложенного запроса, новый кадр здесь не рисуется'],None)}
TARGETS={0xCBEB:'Station.RepaintAndFlag.Entry',0x67AA:'Station.ShipModelChoice.ApplyChoice',0xC85E:'Station.CloseMenuOnRow.Entry',0x67A9:'Station.ShipModelChoice.Entry',
 0x9A58:'Station.EmptyCallback.Entry',0x9A89:'MenuCommandState.PeriodicCall',0x7A16:'DrawItemState.Index30',0x6878:'ShipPanelState.PreviewIndex',0xC873:'Station.DropItemDraw.Entry',
 0x6946:'ModelDescriptionState.ItemIndex',0x7A56:'DrawItemState.Index28',0x7A83:'DrawItemState.Index29',0xA49F:'Station.BeginScreenUpdate.Entry',
 0x6396:'Station.SelectRamBank.Entry',0x67D7:'PanelHoverState.ShipsRow',0x67BC:'Station.ShipModelChoice.ReturnBank0',0xE146:'D3DPreviewState.RowOperand',
 0x6933:'ModelDescriptionState.TopRow',0xA496:'Station.EndScreenUpdate.Entry',0x68EB:'ShipPanelState.PendingRedraw'}
MODIFIED_WRITES=((0x6783,0x9A89,'Station',0x9A88,2,2),(0x67B9,0xE146,'D3D',0xE145,1,4),(0x67C4,0x6933,'Station',0x6932,2,5),(0x67CC,0x68EB,'Station',0x68EA,1,5))


def name_operands(region,address,operation):
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 if region!='Station' or address not in FUNCTIONS:return operation
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation.replace('LD A, #14','LD A, @ShipPreviewConst.PreviewPage').replace('LD A, #10','LD A, @StationIrqConst.StationPage').replace('CP #FF','CP @TradePanelConst.NoRow')
