"""Два доказанных поставщика произведений, естественное продолжение общего входа в D908."""
FUNCTIONS={
 0xD85E:('ProjectPlanarVertexGroup','Произведения плоской группы с прямой второй компонентой и переходом к генератору вершин'),
 0xD8BE:('PreparePreviewVertexProducts','Девять табличных произведений общей матрицы с последовательным продолжением в генератор группы')}
ENDS={0xD85E:0xD896,0xD8BE:0xD908}
DOCUMENTS={('D3D',entry):('PreviewVertexProducts','девять физических операндов, порядок столбцов, точные регистры и переход в генератор') for entry in FUNCTIONS}
LABELS={}
CONTINUATIONS={0xD8BE:0xD908}
ORDERED_INCLUDES={'PreparePreviewVertexProducts':0,'ProjectPreviewVertexGroup':1}
STATE_MODULE='PreviewPlanarProductsState'
STATE={0xD861:'CosFirst',0xD869:'SinFirst',0xD871:'SinSecond',0xD87B:'CosSecond'}
STATE_DESCRIPTIONS={'CosFirst':'операнд косинуса для первого входного параметра','SinFirst':'операнд синуса для третьего входного параметра','SinSecond':'операнд синуса, отрицаемого перед умножением первого параметра','CosSecond':'операнд косинуса для третьей компоненты третьего параметра'}
CONTRACTS={}
for entry in FUNCTIONS:
 CONTRACTS['D3D',entry]=(
  ["DE - D третий байтовый параметр группы, входной E не используется",
   "BC - B первый и C второй байтовые параметры группы, таблица работает с их знаковыми байтовыми значениями",
   "IX - IXL маска комбинаций, бит i выбирает комбинацию i",
   ("девять Coeff11..Coeff33 в PreviewMatrixComposeState содержат исходную композицию сцены и модели" if entry==0xD8BE else "CosFirst, SinFirst, SinSecond, CosSecond содержат четыре байтовых коэффициента плоского входа"),
   "параметры перспективы, NextOffset и выходной буфер подготовлены по договору ProjectPreviewVertexGroup",
   "SP указывает на CPU-возврат, под ним доступны два байта для CALL табличных помощников",
   "банк 4 доступен для записи, прерывания отключены, NMI и повторный вход исключены"],
  ["в девять байтов PackedFirst..PackedThird и DepthFirst..DepthThird записаны произведения по таблице PreviewVertexProducts.md",
   "HL, DE, BC, AF, HL', DE', BC', AF', IX и IY после общего возврата принадлежат точному договору ProjectPreviewVertexGroup",
   "CPU-SP после возврата через генератор равен входному SP+2, исходные два байта адреса возврата сохранены",
   "два байта под входным CPU-SP содержат последний адрес возврата табличного помощника",
   "I, IFF и IM сохраняются, исходные параметры B/C/D и коэффициенты повторно не сохраняются",
   "рабочий буфер и операнды комбинаций обновлены генератором и настоящей перспективой"],
  ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, два байта под CPU-SP, девять произведений и рабочие записи генератора"],
  [("столбцы общей матрицы читаются в физическом порядке 1,3,2, первые две строки упаковываются в слова" if entry==0xD8BE else "параметр C записывается без табличного приближения, четыре отсутствующие компоненты обнуляются"),
   "каждое P является исходной разностью свёрнутых квадратов, не заменяется математическим умножением",
   ("последний LD переходит в ProjectPreviewVertexGroup без настоящего JP, порядок include 0,1 обязателен" if entry==0xD8BE else "последний JP передаёт генератору исходный CPU-возврат без дополнительного CALL"),
   "собственного RET здесь нет, обычный CPU-стек восстанавливает и читает генератор группы",
   "плоский вход вызывается из D819, но включение этого пути в наблюдавшиеся игровые кадры пока не установлено" if entry==0xD85E else "физический обход групп D896 исследуется отдельно от этой композиции"])
COMMENTS={
 0xD85E:(["выбор исходной таблицы квадратов для плоского набора произведений"],None),
 0xD860:(["расчёт P(CosFirst,B), старшая компонента первой упакованной пары"],None),
 0xD868:(["расчёт P(SinFirst,D), старшая компонента третьей упакованной пары"],None),
 0xD870:(["расчёт отрицательного SinSecond до табличного произведения с B"],None),
 0xD87A:(["расчёт P(CosSecond,D), третья компонента третьего параметра"],None),
 0xD882:(["чтение C для прямой второй компоненты без приближённого умножения на 127"],None),
 0xD886:(["обнуление четырёх отсутствующих компонент плоской группы"],None),
 0xD893:(["передача подготовленных произведений генератору с исходным адресом CPU-возврата"],None),
 0xD8BE:(["выбор исходной таблицы квадратов для общей матрицы"],None)}
for address,row in ((0xD8C0,1),(0xD8D8,2),(0xD8F0,3)):
 COMMENTS[address]=(["-----------------------------------------","Произведения строки "+str(row),"-----------------------------------------","расчёт P(Coeff"+str(row)+"1,B), первый параметр группы"],None)
 COMMENTS[address+8]=(["расчёт P(Coeff"+str(row)+"3,C), второй параметр группы"],None)
 COMMENTS[address+16]=(["расчёт P(Coeff"+str(row)+"2,D), третий параметр группы"],None)
STORES={
 0xD865:'PackedFirst старший байт',0xD86D:'PackedThird старший байт',0xD877:'DepthFirst',0xD87F:'DepthThird',
 0xD883:'PackedSecond младший байт',0xD887:'PackedSecond старший байт',0xD88A:'PackedFirst младший байт',0xD88D:'PackedThird младший байт',0xD890:'DepthSecond',
 0xD8C5:'PackedFirst старший байт',0xD8CD:'PackedSecond старший байт',0xD8D5:'PackedThird старший байт',
 0xD8DD:'PackedFirst младший байт',0xD8E5:'PackedSecond младший байт',0xD8ED:'PackedThird младший байт',
 0xD8F5:'DepthFirst',0xD8FD:'DepthSecond',0xD905:'DepthThird'}
for address,meaning in STORES.items():COMMENTS[address]=(["обновление произведения "+meaning+" в операнде генератора"],None)


def name_operands(region,address,operation):
 if region=='D3D' and address in FUNCTIONS:
  from PreviewVertexGroupFacts import STATE as GROUP_STATE
  for pointer,label in ((0xD911,'PackedFirst'),(0xD914,'PackedSecond'),(0xD917,'PackedThird')):operation=operation.replace('(#'+format(pointer,'04X')+')','(@PreviewVertexGroupState.'+label+'+#01)')
  for pointer,label in GROUP_STATE.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@PreviewVertexGroupState.'+label+')')
  for pointer,register in ((0xD525,'B'),(0xD532,'C'),(0xD53F,'D')):operation=operation.replace('CALL #'+format(pointer,'04X'),'CALL @D3D.LookupPreviewProduct'+register+'.Entry')
  operation=operation.replace('LD H, #C3','LD H, @PreviewModelMatrixConst.ProductPage').replace('JP #D908','JP @D3D.ProjectPreviewVertexGroup.Entry')
 return operation
