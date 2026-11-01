"""Три отложенных переключателя A, полное сравнение памяти и сохранённых регистров."""
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
   for a,v in zip((0xDE97,0xDE9F,0xDEA6,0xDEB1),params):m[a]=v
   for n,a in enumerate((0xDE90,0xDEA3,0xDEAE)):m[a]=6 if bits&(1<<n) else 0x18
   for a in (0xE0E9,0xE0D7,0xE0E5,0xDFFA,0xE07C):m[a]=0xA5
   initial=get_registers({'HL':0x1357,'DE':0x0618,'BC':0x2468,'AF':0x9800|value,'IX':0x369C,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':0xDE90},None,False)
   before=m.copy();s.registers[:]=initial
   for n in range(30):
    if s.registers[PC]==0xDEB9:break
    s.run()
   else:raise AssertionError('channel_a_staging_continuation')
   expected=before.copy();a=0x98;b=0x24
   if bits&1:
    expected[0xDE90]=0x18;expected[0xE0E9]=expected[0xE0D7]=params[0];expected[0xE0E5]=params[1];a=params[1];b=0x11
   if bits&2:expected[0xDFFA]=params[2];expected[0xDEA3]=0x18;a=0x18;b=9
   if bits&4:expected[0xE07C]=params[3];expected[0xDEAE]=0x18;a=0x18;b=9
   r=s.registers;assert m==expected and r[0]==a and r[1]==value and r[2]==b and r[3]==0x68
   assert all(r[i]==initial[i] for i in (4,5,6,7,8,9,10,11,SP,*range(16,24)))
   cases+=1
 report={'passed':True,'cases':cases,'all_gate_combinations':True,'all_parameter_bytes':True,'all_input_flag_bytes':True,
  'all_memory_compared':True,'stop_address':0xDEB9,'sample_and_ornament_rendering_executed':False,'irq_executed':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicChannelAStagingVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
