"""Полная панель моделей с реальными рамкой, характеристикой ключа и банковым текстом D3D."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put,PortTrace
from CheckWorldSignature import signature,logical_flags
from PreviewPriceOracle import calculate
from Analyze import payload


def main():
 _,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);keys={}
 # Подбор входных ключей выполняется независимой формулой, исходный DescribeCurrentKey в модели не заменяется.
 for variant in range(8):
  for low in range(256):
   value=signature(0x4B38,0x4A00|low,variant);keys.setdefault(value['size'],(0x4B38,0x4A00|low,variant))
  if len(keys)==16:break
 assert set(keys)==set(range(1,17));initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=market=owned_cases=wakes=0
 for owned in (0,1,255):
  for level in (range(1,17) if owned==0 else range(1,8)):
   for selector in (0,1,2,255):
    for page in (0x10,0x18):
     for x,y,width,height in ((1,2,24,12),(2,1,16,5)):
      for flags in (0,1):
       m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[PC]=0x67E0;m[0x6306]=page;put(m,0x7FFE,[255,63]);put(m,0x67E1,[25,0]);record=0xF0FD+16*25;text_index=m[record+5];put(m,record,[x,y,width,height,flags,text_index]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));m[0x67D2]=0xA7;m[0x67D7]=0x6B;m[0x6906]=selector;m[0x79DD]=owned;m[0x9849]=(level-1)%7;m[0x984A]=(level-1)%4
       first,second,variant=keys[level];put(m,0x983F,first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([variant]))
       if owned:index=m[0x9849] if selector==0 else m[0x984A]
       else:index=m[0x94BC+2*(level-1)+int(selector!=0)]
       oracle=None;descriptor_calls=0;local_wakes=0
       for _ in range(240000):
        pc=r[PC]
        if pc==0x3FFF:break
        if pc==0xA464:descriptor_calls+=1
        if pc==0xE0C5:
         assert m.o7ffd&7==4 and r[A]==selector and r[H]==owned and r[16]==index and m[0x67D7]==255 and m[0xBD73]==36 and m[0xBD26]==0
         oracle=calculate(bytearray(m[0:65536]),selector,owned,index,r[2]*256+r[3],r[D]*256+r[E])
        if pc==0xC089 and m.o7ffd&7==0:assert m[pc]==0x76;r[PC]+=1;local_wakes+=1
        else:s.run()
       else:raise AssertionError(('instruction_limit',owned,level,selector,page,hex(r[PC])))
       assert oracle is not None;hl,de,bc,_,_,count,count_flags,cx,cy=oracle['registers'];expected_page=(page&0xF8)|0x10
       assert (r[H]*256+r[L],r[D]*256+r[E],r[2]*256+r[3],r[A],r[F],r[16],r[17],m[0x6320],m[0x6321])==(hl,de,bc,count,count_flags,expected_page,logical_flags(expected_page),cx,cy),(owned,level,selector,page)
       assert bytes(m[0x4000:0x5B00])==oracle['screen'] and bytes(m.banks[4])==oracle['bank'] and m[0x67D2]==count and m[0x67D7]==255 and m[0x6306]==expected_page and m.o7ffd==expected_page
       expected_ports=[] if owned else [(0x7FFD,(page&0xF8)|0x11),(0x7FFD,(page&0xF8)|0x10)];expected_ports += [(0x7FFD,(page&0xF8)|0x14),(0x7FFD,expected_page)]
       assert trace.writes==expected_ports and descriptor_calls==int(not owned) and local_wakes==1 and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
       cases+=1;market+=not owned;owned_cases+=bool(owned);wakes+=local_wakes
 # Проверка временного RET до первого чтения индекса и геометрии.
 for flags in range(256):
  m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);m[0x67E0]=0xC9;put(m,0x7FFE,[255,63]);before=[bytes(b) for b in m.banks];s=Simulator(m);s.registers[:]=initial;r=s.registers;r[F]=flags;s.run(start=0x67E0,stop=0x3FFF)
  assert [bytes(b) for b in m.banks]==before and r[A]==initial[A] and r[F]==flags and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
 report=dict(passed=True,cases=cases,market_cases=market,owned_cases=owned_cases,all_16_system_levels=True,zero_exact_one_and_other_selectors=True,real_caption_descriptor_banking_and_prices=True,independent_price_body_bitmap_and_bank_oracle=True,caption_uses_separate_proved_contract=True,hover_row_count_and_selection_checked=True,disabled_entry_cases=256,explicit_halt_wakeups=wakes,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ModelListPanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
