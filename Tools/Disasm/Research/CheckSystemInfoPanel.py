"""Полная банковая информационная панель, проверка аргументов и последовательности настоящих печатателей."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import signature,classify_region
from CheckCoordinateDistance import reference as distance
from CheckCompactDecimal import digits


def main():
 station,map_source,banks=make_context();prefixes=[];cursor=0x2722
 for _ in range(16):end=map_source.index(10,cursor);prefixes.append(map_source[cursor:end]);cursor=end+1
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=wakeups=0;observed_counts=set();distance_codes=set();trait_codes=set()
 def name(first,second):return prefixes[second&15]+b'-'+digits((second&0xF0)|((first>>8)&15))+b'/'+digits(((first>>8)&0xF0)|((second>>8)&15))+b'-'+bytes([0x80+(second>>12),10])
 for fold in range(8):
  for profile in range(4):
   for variant in (0,1,255):
    for page in (0x10,0x18):
     current_first=0x4B38;current_second=0x4A00|(0x4B^0x38^0x4A^(7-fold));selected_first=0 if profile==2 else current_first;selected_second=0x4A00|((selected_first>>8)^(selected_first&255)^0x4A^fold)
     if profile==3:current_first,current_second=selected_first,selected_second
     current=(current_first,current_second,(variant+17)&255);selected=(selected_first,selected_second,variant)
     fuel=(0x00FF,0x0100,0xFFFF,0)[profile];fuel_value=(fuel>>8) if fuel>>8 else (fuel&255)//2
     memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);memory[0x6306]=page;sim=Simulator(memory);trace=PortTrace(sim);sim.set_tracer(trace)
     put(memory,0x7690,[19,0]);put(memory,0xF0FD+19*16,[0,0,16,24,fold&1,13]);put(memory,0x8500,bytes([0x80,255])*128);put(memory,0x8600,bytes(768));put(memory,0x4000,bytes([0x96])*6912)
     for address,key in ((0x983F,current),(0x9844,selected)):put(memory,address,key[0].to_bytes(2,'little')+key[1].to_bytes(2,'little')+bytes([key[2]]))
     put(memory,0x988E,fuel.to_bytes(2,'little'));put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;put(memory,0x9CA6,[0,0xB4]);put(memory,0xB400,[0x8F,0x76,1,1]);r[PC]=0x768F if page==0x10 else 0x7688;seen=[];wakes=0;previous_pc=None
     sel=signature(*selected);cur=signature(*current);observed_counts.add(sel['result']);trait_codes.update((sel['major'],cur['major']))
     # Построение ожидаемой последовательности непосредственных содержательных вызовов, вложенная печать не подменяется.
     x0=((selected_first&255)<<8)|(selected_second&255);y0=(selected_first&0xFF00)|(selected_second>>8);x1=((current_first&255)<<8)|(current_second&255);y1=(current_first&0xFF00)|(current_second>>8)
     dist=distance(map_source,x0,y0,x1,y1,0)[0];distance_codes.add(dist)
     expected=[('text',0xEA9B),('number',fuel_value,0,49,8),('distance',selected_first,selected_second,current_first,current_second)]
     expected += [('glyph',45,49,16)] if dist==255 else [('number',dist,0,49,16)]
     expected += [('name',selected_first,selected_second),('region',selected_first),('lf',0xF0B2,classify_region(selected_first),0,40),('text',0x630B),('label',selected_first,selected_second,variant,34,56),('describe',selected_first,selected_second,variant)]
     if sel['result']==0:expected += [('text',0xEB82)]
     else:
      expected += [('traits',sel['major'],sel['size'],sel['minor'],25,64)]
      expected += [('selected_label',i,(i%3)*32,96+(i//3)*8) for i in range(sel['result'])]
     expected += [('name',current_first,current_second),('region',current_first),('lf',0xF0B2,classify_region(current_first),0,128),('text',0x630B),('label',current_first,current_second,current[2],34,144),('current',)]
     if cur['result']:expected += [('traits',cur['major'],cur['size'],cur['minor'],25,152)]
     for step in range(300000):
      pc=r[PC]
      if pc==0x3FFF:break
      if pc==0xC089:assert memory[pc]==0x76;r[PC]+=1;wakes+=1;continue
      ret=memory[r[SP]]+256*memory[r[SP]+1];hl=r[H]*256+r[L];de=r[D]*256+r[E];bc=r[B]*256+r[C];px,py=memory[0x6320:0x6322]
      direct=previous_pc is not None and 0x768F<=previous_pc<0x7839 and memory[previous_pc]==0xCD
      if direct:
       if pc==0xBD08:seen.append(('text',hl))
       elif pc==0xBC01:seen.append(('number',bc,r[A],px,py))
       elif pc==0xAE8D:seen.append(('glyph',r[A],px,py))
       elif pc==0xE7BA:seen.append(('distance',de,bc,r[20]*256+r[21],r[18]*256+r[19]))
       elif pc==0xE6AB:seen.append(('name',hl,de))
       elif pc==0xE779:seen.append(('region',hl))
       elif pc==0xA37A:seen.append(('lf',hl,r[A],px,py))
       elif pc==0xC8C9:seen.append(('label',hl,de,r[A],px,py))
       elif pc==0xA46E:seen.append(('describe',hl,de,r[A]))
       elif pc==0xA3A1:seen.append(('traits',r[H],r[L],r[E],px,py))
       elif pc==0xC8C2:seen.append(('selected_label',r[A],px,py))
       elif pc==0xA464:seen.append(('current',))
      # Проверка сформированных имён до их настоящей печати, оба прохода используют один переиспользуемый буфер.
      if direct and pc==0xBD08 and hl==0x630B:
       key=selected if len([v for v in seen if v[0]=='name'])==1 else current;raw=name(*key[:2]);assert bytes(memory[0x630B:0x630B+len(raw)])==raw
      previous_pc=pc;sim.run()
     else:raise AssertionError(('instruction_limit',fold,profile,variant,page,hex(r[PC])))
     assert seen==expected,(fold,profile,variant,page,seen,expected)
     assert memory[0x9908]==dist and memory[0xBD26]==0 and memory[0x6306]==page and memory.o7ffd==page and wakes==1
     assert r[8:12]==initial[8:12] and r[SP]==0x8000
     if cur['result']:
      assert (r[H]*256+r[L],r[D],r[E],r[B]*256+r[C],r[A],r[F])==(0xA822,cur['region'],cur['minor'],(cur['result']<<8)|cur['flags'],0,0x45)
     else:assert (r[H],r[L],r[D],r[E],r[A],r[F])==(cur['major'],cur['size'],cur['region'],cur['minor'],0,cur['flags'])
     assert [v for port,v in trace.writes if port==0x7FFD][-1]==page;cases+=1;wakeups+=wakes
 # Проверка раннего выхода обёртки по отсутствующему указателю для всех F, без вызова рамки и смены банка.
 absent=0
 for flags in range(256):
  memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);memory[0x6306]=0x10;sim=Simulator(memory);trace=PortTrace(sim);sim.set_tracer(trace)
  put(memory,0x9CA6,[0,0xB4]);put(memory,0xB400,[1,1]);put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;r[F]=flags;sim.run(start=0x7688,stop=0x3FFF)
  assert r[H]*256+r[L]==0x1357 and r[D]*256+r[E]==0x768F and r[B]*256+r[C]==0x36C9 and (r[A],r[F])==(1,flags&1) and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and not trace.writes;absent+=1
 report=dict(passed=True,cases=cases,guarded_whole_panel_cases=cases//2,absent_guard_cases=absent,selected_counts=sorted(observed_counts),trait_major_codes=sorted(trait_codes),distance_codes=sorted(distance_codes),method='real_caption_text_name_distance_descriptors_and_variant_labels_with_semantic_call_argument_trace',all_selected_counts=True,actual_calls_executed=True,calls_stubbed=False,whole_bitmap_independent_oracle=False,explicit_halt_wakeups=wakeups,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SystemInfoPanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
