"""Точные колонки оборудования и сохранённая числовая характеристика ключа."""
import re
FUNCTIONS={0x733F:('SetupEquipmentColumns','Подготовка четырёх X-колонок оснащения и сохранение характеристики L текущего ключа')}
RENAMES={'Unknown733F':'SetupEquipmentColumns'}
LABELS={}
DOCUMENTS={('Station',0x733F):('EquipmentListSetup','четыре исходных операнда X, формула 1..16 и точные флаги банкового вызова')}
CONTRACTS={('Station',0x733F):(
 ['SignatureInput.Entry содержит физический пятибайтовый FSignatureInput, действуют условия DescribeCurrentKey',
  'банк станции 0 выбран, CurrentPage равен 10 либо 18, реальные переключения банка разрешены',
  'операнды колонок и EquipmentListState.KeySize доступны для записи, обычный CPU-возврат доступен'],
 ['HL содержит H геометрический код характеристики и L числовое значение 1..16, DE содержит D код области и E младший двухбитовый признак',
  'BC сохранён, AF содержит A=L результата, F сохранён от DescribeCurrentKey, а не вычислен из нового A',
  "HL', DE', BC', IX, IY, I, IFF и IM сохранены, AF' содержит восстановленную страницу и флаги её OR",
  'Style=0, Column2X=74, Column3X=86, Column4X=9C, Column5X=AE, все значения X измеряются в пикселях окна',
  'KeySize равен L результата, рабочий FSignatureKey по 631C изменён согласно DescribeCurrentKey',
  'банк 1 выбран для расчёта, затем восстановлен банк 0 с исходным экранным битом, SP после RET входному+2'],
 ["HL, DE, AF, AF', Style, четыре операнда X, KeySize, рабочий FSignatureKey и порт страницы"],
 ['флаги не описывают размер KeySize, F=44 для исходного XOR AND 7 равного нулю, F=42 для единицы, иначе F=02',
  'KeySize вычисляется из инвертированной контрольной суммы после Variant+1 шагов как ((inverted >> 2) AND 15)+1',
  'по 72DC KeySize сравнивается с порогом модели станции, при меньшем значении колонка веса получает дефис',
  'процедура не выводит текст и не меняет bitmap, не создаёт новый адрес или участок памяти'])}
COMMENTS={0x733F:(['обновление режима текста, для списка оборудования автоматический перенос выключен'],None),
 0x7343:(['подготовка X второй колонки в пикселях относительно окна'],None),
 0x7348:(['подготовка X третьей колонки'],None),0x734D:(['подготовка X четвёртой колонки'],None),
 0x7352:(['подготовка X пятой колонки'],None),0x7357:(['расчёт характеристики фактического текущего пятибайтового ключа'],None),
 0x735A:(['сохранение результата L в операнд сравнения таблицы, флаги DescribeCurrentKey остаются прежними'],None)}
TARGETS={0xA464:'Station.DescribeCurrentKey.Entry',0x72DD:'EquipmentListState.KeySize'}
MODIFIED_WRITES=((0x735B,0x72DD,'Station',0x72DC,1,5),)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 for value,name in (('74','Column2X'),('86','Column3X'),('9C','Column4X'),('AE','Column5X')):
  operation=operation.replace('LD A, #'+value,'LD A, @EquipmentListConst.'+name)
 return operation
