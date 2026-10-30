"""Физический пятибайтовый вход банковой характеристики, без назначения неизвестных игровых единиц."""
PATH='Source/Station/Data/CurrentSignature.asm'


def render(source):
    values=(int.from_bytes(source[0x383F:0x3841],'little'),int.from_bytes(source[0x3841:0x3843],'little'),source[0x3843])
    lines=['                module SignatureInput','; Документация [формула ключа](../../../Docs/WorldSignature.md)',
           '                assert $ == #983F',
           ('Entry:'.ljust(16)+f'FSignatureInput {{ #{values[0]:04X}, #{values[1]:04X}, #{values[2]:02X} }}').ljust(80)+'; FirstWord, SecondWord, Variant, исходные байты текущего ключа',
           '                assert $ == #9844','                endmodule']
    symbols={'SignatureInput.Entry':0x983F}
    for field,offset in (('FirstWord',0),('SecondWord',2),('Variant',4)):symbols['SignatureInput.Entry.'+field]=0x983F+offset
    return '\n'.join(lines)+'\n',symbols
