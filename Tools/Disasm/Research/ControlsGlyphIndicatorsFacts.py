"""Полный управляющий вход трёх знаков, точные ограничения и временный SP в растре."""
FUNCTIONS = {0xE021:('UpdateGlyphIndicators','Очистка двух экранных зон и обновление до трёх трёхстрочных знаков с точными байтовыми ограничениями')}
LOCAL = {0xE09B:'ClampFirstXLow',0xE0A1:'ClampFirstXHigh',0xE0A7:'FirstXReady',
    0xE0B3:'ClampFirstYHigh',0xE0B9:'FirstYReady',0xE0C7:'DrawFirst',0xE0CA:'CheckSecond',
    0xE0E4:'ClampSecondXLo',0xE0EA:'ClampSecondXHi',0xE0F0:'SecondXReady',
    0xE0FC:'ClampSecondYHi',0xE102:'SecondYReady',0xE110:'DrawSecond',
    0xE122:'ClampThirdXLow',0xE128:'ClampThirdXHigh',0xE12E:'ThirdXReady',
    0xE13A:'ClampThirdYHigh',0xE140:'ThirdYReady'}
LABELS = {('Controls',address):name for address,name in LOCAL.items()}
CONTINUATIONS = {}
RENAMES = {'Controls.UnknownE021.Entry':'Controls.UpdateGlyphIndicators.Entry',
    **{'Controls.UnknownE021.Point'+format(a,'04X'):'Controls.UpdateGlyphIndicators.'+name for a,name in LOCAL.items()}}
CONTRACTS = {('Controls',0xE021):(
    ['HL входных аргументов не задаёт, DE и B сохраняются только на пути без единого знака, C и AF числовых аргументов не задают',
     'физические Control, First, Second и Third из ActionGlyphIndicatorState задают режим, запрет, координаты и байт выбора формы',
     'банк 1 выбран, RestoreSP доступен для самомодификации, используются четыре исходных знака и их восемь фаз',
     'на CPU-стеке внешний возврат, ещё два байта нужны для CALL, рамка и код не перекрываются с очищаемыми зонами',
     'IRQ не вмешиваются, код не запрещает их самостоятельно, во время очистки SP действительно направляется в пиксельную RAM'],
    ['при отсутствии знаков HL=0000, DE и B сохраняются, C=Second.X OR Second.Y, A=80, F=42',
     'при наличии знаков HL и DE соответствуют последнему OrThreeRowGlyph, B содержит его ограниченный Y',
     'на выходе по маркеру второго C=Second.X OR Second.Y, A=80, F=42, третий знак пропущен',
     'на выходе по ненулевому ThirdGate C сохраняет удвоенную фазу второго знака, A=ThirdGate, F соответствует AND этого байта',
     'на полном пути C содержит удвоенную фазу третьего знака, A и F соответствуют его последнему OR',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2",
     'RestoreSP содержит входной SP, 64 очищаемых байта обнулены до OR, пиксели знаков затем установлены',
     'R учитывает 71 M1 очистки и допуска первого, 9 M1 проверки второго, 3 M1 проверки ThirdGate и выбранные координатные пути с рисователями'],
    ['HL, DE, BC, AF, RestoreSP, 64 очищаемых байта и байты OR знаков, два байта CPU-стека, R'],
    ['FirstMode=1 пропускает первый знак, все остальные байты режима допускают его, ThirdGate=0 допускает третий после проверки второго',
     'точный маркер отсутствия второго равен OR всех трёх его байтов с результатом 80, это не отдельная проверка SignSource=80',
     'координаты первого и второго ограничены X=152..165, третьего X=176..189, все Y=104..117',
     'X сначала складывается по модулю байта с центром, знаковое переполнение выбирает нижнюю границу, затем идут беззнаковые сравнения',
     'Y складывается с 70 по модулю байта без отдельной ветви переполнения, заменить это обычным целочисленным clamp нельзя',
     'первый и второй рисователи вызываются CALL, третий получает хвостовой JP либо последовательное исполнение в соседнем файле',
     'смысл исходных векторов в игре и Unknown83 не установлен, локальный экранный алгоритм проверен на всех байтовых координатах'])}
COMMENTS = {
    0xE021:(['сохранение настоящего входного SP в операнде RestoreSP перед использованием SP как указателя очистки'],None),
    0xE025:(['подготовка нулевого слова, два PUSH с DEC SP очищают четыре столбца и сохраняют промежуточный'],None),
    0xE088:(['восстановление обычного SP, исходный нулевой операнд уже заменён сохранённым входным значением'],None),
    0xE08B:(['-----------------------------------------','Допуск первого знака','проверка числового FirstMode перед обработкой First'],None),
    0xE08F:([], 'переход, если FirstMode равен SkipFirstMode, сразу проверить второй вход'),
    0xE091:(['вычисление байтового X первого знака, знаковое переполнение исходного ADD обрабатывается отдельно'],None),
    0xE096:([], 'переход, если сложение First.X с LeftCenterX не дало знакового переполнения, продолжить ограничение'),
    0xE099:(['выбор LeftMinX при знаковом переполнении, исходное поведение сохраняется'],None),
    0xE09B:(['проверка нижней границы уже байтового X первого знака'],None),
    0xE09D:([], 'переход, если байтовый X не меньше LeftMinX, проверить верхнюю границу'),
    0xE0A1:(['проверка исключённой верхней границы X первого знака'],None),
    0xE0A3:([], 'переход, если байтовый X меньше LeftEndX, горизонтальная координата готова'),
    0xE0A7:(['вычисление байтового Y первого знака без отдельной ветви знакового переполнения'],None),
    0xE0AD:(['проверка нижней границы Y первого знака'],None),
    0xE0AF:([], 'переход, если байтовый Y не меньше MinY, проверить верхнюю границу'),
    0xE0B3:(['проверка исключённой верхней границы Y первого знака'],None),
    0xE0B5:([], 'переход, если байтовый Y меньше EndY, вертикальная координата готова'),
    0xE0B9:(['проверка знака First.SignSource перед выбором плюса или креста'],None),
    0xE0C1:([], 'переход, если First.SignSource неотрицателен, использовать Plus00'),
    0xE0C7:(['рисование первого знака настоящим CALL, после него обычный SP восстанавливается RET рисователя'],None),
    0xE0CA:(['-----------------------------------------','Маркер второго входа','вычисление OR всех трёх байтов Second, в C остаётся OR только X и Y'],None),
    0xE0D7:(['проверка точного значения VectorSentinel, остальные результаты OR допускают второй знак'],None),
    0xE0D9:([], 'выход, если OR трёх байтов Second равен VectorSentinel, второй и третий знаки пропущены'),
    0xE0DA:(['вычисление байтового X второго знака с исходной ветвью знакового переполнения'],None),
    0xE0DF:([], 'переход, если сложение Second.X с LeftCenterX не дало знакового переполнения'),
    0xE0E4:(['проверка нижней границы X второго знака'],None),
    0xE0E6:([], 'переход, если байтовый X не меньше LeftMinX, проверить верхнюю границу'),
    0xE0EA:(['проверка исключённой верхней границы X второго знака'],None),
    0xE0EC:([], 'переход, если байтовый X меньше LeftEndX, горизонтальная координата готова'),
    0xE0F0:(['вычисление байтового Y второго знака'],None),
    0xE0F6:(['проверка нижней границы Y второго знака'],None),
    0xE0F8:([], 'переход, если байтовый Y не меньше MinY, проверить верхнюю границу'),
    0xE0FC:(['проверка исключённой верхней границы Y второго знака'],None),
    0xE0FE:([], 'переход, если байтовый Y меньше EndY, вертикальная координата готова'),
    0xE102:(['проверка знака Second.SignSource перед выбором заполненного или полого квадрата'],None),
    0xE10A:([], 'переход, если Second.SignSource неотрицателен, использовать Solid00'),
    0xE110:(['рисование второго знака настоящим CALL после возможного первого'],None),
    0xE113:(['-----------------------------------------','Допуск третьего знака','проверка полного байта ThirdGate, ненулевое значение завершает обновление'],None),
    0xE117:([], 'выход, если ThirdGate ненулевой, сохранить адреса второго знака и вернуть значение запрета в A'),
    0xE118:(['вычисление X третьего знака с центром RightCenterX, физическая запись Third хранит Y перед X'],None),
    0xE11D:([], 'переход, если сложение Third.X с RightCenterX не дало знакового переполнения'),
    0xE122:(['проверка нижней границы X третьего знака'],None),
    0xE124:([], 'переход, если байтовый X не меньше RightMinX, проверить верхнюю границу'),
    0xE128:(['проверка исключённой верхней границы X третьего знака'],None),
    0xE12A:([], 'переход, если байтовый X меньше RightEndX, горизонтальная координата готова'),
    0xE12E:(['вычисление байтового Y третьего знака'],None),
    0xE134:(['проверка нижней границы Y третьего знака'],None),
    0xE136:([], 'переход, если байтовый Y не меньше MinY, проверить верхнюю границу'),
    0xE13A:(['проверка исключённой верхней границы Y третьего знака'],None),
    0xE13C:([], 'переход, если байтовый Y меньше EndY, вертикальная координата готова'),
    0xE140:(['проверка знака Third.SignSource, оба пути используют внешний возврат обновления'],None),
    0xE148:([], 'переход, если Third.SignSource неотрицателен, хвостом рисовать Solid00'),
    0xE14B:(['выбор Hollow00 перед последовательным продолжением в OrThreeRowGlyph.asm'],None),
}


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address==0xE021:
        fields={0x9B81:'Control.FirstMode',0x9B82:'Control.ThirdGate',
            0x9B8A:'First.X',0x9B8B:'First.Y',0x9B8C:'First.SignSource',
            0x9B87:'Second.X',0x9B88:'Second.Y',0x9B89:'Second.SignSource',
            0x9B84:'Third.Y',0x9B85:'Third.X',0x9B86:'Third.SignSource'}
        for address,name in fields.items():
            operation=operation.replace('(#'+format(address,'04X')+')','(@ActionGlyphIndicatorState.'+name+')')
        operation=operation.replace('(#E089)','(@ControlsGlyphIndicatorsState.RestoreSP)')
        for row in range(8):
            operation=operation.replace('LD SP, #'+format(0x48B8+256*row,'04X'),'LD SP, @ControlsGlyphIndicatorsConst.TopRow'+str(row)+'SP')
            operation=operation.replace('LD SP, #'+format(0x48D8+256*row,'04X'),'LD SP, @ControlsGlyphIndicatorsConst.BottomRow'+str(row)+'SP')
        for value,name in ((0xA0,'LeftCenterX'),(0xB8,'RightCenterX'),(0x70,'CenterY')):
            operation=operation.replace('ADD A, #'+format(value,'02X'),'ADD A, @ControlsGlyphIndicatorsConst.'+name)
        for value,name in ((0x98,'LeftMinX'),(0xA6,'LeftEndX'),(0xB0,'RightMinX'),(0xBE,'RightEndX'),
                           (0x68,'MinY'),(0x76,'EndY'),(0x80,'VectorSentinel')):
            operation=operation.replace('CP #'+format(value,'02X'),'CP @ControlsGlyphIndicatorsConst.'+name)
        for value,name in ((0x98,'LeftMinX'),(0xA5,'LeftMaxX'),(0xB0,'RightMinX'),(0xBD,'RightMaxX'),(0x68,'MinY'),(0x75,'MaxY')):
            operation=operation.replace('LD A, #'+format(value,'02X'),'LD A, @ControlsGlyphIndicatorsConst.'+name)
        for value,name in ((0xE1B1,'Plus00'),(0xE1E1,'Cross00'),(0xE211,'Solid00'),(0xE241,'Hollow00')):
            operation=operation.replace('LD DE, #'+format(value,'04X'),'LD DE, @ControlsThreeRowGlyphs.'+name)
    return operation


def qualify_restore_sp(mutations,regions):
    """Привязка доказанной самомодификации SP к реальному банку и дисковому байту."""
    controls=next(region for region in regions if region['name']=='Controls')
    target=next(i for i in controls['instructions'] if i['address']==0xE088)
    assert target['slot']==23 and target['operation']=='LD SP,#0000'
    matches=[item for item in mutations if item['region']=='Controls' and item['writer']==0xE021 and item['target']==0xE089]
    assert len(matches)==1
    matches[0].update(writer_bank=1,target_bank=1,target_region='Controls',target_slot=23,
        target_offset=target['offset']+1,target_path='Source/Controls/UpdateGlyphIndicators.asm')
