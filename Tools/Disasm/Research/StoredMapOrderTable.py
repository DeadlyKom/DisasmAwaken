"""Исходные 11 байтов служебного поля и десяти смещений второго списка."""
PATH='Source/Station/Data/StoredMapOrder.asm'


def render(source):
 raw=source[0x3970:0x397B]
 if raw!=bytes([0x22]+[0]*10):raise ValueError('Изменилось исходное состояние порядка второго списка')
 fields=['Layout']+['Order'+format(i,'02d') for i in range(10)]
 lines=['                module StoredMapOrder','; Документация [количество и порядок второго списка](../../../Docs/SecondaryPointOrder.md)',
  '; Потребитель [открытая цепочка и код режима](../../../Docs/MapPointChain.md)',
  '                assert $ == #9970','Entry:'.ljust(16)+'FStoredMapOrder {']
 for index,(field,value) in enumerate(zip(fields,raw)):
  code='                    #'+format(value,'02X')+(',' if index<10 else '')
  lines.append(code.ljust(80)+'; FStoredMapOrder.'+field+(', N=2, режим Xor, биты 7..6 нулевые' if index==0 else ''))
 lines+=['                }','                assert $ == #997B','                endmodule']
 symbols={'StoredMapOrder.Entry':0x9970,**{'StoredMapOrder.Entry.'+field:0x9970+index for index,field in enumerate(fields)}}
 return '\n'.join(lines)+'\n',symbols
