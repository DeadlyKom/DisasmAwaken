"""Шесть ресурсов семистрочных маркеров с восемью исходными фазами по 16 байтов."""
RESOURCES=(('Selected',0xCDC3),('Secondary',0xCE43),('ActiveAux',0xCEC3),('Cursor',0xCF43),('Primary',0xCFC3),('Stored',0xD043))
RANGES=tuple((address,address+128,'Source/Map/Resources/Marker'+name+'.asm') for name,address in RESOURCES)


def render(source):
 texts={};symbols={}
 for (name,address),(_,end,path) in zip(RESOURCES,RANGES):
  data=source[address-0xC000:end-0xC000]
  if len(data)!=128:raise ValueError('Неполный исходный ресурс маркера')
  lines=['                module MapMarkerSprites','                module '+name,
   '; Документация [источники и фазы маркеров](../../../Docs/MapMarkerSprites.md)',
   '                assert $ == #'+format(address,'04X')]
  for phase in range(8):
   payload=data[phase*16:phase*16+16]
   lines+=['                ; фаза X AND 7 = '+str(phase)+', семь пар строк и два сохранённых конечных байта',
    ('Phase'+str(phase)+':').ljust(16)+'FMapMarkerPhase { '+', '.join('#'+format(v,'02X') for v in payload)+' }']
   prefix='MapMarkerSprites.'+name+'.Phase'+str(phase);symbols[prefix]=address+phase*16
   for row in range(7):
    for byte,side in enumerate(('Left','Right')):symbols[prefix+'.Row'+str(row)+side]=address+phase*16+2*row+byte
   symbols[prefix+'.UnknownTail0']=address+phase*16+14;symbols[prefix+'.UnknownTail1']=address+phase*16+15
  lines+=['                assert $ == #'+format(end,'04X'),'                endmodule','                endmodule'];texts[path]='\n'.join(lines)+'\n'
 return texts,symbols
