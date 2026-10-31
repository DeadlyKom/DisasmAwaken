"""Композиция явных решений отсечения и независимых растровых моделей полного DBE9."""
from PreviewFaceOrientationOracle import orientation
from PreviewPolygonOracle import raster as polygon
from PreviewEdgeRasterOracle import raster as edge
from CheckPreviewClipCaseSemantics import expected
from CheckClipGeometry import classify


def render(source,stream,vertices,points,initial_flag,profile,cases):
 bitmap=bytes(source);events=[];position=0;face_flag=initial_flag;fill_mode=0x5A;size=0xF1;line_mode=None;seen=0xA7;block=0x5A;clipped_polygons=clipped_segments=0;line_state=None
 def point(i):return vertices[i],vertices[(i+2)&255]
 def clip(first,second,corner_seen,mode):
  a,b=classify(first,profile),classify(second,profile)
  return expected(cases[a,b],first,second,corner_seen,mode,profile)
 while stream[position]:
  header=stream[position];count=header&15;indices=stream[position+1:position+count+1];position+=count+1
  if not header&128:
   assert 3<=count<=15
   selected=indices[:3] if count<5 else indices[::2][:3]
   facing=orientation(vertices,selected,count,0)['af'][1]&128;face_flag=0 if facing else 1
   if not facing:continue
   codes=[vertices[(i+4)&255] for i in indices];combined=0
   for code in codes:combined|=code
   if 0 in codes or (combined^255)&0xF0:continue
   fill_mode=(header>>4)&7
   if combined&15:
    seen=0;block=0;contour=[];special=False;clipped_polygons+=1
    for first,second in zip([points[indices[-1]],*[points[i] for i in indices[:-1]]],[points[i] for i in indices]):
     added,seen,exit,_=clip(first,second,seen,0);contour+=added
     if exit=='special':special=True;break
    size=len(contour)*2
    if special or size<6:continue
   else:contour=[point(i) for i in indices];size=count*2
   plotted=tuple((row,col) for col,row in contour);events.append(('polygon',fill_mode,plotted));bitmap=polygon(bitmap,plotted,fill_mode)
  else:
   assert 2<=count<=15
   if header&64 and face_flag:continue
   operator=header&48;line_mode='and' if operator==0 else 'or' if operator==16 else 'xor'
   for i,j in zip(indices,indices[1:]):
    c0,c1=vertices[(i+4)&255],vertices[(j+4)&255];combined=c0|c1;line_state=(points[i],points[j],c0,c1)
    if not c0 or not c1 or (combined^255)&0xF0:continue
    if combined&15:
     a,b=points[i],points[j]
     if c0==0xF0:a,b=b,a
     contour,seen,exit,_=clip(a,b,seen,1);block=1;size=2*len(contour);clipped_segments+=1
     if exit=='special' or size!=4:continue
     first,second=contour
    else:first,second=point(i),point(j)
    first=(first[1],first[0]);second=(second[1],second[0]);events.append(('edge',line_mode,first,second));bitmap=edge(bitmap,first,second,line_mode)
 return dict(bitmap=bitmap,events=events,position=position,face_flag=face_flag,fill_mode=fill_mode,contour_size=size,line_mode=line_mode,
  seen=seen,block=block,clipped_polygons=clipped_polygons,clipped_segments=clipped_segments,line_state=line_state)
