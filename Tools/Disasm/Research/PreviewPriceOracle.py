"""Независимая модель двух ценовых текстовых проходов, используется общей панелью и прямым тестом D3D."""
from CheckTextStream import reference
from CheckPreviewDescriptions import paint_positions


def after_cr(m,start,count):
 for _ in range(count):start=m.index(13,start)+1
 return start


def calculate(m,selector,owned,index,bc,de):
 width,height=m[0xAEB3],m[0xAEAB];origin=(m[0xAEBB]+256*m[0xAEBF],m[0xAEC7]+256*m[0xAECB]);working=bytearray(m);working[0xCE8C]=10;bank=bytearray(m[0xC000:]);positions=[];columns=tuple(m[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F));widths=m[0x8900:0x8A00]
 # Отдельные заголовок и тело запускаются с независимыми начальными курсорами.
 reference(m[0xCECE:],widths,0,8,width,height,0,columns,origin,32,positions=positions)
 table=0xCE99 if selector==1 else 0xCE40;end=None
 if owned:
  if index==6:working[0xCE8C]=13
  end=after_cr(working,table,index+2)-1;old=working[end];working[end]=10
 start=after_cr(working,table,index+1);offset,x,y,a,f,_=reference(working[start:],widths,0,24,width,height,0,columns,origin,32,positions=positions);screen,glyphs=paint_positions(m,positions,width,height,origin)
 bank[0xE8C]=13 if owned and index==6 else 10;bank[0x2148]=index
 # Оракул количества использует положение курсора, обычный AF рынка задаётся отдельно.
 q=((y-24)&255)//8;count=q+1;flags=(count&0xA8)|(0x10 if q&15==15 else 0)
 registers=(start+offset,end if owned else de,(bc&0xFF00)|index if owned else bc,a if owned else 0,f if owned else 0x44,count,flags,x,y)
 return dict(registers=registers,screen=screen,bank=bank,glyphs=glyphs,karen=bool(owned and index==6))
