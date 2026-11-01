"""Две отложенные команды позиций, проверка обратного порядка и полного SP."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from VerifySources import structure_symbols


def main():
 layout=structure_symbols();assert layout['FMUSICDEFERREDPAIRFRAME']==6 and [layout['FMUSICDEFERREDPAIRFRAME.'+f] for f in ('LATESTHANDLER','EARLIERHANDLER','CALLERRETURN')]==[0,2,4]
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);counts=collections.Counter()
 profiles=(('A',0xE439,0xE647,0xE652,0xDEA6,0xDEB1,0xDEA3,0xDEAE),('B',0xE4E6,0xE698,0xE6A3,0xDF34,0xDF3F,0xDF31,0xDF3C),('C',0xE583,0xE6EE,0xE6F4,0xE1F9,0xE27A,None,None))
 for channel,entry,sample_handler,ornament_handler,sample,ornament,sample_gate,ornament_gate in profiles:
  for second_opcode in (3,4):
   for first in range(256):
    # Все пары байтов подтверждают, что более поздний PUSH получает первый параметр.
    for second in range(256):
     target=sample_handler if second_opcode==3 else ornament_handler;m.recording=False;m[0x7000:0x7005]=[3,second_opcode,0xD0,first,second];m[0xBFFA:0xC000]=[0xA5]*4+[255,63];m[0xE2B9]=0x31;m[0xE6EC]=0xA5
     initial=get_registers({'HL':0xDB57,'DE':0x7000,'BC':0x2468,'AF':0x9876,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x0618,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':entry},None,False);s.registers[:]=initial;m.writes=[];m.recording=True
     for n in range(120):
      if s.registers[PC]==0x3FFF:break
      s.run()
     else:raise AssertionError(('effect_stack_return',channel,second_opcode))
     m.recording=False;expected=[(0xBFFD,sample_handler>>8),(0xBFFC,sample_handler&255),(0xBFFB,target>>8),(0xBFFA,target&255)]
     if channel=='C':expected += [(0xE6EC,0x31),(0xE6EC,0x31)]
     first_address=sample if second_opcode==3 else ornament;expected.append((first_address,first));expected.append((sample,second))
     if channel!='C':expected += [(sample_gate if second_opcode==3 else ornament_gate,6),(sample_gate,6)]
     assert sorted(m.writes)==sorted(expected),('stack_memory',channel,second_opcode,first,second)
     positions=[v for a,v in m.writes if a in (sample,ornament)];assert positions==[first,second]
     for field,value in (('LATESTHANDLER',target),('EARLIERHANDLER',sample_handler),('CALLERRETURN',0x3FFF)):
      address=0xBFFA+layout['FMUSICDEFERREDPAIRFRAME.'+field];assert m[address]+256*m[address+1]==value
     r=s.registers;assert r[SP]==0xC000 and r[0]==(second if channel=='C' else 6) and r[1]==0x41 and r[2]*256+r[3]==0x1020 and r[4]*256+r[5]==0x7005 and r[6]*256+r[7]==target
     assert all(r[i]==initial[i] for i in (8,9,10,11,*range(16,24)));counts[channel+'.3_'+str(second_opcode)]+=1
 report={'passed':True,'cases_by_sequence':dict(counts),'total_cases':sum(counts.values()),'all_parameter_pairs':True,'physical_deferred_stack_words_checked':True,
  'lifo_execution_order_checked':True,'physical_struct_fields_checked':True,'duplicate_sample_command_overwrite_checked':True,'every_memory_write_observed':True,'all_effect_permutations_proved':False,'irq_executed':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicEffectStackVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
