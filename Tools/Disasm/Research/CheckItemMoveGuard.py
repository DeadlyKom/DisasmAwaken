"""Проверка BE27, точный указатель DrawHandler и последующий поиск другого ключа, индекса."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context
from CheckMoveDrawItem import decrement_flags


def main():
 _,_,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:]=bytes(banks[0]);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x5F00,'DE':0,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=absent=appended=different_key=beyond_copy=0
 # Проверка отсутствия указателя, согласованных записей и двух видов несогласованности указателя с индексом.
 for length in (0,1,2,8,46,64,65,128,256):
  for key in (0,45):
   positions=sorted({0,length//2,length-1}) if length else [0]
   for position in positions:
    for mode in range(4):
     if length==0 and mode or mode==3 and (length<2 or position==0):continue
     pointers=[0x5000+8*i for i in range(length)];target=0x5E00 if mode==0 else pointers[position];keys=[i+128 for i in range(length)]
     if mode==1:keys[position]=key
     elif mode in (0,3) and length:keys[0]=key
     for pattern in (0,1,0x5C,0x5D,0xFF):
      for pointer,index in zip(pointers,keys):memory[pointer:pointer+6]=bytes([0xC9 if pattern&1 else 0x21,index&255,index>>8,0xC3,0x58,0x9A])
      memory[0x5F00:0x5F06]=bytes([0x21,key,0,0xC3,0x58,0x9A]);record=0xF0FD+16*key
      original_record=bytearray((pattern+17*i)&255 for i in range(16));original_record[12:14]=target.to_bytes(2,'little');memory[record:record+16]=original_record
      buffer=bytearray((i*73+pattern*19)&255 for i in range(4096));data=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes([0xA5,1]);buffer[:len(data)]=data;expected=bytearray(buffer)
      memory[0x8000:0x9000]=buffer;memory[0x9CA6:0x9CA8]=bytes([0,0x80])
      selected=0x5F00;found=keys.index(key) if key in keys else -1
      if mode==0:
       if not length:carry=0
       else:
        last=pointers[-1];carry=int((last&255)<(target&255)) if last>>8==target>>8 else int(last>>8<target>>8)
       expected_a,expected_f=1,carry;absent+=1
      elif found<0:
       offset=2*length;expected[offset:offset+4]=selected.to_bytes(2,'little')+bytes([1,1]);expected_a,expected_f=1,0;appended+=1
      else:
       selected=pointers[found];offset=2*found;expected[offset:offset+128]=expected[offset+2:offset+130];cursor=offset;count=0
       while expected[cursor+1]!=1:cursor+=2;count+=1
       expected[cursor:cursor+4]=selected.to_bytes(2,'little')+bytes([1,1]);expected_a=count&255;expected_f=decrement_flags((count+1)&255)
       different_key+=mode==3;beyond_copy+=length-found-1>=64
      memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[D],r[E]=key>>8,key&255;r[F]=pattern
      sim.run(start=0xBE27,stop=0x3FFF)
      assert memory[0x8000:0x9000]==expected,(length,position,mode,pattern)
      assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(selected,key,expected_a,expected_f,0x8000),(length,position,mode,pattern,list(r))
      assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and memory[record:record+16]==original_record;cases+=1
 report=dict(passed=True,cases=cases,absent_pointer_cases=absent,present_pointer_missing_index_appends=appended,
  pointer_guard_and_index_move_select_different_handlers=different_key,beyond_fixed_shift_cases=beyond_copy,
  full_4096_byte_tail_checked=True,disabled_handlers_tested=True,record_and_preserved_registers_checked=True,
  method='original_BE27_presence_guard_then_real_BE38_against_full_physical_shift_and_index_model',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ItemMoveGuardVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
