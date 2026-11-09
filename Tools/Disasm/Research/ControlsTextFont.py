"""Шестистрочные пары четырёхпиксельных знаков CONTROL0, 104 пары до кода C870."""
START,END=0x600,0x870
PATH='Source/Controls/Resources/TextFont4x6.bin'
PREFIX_PATH='Source/Resources/22_CONTROL0/Unclassified0546_0600.bin'
FIRST_CODE,LAST_CODE=0x20,0xEF
FORMAT='PACKED_4X6_GLYPH_PAIRS'


def unpack(raw):
    assert len(raw)==624
    result=[]
    for pair in range(104):
        rows=raw[pair*6:pair*6+6]
        for shift in (4,0):result.append(tuple(tuple((row>>(shift+3-x))&1 for x in range(4)) for row in rows))
    assert len(result)==208
    return result


def pack(glyphs):
    assert len(glyphs)==208
    return bytes(sum(glyphs[2*pair][y][x]<<(7-x) for x in range(4))+sum(glyphs[2*pair+1][y][x]<<(3-x) for x in range(4)) for pair in range(104) for y in range(6))
