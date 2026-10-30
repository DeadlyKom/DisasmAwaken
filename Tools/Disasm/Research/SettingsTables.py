"""Физические слова интерфейсных и полётных настроек и исходные изменяемые подписи."""
CHOICES='Source/Station/Data/InterfaceChoices.asm'
COLORS='Source/Station/Data/InterfaceColors.asm'
CONTROLS='Source/Station/Data/ControlOptions.asm'
TEXT='Source/Station/Data/SettingsText.asm'


def words(source,module,labels,origin):
    lines=['                module '+module,'; Документация [настройки](../../../Docs/SettingsLabels.md)',
           f'                assert $ == #{origin:04X}']
    symbols={}
    for i,label in enumerate(labels):
        offset=origin-0x6000+2*i;value,mask=source[offset:offset+2]
        lines.append((label+':').ljust(16)+f'FSettingWord {{ #{value:02X}, #{mask:02X} }}'.ljust(64)+'; ValueOrRow, KeyMask, порядок исходного массива')
        symbols[module+'.'+label]=origin+2*i
    lines+=[f'                assert $ == #{origin+2*len(labels):04X}','                endmodule']
    return '\n'.join(lines)+'\n',symbols


def render(source):
    outputs={};symbols={}
    for path,module,labels,origin in (
            (CHOICES,'InterfaceChoices',('MouseOption','JoyOption','MusicMode','FillMode'),0x99AE),
            (COLORS,'InterfaceColors',('InkBits','PaperRotate','HighRotate'),0x99C2),
            (CONTROLS,'ControlOptions',tuple(f'Unknown{i:02d}' for i in range(43)),0x99C8)):
        text,local=words(source,module,labels,origin);outputs[path]=text;symbols.update(local)
    lines=['                module SettingsText','; Документация [изменяемые подписи](../../../Docs/SettingsLabels.md)',
           '; исходные тексты до FormatSettingsLabel, загрузчик заменяет их по длине до нуля',
           '                assert $ == #9728','Interface:      db "YNYNQAOP M040", #00',
           '                assert $ == #9736','Controls:       db "YSXKLNMA ", #1F, "PHC123JFZRBQWEGDTVSXKLA ", #1F',
           '                db "PHC1JQDB", #00','                assert $ == #9762','                endmodule']
    outputs[TEXT]='\n'.join(lines)+'\n';symbols.update({'SettingsText.Interface':0x9728,'SettingsText.Controls':0x9736})
    return outputs,symbols
