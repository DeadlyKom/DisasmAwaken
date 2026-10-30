"""Подтверждённые физические категории, правила и начальные пары рынка."""
CATEGORIES='Source/Station/Data/MarketCategories.asm'
RULES='Source/Station/Data/MarketRules.asm'
ROWS='Source/Station/Data/MarketRows.asm'
RANGES=((0x34DC,0x34F7,CATEGORIES),(0x3518,0x3554,RULES),(0x3555,0x3592,ROWS))


def render(source):
 texts={};symbols={}
 for start,end,path in RANGES:
  module={CATEGORIES:'MarketCategories',RULES:'MarketRules',ROWS:'MarketRows'}[path]
  lines=['                module '+module,'; Документация [генерация рынка](../../../Docs/MarketGeneration.md)',
         f'                assert $ == #{start+0x6000:04X}']
  if path==CATEGORIES:
   for index,value in enumerate(source[start:end]):
    label='Category'+str(index).zfill(2);symbols[module+'.'+label]=start+index+0x6000
    lines.append(((label+':').ljust(16)+f'db #{value:02X}').ljust(80)+'; категория строки '+str(index)+', сравнивается с MinorCode')
  else:
   structure='FMarketRule' if path==RULES else 'FMarketRow'
   fields=('BasePrice','StockRule') if path==RULES else ('StockAndMark','Price')
   for index in range(30):
    address=start+2*index+0x6000;label=('Rule' if path==RULES else 'Row')+str(index).zfill(2)
    symbols[module+'.'+label]=address
    for offset,field in enumerate(fields):symbols[module+'.'+label+'.'+field]=address+offset
    values=source[start+2*index:start+2*index+2]
    comment='BasePrice, StockRule' if path==RULES else 'StockAndMark, Price, исходная пустая строка'
    if path==RULES and index>=27:comment+=', для этой строки читается только BasePrice'
    lines.append(((label+':').ljust(16)+structure+f' {{ #{values[0]:02X}, #{values[1]:02X} }}').ljust(80)+'; '+comment)
   if path==ROWS:
    symbols[module+'.EndMarker']=0x9591
    lines.append(('EndMarker:'.ljust(16)+f'db #{source[0x3591]:02X}').ljust(80)+'; исходный маркер, генерация и очистка его сохраняют')
  lines += [f'                assert $ == #{end+0x6000:04X}','                endmodule']
  texts[path]='\n'.join(lines)+'\n'
 return texts,symbols
