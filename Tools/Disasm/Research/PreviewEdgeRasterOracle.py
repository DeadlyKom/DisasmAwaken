"""Независимые точки отрезка DE1C, исключённый конец и три пиксельных операции."""


def address(row,column):
 return 0x4000+(row//64)*2048+(row&7)*256+((row//8)&7)*32+column//8


def points(first,second):
 if first==second:return []
 if second[0]<first[0]:first,second=second,first
 row,col=first;end_row,end_col=second;dy=end_row-row;dx=abs(end_col-col);direction=1 if end_col>col else -1;major=max(dx,dy);minor=min(dx,dy);half=major//2
 # Количество переносов по малой оси после t шагов выводится напрямую из целочисленного накопителя ошибки.
 def minor_steps(t):return (t*minor+major-1-half)//major
 return [(row+minor_steps(t),col+direction*t) if dx>=dy else (row+t,col+direction*minor_steps(t)) for t in range(major)]


def raster(buffer,first,second,mode,origin=(0,0)):
 result=bytearray(buffer)
 for row,column in points(first,second):
  row+=origin[0];column+=origin[1];offset=address(row,column)-0x4000;bit=128>>(column&7)
  if mode=='xor':result[offset]^=bit
  elif mode=='or':result[offset]|=bit
  elif mode=='and':result[offset]&=255^bit
  else:raise ValueError(mode)
 return result


def logical(value):
 return (value&0xA8)|(64 if value==0 else 0)|(4 if value.bit_count()%2==0 else 0)


def arithmetic(first,second,subtract=False):
 total=first-second if subtract else first+second;value=total&255
 signed=lambda v:v-256 if v&128 else v
 mathematical=signed(first)+(-signed(second) if subtract else signed(second))
 flags=(value&0xA8)|(64 if value==0 else 0)|(16 if (first^second^value)&16 else 0)|(4 if not -128<=mathematical<=127 else 0)|(2 if subtract else 0)|int(total<0 or total>255)
 return value,flags


def row_context(pointer):
 high=((pointer>>8)+1)&255;low=pointer&255
 if high&7:return high&7,logical(high&7)|16
 a,f=arithmetic(low,32)
 if f&1:return a,f
 return arithmetic(high,8,True)


def column_context(low,direction,carry):
 old=(low-direction)&255
 return (low&0xA8)|(64 if low==0 else 0)|(16 if (old&15)==(15 if direction>0 else 0) else 0)|(4 if old==(127 if direction>0 else 128) else 0)|(0 if direction>0 else 2)|carry


def registers(first,second,mode,bitmap,origin=(0,0)):
 if first==second:return dict(af=(0x5A,0x42),alt_af=(0x69,0xCF))
 start,end=(second,first) if second[0]<first[0] else (first,second)
 dy=end[0]-start[0];dx=abs(end[1]-start[1]);major=max(dx,dy);minor=min(dx,dy);half=major//2;direction=1 if end[1]>start[1] else -1;steep=dy>dx
 borrowed=half+minor>=major;before_error=(half+minor)%major;crossed=(end[1]//8)!=((end[1]-direction)//8)
 mask=128>>(end[1]&7);mask=mask if mode!='and' else 255^mask;carry=int(crossed if mode!='and' else not crossed);rotation=logical(mask)|carry
 end_pointer=address(end[0]+origin[0],end[1]+origin[1])
 if steep:
  before_row=(end[0]-1,end[1]-direction*borrowed);main=row_context(address(before_row[0]+origin[0],before_row[1]+origin[1]))
  alt_flags=column_context(end_pointer&255,direction,carry) if borrowed and crossed else rotation if borrowed else arithmetic(before_error,minor,True)[1]
 else:
  alt_flags=arithmetic((before_error-minor)&255,major)[1] if borrowed else arithmetic(before_error,minor,True)[1]
  if borrowed:flags=row_context(address(end[0]-1+origin[0],end[1]+origin[1]))[1]
  else:flags=column_context(end_pointer&255,direction,carry) if crossed else rotation
  main=(bitmap[end_pointer-0x4000],flags)
 return dict(af=main,alt_af=(half,alt_flags))
