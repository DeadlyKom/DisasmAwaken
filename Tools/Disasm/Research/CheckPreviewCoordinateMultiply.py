"""Независимая целочисленная модель исходного переходного умножителя EB10."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP,PC
from Analyze import payload
from CheckWorldSignature import logical_flags


class Memory(list):
 def __setitem__(self,key,value):
  if getattr(self,'recording',False):self.writes.append((key,value))
  super().__setitem__(key,value)


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def main():
 m=Memory([0]*65536);raw=payload(6);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x3FFF,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x47AD,'^DE':0x369C,'^BC':0x58BE,'^AF':0x69CF},None,False);m.recording=True;cases=0
 def check(coefficient,value):
  nonlocal cases
  s.registers[:]=initial;r=s.registers;r[A]=coefficient;r[20]=value>>8;r[21]=value&255;m.writes=[]
  # Расчёт математического модуля произведения и усечения к нулю, коэффициент 80 отдельно не является штатным.
  cv=signed(coefficient,8);vv=signed(value,16);magnitude=0 if coefficient==128 else abs(cv)*abs(vv)//128;negative=bool((coefficient^(value>>8))&128);answer=(-magnitude if negative else magnitude)&65535;sign_byte=coefficient^(value>>8)
  expected_flags=((answer>>8)&0xA8)|(0x40 if answer==0 else 0)|(0x10 if magnitude&0xFFF else 0)|2|bool(magnitude) if negative else logical_flags(sign_byte)
  product=0 if coefficient==128 else abs(cv)*abs(vv);upper=product>>15;previous=product>>16;carry=(product>>15)&1;alt_flags=(upper&0x28)|(0x40 if upper==0 else 0)|(0x10 if (previous&15)*2+carry>15 else 0)
  s.run(start=0xEB10,stop=0x3FFF)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[2],r[3],r[A],r[F],r[16],r[17],r[SP])==(answer,magnitude if negative else abs(vv),0x58,0,sign_byte,expected_flags,upper,alt_flags,0x7FFE),(coefficient,value,tuple(r[:8]),r[16:18],answer,expected_flags,upper,alt_flags)
  assert r[18:24]==[0x36,0xC9,0x3F,0xFF,0x13,0x57] and r[8:12]==initial[8:12] and m.writes==[(0xEB7C,255),(0xEB7D,63)]
  cases+=1
 # Проверка всех 16-битных координат на крайних и единичных коэффициентах.
 for coefficient in (129,255,0,1,127):
  for value in range(65536):check(coefficient,value)
 # Проверка всех коэффициентов на наборах старших байтов и младших границах, включая 80.
 for coefficient in range(256):
  for high in range(0,256,8):
   for low in (0,1,127,128,254,255):check(coefficient,high*256+low)
 report=dict(passed=True,cases=cases,all_coordinate_words_for_coefficients=[-127,-1,0,1,127],all_coefficient_bytes_sampled=True,coefficient_80_original_zero_result_preserved=True,independent_integer_product_and_register_flags=True,exact_two_self_modified_return_bytes=True,sp_unchanged=True,alternate_and_index_registers_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewCoordinateMultiplyVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
