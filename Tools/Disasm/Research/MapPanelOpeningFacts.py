"""Сохранённая геометрия одиннадцати исходных панелей группы карты."""
import re
FUNCTIONS={0x7AC4:('OpenMapPanelGroup','Подготовка группы из одиннадцати панелей карты с восстановлением геометрии и запросом обновления')}
RENAMES={'Unknown7AC4':'OpenMapPanelGroup'}
LABELS={}
DOCUMENTS={('Station',0x7AC4):('MapPanelOpening','фиксированный порядок одиннадцати ключей, алиасы и полные физические хвосты')}
CONTRACTS={('Station',0x7AC4):(
 ['BC сохраняемый контекст, входные HL, DE и AF отдельного параметра не задают',
  'индексы в одиннадцати исходных рисователях подготовлены, их FInterfaceItem и Saved-поля доступны',
  'список ограничен исходным маркером, хвосты сдвига 128 байтов доступны, действуют договоры RestoreItemBounds',
  'банк станции 0 выбран, операнд RefreshPending доступен, обычный CPU-возврат доступен'],
 ['RefreshPending=1, последовательно восстановлены и перенесены ключи 21, 18, 19, 12, 13, 14, 15, 17, 16, 11, 20',
  'HL содержит выбранный существующий либо исходный последний рисователь, DE равен ключу DrawVariantPanel, штатно 20',
  'BC сохранён, AF содержит A=SavedHeight последней записи, F=A4',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
  'X, Y, Width и Height выбранных записей восстановлены из Saved-полей, прочие поля сохранены',
  'EventEnabled=0, список с физическим хвостом изменён, bitmap и активная страница сохранены'],
 ['HL, DE, AF, RefreshPending, первые четыре поля выбранных FInterfaceItem, список и EventEnabled'],
 ['RestoreItemBounds принимает адрес рисователя, его изменяемое слово задаёт ключ, вход не является прямым индексом',
  'при алиасе ключа сохраняется первый существующий адрес, исходный либо чужой C9 не включается автоматически',
  'каждое найденное удаление сдвигает ровно 128 байтов, хвост за ограничителем является частью результата',
  'это подготовка списка, немедленного рисования, банкового вызова и включения рисователей здесь нет',
  'запрос позднее читает UpdateVariantPanel, его отложенный путь отдельно проверяет ActiveItemState.Active'])}
POINTERS=((0x7B51,'DrawFlightButton'),(0x7CF8,'DrawContractButton'),(0x768F,'DrawSystemInfoPanel'),(0x7BA8,'DrawStoredPointToggle'),
 (0x7C1E,'DrawSecondaryPointToggle'),(0x7C7E,'DrawItem14'),(0x7CB6,'DrawItem15'),(0x7D24,'DrawItem17'),
 (0x7D53,'DrawItem16'),(0x6DA8,'DrawMapPanel'),(0x788C,'DrawVariantPanel'))
TARGETS={0x78D7:'VariantPanelState.RefreshPending',0xCBA9:'Station.RestoreItemBounds.Entry',**{a:'Station.'+name+'.Entry' for a,name in POINTERS}}
COMMENTS={0x7AC4:(['установка запроса позднего обновления панели вариантов до восстановления группы'],None)}
for j,(_,name) in enumerate(POINTERS):COMMENTS[0x7AC9+6*j]=(['подготовка сохранённой геометрии '+name+', позиция '+str(j+1)+' из 11'],None)
COMMENTS[0x7B08]=(['восстановление последней панели с возвратом сразу вызывающей стороне'],None)
MODIFIED_WRITES=((0x7AC6,0x78D7,'Station',0x78D6,1,5),)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
