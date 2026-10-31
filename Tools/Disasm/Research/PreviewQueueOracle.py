"""Независимая модель подготовки очереди по исходным записям и матричным коэффициентам."""
import struct
from CheckPreviewCoordinateMultiply import signed
from CheckPreviewTransform import adc16,CONTINUATIONS
from CheckPreviewBounds import reference as bounds


def transformed(coords,matrix,previous):
 results=list(previous);last=None
 for row in range(3):
  parts=[];carries=[]
  for term in range(3):
   coefficient=matrix[row][term];word=coords[term];cv=signed(coefficient,8);vv=signed(word,16);product=abs(cv)*abs(vv);magnitude=product//128;negative=bool((coefficient^(word>>8))&128)
   parts.append((-magnitude if negative else magnitude)&65535);carries.append(int(negative and magnitude!=0))
   upper=product>>15;alt_flags=(upper&0x28)|(0x40 if upper==0 else 0)|(0x10 if ((product>>16)&15)*2+((product>>15)&1)>15 else 0)
   context=(magnitude if negative else abs(vv),upper,alt_flags,CONTINUATIONS[row][term])
   if term==1:
    pair,flags=adc16(parts[1],parts[0],carries[1])
    if flags&4:return results,context,'transform_overflow'
   if term==2:
    value,flags=adc16(parts[2],pair,carries[2]);last=context
    if flags&4:return results,context,'transform_overflow'
    results[row]=value
 return results,last,None


def build(raw,records,matrix,pool,initial_params=(3,5,7),header_overrides=None):
 header_overrides=header_overrides or {};matrix=tuple(tuple(129 if value==128 else value for value in row) for row in matrix)
 def word(address):
  offset=address-0xC000
  return int.from_bytes(raw[offset:offset+2],'little')
 previous=[word(p) for p in (0xDAF6,0xDA38,0xDA16)]
 accepted=[];order=[];reasons=[];params=tuple(initial_params);flags=0xA7;model_offset=0x5B
 ix=0x2468;iy=0x5C3A;alt_af=(0x69,0xCF);alt_de=0x247A;bc=0x58BE;de=0x47AD;terminal=len(records)
 for index,(coords,model,angles) in enumerate(records):
  first=coords[0]
  if first>>8==128:
   if first&128:terminal=index;reasons.append('end_marker');break
   reasons.append('disabled');continue
  if any(abs(signed(word>>8,8))>=112 for word in coords):
   reasons.append('raw_coordinate_range');continue
  params=tuple(angles);flags=int((angles[0]|angles[2])==0);model_offset=model;iy=0xED11
  previous,last,reason=transformed(coords,matrix,previous);de,upper,alt_flags,alt_de=last;alt_af=(upper,alt_flags);bc=params[2]*256
  if reason:reasons.append(reason);continue
  first,second,depth=previous;de=depth
  first_high=first>>8;first_fold=first_high if first_high<128 else 255-first_high
  if first_fold>=96:reasons.append('transformed_first_range');continue
  if depth&32768:reasons.append('negative_depth');continue
  if depth>>8<31:model_offset=(model_offset+2)&255
  pointer=word(0xD000+model_offset)
  size=raw[pointer-0xC000];header=header_overrides.get(pointer+1,raw[pointer-0xC000+1]);flags|=header&128;exponent=header&127
  if not 1<=exponent<=6:raise ValueError('Масштаб модели вне доказанного домена')
  radius=size<<(exponent-1);bc=exponent*256+size;de=radius
  if ((depth+radius)&65535)&32768:reasons.append('depth_plus_radius');continue
  ix=(ix&0xFF00)|size
  outcome,_,_,bc,de,_=bounds(depth,first,second,size,exponent)
  if outcome!='accepted':reasons.append(outcome);continue
  node=dict(flags=flags,model=model_offset,angles=params,first=first,second=second,depth=depth,key2=coords[1])
  position=len(order)
  for p,node_index in enumerate(order):
   old=accepted[node_index];use_second=bool((old['flags']|flags)&128);old_key=old['key2'] if use_second else old['depth'];new_key=coords[1] if use_second else depth
   if ((old_key-new_key)&65535)&32768:position=p;break
  if order:
   ix=0xC700+14*order[0 if position==0 else position-1]
   if position:
    low=14*order[position] if position<len(order) else 14*order[-1] if len(order)>1 else 0x11
    iy=0xC700+low
  de=coords[1];bc=depth;order.insert(position,len(accepted));accepted.append(node);reasons.append('accepted')
 result=bytearray(pool)
 for p,node_index in enumerate(order):
  node=accepted[node_index];following=14*order[p+1] if p+1<len(order) else 1
  result[14*node_index:14*node_index+14]=struct.pack('<6B4H',following,node['flags'],node['model'],*node['angles'],node['first'],node['second'],node['depth'],node['key2'])
 return dict(pool=bytes(result),head=14*order[0] if order else 1,free=14*len(accepted),accepted=accepted,order=order,reasons=reasons,terminal=terminal,params=params,flags=flags,model_offset=model_offset,results=previous,ix=ix,iy=iy,alt_af=alt_af,alt_de=alt_de,bc=bc,de=de)
