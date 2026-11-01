"""Сброс и подготовка B, включая изменяемый CPL и пропускаемую настройку скольжения."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=[0xA5]*65536;m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);cases=0
 samples=[(v,(v*257)^0x5AA5,(v*127+1)&65535,(v*31)&65535) for v in range(256)]
 samples += [(v,0x1234,0x5678,step) for v in (0,1,255) for step in (0,1,0x7FFF,0x8000,0xA55A,0xFFFF)]
 # Проверка всех сочетаний трёх пропускаемых блоков и NOP/CPL разрешения канала.
 for value,sample,ornament,step in samples:
  for bits in range(32):
   volume=value^0xA5;env=value^0x5A;target=(value+19)&255;delay=(value*73+7)&255;branch=0x1D if value&1 else 0
   for n,a in enumerate((0xDEBF,0xDEEF,0xDF00)):m[a]=6 if bits&(1<<n) else 0x18
   m[0xDED6]=0x2F if bits&8 else 0;m[0xDEBC]=1 if bits&16 else 0x22
   for a,v in ((0xDEDB,value),(0xDEEB,volume),(0xDEFC,env),(0xDF03,target),(0xDF08,delay),(0xDF16,branch)):m[a]=v
   for a,v in ((0xDEE0,sample),(0xDEF6,ornament),(0xDF10,step)):m[a:a+2]=[v&255,v>>8]
   for a in (0xE0F9,0xE13D,0xE154,0xE17C,0xE19F,0xE1D7,0xE16C,0xE16D,0xE0EE,0xE1BB,0xE0F5,0xE0F6,0xE12C,0xE178,0xE179,0xE136,0xE1B3,0xE1CE,0xE1A8,0xE1A9,0xE1AF,0xE198,0xE199):m[a]=0xA5
   initial=get_registers({'HL':0x1357,'DE':0x0618,'BC':0x2468,'AF':0x9800|value,'IX':0x369C,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':0xDEB9},None,False);before=m.copy();s.registers[:]=initial
   for n in range(70):
    if s.registers[PC]==0xDF1E:break
    s.run()
   else:raise AssertionError('channel_b_reset_continuation')
   expected=before.copy();expected[0xE12C]=volume;hl=0;b=0xE1 if bits&16 else 0x24;c=0x98 if bits&16 else 0x68;f=0x44;a=volume
   if not bits&16:expected[0xE198:0xE19A]=[0,0]
   if bits&1:
    for x in (0xE0F9,0xE13D,0xE154,0xE17C,0xE19F,0xE1D7,0xE16C,0xE16D):expected[x]=0
    expected[0xE0EE]=0xFF if bits&8 else 0;expected[0xE1BB]=value;expected[0xE0F5:0xE0F7]=[sample&255,sample>>8];expected[0xE110]=0x10;hl=sample;b=0x29;f=0x7E if bits&8 else 0x44
   if bits&2:expected[0xE17C]=0;expected[0xE178:0xE17A]=[ornament&255,ornament>>8];expected[0xE136]=env;hl=ornament;b=0x0F;f=0x44;a=env
   if bits&4:
    expected[0xE1B3]=target;expected[0xE19F]=expected[0xE1CE]=delay;expected[0xE1A8:0xE1AA]=[step&255,step>>8];expected[0xE1AF]=branch;expected[0xE1D7]=0;hl=step;b=0x1C;f=0x44;a=0
   r=s.registers;assert m==expected,('memory',value,bits)
   assert r[0]==a and r[1]==f and r[2]==b and r[3]==c and r[6]*256+r[7]==hl,('registers',value,bits,r[:8],a,f,b,c,hl)
   assert all(r[i]==initial[i] for i in (4,5,8,9,10,11,SP,*range(16,24)))
   cases+=1
 report={'passed':True,'cases':cases,'all_gate_and_enable_and_reset_code_combinations':True,'all_parameter_low_bytes':True,'nop_and_cpl_channel_enable':True,'ld_memory_hl_and_ld_bc_reset_modes':True,
  'slide_branch_values':[0,29],'all_memory_compared':True,'control_gates_not_self_cleared':True,'stop_address':0xDF1E,'irq_executed':False,'later_synthesis_executed':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicChannelBResetVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
