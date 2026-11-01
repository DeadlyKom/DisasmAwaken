"""Обработчик статуса, настоящий вызов геометрии по Z и сохранённый AF вокруг непрямого рисунка."""
import re
FUNCTIONS={0x7F17:('HandleStatusPanelAction','Геометрия по входному Z, перенос статусного элемента и условный рисунок с восстановлением AF')}
RENAMES={'HandleItem00':'HandleStatusPanelAction'}
LABELS={('Station',0x7F1A):'ApplyAction'}
LABEL_RENAMES={'HandleStatusPanelAction.Point7F1A':'HandleStatusPanelAction.ApplyAction'}
DOCUMENTS={('Station',0x7F17):('StatusPanelAction','входной Z, ранний Carry, два физических кадра и возвращение AF после рисунка')}
CONTRACTS={('Station',0x7F17):(
 ['HL запасной рисователь, DE индекс статусного элемента, штатно 0, BC контекст выбранных помощников',
  'AF входа задаёт Z разрешения TrackItemGeometry и Carry раннего выхода, Z не вычисляется из A собственным кодом',
  'IX, FlagsCache и ввод удовлетворяют TrackItemGeometry при Z=1, станционный код выбран',
  'действуют договоры CloseActiveItem, MoveItemToTail и SuspendPointer, активный callback возвращается с допустимым стеком',
  'найденный либо запасной рисователь возвращается обычным RET, сохраняет доступность ResumeActionPointer и RestoreActionAF',
  'стек вмещает FActionReturnFrame и FActionDrawFrame, указатель и экраны удовлетворяют выбранному рисователю и ResumePointer'],
 ['при исходном Z=1 выполнен TrackItemGeometry, при Z=0 вызов пропущен, A не является собственной проверкой этого решения',
  'при Carry после выбранной геометрии либо исходном Carry на пути без неё немедленно возвращён текущий контекст',
  'иначе текущий AF сохраняется в FActionReturnFrame.SavedAF до закрытия активного элемента и переноса выбранного',
  'если MoveItemToTail вернул Z=1, HL найденный либо последний рисователь, DE исходный индекс, BC по активному callback, AF восстановлен из SavedAF',
  'если Z=0, указатель снят, создан DrawReturn=ResumeActionPointer и выполнен JP в фактический найденный рисователь',
  'рисователь получает FActionDrawFrame с DrawReturn, SavedAF и внешним ReturnAddress, DE перед JP заменён на 7F30',
  'после RET рисователя выполняются ResumePointer, POP AF и внешний RET, восстановлен AF после выбранной геометрии',
  'HL, DE, BC, альтернативные и индексные пары на рисующем пути принадлежат фактическому рисователю и общим помощникам',
  'I, IFF и IM сохраняются собственным кодом, внешние callback и IRQ обязаны удовлетворять оговорённым договорам, SP после возврата входному+2'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по выбранным помощникам и callback, список, геометрия, экран и рабочие данные рисунка"],
 ['сохранённый AF снимается ровно один раз в общем RestoreActionAF, промежуточные статусы рисователя не становятся результатом действия',
  'перенос ищет по индексу и сохраняет существующий C9-алиас, его адрес не подменяется запасным HL',
  'MoveItemToTail переносит физические 128 байтов даже для последней записи, Z=1 означает отсутствие следующих указателей после переноса',
  'внутренний ApplyAction=Entry+3 имеет тот же договор, JP префикса нового CPU-кадра не создаёт',
  'модель проверяет настоящий статусный рисунок и пустой активный callback, произвольные внешние callback ограничены их собственными договорами'])}
COMMENTS={0x7F17:(['переход к общему действию статусной панели без создания CPU-кадра'],None),
 0x7F1A:(['проверка входного Z для самостоятельной ветви интерактивной геометрии'],'вызов, если входной Z установлен, выполнить TrackItemGeometry независимо от значения A'),
 0x7F1D:([],'выход, если текущий Carry установлен, сохранить результат геометрии либо исходного контекста'),
 0x7F1E:(['создание SavedAF кадра FActionReturnFrame после возможной геометрии'],None),
 0x7F1F:(['закрытие прежнего активного элемента, его callback не заменяет сохранённый AF'],None),
 0x7F22:(['поиск статусного индекса и перенос существующего рисователя в конец списка'],None),
 0x7F25:([],'переход, если выбранный рисователь уже последний, восстановить SavedAF без рисунка'),
 0x7F28:(['удаление указателя перед обновлением bitmap'],None),0x7F2B:(['выбор синтетического возврата через возобновление указателя'],None),
 0x7F2E:(['создание DrawReturn перед SavedAF и внешним ReturnAddress'],None),0x7F2F:(['вызов фактического рисователя через подготовленный стек, его RET вернёт в ResumeActionPointer'],None)}
TARGETS={0x7F1A:'Station.HandleStatusPanelAction.ApplyAction',0xC87C:'Station.TrackItemGeometry.Entry',0x9E77:'Station.CloseActiveItem.Entry',0xBE38:'Station.MoveItemToTail.Entry',
 0x7F33:'Station.RestoreActionAF.Entry',0x63C3:'Station.SuspendPointer.Entry',0x7F30:'Station.ResumeActionPointer.Entry'}


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
