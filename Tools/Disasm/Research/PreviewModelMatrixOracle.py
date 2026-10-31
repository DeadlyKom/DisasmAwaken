"""Независимые числовые формулы EF5E..F055, без исполнения Z80."""

TARGETS=(0xD561,0xD563,0xD565,0xD5FD,0xD5FF,0xD601,0xD6A9,0xD6AB,0xD6AD)


def signed(value):
 return value-256 if value&128 else value


def square(index):
 return min(index,255-index)**2//127


def product(a,b):
 difference=(signed(a)//2-signed(b)//2)&255
 summed=(difference+b)&255
 return (square(summed)-square(difference))&255,summed,square(difference)


def arithmetic(a,b,subtract=False):
 total=a-b if subtract else a+b;value=total&255
 overflow=not -128<=signed(a)+(-signed(b) if subtract else signed(b))<=127
 flags=(value&0xA8)|(64 if value==0 else 0)|(16 if ((a^b^value)&16) else 0)|(4 if overflow else 0)|(2 if subtract else 0)|int(total<0 or total>255)
 return value,flags


def corrected(a,b,subtract=False):
 value,flags=arithmetic(a,b,subtract)
 if flags&4:
  value,flags=arithmetic(0,value,True)
  if flags&4:
   old=value;value=(value-1)&255
   flags=(flags&1)|(value&0xA8)|(64 if value==0 else 0)|(16 if old&15==0 else 0)|(4 if old==128 else 0)|2
 return value,flags


def matrix(angles,flags,sine):
 first,second,third=angles
 if flags&1:
  s=sine[second];c=sine[(second+64)&255]
  return dict(values=(c,0,(-s)&255,s,0,c,0,127,0),shortcut=True,af=(127,68),hl=0xC400|second,b=second)
 s1=sine[first];c1=sine[(first+64)&255];s2=sine[second];c2=sine[(second+64)&255];s3=sine[third];c3=sine[(third+64)&255]
 p=lambda a,b:product(a,b)[0]
 a11=p(c3,c2);a21=p(s2,c3)
 a12=corrected(p(p(c2,c1),s3),p(s2,s1))[0]
 a32=p(c3,c1)
 a22=corrected(p(p(s2,c1),s3),p(c2,s1),True)[0]
 a13=corrected(p(p(c2,s1),s3),p(s2,c1),True)[0]
 a33=p(c3,s1)
 last,index,table_value=product(p(s2,s1),s3)
 a23,f=corrected(last,p(c2,c1))
 return dict(values=(a11,a12,a13,a21,a22,a23,(-s3)&255,a32,a33),shortcut=False,af=(a23,f),hl=0xC300|index,de=s3*256+table_value,bc=s1*256+c1,ix=p(c2,c1)*256+s2,iy=c3*256+c2)
