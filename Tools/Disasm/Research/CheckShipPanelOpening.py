"""Полное открытие корабельной группы с исходным сбросом, банковыми OUT и списком рисования."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
GROUP=((0x7A15,30),(0x7A82,29),(0x7A55,28),(0x67E0,25),(0x6945,27),(0x6877,26))


def main():
 _,_,base=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 for page in (0x10,0x18):
  for kind in range(4):
   for disabled in (False,True):
    for height in range(256):
     m=SliceableMemory(banks=[b.copy() for b in base],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial
     put(m,0x5F00,[0x21,26,0,0xC9]);put(m,0x5F08,[0x21,63,0,0xC9]);put(m,0x9CA6,[0,0xB4]);m[0x9A82]=0xA7;m[0x6306]=page;m[0xB3FF]=0xA5;m[0xB501]=0x5A;m.banks[4][0x2146]=0xD3
     original={};keys={0x5F00:26,0x5F08:63}
     # Подготовка всех полей записей и исходных изменяемых индексов, в том числе отключённых рисователей.
     for j,(pointer,index) in enumerate(GROUP):
      m[pointer]=0xC9 if disabled else 0x21;put(m,pointer+1,index.to_bytes(2,'little'));keys[pointer]=index
      record=bytes([0xA0,0xB0,1,1,height^index,0,0,0,(height+index)&255,(height*3+index)&255,(height*5+index)&255,height if j==len(GROUP)-1 else (height+j+1)&255,0,0,0,0]);put(m,0xF0FD+16*index,record);original[index]=record
     entries=[] if kind==0 else ([p for p,_ in reversed(GROUP)]+[0x5F08] if kind==1 else ([0x5F00,0x5F08] if kind==2 else [GROUP[0][0],GROUP[0][0],0x5F08]))
     raw=b''.join(p.to_bytes(2,'little') for p in entries)+bytes([1,1]);put(m,0xB400,raw+bytes(256-len(raw)));expected=list(entries)
     # Независимая модель списка выбирает первое совпадение ключа, сохраняя существующий адрес-алиас.
     for pointer,index in GROUP:
      found=next((i for i,p in enumerate(expected) if keys[p]==index),None);selected=expected.pop(found) if found is not None else pointer;expected.append(selected)
     put(m,0x7FFE,[255,63]);screen=bytes(m[0x4000:0x6000]);s.run(start=0x7DF1,stop=0x3FFF);r=s.registers
     expected_raw=b''.join(p.to_bytes(2,'little') for p in expected)+bytes([1,1]);assert bytes(m[0xB400:0xB400+len(expected_raw)])==expected_raw
     # Независимый результат записей учитывает предварительные SET/RES и последующее восстановление четырёх границ.
     for pointer,index in GROUP:
      record=bytearray(original[index]);record[:4]=record[8:12]
      if index==29:record[4]|=1
      if index==28:record[4]&=254
      assert bytes(m[0xF0FD+16*index:0xF10D+16*index])==record and m[pointer]==(0xC9 if disabled else 0x21)
     assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(expected[-1],26,height,0xA4,0x8000)
     assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
     assert screen==bytes(m[0x4000:0x6000]) and m[0x9A82]==0 and m[0xB3FF]==0xA5 and m[0xB501]==0x5A
     assert m[0x6906]==0 and m[0x68EB]==1 and m[0x79DD]==0 and m[0x67D7]==255 and m.banks[4][0x2146]==0
     assert trace.writes==[(0x7FFD,page|4),(0x7FFD,page)] and m.o7ffd==page;cases+=1
 report=dict(passed=True,cases=cases,real_reset_and_banking=True,all_saved_height_and_frame_flag_bytes=True,all_physical_record_fields_compared=True,empty_reversed_aliased_and_duplicate_lists=True,disabled_opcodes_retained=True,no_immediate_screen_drawing=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipPanelOpeningVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
