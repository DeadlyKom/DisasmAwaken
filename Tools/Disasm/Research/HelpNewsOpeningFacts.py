"""Подготовка сохранённой геометрии справки и панели галактических новостей."""
FUNCTIONS={0x7A92:('OpenHelpPanels','Перенос текстовой панели и списка справки в конец рисования с восстановлением их сохранённой геометрии'),
 0x7AAE:('OpenGalaxyNewsPanel','Перенос панели галактических новостей в конец рисования и восстановление сохранённой геометрии')}
RENAMES={'Unknown7A92':'OpenHelpPanels','Unknown7AAE':'OpenGalaxyNewsPanel'}
LABELS={}
DOCUMENTS={('Station',a):('HelpNewsOpening','два порядка восстановления, точный физический хвост, алиасы ключа и отсутствие немедленного рисования') for a in FUNCTIONS}
CONTRACTS={}
for address,last,sequence in ((0x7A92,22,'DrawHelpText, затем DrawHelpContents'),(0x7AAE,24,'DrawDecodedMessagePanel')):
 CONTRACTS['Station',address]=(
  ['BC сохраняемый контекст, входные HL, DE и AF отдельного параметра не задают',
   'индексы в исходных обёртках '+sequence+' подготовлены, их FInterfaceItem и SavedX/Y/Width/Height доступны',
   'список имеет исходный ограничитель и доступный хвост фиксированного сдвига, выполняется договор RestoreItemBounds',
   'банк станции 0 выбран и тень страницы согласована, обычный CPU-возврат доступен'],
  ['последовательно выполнены RestoreItemBounds для '+sequence,
   'HL содержит выбранный существующий либо исходный последний рисователь, DE равен ключу последней исходной обёртки, штатно '+str(last),
   'BC сохранён, AF содержит A=SavedHeight последней записи, F=A4',
   "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
   'X, Y, Width и Height каждой выбранной записи восстановлены из SavedX, SavedY, SavedWidth и SavedHeight, прочие поля сохранены',
   'EventEnabled=0, выбранные ключи перенесены в конец списка, bitmap, активная страница и номер LF-записи HELP не меняются'],
  ['HL, DE, AF, первые четыре поля выбранных FInterfaceItem, список с физическим хвостом, EventEnabled'],
  ['при совпадении ключа сохраняется первый существующий адрес, чужой алиас и временный C9 не мешают поиску',
   'каждый MoveItemToTail копирует ровно 128 байтов, включая хвост за ограничителем, этот эффект не заменяется логической перестановкой',
   'последний вызов оформлен хвостовым JP, здесь нет перерисовки, включения C9 или изменения содержимого панели'])
COMMENTS={0x7A92:(['подготовка текстовой панели справки первой в группе'],None),0x7A95:(['восстановление сохранённой геометрии и перенос первого ключа'],None),
 0x7A98:(['подготовка списка разделов последним в группе'],None),0x7A9B:(['восстановление списка с возвратом непосредственно вызывающей стороне'],None),
 0x7AAE:(['подготовка панели галактических новостей, текущий источник сообщения сохраняется'],None),
 0x7AB1:(['восстановление геометрии и перенос ключа без немедленного рисования'],None)}
TARGETS={0x69A8:'Station.DrawHelpText.Entry',0x6A5B:'Station.DrawHelpContents.Entry',0x6DD4:'Station.DrawDecodedMessagePanel.Entry',0xCBA9:'Station.RestoreItemBounds.Entry'}


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for target,name in TARGETS.items():operation=operation.replace('#'+format(target,'04X'),'@'+name)
 return operation
