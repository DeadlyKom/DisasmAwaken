"""Восемь байтовых шагов D4DF, отделённые от сдвиговых инструкций Z80."""
from PreviewEdgeRasterOracle import arithmetic


def divide(high,low,divisor,carry):
 remainder=high;quotient=0;flags=0
 for bit in range(7,-1,-1):
  # Старший девятый разряд исходный код теряет перед SUB, восстановление тоже остаётся байтовым.
  trial=((remainder*2)|((low>>bit)&1))&255
  remainder,flags=arithmetic(trial,divisor,True)
  accepted=trial>=divisor;quotient=(quotient*2+accepted)&255
  if not accepted:remainder,flags=arithmetic(remainder,divisor)
 inverse=quotient^255
 return dict(remainder=remainder,encoded=(carry<<7)|(inverse>>1),flags=flags,quotient_bits=quotient,inverse_quotient=inverse)
