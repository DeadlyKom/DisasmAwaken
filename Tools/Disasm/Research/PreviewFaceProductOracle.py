"""Независимая числовая модель знакового произведения E869, включая особый край 8000."""
from CheckWorldSignature import logical_flags


def signed(value):return value-65536 if value&32768 else value


def product(first,second,initial_bc=0x36C9,initial_ix=0x2468):
 a=abs(signed(first));b=abs(signed(second));large=a>=256 and b>=256
 # У длинной ветви разряд 15 множителя теряется, затем безусловный хвост предполагает ведущую единицу в разряде 8.
 magnitude=a*(256 if large and b==32768 else b)
 negative=bool((first^second)&32768);answer=(-magnitude if negative else magnitude)&0xFFFFFFFF;sign=(first>>8)^(second>>8)
 if negative:
  high=answer>>16;borrow=int(bool(magnitude&65535));magnitude_high=magnitude>>16
  flags=((high>>8)&0xA8)|(64 if high==0 else 0)|(16 if (magnitude_high&4095)+borrow else 0)|2|int(bool(magnitude_high+borrow));bc=magnitude_high
 else:
  flags=logical_flags(sign);bc=0 if large else (initial_bc if a<256 and b<256 else initial_bc&0xFF00)
 return dict(result=answer,hl=answer>>16,de=answer&65535,bc=bc,af=(sign,flags),ix=magnitude&65535 if large else initial_ix,large=large,magnitude=magnitude,extreme_multiplier_lost=large and b==32768)
