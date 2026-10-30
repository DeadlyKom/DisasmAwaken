"""Физические нулевые записи двух точек и четырёх произведений в неиспользуемых ячейках таблицы."""
ENDPOINTS='Source/Map/Data/ClipEndpoints.asm'
PRODUCTS='Source/Map/Data/ClipProducts.asm'
OUTPUT_SIZE='Source/Map/Data/ClipOutputSize.asm'
CORNERS='Source/Map/Data/ClipCornerState.asm'


def render(source):
 outputs={};symbols={}
 for path,begin,end,structure,records in (
  (ENDPOINTS,0xDE2F,0xDE39,'FProjectedPoint',(('FirstPoint',0xDE2F),('SecondPoint',0xDE34))),
  (PRODUCTS,0xDE6B,0xDE7B,'FClipProduct',(('TopProduct',0xDE6B),('BottomProduct',0xDE6F),('LeftProduct',0xDE73),('RightProduct',0xDE77)))):
  if source[begin-0xC000:end-0xC000]!=bytes(end-begin):raise ValueError('Изменены исходные нулевые рабочие записи отсечения')
  lines=['                module MapClipWork','; Документация [рабочие точки и произведения](../../../Docs/ClipProducts.md)',
   '                assert $ == #'+format(begin,'04X')]
  for name,address in records:
   values='#0000, #0000, #00' if structure=='FProjectedPoint' else '#0000, #0000'
   lines+=['                ; исходные нулевые поля, заполнение вычисляется во время исполнения',
    (name+':').ljust(16)+structure+' { '+values+' }']
   symbols['MapClipWork.'+name]=address
   for field,offset in ((('X',0),('Y',2),('ClipCodes',4)) if structure=='FProjectedPoint' else (('LowWord',0),('HighWord',2))):symbols['MapClipWork.'+name+'.'+field]=address+offset
  lines+=['                assert $ == #'+format(end,'04X'),'                endmodule'];outputs[path]='\n'.join(lines)+'\n'
 if source[0x1E3B]!=0:raise ValueError('Изменён исходный байтовый размер выходного списка')
 outputs[OUTPUT_SIZE]='\n'.join(['                module MapClipWork',
  '; Документация [выходные пересечения](../../../Docs/ClipIntersections.md)',
  '                assert $ == #DE3B',
  'OutputSize:'.ljust(16)+'db #00',
  '                assert $ == #DE3C','                endmodule'])+'\n'
 symbols['MapClipWork.OutputSize']=0xDE3B
 if source[0x1E39:0x1E3B]!=bytes(2):raise ValueError('Изменено исходное состояние углов отсечения')
 outputs[CORNERS]='\n'.join(['                module MapClipWork',
  '; Документация [состояние углов](../../../Docs/ClipCases.md)',
  '                assert $ == #DE39',
  '                ; исходные SeenFlags=0, BlockCode=0, это дисковый снимок до вызовов',
  'Corners:'.ljust(16)+'FClipCornerState { #00, #00 }',
  '                assert $ == #DE3B','                endmodule'])+'\n'
 symbols.update({'MapClipWork.Corners':0xDE39,'MapClipWork.Corners.SeenFlags':0xDE39,'MapClipWork.Corners.BlockCode':0xDE3A})
 return outputs,symbols
