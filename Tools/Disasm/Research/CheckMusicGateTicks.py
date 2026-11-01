"""Независимая модель трёх счётчиков чередования и записи амплитуд AY."""
from pathlib import Path
import collections, json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP


class Memory(list):
 def __setitem__(self,key,value):
  if getattr(self,'recording',False):assert isinstance(key,int);self.writes.append((key,value))
  super().__setitem__(key,value)


def xor_flags(v):return (v&0xA8)|(0x40 if not v else 0)|(4 if v.bit_count()%2==0 else 0)


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);counts=collections.Counter()
 profiles=(('A',0xE0D3,0xE0ED,0xDC08,0xE0D7,0xDFEF,0xE0E5,0xE0E9),('B',0xE1D3,0xE1ED,0xDC09,0xE1D7,0xE0EE,0xE1E5,0xE1E9),('C',0xE2D1,0xE2EB,0xDC0A,0xE2D5,0xE1EE,0xE2E3,0xE2E7))
 for name,start,stop,amplitude,counter,state,disabled,enabled in profiles:
  # Проверка всех байтов счётчика и состояния, Carry проверяется независимо.
  for old in range(256):
   for current in range(256):
    for carry in (0,1):
     off=(current*73+old)&255;on=(old*31+current+7)&255;level=(current^old)&255
     m.recording=False;m[counter]=old;m[state]=current;m[disabled]=off;m[enabled]=on;m[amplitude]=0xA5
     initial=get_registers({'HL':0x1357,'DE':0x2468,'BC':0x369C,'AF':level*256+carry,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':start},None,False)
     s.registers[:]=initial;m.writes=[];m.recording=True
     for n in range(18):
      if s.registers[PC]==stop:break
      s.run()
     else:raise AssertionError(('gate_boundary',name,old,current))
     m.recording=False;v=(old-1)&255;f=carry|(v&0xA8)|(0x40 if v==0 else 0)|(4 if old==0x80 else 0)|(0x10 if old&15==0 else 0)|2
     expected=[(amplitude,level)];hl=0x1357;next_state=current;next_counter=old
     if v<128:
      if v==0:
       next_state=current^255;f=xor_flags(next_state);hl=state;expected.append((state,next_state));v=on if next_state==0 else off
      next_counter=v;expected.append((counter,v))
     r=s.registers;assert m.writes==expected,(name,old,current,m.writes,expected)
     assert m[counter]==next_counter and m[state]==next_state and m[amplitude]==level
     assert r[0]==v and r[1]==f and r[6]*256+r[7]==hl,(name,old,current,r[:8],v,f,hl)
     assert all(r[i]==initial[i] for i in (2,3,4,5,8,9,10,11,SP,*range(16,24)))
     counts[name]+=1
 report={'passed':True,'cases_by_channel':dict(counts),'all_counter_and_state_bytes':True,'both_input_carry_values':True,'every_memory_write_observed':True,
  'negative_dec_leaves_counter_unchanged':True,'counter1_toggles_full_state_byte':True,'no_bit_flags_assumed':True,'ports_executed':False,'irq_executed':False,'full_synthesis_proved':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicGateTicksVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
