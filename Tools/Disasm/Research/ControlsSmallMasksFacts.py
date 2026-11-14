"""Подготовка строковых масок по радиусу 2..8, обе ветви и повторная запись первой строки."""
FUNCTIONS = {0xD9B0:('BuildSmallBodyMasks','Подготовка строковых масок малой фигуры из упакованной затравки радиуса')}
LOCAL = {0xD9BD:'SelectSeed',0xD9C8:'ShiftMask',0xD9CF:'RepeatMask'}
LABELS = {('Controls',address):name for address,name in LOCAL.items()}
RENAMES = {'Controls.UnknownD9B0.Entry':'Controls.BuildSmallBodyMasks.Entry',
    **{'Controls.UnknownD9B0.Point'+format(a,'04X'):'Controls.BuildSmallBodyMasks.'+name for a,name in LOCAL.items()}}
CONTINUATIONS = {}
CONTRACTS = {('Controls',0xD9B0):(
    ['HL и DE входных аргументов не задают, BC задаёт сохраняемый C, AF задаёт A=2..8 как радиус',
     "AF' задаёт A'=0 для Primary либо ненулевой A' для Alternate, исходный F сохраняется в альтернативном AF",
     'банк 1 выбран, исходные затравки сохранены, Row00..Row0B доступны для записи',
     'на CPU-стеке внешний возврат, дополнительный стек не используется, IRQ не вмешиваются'],
    ['HL указывает AlternateR0+радиус, DE содержит D=0 и E=радиус, BC содержит B=0 и исходный C',
     'A=Packed альтернативной затравки AND PixelsMask, F соответствует AND A с H=1, N=0 и Carry=0',
     "HL', DE', BC' сохраняются, AF' содержит исходный входной AF, IX и IY, I, IM и IFF сохраняются",
     'SP=входной SP+2, R получает 20+[исходный селектор ненулевой]+5*t+3*радиус M1, t=Packed AND CountMask',
     'сначала записаны t арифметически сдвигаемых масок и радиус копий последней, затем Row00 повторно заменена альтернативной маской'],
    ["HL, DE, B, AF, AF', t+радиус байтов Row00..Row0B, R"],
    ['для исходных радиусов 2..8 t=floor(радиус/2), максимум записывается 12 разных байтов и 13 записей с повтором Row00',
     'SRA сохраняет знаковый разряд маски, замена на SRL меняет исходные формы',
     'альтернативная маска Row00 загружается независимо от выбранной затравки основной части',
     'радиусы 0 и 1 вне договора, при B=0 цикл выходит за LA8FA и перекрывает код построителя',
     '20 байтов после Row0B завершают исходный резерв LA8FA, штатные радиусы их не изменяют',
     "DrawSmallBody отсекает радиусы вне 2..8 до вызова, A' выбирает затравку после входа D9DE либо D9DF"])}
COMMENTS = {
    0xD9B0:(['сохранение радиуса в E для индексации затравок и длины повторяемой части'],None),
    0xD9B3:(['выбор базы Primary до проверки альтернативного селектора'],None),
    0xD9B6:(['сохранение исходного радиуса и F в альтернативном AF, получение селектора из A\''],None),
    0xD9B7:(['проверка нулевого селектора для выбора затравки'],None),
    0xD9B8:([], 'переход, если селектор равен нулю, использовать Primary через SelectSeed'),
    0xD9BA:(['выбор базы Alternate для любого ненулевого селектора'],None),
    0xD9BD:(['поиск упакованной затравки с исходным радиусом'],None),
    0xD9BE:(['выделение числового количества сдвигов из разрядов 2..0 Packed'],None),
    0xD9C2:(['выделение начальной пиксельной маски из разрядов 7..3 Packed'],None),
    0xD9C8:(['создание последовательности строк арифметическим сдвигом маски, бит 7 сохраняется'],None),
    0xD9CE:(['подготовка числа повторов последней сдвинутой маски по исходному радиусу'],None),
    0xD9CF:(['заполнение продолжающей части неизменной сдвинутой маской'],None),
    0xD9D3:(['поиск альтернативной затравки для обязательной замены Row00 независимо от первого выбора'],None),
    0xD9D8:(['выделение пиксельной части альтернативной затравки, эти F возвращаются вызывающему'],None),
    0xD9DA:(['повторное обновление Row00 альтернативной маской после построения остальных строк'],None)}


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address==0xD9B0:
        operation=operation.replace('#D97E','@ControlsSmallMaskSeeds.PrimaryR0')
        operation=operation.replace('#D987','@ControlsSmallMaskSeeds.AlternateR0')
        operation=operation.replace('#D990','@ControlsSmallMaskRows.Row00')
        operation=operation.replace('AND #07','AND @SmallMaskConst.CountMask')
        operation=operation.replace('AND #F8','AND @SmallMaskConst.PixelsMask')
    return operation
