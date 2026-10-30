"""Физические входные точки, пара изменяемых кодов и две восьмифазные маски рисователя."""
POINTS='Source/Map/Data/MapLinePoints.asm'
MODE='Source/Map/Data/MapLineMode.asm'
MASKS='Source/Map/Data/MapLineMasks.asm'
RANGES=((0xDE2B,0xDE2F,POINTS),(0xDE3C,0xDE3E,MODE),(0xD420,0xD430,MASKS))


def render(source):
 outputs={};symbols={}
 for begin,end,path,structure,records in (
  (0xDE2B,0xDE2F,POINTS,'FClipOutputPoint',(('Start',0xDE2B,('X','Y')),('Finish',0xDE2D,('X','Y')))),
  (0xDE3C,0xDE3E,MODE,'FMapLineMode',(('Mode',0xDE3C,('PixelOpcode','ByteCrossOpcode')),)),
  (0xD420,0xD430,MASKS,'FMapLineMaskSet',(('SetBit',0xD420,tuple('Phase'+str(i) for i in range(8))),('ClearBit',0xD428,tuple('Phase'+str(i) for i in range(8)))))):
  module='MapLineMasks' if path==MASKS else 'MapLineWork';lines=['                module '+module,
   '; Документация [самомодифицируемый рисователь](../../../Docs/MapLine.md)',
   '                assert $ == #'+format(begin,'04X')]
  for name,address,fields in records:
   data=source[address-0xC000:address-0xC000+len(fields)]
   lines+=['                ; исходные значения полей в порядке структуры, код инициализирует рабочие записи отдельно',
    (name+':').ljust(16)+structure+' { '+', '.join('#'+format(v,'02X') for v in data)+' }']
   symbols[module+'.'+name]=address
   for i,field in enumerate(fields):symbols[module+'.'+name+'.'+field]=address+i
  lines+=['                assert $ == #'+format(end,'04X'),'                endmodule'];outputs[path]='\n'.join(lines)+'\n'
 return outputs,symbols
