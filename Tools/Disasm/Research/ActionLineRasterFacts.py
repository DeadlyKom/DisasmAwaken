"""Линейный растеризатор ACTION с заменяемыми операциями и временным SP строки."""
FUNCTIONS={0xDDF0:('DrawLinearLine','Растеризация отрезка в линейный буфер страницы 80 с режимами AND, OR и XOR без конечной точки')}
LOCAL={0xDE0A:'OrderedY',0xDE3F:'ApplyLeft',0xDE42:'LeftBoundary',0xDE44:'LeftError',0xDE4F:'LeftByte',0xDE55:'LeftRow',
    0xDE5F:'SteepLeft',0xDE71:'LeftDownPixel',0xDE72:'ApplyDownLeft',0xDE7C:'LeftDownBound',0xDE7E:'LeftDownNext',0xDE84:'LeftDownByte',
    0xDE8B:'Rightward',0xDEA3:'ApplyRight',0xDEA6:'RightBoundary',0xDEA8:'RightError',0xDEB3:'RightByte',0xDEB9:'RightRow',
    0xDEC3:'SteepRight',0xDED5:'RightDownPixel',0xDED6:'ApplyDownRight',0xDEE0:'RightDownBound',0xDEE2:'RightDownNext',0xDEE8:'RightDownByte',0xDEEC:'RestoreStack'}
STATE_FIELDS=(('FirstPoint',0x8D2A,'упакованные пиксельные координаты, Second в младшем байте и First в старшем'),
    ('SecondPoint',0x8D2C,'второй упакованный конец отрезка'),('PixelOpcode',0x8D4E,'числовая команда A1 для AND, B1 для OR либо A9 для XOR'),
    ('BranchOpcode',0x8D4F,'числовая команда 30 для JR NC режима AND либо 38 для JR C режимов OR/XOR'),
    ('MaskOffset',0xDE0F,'изменяемый операнд ADD A,nn, 18 для AND либо 10 для OR/XOR'),
    ('SavedSP',0xDEED,'операнд восстановления CPU SP перед RET'))
MODIFIED_WRITERS=((0xDDFC,0xDEED,0xDEEC,2),)
CONTRACTS={('Action',0xDDF0):(
    ['FirstPoint и SecondPoint задают Second от 0 до 255 и First от 0 до 95 в пикселях, младший байт соответствует Second',
     'PixelOpcode, BranchOpcode и MaskOffset согласованы как A1/30/18 для очистки, B1/38/10 для OR либо A9/38/10 для XOR',
     'исходные восемь масок E010 и восемь инверсных E018 сохранены, буфер 8000..8BFF доступен на запись',
     'HL, DE и BC входных аргументов не задают, входные AF и альтернативный AF существенны только для случая равных концов',
     'ACTION находится в банке 0 и доступен на запись, на CPU-стеке внешний возврат, прерывания не вмешиваются во временный SP=0020'],
    ['при равных концах HL=0, DE содержит исходную упакованную SecondPoint, BC и A сохраняются, F=42, альтернативный набор сохранён, RAM не записывается',
     'при разных концах при необходимости выполняется обмен по First, рисование идёт от меньшей First к большей, при равной First порядок концов сохраняется',
     'выданы max(abs(deltaSecond),abs(deltaFirst)) пикселей, первый включён, нормализованный конечный исключён',
     'HL содержит линейный адрес байта конечной точки, B=0, C содержит маску её фазы, D большую длину, E меньшую',
     "A' равен половине большей длины с округлением вниз, точные основной AF и F' зависят от последнего вращения маски, изменения адреса и шага ошибки",
     "все AF и AF' задаются числовой моделью raster в CheckActionLineRaster.py, для пологого пути A может содержать загруженный неизменённый следующий байт",
     "HL', DE', BC', IX и IY сохраняются, I, IM, IFF и paging сохраняются, SP восстановлен и после RET равен входному SP+2, R меняется",
     'переписаны SavedSP и два opcode выбранного из четырёх ядер, остальные ядра сохраняются, порты не используются'],
    ["HL, DE, BC, AF, AF', R, пиксельные байты с точными дополнительными сохранениями, SavedSP и два opcode выбранного ядра"],
    ['код не проверяет First<=95, расширенная серия First 0..255 подтверждает записи до 9FFF, их игровая допустимость отдельно не доказана',
     'буфер линейный, адрес равен 8000 плюс First*32 плюс Second DIV 8, это не адресная раскладка экрана ULA',
     'ошибка начинается с половины большой длины, меньшая координата продвигается только при строго отрицательной ошибке',
     'пологие ядра накапливают байт и сохраняют его при смене байта, строки либо завершении, возможны записи неизменённого соседнего байта',
     'крутые ядра сохраняют байт для каждого пикселя, конечная точка всё равно исключена',
     'AND использует инверсную маску и JR NC, OR/XOR прямую маску и JR C, сохраняются фактические изменяемые байты инструкций',
     'SP=0020 является шагом строки, DI/EI здесь нет, ISR не должен использовать этот временный стек, новые области памяти не выделяются',
     '49920 сценариев проверяют все регистры кроме R, всю физическую RAM и кратность записей, точное R/T, все совместные входы, IRQ, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0xDDF0:(['-----------------------------------------','Проверка совпадающих концов','Чтение двух упакованных точек, сравнение полного слова с очищенным Carry.'],None),
    0xDDFA:([], 'выход, если оба упакованных конца совпадают, пиксели и изменяемые opcode не записывать'),
    0xDDFC:(['-----------------------------------------','Рабочий SP как шаг строки','Сохранение CPU-стека в операнде и установка SP=32 для ADD HL,SP между линейными строками.'],None),
    0xDE03:(['Расчёт разности First, при отрицательном результате концы меняются местами.'],None),
    0xDE05:([], 'переход, если First второго конца не меньше First первого, обмен концов не нужен'),
    0xDE0A:(['-----------------------------------------','Адрес и маска первого пикселя','Чтение фазы Second AND 7 и выбор прямой либо инверсной таблицы по изменяемому MaskOffset.'],None),
    0xDE18:(['Расчёт линейного адреса 8000+First*32+Second DIV 8, SCF вводит старший бит страницы 80.'],None),
    0xDE26:(['Расчёт разности Second и выбор горизонтального направления.'],None),
    0xDE27:([], 'переход, если Second первого конца меньше Second второго, рисовать вправо'),
    0xDE29:(['Проверка большой длины для левого направления, равенство выбирает пологое ядро.'],None),
    0xDE2A:([], 'переход, если модуль deltaSecond меньше deltaFirst, выбрать крутое левое ядро'),
    0xDE2C:(['-----------------------------------------','Пологое левое ядро','Подготовка D как большой длины, E как меньшей и альтернативного A как половины большой длины.'],None),
    0xDE32:(['Обновление opcode пикселя и условия переноса между байтами для текущего режима.'],None),
    0xDE3F:(['Исходный NOP заменяется AND C, OR C либо XOR C, значения исходного образа не исправляются.'],None),
    0xDE42:([], 'переход, если вращение маски требует предыдущего байта, режим AND меняет opcode проверки Carry на NC'),
    0xDE44:(['Расчёт следующей ошибки, пиксельный аккумулятор временно сохраняется в альтернативном AF.'],None),
    0xDE46:([], 'переход, если ошибка после вычитания меньшей длины отрицательна, перейти к следующей строке'),
    0xDE4F:(['Сохранение накопленного байта перед переходом в предыдущий байт линейной строки.'],None),
    0xDE55:(['Коррекция отрицательной ошибки и сохранение байта перед прибавлением шага строки.'],None),
    0xDE5F:(['-----------------------------------------','Крутое левое ядро','Подготовка количества строк и ошибки, каждое прохождение записывает один пиксельный байт.'],None),
    0xDE65:(['Обновление opcode выбранного крутого ядра.'],None),
    0xDE71:(['Чтение текущего пиксельного байта, маска применяется подготовленной командой.'],None),
    0xDE75:(['Расчёт ошибки после обязательного продвижения на строку.'],None),
    0xDE77:([], 'переход, если ошибка неотрицательна, горизонтальную фазу не менять'),
    0xDE7C:([], 'переход, если горизонтальный шаг пересёк байт, режим AND меняет opcode проверки Carry на NC'),
    0xDE8B:(['-----------------------------------------','Правое направление','Расчёт модуля deltaSecond, затем выбор крутой либо пологой ветви.'],None),
    0xDE8E:([], 'переход, если модуль deltaSecond меньше deltaFirst, выбрать крутое правое ядро'),
    0xDE90:(['Подготовка большой и меньшей длин пологого правого ядра.'],None),
    0xDE96:(['Обновление opcode пикселя и перехода между байтами правого ядра.'],None),
    0xDEA6:([], 'переход, если вращение маски требует следующего байта, режим AND меняет opcode проверки Carry на NC'),
    0xDEA8:(['Расчёт следующей ошибки пологого правого ядра.'],None),
    0xDEAA:([], 'переход, если ошибка отрицательна, скорректировать её и перейти к следующей строке'),
    0xDEB3:(['Сохранение накопленного байта перед переходом в следующий байт строки.'],None),
    0xDEB9:(['Коррекция ошибки и переход на следующую линейную строку.'],None),
    0xDEC3:(['-----------------------------------------','Крутое правое ядро','Подготовка длины по строкам и половинной ошибки.'],None),
    0xDEC9:(['Обновление opcode выбранного правого крутого ядра.'],None),
    0xDED5:(['Чтение и запись текущего пиксельного байта до продвижения на следующую строку.'],None),
    0xDED9:(['Расчёт ошибки и необходимости продвижения горизонтальной фазы.'],None),
    0xDEDB:([], 'переход, если ошибка неотрицательна, горизонтальную фазу не менять'),
    0xDEE0:([], 'переход, если горизонтальный шаг требует следующего байта, режим AND меняет opcode проверки Carry на NC'),
    0xDEEC:(['-----------------------------------------','Возврат к CPU-стеку','Восстановление исходного SP перед настоящим RET, временный шаг строки больше не используется.'],None)}


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xDDF0:
        for name,address,_ in STATE_FIELDS:operation=operation.replace('(#'+format(address,'04X')+')','(@ActionLineRasterState.'+name+')')
        operation=operation.replace('LD SP, #0020','LD SP, @ActionLineRasterConst.RowBytes').replace('AND #07','AND @ActionLineRasterConst.PhaseMask').replace('LD A, #E0','LD A, @ActionLineRasterConst.MaskPage')
    return operation


def constants():
    lines=['','                module ActionLineRasterConst']
    for name,value,note in (('RowBytes',32,'шаг строки линейного буфера'),('PhaseMask',7,'фаза пикселя внутри байта'),('MaskPage',0xE0,'страница исходных масок'),
        ('SetOffset',0x10,'смещение прямых масок OR/XOR'),('ClearOffset',0x18,'смещение инверсных масок AND'),('AndOpcode',0xA1,'команда AND C'),('OrOpcode',0xB1,'команда OR C'),('XorOpcode',0xA9,'команда XOR C'),('CarryBranch',0x38,'команда JR C'),('NoCarryBranch',0x30,'команда JR NC')):
        lines.append((name.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+note)
    return '\n'.join(lines+['                endmodule',''])


INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionLineRasterConst',constants()),)


def qualify_mutations(mutations,regions,functions,pieces):
    region=next(r for r in regions if r['name']=='Action');instructions={i['address']:i for i in region['instructions']}
    for writer,target,pixel in ((0xDE35,0xDE3F,True),(0xDE3B,0xDE42,False),(0xDE68,0xDE72,True),(0xDE6E,0xDE7C,False),
        (0xDE99,0xDEA3,True),(0xDE9F,0xDEA6,False),(0xDECC,0xDED6,True),(0xDED2,0xDEE0,False)):
        assert instructions[writer]['operation']=='LD (#'+format(target,'04X')+'),A'
        original=instructions[target];assert original['operation']=='NOP' if pixel else original['operation'].startswith('JR C,')
        assert not any(m['region']=='Action' and m['writer']==writer for m in mutations)
        mutations.append(dict(region='Action',writer=writer,target=target,target_instruction=target,size=1,target_operation=original['operation'],
            path='Source/Action/DrawLinearLine.asm',writer_bank=0,target_bank=0,target_region='Action',target_slot=17,target_offset=target-0x6000,
            writer_source_classified=True,target_source_classified=True,target_path='Source/Action/DrawLinearLine.asm',
            target_opcode_executable_byte=True,target_runtime_opcodes=[0xA1,0xA9,0xB1] if pixel else [0x30,0x38]))
    mutations.sort(key=lambda m:(m['region'],m['writer'],m['target']))
