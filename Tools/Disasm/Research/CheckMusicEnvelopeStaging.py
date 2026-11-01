"""Независимая проверка подготовки огибающей до границы AdvancePatternA."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP


def parity(v):return int(v.bit_count()%2==0)


def main():
 source=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=[0xA5]*65536;m[0xDB00:0xDB00+len(source)]=source;s=Simulator(m)
 initial=get_registers({'HL':0x1357,'DE':0x0618,'BC':0x2468,'AF':0x9876,'IX':0x369C,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE},None,False)
 steps=(0,1,0x7FFF,0x8000,0xA55A,0xFFFF);counts={'prepare':0,'commit':0};write_set=set()
 # Проверка всех форм и задержек с включённым и выключенным отложенным шагом.
 for shape in range(256):
  for gate in (0x18,0x06):
   for step in steps:
    delay=(shape*73+step)&255;noise=shape^0xA5;base=step^0x5AA5;tempo=(shape*31+step)&255;m[0xDF62]=tempo
    m[0xDF48]=shape;m[0xDF50:0xDF52]=[base&255,base>>8];m[0xDF67]=noise;m[0xDF6B]=gate;m[0xDF6E:0xDF70]=[step&255,step>>8];m[0xDF74]=delay
    for a in (0xDC0D,0xDC06,0xE37D,0xE2EE,0xE2EF,0xE2F1,0xE2F2,0xE2FA,0xE302,0xE303,0xE309):m[a]=0xA5
    before=m.copy();s.registers[:]=initial;s.registers[PC]=0xDF47
    for n in range(40):
     if s.registers[PC]==0xDF7F:break
     s.run()
    else:raise AssertionError(('prepare_did_not_reach_continuation',shape,gate))
    expected=before.copy();expected[0xDC0D]=shape;expected[0xDC06]=noise;expected[0xE37D]=tempo
    f=(shape&0xA8)|(0x40 if shape==0 else 0)|(parity(shape)<<2);hl=0x1357
    if shape:
     expected[0xE2F1:0xE2F3]=[base&255,base>>8];expected[0xDF48]=0;expected[0xE2EE:0xE2F0]=[0,0];expected[0xE2FA]=0;f=0x44;hl=0
    af=(noise<<8)|f;bc=0x2468
    if gate==6:
     expected[0xE302:0xE304]=[step&255,step>>8];expected[0xE2FA]=expected[0xE309]=delay;expected[0xDF6B]=0x18;hl=step;bc=0x1268;af=0x1800|f
    assert m==expected,('prepare_memory',shape,gate,step)
    r=s.registers;assert r[0]*256+r[1]==af and r[6]*256+r[7]==hl and r[2]*256+r[3]==bc
    assert [r[i] for i in (4,5,8,9,10,11,SP,*range(16,24))]==[initial[i] for i in (4,5,8,9,10,11,SP,*range(16,24))]
    write_set.update(a for a,(x,y) in enumerate(zip(before,m)) if x!=y);counts['prepare']+=1
 # Проверка блока фиксации, все байты задержки и E сохраняются как физические байты.
 for delay in range(256):
  for step in steps:
   for e in (0,6,0x18,0xFF):
    m[0xDF74]=delay;before=m.copy();s.registers[:]=initial;s.registers[PC]=0xDF70;s.registers[6]=step>>8;s.registers[7]=step&255;s.registers[5]=e
    entry=s.registers.copy()
    for n in range(12):
     if s.registers[PC]==0xDF7F:break
     s.run()
    else:raise AssertionError('commit_did_not_reach_continuation')
    expected=before.copy();expected[0xE302:0xE304]=[step&255,step>>8];expected[0xE2FA]=expected[0xE309]=delay;expected[0xDF6B]=e
    assert m==expected and s.registers[0]==e
    assert all(s.registers[i]==entry[i] for i in (1,2,3,4,5,6,7,8,9,10,11,SP,*range(16,24)))
    counts['commit']+=1
 report={'passed':True,'cases':counts,'all_shape_bytes':True,'all_delay_bytes':True,'all_tempo_bytes':True,'step_boundary_words':list(steps),'all_memory_compared':True,
  'observed_changed_addresses':sorted(write_set),'returning_call_not_assumed':True,'stop_address':0xDF7F,'pattern_advance_executed':False,
  'irq_executed':False,'native_audio_verified':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicEnvelopeStagingVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
