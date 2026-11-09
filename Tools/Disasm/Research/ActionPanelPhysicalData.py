"""Существующие физические источники панели, маска событий и четыре BCD-пары."""
from PreviewSceneTables import render as render_records,parse as parse_records

BCD_FIELDS=(('MidHigh',1,'BCD-пара разрядов 10^4 и 10^5, регистр E'),
            ('High',1,'BCD-пара разрядов 10^6 и 10^7, регистр D'),
            ('Low',1,'BCD-пара разрядов 10^0 и 10^1, регистр L'),
            ('MidLow',1,'BCD-пара разрядов 10^2 и 10^3, регистр H'))
WORD_FIELDS=(('Value',2,'знаковое слово источника шестой шкалы, полный игровой смысл и единицы неизвестны'),)
LEVEL_FIELDS=(('Value',1,'байтовый источник первой шкалы, полный игровой смысл неизвестен'),)
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
          ('ActionPanelGaugesState','SignedWord',0xA78F,'ActionPanelSignedWord.Value.Value'),
          ('ActionPanelGaugesState','FirstValue',0xA794,'ActionPanelFirstLevel.Value.Value'),
          ('ActionCloseRecordState','UnknownA794',0xA794,'ActionPanelFirstLevel.Value.Value'))
REQUIRED_REPORTS=('ControlsBcdCounterVerification','ControlsBcdExactVerification','ActionPanelGaugesVerification',
                  'ActionNearZeroWordVerification','ActionFrameGatesVerification','ActionMutableGaugePhasesVerification')
DOCUMENT='ActionPanelPhysicalData'
TAG='ActionPanelPhysicalData'


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
        offset=0;assertions=[]
        for field,width,meaning in fields:
            op='db #00' if width==1 else 'dw #0000'
            lines.append((field.ljust(16)+op).ljust(80)+'; '+meaning)
            assertions.append('                assert '+name+'.'+field+' == '+str(offset));offset+=width
        lines+=['                ends','                assert '+name+' == '+str(offset),*assertions,'']
    return '\n'.join(lines)+'\n'
