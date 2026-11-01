"""Прямой вход установки длительностей B, без предварительного чтения первого байта."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);cases=0
 # Проверка всех пар длительностей и сохранения всех байтов F.
 for first in range(256):
  for second in range(256):
   m.recording=False;m[0x7000]=second;m[0xBFFE:0xC000]=[255,63];initial=get_registers({'HL':0x1357,'DE':0x7000,'BC':0x2468,'AF':first*256+second,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':0xDDF2},None,False);s.registers[:]=initial;m.writes=[];m.recording=True
   for n in range(12):
    if s.registers[PC]==0x3FFF:break
    s.run()
   else:raise AssertionError('gate_setter_b_return')
   m.recording=False;r=s.registers;assert sorted(m.writes)==sorted([(0xDF25,first),(0xDF2D,second),(0xDF1E,6)])
   assert r[0]==6 and r[1]==second and r[4]*256+r[5]==0x7001 and r[SP]==0xC000
   assert all(r[i]==initial[i] for i in (2,3,6,7,8,9,10,11,*range(16,24)));cases+=1
 report={'passed':True,'cases':cases,'all_duration_pairs':True,'all_input_flag_bytes':True,'entry':0xDDF2,'every_memory_write_observed':True,'irq_executed':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicGateSetterBVerification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
