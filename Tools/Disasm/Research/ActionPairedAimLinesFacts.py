"""63B6, фазовое окно, третья шкала и пара прямых XOR-растеризаций к прицелу."""
FUNCTIONS={0x63B6:('RequestPairedAimLines','Фазовый допуск двух XOR-линий к прицелу с расходом третьей шкалы и включением захвата цели')}
LOCAL={0x63EE:'SetX',0x6401:'SetY'}
STATE_MODULE='ActionPairedAimState'
STATE_FIELDS=(('Phase',0x63B7,'изменяемый операнд LD A,n, на каждом вызове получает сумму по модулю 256'),
              ('PhaseStep',0x63B9,'изменяемый операнд ADD A,n, поле 04 набора параметров задаёт шаг фазового допуска'))
MODIFIED_WRITERS=((0x63BA,0x63B7,0x63B6,1),(0x63C6,0xA8BC,0xA8BB,1),(0x63CB,0x666B,0x666A,1),
                  (0x63CF,0xE310,0xE30F,1),(0x63D5,0xECA9,0xECA8,2),(0x63E0,0xDE0F,0xDE0E,1))
CONTRACTS={('Action',0x63B6):(
    ['HL, DE, BC и AF числовых аргументов не задают, Phase и PhaseStep задают байтовый фазовый допуск',
     'ThirdValue содержит значение третьей шкалы, поля точки ActionAimPoint доступны, допустим профиль Y от 0 до 88',
     'линейный буфер 8000..8BFF и путь равных концов на строке 95 доступны, таблицы прямых масок E010 сохранены',
     'перенесённый код банка 5 и ACTION банка 0 доступны для самомодификации, CPU-стек не пересекается с пикселями, IRQ исключены'],
    ['Phase получает Phase+PhaseStep по модулю 256 на всех путях, только Carry суммы допускает дальнейшую обработку',
     'без Carry A/F соответствуют сумме и остальные данные сохраняются, при ThirdValue<2 A/F соответствуют CP 2 и линии не рисуются',
     'после полного допуска ThirdValue уменьшается на два, ThirdRequest получает 1, Gate захвата проецируемой записи получает 0',
     'CursorA получает EE34, рабочие команды растеризатора настроены на XOR и прямую таблицу масок',
     'целевая точка получает X+8 и Y+6 с двумя отдельными поправками по R, младший бит задаёт модуль 0/1, бит 4 знак поправки',
     'реальные линии рисуются от упакованных 5F40 и 5FC0 к одной сохранённой точке, конечные точки каждого нормализованного отрезка исключены',
     'используется DrawPacked по DDFC, при совпавшем конце нулевой B запускает 256 итераций влево вместо пустого вывода',
     "после рисования HL, DE, BC, AF и AF' соответствуют второй прямой растеризации, HL'/DE'/BC', IX, IY, I/IM/IFF и paging сохраняются",
     'SP после внешнего RET равен входному SP+2, первая линия использует дополнительную рамку в четыре байта, R на нерисующих путях сверяется точно'],
    ["HL, DE, BC, AF, AF', R по достигнутому пути, Phase, ThirdValue, ThirdRequest, Gate, CursorA, рабочие и кодовые операнды растеризатора, пиксели и CPU-стек, SP внешним RET"],
    ['фазовый шаг является числовым параметром частоты допуска, PhaseStep=0 не даёт Carry, игровой вызывающий код этого входа ещё отдельно не установлен',
     'буфер FirstPoint/SecondPoint не обновляется, два конца передаются непосредственно HL и DE, подмена обычным входом DDF0 изменила бы равные случаи',
     '77824 сценария включили все пары Phase/PhaseStep, все значения ThirdValue, все X и разные Y/R, 512 совпавших концов сохранены как исходная особенность',
     'сверены регистры кроме R растеризатора, все восемь банков и кратность записей, 33184 нерисующих пути проверены с точным R',
     'профиль Y>88, полный игровой вызов, R/T растеризатора, полное произведение входов, аппаратные IRQ, сборка и нативный запуск не доказаны'])}
COMMENTS={
    0x63B6:(['Расчёт нового фазового байта с изменяемым шагом, сумма сохраняется до проверки допуска.'],None),
    0x63BD:([],'выход, если байтовая сумма не дала Carry, фазовый байт уже обновлён'),
    0x63BE:(['Проверка наличия двух делений третьей шкалы перед расходом и выводом.'],None),
    0x63C3:([],'выход, если ThirdValue меньше двух, третью шкалу и экран сохранить'),
    0x63C4:(['Расчёт и запись ThirdValue после расхода двух делений.'],None),
    0x63C9:(['Обновление запроса третьей шкалы и разрешение CaptureProjectedRecord нулевым Gate.'],None),
    0x63D2:(['Обновление курсора AY-канала A, фактический вывод звука выполняет кадровый потребитель позднее.'],None),
    0x63D8:(['Обновление рабочих команд до XOR C, JR C и смещения прямых пиксельных масок.'],None),
    0x63E3:(['Расчёт отдельной поправки X, младший бит R задаёт модуль, бит 4 выбирает отрицание.'],None),
    0x63EA:([],'переход, если бит 4 первого прочитанного R сброшен, поправку X не отрицать'),
    0x63EE:(['Расчёт X конечной точки по текущему прицелу, смещению 8 и исходной байтовой поправке.'],None),
    0x63F6:(['Расчёт поправки Y по отдельному более позднему чтению R с теми же правилами модуля и знака.'],None),
    0x63FD:([],'переход, если бит 4 второго прочитанного R сброшен, поправку Y не отрицать'),
    0x6401:(['Расчёт Y конечной точки по текущему прицелу, смещению 6 и байтовой поправке.'],None),
    0x6409:(['Сохранение одного целевого DE для двух прямых входов растеризатора с разными неподвижными концами.'],None),
    0x640A:(['Выбор первой неподвижной точки, Second=64 и First=95, и настоящий прямой вход без проверки равенства.'],None),
    0x6410:(['Выбор второй неподвижной точки, Second=192 и First=95, восстановление того же целевого DE.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionPairedAimConst','''
                ; Исходные параметры двух линий прицела
                module ActionPairedAimConst
DefaultPhase    equ #00                                                         ; исходный аккумулятор фазового допуска
DefaultStep     equ #32                                                         ; исходный шаг, изменяется полем 04 набора параметров
Cost            equ #02                                                         ; расход двух делений ThirdValue
XorMode         equ #38A9                                                       ; младший байт XOR C, старший JR C
FirstPoint      equ #5F40                                                       ; Second=64, First=95
SecondPoint     equ #5FC0                                                       ; Second=192, First=95
XOffset         equ #08                                                         ; перенос точки прицела по горизонтали перед поправкой
YOffset         equ #06                                                         ; перенос точки прицела по вертикали перед поправкой
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x63B6):return operation
    for address,name in ((0x63B7,'@ActionPairedAimState.Phase'),(0xA8BC,'@ActionPanelGaugesState.ThirdValue'),
                         (0x666B,'@ActionPanelGaugesState.ThirdRequest'),(0xE310,'@ActionProjectedCaptureState.Gate'),
                         (0xECA9,'@ActionAyEffectState.CursorA'),(0x8D4E,'@ActionLineRasterState.PixelOpcode'),
                         (0xDE0F,'@ActionLineRasterState.MaskOffset'),(0x9B19,'@ActionAimPoint.Value.X'),(0x9B1A,'@ActionAimPoint.Value.Y')):
        operation=operation.replace('(#'+format(address,'04X')+')','('+name+')')
    for before,after in (('LD A, #00','LD A, @ActionPairedAimConst.DefaultPhase'),('ADD A, #32','ADD A, @ActionPairedAimConst.DefaultStep'),
                         ('CP #02','CP @ActionPairedAimConst.Cost'),('SUB #02','SUB @ActionPairedAimConst.Cost'),
                         ('LD HL, #EE34','LD HL, @ActionAyStreams.PairedAimRow00'),('LD HL, #38A9','LD HL, @ActionPairedAimConst.XorMode'),
                         ('LD A, #10','LD A, @ActionLineRasterConst.SetOffset'),('ADD A, #08','ADD A, @ActionPairedAimConst.XOffset'),
                         ('ADD A, #06','ADD A, @ActionPairedAimConst.YOffset'),('LD HL, #5F40','LD HL, @ActionPairedAimConst.FirstPoint'),
                         ('LD HL, #5FC0','LD HL, @ActionPairedAimConst.SecondPoint'),('#DDFC','@Action.DrawLinearLine.DrawPacked')):
        operation=operation.replace(before,after)
    return operation


def qualify_mutations(records,flow,functions,pieces):
    paths={0x63B7:'Source/Action/RequestPairedAimLines.asm',0xA8BC:'Source/Action/UpdateFrame.asm',
        0x666B:'Source/Action/UpdatePanelGauges.asm',0xE310:'Source/Action/CaptureProjectedRecord.asm',
        0xECA9:'Source/Action/UpdateAyEffects.asm',0xDE0F:'Source/Action/DrawLinearLine.asm'}
    for item in records:
        if item['region']=='Action' and item['writer'] in (0x63BA,0x63C6,0x63CB,0x63CF,0x63D5,0x63E0):
            bank=5 if item['target']<0x8000 else 2 if item['target']<0xC000 else 0
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000+0x23D,writer_bank=5,
                target_slot=17,target_offset=item['target']-0x6000+(0x23D if bank==5 else 0),target_bank=bank,target_region='Action',
                target_path=paths[item['target']],target_source_classified=True,writer_source_classified=True)
