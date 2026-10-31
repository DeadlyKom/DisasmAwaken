"""Чтение физических заголовков и четырёхбайтовых групп моделей исходного банка 4."""
def records(source,model_offset):
 if model_offset not in range(0,44,2):raise ValueError('Смещение вне 22 исходных указателей моделей')
 pointer=int.from_bytes(source[0x1000+model_offset:0x1002+model_offset],'little');start=pointer-0xC000
 if not 0<=start<len(source)-2:raise ValueError('Указатель модели вне исходных байтов банка 4')
 size,flags=source[start:start+2];position=start+2;groups=[]
 # Поиск однобайтового нуля маски, координаты читаются только для ненулевой маски.
 while position<len(source) and source[position]:
  if position+4>len(source):raise ValueError('Обрезана физическая группа модели')
  groups.append((0xC000+position,tuple(source[position:position+4])));position+=4
 if position>=len(source):raise ValueError('Не найден исходный конец групп модели')
 return dict(pointer=pointer,size=size,scale_flags=flags,exponent=flags&127,groups=groups,terminator=0xC000+position,vertices=sum(data[0].bit_count() for address,data in groups))
