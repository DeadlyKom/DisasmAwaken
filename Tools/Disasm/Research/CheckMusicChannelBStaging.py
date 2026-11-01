"""Три отложенных переключателя B, полное сравнение памяти и сохранённых регистров."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=[0xA5]*65536;m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);cases=0
 # Проверка всех комбинаций трёх отложенных команд и всех байтов их параметров.
 for value in range(256):
  for bits in range(8):
   params=(value,value^0xA5,(value*73+19)&255,(value*31+7)&255)
   for a,v in zip((0xDF25,0xDF2D,0xDF34,0xDF3F),params):m[a]=v
   for n,a in enumerate((0xDF1E,0xDF31,0xDF3C)):m[a]=6 if bits&(1<<n) else 0x18
   for a in (0xE1E9,0xE1D7,0xE1E5,0xE0F9,0xE17C):m[a]=0xA5
   initial=get_registers({'HL':0x1357,'DE':0x0618,'BC':0x2468,'AF':0x9800|value,'IX':0x369C,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':0xDF1E},None,False)
   before=m.copy();s.registers[:]=initial
   for n in range(30):
    if s.registers[PC]==0xDF47:break
    s.run()
   else:raise AssertionError('channel_b_staging_continuation')
   expected=before.copy();a=0x98;b=0x24
   if bits&1:
    expected[0xDF1E]=0x18;expected[0xE1E9]=expected[0xE1D7]=params[0];expected[0xE1E5]=params[1];a=params[1];b=0x11
   if bits&2:expected[0xE0F9]=params[2];expected[0xDF31]=0x18;a=0x18;b=9
   if bits&4:expected[0xE17C]=params[3];expected[0xDF3C]=0x18;a=0x18;b=9
   r=s.registers;assert m==expected and r[0]==a and r[1]==value and r[2]==b and r[3]==0x68
   assert all(r[i]==initial[i] for i in (4,5,6,7,8,9,10,11,SP,*range(16,24)))
   cases+=1
 report={'passed':True,'cases':cases,'all_gate_combinations':True,'all_parameter_bytes':True,'all_input_flag_bytes':True,
  'all_memory_compared':True,'stop_address':0xDF47,'sample_and_ornament_rendering_executed':False,'irq_executed':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicChannelBStagingVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
