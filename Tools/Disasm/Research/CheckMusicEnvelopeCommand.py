"""Проверка косвенного обработчика команды скольжения огибающей по DB8C."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=[0]*65536;m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);cases=0
 # Проверка указателя из физических таблиц команд всех трёх каналов.
 tables=(0xDDCE,0xDDEE,0xDE0E)
 assert all(m[a]+256*m[a+1]==0xDB8C for a in tables)
 for delay in range(256):
  for step in (0,1,0x7FFF,0x8000,0xA55A,0xFFFF):
   for pointer in (0x7000,0x70FE):
    m[pointer:pointer+3]=[delay,step&255,step>>8];m[0xBFFE:0xC000]=[255,63]
    initial=get_registers({'HL':0x1357,'DE':pointer,'BC':0x2468,'AF':0x9800|delay,'IX':0x369C,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':0xDB8C},None,False)
    before=m.copy();s.registers[:]=initial
    for n in range(20):
     if s.registers[PC]==0x3FFF:break
     s.run()
    else:raise AssertionError('envelope_command_did_not_return')
    expected=before.copy();expected[0xDF74]=delay;expected[0xDF6E:0xDF70]=[step&255,step>>8];expected[0xDF6B]=6
    assert m==expected and s.registers[SP]==0xC000
    r=s.registers;assert r[0]==6 and r[1]==delay and r[6]*256+r[7]==step and r[4]*256+r[5]==pointer+3
    assert all(r[i]==initial[i] for i in (2,3,8,9,10,11,*range(16,24)))
    cases+=1
 report={'passed':True,'cases':cases,'entry':0xDB8C,'physical_dispatch_table_words':list(tables),'all_delay_and_flag_bytes':True,
  'page_crossing_stream':True,'all_memory_compared':True,'irq_executed':False,'full_effect_playback_proved':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicEnvelopeCommandVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
