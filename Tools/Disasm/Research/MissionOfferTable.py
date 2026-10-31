"""Шестнадцать исходных байтов состояния, четыре промежуточных слова Unknown, MessageIndex задаёт сообщение расшифровки."""
PATH='Source/Station/Data/MissionOffer.asm'
FIELDS=('FirstWord','SecondWord','UnknownWord04','UnknownWord06','UnknownWord08','UnknownWord0A','Reward','RequiredTonnage','MessageIndex')


def render(source):
 raw=source[0x38B0:0x38C0];values=[int.from_bytes(raw[i:i+2],'little') for i in range(0,14,2)]+list(raw[14:])
 lines=['                module MissionOffer','; Документация [генератор предложения](../../../Docs/MissionOffer.md)',
  '                assert $ == #98B0','Entry:'.ljust(16)+'FMissionOfferState {']
 symbols={'MissionOffer.Entry':0x98B0}
 for i,(field,value) in enumerate(zip(FIELDS,values)):
  line='                    #'+format(value,'04X' if i<7 else '02X')+(',' if i<8 else '')
  lines.append(line.ljust(80)+'; '+field+', исходное значение поля')
  symbols['MissionOffer.Entry.'+field]=0x98B0+(2*i if i<7 else 14+i-7)
 lines+=['                }','                assert $ == #98C0','                endmodule']
 return '\n'.join(lines)+'\n',symbols
