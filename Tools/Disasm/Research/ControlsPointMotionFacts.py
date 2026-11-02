"""Полная коррекция 35 точек, исходные единичные поправки и ветвь непродвижения сохранены."""
from ControlsPointRespawnFacts import name_operands as respawn_operands

FUNCTIONS = {0xCB00:('UpdateBufferPoints','Последовательная коррекция 35 точек по Y, X и двум табличным коэффициентам')}
CONTINUATIONS = {}
LOCAL = {
    0xCB12:'AdvanceYDown',0xCB1A:'ReplaceYDown',0xCB1E:'YDownModulo',0xCB24:'YDownLimit',
    0xCB2A:'YDownStore',0xCB37:'YDownLimitX',0xCB3D:'YDownStoreX',0xCB48:'YDownKeepX',
    0xCB54:'PrepareYUp',0xCB59:'AdvanceYUp',0xCB61:'ReplaceYUp',0xCB65:'YUpModulo',
    0xCB6B:'YUpLimit',0xCB71:'YUpStore',0xCB80:'YUpLimitX',0xCB86:'YUpStoreX',0xCB91:'YUpKeepX',
    0xCB9A:'BeginXPass',0xCBAC:'AdvanceXRight',0xCBB4:'ReplaceXRight',0xCBB7:'XRightModulo',
    0xCBBD:'XRightLimit',0xCBC3:'XRightStore',0xCBD1:'XRightYLimit',0xCBD7:'XRightStoreY',0xCBE4:'XRightKeepY',
    0xCBF0:'PrepareXLeft',0xCBF5:'AdvanceXLeft',0xCBFD:'ReplaceXLeft',0xCC00:'XLeftModulo',
    0xCC06:'XLeftLimit',0xCC0C:'XLeftStore',0xCC1C:'XLeftYLimit',0xCC22:'XLeftStoreY',0xCC2F:'XLeftKeepY',
    0xCC38:'BeginTurn',0xCC45:'PrepareTurn',0xCC6F:'StoreTurnCalls',0xCC78:'TurnPoint',
    0xCC89:'YCosAbs',0xCC91:'YCosMultiply',0xCCC9:'YCosSignDone',
    0xCCDD:'XSinAbs',0xCCE5:'XSinMultiply',0xCD1D:'SumTurnY',0xCD2F:'ResetYOut',0xCD3F:'KeepTurnY',
    0xCD54:'XCosAbs',0xCD5C:'XCosMultiply',0xCD94:'XCosSignDone',
    0xCDA8:'YNegSinAbs',0xCDB0:'YNegSinMultiply',0xCDE8:'SumTurnX',0xCDFA:'ResetXOut',0xCE09:'StoreTurnPoint'}
for prefix,addresses in (
    ('YCos',(0xCC97,0xCC9D,0xCCA3,0xCCA9,0xCCAF,0xCCB5,0xCCBB)),
    ('XSin',(0xCCEB,0xCCF1,0xCCF7,0xCCFD,0xCD03,0xCD09,0xCD0F)),
    ('XCos',(0xCD62,0xCD68,0xCD6E,0xCD74,0xCD7A,0xCD80,0xCD86)),
    ('YNegSin',(0xCDB6,0xCDBC,0xCDC2,0xCDC8,0xCDCE,0xCDD4,0xCDDA))):
    LOCAL.update({a:prefix+'Shift'+str(index+1) for index,a in enumerate(addresses)})
LABELS = {('Controls',a):name for a,name in LOCAL.items()}
RENAMES = {'Controls.UnknownCB00.Entry':'Controls.UpdateBufferPoints.Entry',
    **{'Controls.UnknownCB00.Point'+format(a,'04X'):'Controls.UpdateBufferPoints.'+name for a,name in LOCAL.items()}}
CONTRACTS = {('Controls',0xCB00):(
    ['HL, DE, BC, AF и альтернативные регистры входных аргументов не задают, регистр R задаёт источник обновляемых выборок',
     'банк 1 выбран, 35 FBufferPoint содержат Y=0..95 и байтовый X, таблица коэффициентов 9900..99FF готова',
     'YControl=9B95, XControl=9B96, TurnControl=9B97 задают три управляющих байта, единицы игрового управления здесь не предполагаются',
     'код, координаты и стек доступны для записи, YWrapOffset, XWrapOffset и оба YOffset возврата точки равны исходному нулю',
     'на CPU-стеке внешний возврат, ещё два байта нужны для CALL, договор не включает вмешательство IRQ'],
    ['при возврате 35 записей последовательно обработаны по Y, X и табличной коррекции, Y остаётся в 0..95, X в 0..255',
     'без третьей фазы HL=C547 при ненулевом XControl либо C501 при нулевом, AF=0054',
     'после третьей фазы HL=C546 и AF=4642, эти значения F не являются кодом успешности игрового действия',
     'DE сохраняется, если не было вызовов RespawnPointIndexPos/Neg, иначе содержит D=X и E=Y последнего такого возврата',
     'B сохраняется кроме пути повторного создания Y при отрицательном YControl, там остаётся последний ограниченный остаток',
     'C содержит последний шаг X или Y, при вызове возврата точки заменён его шагом, без этих операций сохраняется',
     "при TurnControl=0 AF' сохраняется, HL', DE', BC' сохраняются без генератора либо содержат его последний результат",
     "после третьей фазы HL' содержит последнее вычисленное Y либо X до ограничения, DE' последний перекрёстный результат, BC'=0030 либо 0080",
     "AF' после третьей фазы содержит округлённый модуль последнего перекрёстного произведения и флаги INC, формула приведена в документации",
     'IX и IY, I, IM и IFF сохраняются, SP=входной SP+2, R точно соответствует выполненным M1 при отсутствии IRQ'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', координаты, Seed, фазовые байты, операнды коэффициентов и CALL, TurnYStore, два байта CPU-стека, R"],
    ['при трёх нулевых управляющих байтах RAM не записывается, процедура лишь устанавливает выходные регистры',
     'нули Y и крайние X не отбрасываются как пустые элементы, повторное создание зависит от направления и исходных границ',
     'семибитовое произведение всегда содержит единичную поправку, даже нулевой модуль даёт +1 либо -1 по знаковым битам',
     'TurnControl=C0 даёт нулевой шаг возврата, если понадобится пересоздать точку, цикл SUB 0 не вернёт управление',
     'страница 99 содержит исходную синусоиду ACTION, индекс со сдвигом QuarterCycle даёт косинус, байты таблицы сохранены отдельно',
     'модель исполняет настоящие генератор и оба динамических возврата, но не является нативным игровым кадром'])}

COMMENTS = {}
COMMENTS.update({
    0xCB00:(['-----------------------------------------','Обновление Y с повторным созданием точки на границе','-----------------------------------------',
        'выбор первого физического поля Y таблицы ControlsBufferPoints'],None),
    0xCB03:(['чтение YControl, нулевое управление пропускает весь проход Y'],None),
    0xCB06:(['проверка нулевого управления Y перед выбором направления'],None),
    0xCB07:([], 'переход, если YControl равен нулю, продолжить с BeginXPass'),
    0xCB0A:([], 'переход, если YControl имеет установленный бит 7, подготовить движение в PrepareYUp'),
    0xCB0D:(['вычисление шага вниз, (4*YControl+2) AND FF'],None),
    0xCB12:(['вычисление нового Y добавлением шага к текущей координате'],None),
    0xCB14:([], 'переход, если сложение Y со шагом переполнило байт, пересоздать точку в ReplaceYDown'),
    0xCB16:(['проверка верхней границы YUpperLimit после сложения без переноса'],None),
    0xCB18:([], 'переход, если новый Y меньше YUpperLimit, сохранить X через YDownKeepX'),
    0xCB1A:(['получение семибитового R для нового Y после пересечения нижней границы'],None),
    0xCB1E:(['проверка остатка от R относительно шага Y'],None),
    0xCB1F:([], 'переход, если остаток меньше шага Y, продолжить с YDownLimit'),
    0xCB21:(['вычисление остатка повторным вычитанием ненулевого шага'],None),
    0xCB24:(['проверка верхнего ограничения нового остатка значением YUpperLimit-1'],None),
    0xCB26:([], 'переход, если остаток меньше YUpperLimit-1, продолжить с YDownStore без загрузки ограничителя'),
    0xCB2A:(['вычисление нового Y с исходным YWrapOffset и сохранение физического поля Y'],None),
    0xCB2D:(['создание нового X настоящим вызовом NextBufferRandom после пересечения границы Y'],None),
    0xCB31:(['проверка нулевого X после генератора'],None),
    0xCB33:([], 'переход, если X не меньше MinCoordinate, продолжить с YDownLimitX'),
    0xCB37:(['проверка верхнего ограничения XUpperLimit'],None),
    0xCB39:([], 'переход, если X меньше XUpperLimit, продолжить с YDownStoreX без уменьшения'),
    0xCB3D:(['сохранение нового X и переход указателя к следующей записи Y,X'],None),
    0xCB40:(['проверка достижения ByteCount после заполнения всей записи'],None),
    0xCB42:([], 'переход, если младший байт указателя меньше ByteCount, обработать следующую точку в AdvanceYDown'),
    0xCB48:(['сохранение только нового Y, существующий X не изменяется'],None),
    0xCB4C:(['проверка завершения 35 записей в проходе Y'],None),
    0xCB4E:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceYDown'),
    0xCB54:(['вычисление шага вверх с сохранением Carry от NEG в двух RLA, для YControl=80 шаг равен 3'],None),
    0xCB59:(['вычисление нового Y вычитанием шага вверх'],None),
    0xCB5B:([], 'переход, если исходный Y меньше шага, пересоздать точку в ReplaceYUp'),
    0xCB5D:(['проверка минимальной координаты Y после вычитания без заёма'],None),
    0xCB5F:([], 'переход, если новый Y не меньше MinCoordinate, сохранить X через YUpKeepX'),
    0xCB61:(['получение R для повторного создания точки после пересечения верхней границы'],None),
    0xCB65:(['проверка остатка R относительно шага вверх'],None),
    0xCB66:([], 'переход, если остаток меньше шага Y, продолжить с YUpLimit'),
    0xCB68:(['вычисление остатка семибитового R вычитанием шага'],None),
    0xCB6B:(['проверка ограничения остатка значением YUpperLimit-1'],None),
    0xCB6D:([], 'переход, если остаток меньше YUpperLimit-1, продолжить с YUpStore'),
    0xCB71:(['вычисление отражённого Y=YUpperLimit-остаток, B становится рабочим остатком'],None),
    0xCB76:(['создание нового X после выхода Y через верхнюю границу'],None),
    0xCB7A:(['проверка нулевого сгенерированного X'],None),
    0xCB7C:([], 'переход, если X не меньше MinCoordinate, продолжить с YUpLimitX'),
    0xCB80:(['проверка верхнего ограничения нового X'],None),
    0xCB82:([], 'переход, если X меньше XUpperLimit, продолжить с YUpStoreX'),
    0xCB86:(['сохранение нового X и выбор следующего физического поля Y'],None),
    0xCB89:(['проверка завершения таблицы после повторного создания точки'],None),
    0xCB8B:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceYUp'),
    0xCB91:(['сохранение нового Y без изменения X'],None),
    0xCB95:(['проверка завершения прохода вверх по всем записям'],None),
    0xCB97:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceYUp'),
    0xCB9A:(['-----------------------------------------','Обновление X с возможной заменой Y','-----------------------------------------',
        'выбор поля FBufferPoint.X первой записи перед независимым проходом X'],None),
    0xCBA0:(['проверка нулевого XControl перед выбором направления'],None),
    0xCBA1:([], 'переход, если XControl равен нулю, продолжить с BeginTurn'),
    0xCBA4:([], 'переход, если XControl находится в 1..127, подготовить движение в PrepareXLeft'),
    0xCBA7:(['вычисление шага вправо с Carry от NEG, исходный 80 даёт шаг 3'],None),
    0xCBAC:(['вычисление нового X добавлением шага вправо'],None),
    0xCBAE:([], 'переход, если сложение X со шагом переполнило байт, продолжить с ReplaceXRight'),
    0xCBB0:(['проверка верхнего ограничения X после сложения без переноса'],None),
    0xCBB2:([], 'переход, если новый X меньше XUpperLimit, сохранить Y через XRightKeepY'),
    0xCBB4:(['получение нового X через NextBufferRandom после пересечения правой границы'],None),
    0xCBB7:(['проверка остатка сгенерированного байта относительно шага вправо'],None),
    0xCBB8:([], 'переход, если остаток меньше шага X, продолжить с XRightLimit'),
    0xCBBA:(['вычисление остатка повторным вычитанием шага вправо'],None),
    0xCBBD:(['проверка ограничения остатка значением XUpperLimit-1'],None),
    0xCBBF:([], 'переход, если остаток меньше XUpperLimit-1, продолжить с XRightStore'),
    0xCBC3:(['вычисление нового X с исходным XWrapOffset и сохранение поля X'],None),
    0xCBC6:(['получение нового Y из семи младших битов R'],None),
    0xCBCB:(['проверка нулевой вертикальной координаты'],None),
    0xCBCD:([], 'переход, если Y не меньше MinCoordinate, продолжить с XRightYLimit'),
    0xCBD1:(['проверка верхней границы нового Y'],None),
    0xCBD3:([], 'переход, если Y меньше YUpperLimit, продолжить с XRightStoreY без свёртки'),
    0xCBD5:(['свёртка больших семибитовых Y вычитанием YFold, это не остаток по высоте растра'],None),
    0xCBD7:(['сохранение нового Y и выбор поля X следующей записи'],None),
    0xCBDC:(['проверка завершения прохода X после повторного создания точки'],None),
    0xCBDE:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXRight'),
    0xCBE4:(['сохранение нового X без изменения Y'],None),
    0xCBE8:(['проверка завершения прохода вправо'],None),
    0xCBEA:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXRight'),
    0xCBF0:(['вычисление шага влево, (4*XControl+2) AND FF'],None),
    0xCBF5:(['вычисление нового X вычитанием шага влево'],None),
    0xCBF7:([], 'переход, если исходный X меньше шага, продолжить с ReplaceXLeft'),
    0xCBF9:(['проверка минимальной координаты X после вычитания без заёма'],None),
    0xCBFB:([], 'переход, если новый X не меньше MinCoordinate, сохранить Y через XLeftKeepY'),
    0xCBFD:(['получение нового X настоящим вызовом генератора'],None),
    0xCC00:(['проверка остатка сгенерированного байта относительно шага влево'],None),
    0xCC01:([], 'переход, если остаток меньше шага X, продолжить с XLeftLimit'),
    0xCC03:(['вычисление остатка повторным вычитанием шага влево'],None),
    0xCC06:(['проверка ограничения остатка значением XUpperLimit-1'],None),
    0xCC08:([], 'переход, если остаток меньше XUpperLimit-1, продолжить с XLeftStore'),
    0xCC0C:(['вычисление отражённого X=255-остаток, исходные значения 254 и 255 не исключаются повторно'],None),
    0xCC11:(['получение нового семибитового Y после пересоздания X'],None),
    0xCC16:(['проверка нулевого нового Y'],None),
    0xCC18:([], 'переход, если Y не меньше MinCoordinate, продолжить с XLeftYLimit'),
    0xCC1C:(['проверка верхней границы нового Y'],None),
    0xCC1E:([], 'переход, если Y меньше YUpperLimit, продолжить с XLeftStoreY без свёртки'),
    0xCC20:(['свёртка больших значений Y вычитанием YFold'],None),
    0xCC22:(['сохранение нового Y и переход к полю X следующей записи'],None),
    0xCC27:(['проверка завершения таблицы после пересоздания точки'],None),
    0xCC29:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXLeft'),
    0xCC2F:(['сохранение нового X без изменения Y'],None),
    0xCC33:(['проверка завершения прохода влево'],None),
    0xCC35:([], 'переход, если младший байт указателя меньше ByteCount, продолжить AdvanceXLeft')})


COMMENTS.update({
    0xCC38:(['-----------------------------------------','Табличная коррекция относительно CenterX, CenterY','-----------------------------------------',
        'вычисление индекса синусоиды как отрицания TurnControl'],None),
    0xCC3D:(['проверка необходимости третьего прохода'],None),
    0xCC3E:([], 'выход, если TurnControl равен нулю'),
    0xCC40:([], 'переход, если индекс синусоиды неотрицательный, подготовить шаг в PrepareTurn'),
    0xCC43:(['вычисление модуля отрицательного индекса с сохранением Carry от NEG'],None),
    0xCC45:(['вычисление шага возврата точки двумя RLA с исходным Carry, значение C0 управления даёт нулевой шаг'],None),
    0xCC47:(['обновление изменяемого шага обоих входов повторного создания точки'],None),
    0xCC4D:(['поиск синуса по индексу в исходной странице SinePage'],None),
    0xCC50:(['обновление коэффициентов XSinCoeff и YNegSinCoeff противоположными знаками синуса'],None),
    0xCC58:(['вычисление индекса косинуса смещением на QuarterCycle по модулю 256'],None),
    0xCC5D:(['обновление двух операндов косинуса для независимого расчёта Y и X'],None),
    0xCC63:(['восстановление знака индекса для выбора физического входа возврата точки'],None),
    0xCC69:([], 'переход, если индекс синусоиды неотрицательный, сохранить вход RespawnPointIndexPos'),
    0xCC6C:(['выбор входа RespawnPointIndexNeg для отрицательного индекса'],None),
    0xCC6F:(['обновление обоих операндов CALL одним выбранным входом возврата точки'],None),
    0xCC75:(['поиск первой физической записи FBufferPoint перед третьим проходом'],None),
    0xCC78:(['вычисление знакового смещения исходного Y относительно CenterY'],None),
    0xCD1D:(['вычисление нового Y как CenterY плюс два знаковых произведения, единичные поправки сохранены'],None),
    0xCD22:(['проверка старшего байта нового Y, ненулевой байт означает выход из допустимой области'],None),
    0xCD24:([], 'переход, если старший байт нового Y ненулевой, пересоздать точку в ResetYOut'),
    0xCD27:(['проверка нижней границы нового Y'],None),
    0xCD29:([], 'переход, если новый Y меньше MinCoordinate, пересоздать точку в ResetYOut'),
    0xCD2B:(['проверка верхней границы нового Y'],None),
    0xCD2D:([], 'переход, если новый Y меньше YUpperLimit, сохранить его в KeepTurnY'),
    0xCD2F:(['повторное создание точки без расчёта X после недопустимого Y'],None),
    0xCD30:(['вызов входа, выбранного через YRespawnCall, исходный операнд указывает RespawnPointIndexPos'],None),
    0xCD33:(['сохранение X, затем Y возвращённой точки и продвижение к следующей записи'],None),
    0xCD38:(['проверка завершения 35 записей после выхода Y за границы'],None),
    0xCD3B:([], 'переход, если младший байт указателя меньше ByteCount, продолжить с TurnPoint'),
    0xCD3F:(['сохранение допустимого Y в операнде TurnYStore до проверки нового X'],None),
    0xCD43:(['вычисление смещения исходного X относительно CenterX для произведения с косинусом'],None),
    0xCD95:(['вычисление смещения исходного Y относительно CenterY для произведения с отрицательным синусом'],None),
    0xCDE8:(['вычисление нового X как CenterX плюс два знаковых произведения с исходными координатами'],None),
    0xCDED:(['проверка старшего байта нового X'],None),
    0xCDEF:([], 'переход, если старший байт нового X ненулевой, пересоздать точку в ResetXOut'),
    0xCDF2:(['проверка нижней границы нового X'],None),
    0xCDF4:([], 'переход, если новый X меньше MinCoordinate, пересоздать точку в ResetXOut'),
    0xCDF6:(['проверка верхней границы нового X'],None),
    0xCDF8:([], 'переход, если новый X меньше XUpperLimit, сохранить оба результата в StoreTurnPoint'),
    0xCDFA:(['повторное создание обоих полей после недопустимого X, ранее вычисленный Y не используется'],None),
    0xCDFB:(['вызов входа, выбранного через XRespawnCall, исходный операнд указывает RespawnPointIndexPos'],None),
    0xCDFE:(['сохранение Y и X возвращённой точки и продвижение к следующей записи'],None),
    0xCE02:(['проверка завершения таблицы после выхода X за границы'],None),
    0xCE05:([], 'переход, если младший байт указателя меньше ByteCount, продолжить с TurnPoint'),
    0xCE09:(['сохранение отложенного Y и нового X только после успешной проверки обеих координат'],None),
    0xCE0F:(['проверка завершения таблицы после сохранения допустимых координат'],None),
    0xCE12:([], 'переход, если младший байт указателя меньше ByteCount, продолжить с TurnPoint'),
    0xCE15:(['-----------------------------------------'],None)})

# Четыре физически встроенных ядра имеют общий доказанный алгоритм.
for entry,absolute,multiply,shifts,sign_gate,sign_done,coordinate,coefficient in (
    (0xCC7D,0xCC89,0xCC91,(0xCC97,0xCC9D,0xCCA3,0xCCA9,0xCCAF,0xCCB5,0xCCBB),0xCCC1,0xCCC9,'Y-CenterY','YCosCoeff'),
    (0xCCD1,0xCCDD,0xCCE5,(0xCCEB,0xCCF1,0xCCF7,0xCCFD,0xCD03,0xCD09,0xCD0F),0xCD15,0xCD1D,'X-CenterX','XSinCoeff'),
    (0xCD48,0xCD54,0xCD5C,(0xCD62,0xCD68,0xCD6E,0xCD74,0xCD7A,0xCD80,0xCD86),0xCD8C,0xCD94,'X-CenterX','XCosCoeff'),
    (0xCD9C,0xCDA8,0xCDB0,(0xCDB6,0xCDBC,0xCDC2,0xCDC8,0xCDCE,0xCDD4,0xCDDA),0xCDE0,0xCDE8,'Y-CenterY','YNegSinCoeff')):
    COMMENTS[entry]=(['вычисление произведения '+coordinate+' на '+coefficient+' с семибитовым масштабом'],None)
    COMMENTS[entry+2]=(['определение знака произведения по различию знаковых битов двух множителей'],None)
    COMMENTS[entry+5]=(['проверка знакового бита коэффициента перед получением его модуля'],None)
    COMMENTS[entry+6]=([], 'переход, если коэффициент неотрицательный, продолжить с '+LOCAL[absolute])
    COMMENTS[entry+9]=(['вычисление модуля отрицательного коэффициента, байт 80 сохраняет модуль 128'],None)
    COMMENTS[absolute]=(['проверка знака координатного смещения перед умножением модулей'],None)
    COMMENTS[absolute+2]=([], 'переход, если координатное смещение неотрицательное, продолжить с '+LOCAL[multiply])
    COMMENTS[absolute+5]=(['вычисление модуля отрицательного координатного смещения'],None)
    COMMENTS[multiply]=(['вычисление старших семи разрядов произведения последовательным накоплением и сдвигами'],None)
    for bit,target in enumerate(shifts):
        COMMENTS[target-5]=(['проверка разряда '+str(bit)+' модуля коэффициента'],None)
        COMMENTS[target-3]=([], 'переход, если разряд '+str(bit)+' коэффициента нулевой, продолжить с '+LOCAL[target]+' без добавления')
        COMMENTS[target-1]=(['добавление модуля координаты к частичному произведению'],None)
    COMMENTS[shifts[-1]+1]=(['вычисление исходной единичной поправки, модуль результата равен floor(произведение/128)+1'],None)
    COMMENTS[sign_gate]=([], 'переход, если знаковые биты множителей совпадают, продолжить с '+LOCAL[sign_done]+' с положительным результатом')
    COMMENTS[sign_gate+3]=(['вычисление отрицательного 16-битного результата из округлённого модуля'],None)


def name_operands(region,function_address,operation):
    operation = respawn_operands(region,function_address,operation)
    if region=='Controls' and function_address==0xCB00:
        for address,name in ((0x9B95,'YControl'),(0x9B96,'XControl'),(0x9B97,'TurnControl'),
            (0xCC7E,'YCosCoeff'),(0xCCD2,'XSinCoeff'),(0xCD49,'XCosCoeff'),(0xCD9D,'YNegSinCoeff'),
            (0xCD31,'YRespawnCall'),(0xCDFC,'XRespawnCall'),(0xCE0B,'TurnYStore')):
            operation = operation.replace('(#'+format(address,'04X')+')','(@ControlsPointMotionState.'+name+')')
        for before,after in (('#C500','@ControlsBufferPoints.Point00'),
            ('#C501','@ControlsBufferPoints.Point00 + @FBufferPoint.X'),
            ('CP #46','CP @BufferPointConst.ByteCount'),('CP #01','CP @BufferPointConst.MinCoordinate'),
            ('CP #FE','CP @BufferPointConst.XUpperLimit'),('CP #5F','CP @BufferPointConst.YUpperLimit'),
            ('LD A, #5F','LD A, @BufferPointConst.YUpperLimit'),
            ('CP #5E','CP @BufferPointConst.YUpperLimit - 1'),('LD A, #5E','LD A, @BufferPointConst.YUpperLimit - 1'),
            ('CP #FD','CP @BufferPointConst.XUpperLimit - 1'),('LD A, #FD','LD A, @BufferPointConst.XUpperLimit - 1'),
            ('AND #7F','AND @BufferPointConst.YIndexMask'),
            ('SUB #30','SUB @BufferPointMotionConst.CenterY'),('LD BC, #0030','LD BC, @BufferPointMotionConst.CenterY'),
            ('SUB #80','SUB @BufferPointMotionConst.CenterX'),('LD BC, #0080','LD BC, @BufferPointMotionConst.CenterX'),
            ('LD H, #99','LD H, @BufferPointMotionConst.SinePage')):
            operation = operation.replace(before,after)
    if region=='Action' and function_address==0xA85E:
        operation = operation.replace('CALL #CB00','CALL @Controls.UpdateBufferPoints.Entry')
    return operation


def name_instruction(region,function_address,address,operation):
    if region=='Controls' and function_address==0xCB00:
        if address in (0xCBD5,0xCC20):
            operation=operation.replace('SUB #40','SUB @BufferPointConst.YFold')
        if address==0xCC59:
            operation=operation.replace('ADD A, #40','ADD A, @BufferPointMotionConst.QuarterCycle')
        if address==0xCC64:
            operation=operation.replace('SUB #40','SUB @BufferPointMotionConst.QuarterCycle')
    return operation
