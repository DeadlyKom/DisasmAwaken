"""Независимый разбор внутреннего потока DD4F, композиция геометрии и трёх режимов рёбер."""
from PreviewFaceOrientationOracle import orientation
from PreviewPolygonOracle import raster as polygon,registers as polygon_registers
from PreviewEdgeRasterOracle import raster as edge,registers as edge_registers,arithmetic


def render(source,stream,vertices,initial_face_flag,initial):
 bitmap=bytes(source);position=0;events=[];face_flag=initial_face_flag;fill_mode=0x5A;contour_size=0xF1;line_mode=None
 def word(offset):return initial[offset]*256+initial[offset+1]
 state=dict(de=word(4),bc=word(2),ix=word(8),iy=word(10),alt_af=tuple(initial[16:18]),alt_bc=word(18),alt_de=word(20),alt_hl=word(22))
 def point(index):return vertices[(index+2)&255],vertices[index]
 while True:
  header=stream[position]
  if header==0:break
  count=header&15;indices=stream[position+1:position+1+count];position+=count+1
  assert len(indices)==count
  if not header&128:
   assert count>=3
   selected=indices[:3] if count<5 else indices[::2][:3]
   facing_result=orientation(vertices,selected,count,state['alt_af'][1]&1,state['ix']);first_product=facing_result['first_product']
   state.update(de=facing_result['low'],ix=facing_result['ix'],alt_af=facing_result['alt_af'],alt_bc=first_product['bc'],alt_de=first_product['de'],alt_hl=first_product['hl'])
   facing=facing_result['af'][1]&128
   face_flag=0 if facing else 1
   if not facing:state['bc']=count+1;continue
   fill_mode=(header>>4)&7;contour_size=count*2;points=tuple(point(i) for i in indices)
   events.append(('polygon',fill_mode,points));bitmap=polygon(bitmap,points,fill_mode)
   out=polygon_registers(points,fill_mode)
   for key in ('de','bc'):state[key]=out[key]
   if out['degenerate']:
    _,flags=arithmetic(count*2,1,True);state['alt_af']=(count*2-1,flags&254)
   else:
    for key in ('ix','iy','alt_af','alt_bc','alt_de','alt_hl'):state[key]=out[key]
  else:
   assert count>=2
   if header&64 and face_flag:state['bc']=count+1;continue
   operator=header&48;line_mode='and' if operator==0 else 'or' if operator==16 else 'xor'
   points=tuple(point(i) for i in indices)
   for first,second in zip(points,points[1:]):
    events.append(('edge',line_mode,first,second));bitmap=edge(bitmap,first,second,line_mode)
    if first==second:state['de']=second[0]*256+second[1]
    else:
     dy=abs(second[0]-first[0]);dx=abs(second[1]-first[1]);state['de']=max(dx,dy)*256+min(dx,dy)
     state['alt_af']=edge_registers(first,second,line_mode,bitmap)['alt_af']
   state['bc']&=255
 return dict(bitmap=bitmap,events=events,position=position,face_flag=face_flag,fill_mode=fill_mode,contour_size=contour_size,line_mode=line_mode,registers=state)
