"""Четыре полных и кэшированных пересечения, исходная байтовая проекция и флаги курсора."""
ITEMS=((0xE664,'Top',0xE6AF),(0xE6AF,'Bottom',0xE6FA),(0xE6FA,'Left',0xE757),(0xE757,'Right',0xE7B4))
FUNCTIONS={p:('AppendPreviewClip'+name+'Intersection','Пересечение с границей '+name+' и запись исходной байтовой проекции в контур C8') for p,name,_ in ITEMS}
ENDS={p:end for p,_,end in ITEMS}
LABELS={('D3D',p+3):'FromProduct' for p,_,_ in ITEMS}
INTERNAL_ROOTS=tuple(p+3 for p,_,_ in ITEMS)
for p,name,_ in ITEMS:
 if name in ('Top','Bottom'):LABELS['D3D',p+56]='MaxColumn';LABELS['D3D',p+58]='KeepColumn'
 else:LABELS['D3D',p+59]='MinRow';LABELS['D3D',p+76]='StoreLowRow'
DOCUMENTS={('D3D',p):('PreviewClipIntersections','полный и кэшированный входы, однокомплементное деление, насыщение, сохранение младшего байта и точные регистры') for p,_,_ in ITEMS}
CONST_MODULE='PreviewClipIntersectionConst'
CONSTANTS=(('LowRowLimit',192,'исходный исключённый порог младшего байта строки, старший положительный байт здесь не отвергается'),)
DATA_WRITES={0xC22B:(1,'Source/D3D/Data/PreviewContourSize.asm')}
CONTRACTS={}
COMMENTS={}
for p,name,_ in ITEMS:
 horizontal=name in ('Top','Bottom');axis='строк' if horizontal else 'колонок';boundary={'Top':'минимальная строка','Bottom':'максимальная строка','Left':'минимальная колонка','Right':'максимальная колонка'}[name]
 CONTRACTS['D3D',p]=(
  ['HL и DE не являются входами, BC сохраняемый контекст соответствующих ветвей вложенной арифметики',
   'AF полного Entry не задаёт результат, внутренний FromProduct использует входной Carry как будущий Carry альтернативного AF делителя',
   "HL', DE', BC' сохраняются, AF' перезаписывается числителем и делением, IX контекст короткого умножения, IY сохраняется",
   'PreviewClipFirst и PreviewClipSecond содержат слова координат, все граничные операнды подготовлены ConfigurePreviewClip',
   'FromProduct принимает готовый кэш '+name+', полный Entry предварительно вызывает его настоящий производитель',
   'знаковое слово второго минус первого для '+axis+' ненулевое, U<abs(d)*65536 для фактического результата умножителя',
   'ByteCount=N задаёт байтовый курсор C8, под CPU-SP доступны шесть байтов полного Entry либо два кэшированного'],
  ['HL=C800+((N+2) AND FF), DE зависит от ветви проекции, точные формулы в документации',
   'BC от делителя, если числитель отрицателен это его исходное старшее слово, иначе при отрицательном d исходный d',
   'при неотрицательных входах деления BC сохраняется от внешнего FromProduct либо возвращается производителем полного Entry',
   'AF - A новый ByteCount, F от второго INC L, Carry '+('нулевой' if horizontal else 'установлен только при сохранении младшего байта строки'),
   "HL', DE', BC' сохранены, AF' содержит младший байт слова частного и точный F' делителя",
   'IXH от производителя либо входного FromProduct, IXL число отрицательных входов деления минус один по модулю 256, IY сохранён',
   'SP после RET равен входному+2, I, IFF и IM сохранены, координатные записи не меняются',
   'два байта проекции и новый ByteCount записаны, полный Entry также обновляет четыре байта кэша '+name],
  ["HL, DE, BC, AF, AF', IX, два байта C8, ByteCount, кэш полного Entry и вложенный CPU-стек"],
  ['выбранная фиксированная граница '+boundary+', вычисляемая координата '+('колонка' if horizontal else 'строка'),
   'при H=0 колонка сохраняет весь L без сравнения с настроенным максимумом, H<0 выбирает минимум, положительный H максимум' if horizontal else 'при отрицательном H строка насыщается минимумом, иначе L<192 сохраняется даже при ненулевом положительном H',
   'угловые границы не нормализуются, начальный ByteCount может оборачиваться только внутри C8',
   'нулевой знаменатель и переполнение слова частного исключены договором, исходный код проверки не добавляет',
   'возвращаемый Carry характеризует ветвь проекции, окончательный приём контура проверяет внешний диспетчер'])
 COMMENTS[p]=(['полная подготовка кэша '+name+' настоящим производителем перед пересечением'],None)
 COMMENTS[p+3]=(['внутренний вход с готовым кэшем, чтение младшего байта 32-битного числителя'],None)
 COMMENTS[p+6]=(['сохранение младшего байта числителя в A\' вместе с текущим Carry'],None)
 COMMENTS[p+7]=(['чтение следующего байта числителя в основной A'],None)
 COMMENTS[p+10]=(['чтение координат второго и первого конца для знаменателя по оси '+axis],None)
 COMMENTS[p+17]=(['сброс Carry перед обёрнутой разностью знаменателя'],None)
 COMMENTS[p+18]=(['расчёт знаменателя, его S передаётся делителю как знак'],None)
 COMMENTS[p+20]=(['перенос знаменателя в DE без изменения флагов'],None)
 COMMENTS[p+21]=(['чтение старшей половины числителя с сохранением S знаменателя'],None)
 COMMENTS[p+24]=(['деление настоящим EA01, однокомплементный результат не заменяется обычным частным'],None)
 COMMENTS[p+27]=(['чтение исходного начала вычисляемой координаты'],None)
 COMMENTS[p+31]=(['расчёт итогового слова координаты прибавлением начала по модулю 65536'],None)
 COMMENTS[p+32]=(['проверка старшего байта результата для исходного преобразования в байтовый контур'],None)
 if horizontal:
  COMMENTS[p+34]=([], 'переход, если старший байт координаты нулевой, сохранить младшую колонку')
  COMMENTS[p+36]=([], 'переход, если старший байт координаты неотрицателен, выбрать максимум колонки')
  COMMENTS[p+39]=(['чтение курсора для отрицательной координаты, будут записаны минимум колонки и выбранная строка'],None)
  COMMENTS[p+45]=(['запись минимальной колонки из изменяемого операнда MinY'],None)
  COMMENTS[p+47]=(['продвижение к строковому байту в той же странице C8'],None)
  COMMENTS[p+48]=(['запись выбранной граничной строки из настроенного операнда'],None)
  COMMENTS[p+50]=(['расчёт следующего курсора, Carry остаётся нулевым после AND A'],None)
  COMMENTS[p+51]=(['сохранение нового размера без изменения флагов второго INC'],None)
  COMMENTS[p+56]=(['выбор максимальной колонки из изменяемого байтового операнда'],None)
  COMMENTS[p+58]=(['сохранение байтовой колонки в E, D остаётся старшим байтом исходного начала'],None)
  COMMENTS[p+59]=(['чтение курсора для пары с выбранной колонкой'],None)
  COMMENTS[p+65]=(['запись вычисленной либо насыщенной колонки'],None)
  COMMENTS[p+66]=(['продвижение к граничной строке пары'],None)
  COMMENTS[p+67]=(['запись строки границы, исходный операнд обновляется установщиком'],None)
  COMMENTS[p+69]=(['расчёт следующего курсора внутри C8 с Carry=0'],None)
  COMMENTS[p+70]=(['обновление ByteCount с сохранением точных F второго INC'],None)
 else:
  COMMENTS[p+34]=([], 'переход, если старший байт координаты отрицателен, записать минимальную строку')
  COMMENTS[p+37]=(['чтение младшего байта строки, положительный старший байт отдельно не отвергается'],None)
  COMMENTS[p+38]=(['проверка младшего байта относительно постоянного порога 192'],None)
  COMMENTS[p+40]=([], 'переход, если младший байт строки меньше 192, сохранить его без насыщения')
  COMMENTS[p+42]=(['чтение курсора для строки, насыщенной максимумом'],None)
  COMMENTS[p+48]=(['запись выбранной граничной колонки'],None)
  COMMENTS[p+50]=(['продвижение к строковому байту пары'],None)
  COMMENTS[p+51]=(['запись максимальной строки из настроенного операнда'],None)
  COMMENTS[p+53]=(['расчёт следующего курсора после насыщения максимумом, Carry=0'],None)
  COMMENTS[p+54]=(['обновление размера с сохранением флагов второго INC'],None)
  COMMENTS[p+59]=(['чтение курсора для отрицательной строки'],None)
  COMMENTS[p+65]=(['запись выбранной граничной колонки для отрицательного результата'],None)
  COMMENTS[p+67]=(['продвижение к строковому байту без переноса страницы'],None)
  COMMENTS[p+68]=(['запись минимальной строки'],None)
  COMMENTS[p+70]=(['расчёт следующего курсора отрицательной ветви, Carry=0'],None)
  COMMENTS[p+71]=(['обновление ByteCount без изменения F второго INC'],None)
  COMMENTS[p+76]=(['сохранение младшей строки в D, E остаётся младшим байтом исходного начала'],None)
  COMMENTS[p+77]=(['чтение курсора для сохранённого младшего байта строки'],None)
  COMMENTS[p+83]=(['запись выбранной граничной колонки'],None)
  COMMENTS[p+85]=(['продвижение к сохранённой строке, Carry=1 от успешного CP 192'],None)
  COMMENTS[p+86]=(['запись D без повторной проверки положительного старшего байта'],None)
  COMMENTS[p+87]=(['расчёт нового курсора с сохранением Carry=1'],None)
  COMMENTS[p+88]=(['обновление ByteCount и возврат точных F сохранённого младшего байта'],None)


def name_operands(region,address,operation):
 if region!='D3D' or address not in FUNCTIONS:return operation
 data={0xC22B:'PreviewContourSize.Value.ByteCount',0xC22C:'PreviewClipFirst.Value.SecondAxis',0xC22E:'PreviewClipFirst.Value.FirstAxis',0xC23C:'PreviewClipSecond.Value.SecondAxis',0xC23E:'PreviewClipSecond.Value.FirstAxis',0xC2DC:'PreviewClipTopProduct.Value.LowWord',0xC2DD:'PreviewClipTopProduct.Value.LowWord + 1',0xC2DE:'PreviewClipTopProduct.Value.HighWord',0xC2EA:'PreviewClipBottomProduct.Value.LowWord',0xC2EB:'PreviewClipBottomProduct.Value.LowWord + 1',0xC2EC:'PreviewClipBottomProduct.Value.HighWord',0xC2EE:'PreviewClipLeftLow.Value.Word',0xC2EF:'PreviewClipLeftLow.Value.Word + 1',0xC2FA:'PreviewClipLeftHigh.Value.Word',0xC2FC:'PreviewClipRightProduct.Value.LowWord',0xC2FD:'PreviewClipRightProduct.Value.LowWord + 1',0xC2FE:'PreviewClipRightProduct.Value.HighWord'}
 for pointer,label in data.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@'+label+')')
 for p,name,_ in ITEMS:operation=operation.replace('#'+format({'Top':0xE5E8,'Bottom':0xE607,'Left':0xE626,'Right':0xE645}[name],'04X'),'@D3D.BuildPreviewClip'+name+'Product.Entry')
 operation=operation.replace('#EA01','@D3D.DividePreviewClip32To16.Entry')
 for (_,pointer),label in LABELS.items():
  owner=next(name for p,name,end in ITEMS if p<=pointer<end)
  operation=operation.replace('#'+format(pointer,'04X'),'@D3D.AppendPreviewClip'+owner+'Intersection.'+label)
 return operation.replace('LD H, #C8','LD H, @PreviewPolygonConst.PointPage').replace('CP #C0','CP @PreviewClipIntersectionConst.LowRowLimit')
