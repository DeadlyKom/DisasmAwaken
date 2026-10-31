"""Геометрические пересечения рёбер по строкам, без регистров IX/IY и развёрнутого кода."""
from PreviewEdgeRasterOracle import address
from PreviewEdgeRasterOracle import arithmetic,logical
PATTERNS=((255,0),(119,170),(85,255),(17,85),(0,0),(0,0),(0,0),(0,0))


def segment(vertices,row,direction):
 start=min(range(len(vertices)),key=lambda i:vertices[i][0]);i=start
 for _ in vertices:
  j=(i+direction)%len(vertices);y0,x0=vertices[i];y1,x1=vertices[j]
  if y0<=row<y1:
   return y0,x0,y1,x1
  i=j
 raise AssertionError(('no_ascending_edge',vertices,row,direction))


def boundary(vertices,row,direction):
 y0,x0,y1,x1=segment(vertices,row,direction);height=y1-y0
 return x0+((x1-x0)*(row-y0)+height//2)//height


def raster(source,vertices,mode):
 result=bytearray(source);low=min(y for y,x in vertices);high=max(y for y,x in vertices)
 first,delta=PATTERNS[mode]
 for row in range(low,high):
  left=boundary(vertices,row,-1);right=boundary(vertices,row,1)
  pattern=first^(delta if (row-low)&1 else 0)
  for column in range(left,right):
   pointer=address(row,column)-0x4000;mask=128>>(column&7)
   result[pointer]=(result[pointer]&~mask)|(pattern&mask)
 return bytes(result)


def registers(vertices,mode):
 """Конечный контекст выводится из последней строки и последних двух геометрических рёбер."""
 low=min(y for y,x in vertices);high=max(y for y,x in vertices)
 if low==high:return dict(degenerate=True,af=(high,0x42|(high&0x28)),bc=1,de=high*257)
 left=boundary(vertices,high-1,-1);right=boundary(vertices,high-1,1)
 def edge(direction):
  y0,x0,y1,x1=segment(vertices,high-1,direction);height=y1-y0;delta=x1-x0
  # Целая часть шага округлена вверх, нулевой наклон исходно использует +1 с коррекцией -1.
  step=-((-delta)//height) if delta else 1
  return x1,height//2,(0x2000+32*step)&65535
 left_end,left_error,left_step=edge(-1);right_end,right_error,right_step=edge(1)
 difference=right//8-left//8
 if difference:tail=(-2*difference)&255
 else:
  covered=sum(128>>(x&7) for x in range(left,right));tail=covered^255
 first,delta=PATTERNS[mode];pattern=first^(delta if (high-low)&1 else 0)
 # Адрес строки использует перенос целого шага левой границы до дробной коррекции.
 # На колонке 255 ошибка адреса может накапливаться несколько пустых строк подряд.
 pointer=address(low,0);b=pointer>>8;c=pointer&255
 for row in range(low,high):
  x=boundary(vertices,row,-1);right_x=boundary(vertices,row,1)
  y0,x0,y1,x1=segment(vertices,row,-1);height=y1-y0;delta_x=x1-x0
  step=-((-delta_x)//height) if delta_x else 1
  increment=(0x2000+32*step)&65535;c=(c&0xE0)|(right_x//8)
  left_before=(((row&7)<<13)+x*32+mode*2)&65535;b=(b+1)&255
  if left_before+increment>65535:
   total=c+32;c=total&255
   if total<256:b=(b-8)&255
 return dict(degenerate=False,af=(high,0x42|(high&0x28)),bc=b*256+c,de=0xD100|tail,
  ix=(((high&7)<<13)+left_end*32+mode*2)&65535,
  iy=(((high&7)<<13)+right_end*32+mode*2+16)&65535,
  alt_hl=right_error*256+left_error,alt_bc=left_step,alt_de=right_step,alt_af=(pattern,logical(pattern)))
