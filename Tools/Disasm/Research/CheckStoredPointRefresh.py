"""Общие хвосты рисунка списков и нормализации B с настоящей картой и необязательной информационной панелью."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put,pointer_image


def main():
 _,_,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=wakeups=0;baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912))
 for entry in (0x7B9B,0x7C4A):
  for count in range(11):
   for info in (False,True):
    for page in (0x10,0x18):
     m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);m[0x6306]=page;s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
     put(m,0x6DA9,[11,0]);put(m,0xF1AD,[1,1,12,12,0,0]);put(m,0x7690,[19,0]);put(m,0xF0FD+19*16,[16,0,16,24,0,13]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,[0,0]);put(m,0x9A8D,[255,255]);put(m,0x9A90,[0x58,0x9A]);m[0x6548]=1;m[0x9B16]=0
     put(m,0x6300,[0,0,0,0,80,72]);put(m,0x983F,bytes([0x70])*4+bytes([0]));put(m,0x9844,bytes([0x70])*4+bytes([0]));put(m,0x988E,[0,0]);m[0x99A3]=0x80;m[0x99B4]=1
     # Полный A задаёт читаемый положительный байт при обратном поиске пустого B, новый сторож не добавляется.
     put(m,0x990A,b''.join(bytes([1+i,0,2+i,3+i,4+i]) for i in range(10))+bytes([0x80]));rows=[bytes([i+1,0,10+i,20+i,30+i]) if i<count else bytes([255,0xA7,0xB8,0xC9,0xDA]) for i in range(10)];put(m,0x993D,b''.join(rows)+bytes([0x80]));put(m,0x6309,(0x993D+45).to_bytes(2,'little'));put(m,0x9970,bytes([0xA2])+bytes([0xB7])*10)
     put(m,0x9CA6,[0,0xB4]);put(m,0xB400,(bytes([0x8F,0x76]) if info else b'')+bytes([1,1]));put(m,0x4000,baseline);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;r[PC]=entry;wakes=0
     for _ in range(400000):
      if r[PC]==0x3FFF:break
      halt=(r[PC]==0xC14B and m.o7ffd&7==1) or (r[PC]==0xC089 and m.o7ffd&7==0)
      if halt:assert m[r[PC]]==0x76;r[PC]+=1;wakes+=1
      else:s.run()
     else:raise AssertionError(('instruction_limit',hex(entry),count,info,page,hex(r[PC])))
     assert m[0x6306]==m.o7ffd==0x10 and r[SP]==0x8000 and r[10:12]==initial[10:12] and r[A]==0x10
     assert m.banks[7][:6912]==list(baseline) and m[0x6D75]==m[0x6D90]==0 and m[0x6D7B]==1 and m[0xBD26]==0
     assert bytes(m[0x993D:0x9970])==b''.join(rows)+bytes([0x80])
     if entry==0x7C4A:
      assert m[0x6309]+256*m[0x630A]==0x993D+5*max(count-1,0)
      assert m[0x9970]==0xA0|count and m[0x9971:0x9971+count]==list(range(0,5*count,5)) and m[0x9971+count:0x997B]==[0xB7]*(10-count)
     else:assert m[0x6309:0x630B]==[0x6A,0x99] and m[0x9970:0x997B]==[0xA2]+[0xB7]*10
     assert wakes==2+int(info);cases+=1;wakeups+=wakes
 report=dict(passed=True,cases=cases,secondary_counts=list(range(11)),original_order_and_map_scene_executed=True,optional_information_panel_executed=True,initial_pages=[16,24],final_page=16,screen_snapshot_compared=True,whole_bitmap_independent_oracle=False,explicit_halt_wakeups=wakeups,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StoredPointRefreshVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
