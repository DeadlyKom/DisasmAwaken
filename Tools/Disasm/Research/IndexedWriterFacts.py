"""Два захватывающих писателя байтов с разной обработкой разрядов результата."""
ENTRIES={0xC685:('PushCargo7BitWriter','ReadCargoField',True),0xC6B6:('PushMarket7BitWriter','ReadMarketField',True),
 0xC6BC:('PushEquipmentWeightWriter','ReadEquipmentWeight',False),0xC6E4:('PushSecondWeightWriter','ReadSecondWeight',False)}
FUNCTIONS={a:(name,'Создание захватывающего писателя '+('семибитового поля' if packed else 'кодированного веса')+' через '+reader) for a,(name,reader,packed) in ENTRIES.items()}
DOCUMENTS={('Text',a):('IndexedWriters','захват адреса и значения, рамка оператора и точный способ сохранения') for a in ENTRIES}
LABELS={('Text',0xC688):'Capture',('Text',0xC695):'Invoke',('Text',0xC6A5):'Store',('Text',0xC6AC):'MaskLow',
 ('Text',0xC6BF):'Capture',('Text',0xC6CB):'Invoke',('Text',0xC6DB):'Store',('Text',0xC6E2):'StoreValue'}
CONTRACTS={}
for address,(name,reader,packed) in ENTRIES.items():
 CONTRACTS['Text',address]=(
  ["HL' указывает на два доступных байта следующего слова выражения, действует входной договор "+reader,
   'результат читателя HL должен быть адресом записываемого целевого байта, полученное значение доступно',
   'до Invoke нельзя создавать другой писатель того же общего шаблона, захваченные операнды общие',
   'Invoke принимает FFieldInvokeFrame и BC правый операнд, оператор возвращает DE через RET в банк LANG 6'],
  ['Entry - HL адрес от читателя, DE общий Invoke, BC от читателя, AF '+('A=E читателя, F сохранён' if packed else 'от читателя'),
   "Entry - HL' увеличен на два, DE' содержит Invoke, BC', AF', IX, IY по договору читателя",
   'Entry обновляет общие операнды Target и InitialValue, само целевое поле не записывает',
   'Invoke передаёт оператору DE захваченное байтовое значение с нулевым D, BC правый операнд',
   'перед входом оператора CPU-стек FIndexedOperatorFrame, сохранены StoreReturn, SavedTarget и AfterStore',
   'Store возвращает HL адрес цели, BC как у оператора, '+('DE с E=127 при D!=0 либо E AND 127 при D=0, D сохранён' if packed else 'DE как у оператора, включая D'),
   'Store - AF '+('A сохранённый байт, F от OR маркера с младшими семью разрядами' if packed else 'A сохранённый байт, F от BIT либо CPL по текущему bit7'),
   'SP после Entry равен входному SP+2, после Invoke либо отдельного Store входному SP+4'],
  ["Entry - HL, DE, BC, AF, HL', DE', BC' только B, AF' и IX по договору читателя",
   'Invoke - HL, DE и регистры по договору оператора',('Store - HL, DE только E, AF' if packed else 'Store - HL, AF')],
  ['целевой адрес и левый операнд захватываются при создании, маркер либо условие инверсии читается из памяти только в Store',
   'Invoke добавляет SavedTarget между StoreReturn и AfterStore, Store снимает этот адрес POP HL',
   ('D!=0 выбирает E=127, но при D=0 значение E>=128 только маскируется, общего насыщения min(result,127) нет' if packed else 'D результата игнорируется, если E>=128, запись может изменить исходный bit7 несмотря на условие инверсии'),
   'игровой смысл маркера и физические единицы веса отдельно не доказаны'])
COMMENTS={
 0xC685:(['получение адреса и текущего байта грузовой записи для захвата'],None),
 0xC688:(['выбор E читателя как захваченного левого операнда, для груза bit7 может остаться'],None),
 0xC689:(['обновление общего операнда Target адресом целевого байта'],None),
 0xC68C:(['обновление общего InitialValue байтом левого операнда'],None),
 0xC68F:(['выбор общего Invoke семибитового писателя'],None),
 0xC695:(['снятие адреса оператора из рамки вызова'],None),
 0xC696:(['чтение захваченного адреса из изменяемого операнда Target'],None),
 0xC699:(['чтение захваченного байтового левого операнда InitialValue'],None),
 0xC69B:(['сохранение Target на CPU-стеке до завершения операции'],None),
 0xC69C:(['выбор Store как аппаратного возврата оператора'],None),
 0xC69F:(['создание шестибайтовой рамки FIndexedOperatorFrame'],None),
 0xC6A0:(['создание DE из захваченного левого байта с нулевым старшим байтом'],None),
 0xC6A3:(['передача адреса оператора в HL и левого значения в DE'],None),
 0xC6A5:(['восстановление Target после RET оператора'],None),
 0xC6A7:(['проверка ненулевого старшего байта результата перед выбором младших семи разрядов'],None),
 0xC6A8:([], 'переход, если D равен нулю, использовать младший E после маскирования'),
 0xC6AA:(['выбор E=127 при любом ненулевом D, старший D не изменяется'],None),
 0xC6AC:(['выбор младших семи разрядов E, значения 128..255 оборачиваются, не насыщаются'],None),
 0xC6B0:(['чтение текущего маркера целевого байта в момент сохранения'],None),
 0xC6B1:(['выделение bit7 для объединения с новым семибитовым значением'],None),
 0xC6B3:(['создание записываемого байта и окончательных флагов'],None),
 0xC6B6:(['получение адреса и значения рынка перед общим захватом семибитового поля'],None),
 0xC6BC:(['получение адреса и декодированного веса оснащения'],None),
 0xC6BF:(['обновление захваченного адреса общего писателя кодированных весов'],None),
 0xC6C2:(['сохранение A читателя как левого операнда веса'],None),
 0xC6C5:(['выбор общего Invoke писателя кодированного веса'],None),
 0xC6CB:(['снятие адреса оператора из рамки вызова писателя веса'],None),
 0xC6CC:(['чтение захваченного адреса целевого веса'],None),
 0xC6CF:(['чтение захваченного левого значения веса'],None),
 0xC6D1:(['сохранение адреса веса для последующего Store'],None),
 0xC6D2:(['выбор Store как возврата оператора веса'],None),
 0xC6D5:(['создание рамки StoreReturn, SavedTarget, AfterStore'],None),
 0xC6D6:(['создание левого DE с нулевым D из захваченного A'],None),
 0xC6D9:(['передача оператору HL адреса и DE левого значения'],None),
 0xC6DB:(['восстановление адреса веса после RET оператора'],None),
 0xC6DC:(['проверка bit7 текущего байта, захваченное прежнее значение тут не используется'],None),
 0xC6DE:(['выбор только младшего E результата, D не участвует в сохранении'],None),
 0xC6DF:([], 'переход, если текущий bit7 цели снят, записать E без инверсии'),
 0xC6E1:(['инверсия младшего E по текущему bit7 цели, старший разряд результата может сменить кодировку'],None),
 0xC6E2:(['запись кодированного веса без отдельного насыщения и без изменения DE'],None),
 0xC6E4:(['получение адреса и декодированного значения второго набора весов'],None)}


def name_operands(region,address,operation):
 if region!='Text' or address not in ENTRIES:return operation
 _,_,packed=ENTRIES[address]
 if packed:
  return operation.replace('#C697','@PackedWriterState.Target').replace('#C69A','@PackedWriterState.InitialValue').replace('#C695','@Text.PushCargo7BitWriter.Invoke').replace('#C6A5','@Text.PushCargo7BitWriter.Store')
 return operation.replace('#C6CD','@EncodedWriterState.Target').replace('#C6D0','@EncodedWriterState.InitialValue').replace('#C6CB','@Text.PushEquipmentWeightWriter.Invoke').replace('#C6DB','@Text.PushEquipmentWeightWriter.Store')
