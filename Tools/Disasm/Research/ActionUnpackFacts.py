"""Полётная копия подтверждённого HR-декодера, все смещения взяты из сверенных инструкций."""
import re
import UnpackResourceFacts as primary

DELTA=0xC24
FUNCTIONS={0xAB23:('UnpackResource','Распаковка HR-потока в полётном коде с переносом входа, LZ-ссылками, тройками и восстановлением шестибайтового конца')}
LOCAL={address+DELTA:name for address,name in primary.NAMES.items()}
OLD_LOCAL=(0xAB3C,0xAB48,0xAB59,0xAB5F,0xAB61,0xAB62,0xAB68,0xAB6C,0xAB6E,
    0xAB74,0xAB80,0xAB8A,0xAB8B,0xAB90,0xAB96,0xABA0,0xABA5,0xABA7,0xABAD,
    0xABB0,0xABBE,0xABC2,0xABC4,0xABC9,0xABD4,0xABE7,0xABE9,0xABEF,0xABF8,
    0xAC01,0xAC0A,0xAC16,0xAC19,0xAC1F,0xAC2D)
LABELS={('Action',address):name for address,name in LOCAL.items()}
RENAMES={'Action.UnpackResource.Point'+format(address,'04X'):'Action.UnpackResource.'+LOCAL[address] for address in OLD_LOCAL}
ADDITIONAL_SYMBOLS={'Action.UnpackResource.'+name:address for address,name in LOCAL.items() if address not in OLD_LOCAL}
LOCATION={0xAB23:'общий фиксированный банк 2'}
CONTINUATIONS={}


def translate(text):
    return text.replace('9EFF..A01F','AB23..AC43').replace('RefillPackedBits','ReadWordFromIX')


CONTRACTS={('Action',0xAB23):tuple([translate(text) for text in section]
    for section in primary.CONTRACTS['Station',0x9EFF])}
CONTRACTS['Action',0xAB23][3].extend([
    '184 инструкции распаковщика и чтения слова сверены со станционной копией, сдвигаются только внутренние адреса кода на C24',
    'проверена вся логическая RAM кроме остаточных временных слов стека, каждая запись ограничена объявленными диапазонами',
    'кратность записей не доказана независимым эталоном, физические банки отдельно не моделировались'])
COMMENTS={address+DELTA:([translate(text) for text in before],None if right is None else translate(right))
    for address,(before,right) in primary.COMMENTS.items()}
TARGETS={**{a:'Action.UnpackResource.'+n for a,n in LOCAL.items()},
    0xAC38:'Action.ReadWordFromIX.Entry',0x2758:'PackedResourceConst.ResultWord'}


def name_operands(region,address,operation):
    if region=='Action' and address==0xAB23:
        operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)]
            if int(m[1],16) in TARGETS else m[0],operation)
        operation=primary.OPS.get(operation,operation)
    return operation
