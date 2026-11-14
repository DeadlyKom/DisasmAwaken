"""Существующие физические источники панели, маска событий и четыре BCD-пары."""
from PreviewSceneTables import render as render_records,parse as parse_records

BCD_FIELDS=(('MidHigh',1,'BCD-пара разрядов 10^4 и 10^5, регистр E'),
            ('High',1,'BCD-пара разрядов 10^6 и 10^7, регистр D'),
            ('Low',1,'BCD-пара разрядов 10^0 и 10^1, регистр L'),
            ('MidLow',1,'BCD-пара разрядов 10^2 и 10^3, регистр H'))
WORD_FIELDS=(('Value',2,'знаковая скорость для вектора движения и шестой шкалы'),)
LEVEL_FIELDS=(('Value',1,'уровень защиты игрока SHILD, источник первой шкалы'),)
EVENT_FIELDS=(('Flags',1,'UpdateFrame использует биты 0, 1 и 2, остальные биты не интерпретируются'),)
TABLES=(
    (17,0x6000,('ActionFlightCounter','Source/Action/Data/FlightCounter.asm',0x3BBD,0x3BC1,
                'FFlightBcdCounter',BCD_FIELDS,('Value',))),
    (17,0x6000,('ActionPanelEvents','Source/Action/Data/PanelEvents.asm',0x478C,0x478D,
                'FPanelEventFlags',EVENT_FIELDS,('Value',))),
    (17,0x6000,('ActionPanelSignedWord','Source/Action/Data/PanelSignedWord.asm',0x478F,0x4791,
                'FPanelSignedWord',WORD_FIELDS,('Value',))),
    (17,0x6000,('ActionPanelFirstLevel','Source/Action/Data/PanelFirstLevel.asm',0x4794,0x4795,
                'FPanelGaugeValue',LEVEL_FIELDS,('Value',))),
)
BINDINGS=(('ControlsBcdCounterState','HighPairs',0x9BBD,'ActionFlightCounter.Value.MidHigh'),
          ('ControlsBcdCounterState','LowPairs',0x9BBF,'ActionFlightCounter.Value.Low'),
          ('ActionPanelGaugesState','SpeedWord',0xA78F,'ActionPanelSignedWord.Value.Value'),
          ('ActionPanelGaugesState','FirstValue',0xA794,'ActionPanelFirstLevel.Value.Value'))
REQUIRED_REPORTS=('ControlsBcdCounterVerification','ControlsBcdExactVerification','ActionPanelGaugesVerification',
                  'ActionNearZeroWordVerification','ActionFrameGatesVerification','ActionMutableGaugePhasesVerification')
DOCUMENT='ActionPanelPhysicalData'
TAG='ActionPanelPhysicalData'


def name_operands(region, address, operation):
    if (region, address) != ('Action', 0xA85E):
        return operation
    operands = {
        '(#A78C)': '(@ActionPanelEvents.Value.Flags)',
        '(#A794)': '(@ActionPanelGaugesState.FirstValue)',
        '(#664A)': '(@ActionPanelGaugesState.FirstRequest)',
        '(#666B)': '(@ActionPanelGaugesState.ThirdRequest)',
        '(#6682)': '(@ActionPanelGaugesState.FourthValue)',
        '(#6693)': '(@ActionPanelGaugesState.FifthValue)',
        '(#A8BC)': '(@ActionPanelGaugesState.ThirdValue)',
        '(#ECA9)': '(@ActionAyEffectState.CursorA)',
        '(#ECF6)': '(@ActionAyEffectsState.CursorB)',
        'LD HL, #EF22': 'LD HL, @ActionAyStreams.EventBit0Row00',
        'LD HL, #ED8F': 'LD HL, @ActionAyStreams.EventBit1Row00',
        'BIT 0, C': 'BIT @ActionPanelEventConst.CostBit, C',
        'BIT 1, C': 'BIT @ActionPanelEventConst.BlinkBit, C',
        'BIT 2, C': 'BIT @ActionPanelEventConst.FixedCostBit, C',
    }
    for old, new in operands.items():
        operation = operation.replace(old, new)
    return operation


def validate_sources(sources):
    data=sources[17]
    # Проверка исходных чисел, рабочая инициализация и игровые единицы ими не подменяются.
    assert data[0x3BBD:0x3BC1]==bytes((0x22,0x01,0x10,0x10))
    assert data[0x478C]==0 and data[0x478F:0x4791]==bytes((20,0)) and data[0x4794]==46
    return dict(counter_bytes=4,counter_initial_decimal=1221010,panel_state_bytes=4,
                counter_units_proved=False,full_game_meaning_proved=False)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физическое состояние панели](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():
    lines=[]
    for name,fields in (('FFlightBcdCounter',BCD_FIELDS),('FPanelEventFlags',EVENT_FIELDS),
                        ('FPanelSignedWord',WORD_FIELDS),('FPanelGaugeValue',LEVEL_FIELDS)):
        lines+=['                ; Существующее физическое состояние панели, новая память не выделяется',
                '                struct '+name]
        if name == 'FPanelEventFlags':
            lines.extend(('                ; Разряды 7..0, ? ? ? ? ? F B C, маски C=#01, B=#02, F=#04',
                          '                ; Нулевое значение не запрашивает списание, мигание и связанный звук'))
        offset=0;assertions=[]
        for field,width,meaning in fields:
            op='db #00' if width==1 else 'dw #0000'
            lines.append((field.ljust(16)+op).ljust(80)+'; '+meaning)
            assertions.append('                assert '+name+'.'+field+' == '+str(offset));offset+=width
        lines+=['                ends','                assert '+name+' == '+str(offset),*assertions,'']
    return '\n'.join(lines)+'\n'
