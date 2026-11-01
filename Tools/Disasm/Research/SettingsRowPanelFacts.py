"""Печать текущих значений среды и игры с общим хвостом и альтернативным счётчиком."""
import re
FUNCTIONS={0x6B9E:('TryDrawEnvironmentPanel','Условное рисование установок среды при точном указателе панели в списке'),
 0x6BA5:('DrawEnvironmentPanel','Рамка установок среды, сброс подсветки и сохранение числа обработанных значений'),
 0x6BBE:('PrintEnvironmentRows','CR-подписи установок среды и общий цикл текущих значений со счётчиком в A\''),
 0x6C00:('SetupEnvironmentText','Запрет переноса установок среды и выбор колонки значений X=66'),
 0x7630:('TryDrawGameSettings','Условное рисование установок игры при точном указателе панели в списке'),
 0x7637:('DrawGameSettings','Рамка установок игры, сброс подсветки и сохранение числа обработанных значений'),
 0x7650:('PrintGameSettingsRows','CR-подписи игровых клавиш и передача значений в общий цикл среды'),
 0x766C:('SetupGameSettingsText','Запрет переноса установок игры и выбор колонки значений X=110')}
RENAMES={'Unknown6B9E':'TryDrawEnvironmentPanel','DrawItem41':'DrawEnvironmentPanel','Unknown6BBE':'PrintEnvironmentRows','Unknown6C00':'SetupEnvironmentText',
 'Unknown7630':'TryDrawGameSettings','DrawItem42':'DrawGameSettings','Unknown7650':'PrintGameSettingsRows','Unknown766C':'SetupGameSettingsText'}
LABELS={('Station',0x6BB6):'RenderRows',('Station',0x6BD7):'ResetCount',('Station',0x6BD9):'DrawValue',('Station',0x6BEF):'NextRow',('Station',0x7648):'RenderRows'}
LABEL_RENAMES={'PrintEnvironmentRows.Point6BD7':'PrintEnvironmentRows.ResetCount','PrintEnvironmentRows.Point6BD9':'PrintEnvironmentRows.DrawValue','PrintEnvironmentRows.Point6BEF':'PrintEnvironmentRows.NextRow'}
CONTINUATIONS={0x6B9E:0x6BA5,0x7630:0x7637}
DOCUMENTS={('Station',a):('SettingsRowPanels','два CR-списка, общий хвост значений, полный индекс и счётчик обработанных полей') for a in FUNCTIONS}
CONTRACTS={}
for address,column in ((0x6C00,66),(0x766C,110)):
 CONTRACTS['Station',address]=(
  ['нет регистровых параметров, существующие операнды Style и Column2X доступны для записи'],
  ['HL, DE, BC сохранены, AF содержит A='+str(column)+', F=44',
   "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
   'TextWindow.Style=0, TextStreamState.Column2X='+str(column)+', экран, курсор и страница не меняются'],
  ['AF, TextWindow.Style, TextStreamState.Column2X'],
  ['нулевой Style выбирает пропуск остатка подписи при отказе ширины, значение X задано в пикселях относительно окна',
   'проверены все 65536 AF и все прежние байты обоих операндов'])
for address,label_base,value_name,value_base,number in ((0x6BBE,'DECB','SettingsText.Interface','9728',13),(0x7650,'DF3C','SettingsText.Controls','9736',43)):
 CONTRACTS['Station',address]=(
  ['HL содержит полное слово начальной позиции, младший байт выбирает CR-подпись, полное слово смещает указатель значений',
   'BC сохраняемый контекст поиска подписи, остальные регистры не задают отдельного параметра',
   'окно, Column2X, глифы, стек и нультерминированные значения подготовлены, Style=0 соответствует штатному выводу',
   'от '+label_base+' существуют L+1 разделителей CR и завершающийся поток подписи, от '+value_name+'+HL читается конечный массив'],
  ['HL указывает за фактически обработанными значениями либо на исходный нуль, DE равен входному HL',
   'BC первоначально '+value_base+', после попытки нового Y B=97, C=Height',
   'AF=0044 при нулевом значении, AF=0042 при последнем статусе глифа 1 либо 2, иначе A новый байтовый Y и F от CP Height на отказе строки',
   "HL', DE', BC', IX, IY, I, IFF и IM сохранены, A' содержит число обработанных ненулевых значений по модулю 256",
   "F' принадлежит последнему INC счётчика, при нуле обработанных значений A'F'=0044, SP после RET входному+2",
   'первый курсор подписи X=0,Y=8, перед значениями Y=8, перед каждым значением X=Column2X, bitmap содержит принятую часть вывода'],
  ["HL, DE, BC, AF, AF', курсор, bitmap и изменяемые операнды PrintAfterCR и DrawKeyLabel"],
  ['исходная подпись содержит '+str(number)+' значений, границы и допустимость индекса обёртка не проверяет',
   'счётчик увеличивается до проверки результата DrawKeyLabel, последний отказ тоже учитывается',
   'общий вход PrintEnvironmentRows.ResetCount принимает HL непосредственно на первом значении, DE и B сохраняемый контекст, C меняется только при попытке нового Y',
   'общий вход не печатает подписи и не сбрасывает Y, он обнуляет альтернативный счётчик и переходит к тем же правилам значений'])
for address,render,index,row,setup,printer in (
 (0x6BA5,'EnvironmentPanelState',41,'PanelHoverState.EnvironmentRow','SetupEnvironmentText','PrintEnvironmentRows'),
 (0x7637,'GameSettingsPanelState',42,'PanelHoverState.GameSettingsRow','SetupGameSettingsText','PrintGameSettingsRows')):
 CONTRACTS['Station',address]=(
  [render+'.ItemIndex содержит индекс FInterfaceItem, штатно '+str(index)+', либо Entry временно содержит C9',
   'геометрия, шрифт, таблицы, стек и IRQ удовлетворяют DrawCaptionItem, TopRow и значения подготовлены',
   'для обычного Entry выполняются договоры '+setup+' и '+printer],
  ['после рамки '+row+'=FF, окно и колонка значений настроены, TopRow передан печатателю',
   'HL, DE и BC принадлежат печатателю, основной AF содержит его альтернативный счётчик и флаги',
   "AF' содержит основной результат печатателя, HL', DE', BC', IX и IY сохранены",
   render+'.RowCount получает полный байт обработанных значений, включая последний отказ, TopRow не меняется',
   'страница не переключается собственным кодом, I, IFF и IM сохраняются при договоре IRQ, SP после RET входному+2',
   'RenderRows принимает HL от прокрутки, пропускает рамку, сброс подсветки, настройку и чтение TopRow, затем выполняет печать и запись RowCount',
   'при временном C9 в Entry сохраняются регистры, флаги и память, SP после RET входному+2'],
  ["HL, DE, BC, AF, AF', окно, курсор, bitmap, номер подсветки, RowCount и изменяемые операнды помощников"],
  ['RowCount задаёт D обработчика наведения, число начатых значений не является числом успешно нарисованных строк',
   'пробуждение HALT рамки требуется только для Entry, внутренний RenderRows нового HALT не выполняет'])
for address,target in ((0x6B9E,'DrawEnvironmentPanel'),(0x7630,'DrawGameSettings')):
 CONTRACTS['Station',address]=(
  ['HL и BC сохраняемый контекст TestDrawPointer, список с исходным ограничителем доступен',
   'для присутствующего исходного рисователя выполняется договор '+target],
  ['при отсутствии HL и BC сохранены, DE содержит точный адрес '+target+'.Entry, AF принадлежит TestDrawPointer',
   'при совпадении исходного рисователя выполняется весь его договор через физическое продолжение следующего файла',
   'при совпадении временного C9 рисователя AF=0050, HL и BC сохранены, DE содержит адрес рисователя',
   'SP после возврата входному+2, остальные регистры по фактически выполненному рисователю либо сохранены на отказе'],
  ['DE, AF, другие регистры и память только по фактически выполненному рисователю'],
  ['алиас с тем же ключом элемента не заменяет точного указателя, порядок include (0), (1) жёсткий'])
COMMENTS={
 0x6B9E:(['поиск точного адреса панели среды в текущем списке рисования'],None),0x6BA4:([],'выход, если точный указатель панели среды отсутствует'),
 0x6BA5:(['чтение изменяемого индекса панели среды перед рисованием рамки'],None),0x6BA8:(['рисование рамки и заголовка с подготовкой окна'],None),
 0x6BAB:(['сброс прежней XOR-полосы, фон панели заменяется'],None),0x6BB0:(['выбор политики без переноса и колонки значений среды'],None),
 0x6BB3:(['чтение полного слова прокрутки панели среды'],None),
 0x6BB6:(['RenderRows принимает HL от прокрутки, рамка и настройка уже подготовлены'],None),
 0x6BB9:(['получение альтернативного счётчика обработанных значений'],None),0x6BBA:(['обновление байтового ограничения строк обработчика наведения'],None),
 0x6BBE:(['сохранение полного исходного индекса в DE и подготовка курсора подписей'],None),
 0x6BC5:(['поиск CR-подписи, только E задаёт число пропускаемых разделителей'],None),
 0x6BCD:(['сброс Y перед значениями независимо от результата подписей'],None),
 0x6BD2:(['расчёт полного адреса начального значения, старший байт индекса не отбрасывается'],None),
 0x6BD7:(['ResetCount принимает HL значений, DE и B сохраняются, исходный Y подготовлен вызывающим кодом'],None),
 0x6BD9:(['обновление X колонки перед каждым значением, включая нулевой ограничитель'],None),
 0x6BDF:(['проверка нуля, ограничивающего массив значений'],None),0x6BE1:([],'выход, если текущее значение равно нулю, оно не учитывается в счётчике'),
 0x6BE2:(['вывод одного значения, специальные клавиши дают четыре глифа'],None),
 0x6BE5:(['переход к следующему значению и обновление альтернативного байтового счётчика до проверки статуса'],None),
 0x6BE9:([],'переход, если последний глиф принят, проверить следующую строку'),
 0x6BEB:(['проверка вертикального отказа глифа с кодом 1'],None),0x6BEC:([],'выход, если последний статус глифа равен 1, значение уже учтено'),
 0x6BED:(['проверка отказа относительной высоты с кодом 2'],None),0x6BEE:([],'выход, если последний статус глифа равен 2, значение уже учтено'),
 0x6BEF:(['расчёт следующего байтового Y с шагом 8 и проверка высоты окна'],None),
 0x6BF9:([],'выход, если новый Y не меньше высоты, последняя обработанная строка уже учтена'),
 0x6BFA:(['обновление принятого Y перед следующим значением'],None),
 0x6C00:(['отключение переноса подписей и выбор колонки значений среды X=66'],None),
 0x7630:(['поиск точного адреса панели установок игры в списке рисования'],None),0x7636:([],'выход, если точный указатель панели установок игры отсутствует'),
 0x7637:(['чтение изменяемого индекса панели установок игры'],None),0x763A:(['рисование рамки и заголовка с подготовкой окна'],None),
 0x763D:(['сброс прежней XOR-полосы после замены фона'],None),0x7642:(['отключение переноса и выбор колонки игровых значений'],None),
 0x7645:(['чтение полного слова прокрутки установок игры'],None),0x7648:(['RenderRows принимает HL от прокрутки без новой рамки'],None),
 0x764B:(['получение альтернативного счётчика обработанных значений'],None),0x764C:(['обновление байтового ограничения наведения по обработанным значениям'],None),
 0x7650:(['сохранение полного исходного индекса и подготовка начального курсора подписей'],None),
 0x7657:(['выбор CR-подписи игровых клавиш по младшему байту исходного индекса'],None),
 0x765F:(['сброс Y перед значениями независимо от результата подписей'],None),
 0x7664:(['расчёт полного адреса значения в физической подписи SettingsText.Controls'],None),
 0x7669:(['передача значений в общий хвост с новым альтернативным счётчиком'],None),
 0x766C:(['отключение переноса и выбор колонки игровых значений X=110'],None)}
TARGETS={0x6BA5:'Station.DrawEnvironmentPanel.Entry',0xCB64:'Station.TestDrawPointer.Entry',0xC287:'Station.DrawCaptionItem.Entry',
 0x6B95:'PanelHoverState.EnvironmentRow',0x6C00:'Station.SetupEnvironmentText.Entry',0x6B23:'EnvironmentPanelState.TopRow',0x6BBE:'Station.PrintEnvironmentRows.Entry',
 0x6B90:'EnvironmentPanelState.RowCount',0x6320:'TextWindow.CursorX',0x6321:'TextWindow.CursorY',0xDECB:'SettingsRowConst.EnvLabels',
 0xA36E:'Station.PrintAfterCR.Entry',0x9728:'SettingsText.Interface',0xBD73:'TextStreamState.Column2X',0xBDF0:'Station.DrawKeyLabel.Entry',
 0x6BEF:'Station.PrintEnvironmentRows.NextRow',0xAEAB:'TextWindow.Height',0x6BD9:'Station.PrintEnvironmentRows.DrawValue',0xBD26:'TextWindow.Style',
 0x7637:'Station.DrawGameSettings.Entry',0x7627:'PanelHoverState.GameSettingsRow',0x766C:'Station.SetupGameSettingsText.Entry',0x75D3:'GameSettingsPanelState.TopRow',
 0x7650:'Station.PrintGameSettingsRows.Entry',0x7622:'GameSettingsPanelState.RowCount',0xDF3C:'SettingsRowConst.GameLabels',0x9736:'SettingsText.Controls',
 0x6BD7:'Station.PrintEnvironmentRows.ResetCount'}
MODIFIED_WRITES=((0x6BAD,0x6B95,'Station',0x6B94,1,5),(0x6BBA,0x6B90,'Station',0x6B8E,1,5),
 (0x6C01,0xBD26,'Station',0xBD25,1,2),(0x6C06,0xBD73,'Station',0xBD72,1,2),
 (0x763F,0x7627,'Station',0x7626,1,5),(0x764C,0x7622,'Station',0x7620,1,5),
 (0x766D,0xBD26,'Station',0xBD25,1,2),(0x7672,0xBD73,'Station',0xBD72,1,2))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation.replace('LD A, #42','LD A, @SettingsRowConst.EnvColumn').replace('LD A, #6E','LD A, @SettingsRowConst.GameColumn')
