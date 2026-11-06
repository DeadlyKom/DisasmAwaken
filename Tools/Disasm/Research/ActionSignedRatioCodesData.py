"""Исходные 256 табличных кодов, не синтезируемые из стандартной тригонометрической функции."""
import hashlib,re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('Code',1,'исходный код для индекса модуля отношения, смещение знаковой ветви добавляет потребитель'),)
TABLE=('ActionSignedRatioCodes','Source/Action/Data/SignedRatioCodes.asm',0x3A00,0x3B00,
       'FSignedRatioCode',FIELDS,tuple('Index'+format(i,'02X') for i in range(256)))
DIGEST='ba28ccb977abc96ca36b12e95e251b1804dc305fab713ae076d4f16602625497'


def validate(source):
    raw=bytes(source[0x3A00:0x3B00]);assert len(raw)==256 and hashlib.sha256(raw).hexdigest()==DIGEST
    return raw


def render(source):
    validate(source);text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[табличный код знакового отношения](../../../Docs/ActionSignedRatioCode.md)'),labels


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()];clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionSignedRatioCodes' and clean.pop(0)=='assert $ == #9A00'
    for name in TABLE[6]:
        assert clean.pop(0)==(name+':').ljust(16)+'FSignedRatioCode {'
        assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0));assert clean.pop(0)=='}'
    assert clean==['assert $ == #9B00','endmodule']
    return parse_records(text,TABLE,0x6000)
