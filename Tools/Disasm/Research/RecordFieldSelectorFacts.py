"""Выбранные и банковые входы двух наборов пятибайтовых записей."""
ENTRIES={0xC207:('ReadSelectedPrimaryFields',0x9849,False,3,0xC21A),
 0xC227:('ReadSelectedSecondaryFields',0x984A,False,2,0xC23A),
 0xC2D6:('ReadBank4PrimaryFields',0x9849,True,3,0xC2E6),
 0xC2F0:('ReadBank4SecondaryFields',0x984A,True,2,0xC300)}
FUNCTIONS={a:(name,'Чтение свойств '+('первого' if n==3 else 'второго')+' набора по '+('индексу банка 4' if banked else 'байту выбранной записи')) for a,(name,selector,banked,n,target) in ENTRIES.items()}
DOCUMENTS={('Text',a):('RecordFieldSelectors','точные c/t/s и c/v, исходный селектор и возврат 127') for a in ENTRIES}
LABELS={('Text',target):'NoSuffix' for _,_,_,_,target in ENTRIES.values()}
CONTRACTS={};COMMENTS={}
for address,(name,selector,banked,n,target) in ENTRIES.items():
 CONTRACTS['Text',address]=(
  ['IX - начало необязательного индекса либо точки, таблицы читаемы, действуют договоры ParseFieldSuffix и стекового чтения',
   ('индекс по умолчанию получает SumBank4Index, доступны банк 4 и возврат в LANG 6' if banked else 'индекс по умолчанию равен байту по #'+format(selector,'04X')),
   'явное число задаёт (число-1) AND #FFFF, свойства используют младший байт этого индекса'],
  ['без точки HL индекс парсера, DE='+('127 независимо от индекса' if banked else 'исходный байт селектора независимо от явного числа'),
   'без точки BC - B=0, C исходный индекс по умолчанию, AF - A непрочитанный символ, F последнего CP парсера',
   'с точкой DE прочитанное поле, HL адрес поля либо его старшего байта, BC младший байт индекса с нулевым B',
   'с точкой AF по договору ReadStrideFiveWord либо ReadStrideFiveByte, A младший байт адреса выбранного обработчика',
   "HL', DE' сохранены, BC' - B'="+str(n)+", C' сохранён, AF' и IY, I и IFF сохранены",
   'IX первый непрочитанный символ, SP обычного возврата равен входному SP+2',
   ('порт и тень выбирают банк 4 затем банк 6, на пути без точки это тоже выполняется' if banked else 'переключений банков нет')],
  ["HL, DE, BC, AF, BC' только B, IX"],
  ['первый набор c читает слово #9803+5*индекс, t байт #9802+5*индекс, s байт #9806+5*индекс',
   'второй набор c читает слово #9826+5*индекс, v байт #9829+5*индекс',
   'игровые имена и единицы этих физических полей пока не установлены, первичный и вторичный обозначают разные таблицы',
   'неизвестный суффикс передаёт управление SkipLine без обычного числового результата'])
 if banked:
  COMMENTS[address]=(['получение индекса по двум байтам банка 4 с возвратом LANG 6'],None)
  COMMENTS[address+3]=(['установка числа свойств в альтернативном B'],None)
  COMMENTS[address+7]=(['выбор адреса за одной записью до таблицы свойств набора'],None)
  COMMENTS[address+10]=(['выбор локального возврата константы 127 для отсутствующей точки'],None)
  COMMENTS[target]=(['возврат исходной константы 127 без чтения полей записи'],None)
 else:
  COMMENTS[address]=(['чтение слова по адресу селектора, следующий байт B сразу отбрасывается'],None)
  COMMENTS[address+4]=(['обнуление B, индекс по умолчанию остаётся в C'],None)
  COMMENTS[address+6]=(['установка числа свойств в альтернативном B'],None)
  COMMENTS[address+10]=(['выбор адреса за одной записью до таблицы свойств набора'],None)
  COMMENTS[address+13]=(['выбор локального чтения исходного селектора без точки'],None)
  COMMENTS[target]=(['повторное чтение байта селектора, явный числовой индекс здесь не используется'],None)


def name_operands(region,address,operation):
 if region!='Text' or address not in ENTRIES:return operation
 name,_,_,_,target=ENTRIES[address]
 return operation.replace('#'+format(target,'04X'),'@Text.'+name+'.NoSuffix').replace('CALL #AA1D','CALL @Station.SumBank4Index.Entry')
