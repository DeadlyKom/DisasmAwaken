"""Двухбайтовый заголовок текущей модели, сохраняемый в очереди отрисовки."""
from PreviewSceneTables import render as render_records,parse as parse_records
FIELDS=(('ModeBits',1,'бит 0 задаёт одноосный расчёт, RenderSceneFrame пишет 00 либо 01'),
        ('ModelByteOffset',1,'байтовое смещение слова указателя модели в таблице OBJECT3D'))
TABLES=((17,0x6000,('ActionRenderHeader','Source/Action/Data/RenderHeader.asm',0x3B8D,0x3B8F,
                    'FRenderHeaderState',FIELDS,('Value',))),)
BINDINGS=(('ActionRenderQueueInsertState','HeaderWord0',0x9B8D,'ActionRenderHeader.Value.ModeBits'),
          ('ActionObjectVerticesState','ModelByteOffset',0x9B8E,'ActionRenderHeader.Value.ModelByteOffset'))
REQUIRED_REPORTS=('ActionRenderMatrixVerification','ActionRenderCoefficientsVerification')
DOCUMENT='ActionRenderHeaderPhysicalData'
TAG='ActionRenderHeaderPhysicalData'


def validate_sources(sources):
    assert sources[17][0x3B8D:0x3B8F]==bytes(2)
    return dict(header_bytes=2,one_axis_bit=0,one_axis_mask=1,
                other_mode_bit_game_meanings_proved=False,initial_values_are_fixed_runtime_values=False)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[заголовок текущей модели](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():
    lines=['                ; Заголовок текущей модели, слово снимка HeaderWord0',
           '                struct FRenderHeaderState']
    for field,width,meaning in FIELDS:lines.append((field.ljust(16)+'db #00').ljust(80)+'; '+meaning)
    lines+=['                ends','                assert FRenderHeaderState == 2',
            '                assert FRenderHeaderState.ModeBits == 0',
            '                assert FRenderHeaderState.ModelByteOffset == 1','']
    return '\n'.join(lines)+'\n'
