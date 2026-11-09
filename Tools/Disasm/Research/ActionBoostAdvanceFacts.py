"""7504, исходные делители расхода и появления класса 20, шестнадцать шагов шкалы."""
TAG='ActionBoostAdvance'
TITLE='общий хвост ускорения, расход и шестнадцать шагов шкалы'
CASES=69728
FUNCTIONS={0x7504:('AdvanceBoost','Общий хвост ускорения с фазовым расходом выбранного байта, созданием класса 20 и шестнадцатью шагами шкалы')}
ENDS={0x7504:0x754C}
KEYS={}
LOCAL={0x750C:'StepFastPhase',0x7514:'StepSlowPhase',0x752B:'RotateFirst',0x7533:'RotateSecond',0x753C:'SetBoostLimit',0x7544:'IncreaseLoop'}
MUTATIONS=((0x750F,0x750D,1,0x750C,None),(0x7519,0x7515,1,0x7514,None),
 (0x7528,0x665C,1,0x665B,'Source/Action/UpdatePanelGauges.asm'),
 (0x752E,0x752C,1,0x752B,None),(0x7536,0x7534,1,0x7533,None),
 (0x753F,0x7693,2,0x7692,'Source/Action/IncreaseGaugeWord.asm'))
CONTRACTS={('Action',0x7504):(
 ['HL, DE, BC и AF числовых аргументов не задают, вызывающий RequestBoost уже установил Request и не обнаружил препятствия',
  'доступны Preferred и Fallback для SelectPreferredByte, Current, четыре фазовых операнда и LimitWord',
  'действуют договоры ReleaseClass14Records, CreateRandomClass20Record и IncreaseGaugeWord.MotionGate',
  'доступны список записей, Stream8 и коэффициенты преобразования, банк 0 выбран, стек допускает тридцать два дополнительных байта',
  'IRQ и повторный вход исключены, размещение исходных операндов не изменяется'],
 ['SelectPreferredByte возвращает выбранный байт A и его адрес HL, C получает A-1 по модулю 256',
  'при знаке C управление передаётся ReleaseClass14Records, допустимы только выбранные значения 1..128',
  'FastPhase увеличивается по модулю 256, лишь при его переходе в ноль SlowPhase получает (старое+1) AND 7',
  'лишь при двух нулевых результатах выбранный байт получает C, Current уменьшается по модулю 256, SecondRequest получает 1',
  'FirstRotation вращается RRCA всегда на допущенном пути, SecondRotation вращается только при старом бите 0 FirstRotation',
  'лишь при единичном старом бите 0 обоих вращений вызывается настоящий CreateRandomClass20Record, отказ выделения не отменяет дальнейшее ускорение',
  'LimitWord получает 1000 после возможного создания записи, затем IncreaseGaugeWord.MotionGate вызывается шестнадцать раз',
  'проверка SkipDetail по 7680 пропускается, MotionOpcode по 7685 всё ещё должен быть 3A для изменения SignedWord',
  'на обычном завершении B=0, C сохранён из состояния перед циклом, прочие выходы соответствуют последнему шагу шкалы и возможному создателю',
  'без создания альтернативные и индексные регистры сохраняются, при создании действуют его выходы, paging, I, IM и IFF сохраняются',
  'внешний RET даёт SP=входной SP+2, знак ограничения проверяется исходной обёрнутой разностью, общего насыщения нет'],
 ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IY, R по дочерним путям, выбранный байт, Current, фазовые операнды, запросы шкал, LimitWord, SignedWord, запись класса 20 и CPU-стек'],
 ['SecondRequest по 665C относится ко второй шкале, SignedWord дополнительно создаёт SixthRequest по 669F через ребёнка',
  'ноль Current при расходе становится FF, верхние биты SlowPhase отбрасываются только при шаге FastPhase через ноль',
  'изначальные фазы 00/00 и вращения 11/88 сохранены, имена описывают доказанные операции, физический смысл классов не выдумывается',
  '69728 сквозных сценариев исполняют исходные оба фрагмента и настоящих детей, все пары Preferred/Fallback проверены',
  'сверены регистры кроме R и тактов, все банки RAM и кратность записей вне тридцати двух временных байтов стека',
  'полное произведение входов, IRQ, сборка и нативная игра не проверялись'])}
COMMENTS={
 0x7504:(['Выбор существующего ненулевого Preferred либо Fallback вместе с адресом его физического байта.'],None),
 0x7508:(['Проверка знака выбранного значения после уменьшения, допускаются только исходные байты 1..128.'],None),
 0x7509:([],'переход, если A-1 имеет бит 7, освободить класс 14 без расхода и шагов шкалы'),
 0x750C:(['Обновление быстрого фазового операнда по модулю 256.'],None),
 0x7512:([],'переход, если FastPhase не перешёл в ноль, пропустить медленный шаг и расход'),
 0x7514:(['Расчёт следующей медленной фазы, старшие пять битов отбрасываются маской 07.'],None),
 0x751C:([],'переход, если SlowPhase ненулевой, пропустить расход выбранного байта'),
 0x751E:(['Обновление выбранного байта и Current только при совпавшем нуле обеих фаз.'],None),
 0x7526:(['Создание запроса второй шкалы после расхода, нулевой Current исходно оборачивается в FF.'],None),
 0x752B:(['Расчёт первого кольцевого вращения, Carry содержит старый бит 0.'],None),
 0x7531:([],'переход, если старый бит 0 FirstRotation сброшен, пропустить второе вращение и создание'),
 0x7533:(['Расчёт второго вращения, его старый бит 0 допускает создание класса 20.'],None),
 0x7539:([],'вызов, если старый бит 0 SecondRotation установлен, создать запись класса 20'),
 0x753C:(['Обновление существующего LimitWord перед шестнадцатью шагами, новое размещение памяти не создаётся.'],None),
 0x7542:(['Подготовка шестнадцати вызовов внутреннего входа шкалы, проверка SkipDetail пропускается.'],None),
 0x7544:(['Сохранение счётчика и младшего C вокруг каждого настоящего шага шкалы.'],None)}


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0x7504):return operation
    replacements={'CALL #74FB':'CALL @Action.SelectPreferredByte.Entry','JP M, #6172':'JP M, @Action.ReleaseClass14Records.Entry',
      'CALL C, #617D':'CALL C, @Action.CreateRandomClass20Record.Entry',
      'CALL #7685':'CALL @Action.IncreaseGaugeWord.MotionGate',
      '(#665C)':'(@ActionPanelGaugesState.SecondRequest)',
      '(#7693)':'(@ActionControlDecayState.LimitWord)',
      '(#9BD2)':'(@ActionByteLimitCounter.Value.Current)'}
    for address,name in ((0x750D,'FastPhase'),(0x7515,'SlowPhase'),(0x752C,'FirstRotation'),(0x7534,'SecondRotation')):
        replacements['(#'+format(address,'04X')+')']='(@ActionBoostState.'+name+')'
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.AdvanceBoost.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Source/Action/RequestBoost.asm';text=path.read_text('utf-8');assert text.count('#7504')==1
    pending[path]=text.replace('#7504','@Action.AdvanceBoost.Entry').encode('utf-8')
    path=root/'Tools/Disasm/Research/ActionBoostCommandFacts.py';text=path.read_text('utf-8')
    text=text.replace("'JP #6172':'JP @Action.ReleaseClass14Records.Entry'","'JP #6172':'JP @Action.ReleaseClass14Records.Entry',\n      '#7504':'@Action.AdvanceBoost.Entry'")
    pending[path]=text.encode('utf-8')
    path=root/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    block='                ; Существующие операнды фаз ускорения, новая память не выделяется\n                module ActionBoostState\n'
    for name,address,label,note in (('FastPhase',0x750D,'StepFastPhase','байтовая фаза, переполнение допускает шаг SlowPhase'),
      ('SlowPhase',0x7515,'StepSlowPhase','медленная фаза, очередное значение ограничивается маской 07'),
      ('FirstRotation',0x752C,'RotateFirst','первое RRCA, старый бит 0 допускает второе вращение'),
      ('SecondRotation',0x7534,'RotateSecond','второе RRCA, старый бит 0 допускает создание класса 20')):
        block+=(name.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+note+'\n'
        block+='                assert '+name+' == @Action.AdvanceBoost.'+label+'+1\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=root/'Source/Action/IncreaseGaugeWord.asm';text=path.read_text('utf-8')
    needle='                LD A, (@ActionGaugeWordKeysState.MotionOpcode)';assert text.count(needle)==1
    notes=['Внутренний вход MotionGate из AdvanceBoost, проверка SkipDetail уже пропущена.',
      'In:', '  HL, DE, BC и AF числовых аргументов не задают, доступны MotionOpcode, SignedWord и LimitWord',
      'Out:', '  при MotionOpcode не 3A HL, DE и BC сохранены, A равен опкоду, F соответствует CP 3A',
      '  иначе действуют расчёт и выходы основного входа после проверки SkipDetail, внешний RET задаёт SP=входной SP+2',
      'Corrupt:', '  HL, DE, AF, R, SignedWord и SixthRequest только на допущенном пути',
      'Документация [шестнадцать вызовов ускорения](../../Docs/ActionBoostAdvance.md).']
    pending[path]=text.replace(needle,'\n'.join('                ; '+v for v in notes)+'\nMotionGate:     LD A, (@ActionGaugeWordKeysState.MotionOpcode)').encode('utf-8')
    symbols['Action.IncreaseGaugeWord.MotionGate']=0x7685
    path=root/'Tools/Disasm/Research/ActionGaugeWordKeyFacts.py';text=path.read_text('utf-8')
    text=text.replace('local={} if increase else','local={0x7685:\'MotionGate\'} if increase else')
    marker='    def name_operands(region,address,operation):';assert text.count(marker)==1
    text=text.replace(marker,'    if increase:comments[0x7685]=(comments[0x7685][0]+'+repr(notes)+',None)\n'+marker)
    pending[path]=text.encode('utf-8')
    path=root/'Tools/Disasm/Research/SemanticNames.py';text=pending.get(path,path.read_bytes()).decode('utf-8')
    pending[path]=(text+"\nLABELS['Action',0x7685]='MotionGate'\n").encode('utf-8')
