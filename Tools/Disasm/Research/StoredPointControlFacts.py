"""Трёхбайтовые входы событий шести доказанных операций списков, новое действие сохраняется callback, а не вызывается сразу."""
FUNCTIONS={0x7B57:('HandleStoredPointToggle','Подготовка callback переключения A через общий выбор геометрии либо активации'),
 0x7BB6:('HandleSecondaryPointToggle','Подготовка callback переключения B через общий выбор геометрии либо активации'),
 0x7C5A:('HandleSecondaryClear','Подготовка callback очистки B через общий выбор геометрии либо активации'),
 0x7C84:('HandleStoredPointCycle','Подготовка callback циклического выбора A через геометрию либо активацию'),
 0x7CFE:('HandleCurrentMapCenter','Подготовка callback центрирования текущего ключа через геометрию либо активацию'),
 0x7D2A:('HandleSecondaryCursor','Подготовка callback установки курсора B через геометрию либо активацию')}
TARGETS={0x7B57:(0x7B61,'ToggleStoredMapPoint'),0x7BB6:(0x7BC0,'ToggleSecondaryMapPoint'),0x7C5A:(0x7C64,'ClearSecondaryMapPoints'),0x7C84:(0x7C8E,'CycleStoredMapPoint'),0x7CFE:(0x7D08,'CenterCurrentMapPoint'),0x7D2A:(0x7D34,'SelectSecondaryListCursor')}
LABELS={('Station',a+3):'Action' for a in FUNCTIONS}
DOCUMENTS={('Station',a):('StoredPointEdits','событие с входом Entry+3, отложенный callback и общая развилка активации') for a in FUNCTIONS}
CONTRACTS={}
COMMENTS={}
for address,(_,target) in TARGETS.items():
 CONTRACTS['Station',address]=(
  ['DE - индекс элемента, BC - сохраняемый контекст, AF - селектор по договору ActivateInterfaceCallback',
   'действуют условия TrackItemGeometry, ToggleItemBounds и ActivateItem для реально выбранной ветви, FlagsCache подготовлен',
   'Entry содержит исходный JP в Action, диспетчер может входить сразу через Action=Entry+3'],
  ['HL заменён адресом '+target+'.Entry, затем выполняется настоящий ActivateInterfaceCallback',
   'NextCallback получает этот адрес до выбора ветви, новое действие этим обработчиком немедленно не вызывается',
   'при A=0 возможны интерактивная геометрия либо переключение границ, ненулевой A активирует элемент по общему договору',
   'DE и BC сохранены, HL, AF и IX соответствуют выбранному пути ActivateInterfaceCallback с новым callback',
   'H\', DE\', BC\', IY, I и IFF сохраняются по договорам помощников, L\' и AF\' рабочие на пути рисунка',
   'RET после общего помощника возвращает тому же вызывающему коду, SP обычного возврата равен входному SP+2'],
  ["HL, AF, HL', AF', IX и графическое состояние выбранного общего пути"],
  ['первый JP не создаёт стекового адреса возврата, вход Action пропускает только этот трёхбайтовый префикс',
   'на нулевом селекторе сохранённый NextCallback сам по себе не означает, что операция списка была исполнена',
   'проверка основана на точной последовательности десяти байтов и доказанных договорах общего помощника, это не самостоятельное доказательство аппаратного ввода'])
 COMMENTS[address]=(['передача с внешней трёхбайтовой обёртки в доступный диспетчеру вход Action'],None)
 COMMENTS[address+3]=(['выбор адреса '+target+' для сохранения в NextCallback, прямого вызова операции здесь нет'],None)
 COMMENTS[address+6]=(['общий выбор геометрии, контура либо активации с новым callback'],None)


def name_operands(region,address,operation):
 if region=='Station' and address in TARGETS:
  value,name=TARGETS[address];operation=operation.replace('LD HL, #'+format(value,'04X'),'LD HL, @Station.'+name+'.Entry')
 return operation
