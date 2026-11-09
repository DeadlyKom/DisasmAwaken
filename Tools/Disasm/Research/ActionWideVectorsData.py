"""Шесть физических начальных векторов до известного рабочего блока 9B6F."""
import re
MODULE='ActionWideVectors'
PATH='Source/Action/Data/WideVectors.asm'
START,END=0x3B27,0x3B6F
NAMES=tuple('Vector'+format(i,'02X') for i in range(6))
NOTES=('разряды 7..0','разряды 15..8','разряды 23..16, бит 7 задаёт знак слова в 7F0E','разряды 31..24, бит 7 задаёт знак signed32')


def render(source, *, module=MODULE, origin=0x9B27, start=START, document='ActionWideVectors'):
    lines=['                module '+module,'                ; Документация [широкие цели](../../../Docs/'+document+'.md)',
        f'                assert $ == #{origin:04X}'];symbols={}
    for index,name in enumerate(NAMES):
        key=module+'.'+name;address=origin+12*index;symbols[key]=address
        lines+=['                ; -----------------------------------------','                ; Исходный физический вектор '+str(index),
            (name+':').ljust(16)+'FActionWideVector {']
        for component in range(3):
            prefix=key+'.Component'+str(component);symbols[prefix]=address+4*component
            lines.append('                    {'.ljust(80)+'; Component'+str(component)+', исходная компонента signed32')
            for byte in range(4):
                value=source[start+12*index+4*component+byte];symbols[prefix+'.Byte'+str(byte)]=address+4*component+byte
                lines.append(('                        #'+format(value,'02X')+(',' if byte<3 else '')).ljust(80)+'; Byte'+str(byte)+', '+NOTES[byte])
            lines.append('                    }'+(',' if component<2 else ''))
        lines.append('                }')
    lines+=[f'                assert $ == #{origin+72:04X}','                endmodule'];text='\n'.join(lines)+'\n'
    raw,parsed=parse(text,module=module,origin=origin);assert raw==source[start:start+72] and parsed==symbols
    return text,symbols


def parse(text, *, module=MODULE, origin=0x9B27):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()];clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+module and clean.pop(0)==f'assert $ == #{origin:04X}'
    raw=bytearray();symbols={};cursor=0
    for index,name in enumerate(NAMES):
        assert clean[cursor]==(name+':').ljust(16)+'FActionWideVector {';cursor+=1
        key=module+'.'+name;address=origin+12*index;symbols[key]=address
        for component in range(3):
            prefix=key+'.Component'+str(component);symbols[prefix]=address+4*component
            assert clean[cursor]=='{';cursor+=1
            for byte in range(4):
                token=clean[cursor];cursor+=1
                assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if byte<3 else ''),token)
                raw.append(int(token[1:3],16));symbols[prefix+'.Byte'+str(byte)]=address+4*component+byte
            assert clean[cursor]=='}'+(',' if component<2 else '');cursor+=1
        assert clean[cursor]=='}';cursor+=1
    assert clean[cursor:]==[f'assert $ == #{origin+72:04X}','endmodule'] and len(raw)==72
    return bytes(raw),symbols
