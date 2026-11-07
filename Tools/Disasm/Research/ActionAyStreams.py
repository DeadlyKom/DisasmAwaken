"""Восемь потоков с доказанными указателями и достижимыми нулевыми маркерами, остальные байты не классифицируются."""
import re
FIELDS=(('ToneLow','младший байт периода'),('ToneHigh','старший байт периода, полный исходный байт'),
        ('MixerBits','байт для OR со смесителем, B предварительно выполняет RLCA'),('Volume','байт записи уровня, полный исходный байт'))
STREAMS=(('EventBit1',0xED8F,6),('Missile',0xEDA8,6),('WaitLoop',0xEE4D,53),('EventBit0',0xEF22,6),('Record',0xEF3B,5),
         ('Capture',0xEE02,6),('FullSlots',0xEE1B,6),('PairedAim',0xEE34,6))
GROUPS=(('Source/Action/Data/AyStreamsFirst.asm',STREAMS[:2]),('Source/Action/Data/AyStreamsLater.asm',STREAMS[2:5]),
        ('Source/Action/Data/AyCaptureStreams.asm',STREAMS[5:7]),
        ('Source/Action/Data/AyPairedAimStream.asm',STREAMS[7:]))


def bounds(streams):return streams[0][1]-0x6000,streams[-1][1]+4*streams[-1][2]+1-0x6000


def structure_text():
    lines=['','                ; Физическая четырёхбайтовая строка потоков эффектов ACTION','                struct FActionAyFrame']
    for name,note in FIELDS:lines.append((name.ljust(16)+'db 0').ljust(80)+'; '+note)
    return '\n'.join(lines+['                ends','',''])


def render(source,streams):
    start,end=bounds(streams);lines=['                module ActionAyStreams',
        '                ; Документация [строки звуковых потоков](../../../Docs/ActionAyStreams.md)',
        '                assert $ == #'+format(start+0x6000,'04X')];labels={}
    for name,address,count in streams:
        assert not any(source[address-0x6000+4*i]==0 for i in range(count))
        assert source[address-0x6000+4*count]==0
        for i in range(count):
            label=name+'Row'+format(i,'02X');assert len(label)<=15;row_address=address+4*i
            labels['ActionAyStreams.'+label]=row_address
            lines.append((label+':').ljust(16)+'FActionAyFrame {')
            for offset,(field,note) in enumerate(FIELDS):
                labels['ActionAyStreams.'+label+'.'+field]=row_address+offset
                value=source[row_address-0x6000+offset];token='#'+format(value,'02X')+(',' if offset<3 else '')
                lines.append((' '*20+token).ljust(80)+'; '+field+', '+note)
            lines.append('                }')
        label=name+'End';labels['ActionAyStreams.'+label]=address+4*count
        lines.append(((label+':').ljust(16)+'db #00').ljust(80)+'; нулевой ToneLow следующей строки, отключить поток')
    lines+=['                assert $ == #'+format(end+0x6000,'04X'),'                endmodule']
    return '\n'.join(lines)+'\n',labels


def parse(text,streams):
    start,end=bounds(streams);clean=[line.partition(';')[0].strip() for line in text.splitlines()];clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionAyStreams';assert clean.pop(0)=='assert $ == #'+format(start+0x6000,'04X')
    raw=bytearray();labels={};cursor=start+0x6000
    for name,address,count in streams:
        assert cursor==address
        for i in range(count):
            label=name+'Row'+format(i,'02X');assert clean.pop(0)==(label+':').ljust(16)+'FActionAyFrame {'
            labels['ActionAyStreams.'+label]=cursor
            for offset,(field,_) in enumerate(FIELDS):
                token=clean.pop(0);assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if offset<3 else ''),token)
                labels['ActionAyStreams.'+label+'.'+field]=cursor;raw.append(int(token[1:3],16));cursor+=1
            assert clean.pop(0)=='}'
        label=name+'End';assert clean.pop(0)==(label+':').ljust(16)+'db #00'
        labels['ActionAyStreams.'+label]=cursor;raw.append(0);cursor+=1
    assert cursor==end+0x6000 and clean==['assert $ == #'+format(cursor,'04X'),'endmodule']
    return bytes(raw),labels
