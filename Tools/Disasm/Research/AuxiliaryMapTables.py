"""Десять физических ключей и одиннадцать общих кодов, следующий отрицательный байт принадлежит настройке интерфейса."""
KEYS='Source/Station/Data/MapAuxiliaryPoints.asm'
CODES='Source/Station/Data/MapAuxiliaryCodes.asm'
RANGES=((0x397B,0x39A3,KEYS),(0x39A3,0x39AE,CODES))
CODE_FIELDS=('ActiveCode','CompletionCode',*('Unknown'+format(i,'02d') for i in range(2,11)))


def render(source):
 texts={};symbols={};lines=['                module MapAuxiliaryPoints',
  '; Документация [общие ключи и коды маркеров](../../../Docs/AuxiliaryMapPoints.md)',
  '                assert $ == #997B']
 for index in range(10):
  offset=0x397B+4*index;first=int.from_bytes(source[offset:offset+2],'little');second=int.from_bytes(source[offset+2:offset+4],'little')
  name='Key'+format(index,'02d');lines+=['                ; FirstWord и SecondWord сохраняют исходный четырёхбайтовый координатный ключ',
   (name+':').ljust(16)+'FMapCoordinateKey { #'+format(first,'04X')+', #'+format(second,'04X')+' }']
  prefix='MapAuxiliaryPoints.'+name;symbols[prefix]=offset+0x6000;symbols[prefix+'.FirstWord']=offset+0x6000;symbols[prefix+'.SecondWord']=offset+0x6002
 lines+=['                assert $ == #99A3','                endmodule'];texts[KEYS]='\n'.join(lines)+'\n'
 data=source[0x39A3:0x39AE];assert len(data)==11 and source[0x39AE]&128
 lines=['                module MapAuxiliaryCodes',
  '                ; Документация [общие коды и смежная граница](../../../Docs/AuxiliaryMapPoints.md)',
  '                assert $ == #99A3',
  '                ; ActiveCode и CompletionCode совпадают с ячейками состояния миссии',
  '                ; Unknown02..Unknown10 сохранены, карта читает их как числовые управляющие коды',
  'State:'.ljust(16)+'FMapMarkerCodes {']
 for index,(field,value) in enumerate(zip(CODE_FIELDS,data)):
  meaning=('состояние миссии и первый код карты' if index==0 else
           'код повторной награды и второй код карты' if index==1 else
           'код за десятью физическими ключами, глобальное назначение не установлено' if index==10 else
           'код для Key'+format(index,'02d')+', глобальное назначение не установлено')
  initializer='                    #'+format(value,'02X')+(',' if index<10 else '')
  lines.append(initializer.ljust(80)+'; '+field+', '+meaning)
 lines += ['                }',
  '                ; следующий байт принадлежит InterfaceChoices и служит отрицательной границей исходного снимка',
  '                assert $ == #99AE','                endmodule'];texts[CODES]='\n'.join(lines)+'\n';symbols['MapAuxiliaryCodes.State']=0x99A3
 for index,field in enumerate(CODE_FIELDS):symbols['MapAuxiliaryCodes.State.'+field]=0x99A3+index
 return texts,symbols
