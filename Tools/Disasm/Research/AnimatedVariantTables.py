"""Шесть циклических траекторий и четыре восьмифазных трёхстрочных ресурса."""
PATHS=((7,0xCA45),(10,0xCA7E),(13,0xCACF),(16,0xCB38),(19,0xCBB9),(22,0xCC52))
SPRITES=(('Default',0xCD03),('Current',0xCD33),('Stored',0xCD63),('Selected',0xCD93))
RANGES=tuple((address-0xC000,address-0xC000+8*radius+1,'Source/Map/Data/VariantPath'+str(radius)+'.asm') for radius,address in PATHS)+tuple((a-0xC000,a-0xC000+48,'Source/Map/Resources/Variant'+n+'.asm') for n,a in SPRITES)


def render(source):
 texts={};symbols={}
 for radius,address in PATHS:
  path='Source/Map/Data/VariantPath'+str(radius)+'.asm';prefix='MapVariantPaths.Radius'+str(radius)
  lines=['                module MapVariantPaths','                module Radius'+str(radius),
   '; Документация [циклические смещения и фазовые ресурсы](../../../Docs/AnimatedVariants.md)',
   '                assert $ == #'+format(address,'04X'),
   '                ; OffsetX и OffsetY задают знаковые байтовые смещения в пикселях относительно общего начала']
  for index in range(4*radius):
   offset=address-0xC000+2*index;x,y=source[offset:offset+2];name='Point'+format(index,'02d')
   lines.append((name+':').ljust(16)+'FMapPathPoint { #'+format(x,'02X')+', #'+format(y,'02X')+' }')
   symbols[prefix+'.'+name]=offset+0xC000;symbols[prefix+'.'+name+'.OffsetX']=offset+0xC000;symbols[prefix+'.'+name+'.OffsetY']=offset+0xC001
  end=address+8*radius;assert source[end-0xC000]==0x80
  lines+=['                ; отдельный байт 80 завершает поток, отрицательные координаты остальных записей допустимы',
   'End:'.ljust(16)+'db #80','                assert $ == #'+format(end+1,'04X'),'                endmodule','                endmodule']
  symbols[prefix+'.End']=end;texts[path]='\n'.join(lines)+'\n'
 for name,address in SPRITES:
  path='Source/Map/Resources/Variant'+name+'.asm';prefix='MapVariantSprites.'+name
  lines=['                module MapVariantSprites','                module '+name,
   '; Документация [трёхстрочные фазы варианта](../../../Docs/AnimatedVariants.md)',
   '                assert $ == #'+format(address,'04X'),
   '                ; Row0..Row2 содержат по два смежных экранных байта, сдвиг фазы соответствует младшим трём битам X']
  for phase in range(8):
   offset=address-0xC000+6*phase;values=source[offset:offset+6];label='Phase'+str(phase)
   lines.append((label+':').ljust(16)+'FMapVariantPhase { '+', '.join('#'+format(v,'02X') for v in values)+' }');symbols[prefix+'.'+label]=offset+0xC000
   for index,field in enumerate('Row'+str(row)+side for row in range(3) for side in ('Left','Right')):symbols[prefix+'.'+label+'.'+field]=offset+0xC000+index
  lines+=['                assert $ == #'+format(address+48,'04X'),'                endmodule','                endmodule'];texts[path]='\n'.join(lines)+'\n'
 return texts,symbols
