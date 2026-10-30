"""Семь исходных LF-потоков рисователя условий миссии, CP866 без перекодирования байтов."""
PATH='Source/Station/Data/MissionTexts.asm'
TEXTS=((0xAB66,0xAB82,'Reminder'),(0xAB82,0xAB9E,'Invitation'),(0xAB9E,0xABB1,'Success'),
 (0xABB1,0xABC2,'TargetCaption'),(0xABC2,0xABF8,'TonnageCaption'),(0xABF8,0xAC0E,'RewardCaption'),
 (0xAC0E,0xAC14,'CurrencySuffix'))


def render(source):
 lines=['                module MissionTexts','; Документация [условия и награда миссии](../../../Docs/MissionCompletion.md)',
  '                assert $ == #AB66'];symbols={}
 for begin,end,name in TEXTS:
  raw=source[begin-0x6000:end-0x6000]
  if raw[-1]!=10 or 10 in raw[:-1]:raise ValueError('Изменились границы исходного LF-потока миссии')
  lines+=['                ; исходный поток CP866, управляющие байты и написание сохранены',
   (name+':').ljust(16)+'db '+', '.join('#'+format(value,'02X') for value in raw)]
  symbols['MissionTexts.'+name]=begin
 lines+=['                assert $ == #AC14','                endmodule']
 return '\n'.join(lines)+'\n',symbols
