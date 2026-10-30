"""Перепаковка координат и исходное центрирование видимой области карты."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def adc16_flags(left,right):
 total=left+right;result=total&65535
 return ((result>>8)&0xA8)|(0x40 if result==0 else 0)|(0x10 if (left^right^result)&4096 else 0)|(4 if (~(left^right)&(left^result)&32768) else 0)|int(total>65535)


def reference(x,y,width,height):
 def offset(size):return 0xFF00|(-(size>>1)&255)
 raw_x=(x+offset(width))&65535;raw_y=(y+offset(height))&65535
 return (0 if raw_x&32768 else raw_x),(0 if raw_y&32768 else raw_y),adc16_flags(y,offset(height))


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 fixtures=[(value,65535-value,32,24) for value in range(65536)]
 fixtures += [(value,value,size,255-size) for size in range(256) for value in sorted({0,1,127,128,255,256,32767,32768,65535,max(0,(size>>1)-1),size>>1,(size>>1)+1})]
 # Проверка всех координатных слов и байтов размеров, включая нулевой полуразмер.
 for x,y,width,height in fixtures:
  first=((y>>8)<<8)|(x>>8);second=((y&255)<<8)|(x&255)
  memory[0x6304:0x6306]=bytes([width,height]);memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers
  r[D],r[E]=first>>8,first&255;r[H],r[L]=second>>8,second&255
  expected_x,expected_y,flags=reference(x,y,width,height)
  sim.run(start=0xC333,stop=0x3FFF)
  out_de=((expected_y&255)<<8)|(expected_x&255);out_hl=((expected_y>>8)<<8)|(expected_x>>8)
  assert bytes(memory[0x6300:0x6304])==out_de.to_bytes(2,'little')+out_hl.to_bytes(2,'little')
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(out_hl,out_de,255,(-(height>>1))&255,expected_y&255,flags,0x8000)
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];cases+=1
 report=dict(passed=True,cases=cases,method='original_view_center_all_coordinate_words_and_all_dimension_bytes',
  zero_half_dimension_subtracts_256=True,clamp_uses_wrapped_sign_not_unsigned_borrow=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapViewCenterVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
