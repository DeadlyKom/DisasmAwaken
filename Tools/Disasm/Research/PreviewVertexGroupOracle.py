"""Числовая модель группы вершин D908..DA13 и композиция с доказанной перспективой."""
from PreviewPerspectiveOracle import project,registers
WORD_TARGETS={0:0xD97A,1:0xD9AE,3:0xD9BB,2:0xD9CA,5:0xD9EF,4:0xD9FC,6:0xD9D5,7:0xD9E2}
BYTE_TARGETS={5:0xD9F2,4:0xD9FF,6:0xD9D8,7:0xD9E5}


def rotate(value):return ((value<<1)|(value>>7))&255


def packed_rotate(value):return rotate(value&255)+256*rotate(value>>8)


def packed_negative(value):return ((-(value&255))&255)+256*((-(value>>8))&255)


def combinations(u,v,w,negative):
 values={0:(u+v+w)&65535}
 values[1]=(values[0]-packed_rotate(u))&65535
 values[3]=(values[1]-packed_rotate(v))&65535
 values[2]=(values[3]+packed_rotate(u))&65535
 values[5]=negative(values[2])
 values[4]=(values[5]+packed_rotate(u))&65535
 values[6]=(values[4]-packed_rotate(v))&65535
 values[7]=(values[6]-packed_rotate(u))&65535
 return values


def byte_combinations(u,v,w):
 values={0:(u+v+w)&255};ru=rotate(u);rv=rotate(v)
 values[1]=(values[0]-ru)&255;values[3]=(values[1]-rv)&255;values[2]=(values[3]+ru)&255
 values[5]=(-values[2])&255;values[4]=(values[5]+ru)&255;values[6]=(values[4]-rv)&255;values[7]=(values[6]-ru)&255
 return values


def group(words,thirds,mask,base,exponent,centres,offset,buffer):
 input_low=words[0]&255;words=combinations(*words,packed_negative);thirds=byte_combinations(*thirds)
 if mask==1:vertices=[(words[0],thirds[0])]
 elif mask==129:vertices=[(words[0],thirds[0]),(packed_negative(words[0]),(-thirds[0])&255)]
 else:vertices=[(words[index],thirds[index]) for index in (0,1,3,2,6,7,5,4) if mask&(1<<index)]
 memory=bytearray(buffer);stack=0xC600+offset;reasons=[];alt_af=(0x69,0xCF);alt_bc=0x58BE;alt_de=0x47AD;alt_hl=0x369C;last_success=None;last_flags=0
 for packed,third in vertices:
  vertex=(third,packed&255,packed>>8);out=project(vertex,base,exponent,centres);previous=memory[stack-6-0xC5F0]+256*memory[stack-5-0xC5F0]
  context=registers(vertex,base,exponent,centres,stack,previous,initial_alt_af=alt_af,initial_alt_bc=alt_bc)
  for pointer,value in ((stack-2,out['first']),(stack-4,out['second'])):
   memory[pointer-0xC5F0]=value&255;memory[pointer+1-0xC5F0]=value>>8
  if out['valid']:last_success=(out['second'],stack-6)
  alt_af=context['alt_af'];alt_bc=context['alt_bc'];alt_de=context['alt_de'];alt_hl=context['alt_hl'];last_flags=context['af'][1];stack+=5;reasons.append(out['reason'])
 # При обычной маске без бита 4 последний BIT оставляет Z/PV, даже если ранее проектировались другие вершины.
 if mask not in (1,129) and not mask&16:last_flags=0x44
 final_flags=(last_flags&0xC4)|((stack>>8)&0x28)
 final_de=vertices[-1][0] if mask in (1,129) else words[4]
 return dict(words=words,thirds=thirds,vertices=vertices,buffer=memory,stack=stack,af=(stack&255,final_flags),bc=mask*256+rotate(input_low),de=final_de,ix=(((-thirds[0])&255) if mask==129 else thirds[0])*256+thirds[2],iy=thirds[1]*256+thirds[3],alt_af=alt_af,alt_bc=alt_bc,alt_de=alt_de,alt_hl=alt_hl,last_success=last_success,reasons=reasons)
