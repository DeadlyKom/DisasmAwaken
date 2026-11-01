"""Три входа завершения C, сохранение альтернативного AF и договор счётчика."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory, xor_flags


def main(profiles=None,stem="MusicChannelCFinish"):
 if profiles is None:profiles=((0xE2CB,0xE2EB,0xE2CC,0xE29D,0xE2D5,0xE1EE,0xE2E3,0xE2E7,0xDC0A),)
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);cases=0
 # Проверка основного входа перезагрузки, сохранения текущего счётчика и одного восстановления AF.
 for finish,stop,reload,slide_counter,gate_counter,state_address,off_address,on_address,amplitude in profiles:
  for entry in (finish,finish+2,finish+5):
   for counter in range(256):
    for state in range(256):
     for carry in (0,1):
      level=state^counter;delay=(counter*73+state)&255;current=(counter+state*31)&255;off=state^0xA5;on=counter^0x5A
      m.recording=False;m[reload]=delay;m[slide_counter]=0xA5;m[gate_counter]=counter;m[state_address]=state;m[off_address]=off;m[on_address]=on;m[amplitude]=0xA5
      initial=get_registers({'HL':0x1357,'DE':0x2468,'BC':0x369C,'AF':current*256+state,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':level*256+carry,'SP':0xDD00,'PC':entry},None,False)
      s.registers[:]=initial;m.writes=[];m.recording=True
      for n in range(22):
       if s.registers[PC]==stop:break
       s.run()
      else:raise AssertionError('finish_c_boundary')
      m.recording=False;expected=[]
      if entry!=finish+5:expected.append((slide_counter,delay if entry==finish else current))
      expected.append((amplitude,level));a=(counter-1)&255;f=carry|(a&0xA8)|(0x40 if not a else 0)|(4 if counter==128 else 0)|(16 if counter&15==0 else 0)|2;hl=0x1357
      if a<128:
       if a==0:
        new_state=state^255;expected.append((state_address,new_state));hl=state_address;f=xor_flags(new_state);a=on if new_state==0 else off
       expected.append((gate_counter,a))
      r=s.registers;assert m.writes==expected and r[0]==a and r[1]==f and r[6]*256+r[7]==hl
      assert r[16]==(delay if entry==finish else current) and r[17]==state
      assert all(r[i]==initial[i] for i in (2,3,4,5,8,9,10,11,SP,*range(18,24)))
      cases+=1
 report={'passed':True,'cases':cases,'entries':[f+delta for f,*rest in profiles for delta in (0,2,5)],'all_gate_counter_and_state_bytes':True,'both_saved_carry_values':True,
  'alternate_af_exactly_checked':True,'every_memory_write_observed':True,'stop_addresses':[p[1] for p in profiles],'ay_output_executed':False,'irq_executed':False,'assembly_executed':False}
 (ROOT/('Tools/Disasm/Reports/'+stem+'Verification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
