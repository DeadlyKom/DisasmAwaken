"""Полная композиция границ, трёх таблиц и выбора модели в исходном D3D E13C."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context
from CheckSpriteLineTable import address
from CheckPreviewClipBounds import reference_patch
from Analyze import payload


def main():
 _,_,banks=make_context();raw=payload(6);template=bytearray(65536);template[0x4000:0x8000]=bytes(banks[5]);template[0x8000:0xC000]=bytes(banks[2]);template[0xC000:0xC000+len(raw)]=raw;template[0x7FFE:0x8000]=bytes([255,63]);cases=0
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 for selector in range(256):
  for k in range(16):
   m=bytearray(template);s=Simulator(m);s.registers[:]=initial;r=s.registers;max_x=(k*17)&255;max_y=(k*31)&255;min_x=(k*47)&255;min_y=(k*73)&255;x=(k*53)&255;y=(k*19)&255;row=(k*37)&255;base=(k*71)&255;old_f=(selector*13+k*7)&255
   r[A]=selector;r[F]=old_f;r[H]=max_x;r[L]=max_y;r[D]=min_x;r[E]=min_y;r[20]=y;r[21]=x;m[0xE146]=row;m[0xE148]=base;expected=bytearray(m)
   # Независимые геометрические модели дают общий результат двух настоящих вызываемых помощников.
   for ptr,value in reference_patch(max_x,max_y,min_x,min_y).items():expected[ptr]=value
   origin=(y+16)&255;column=((x+8)&255)//8;rows=[address(origin+i) for i in range(256)];end=address(origin+256);expected[0xC900:0xCA00]=bytes(a>>8 for a in rows);expected[0xCA00:0xCB00]=bytes(a&255 for a in rows);expected[0xCB00:0xCC00]=bytes(column+i//8 for i in range(256))
   # Байтовое смещение модели использует сумму индексов без переноса и особую добавку только для исходного A=1.
   summed=(row+base)&255;offset=(4*summed)&255;b=(selector-1)&255
   if selector==1:
    value=(offset+28)&255;flags=(value&0xA8)|(0x40 if value==0 else 0)|((offset^28^value)&0x10)|(4 if (~(offset^28)&(offset^value)&128) else 0)|int(offset+28>255);offset=value
   else:flags=(b&0xA8)|(0x40 if b==0 else 0)|(0x10 if selector&15==0 else 0)|(4 if selector==128 else 0)|2|int(bool(summed&64))
   expected[0xCDC6]=offset;expected[0x7FFA:0x7FFE]=bytes([0x44,0xE1,old_f,selector]);s.run(start=0xE13C,stop=0x3FFF)
   alt_a=(origin&7) if origin&7 else (0 if origin%64==0 else end>>8);alt_f=0x88|int(origin%64==0)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[2],r[3],r[A],r[F],r[16],r[17],r[SP])==(0xCB00,end,b,old_f,offset,flags,alt_a,alt_f,0x8000),(selector,k)
   assert r[18:24]==[initial[2],initial[3],min_x,max_y,max_x,min_y] and r[8:12]==initial[8:12] and m==expected;cases+=1
 report=dict(passed=True,cases=cases,all_selectors=True,all_input_flag_bytes_covered=True,real_clip_and_table_callees=True,independent_full_memory_and_register_oracle=True,exact_four_stack_scratch_bytes=True,byte_index_overflow_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewSetupVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
