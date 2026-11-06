"""Две реальные пятибайтовые точки внутри невыбираемых ячеек младшей таблицы адресов."""
import re
POINTS=(('FirstPoint',0x6F0B,'Source/Action/Data/ClipFirstPoint.asm'),('SecondPoint',0x6F1B,'Source/Action/Data/ClipSecondPoint.asm'))


def render(source,name,offset):
    data=source[offset:offset+5];assert len(data)==5;address=offset+0x6000
    lines=['                module ActionClipPoints','                ; Документация [точки и пересечения](../../../Docs/ActionClipProducts.md)',
        '                assert $ == #'+format(address,'04X'),(name+':').ljust(16)+'FRenderProjectedPoint {',
        ('                    #'+format(int.from_bytes(data[:2],'little'),'04X')+',').ljust(80)+'; Second, исходная горизонтальная координата',
        ('                    #'+format(int.from_bytes(data[2:4],'little'),'04X')+',').ljust(80)+'; First, исходная вертикальная координата',
        ('                    #'+format(data[4],'02X')).ljust(80)+'; ClipCode, исходный нуль означает ещё не подготовленный код',
        '                }','                assert $ == #'+format(address+5,'04X'),'                endmodule']
    labels={'ActionClipPoints.'+name:address}
    labels.update({'ActionClipPoints.'+name+'.'+field:address+delta for field,delta in (('Second',0),('First',2),('ClipCode',4))})
    return '\n'.join(lines)+'\n',labels


def parse(text,name,offset):
    clean=[line.partition(';')[0].rstrip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert len(clean)==9 and clean[:3]==['                module ActionClipPoints','                assert $ == #'+format(offset+0x6000,'04X'),(name+':').ljust(16)+'FRenderProjectedPoint {']
    assert clean[6:]==['                }','                assert $ == #'+format(offset+0x6005,'04X'),'                endmodule']
    assert all(re.fullmatch(r'\s+#[0-9A-F]{4},',clean[i]) for i in (3,4)) and re.fullmatch(r'\s+#[0-9A-F]{2}',clean[5])
    raw=b''.join(int(clean[i].strip().removesuffix(',')[1:],16).to_bytes(2,'little') for i in (3,4))+bytes((int(clean[5].strip()[1:],16),))
    dummy=bytearray(offset+5);dummy[offset:offset+5]=raw
    return raw,render(dummy,name,offset)[1]
