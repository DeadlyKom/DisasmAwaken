"""Обход физических групп по двум входам D896 и D819 с независимой числовой композицией."""
from PreviewModelGroups import records
from PreviewVertexProductsOracle import general,planar
from PreviewVertexGroupOracle import group


def walk(source,model_offset,entry,coefficients,angle,reference,base,centres,buffer,empty=False):
 model=records(source,model_offset);groups=[] if empty else model['groups'];exponent=model['exponent'];memory=bytearray(buffer);offset=4;last=None;last_success=None;vertices=0
 alternates=((0x69,0xCF),0x58BE,0x47AD,0x369C);product_inputs=None;reasons=[]
 if entry==0xD819:
  delta=(angle-reference)&255;sin=source[0x400+delta];cos=source[0x400+((delta+64)&255)];planar_coefficients=(cos,sin,sin,cos)
 else:planar_coefficients=None
 for address,data in groups:
  mask,*factors=data;words,thirds=general(coefficients,factors) if entry==0xD896 else planar(planar_coefficients,factors)
  last=group(words,thirds,mask,base,exponent,centres,offset,memory,initial_alternates=alternates)
  memory=last['buffer'];offset=last['stack']&255;alternates=(last['alt_af'],last['alt_bc'],last['alt_de'],last['alt_hl'])
  if last['last_success'] is not None:last_success=last['last_success']
  vertices+=len(last['vertices']);reasons+=last['reasons'];product_inputs=(words,thirds)
 terminal=model['pointer']+2 if empty else model['terminator']
 return dict(buffer=memory,offset=offset,last=last,last_success=last_success,vertices=vertices,reasons=reasons,product_inputs=product_inputs,planar_coefficients=planar_coefficients,bc=last['bc'] if last else exponent*256+0xC9,de=last['de'] if last else 0x247A,ix=last['ix'] if last else 0x2468,iy=last['iy'] if last else 0x5C3A,alternates=alternates,hl=terminal+1,model=model,groups=groups)
