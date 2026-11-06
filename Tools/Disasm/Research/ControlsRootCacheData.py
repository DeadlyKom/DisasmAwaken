"""Три буквальные физические страницы табличного корня, включая 23 особые строки и три исключения."""
import math,re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('Value',1,'исходный байт плоскости, назначение и индекс заданы именем экземпляра'),)
TABLE=('ControlsRootCache','Source/Controls/Data/RootCache.asm',0,0x300,'FRootCacheByte',FIELDS,
    tuple(plane+format(index,'02X') for plane in ('Initial','BaseLow','BaseHigh') for index in range(256)))


def validate(source):
    raw=bytes(source[:768]);assert len(raw)==768
    for index in range(256):
        root={9:47,169:207,225:239}.get(index,math.isqrt(index*256))
        initial=root^255 if index<233 else root
        base=(-root*root)&65535 if index<233 else root*root
        assert raw[index]==initial and raw[256+index]+256*raw[512+index]==base,index
    return raw


def render(source):
    validate(source);text,labels=render_records(source,TABLE,0xC000)
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[табличный корень и особые строки](../../../Docs/ActionCachedRoot.md)')
    return text,labels


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ControlsRootCache' and clean.pop(0)=='assert $ == #C000'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FRootCacheByte {'
        assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #C300','endmodule']
    return parse_records(text,TABLE,0xC000)
