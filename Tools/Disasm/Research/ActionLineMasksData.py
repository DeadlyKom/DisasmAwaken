"""Физические маски восьми пиксельных фаз, прямые для OR/XOR и инверсные для AND."""
import re
PATH='Source/Action/Data/LineMasks.asm'
RECORDS=tuple((kind+str(phase),0xE010+offset+phase) for kind,offset in (('Set',0),('Clear',8)) for phase in range(8))


def structure_text():
    return '\n                struct FLinePixelMask\n'+('Mask            db #00').ljust(80)+'; физическая маска одной пиксельной фазы\n                ends\n                assert FLinePixelMask == #01\n                assert FLinePixelMask.Mask == #00\n'


def bindings():
    return {key:address for name,address in RECORDS for key in ('ActionLineMasks.'+name,'ActionLineMasks.'+name+'.Mask')}


def render(source):
    lines=['                module ActionLineMasks','                ; Документация [растеризатор и маски](../../../Docs/ActionLineRaster.md)','                assert $ == #E010']
    for name,address in RECORDS:
        value=source[address-0x6000]
        lines.extend([(name+':').ljust(16)+'FLinePixelMask {',('                    #'+format(value,'02X')).ljust(80)+'; Mask, '+('единица выбирает пиксель' if name.startswith('Set') else 'нуль выбирает очищаемый пиксель')+', фаза '+name[-1],'                }'])
    lines+=['                assert $ == #E020','                endmodule']
    return '\n'.join(lines)+'\n',bindings()


def parse(text):
    lines=[line.partition(';')[0].rstrip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert len(lines)==52 and lines[:2]==['                module ActionLineMasks','                assert $ == #E010']
    raw=bytearray()
    for index,(name,address) in enumerate(RECORDS):
        block=lines[2+3*index:5+3*index]
        assert block[0]==(name+':').ljust(16)+'FLinePixelMask {' and block[2]=='                }'
        assert re.fullmatch(r'\s+#[0-9A-F]{2}',block[1]);raw.append(int(block[1].strip()[1:],16))
    assert lines[-2:]==['                assert $ == #E020','                endmodule']
    return bytes(raw),bindings()
