"""Четыре исходных ветви ребра DE1C..DF45, точные параметры и изменяемые opcode."""
FUNCTIONS={0xDE1C:('RasterizePreviewEdge','Растровое ребро с исключённым концом, четырьмя ветвями, режимами XOR/OR/AND и точными флагами')}
ENDS={0xDE1C:0xDF46}
DOCUMENTS={('D3D',0xDE1C):('PreviewEdgeRaster','формула точек, физические параметры, четыре ветви, режимы, точные регистры и проверка bitmap')}
LABELS={('D3D',p):n for p,n in (
 (0xDE2F,'RowsReady'),(0xDE33,'MaskIndex'),(0xDE65,'LeftFlatLoop'),(0xDE66,'LeftFlatOp'),(0xDE69,'LeftFlatJump'),
 (0xDE6B,'LeftFlatError'),(0xDE74,'LeftFlatByte'),(0xDE7A,'LeftFlatRow'),(0xDE8E,'LeftFlatRead'),
 (0xDE92,'LeftSteep'),(0xDEA4,'LeftSteepLoop'),(0xDEA5,'LeftSteepOp'),(0xDEB8,'LeftSteepError'),(0xDEBF,'LeftSteepJump'),(0xDEC1,'LeftSteepNext'),(0xDEC5,'LeftSteepByte'),
 (0xDECA,'Right'),(0xDEE1,'RightFlatLoop'),(0xDEE2,'RightFlatOp'),(0xDEE5,'RightFlatJump'),(0xDEE7,'RightFlatError'),(0xDEF0,'RightFlatByte'),(0xDEF6,'RightFlatRow'),(0xDF0A,'RightFlatRead'),
 (0xDF0E,'RightSteep'),(0xDF20,'RightSteepLoop'),(0xDF21,'RightSteepOp'),(0xDF34,'RightSteepError'),(0xDF3B,'RightSteepJump'),(0xDF3D,'RightSteepNext'),(0xDF41,'RightSteepByte'))}
STATE_MODULE='PreviewEdgeRasterState'
STATE={0xDE34:'MaskOffset'}
OPCODE_TARGETS={}
for op,jump,name in ((0xDE66,0xDE69,'LeftFlat'),(0xDEA5,0xDEBF,'LeftSteep'),(0xDEE2,0xDEE5,'RightFlat'),(0xDF21,0xDF3B,'RightSteep')):
 STATE[op]=name+'Op';STATE[jump]=name+'Jump';OPCODE_TARGETS[op]=0;OPCODE_TARGETS[jump]=0x38
STATE_DESCRIPTIONS={name:('операнд младшего адреса таблицы масок, B0 либо B8' if name=='MaskOffset' else 'изменяемый opcode пиксельной операции ветви '+name[:-2] if name.endswith('Op') else 'изменяемый opcode границы байта ветви '+name[:-4]) for name in STATE.values()}
CONST_MODULE='PreviewEdgeRasterConst'
CONSTANTS=(('MaskPage',0xCD,'старший байт исходных таблиц PreviewPixelMasks'),('RowHighPage',0xC9,'старший байт страницы PreviewLineTable.RowHigh'))
CONTRACTS={('D3D',0xDE1C):(
 ["PreviewEdgeEndpoints.Value.StartPoint и EndPoint содержат слова, младший байт колонка, старший строка",
  "PreviewEdgeMode.Value содержит согласованную пару A9/38 для XOR, B1/38 для OR либо A1/30 для AND",
  "MaskOffset содержит B0 для XOR и OR, B8 для AND, исходные таблицы масок сохранены",
  "PreviewLineTable.RowHigh, RowLow и Column подготовлены BuildSpriteLineTable в текущем банке 4",
  "профиль требует попадания обоих концов и всех точек в bitmap 256 на 192 после добавления начала таблиц",
  "CPU-стек не пересекает экран и изменяемый код, повторный вход в общий код opcode исключён",
  "HL, DE, BC, AF не задают координаты, их входной контекст сохраняется только в указанных случаях раннего выхода"],
 ["для разных концов HL содержит адрес исключённого конца, DE содержит D=max(dx,dy), E=min(dx,dy), BC содержит B=0 и C маску конца",
  "C является одноразрядной маской для XOR и OR либо её инверсией для AND",
  "AF пологой ветви содержит A равный конечному экранному байту, F от последнего поворота маски, смены колонки либо строки",
  "AF крутой ветви принадлежит расчёту последнего перехода строки, A не является возвращаемым пикселем",
  "AF' содержит A'=floor(max(dx,dy)/2), F' точного последнего действия накопителя ошибки, маски либо колонки",
  "полные формулы AF и AF' приведены в registers, row_context, column_context независимой модели",
  "HL', DE', BC', IX, IY, I, IFF и IM сохраняются, SP после RET равен входному+2, CPU-стек не записывается",
  "при совпавших словах концов HL=0, DE равен слову конца, BC, A и весь альтернативный набор сохранены, F=42",
  "при непустом ребре меняются два opcode выбранной ветви и экранные байты, при совпавших концах записей нет"],
 ["HL, DE, BC, AF, AF', два opcode выбранной ветви, затронутые экранные байты"],
 ["при разных строках начало выбирается по меньшей строке, при равных строках исходный порядок концов сохраняется",
  "начальная точка включена, конечная исключена, равенство dx и dy выбирает пологую ветвь",
  "пологая ветвь накапливает несколько пикселей байта в A и может повторно записывать неизменённый соседний байт",
  "AND использует инверсную маску и заменяет исходный JR C на JR NC, оба изменяемых байта необходимы",
  "не выровненное горизонтальное начало таблиц округляется вниз до байтовой колонки, остаток не добавляется в маску",
  "сам код отсечения не выполняет, внеэкранные таблицы и неподготовленные opcode не входят в проверенный профиль",
  "проверка включает настоящую подготовку таблиц, весь bitmap и точные основные и альтернативные AF, не аппаратные IRQ"])}
COMMENTS={
 0xDE1C:(["-----------------------------------------","Концы и нормализация строк","-----------------------------------------","чтение двух физических слов концов отрезка"],None),
 0xDE23:(["очистка Carry перед сравнением полных координатных слов"],None),
 0xDE24:(["проверка полного совпадения концов без рисования одной точки"],None),
 0xDE26:([],"выход, если координатные слова совпадают, отрезок не рисуется"),
 0xDE27:(["восстановление первого слова после сравнения"],None),
 0xDE28:(["расчёт разности строк для выбора начала с меньшей строкой"],None),
 0xDE2A:([],"переход, если строка второго конца не меньше первой, перестановка не нужна"),
 0xDE2C:(["перестановка концов и расчёт модуля разности строк"],None),
 0xDE2F:(["сохранение длины по строкам, колонка конца остаётся в E"],None),
 0xDE30:(["расчёт индекса пиксельного бита начала внутри экранного байта"],None),
 0xDE33:(["добавление подготовленного B0 либо B8 к индексу маски"],None),
 0xDE36:(["расчёт полного адреса исходной маски с переносом младшей суммы"],None),
 0xDE3B:(["чтение выбранной маски и временное сохранение её в AF'"],None),
 0xDE3D:(["-----------------------------------------","Экранный адрес начала","-----------------------------------------","сохранение относительной колонки и выбор строки таблиц"],None),
 0xDE41:(["чтение старшего и младшего байтов адреса строки"],None),
 0xDE46:(["расчёт младшего экранного адреса добавлением байтовой колонки"],None),
 0xDE49:(["перенос маски в C с восстановлением относительной начальной колонки в A"],None),
 0xDE4D:(["расчёт разности начальной и конечной колонок"],None),
 0xDE4E:([],"переход, если начальная колонка меньше конечной, рисовать вправо"),
 0xDE50:(["проверка выбора главной оси для движения влево"],None),
 0xDE51:([],"переход, если длина по колонкам меньше длины по строкам, выбрать крутую ветвь"),
 0xDE53:(["-----------------------------------------","Пологая ветвь влево","-----------------------------------------","сохранение главной длины в D и B, малой длины в E"],None),
 0xDE56:(["расчёт начальной ошибки как половины главной длины с округлением вниз"],None),
 0xDE58:(["сохранение накопителя ошибки в альтернативном AF"],None),
 0xDE92:(["-----------------------------------------","Крутая ветвь влево","-----------------------------------------","сохранение малой длины по колонкам и главной длины по строкам"],None),
 0xDE95:(["расчёт начальной половины главной длины для ошибки"],None),
 0xDECA:(["-----------------------------------------","Выбор ветви вправо","-----------------------------------------","расчёт модуля отрицательной разности колонок"],None),
 0xDECC:(["проверка главной оси для движения вправо"],None),
 0xDECD:([],"переход, если длина по колонкам меньше длины по строкам, выбрать крутую ветвь"),
 0xDECF:(["сохранение главной и малой длин пологого ребра вправо"],None),
 0xDED2:(["расчёт начальной половины главной длины"],None),
 0xDF0E:(["-----------------------------------------","Крутая ветвь вправо","-----------------------------------------","сохранение главной и малой длин крутого ребра вправо"],None),
 0xDF11:(["расчёт начальной половины главной длины"],None)}
for load,write_op,read_branch,write_branch in ((0xDE59,0xDE5C,0xDE5F,0xDE62),(0xDE98,0xDE9B,0xDE9E,0xDEA1),(0xDED5,0xDED8,0xDEDB,0xDEDE),(0xDF14,0xDF17,0xDF1A,0xDF1D)):
 COMMENTS[load]=(["чтение байта пиксельной операции из физического экземпляра режима"],None)
 COMMENTS[write_op]=(["обновление opcode NOP выбранной ветви на подготовленный AND, XOR либо OR"],None)
 COMMENTS[read_branch]=(["чтение opcode перехода по границе байта, C для прямой маски, NC для инверсной"],None)
 COMMENTS[write_branch]=(["обновление opcode условного перехода без изменения его смещения"],None)
for op,rotate,jump in ((0xDE66,0xDE67,0xDE69),(0xDEE2,0xDEE3,0xDEE5)):
 COMMENTS[op]=(["пиксельная операция над накопленным байтом, исходный NOP заменяется выбранной ветвью"],None)
 COMMENTS[rotate]=(["циклическое продвижение маски на одну колонку в выбранном направлении"],None)
 COMMENTS[jump]=(["исходный JR C в режиме AND меняется на JR NC, направление границы связано с инверсией маски"],"переход, если Carry установлен, перейти к соседнему экранному байту")
for error,branch,row,restore in ((0xDE6B,0xDE6D,0xDE7A,0xDE6F),(0xDEE7,0xDEE9,0xDEF6,0xDEEB)):
 COMMENTS[error]=(["выбор накопителя ошибки вместо текущего экранного байта"],None)
 COMMENTS[error+1]=(["вычитание малой длины из ошибки пологой ветви"],None)
 COMMENTS[branch]=([],"переход, если ошибка дала заём, продвинуть строку")
 COMMENTS[row]=(["восстановление ошибки добавлением главной длины после заёма"],None)
 COMMENTS[restore]=(["восстановление экранного байта после шага без смены строки"],None)
for store,step,read in ((0xDE74,0xDE75,0xDE76),(0xDEF0,0xDEF1,0xDEF2)):
 COMMENTS[store]=(["запись накопленного байта перед переходом границы колонки"],None)
 COMMENTS[step]=(["переход к соседнему байту без переноса младшего адреса в H"],None)
 COMMENTS[read]=(["чтение нового байта для последующего накопления пикселей"],None)
for op,store,error,branch,add,rotate,jump,swap,byte in (
 (0xDEA5,0xDEA6,0xDEB8,0xDEBA,0xDEBC,0xDEBD,0xDEBF,0xDEC1,0xDEC5),
 (0xDF21,0xDF22,0xDF34,0xDF36,0xDF38,0xDF39,0xDF3B,0xDF3D,0xDF41)):
 COMMENTS[op]=(["пиксельная операция текущей строки, исходный NOP заранее заменён рабочим opcode"],None)
 COMMENTS[store]=(["запись изменённого байта перед обязательным продвижением строки"],None)
 COMMENTS[error]=(["выбор накопителя ошибки после продвижения экранной строки"],None)
 COMMENTS[error+1]=(["вычитание малой длины для решения о сдвиге колонки"],None)
 COMMENTS[branch]=([],"переход, если ошибка не дала заёма, колонку не менять")
 COMMENTS[add]=(["восстановление ошибки добавлением главной длины"],None)
 COMMENTS[rotate]=(["сдвиг маски на следующую колонку после заёма ошибки"],None)
 COMMENTS[jump]=(["режим AND заменяет исходный JR C на JR NC"],"переход, если Carry установлен, изменить байтовую колонку")
 COMMENTS[swap]=(["восстановление рабочего AF после решения по колонке"],None)
 COMMENTS[byte]=(["изменение байтовой колонки на единицу при переходе пиксельного бита через край"],None)
for inc,load,and_op,branch,low,add,carry,high,sub,ready in (
 (0xDE7D,0xDE7E,0xDE7F,0xDE81,0xDE84,0xDE85,0xDE88,0xDE8A,0xDE8B,0xDE8E),
 (0xDEA7,0xDEA8,0xDEA9,0xDEAB,0xDEAE,0xDEAF,0xDEB2,0xDEB4,0xDEB5,0xDEB8),
 (0xDEF9,0xDEFA,0xDEFB,0xDEFD,0xDF00,0xDF01,0xDF04,0xDF06,0xDF07,0xDF0A),
 (0xDF23,0xDF24,0xDF25,0xDF27,0xDF2A,0xDF2B,0xDF2E,0xDF30,0xDF31,0xDF34)):
 COMMENTS[inc]=(["продвижение старшего адресного байта на следующую пиксельную строку ULA"],None)
 COMMENTS[and_op]=(["проверка остатка строки внутри восьмистрочного знакоместа"],None)
 COMMENTS[branch]=([],"переход, если граница восьми строк не достигнута, адрес строки готов")
 COMMENTS[low]=(["расчёт следующей строки знакомест через младший адрес"],None)
 COMMENTS[add]=(["добавление 32 байтов к младшему экранному адресу"],None)
 COMMENTS[carry]=([],"переход, если младший адрес переполнился, переход в следующую часть экрана уже готов")
 COMMENTS[high]=(["коррекция старшего адреса внутри текущей части экрана"],None)
 COMMENTS[sub]=(["вычитание восьми старших адресных шагов после границы знакоместа"],None)


def name_operands(region,address,operation):
 if region=='D3D' and address==0xDE1C:
  for pointer,label in ((0xC24B,'PreviewEdgeEndpoints.Value.StartPoint'),(0xC24D,'PreviewEdgeEndpoints.Value.EndPoint'),(0xC26F,'PreviewEdgeMode.Value.PixelOpcode'),(0xC270,'PreviewEdgeMode.Value.BoundaryOpcode')):
   operation=operation.replace('(#'+format(pointer,'04X')+')','(@'+label+')')
  for pointer,label in STATE.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@PreviewEdgeRasterState.'+label+')')
  for (_,pointer),label in LABELS.items():operation=operation.replace('#'+format(pointer,'04X'),'@D3D.RasterizePreviewEdge.'+label)
  operation=operation.replace('AND #07','AND @ScreenConst.PixelOffsetMask').replace('ADD A, #20','ADD A, @ScreenConst.ByteColumns').replace('SUB #08','SUB @ScreenConst.PixelsPerChar')
  operation=operation.replace('LD A, #CD','LD A, @PreviewEdgeRasterConst.MaskPage').replace('LD H, #C9','LD H, @PreviewEdgeRasterConst.RowHighPage')
 return operation
