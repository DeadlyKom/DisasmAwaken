"""Две существующие пятибайтовые точки текущего отрезка в невозможных ячейках таблицы."""
CURRENT='Source/Map/Data/CurrentMapChainPoint.asm'
PREVIOUS='Source/Map/Data/PreviousMapChainPoint.asm'
RANGES=((0xDE0B,0xDE10,CURRENT),(0xDE1B,0xDE20,PREVIOUS))


def render(source):
 outputs={};symbols={}
 for (begin,end,path),name in zip(RANGES,('CurrentPoint','PreviousPoint')):
  data=source[begin-0xC000:end-0xC000];values=(int.from_bytes(data[:2],'little'),int.from_bytes(data[2:4],'little'),data[4])
  outputs[path]='\n'.join(['                module MapChainWork',
   '; Документация [открытая цепочка карты](../../../Docs/MapPointChain.md)',
   '                assert $ == #'+format(begin,'04X'),
   '                ; исходные X,Y и ClipCodes, все пять байтов обновляются перед обработкой ребра',
   (name+':').ljust(16)+'FProjectedPoint { #'+format(values[0],'04X')+', #'+format(values[1],'04X')+', #'+format(values[2],'02X')+' }',
   '                assert $ == #'+format(end,'04X'),'                endmodule'])+'\n'
  symbols['MapChainWork.'+name]=begin
  for field,offset in (('X',0),('Y',2),('ClipCodes',4)):symbols['MapChainWork.'+name+'.'+field]=begin+offset
 return outputs,symbols
