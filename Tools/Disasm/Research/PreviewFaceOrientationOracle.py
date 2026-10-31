"""Точная ориентация DFA6 с исходными заёмами и двумя произведениями E869."""
from PreviewFaceProductOracle import product,signed


def subtract(first,second,carry):
 total=first-second-carry;value=total&65535;mathematical=signed(first)-signed(second)-carry
 flags=((value>>8)&0xA8)|(64 if value==0 else 0)|(16 if (first&4095)-(second&4095)-carry<0 else 0)|(4 if not -32768<=mathematical<=32767 else 0)|2|int(total<0)
 return value,flags


def orientation(buffer,indices,count,alt_carry,initial_ix=0x2468):
 points=[]
 for offset in indices:
  second=buffer[offset]+256*buffer[(offset+1)&255];first=buffer[(offset+2)&255]+256*buffer[(offset+3)&255];points.append((first,second))
 (x0,y0),(x1,y1),(x2,y2)=points
 dx2,f=subtract(x2,x0,int(count<5));dx1,f=subtract(x1,x0,f&1);dy2,f=subtract(y2,y0,f&1);dy1,f=subtract(y1,y0,f&1)
 first_product=product(dy1,dx2,initial_bc=x0,initial_ix=initial_ix)
 second_product=product(dx1,dy2,initial_bc=y0,initial_ix=first_product['ix'])
 low,f=subtract(second_product['de'],first_product['de'],second_product['af'][1]&1);high,f=subtract(second_product['hl'],first_product['hl'],f&1)
 incremented=(indices[1]+3)&255;previous=(incremented-1)&255
 alt_flags=(incremented&0xA8)|(64 if incremented==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)|alt_carry
 return dict(low=low,high=high,af=(second_product['af'][0],f),alt_af=(x1>>8,alt_flags),first_product=first_product,second_product=second_product,ix=second_product['ix'],differences=(dx2,dx1,dy2,dy1),points=points)
