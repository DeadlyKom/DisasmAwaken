"""Самомодифицируемые строки наведения семи исходных списков."""
# Физические параметры взяты из исходных инструкций и таблицы FInterfaceItem.
PANELS=(
 (0x67D0,'UpdateShipListHover',25,0x67E0,0x1E1B,'ShipsRow',0x67D7,False,'списка Корабли'),
 (0x6A4B,'UpdateIndexListHover',22,0x6A5B,0x1E0B,'IndexRow',0x6A52,False,'списка Индекс'),
 (0x6B8E,'UpdateEnvironmentHover',41,0x6BA5,0x1E0B,'EnvironmentRow',0x6B95,False,'установок среды'),
 (0x7210,'UpdateEquipmentHover',38,0x7227,0x1E1B,'EquipmentRow',0x7217,False,'оснащения корабля'),
 (0x7482,'UpdateToPositionHover',43,0x7492,0x2803,'ToPositionRow',0x7489,True,'списка В позицию 1..5'),
 (0x750B,'UpdateFromPositionHover',44,0x751B,0x2803,'FromPositionRow',0x7512,True,'списка С позиции 1..5'),
 (0x7620,'UpdateGameSettingsHover',42,0x7637,0x1E0B,'GameSettingsRow',0x7627,False,'установок игры'))
FUNCTIONS={a:(name,'Обновление XOR-полосы '+description+' с сохранением номера только по Z=0') for a,name,_,_,_,_,_,_,description in PANELS}
DOCUMENTS={('Station',a):('PanelHover','точные ограничения, изменяемые строки и различие пиксельного и строчного входов') for a in FUNCTIONS}


def row_symbol(name):
 return 'ScriptSelection.EquipmentRow' if name=='EquipmentRow' else 'PanelHoverState.'+name


CONTRACTS={};COMMENTS={}
for a,name,index,draw,area,row,operand,pixel,description in PANELS:
 callee='UpdatePixelHover' if pixel else 'UpdateRowHover'
 CONTRACTS['Station',a]=(
  ['IX - допустимая FInterfaceItem '+description+', подготовлены указатель, шрифт, таблицы адресации и банковое XOR-ядро',
   'список рисования непуст и завершается исходным маркером, PointerY=0..191, выбран станционный банк 0',
   row_symbol(row)+' содержит прежний номер либо FF, его операнд доступен для записи',
   'действуют договоры '+callee+', XorItemRow, XorPointerRow, SuspendPointer и ResumePointer'],
  ['перед '+callee+' установлены HL=DrawItem'+str(index)+'.Entry, DE='+format(area,'04X')+', A прежний номер',
   ('D=40 пикселей передаётся прямо, E=3, высота FInterfaceItem не ограничивает область этого входа' if pixel else
    'D=30 запрошенных строк, E='+str(area&255)+' пикселей, фактическую байтовую высоту рассчитывает ClampRowHeight'),
   'при Z=1 возвращённого '+callee+' сохранённый номер не меняется, выходные регистры принадлежат соответствующей ветви отказа или совпадения',
   'при Z=0 весь возвращённый A записан в '+row_symbol(row)+', даже если A=0 либо повторная проверка вернула высоту',
   "HL, DE, BC и AF принадлежат "+callee+", HL', DE', BC', IX, IY сохраняются, AF' рабочий только на обновлении указателя",
   'при соблюдении договоров SP обычного возврата равен входному SP+2, I, IFF и IM не меняются'],
  ["HL, DE, BC, AF, AF' на изменении полосы и указателя"],
  ['обновление допускается лишь для точного адреса рисователя в последнем слове списка',
   'Z показывает отсутствие обновления, он не равнозначен нулю A',
   'две проверки PointerY не атомарны, обёртка не исправляет служебный результат позднего отказа',
   'рисователь сбрасывает свой операнд строки в FF после замены фона, эта обёртка сама фон панели не рисует',
   'названия списков взяты из исходных заголовков и текстов, назначение действий их строк этим контрактом не устанавливается'])
 COMMENTS.update({
  a: (['выбор '+('40 пикселей и отступа 3' if pixel else 'запроса 30 строк и отступа '+str(area&255))+' для '+description],None),
  a+3: (['выбор точного рисователя, который должен быть последним в списке'],None),
  a+6: (['чтение изменяемого номера прежней XOR-полосы, FF означает её отсутствие'],None),
  a+8: (['проверка положения указателя и обновление полосы через '+callee],None),
  a+11: ([], 'выход, если '+callee+' вернул Z=1, сохранить прежний номер'),
  a+12: (['сохранение полного результата A только по Z=0, нулевая строка тоже допустима'],None)})

# Старший операнд корабельного наведения перезаписывается доказанным рисователем, 30 является только исходным значением.
ship_contract=list(CONTRACTS['Station',0x67D0])
ship_contract[1]=[line.replace('DrawItem25','DrawModelListPanel').replace('DE=1E1B','DE с младшим отступом 1B и старшим ModelListState.HoverRows').replace('D=30 запрошенных строк','D равен текущему ModelListState.HoverRows, исходно 30') for line in ship_contract[1]]
ship_contract[3]=[*ship_contract[3],'DrawModelListPanel записывает вычисленный счётчик в 67D2, поэтому во время игры D не обязан равняться исходному 30']
CONTRACTS['Station',0x67D0]=tuple(ship_contract)
COMMENTS[0x67D0]=(['выбор отступа 27 пикселей и текущего счётчика ModelListState.HoverRows, исходно 30'],None)


def name_operands(region,address,operation):
 if region!='Station':return operation
 for panel in PANELS:
  operation=operation.replace('(#'+format(panel[6],'04X')+')','(@'+row_symbol(panel[5])+')')
 if address not in FUNCTIONS:return operation
 panel=next(p for p in PANELS if p[0]==address)
 constant='PositionsPixels' if panel[7] else ('IndentedRows' if panel[4]&255==27 else 'Rows')
 return operation.replace('LD DE, #'+format(panel[4],'04X'),'LD DE, @PanelHoverConst.'+constant).replace('LD HL, #'+format(panel[3],'04X'),'LD HL, @Station.'+('DrawModelListPanel' if panel[2]==25 else 'DrawItem'+str(panel[2]))+'.Entry')
