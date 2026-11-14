"""Прицельный запрос либо притягивание и байтовый сбор, исходный стек данных и два перекрытых правила."""
TAG='ActionTractorCollect'
TITLE='прицельный запрос и сбор захваченного объекта'
CASES=264679
FUNCTIONS={0x7317:('RequestAimOrCollectTarget','Запрос прицельных линий либо притягивание и сбор захваченного объекта по режиму силового луча')}
ENDS={0x7317:0x741D}
KEYS={0x7317:0x06}
LOCAL={0x7334:'DropTarget',0x733A:'PullTarget',0x7355:'CheckFirst',0x735C:'StepFirst',0x7364:'AddFirst',0x7366:'StoreFirst',
    0x7373:'CheckSecond',0x737A:'StepSecond',0x7382:'AddSecond',0x7384:'StoreSecond',
    0x7391:'CheckThird',0x7398:'StepThird',0x73A0:'AddThird',0x73A2:'StoreThird',0x73A3:'RestoreStack',
    0x73C2:'RandomAmount',0x73C9:'ReadPayload',0x73D2:'ApplyRule',0x73EB:'CheckByte',0x740E:'QueuePickup'}
MUTATIONS=((0x7344,0x73A4,2,0x73A3,None),
    (0x7411,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'))
CONTRACTS={('Action',0x7317):(
    ['HL, DE, BC и AF входных числовых аргументов не задают, результат сохранения зависит от выбранной ветви',
     'Mode по 7318 выбирает действие, ноль передаёт управление RequestPairedAimLines с его отдельным договором',
     'при ненулевом Mode Target0 задаёт полный байт кода, 80..FF дают отказ по знаку, для остальных адрес записи должен быть доступен',
     'компоненты, поля StateCode, ClassCode, OffsetScaleLow, Unknown11, ReuseByte и PickupKind доступны, запись и SavedSP доступны для изменения',
     'банк 0 выбран, поля Used, Capacity и байты от Row00 доступны, чтение правила по виду не проверяет границы таблицы',
     'действуют QueueTextItemBank1 и договор прицельного ребёнка, обычная рамка допускает восемнадцать дополнительных байтов',
     'обычный стек не пересекается с записью и изменяемым кодом, IRQ и повторный вход исключены, обработчик сам DI не выполняет'],
    ['при Mode=0 действует RequestPairedAimLines, хвостовой JP не создаёт дополнительного возврата',
     'при ненулевом Mode и отрицательном Target0 HL, DE и BC сохраняются, A равен Target0, F соответствует OR A, RAM и paging сохраняются',
     'при High первой компоненты=80 или StateCode не 04 Target0 получает FF, A=FF, F сохраняет соответствующий CP, HL указывает проверенное поле',
     'при принятой записи OffsetScaleLow получает 0, три компоненты подтягиваются к диапазону -256..255 с шагом 50, SavedSP получает входной SP-2',
     'если близки не все оси, HL указывает запись, D сохраняется, E равно числу близких осей, BC равен последнему шагу 0000 либо FFCE, A=E и F от CP E,3',
     'когда близки все оси, Target0 получает FF до проверок вместимости, полный алгоритм вида, количества и отказов приведён в документации',
     'при успехе байт Row00+вид и Used обновлены, первая компонента получает 8000, при бите 4 ReuseByte устанавливается бит 2 PanelEvents.Flags',
     'после успеха HL=EE1B, DE указывает выбранный байт груза, B содержит новый либо сохранённый Used, C содержит количество',
     'A содержит младший адрес ReuseByte, F соответствует BIT 4 этого поля, CursorA получает EE1B и в очередь передаётся F36D',
     "при ненулевом Mode HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, внешнее завершение даёт SP=входной SP+2",
     'SP временно указывает прямо на три компоненты, обычный SP восстанавливается до последующих проверок и очереди',
     'после сообщения итоговая страница 10, прочие пути сохраняют paging, отказ очереди не отменяет сбор'],
    ['HL, DE, BC, AF, AF\' на прицельном пути, R, временный SP, SavedSP, координаты и поля записи, Target0, байт груза, Used, флаг события, CursorA, очередь, paging и временный CPU-стек по пути'],
    ['не исправлены оборачивание сумм, снятие Target0 до отказа, байтовая индексация пар груза и чтение двух правил из байтов следующей инструкции',
     'для класса 13 количество и вид читаются из Unknown11 и PickupKind, для класса 10 выбран вид 0F, иначе 1B, количество 1..8 получено из R',
     '264679 сценариев исполняют обработчик до внешнего RET, четыре прицельных сценария действительно рисуют обе линии',
     'сверены регистры кроме полного итогового R и тактов, RAM и кратность записей вне восемнадцати обычных временных байтов стека',
     'M1 до чтения R учтены отдельно, аппаратные IRQ и нативная игра не выполнялись'])}
COMMENTS={
 0x7317:(['Проверка существующего байта Mode, его меняет команда силового луча.'],None),
 0x731A:([],'переход, если Mode равен нулю, передать управление прицельному запросу без рамки CALL'),
 0x731D:(['Проверка знака полного кода Target0, отрицательные значения не преобразуются в адрес.'],None),
 0x7321:([],'выход, если Target0 отрицательный, сохранить запись и захват'),
 0x7322:(['Расчёт адреса по исходному коду, преобразователь не проверяет доступность записи.'],None),
 0x7325:(['Проверка старшего байта первой компоненты на код недоступности 80.'],None),
 0x7329:([],'переход, если старший байт равен 80, снять Target0'),
 0x732B:(['Расчёт адреса StateCode от старшего байта первой компоненты и проверка состояния 04.'],None),
 0x7332:([],'переход, если StateCode равен 04, подготовить притягивание'),
 0x7334:(['Снятие недоступного либо неподходящего захвата, саму запись не изменять.'],None),
 0x733A:(['Обнуление OffsetScaleLow до обработки трёх компонент.'],None),
 0x7340:(['Восстановление базы записи от адреса OffsetScaleLow и сохранение обычного SP после PUSH базы.'],None),
 0x7348:(['Преобразование трёх компонент в стек данных, IRQ не должны использовать этот временный SP.'],None),
 0x734A:(['Создание счётчика компонент со старшим байтом 00 либо FF.'],None),
 0x734C:(['Подготовка отрицательного шага для первой компоненты, знак выбирается по исходному старшему байту.'],None),
 0x7351:([],'переход, если первая компонента неотрицательная, проверить её старший байт без инверсии'),
 0x7355:(['Проверка свёрнутого старшего байта, нуль соответствует исходному 00 либо FF.'],None),
 0x7356:([],'переход, если первая компонента вне близкого диапазона, оставить шаг минус 50'),
 0x7358:(['Учёт близкой первой оси без изменения её слова.'],None),
 0x735E:([],'переход, если первая компонента отрицательная, вычесть отрицательный шаг'),
 0x7360:(['Уменьшение положительной первой компоненты на 50, при близком слове шаг равен нулю.'],None),
 0x7364:(['Увеличение отрицательной первой компоненты на 50, при близком слове шаг равен нулю.'],None),
 0x7366:(['Обновление первой компоненты через PUSH и продвижение стека к следующему слову.'],None),
 0x736A:(['Подготовка того же исходного шага для второй компоненты.'],None),
 0x736F:([],'переход, если вторая компонента неотрицательная, проверить старший байт без инверсии'),
 0x7373:(['Проверка близкого диапазона второй компоненты.'],None),
 0x7374:([],'переход, если вторая компонента вне близкого диапазона, оставить шаг минус 50'),
 0x7376:(['Учёт близкой второй оси с нулевым шагом.'],None),
 0x737C:([],'переход, если вторая компонента отрицательная, вычесть отрицательный шаг'),
 0x737E:(['Уменьшение положительной второй компоненты на 50 либо сохранение близкой.'],None),
 0x7382:(['Увеличение отрицательной второй компоненты на 50 либо сохранение близкой.'],None),
 0x7384:(['Обновление второй компоненты и продвижение стека к третьему слову.'],None),
 0x7388:(['Подготовка того же исходного шага для третьей компоненты.'],None),
 0x738D:([],'переход, если третья компонента неотрицательная, проверить старший байт без инверсии'),
 0x7391:(['Проверка близкого диапазона третьей компоненты.'],None),
 0x7392:([],'переход, если третья компонента вне близкого диапазона, оставить шаг минус 50'),
 0x7394:(['Учёт близкой третьей оси с нулевым шагом.'],None),
 0x739A:([],'переход, если третья компонента отрицательная, вычесть отрицательный шаг'),
 0x739C:(['Уменьшение положительной третьей компоненты на 50 либо сохранение близкой.'],None),
 0x73A0:(['Увеличение отрицательной третьей компоненты на 50 либо сохранение близкой.'],None),
 0x73A2:(['Обновление третьей компоненты перед восстановлением обычного CPU-стека.'],None),
 0x73A3:(['Восстановление SP из операнда SavedSP, записанного до установки стека данных.'],None),
 0x73A7:(['Проверка числа близких осей после обновления всех трёх слов.'],None),
 0x73AA:([],'выход, если близки не все три оси, сохранить Target0 для следующего притягивания'),
 0x73AB:(['Снятие Target0 до проверок вместимости, последующие отказы его не восстанавливают.'],None),
 0x73B1:(['Расчёт адреса ClassCode и проверка класса 13 с собственными видом и количеством.'],None),
 0x73B8:([],'переход, если ClassCode равен 13, прочитать полный байт вида и количества из записи'),
 0x73BA:(['Проверка класса 10, он выбирает вид 0F, остальные классы вид 1B.'],None),
 0x73BE:([],'переход, если ClassCode равен 10, сохранить уже выбранный вид 0F'),
 0x73C2:(['Расчёт количества 1..8 из фактического R после исходных M1, программный генератор не вызывается.'],None),
 0x73C9:(['Чтение полного PickupKind как вида и Unknown11 как количества, ограничения диапазона нет.'],None),
 0x73D2:(['Расчёт адреса правила 741D+вид, после 28 самостоятельных байтов чтение продолжается в код.'],None),
 0x73D9:(['Чтение Used и поля учёта из двух старших битов правила.'],None),
 0x73E1:([],'переход, если поле учёта C0 ненулевое, сохранить Used без проверки его кандидата'),
 0x73E3:(['Расчёт кандидата Used по модулю 256, перенос суммы не используется для отказа.'],None),
 0x73E6:(['Проверка беззнакового Capacity против обёрнутого кандидата.'],None),
 0x73EA:([],'выход, если Capacity меньше кандидата, Target0 уже снят, объект остаётся активным'),
 0x73EB:(['Расчёт байтового адреса Row00+вид, размер двухбайтовой записи здесь не учитывается.'],None),
 0x73F2:(['Расчёт нового байта груза по модулю 256 и проверка границы 201.'],None),
 0x73F6:([],'выход, если обёрнутый новый байт не меньше 201, ничего не записывать в груз и Used'),
 0x73F7:(['Обновление выбранного байта и Used только после обеих проверок.'],None),
 0x73FC:(['Отметка собранной записи недоступным словом 8000 в первой компоненте.'],None),
 0x7401:(['Расчёт адреса ReuseByte и проверка его бита 4 после отметки записи.'],None),
 0x7407:([],'переход, если бит 4 ReuseByte сброшен, не устанавливать бит 2 события'),
 0x7409:(['Установка бита 2 существующего поля событий при помеченной записи.'],None),
 0x740E:(['Выбор звукового потока и сообщения о подборе после необратимого изменения состояния.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x7317:return operation
    replacements={'(#9B1B)':'(@ActionMissileTargets.Value.Target0)',
        '(#73A4)':'(@ActionTractorCollectState.SavedSP)',
        '(#9BD2)':'(@ActionFlightTonnage.Value.Used)',
        '(#9BD3)':'(@ActionFlightTonnage.Value.Capacity)',
        'LD HL, #741D':'LD HL, @ActionTractorCargoRules.Kind00.Control',
        'LD HL, #9BD4':'LD HL, @ActionOwnedCargoRows.Row00.QuantityAndMark',
        'LD HL, #A78C':'LD HL, @ActionPanelEvents.Value.Flags',
        'SET 2, (HL)':'SET @ActionPanelEventConst.FixedCostBit, (HL)',
        'LD HL, #EE1B':'LD HL, @ActionTractorCollectConst.Sound',
        '(#ECA9)':'(@ActionAyEffectState.CursorA)',
        'CALL #E6A7':'CALL @Action.RecordIndexToAddress.Entry',
        'JP Z, #63B6':'JP Z, @Action.RequestPairedAimLines.Entry',
        'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry',
        'LD BC, #FFCE':'LD BC, @ActionTractorCollectConst.NegativeStep',
        'CP #03':'CP @ActionTractorCollectConst.CloseAxes',
        'CP #04':'CP @ActionTractorCollectConst.RequiredState',
        'CP #13':'CP @ActionTractorCollectConst.PayloadClass',
        'CP #10':'CP @ActionTractorCollectConst.AlternateClass',
        'CP #80':'CP @ActionTractorCollectConst.InactiveHigh',
        'LD (HL), #80':'LD (HL), @ActionTractorCollectConst.InactiveHigh',
        'LD A, #FF':'LD A, @ActionTractorCollectConst.NoTarget',
        'LD E, #0F':'LD E, @ActionTractorCollectConst.AlternateKind',
        'LD E, #1B':'LD E, @ActionTractorCollectConst.DefaultKind',
        'AND #07':'AND @ActionTractorCollectConst.RandomMask',
        'AND #C0':'AND @ActionTractorCollectConst.AccountingMask',
        'CP #C9':'CP @ActionTractorCollectConst.ByteEndLimit',
        'ADD A, #09':'ADD A, @ActionTractorCollectConst.HighToState',
        'ADD A, #06':'ADD A, @ActionTractorCollectConst.StateToValue',
        'SUB #10':'SUB @FActionRecord.OffsetScaleLow',
        'ADD A, #12':'ADD A, @FActionRecord.ClassCode',
        'ADD A, #11':'ADD A, @ActionTractorCollectConst.ClassToKind',
        'ADD A, #EE':'ADD A, @ActionTractorCollectConst.KindToAmount',
        'ADD A, #17':'ADD A, @ActionTractorCollectConst.HighToReuse'}
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.RequestAimOrCollectTarget.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Includes/Variables/Include.inc';text=path.read_text('utf-8');needle='Mode            equ #7318';lines=[];found=0
    for line in text.splitlines():
        if line.startswith(needle):line+='\n                assert Mode == @Action.RequestAimOrCollectTarget.Entry + 1';found+=1
        lines.append(line)
    assert found==1;text='\n'.join(lines)+'\n';assert text.count('                endif')==1
    addition='                ; Существующий операнд восстановления обычного стека после чтения компонент через SP\n                module ActionTractorCollectState\n'
    addition+='SavedSP         equ #73A4'.ljust(80)+'; обычный SP после PUSH базы, подставляется в LD SP,nn по RestoreStack\n'
    addition+='                assert SavedSP == @Action.RequestAimOrCollectTarget.RestoreStack + 1\n                endmodule\n\n'
    pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')
    path=root/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    addition='                ; Исходные параметры притягивания и байтового сбора, новые области не выделяются\n                module ActionTractorCollectConst\n'
    for name,value,description in (
        ('PullStep','#32','шаг компоненты 50, единицы не установлены'),('NegativeStep','#FFCE','отрицательный шаг для исходных ADD и SBC'),
        ('CloseAxes','#03','все три старших байта должны быть 00 либо FF'),('RequiredState','#04','допускаемое StateCode захваченной записи'),
        ('PayloadClass','#13','класс со своими байтами вида и количества'),('AlternateClass','#10','класс, выбирающий вид 0F'),
        ('InactiveHigh','#80','полный код недоступности в старшем байте первой компоненты'),('NoTarget','#FF','полный код снятого захвата'),
        ('AlternateKind','#0F','вид для класса 10'),('DefaultKind','#1B','вид для остальных непрофильных классов'),
        ('RandomMask','#07','маска R перед прибавлением единицы'),('AccountingMask','#C0','маска двухбитового поля учёта Used'),
        ('ByteEndLimit','#C9','первая запрещённая сумма байта, 201'),('Sound','#EE1B','исходный поток AY после принятого сбора'),
        ('HighToState','#09','разность StateCode и High первой компоненты'),('StateToValue','#06','разность OffsetScaleLow и StateCode'),
        ('ClassToKind','#11','разность PickupKind и ClassCode'),('KindToAmount','#EE','разность Unknown11 и PickupKind по модулю 256'),
        ('HighToReuse','#17','разность ReuseByte и High первой компоненты')):
        addition+=(name.ljust(16)+'equ '+value).ljust(80)+'; '+description+'\n'
    addition+='                assert NegativeStep == #10000 - PullStep\n'
    addition+='                assert HighToState == FActionRecord.StateCode - FActionRecord.Components.Component0.High\n'
    addition+='                assert StateToValue == FActionRecord.OffsetScaleLow - FActionRecord.StateCode\n'
    addition+='                assert ClassToKind == FActionRecord.PickupKind - FActionRecord.ClassCode\n'
    addition+='                assert KindToAmount == #100 + FActionRecord.Unknown11 - FActionRecord.PickupKind\n'
    addition+='                assert HighToReuse == FActionRecord.ReuseByte - FActionRecord.Components.Component0.High\n'
    addition+='                endmodule\n\n';pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')
    # Документирование двух байтов правил внутри настоящей инструкции следующего обработчика, без второго вывода данных.
    path=root/'Source/Action/ToggleTractorMode.asm';text=path.read_text('utf-8');needle='Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)';assert text.count(needle)==1
    text=text.replace(needle,'                ; Байт опкода 3A и младший байт адреса 5F также читаются как правила видов 28 и 29.\n                ; Перекрытие [сбора объекта и кода](../../Docs/ActionTractorCollect.md), дополнительные байты не выводятся.\n'+needle)
    pending[path]=text.encode('utf-8')
