"""Раздельные физические части контекста отсечения, промежуточная маска не поглощается структурой."""
from PreviewSceneTables import render as render_records,parse as parse_records
HEAD_FIELDS=(('CurrentSecond',2,'полная горизонтальная компонента первой точки текущего сегмента'),
 ('CurrentFirst',2,'полная вертикальная компонента первой точки текущего сегмента'),
 ('NextSecond',2,'полная горизонтальная компонента следующей точки ломаной'))
TAIL_FIELDS=(('NextFirst',2,'полная вертикальная компонента следующей точки ломаной'),
 ('CurrentCode',1,'полный ClipCode первой точки, ноль означает локальный отказ подготовки'),
 ('NextCode',1,'полный ClipCode следующей точки, ноль означает локальный отказ подготовки'))
GATE_FIELDS=(('Code',1,'полный код ориентации, ноль допускает связанную ломаную, любой ненулевой байт запрещает'),)
TABLES=(
 (17,0x6000,('ActionClipLineHead','Source/Action/Data/ClipLineHead.asm',0x2D3A,0x2D40,'FClipLineHead',HEAD_FIELDS,('Value',))),
 (17,0x6000,('ActionClipLineTail','Source/Action/Data/ClipLineTail.asm',0x2D4A,0x2D4E,'FClipLineTail',TAIL_FIELDS,('Value',))),
 (17,0x6000,('ActionFaceGate','Source/Action/Data/FaceGate.asm',0x2D5A,0x2D5B,'FFaceGateCode',GATE_FIELDS,('Value',))))
BINDINGS=tuple(('ActionClippedPacketRendererState',field,address,module+'.Value.'+field) for field,address,module in (
 ('CurrentSecond',0x8D3A,'ActionClipLineHead'),('CurrentFirst',0x8D3C,'ActionClipLineHead'),('NextSecond',0x8D3E,'ActionClipLineHead'),
 ('NextFirst',0x8D4A,'ActionClipLineTail'),('CurrentCode',0x8D4C,'ActionClipLineTail'),('NextCode',0x8D4D,'ActionClipLineTail')))+(
 ('ActionPacketRendererState','FaceGate',0x8D5A,'ActionFaceGate.Value.Code'),)
REQUIRED_REPORTS=('ActionClippedPacketRendererVerification','ActionPacketRendererVerification')
DOCUMENT='ActionClippedLineWorkData'
TAG='ActionClippedLineWorkData'


def validate_sources(sources):
    assert sources[17][0x2D3A:0x2D40]==bytes(6) and sources[17][0x2D4A:0x2D4E]==bytes(4) and sources[17][0x2D5A]==0
    return dict(physical_state_bytes=11,physical_state_fragments=3,interleaved_polygon_mask_bytes_not_reclassified=True,
        face_gate_is_full_code_not_bit_mask=True,unknown_bytes_after_gate_preserved=5)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[рабочие слова текущего отсечения](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():
    lines=[]
    for name,fields in (('FClipLineHead',HEAD_FIELDS),('FClipLineTail',TAIL_FIELDS),('FFaceGateCode',GATE_FIELDS)):
        lines+=['                ; Физическая часть существующего рабочего состояния, адреса и промежуточные маски сохранены','                struct '+name]
        offset=0;assertions=[]
        for field,width,note in fields:
            lines.append((field.ljust(16)+('db #00' if width==1 else 'dw #0000')).ljust(80)+'; '+note)
            assertions.append('                assert '+name+'.'+field+' == '+str(offset));offset+=width
        lines+=['                ends','                assert '+name+' == '+str(offset),*assertions,'']
    return '\n'.join(lines)+'\n'
