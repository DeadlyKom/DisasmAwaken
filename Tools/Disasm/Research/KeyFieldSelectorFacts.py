"""Четыре селектора двух групп характеристик ключа, таблицы сверены по исходным адресам."""
ENTRIES={0xC383:('ReadCurrentKeyParams',0,0xCA25,3),0xC399:('ReadOtherKeyParams',1,0xCA25,3),
 0xC3AF:('ReadCurrentKeyCodes',0,0xCA2E,2),0xC3C5:('ReadOtherKeyCodes',1,0xCA2E,2)}
FUNCTIONS={a:(name,'Выбор '+('текущего' if default==0 else 'второго')+' ключа по умолчанию и группы '+('s, c, u' if count==3 else 'p, g')) for a,(name,default,anchor,count) in ENTRIES.items()}
DOCUMENTS={('Text',a):('KeyFieldSelectors','точные таблицы s/c/u и p/g, явный индекс и путь без точки') for a in ENTRIES}
LABELS={('Text',a+15):'NoSuffix' for a in ENTRIES}
CONTRACTS={};COMMENTS={}
for address,(name,default,anchor,count) in ENTRIES.items():
 CONTRACTS['Text',address]=(
  ['IX - начало необязательного числового выбора либо точки, B сохраняемый контекст до диспетчера',
   'без числа используется код выбора '+str(default)+', явное число преобразуется в (число-1) AND #FFFF',
   'LANG находится в банке 6, данные обоих ключей доступны, действуют договоры ParseFieldSuffix и DescribeKeyChoice'],
  ['без точки HL полный индекс выбора, DE=#'+format(anchor,'04X')+' адрес за одной записью до таблицы свойств',
   'без точки BC - B сохранён, C='+str(default)+', AF - A непрочитанный символ, F последнего CP парсера',
   'с точкой DE поле характеристики по выбранному символу, HL и AF по договору соответствующего GetKey обработчика',
   'с точкой BC - B старший байт слова выбора, C=(младший_байт_выбора-1) AND #FF',
   "HL', DE' сохранены, BC' - B'="+str(count)+", C' сохранён, AF' меняется при банковом запросе поля",
   'IX первый непрочитанный символ, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2'],
  ["HL, DE, BC, AF, BC' только B, AF' на пути свойства, IX"],
  ['группа '+('s/c/u возвращает Major, Minor, Size' if count==3 else 'p/g возвращает Fingerprint, Region'),
   'младший байт выбора 1 выбирает второй ключ, остальные текущий, значит явное число 2 выбирает второй',
   'путь без точки возвращает адрес таблицы в DE, а не числовую характеристику, исходный RET сохранён',
   'при неизвестном символе FindToken передаёт управление SkipLine без обычного результата',
   'игровые единицы параметров и роль второго ключа здесь не предполагаются'])
 COMMENTS[address]=(['установка числа '+str(count)+' свойств выбранной группы в альтернативном B'],None)
 COMMENTS[address+4]=(['выбор кода '+str(default)+' по умолчанию, '+('текущий ключ' if default==0 else 'второй ключ')],None)
 COMMENTS[address+6]=(['выбор адреса за одной записью до группы '+('s/c/u' if count==3 else 'p/g')],None)
 COMMENTS[address+9]=(['выбор локального RET для пути без точки, DE остаётся адресом таблицы'],None)
 COMMENTS[address+15]=(['возврат без суффикса, поле характеристики не вычислялось'],None)


def name_operands(region,address,operation):
 if region=='Text' and address in ENTRIES:
  name=ENTRIES[address][0];return operation.replace('#'+format(address+15,'04X'),'@Text.'+name+'.NoSuffix')
 return operation
