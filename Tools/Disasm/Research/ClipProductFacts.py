"""Четыре самостоятельных произведения для изменяемых границ окна."""
FUNCTIONS={0xD8E2:('ComputeTopClipProduct','Произведение (Y1-MinY)*(X1-X2) для верхней границы окна'),
 0xD901:('ComputeBottomClipProduct','Произведение (Y1-MaxY)*(X1-X2) для нижней границы окна'),
 0xD920:('ComputeLeftClipProduct','Произведение (Y1-Y2)*(X1-MinX) для левой границы окна'),
 0xD93F:('ComputeRightClipProduct','Произведение (Y1-Y2)*(X1-MaxX) для правой границы окна')}
DETAILS={0xD8E2:('TopProduct','Y1-MinY','X1-X2'),0xD901:('BottomProduct','Y1-MaxY','X1-X2'),
 0xD920:('LeftProduct','Y1-Y2','X1-MinX'),0xD93F:('RightProduct','Y1-Y2','X1-MaxX')}
DOCUMENTS={('Map',address):('ClipProducts','точный порядок множителей, 32-битная запись и унаследованный случай 8000') for address in FUNCTIONS}
LABELS={}
CONTRACTS={};COMMENTS={}
for address,(field,left,right) in DETAILS.items():
 CONTRACTS['Map',address]=(
  ['MinX, MinY, MaxX, MaxY обозначают изменяемые слова границ, исходно 0, 0, 255, 255',
   'D0C3 записывает четыре байтовых параметра как слова с нулевым старшим байтом',
   'MapClipWork.FirstPoint и SecondPoint содержат два знаковых 16-битных X,Y, ClipCodes не читается',
   'MapClipWork.'+field+' доступен для записи, KARTA выбран, действуют требования MultiplySigned16',
   'входные основные регистры не передают дополнительных аргументов'],
  ['перед умножением HL=('+left+') modulo 65536, DE=('+right+') modulo 65536',
   'HL возвращает старшее слово, DE младшее слово результата MultiplySigned16 с исходным особым случаем',
   'MapClipWork.'+field+'.LowWord получает DE, HighWord получает HL, порядок четырёх байтов младший вперёд',
   'BC, AF и IX соответствуют MultiplySigned16 для указанных операндов и исходного BC последнего вычитания',
   'для TopProduct исходный BC умножения равен MinY, для BottomProduct MaxY, для LeftProduct и RightProduct равен Y2',
   "все альтернативные регистры, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2",
   'исходные точки, ClipCodes и три других произведения не меняются'],
  ['HL, DE, BC, AF, IX по MultiplySigned16'],
  ['настройка и проверенные фазы описаны в [MapRuntimeProfiles](../../Docs/MapRuntimeProfiles.md)',
   'обе разности оборачиваются до 16 бит перед знаковым умножением, широкий знаковый промежуточный результат вычитания не сохраняется',
   'порядок HL и DE существенен, второе DE=8000 и abs(HL)>=256 наследует особенность полного ядра',
   'формула заголовка описывает обычный случай, для исключения берётся фактический договор MultiplySigned16',
   'нулевые исходные экземпляры лежат в ячейках разнесённой таблицы, которые не выбираются допустимыми кодами',
   'это подготовка числителя пересечения, точный последующий договор деления и игровое отсечение описываются отдельно'])
 COMMENTS[address]=(['подготовка первого вычитания для исходного порядка двух множителей'],None)
 COMMENTS[address+(7 if address in (0xD8E2,0xD901) else 6)]=(['очистка Carry перед первым полным 16-битным вычитанием'],None)
 COMMENTS[address+(10 if address in (0xD8E2,0xD901) else 9)]=(['перенос первой разности во второй операнд DE умножения'],None)
 COMMENTS[address+(11 if address in (0xD8E2,0xD901) else 10)]=(['подготовка второго вычитания для первого операнда HL'],None)
 COMMENTS[address+20]=(['вычисление знакового 32-битного результата настоящим MultiplySigned16'],None)
 COMMENTS[address+23]=(['сохранение младшего слова перед старшим в физическом FClipProduct'],None)


def name_operands(region,address,operation):
 if region=='Map' and (address in FUNCTIONS or address in (0xD4DD,0xD95E,0xD9A9,0xD9F4,0xDA52,0xDAB0,0xD48B,0xD1AC)):
  for base,name,fields in ((0xDE2F,'FirstPoint',(('X',0),('Y',2),('ClipCodes',4))),
   (0xDE34,'SecondPoint',(('X',0),('Y',2),('ClipCodes',4))),
   *[(base,name,(('LowWord',0),('HighWord',2))) for base,name in ((0xDE6B,'TopProduct'),(0xDE6F,'BottomProduct'),(0xDE73,'LeftProduct'),(0xDE77,'RightProduct'))]):
   for field,offset in fields:
    operation=operation.replace('(#'+format(base+offset,'04X')+')','(@MapClipWork.'+name+'.'+field+')')
    if field!='ClipCodes':operation=operation.replace('(#'+format(base+offset+1,'04X')+')','(@MapClipWork.'+name+'.'+field+' + 1)')
  if address in FUNCTIONS:
   operation=operation.replace('LD BC, #0000','LD BC, @MapClipConst.MinCoordinate').replace('LD BC, #00FF','LD BC, @MapClipConst.ExcludedEnd')
 return operation
