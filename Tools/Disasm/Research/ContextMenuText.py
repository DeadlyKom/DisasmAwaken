"""Восемь команд контекстного меню, семь CR и завершающий LF сохраняются побайтово."""
PATH='Source/Station/Data/ContextMenuText.asm'


def render(source):
    begin=0x832E;end=source.index(10,begin)+1
    lines=['                module ContextMenuText','; Документация [контекстное меню](../../../Docs/PopupItems.md)',
           '; байты исходного текста, человекочитаемые комментарии декодированы как CP866',
           '                assert $ == #E32E']
    symbols={'ContextMenuText.Entry':0xE32E};position=begin
    labels=('Entry','CloseAll','RememberEnv','Arrange','EnvOptions','GameOptions','Restore','Save')
    for index,label in enumerate(labels):
        terminator=13 if index<7 else 10
        row_end=source.index(terminator,position)+1
        text=source[position:row_end-1].decode('cp866')
        symbols['ContextMenuText.'+label]=position+0x6000
        for offset in range(position,row_end,8):
            operation='db '+', '.join(f'#{v:02X}' for v in source[offset:min(offset+8,row_end)])
            prefix=(label+':').ljust(16) if offset==position else ' '*16
            lines.append((prefix+operation).ljust(80)+'; '+(text if offset==position else 'продолжение команды и '+('CR' if terminator==13 else 'LF')))
        position=row_end
    assert position==end
    lines+=[f'                assert $ == #{end+0x6000:04X}','                endmodule']
    return '\n'.join(lines)+'\n',symbols,end
