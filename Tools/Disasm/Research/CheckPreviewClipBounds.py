"""Настройка исходных границ D3D, все байтовые размеры и полное сравнение банка."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from Analyze import payload
from D3DClipFacts import PATCHES,PATCH_FORMS


def reference_patch(max_x,max_y,min_x,min_y):
 result={}
 def byte(address,value):result[address]=value
 def word(address,value):result[address]=value&255;result[address+1]=value>>8
 byte(0xDAE7,((max_x+1)&255)//2);byte(0xDBA5,((max_y+1)&255)//2)
 for a,x,y in ((0xE7DB,max_x,max_y),(0xE7BA,min_x,min_y),(0xE7D0,max_x,min_y),(0xE7C5,min_x,max_y)):word(a,256*x+y)
 for addresses,value in (((0xE613,0xE6E0,0xE6F3,0xE72E,0xE78B),max_x),((0xDF7F,),(max_x+1)&255),((0xE5F4,0xE695,0xE6A8,0xE73F,0xE79C),min_x),((0xE646,0xE69D,0xE6E8,0xE788,0xE799,0xE7AB),max_y),((0xDF64,),(max_y+1)&255),((0xE627,0xE692,0xE6DD,0xE72B,0xE73C,0xE74E),min_y)):
  for address in addresses:byte(address,value)
 return result


def main():
 raw=payload(6);forms={}
 for address,(opcode,kind,size) in PATCH_FORMS.items():
  assert raw[address-0xC001]==opcode,(hex(address),kind)
  forms[PATCHES[address]]=dict(address=address,instruction=kind,bytes_written=size)
 m=bytearray(65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=bytes([255,63]);expected=bytearray(m[0xC000:]);s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 for max_x in range(256):
  for max_y in range(256):
   for min_x,min_y in ((0,0),((max_y*73+19)&255,(max_x*47+31)&255)):
    s.registers[:]=initial;r=s.registers;r[H]=max_x;r[L]=max_y;r[D]=min_x;r[E]=min_y
    # Независимая геометрия задаёт четыре угла и повторённые байтовые пределы.
    for address,value in reference_patch(max_x,max_y,min_x,min_y).items():expected[address-0xC000]=value
    s.run(start=0xE011,stop=0x3FFF)
    # Флаги принадлежат последнему INC верхнего Y, Carry остаётся от его раннего деления на два.
    value=(max_y+1)&255;flags=(value&0xA8)|(0x40 if value==0 else 0)|(0x10 if max_y&15==15 else 0)|(4 if max_y==127 else 0)|(value&1)
    assert (r[H],r[L],r[D],r[E],r[A],r[F],r[SP])==(max_x,min_y,min_x,max_y,min_y,flags,0x8000)
    assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    assert m[0xC000:]==expected,(max_x,max_y,min_x,min_y);cases+=1
 report=dict(passed=True,cases=cases,original_patch_instruction_forms=forms,all_byte_width_height_pairs=True,nonzero_and_inverted_lower_bounds=True,full_bank_compared=True,byte_overflow_preserved=True,full_register_and_flags_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipBoundsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
