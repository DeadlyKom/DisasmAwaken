"""Падающий фронт общего запроса, однокадровые защёлки и исходное фазовое затухание."""
FUNCTIONS={0x6F55:('LatchControlsAndDecay','Фиксация запросов управления и фазовое приближение трёх знаковых величин к нулю')}
LOCAL={0x6F76:'ClearRequest',0x6FA6:'ReduceX',0x6FAC:'StoreX',0x6FAF:'LatchY',0x6FDB:'ReduceY',0x6FE1:'StoreY',
    0x6FE4:'LatchTurn',0x700D:'ReduceTurn',0x7013:'StoreTurn'}
LABELS={('Action',a):name for a,name in LOCAL.items()}
RENAMES={'Action.Unknown6F55.Entry':'Action.LatchControlsAndDecay.Entry'}
RENAMES.update({'Action.Unknown6F55.Point'+format(a,'04X'):'Action.LatchControlsAndDecay.'+name for a,name in LOCAL.items()})
CONTINUATIONS={}
CONTRACTS={('Action',0x6F55):(
    ['HL, DE, BC, AF входных аргументов не задают, сохраняемые части зависят от падающего фронта Request',
     'Request и SkipDetail содержат текущий и предыдущий общие запросы, X/Y/TurnPrev и Next задают защёлки каналов',
     'X/Y/TurnPhase содержат полные байты кольцевой фазы, XControl, YControl, TurnControl содержат signed8',
     'операнды стабильны при чтении, на падающем фронте доступны процедуры и конечный список ReleaseClass14Records банка 0',
     'перенесённый ACTION банка 5 доступен, CPU-стек допускает шесть дополнительных байтов и внешний возврат, IRQ не вмешиваются'],
    ['HL=0088, D=14, BC=0040 и IY указывает маркер только при Request=0 и прежнем SkipDetail не ноль',
     'иначе HL, DE, B и IY сохраняются, C=прежний SkipDetail',
     'E, альтернативные регистры и IX сохраняются, I, IM, IFF и 7FFD сохраняются, SP=входной SP+2',
     'SkipDetail получает прежний Request, Request обнулён, каждый Prev получает соответствующий Next',
     'канал со старым Prev не ноль пропущен, остальные сбрасывают пару операндов, вращают Phase и при прежнем бите 0 равном единице сдвигают signed8 к нулю',
     'на падающем фронте освобождён класс 14, LimitWord и SignedWord равны 0088, SixthRequest=1',
     'AF определяется последним каналом, точные формулы и R приведены в документации'],
    ['HL и D только на падающем фронте, BC, AF, IY только на падающем фронте, R, существующие операнды, поля освобождённых записей и шесть временных байтов стека'],
    ['ветвление использует старый Prev, хотя новое Next уже записано, это исходная задержка одного вызова',
     'Phase является восьмибитным циклическим сдвигом, для исходного 92 затухание допускают три из восьми фаз при непрерывном разрешении',
     'переход signed8 от FF к нулю использует XOR и возвращает F=44, нулевой неизменяемый канал после AND возвращает F=54',
     '462929 сценариев проверили все пары общих запросов, фаз и значений, старых и новых запретов каждого канала',
     'проверены настоящие дочерние процедуры, все позиции класса 14 в трёх состояниях, регистры включая R, RAM и записи стека',
     'проверка использует банк 0 для настоящего освобождения, полное произведение входов, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
0x6F55:(['Проверка текущего общего запроса Request, прежнее значение SkipDetail загружается в C до его обновления.'],None),
0x6F5A:(['Обновление SkipDetail текущим запросом без изменения флагов проверки Request.'],None),
0x6F5D:([], 'переход, если Request ненулевой, пропустить обработку падающего фронта'),
0x6F5F:(['Проверка прежнего общего запроса, падение существует только при прежнем ненулевом C.'],None),
0x6F60:([], 'переход, если прежний запрос также нулевой, падающего фронта нет'),
0x6F62:(['Освобождение всех активных записей класса 14 настоящим повторным поиском.'],None),
0x6F65:(['Обновление исходного ограничивающего слова и рабочего SignedWord значением 0088.'],None),
0x6F71:(['Создание запроса перерисовки шестой шкалы после сброса SignedWord.'],None),
0x6F76:(['Обнуление накопленного общего Request, SkipDetail сохраняет его значение до следующего вызова.'],None)}
for start,branch,defaults,phase,phase_branch,load,zero,positive,add,negative,reduce,reduce_branch,store,label in (
    (0x6F7A,0x6F82,0x6F84,0x6F8C,0x6F92,0x6F94,0x6F98,0x6F9A,0x6F9D,0x6F9F,0x6FA6,0x6FA8,0x6FAC,'X'),
    (0x6FAF,0x6FB7,0x6FB9,0x6FC1,0x6FC7,0x6FC9,0x6FCD,0x6FCF,0x6FD2,0x6FD4,0x6FDB,0x6FDD,0x6FE1,'Y'),
    (0x6FE4,0x6FEC,0x6FED,0x6FF5,0x6FFB,0x6FFC,0x7000,0x7001,0x7004,0x7006,0x700D,0x700F,0x7013,'Turn')):
    final=label=='Turn';verb='выход' if final else 'переход'
    COMMENTS[start]=(['Проверка старого '+label+'Prev, затем запись '+label+'Next для следующего вызова без замены проверяемых флагов.'],None)
    COMMENTS[branch]=([],verb+', если старый '+label+'Prev ненулевой, пропустить затухание канала')
    COMMENTS[defaults]=(['Обновление двух исходных байтов накопления клавиатурных обработчиков канала '+label+'.'],None)
    COMMENTS[phase]=(['Расчёт следующей кольцевой '+label+'Phase, исходный литерал 92 является изменяемым операндом.'],None)
    COMMENTS[phase_branch]=([],verb+', если прежний бит 0 фазы нулевой, в этом вызове затухание запрещено')
    COMMENTS[load]=(['Проверка текущего знакового управления '+label+', нулевое значение не записывается повторно.'],None)
    COMMENTS[zero]=([],verb+', если управление уже нулевое, сохранить его без записи')
    COMMENTS[positive]=([], 'переход, если управление положительное, уменьшить его на единицу')
    COMMENTS[add]=(['Расчёт шага отрицательного signed8 к нулю, FF требует отдельного обнуления через XOR.'],None)
    COMMENTS[negative]=([], 'переход, если результат прибавления ещё отрицательный, записать его')
    COMMENTS[reduce]=(['Расчёт шага положительного signed8 к нулю.'],None)
    COMMENTS[reduce_branch]=([], 'переход, если результат вычитания неотрицательный, записать его')
    COMMENTS[store]=(['Обновление соответствующего байта управления с сохранением флагов выбранного арифметического пути.'],None)
CONST_BLOCK='\n                ; Исходные значения сброса управления и накопителей клавиатурных каналов\n                module ActionControlDecayConst\n'
for name,value,note in (('ResetWord',0x88,'значение LimitWord и SignedWord на падающем фронте'),('RequestOn',1,'запрос перерисовки шкалы'),
    ('XYReset',200,'исходный байт сброса двух накопителей X либо Y'),('TurnReset',250,'исходный байт сброса накопителей поворота'),
    ('PhaseSeed',0x92,'начальный восьмибитный цикл, три единичных бита'),('StepUnit',1,'шаг signed8 к нулю')):
    CONST_BLOCK+=name.ljust(16)+('equ #'+format(value,'04X' if name=='ResetWord' else '02X')).ljust(64)+'; '+note+'\n'
CONST_BLOCK+='                endmodule\n\n'
STRUCT_BLOCK=('\n                ; Динамическая рамка внутри NextActiveRecord при падающем фронте Request\n'+
    '                struct FControlDecayFrame\n'+
    'ReturnIterator'.ljust(16)+'dw #E997'.ljust(64)+'; возврат итератора в FindRecordByCode\n'+
    'ReturnFindCode'.ljust(16)+'dw #6177'.ljust(64)+'; возврат поиска в ReleaseClass14Records\n'+
    'ReturnRelease'.ljust(16)+'dw #6F65'.ljust(64)+'; возврат освобождения в обработку падающего фронта\n'+
    'CallerReturn'.ljust(16)+'dw #0000'.ljust(64)+'; внешний возврат LatchControlsAndDecay\n'+
    '                ends\n                assert FControlDecayFrame == #08\n\n')
FIELDS=(('Request',0x6F56,'текущий общий запрос, очищается после переноса в SkipDetail'),
    ('XPrev',0x6F7B,'старый запрет затухания X, проверяется до замены'),('XNext',0x6F7E,'новый запрет X для следующего вызова'),('XPhase',0x6F8D,'восьмибитная кольцевая фаза X'),
    ('YPrev',0x6FB0,'старый запрет затухания Y'),('YNext',0x6FB3,'новый запрет Y для следующего вызова'),('YPhase',0x6FC2,'восьмибитная кольцевая фаза Y'),
    ('TurnPrev',0x6FE5,'старый запрет затухания поворота'),('TurnNext',0x6FE8,'новый запрет поворота для следующего вызова'),('TurnPhase',0x6FF6,'восьмибитная кольцевая фаза поворота'),
    ('LimitWord',0x7693,'исходный операнд LD DE,nn обработчика 7680, игровой смысл ограничения ещё не полностью установлен'),
    ('XStep0',0x7736,'байтовый операнд обработчика 7730'),('XStep1',0x7713,'байтовый операнд обработчика 770D'),
    ('YStep0',0x7759,'байтовый операнд обработчика 7753'),('YStep1',0x777C,'байтовый операнд обработчика 7776'),
    ('TurnStep0',0x76CD,'байтовый операнд обработчика 76C7'),('TurnStep1',0x76F0,'байтовый операнд обработчика 76EA'))


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x6F55):return operation
    for name,value,_ in FIELDS:operation=operation.replace('#'+format(value,'04X'),'@ActionControlDecayState.'+name)
    for value,name in ((0x6F59,'ActionProjectionClipState.SkipDetail'),(0x669F,'ActionPanelGaugesState.SixthRequest'),
        (0xA78F,'ActionPanelGaugesState.SignedWord'),(0x9B95,'ControlsPointMotionState.YControl'),
        (0x9B96,'ControlsPointMotionState.XControl'),(0x9B97,'ControlsPointMotionState.TurnControl')):
        operation=operation.replace('#'+format(value,'04X'),'@'+name)
    return operation.replace('#0088','@ActionControlDecayConst.ResetWord').replace('LD A, #01','LD A, @ActionControlDecayConst.RequestOn').replace('#C8','@ActionControlDecayConst.XYReset').replace('#FA','@ActionControlDecayConst.TurnReset').replace('#92','@ActionControlDecayConst.PhaseSeed').replace('ADD A, #01','ADD A, @ActionControlDecayConst.StepUnit').replace('SUB #01','SUB @ActionControlDecayConst.StepUnit')


def qualify_mutations(records,regions,functions):
    from CheckActionParameterActivation import flat_action
    from InspectZ80 import decoder
    flat=flat_action();source='Source/Action/LatchControlsAndDecay.asm'
    # Проверка границ ещё не классифицированных обработчиков по исходным адресам таблицы клавиш.
    for writer,target,entry,size in ((0x6F68,0x7693,0x7680,2),(0x6F86,0x7736,0x7730,1),(0x6F89,0x7713,0x770D,1),
        (0x6FBB,0x7759,0x7753,1),(0x6FBE,0x777C,0x7776,1),(0x6FEF,0x76CD,0x76C7,1),(0x6FF2,0x76F0,0x76EA,1)):
        assert entry in [flat[a]+256*flat[a+1] for a in range(0x7017,0x704B,2)]
        decoded={i.address:i for i in decoder(flat).disassemble(entry,target+size,'h')};instruction=decoded[target-1]
        assert instruction.bytes==bytes((0x11,0x88,0)) if size==2 else instruction.bytes==bytes((0x3E,0))
        existing=next((m for m in records if m['region']=='Action' and m['writer']==writer),None)
        if existing is None:
            existing=dict(region='Action',writer=writer,target=target,target_instruction=target-1,size=size,
                target_operation=instruction.operation,path=source);records.append(existing)
        existing.update(target_region='Action',target_bank=5,target_slot=17,target_offset=target-0x6000+0x23D,
            target_source_classified=False,target_original_hex=instruction.bytes.hex(),
            target_instruction_boundary_proof='linear_decode_from_original_keyboard_handler_table_entry')
    for item in records:
        if item['region']=='Action' and 0x6F55<=item['writer']<0x7017:
            item.update(writer_bank=5,writer_offset=item['writer']-0x6000+0x23D,writer_source_classified=True)
            if 0x6F55<=item['target']<0x7017:
                item.update(target_region='Action',target_bank=5,target_slot=17,target_offset=item['target']-0x6000+0x23D,
                    target_source_classified=True,target_path=source)
    records.sort(key=lambda m:(m['region'],m['writer'],m['target']))
