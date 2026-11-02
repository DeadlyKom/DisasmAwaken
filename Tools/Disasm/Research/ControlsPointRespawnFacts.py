"""Два доказанных динамических входа возврата точки, с локальным учётом R."""
FUNCTIONS = {
    0xCE16:('RespawnPointIndexPos','Возврат точки с чередованием сторон для неотрицательного индекса управляющей таблицы'),
    0xCE5D:('RespawnPointIndexNeg','Возврат точки с противоположным чередованием сторон для отрицательного индекса таблицы')}
CONTINUATIONS = {}
POSITIVES = (0xCE23,0xCE2A,0xCE30,0xCE3D,0xCE3F,0xCE41,0xCE48,0xCE4E,0xCE5B)
NEGATIVES = (0xCE6A,0xCE71,0xCE77,0xCE82,0xCE84,0xCE86,0xCE8D,0xCE93,0xCEA2)
NAMES = ('FirstModulo','CapFirstY','OffsetFirstY','AcceptFirstX','SecondSample','SecondModulo','CapSecondY','MirrorSecondY','AcceptSecondX')
LOCAL = {**dict(zip(POSITIVES,NAMES)),**dict(zip(NEGATIVES,NAMES))}
LABELS = {('Controls',a):name for a,name in LOCAL.items()}
RENAMES = {'Controls.Unknown'+format(a,'04X')+'.Entry':'Controls.'+name+'.Entry' for a,(name,_) in FUNCTIONS.items()}
for root,addresses in ((0xCE16,POSITIVES),(0xCE5D,NEGATIVES)):
    for address in addresses:
        RENAMES['Controls.Unknown'+format(root,'04X')+'.Point'+format(address,'04X')] = 'Controls.'+FUNCTIONS[root][0]+'.'+LOCAL[address]
CONTRACTS = {}
for entry in FUNCTIONS:
    positive = entry==0xCE16
    prefix = 'Positive' if positive else 'Negative'
    first,second = ('HighX','LowX') if positive else ('LowX','HighX')
    CONTRACTS['Controls',entry] = (
        ['HL, DE, BC, AF входных аргументов не задают, используются '+prefix+'Phase, '+prefix+'Step и '+prefix+'YOffset',
         prefix+'Step=1..255, R задаёт начальный байт refresh, включая сохраняемый при увеличении бит 7',
         'банк 1 выбран, изменяемый фазовый операнд доступен для записи, на CPU-стеке внешний возврат',
         'формулы R и точные регистровые выходы проверены без вмешательства IRQ'],
        ['HL и B сохранены, DE содержит D=X и E=Y, C='+prefix+'Step, A=X',
         prefix+'Phase заменён на исходный байт XOR 01, новое нулевое значение выбирает первую ветвь, любое ненулевое вторую',
         'v=MIN(первое чтение R MOD Step,94), первая ветвь Y=(v+YOffset) AND FF и X='+first,
         'вторая ветвь Y=95-v и X='+second+', обе формулы X приведены в ControlsPointRespawn.md',
         'F соответствует последней проверке CP либо коррекции ADD/SUB координаты X, R включает все выполненные M1',
         "HL', DE', BC', AF', IX и IY, I, IM и IFF сохраняются, SP=входной SP+2"],
        ['DE, BC в части C, AF, один фазовый байт, R'],
        ['дополнительных PUSH, CALL и портовых операций нет, изменяется только фазовый операнд',
         'при Step=0 цикл вычитания не продвигается и не возвращает управление, исходный нулевой шаг требует настройки вызывающим кодом',
         'Phase=00 и 01 чередуют ветви, произвольные старшие биты фазы сохраняются и могут запрещать первую ветвь',
         'HighX может дать 00 либо FE при произвольном R, границы начальной подготовки 35 точек сюда не переносятся',
         'название IndexPos/IndexNeg отражает бит 7 байтового индекса (-control) AND FF, а не знак неограниченного математического числа'])
COMMENTS = {}
for root,phase,step,offset,first_sample,first_mod,cap_first,offset_y,first_x,second_sample,second_mod,cap_second,mirror_y,second_x in (
    (0xCE16,0xCE17,0xCE1E,0xCE31,0xCE21,0xCE23,0xCE2A,0xCE30,0xCE3D,0xCE3F,0xCE41,0xCE48,0xCE4E,0xCE5B),
    (0xCE5D,0xCE5E,0xCE65,0xCE78,0xCE68,0xCE6A,0xCE71,0xCE77,0xCE82,0xCE84,0xCE86,0xCE8D,0xCE93,0xCEA2)):
    COMMENTS[root] = (['чтение фазового байта перед переключением младшего бита'],None)
    COMMENTS[root+2] = (['переключение только младшего бита фазового селектора'],None)
    COMMENTS[root+4] = (['сохранение новой фазы в исходном операнде LD A,nn'],None)
    COMMENTS[root+7] = (['чтение шага, нулевой шаг создаёт непродвигающийся цикл'],None)
    COMMENTS[root+9] = ([], 'переход, если новая фаза ненулевая, выбрать второе сочетание сторон')
    COMMENTS[first_sample] = (['получение первого байта R для остатка по ненулевому шагу'],None)
    COMMENTS[first_mod] = (['проверка остатка относительно шага перед очередным вычитанием'],None)
    COMMENTS[first_mod+1] = ([], 'переход, если остаток меньше шага, ограничить вертикальную координату')
    COMMENTS[cap_first] = (['проверка ограничения остатка сверху значением 94'],None)
    COMMENTS[cap_first+2] = ([], 'переход, если остаток меньше 94, не загружать ограничитель')
    COMMENTS[offset_y] = (['вычисление Y первой ветви с исходным байтовым смещением'],None)
    COMMENTS[second_sample] = (['получение первого R для отражённой вертикальной ветви'],None)
    COMMENTS[second_mod] = (['проверка остатка второй ветви относительно шага'],None)
    COMMENTS[second_mod+1] = ([], 'переход, если остаток меньше шага, ограничить его перед отражением')
    COMMENTS[cap_second] = (['проверка верхнего ограничения 94 для отражённой координаты'],None)
    COMMENTS[cap_second+2] = ([], 'переход, если остаток меньше 94, сохранить его без загрузки ограничителя')
    COMMENTS[mirror_y] = (['вычисление отражённой координаты Y=95-остаток'],None)
    COMMENTS[first_x] = (['возврат горизонтальной координаты в D, вертикальная уже находится в E'],None)
    COMMENTS[second_x] = (['возврат второго сочетания X в D и Y в E'],None)
# Номера инструкций двух разных горизонтальных формул не совпадают относительно RET.
COMMENTS.update({
    0xCE33:(['получение второго R и смещение горизонтальной координаты на 128'],None),
    0xCE37:(['проверка верхней границы смещённого X'],None),
    0xCE39:([], 'переход, если X меньше 254, сохранить координату без коррекции'),
    0xCE53:(['получение второго R без горизонтального смещения'],None),
    0xCE55:(['проверка нулевого X перед заменой на 1'],None),
    0xCE57:([], 'переход, если X не равен нулю, не выполнять прибавление 1'),
    0xCE7A:(['получение второго R без горизонтального смещения первой ветви'],None),
    0xCE7C:(['проверка нулевого X перед заменой на 1'],None),
    0xCE7E:([], 'переход, если X не равен нулю, не выполнять прибавление 1'),
    0xCE98:(['получение второго R для второй ветви со смещением X на 128'],None),
    0xCE9C:(['проверка верхней границы смещённого X второй ветви'],None),
    0xCE9E:([], 'переход, если X меньше 254, сохранить координату без коррекции')})
def name_operands(region,function_address,operation):
    if region=='Controls' and (function_address in FUNCTIONS or function_address==0xCB00):
        for address,name in ((0xCE17,'PositivePhase'),(0xCE1E,'PositiveStep'),(0xCE31,'PositiveYOffset'),
            (0xCE5E,'NegativePhase'),(0xCE65,'NegativeStep'),(0xCE78,'NegativeYOffset')):
            operation = operation.replace('(#'+format(address,'04X')+')','(@ControlsPointRespawnState.'+name+')')
    if region=='Controls' and function_address==0xCB00:
        operation = operation.replace('LD HL, #CE16','LD HL, @Controls.RespawnPointIndexPos.Entry')
        operation = operation.replace('LD HL, #CE5D','LD HL, @Controls.RespawnPointIndexNeg.Entry')
    return operation
