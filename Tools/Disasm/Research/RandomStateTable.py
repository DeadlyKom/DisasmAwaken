"""Физические семь состояний общего генератора, исходный порядок и байты сохраняются."""
PATH='Source/Station/Data/RandomStates.asm'


def render(source):
    lines=['                module RandomStates',
           '; Документация [формула и независимые потоки](../../../Docs/RandomState.md)',
           '                assert $ == #A8AC']
    symbols={}
    for index in range(7):
        offset=0x48AC+3*index;word=int.from_bytes(source[offset:offset+2],'little');high=source[offset+2]
        label='Seed'+str(index);address=offset+0x6000
        lines.append((label+':').ljust(16)+f'FRandomState {{ #{word:04X}, #{high:02X} }}'.ljust(64)+'; LowWord, HighByte, исходное состояние независимого потока')
        symbols['RandomStates.'+label]=address
        symbols['RandomStates.'+label+'.LowWord']=address
        symbols['RandomStates.'+label+'.HighByte']=address+2
    lines+=['                assert $ == #A8C1','                endmodule']
    return '\n'.join(lines)+'\n',symbols
