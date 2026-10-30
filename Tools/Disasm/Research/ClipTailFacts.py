"""Доказанные договоры двенадцати общих помощников исходного отсечения."""
FUNCTIONS={0xDAB0:('AppendTopLeftCorner','Условное добавление верхнего левого угла окна'),
 0xDABB:('AppendTopRightCorner','Условное добавление верхнего правого угла окна'),
 0xDAC6:('AppendBottomLeftCorner','Условное добавление нижнего левого угла окна'),
 0xDAD1:('AppendBottomRightCorner','Условное добавление нижнего правого угла окна'),
 0xDADC:('SubtractTopLeftProducts','Старшее слово и флаги 32-битной разности верхнего и левого произведений'),
 0xDAF0:('SubtractTopRightProducts','Старшее слово и флаги 32-битной разности верхнего и правого произведений'),
 0xDB04:('SubtractBottomLeftProducts','Старшее слово и флаги 32-битной разности нижнего и левого произведений'),
 0xDB18:('SubtractBottomRightProducts','Старшее слово и флаги 32-битной разности нижнего и правого произведений'),
 0xDB2C:('SubtractClipPointX','Знаковые флаги оборачиваемой разности X2-X1'),
 0xDB37:('SubtractClipPointY','Знаковые флаги оборачиваемой разности Y2-Y1'),
 0xDB42:('AppendSecondClipPoint','Добавление младших байтов второй точки либо пары из DE'),
 0xDB59:('UnwindClipFrame','Специальный возврат со снятием трёх слов и установленным Carry')}
DOCUMENTS={('Map',address):('ClipTail','самостоятельные входы, точные флаги, байтовый курсор и специальный стековый кадр') for address in FUNCTIONS}
LABELS={('Map',0xDB4A):'FromDE'}
CONTRACTS={};COMMENTS={}
for address,pair in ((0xDAB0,(0,0)),(0xDABB,(255,0)),(0xDAC6,(0,255)),(0xDAD1,(255,255))):
 CONTRACTS['Map',address]=(
  ['пара угла находится в изменяемом LD DE, исходно Min=0, Max=255, после D0C3 равна параметрам окна',
   'MapClipState.CornerBlock по DE3A разрешает углы только при нуле, ненулевое значение блокирует запись',
   'MapClipWork.OutputSize содержит байтовое смещение в MapClipState.Output, страница F9 доступна для записи'],
  ['при CornerBlock!=0 основные HL, DE, BC сохранены, A=CornerBlock, F соответствует AND A, Carry=0',
   'при CornerBlock=0 добавлена пара X='+('MaxX' if pair[0] else 'MinX')+', Y='+('MaxY' if pair[1] else 'MinY')+' через AppendSecondClipPoint.FromDE',
   'после добавления DE содержит эту пару, HL=F900|новый OutputSize, A=новый OutputSize',
   'F соответствует второму INC L, Carry=0, обновление размера оборачивается по модулю 256',
   "BC, альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2"],
  ['HL, DE, AF при записи, AF при блокировке'],
  ['MinX, MinY, MaxX, MaxY описывают операнды, [обе фазы исполнения](../../Docs/MapRuntimeProfiles.md) проверены отдельно',
   'процедура не устанавливает и не сбрасывает CornerBlock, смысл всех внешних фаз его заполнения ещё разбирается'])
 COMMENTS[address]=(['проверка разрешения добавлять угол в текущей фазе отсечения'],None)
 COMMENTS[address+4]=([], 'выход, если CornerBlock ненулевой, выходной список не менять')
 COMMENTS[address+5]=(['подготовка изменяемой пары X,Y этого угла в E,D'],None)
 COMMENTS[address+8]=(['продолжение в общем писателе двух байтов без нового адреса возврата'],None)
for address,left,right in ((0xDADC,'TopProduct','LeftProduct'),(0xDAF0,'TopProduct','RightProduct'),
 (0xDB04,'BottomProduct','LeftProduct'),(0xDB18,'BottomProduct','RightProduct')):
 CONTRACTS['Map',address]=(
  ['MapClipWork.'+left+' и '+right+' содержат два 32-битных произведения с младшим словом вперёд'],
  ['HL=high('+left+')-high('+right+')-заём из low('+left+')-low('+right+'), modulo 65536',
   'BC=high('+right+'), AF сохраняет A и получает флаги последнего SBC HL,BC с этим заёмом',
   'S отражает бит 31 оборачиваемой разности, Carry полный 32-битный беззнаковый заём',
   'Z проверяет только старшее слово разности после заёма, младшее слово в результат Z не входит',
   "DE, альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2"],
  ['HL, BC, F'],
  ['произведения не меняются, входной Carry очищается OR A перед младшим словом',
   'S без учёта P/V не заменяет математическое знаковое сравнение при переполнении'])
 COMMENTS[address]=(['подготовка младших слов для получения заёма в старшее слово разности'],None)
 COMMENTS[address+10]=(['подготовка старших слов с сохранением заёма от младшего SBC'],None)
for address,axis in ((0xDB2C,'X'),(0xDB37,'Y')):
 CONTRACTS['Map',address]=(
  ['MapClipWork.FirstPoint.'+axis+' и SecondPoint.'+axis+' содержат исходные 16-битные координаты'],
  ['HL=SecondPoint.'+axis+'-FirstPoint.'+axis+' modulo 65536, DE=FirstPoint.'+axis,
   'AF сохраняет A и получает точные флаги SBC HL,DE при исходном Carry=0',
   "BC, альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2"],
  ['HL, DE, F'],['поля точек не меняются, S сам по себе не учитывает переполнение знаковой разности'])
 COMMENTS[address]=(['расчёт оборачиваемой разности второй и первой координат '+axis+' для условий обработчика'],None)
CONTRACTS['Map',0xDB42]=(
 ['Entry читает младшие X,Y из MapClipWork.SecondPoint, старшие координат и ClipCodes игнорируются',
  'FromDE принимает E=X, D=Y, MapClipWork.OutputSize задаёт байтовое смещение в странице MapClipState.Output'],
 ['Output[старый Size]=E, Output[(старый Size+1)&255]=D, OutputSize=(старый Size+2)&255',
  'HL=F900|новый OutputSize, DE содержит записанную пару, BC сохранён',
  'A=новый OutputSize, F соответствует последнему INC L, входной Carry сохраняется',
  "альтернативные регистры, IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2"],
 ['HL, DE у Entry, AF'],
 ['проверки ёмкости и кодов отсечения нет, переход L=FF к 00 остаётся в той же странице F9',
  'FromDE является самостоятельным публичным входом, углы используют именно его'])
COMMENTS.update({0xDB42:(['чтение младшего X второй точки для выхода без масштабирования'],None),
 0xDB46:(['чтение младшего Y второй точки, старший байт намеренно не учитывается'],None),
 0xDB4A:(['поиск адреса следующей двухбайтовой выходной записи по байтовому OutputSize'],None),
 0xDB50:(['запись X и Y с отдельным оборачиванием L внутри страницы F9'],None),
 0xDB54:(['расчёт следующего байтового размера после записи пары'],None),
 0xDB55:(['обновление физического OutputSize, Carry не изменяется'],None)})
CONTRACTS['Map',0xDB59]=(
 ['SP указывает на FClipUnwindFrame, последовательно три снимаемых слова и настоящий адрес возврата',
  'FirstWord передаёт A своим старшим байтом, SecondWord передаёт счётчик своим старшим байтом',
  'ThirdWord является базой для возвращаемого HL, это описание фактического кадра без подмены обычным CALL'],
 ['A=high(FirstWord), BC=(high(SecondWord)-1)&255, HL=(ThirdWord+BC)&65535',
  'Carry=1, S/Z/PV соответствуют DEC старшего байта SecondWord, H=N=0, биты 5 и 3 взяты из A',
  'управление передано по ReturnAddress, SP=входной SP+8',
  "DE, альтернативные регистры, IX, IY, I и IFF сохранены"],
 ['HL, BC, AF, SP'],
 ['первые три слова намеренно удаляются, они не являются тремя обычными адресами CALL этой процедуры',
  'владелец группового кадра и геометрическая причина этого выхода описываются вместе с обработчиками'])
COMMENTS.update({0xDB59:(['снятие первого слова специального кадра, его старший байт становится возвращаемым A'],None),
 0xDB5A:(['снятие второго слова, старший байт задаёт оборачиваемое смещение минус один'],None),
 0xDB5B:(['снятие третьего слова как базы возвращаемого HL'],None),
 0xDB5D:(['расчёт байтового смещения из старшего байта второго снятого слова'],None),
 0xDB60:(['расчёт нового HL с нулевым старшим байтом смещения'],None),
 0xDB61:(['установка специального выходного Carry после вычисления HL'],None)})


def name_operands(region,address,operation):
 if region=='Map' and address in FUNCTIONS:
  operation=operation.replace('(#DE3A)','(@MapClipState.CornerBlock)').replace('(#DE3B)','(@MapClipWork.OutputSize)').replace('LD H, #F9','LD H, @MapClipConst.OutputPage')
  for base,name,fields in ((0xDE2F,'FirstPoint',(('X',0),('Y',2))), (0xDE34,'SecondPoint',(('X',0),('Y',2))),
   *[(base,name,(('LowWord',0),('HighWord',2))) for base,name in ((0xDE6B,'TopProduct'),(0xDE6F,'BottomProduct'),(0xDE73,'LeftProduct'),(0xDE77,'RightProduct'))]):
   for field,offset in fields:operation=operation.replace('(#'+format(base+offset,'04X')+')','(@MapClipWork.'+name+'.'+field+')')
 return operation
