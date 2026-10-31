"""Реальные списки цен D3D и временные разделители против независимого текста и полного bitmap."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from Analyze import payload
from CheckRowHighlight import make_context
from CheckTextStream import reference
from CheckPreviewDescriptions import paint_positions
from PreviewPriceOracle import calculate


def after_cr(m,start,count):
 for _ in range(count):start=m.index(13,start)+1
 return start


def main():
 _,_,banks=make_context();raw=payload(6);template=bytearray(65536);template[0x4000:0x8000]=bytes(banks[5]);template[0x8000:0xC000]=bytes(banks[2]);template[0xC000:0xC000+len(raw)]=raw;template[0x4000:0x5B00]=bytes((i*73+(i>>8)*19+17)&255 for i in range(0x1B00))
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=glyphs=karen=0
 def execute(selector,owned,index,width,height,origin):
  nonlocal cases,glyphs,karen
  m=bytearray(template);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[A]=selector;r[H]=owned;r[L]=(selector*29+index)&255;r[16]=index;r[17]=(selector*11+index*3)&255;m[0xCE8C]=0xA7;m[0xBD73]=36;m[0xAEAB]=height;m[0xAEB3]=width;m[0xAEBB]=origin[0];m[0xAEBF]=0;m[0xAEC7]=origin[1];m[0xAECB]=0;m[0xBD26]=0;m[0x7FFE:0x8000]=bytes([255,63])
  oracle=calculate(m,selector,owned,index,0x36C9,0x247A);glyphs+=oracle['glyphs'];karen+=oracle['karen'];expected=oracle['registers'];screen=oracle['screen'];expected_bank=oracle['bank']
  s.run(start=0xE0C5,stop=0x3FFF);actual=(r[H]*256+r[L],r[D]*256+r[E],r[2]*256+r[3],r[A],r[F],r[16],r[17],m[0x6320],m[0x6321])
  assert actual==expected,(selector,owned,index,width,height,origin,actual,expected)
  assert m[0x4000:0x5B00]==screen and m[0xC000:]==expected_bank and r[18:24]==initial[18:24] and r[8:12]==initial[8:12] and r[SP]==0x8000;cases+=1
 for selector in (0,1,2,255):
  for owned in (0,1,255):
   for index in range(4 if selector==1 else (7 if owned else 6)):
    for width,height,origin in ((128,96,(4,6)),(64,32,(0,0)),(224,160,(6,3)),(32,13,(0,0)),(80,24,(0,0)),(160,80,(248,184))):execute(selector,owned,index,width,height,origin)
 for selector in range(256):
  owned=selector&1;index=selector%(4 if selector==1 else (7 if owned else 6));execute(selector,owned,index,168,80,(5,3))
 report=dict(passed=True,cases=cases,independent_glyphs=glyphs,karen_owned_cases=karen,all_selectors=True,zero_and_two_nonzero_owned_flags=True,real_header_body_and_glyphs=True,whole_bitmap_and_attributes_compared=True,entire_bank_compared=True,temporary_record_end_restored=True,byte_cursor_row_count_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPricesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
