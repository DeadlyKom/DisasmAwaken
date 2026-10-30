"""Два физических списка по десять пятибайтовых записей и одному маркеру конца."""
PATH='Source/Station/Data/StoredMapPoints.asm'


def render(source):
 lines=['; Документация [списки ключей карты](../../../Docs/StoredMapPoints.md)'];symbols={}
 for begin,module in ((0x990A,'StoredMapPointsA'),(0x993D,'StoredMapPointsB')):
  lines+=['                module '+module,'                assert $ == #'+format(begin,'04X')]
  for index in range(10):
   address=begin+5*index;raw=source[address-0x6000:address-0x6000+5]
   if raw!=bytes([255])*5:raise ValueError('Изменена исходная пустая запись сохранённой точки')
   name='Point'+format(index,'02d');values=(int.from_bytes(raw[:2],'little'),int.from_bytes(raw[2:4],'little'),raw[4])
   lines+=['                ; исходная пустая запись, FirstWord, SecondWord и Variant сохранены без нормализации',
    ((name+':').ljust(16)+'FStoredMapPoint { #'+format(values[0],'04X')+', #'+format(values[1],'04X')+', #'+format(values[2],'02X')+' }')]
   symbols[module+'.'+name]=address
   for field,offset in (('FirstWord',0),('SecondWord',2),('Variant',4)):symbols[module+'.'+name+'.'+field]=address+offset
  if source[begin+50-0x6000]!=128:raise ValueError('Изменён однобайтовый конец списка точек')
  lines+=['                ; ограничитель не является пятибайтовой записью','EndByte:'.ljust(16)+'db #80',
   '                assert $ == #'+format(begin+51,'04X'),'                endmodule','']
  symbols[module+'.EndByte']=begin+50
 return '\n'.join(lines)+'\n',symbols
