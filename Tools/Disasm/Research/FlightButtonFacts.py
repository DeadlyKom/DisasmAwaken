"""Элемент 21 с исходной подписью Перелет, его установщик и фактически пустой callback."""
import re
from DeferredActionAdapterFacts import CONTRACTS as ADAPTER_CONTRACTS
from DrawAdapterFacts import CONTRACTS as DRAW_CONTRACTS
FUNCTIONS={0x7B46:('InstallFlightButtonCallback','Установка пустого callback кнопки с исходной подписью Перелет'),
 0x7B50:('EmptyFlightCallback','Пустой RET callback элемента 21, установленный обработчиком кнопки Перелет'),
 0x7B51:('DrawFlightButton','Центрируемая кнопка Перелет, исходный текст 40 и изменяемый индекс элемента 21')}
RENAMES={'HandleItem21':'InstallFlightButtonCallback','Unknown7B50':'EmptyFlightCallback','DrawItem21':'DrawFlightButton'}
LABELS={('Station',0x7B49):'BindCallback'}
LABEL_RENAMES={'InstallFlightButtonCallback.Point7B49':'InstallFlightButtonCallback.BindCallback'}
DOCUMENTS={('Station',a):('FlightButton','доказанная надпись, явная установка адреса, пустой RET и косвенный вызов при закрытии') for a in FUNCTIONS}
CONTRACTS={('Station',0x7B46):tuple([line.replace('ConfirmShipModelTrade','EmptyFlightCallback') for line in part] for part in ADAPTER_CONTRACTS['Station',0x79BD]),
 ('Station',0x7B51):tuple(list(part) for part in DRAW_CONTRACTS['Station',0x7B51]),
 ('Station',0x7B50):(
 ['HL, DE, BC, AF, альтернативные и индексные пары произвольны и сохраняются',
  'CPU-стек содержит читаемый адрес возврата, исходный байт C9 доступен в банке 5 по 7B50'],
 ['HL, DE, BC, AF, альтернативные пары, IX, IY, I, IFF и IM сохранены',
  'SP увеличен на два, PC взят из прежней вершины стека, память и порты не меняются',
  'при штатном вызове CloseActiveItem входной AF=0044 сохраняется до завершающих инструкций вызывающего'],
 ['только SP и PC по обычному RET, R увеличивается при выборке инструкции'],
 ['адрес установлен явным LD HL,7B50 в BindCallback по 7B49 и передан ActivateInterfaceCallback',
  'таблица FInterfaceItem связывает установщик с элементом 21 и TextIndex=40, физический текст Перелет',
  'факт пустого callback установлен по единственному байту и реальному косвенному вызову, алгоритма перелёта здесь нет',
  'эта процедура не обнуляет регистры, не заменяет общий механизм закрытия и не доказывает отсутствие иных механизмов перелёта в игре'])}
CONTRACTS['Station',0x7B46][3].append('текстовая роль элемента установлена по исходному TextIndex 40 и LF-записи Перелет, а не по номеру кнопки')
CONTRACTS['Station',0x7B51][3].append('исходный FInterfaceItem.TextIndex=40 выбирает физическую подпись Перелет, целевой callback этого элемента содержит только RET')
COMMENTS={0x7B46:(['переход к установке пустого callback кнопки Перелет'],None),
 0x7B49:(['выбор исходного RET по 7B50 как новой цели callback'],None),
 0x7B4C:(['сохранение цели и обычная развилка геометрии либо активации, сам callback не исполняется'],None),
 0x7B50:(['возврат без изменения AF и остальных пар, в этом callback нет алгоритма перелёта'],None),
 0x7B51:(['чтение изменяемого индекса кнопки Перелет, исходный загрузчик пишет 21'],None)}
TARGETS={0x7B49:'Station.InstallFlightButtonCallback.BindCallback',0x7B50:'Station.EmptyFlightCallback.Entry',0xCC21:'Station.ActivateInterfaceCallback.Entry',0xC2DF:'Station.DrawCenteredItem.Entry'}


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
