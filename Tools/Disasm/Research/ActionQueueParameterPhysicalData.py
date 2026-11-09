"""Физические поля очереди, длины отсечения и набора изменяемых операндов ACTION."""
from PreviewSceneTables import render as render_records,parse as parse_records
from ActionApplyParametersFacts import TARGETS

QUEUE_FIELDS=(('Head',1,'младшее смещение головы в странице 8F, рабочий конец цепочки 01'),
              ('FreeOffset',1,'смещение следующего узла, рабочий шаг 0E и признак исчерпания FC'))
OUTPUT_FIELDS=(('OutputSize',1,'байтовая длина выходных пар Second, First в странице 90')),
PARAMETER_FIELDS=[]
for index in range(15):
    targets=[(name,address,meaning) for name,address,meaning in TARGETS
             if int(meaning.split(',')[0].split()[1],16)==index]
    if index==1:
        PARAMETER_FIELDS.append(('ReadOnly01',1,'ApplyParameterSet читает поле без записи, отдельный игровой смысл неизвестен'))
    elif index==6:
        PARAMETER_FIELDS.append(('SpawnLowAndBias',1,'общий начальный SpawnLowLimit и база пересчёта SpawnBiasBase'))
    else:
        assert len(targets)==1,(index,targets)
        name,address,meaning=targets[0]
        PARAMETER_FIELDS.append((name,1,meaning+', адрес изменяемого операнда '+format(address,'04X')))
PARAMETER_FIELDS=tuple(PARAMETER_FIELDS)
TABLES=(
    (17,0x6000,('ActionRenderQueueCursor','Source/Action/Data/RenderQueueCursor.asm',0x3BA1,0x3BA3,
                'FRenderQueueCursor',QUEUE_FIELDS,('Value',))),
    (17,0x6000,('ActionClipOutputState','Source/Action/Data/ClipOutputState.asm',0x3BA3,0x3BA4,
                'FClipOutputState',OUTPUT_FIELDS,('Value',))),
    (17,0x6000,('ActionParameterSet','Source/Action/Data/ParameterSet.asm',0x3BA4,0x3BB3,
                'FActionParameterSet',PARAMETER_FIELDS,('Value',))),
)
BINDINGS=(
    ('ActionRenderQueueInsertState','Head',0x9BA1,'ActionRenderQueueCursor.Value.Head'),
    ('ActionRenderQueueInsertState','FreeOffset',0x9BA2,'ActionRenderQueueCursor.Value.FreeOffset'),
    ('ActionClipIntersectionsState','OutputSize',0x9BA3,'ActionClipOutputState.Value.OutputSize'),
    ('ControlsParameterTablesState','Parameters',0x9BA4,'ActionParameterSet.Value.Link1ABaseLimit'),
)
REQUIRED_REPORTS=('ActionRenderQueueInsertVerification','ActionRenderQueueLoadVerification',
                  'ActionClipIntersectionsVerification','ControlsParameterTablesVerification',
                  'ActionApplyParametersVerification','ActionMutableEffectLimitsVerification')
DOCUMENT='ActionQueueParameterPhysicalData'
TAG='ActionQueueParameterPhysicalData'


def validate_sources(sources):
    # Проверка именно исходных инициализаторов, нули не заменяют рабочую инициализацию.
    assert sources[17][0x3BA1:0x3BB3]==bytes(18)
    assert len(PARAMETER_FIELDS)==15 and len(TARGETS)==15
    return dict(queue_cursor_bytes=2,clip_output_size_bytes=1,parameter_bytes=15,
                initial_values_are_working_state=False,all_parameter_game_meanings_proved=False)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[поля очереди и параметров](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():
    lines=[]
    for name,fields in (('FRenderQueueCursor',QUEUE_FIELDS),('FClipOutputState',OUTPUT_FIELDS),
                        ('FActionParameterSet',PARAMETER_FIELDS)):
        lines+=['                ; Физические байты существующего рабочего состояния ACTION',
                '                struct '+name]
        for field,width,meaning in fields:
            assert width==1 and len(field)<=15
            lines.append((field.ljust(16)+'db #00').ljust(80)+'; '+meaning)
        lines+=['                ends','                assert '+name+' == '+str(len(fields))]
        lines+=['                assert '+name+'.'+field+' == '+str(i) for i,(field,width,meaning) in enumerate(fields)]
        lines+=['']
    return '\n'.join(lines)+'\n'
