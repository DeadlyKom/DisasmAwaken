"""Произведения трёх координат группы перед генератором D908."""
from PreviewModelMatrixOracle import product


def general(coefficients,factors):
 # Потребитель берёт столбцы композиции в физическом порядке 1,3,2.
 columns=(0,2,1);words=[];thirds=[]
 for column,factor in zip(columns,factors):
  first=product(coefficients[0][column],factor)[0]
  second=product(coefficients[1][column],factor)[0]
  third=product(coefficients[2][column],factor)[0]
  words.append(second+256*first);thirds.append(third)
 return tuple(words),tuple(thirds)


def planar(coefficients,factors):
 cos_first,sin_first,sin_second,cos_second=coefficients;first,second,third=factors
 p=lambda a,b:product(a,b)[0]
 return (p(cos_first,first)*256,second,p(sin_first,third)*256),(p((-sin_second)&255,first),0,p(cos_second,third))
