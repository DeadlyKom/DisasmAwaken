"""Математическая перспектива DA14..DBD8, без повторения поразрядного делителя Z80."""


def signed(value,bits):
 return value-(1<<bits) if value&(1<<(bits-1)) else value


def axis(value,base,exponent,depth,centre):
 coordinate=signed((signed(value,8)*(1<<(exponent-1))+base)&65535,16)
 magnitude=abs(coordinate)
 if depth==0 or magnitude>=128*depth:return None
 # Деление усечено к нулю до добавления исходного центра с оборачиванием слова.
 quotient=magnitude*256//depth
 return ((-quotient if coordinate<0 else quotient)+centre)&65535


def project(vertex,base,exponent,centres):
 third,first,second=vertex;depth_base,first_base,second_base=base
 depth=(signed(third,8)*(1<<(exponent-1))+depth_base)&65535
 if depth&32768:
  return dict(reason='negative_depth',first=depth_base,second=0x8000|(depth_base&255),valid=False)
 projected_first=axis(first,first_base,exponent,depth,centres[0])
 if projected_first is None:return dict(reason='first_axis',first=depth,second=0x8000|(depth&255),valid=False)
 projected_second=axis(second,second_base,exponent,depth,centres[1])
 if projected_second is None:return dict(reason='second_axis',first=projected_first,second=0x8000|(depth&255),valid=False)
 return dict(reason='accepted',first=projected_first,second=projected_second,valid=True)


def flags16(a,b,subtract=False):
 total=a-b if subtract else a+b;value=total&65535
 mathematical=signed(a,16)+(-signed(b,16) if subtract else signed(b,16))
 return ((value>>8)&0xA8)|(64 if value==0 else 0)|(16 if (a^b^value)&4096 else 0)|(4 if not -32768<=mathematical<=32767 else 0)|(2 if subtract else 0)|int(total<0 or total>65535)


def absolute_context(value,base,exponent):
 term=(signed(value,8)*(1<<(exponent-1)))&65535;coordinate=(term+base)&65535;flags=flags16(term,base)
 if coordinate&32768:
  high=(~(coordinate>>8))&255
  return -signed(coordinate,16),(high,(flags&0xC5)|(high&0x28)|0x12),flags
 return coordinate,(255 if value&128 else 0,flags),flags


def rejected_axis_context(magnitude,depth):
 # Два числовых предела соответствуют проверкам целой части частного до получения его 15 допустимых разрядов.
 if magnitude//256>=depth:return magnitude&255,flags16(magnitude//256,depth,True)
 return ((magnitude&255)*2+1)&255,flags16(magnitude//128,depth,True)


def quotient_context(magnitude,depth):
 quotient,remainder=divmod(magnitude*256,depth)
 # Последний остаток и младший бит частного однозначно определяют последний SBC делителя.
 before_subtract=remainder+(depth if quotient&1 else 0);flags=flags16(before_subtract,depth,True)
 high=quotient>>8
 return high,(flags&0xC4)|(high&0x28)|0x12|((~high)&1)


def registers(vertex,base,exponent,centres,stack,previous_word,initial_alt_af=(0x69,0xCF),initial_alt_bc=0x58BE):
 expected=project(vertex,base,exponent,centres);third,first,second=vertex;depth_base,first_base,second_base=base
 term=(signed(third,8)*(1<<(exponent-1)))&65535;depth=(term+depth_base)&65535
 if expected['reason']=='negative_depth':
  a=255 if third&128 else 0;f=flags16(term,depth_base);alt_af=initial_alt_af;alt_bc=initial_alt_bc;alt_de=expected['second']
 else:
  first_magnitude,first_sign,first_flags=absolute_context(first,first_base,exponent)
  if expected['reason']=='first_axis':
   a,f=rejected_axis_context(first_magnitude,depth);alt_af=first_sign;alt_bc=first_base;alt_de=expected['second']
  else:
   second_magnitude,second_sign,second_flags=absolute_context(second,second_base,exponent)
   if expected['reason']=='second_axis':
    a,f=rejected_axis_context(second_magnitude,depth);alt_af=second_sign;alt_bc=second_base;alt_de=expected['second']
   else:
    quotient=second_magnitude*256//depth
    a=(~(quotient>>8))&255 if second_flags&128 else (255 if second&128 else 0)
    f=second_flags;alt_af=quotient_context(second_magnitude,depth);alt_bc=previous_word;alt_de=centres[1]
 # Последнее ADD HL,SP сохраняет S/Z/PV предыдущего пути и обновляет H/C и недокументированные биты адресом p+5.
 next_stack=(stack+5)&65535;add_flags=flags16(9,(stack-4)&65535)
 final_flags=(f&0xC4)|(add_flags&0x39)
 return dict(af=(a,final_flags),alt_af=alt_af,alt_bc=alt_bc,alt_de=alt_de,alt_hl=next_stack)
