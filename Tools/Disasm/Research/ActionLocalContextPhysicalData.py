"""Физические поля сравнения контекста, поправок и двух независимых счётчиков."""
from PreviewSceneTables import render as render_records,parse as parse_records

PAIR_FIELDS=(('OtherFirst',2,'первое слово для сравнения с SeedFirst'),('OtherSecond',2,'второе слово для сравнения с SeedSecond'))
INDEX_FIELDS=(('SelectedIndex',1,'байт публикации при совпадении обеих пар контекста'),)
GATE_FIELDS=(('Value',1,'знаковое сложение поправок и беззнаковые пороговые сравнения, игровой смысл неизвестен'),)
ARRIVAL_FIELDS=(('Value',2,'счётчик ближнего завершения по модулю 65536, полный игровой смысл неизвестен'),)
LIMIT_FIELDS=(('Current',1,'младший байт E, кандидат пополнения увеличивается по модулю 256'),
              ('Limit',1,'старший байт D, беззнаковый предел кандидата E'))
TABLES=(
    (17,0x6000,('ActionOtherContext','Source/Action/Data/OtherContext.asm',0x3BC6,0x3BCA,'FContextWordPair',PAIR_FIELDS,('Value',))),
    (17,0x6000,('ActionContextIndex','Source/Action/Data/ContextIndex.asm',0x3BCA,0x3BCB,'FContextPublishIndex',INDEX_FIELDS,('Value',))),
    (17,0x6000,('ActionIndexedGate','Source/Action/Data/IndexedGate.asm',0x3BCD,0x3BCE,'FIndexedGateValue',GATE_FIELDS,('Value',))),
    (17,0x6000,('ActionArrivalCounter','Source/Action/Data/ArrivalCounter.asm',0x3BCE,0x3BD0,'FArrivalCounter',ARRIVAL_FIELDS,('Value',))),
    (17,0x6000,('ActionByteLimitCounter','Source/Action/Data/ByteLimitCounter.asm',0x3BD2,0x3BD4,'FByteLimitCounter',LIMIT_FIELDS,('Value',))),
)
BINDINGS=(('ActionContextWordPairsState','OtherFirst',0x9BC6,'ActionOtherContext.Value.OtherFirst'),
          ('ActionContextWordPairsState','OtherSecond',0x9BC8,'ActionOtherContext.Value.OtherSecond'),
          ('ActionWideProjectionLoopState','SelectedIndex',0x9BCA,'ActionContextIndex.Value.SelectedIndex'),
          ('ActionPreferredChanceState','UnknownGate',0x9BCD,'ActionIndexedGate.Value.Value'),
          ('ActionArrivalState','ArrivalCount',0x9BCE,'ActionArrivalCounter.Value.Value'))
REQUIRED_REPORTS=('ActionContextWordPairsVerification','ActionWideProjectionLoopVerification',
                  'ActionTypeDeltaVerification','ActionArrivalStateVerification',
                  'ActionBodyVectorPanelVerification','ActionMissileConsumeVerification')
DOCUMENT='ActionLocalContextPhysicalData'
TAG='ActionLocalContextPhysicalData'


def validate_sources(sources):
    data=sources[17]
    # Проверка исходных инициализаторов независимо от их будущей игровой интерпретации.
    assert data[0x3BC6:0x3BCB]==bytes((0x38,0x4B,0xF4,0x4A,2))
    assert data[0x3BCD:0x3BD0]==bytes(3) and data[0x3BD2:0x3BD4]==bytes((0,40))
    return dict(context_pair_bytes=4,publish_index_bytes=1,indexed_gate_bytes=1,
                arrival_counter_bytes=2,byte_limit_counter_bytes=2,
                full_game_meaning_proved=False,adjacent_unreferenced_bytes_classified=False)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[локальные поля контекста](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():
    lines=[]
    for name,fields in (('FContextWordPair',PAIR_FIELDS),('FContextPublishIndex',INDEX_FIELDS),
                        ('FIndexedGateValue',GATE_FIELDS),('FArrivalCounter',ARRIVAL_FIELDS),('FByteLimitCounter',LIMIT_FIELDS)):
        lines+=['                ; Физические поля существующего контекста ACTION',
                '                struct '+name]
        offset=0;assertions=[]
        for field,width,meaning in fields:
            lines.append((field.ljust(16)+('db #00' if width==1 else 'dw #0000')).ljust(80)+'; '+meaning)
            assertions.append('                assert '+name+'.'+field+' == '+str(offset));offset+=width
        lines+=['                ends','                assert '+name+' == '+str(offset),*assertions,'']
    return '\n'.join(lines)+'\n'
