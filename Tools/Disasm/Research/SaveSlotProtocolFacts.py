"""Исходные обработчики записи/чтения двух секторов SAVE, без обещания исполнения настоящего DOS."""
import re
FUNCTIONS={0x7421:('HandleSaveSlotAction','Выбор позиции и запись двух секторов блока состояния в существующий SAVE-файл'),
 0x74AA:('HandleLoadSlotAction','Выбор позиции и чтение двух секторов существующего SAVE-файла в блок состояния')}
RENAMES={'Unknown7421':'HandleSaveSlotAction','Unknown74AA':'HandleLoadSlotAction'}
LABELS={('Station',0x742E):'TransferState',('Station',0x7470):'RestoreContext',('Station',0x74B7):'TransferState',('Station',0x74F9):'RestoreContext'}
LABEL_RENAMES={'HandleSaveSlotAction.Point742E':'HandleSaveSlotAction.TransferState','HandleLoadSlotAction.Point74B7':'HandleLoadSlotAction.TransferState'}
DOCUMENTS={('Station',a):('SaveSlots','точный протокол DOS, два разных кадра, I, IM, IFF, отсутствие проверки ошибки и физический ключ') for a in FUNCTIONS}
CONTRACTS={}
for address,save in ((0x7421,True),(0x74AA,False)):
 name='ToPositionRow' if save else 'FromPositionRow';command='06 записи' if save else '05 чтения'
 CONTRACTS['Station',address]=(
  ['HL запасной рисователь позиции, DE индекс элемента 43 записи либо 44 чтения, BC контекст, AF полный селектор',
   'действуют договоры RepaintAndFlag, CloseMenuOnRow и DropItemDraw, исходный список и хвосты сдвига доступны',
   'для селектора 1 PanelHoverState.'+name+' содержит выбранный байт, существующий ключ SAVE и системная область DOS доступны',
   'TR-DOS возвращается штатным CPU-возвратом, не меняет кадр, его договоры сохраняют доступность кода, стека и выбранного банка',
   'системная длина ключа поиска DOS подготовлена на девять байтов, после поиска допустимого файла C задаёт индекс записи',
   'команда 08 выдаёт FTrDosEntry в Descriptor, первые два сектора существуют',
   'блок 983B..9A3A и изменяемый операнд восстановления I доступны, IY во время DOS указывает на системные переменные 5C3A'],
  ['при Carry от RepaintAndFlag немедленно возвращён его результат, при селекторе не 1 вызван только CloseMenuOnRow',
   'при выборе FileDigit=(выбранный байт+30) AND FF, имя и тип скопированы девятью байтами в TrDosState.Descriptor',
   'последовательно вызваны команды 0A поиска, 08 дескриптора и '+command+', последний вызов получает HL=983B, B=2, DE=FirstTrack:FirstSector',
   'при штатной '+('записи два сектора получают прежние 512 байтов блока' if save else 'загрузке блок получает 512 байтов первых двух секторов файла')+', создание нового файла не выполняется',
   'DE и IY восстановлены из кадра TransferState, '+('HL сохранён от входа TransferState' if save else 'HL=7534, входной HL TransferState заменён адресом цифры до PUSH'),
   'BC, IX и альтернативные пары имеют результаты DOS и сохраняются DropItemDraw, отдельного сохранения этих регистров нет',
   'I восстановлен до значения в начале TransferState, IM принудительно равен 2, IFF не восстанавливается и зависит от DOS',
   'текущий элемент удалён по сохранённому DE, при найденном ключе EventEnabled=0, A содержит выбранный байт, F соответствует DropItemDraw',
   'при найденном удалении F=44, SP обычного возврата входному+2, явных OUT и самостоятельного нового рисунка после переноса нет'],
  ["HL, BC, AF, HL', DE', BC', AF', IX по DOS, IFF, IM, имя, дескриптор DOS, сохранённый I, список и EventEnabled"+
   (', содержимое существующих секторов при настоящем DOS' if save else ', 512 байтов блока при штатном чтении')],
  ['TransferState является внутренним входом без RepaintAndFlag и проверки селектора, DE и IY задают сохраняемый контекст',
   'до DOS исполняются DI, I=3F и IM 1, исходный режим IM не сохраняется, EI после возврата отсутствует',
   'сохранённый AF содержит A=3F и флаги LD A,I, это не сохранение исходного AF и не восстановление IFF',
   'код не проверяет FF поиска, передаёт его в A команды 08, ошибки дескриптора и переноса тоже не проверяются',
   'выбранный FF не отвергается, арифметика даёт символ 2F вместо цифры, допустимость позиции задаёт вызывающее окружение',
   'модель подменяет 3D13 явными договорами и переносит сектора только в памяти, настоящая ROM, контроллер и дисковая запись не исполнялись'])
COMMENTS={0x7421:(['обновление общей геометрии и порядка списка до обработки выбора позиции'],None),0x7424:([],'выход, если общий обработчик вернул Carry, запись позиции не разрешена'),
 0x7425:(['проверка селектора 1 для записи состояния'],None),0x7426:([],'переход, если селектор равен 1, выполнить протокол записи'),
 0x7429:(['удаление панели только при совпадении символьных строк указателя и окна'],None),0x742C:([],'выход, если символьные строки совпали, помощник закрытия уже завершён'),
 0x742E:(['сохранение текущего I в существующий операнд восстановления записи'],None),0x7433:(['выбор ROM-совместимого режима, IFF запрещается, I=3F, IM 1'],None),
 0x743A:(['создание FSaveSlotFrame, порядок IY, HL, AF, DE оставляет SavedDE на вершине'],None),0x743F:(['выбор системных переменных Spectrum для вызовов TR-DOS'],None),
 0x7443:(['расчёт символа номера файла по полному байту наведения без проверки FF'],None),0x7448:(['обновление пятого символа физического имени SAVE'],None),
 0x744C:(['копирование реального FTrDosFileKey в буфер запроса DOS без терминатора'],None),0x7457:(['поиск существующей записи по имени и типу, результат C далее не проверяется'],None),
 0x745C:(['чтение дескриптора по возвращённому C, исходник передаёт также ошибочный FF'],None),0x7462:(['подготовка 512-байтового блока, адрес первых секторов берётся из дескриптора'],None),
 0x7469:(['выбор ровно двух секторов для записи, длина записи не читается из каталога'],None),0x7470:(['восстановление исходного I и принудительный IM 2 до снятия кадра'],None),
 0x7476:(['снятие FSaveSlotFrame в порядке DE, AF, HL, IY'],None),0x747B:(['удаление текущей панели после возврата DOS, статус записи не проверяется'],None),
 0x747E:(['возврат исходного выбранного байта с флагами удаления панели'],None),
 0x74AA:(['обновление общей геометрии и порядка списка до обработки выбора позиции'],None),0x74AD:([],'выход, если общий обработчик вернул Carry, загрузка позиции не разрешена'),
 0x74AE:(['проверка селектора 1 для загрузки состояния'],None),0x74AF:([],'переход, если селектор равен 1, выполнить протокол чтения'),
 0x74B2:(['удаление панели только при совпадении символьных строк указателя и окна'],None),0x74B5:([],'выход, если символьные строки совпали, помощник закрытия уже завершён'),
 0x74B7:(['расчёт символа позиции и обновление физического имени до сохранения I'],None),0x74C0:(['сохранение I, флаги LD A,I включают Carry предшествующей суммы номера'],None),
 0x74C5:(['выбор I=3F и IM 1 после запрещения прерываний'],None),0x74CC:(['создание FLoadSlotFrame, сохраняемый HL уже равен адресу цифры 7534'],None),
 0x74D1:(['выбор системного IY для последовательных вызовов DOS'],None),0x74D5:(['копирование девяти байтов имени и типа в Descriptor'],None),
 0x74E0:(['поиск существующего файла по скопированному ключу'],None),0x74E5:(['чтение дескриптора без проверки FF или флагов поиска'],None),
 0x74EB:(['подготовка чтения двух физических секторов в исходный блок состояния'],None),0x74F9:(['снятие FLoadSlotFrame в порядке IY, AF, DE, HL'],None),
 0x74FE:(['восстановление I и принудительный IM 2, исходный IFF через EI не восстанавливается'],None),0x7504:(['удаление панели независимо от статуса чтения DOS'],None),
 0x7507:(['возврат выбранного байта с флагами удаления, HL остаётся адресом цифры'],None)}
TARGETS={0xCBEB:'Station.RepaintAndFlag.Entry',0xC85E:'Station.CloseMenuOnRow.Entry',0x7471:'SaveSlotState.SaveI',0x74FF:'SaveSlotState.LoadI',
 0x5C3A:'LoaderConst.SystemIY',0x7489:'PanelHoverState.ToPositionRow',0x7512:'PanelHoverState.FromPositionRow',0x7534:'SaveSlotState.FileDigit',
 0x7530:'SaveSlotFileName.Entry',0x5CDD:'TrDosState.Descriptor',0x3D13:'TrDos.Dispatch',0x983B:'SaveSlotState.Buffer',
 0x5CEB:'TrDosState.Descriptor + FTrDosEntry.FirstSector',0xC873:'Station.DropItemDraw.Entry'}
for (_,a),name in LABELS.items():TARGETS[a]='Station.'+('HandleSaveSlotAction' if a<0x74AA else 'HandleLoadSlotAction')+'.'+name
MODIFIED_WRITES=((0x7430,0x7471,'Station',0x7470,1,5),(0x74C2,0x74FF,'Station',0x74FE,1,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 for old,new in (('LD A, #3F','LD A, @SaveSlotConst.RomI'),('ADD A, #30','ADD A, @NumberConst.DigitZero'),('LD BC, #0009','LD BC, FTrDosFileKey'),
  ('LD C, #0A','LD C, @TrDos.FindFile'),('LD C, #08','LD C, @TrDos.ReadCatalog'),('LD C, #06','LD C, @TrDos.WriteSectors'),('LD C, #05','LD C, @TrDos.ReadSectors'),('LD B, #02','LD B, @SaveSlotConst.SectorCount')):operation=operation.replace(old,new)
 return operation
