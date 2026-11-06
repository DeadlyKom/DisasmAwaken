"""Физический рабочий вектор 9B78..9B80, три знаковые компоненты в дополнительном коде."""
import re
MODULE='ActionWorkVector'
PATH='Source/Action/Data/WorkVector24.asm'
START,END=0x3B78,0x3B81
TRANSFORM_PATH = 'Source/Action/Data/TransformWorkVector24.asm'
TRANSFORM_MODULE = 'ActionTransformWorkVector'
STRUCT_BLOCK='''
                ; Знаковая 24-битная компонента в дополнительном коде, не формат модуля проекции
                struct FActionWorkComponent24
LowWord         dw #0000                                                        ; разряды 15..0, записываются до проверки переполнения старшего байта
High            db #00                                                          ; разряды 23..16, бит 7 задаёт знак всей 24-битной компоненты
                ends
                assert FActionWorkComponent24 == 3

                ; Физический рабочий вектор вычитателя 66D2
                struct FActionWorkVector24
Component0      FActionWorkComponent24                                          ; первая компонента в дополнительном коде
Component1      FActionWorkComponent24                                          ; вторая компонента в дополнительном коде
Component2      FActionWorkComponent24                                          ; третья компонента в дополнительном коде
                ends
                assert FActionWorkVector24 == 9

'''


def render(source, origin=0x9B78, module=MODULE, document='ActionSubtractWorkVector'):
    start = origin - 0x6000
    lines=['                module '+module,'                ; Документация [рабочий вектор](../../../Docs/'+document+'.md)',
        '                assert $ == #'+format(origin,'04X'),'Value:          FActionWorkVector24 {'];symbols={module+'.Value':origin}
    for index in range(3):
        offset=start+3*index;address=origin+3*index;name='Component'+str(index)
        word=source[offset]|source[offset+1]<<8;high=source[offset+2]
        lines+=['                    {'.ljust(80)+'; '+name+', исходная физическая компонента',
            ('                        #'+format(word,'04X')+',').ljust(80)+'; LowWord, исходные разряды 15..0',
            ('                        #'+format(high,'02X')).ljust(80)+'; High, исходные разряды 23..16 со знаком в бите 7',
            '                    }'+(',' if index<2 else '')]
        prefix=module+'.Value.'+name
        symbols[prefix]=address;symbols[prefix+'.LowWord']=address;symbols[prefix+'.High']=address+2
    lines+=['                }','                assert $ == #'+format(origin+9,'04X'),'                endmodule'];text='\n'.join(lines)+'\n'
    assert parse(text, origin, module)==(source[start:start+9],symbols)
    return text,symbols


def parse(text, origin=0x9B78, module=MODULE):
    lines=[line.split(';',1)[0].strip() for line in text.splitlines() if line.split(';',1)[0].strip()]
    assert lines[:3]==['module '+module,'assert $ == #'+format(origin,'04X'),'Value:          FActionWorkVector24 {']
    raw=bytearray();symbols={module+'.Value':origin};cursor=3
    for index in range(3):
        assert lines[cursor]=='{';low,high=lines[cursor+1:cursor+3]
        assert re.fullmatch(r'#[0-9A-F]{4},',low) and re.fullmatch(r'#[0-9A-F]{2}',high)
        word=int(low[1:5],16);raw.extend((word&255,word>>8,int(high[1:],16)))
        assert lines[cursor+3]=='}'+(',' if index<2 else '');cursor+=4
        prefix=module+'.Value.Component'+str(index);address=origin+3*index
        symbols[prefix]=address;symbols[prefix+'.LowWord']=address;symbols[prefix+'.High']=address+2
    assert lines[cursor:]==['}','assert $ == #'+format(origin+9,'04X'),'endmodule']
    return bytes(raw),symbols
