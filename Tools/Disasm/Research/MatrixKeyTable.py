"""Исходный якорь и 62 физических пары кодов, включая нулевые пропуски."""
PATH='Source/Station/Data/KeyboardCodes.asm'


def render(source):
    lines=['                module KeyboardCodes','; Документация [одиночная клавиша](../../../Docs/MatrixKey.md)',
           '; Anchor не проверяется, Code1D..Code5A задают код своей позицией, нулевые пары сохраняются',
           '                assert $ == #96AA']
    symbols={}
    for address in range(0x96AA,0x9728,2):
        label='Anchor' if address==0x96AA else f'Code{0x1D+(address-0x96AC)//2:02X}'
        row,mask=source[address-0x6000:address-0x6000+2]
        comment='якорь перед первым проверяемым элементом' if address==0x96AA else 'RowMask, KeyMask, нулевая пара не ограничивает поиск' if row==mask==0 else 'RowMask, KeyMask для кода позиции'
        lines.append((label+':').ljust(16)+f'FKeyBinding {{ #{row:02X}, #{mask:02X} }}'.ljust(64)+'; '+comment)
        symbols['KeyboardCodes.'+label]=address
    lines+=['                assert $ == #9728','                endmodule']
    return '\n'.join(lines)+'\n',symbols
