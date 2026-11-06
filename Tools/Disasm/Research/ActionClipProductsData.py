"""Четыре физические записи произведений, исходные нули не объявляются мусором."""
import re
PATH='Source/Action/Data/ClipProducts.asm'
RECORDS=(('RightProduct',0xCF2B),('LeftProduct',0xCF2F),('BottomProduct',0xCF33),('TopProduct',0xCF37))


def bindings():
    labels={}
    for name,address in RECORDS:
        labels['ActionClipProductsData.'+name]=address
        for field,offset in (('LowWord',0),('HighWord',2)):labels['ActionClipProductsData.'+name+'.'+field]=address+offset
    return labels


def render(source):
    lines=['                module ActionClipProductsData',
        '                ; Документация [произведения пересечений](../../../Docs/ActionClipProducts.md)',
        '                assert $ == #CF2B']
    for name,address in RECORDS:
        raw=source[address-0x6000:address-0x6000+4];assert len(raw)==4
        low,high=int.from_bytes(raw[:2],'little'),int.from_bytes(raw[2:],'little')
        lines.extend([(name+':').ljust(16)+'FClipProduct {',
            ('                    #'+format(low,'04X')+',').ljust(80)+'; LowWord, исходное младшее слово числителя',
            ('                    #'+format(high,'04X')).ljust(80)+'; HighWord, исходное старшее слово числителя',
            '                }'])
    lines+=['                assert $ == #CF3B','                endmodule']
    return '\n'.join(lines)+'\n',bindings()


def parse(text):
    lines=[line.partition(';')[0].rstrip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert len(lines)==20 and lines[:2]==['                module ActionClipProductsData','                assert $ == #CF2B']
    raw=bytearray()
    for index,(name,address) in enumerate(RECORDS):
        block=lines[2+4*index:6+4*index]
        assert block[0]==(name+':').ljust(16)+'FClipProduct {' and block[3]=='                }'
        assert re.fullmatch(r'\s+#[0-9A-F]{4},',block[1]) and re.fullmatch(r'\s+#[0-9A-F]{4}',block[2])
        for line in block[1:3]:raw.extend(int(line.strip().removesuffix(',')[1:],16).to_bytes(2,'little'))
    assert lines[-2:]==['                assert $ == #CF3B','                endmodule']
    return bytes(raw),bindings()
