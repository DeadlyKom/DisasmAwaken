"""Команда трёх режимов отображения целей и фактическое переполнение байта."""
TAG='ActionOverlayModeCommand'
TITLE='смена режима отображения целей'
CASES=1280
FUNCTIONS={0x7480:('CycleTargetOverlayMode','Смена режима отображения целей при наличии системы наведения')}
ENDS={0x7480:0x74A3}
LOCAL={0x7499:'StoreMode'}
KEYS={0x7480:0x11}
MUTATIONS=((0x7487,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
    (0x7499,0xAA9A,1,0xAA99,'Source/Action/UpdateFrame.asm'),
    (0x749F,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'))
CONTRACTS={('Action',0x7480):(
    ['HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт',
     'CommandDelay допускает команду только при нуле, Guidance.Value=FF означает отсутствие оборудования',
     'Mode является исходным байтовым операндом UpdateFrame, выбран банк 0 для записи потока AY',
     'на CPU-стеке читаемое слово возврата, IRQ не вмешиваются'],
    ['при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, записи отсутствуют',
     'при нулевой задержке CommandDelay получает 10 до проверки оборудования',
     'при Guidance.Value=FF HL, DE и BC сохраняются, A=0, F=50, Mode и CursorA не меняются',
     'при наличии оборудования t=(старый Mode+1) AND FF, новый Mode=t при t<4, иначе 1',
     'при принятом изменении HL=EE02, DE и BC сохраняются, A равен новому Mode, F остаётся результатом CP t,4',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен исходному SP+2",
     'порты не используются, CursorA получает EE02, временных записей CPU-стека нет'],
    ['HL, AF, R, CommandDelay, Mode и CursorA на соответствующих путях'],
    ['нормальный цикл 1, 2, 3, 1 не охватывает все байтовые входы, FF превращается в 00',
     'Mode=1 пропускает ToggleTargetOverlay, Mode=2 передаёт A=1 для коротких рамок, Mode=3 передаёт A=2 для полного прохода',
     'новый Mode=0 также разрешает полный проход, поскольку DEC даёт FF, это исходное поведение',
     '1280 сценариев сверяют всю RAM и архитектурные регистры кроме R и тактов, нативный вывод рамок этим не проверяется'])}
COMMENTS={
 0x7480:(['Проверка задержки перед обработкой команды смены отображения.'],None),
 0x7484:([],'выход, если CommandDelay ненулевой, режим сохранить'),
 0x7485:(['Обновление задержки даже при последующем отказе по отсутствию оборудования.'],None),
 0x748A:(['Проверка полного кода Guidance.Value, только FF запрещает команду.'],None),
 0x748E:([],'выход, если Guidance.Value равен FF, режим и звуковой поток сохранить'),
 0x748F:(['Расчёт следующего байтового режима, INC сохраняет оборачивание FF в 00.'],None),
 0x7495:([],'переход, если увеличенный байт меньше 4, сохранить его вместе с возможным нулём'),
 0x7497:(['Возврат к первому режиму после значений 3..FE.'],None),
 0x7499:(['Обновление исходного операнда режима в UpdateFrame.'],None),
 0x749C:(['Выбор исходного потока подтверждения смены отображения в AY-канале A.'],None),
 0xAA99:(['Чтение режима отображения, 1 пропускает вызов, 2 выбирает короткие рамки, 3 полный проход.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x7480:return operation
    for before,after in {'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
        '(#9C25)':'(@ActionShipEquipment.Guidance.Value)',
        '(#AA9A)':'(@ActionOverlayModeState.Mode)',
        '(#ECA9)':'(@ActionAyEffectState.CursorA)',
        '#7499':'@Action.CycleTargetOverlayMode.StoreMode'}.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Source/Action/UpdateFrame.asm';text=path.read_text('utf-8')
    needle='LD (#5A1A), A\n                LD A, #00\n                DEC A'
    assert text.count(needle)==1
    replacement='LD (#5A1A), A\n                ; Чтение режима отображения, 1 пропускает вызов, 2 выбирает короткие рамки, 3 полный проход.\nOverlayMode:    LD A, #00\n                DEC A'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    assert 'Action.UpdateFrame.OverlayMode' not in symbols;symbols['Action.UpdateFrame.OverlayMode']=0xAA99
    path=root/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    addition='                ; Существующий изменяемый операнд отображения, память не выделяется\n                module ActionOverlayModeState\n'
    addition+='Mode            equ #AA9A'.ljust(80)+'; режим, 1 без отображения, 2 короткие рамки, 3 полный проход\n'
    addition+='                assert Mode == @Action.UpdateFrame.OverlayMode + 1\n                endmodule\n\n'
    pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')
    path=root/'Tools/Disasm/Research/SemanticNames.py';text=pending[path].decode('utf-8')
    pending[path]=(text+"LABELS['Action',0xAA99]='OverlayMode'\n").encode('utf-8')
