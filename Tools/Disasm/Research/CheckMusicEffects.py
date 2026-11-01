"""Семь выделенных отложенных команд A/B/C, реальные обработчики без подмены."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def main(compose=False):
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);counts=collections.Counter()
 profiles={
 'A':{'entries':{1:0xE60C,2:0xE623,3:0xE647,4:0xE652,5:0xDDCA,8:0xDB8C,9:0xE6FA},'delay':0xDE7A,'step':0xDE82,'branch':0xDE88,'target':0xDE75,'pending':0xDE4D,'current':0xE0BB,'sample':0xDEA6,'sample_gate':0xDEA3,'ornament':0xDEB1,'ornament_gate':0xDEAE,'enabled':0xDE97,'disabled':0xDE9F,'gate':0xDE90},
 'B':{'entries':{1:0xE65D,2:0xE674,3:0xE698,4:0xE6A3,5:0xDDEA,8:0xDB8C,9:0xE6FA},'delay':0xDF08,'step':0xDF10,'branch':0xDF16,'target':0xDF03,'pending':0xDEDB,'current':0xE1BB,'sample':0xDF34,'sample_gate':0xDF31,'ornament':0xDF3F,'ornament_gate':0xDF3C,'enabled':0xDF25,'disabled':0xDF2D,'gate':0xDF1E},
 'C':{'entries':{1:0xE6AE,2:0xE6C9,3:0xE6EE,4:0xE6F4,5:0xDE0A,8:0xDB8C,9:0xE6FA},'delay':0xE29D,'reload':0xE2CC,'step':0xE2A6,'branch':0xE2AD,'target':0xE2B1,'pending':0xE2B9,'current':0xE6EC,'sample':0xE1F9,'ornament':0xE27A,'enabled':0xE2E7,'disabled':0xE2E3,'gate_counter':0xE2D5}}
 for channel,p in profiles.items():
  for effect,entry in p['entries'].items():
   # Проверка всех первых параметров и F с шестью граничными словами шага.
   for delay in range(256):
    for step in (0,1,0x7FFF,0x8000,0xA55A,0xFFFF):
     limited_step=step^0xA55A;target=delay^0x5A;current=delay^0xA5;flags=(delay*73)&255
     parameters=[delay,step&255,step>>8,limited_step&255,limited_step>>8];stream=([effect,0xD0] if compose else [])+parameters
     m.recording=False;m[0x7000:0x7000+len(stream)]=stream;m[p['pending']]=target;m[p['current']]=current;m[0xBFFE:0xC000]=[255,63]
     initial=get_registers({'HL':0xDB57 if compose else 0x1357,'DE':0x7000,'BC':0x2468,'AF':0x9800|flags,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x0618,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':{'A':0xE439,'B':0xE4E6,'C':0xE583}[channel] if compose else entry},None,False);s.registers[:]=initial;m.writes=[];m.recording=True
     for n in range(100):
      if s.registers[PC]==0x3FFF:break
      s.run()
     else:raise AssertionError(('effect_return',channel,effect,delay))
     m.recording=False;expected=[];hl=entry if compose else 0x1357;de=0x7002 if compose else 0x7000;bc=0x1020 if compose else 0x2468;a=0 if compose else 0x98;f=0x41 if compose else flags;alt=initial[16:24].copy()
     if compose:
      expected += [(0xBFFD,entry>>8),(0xBFFC,entry&255)]
      if channel=='C':expected.append((0xE6EC,target))
     def put(address,value):expected.append((address,value))
     def word(address,value):put(address,value&255);put(address+1,value>>8)
     if effect in (1,2):
      put(p['delay'],delay)
      if channel=='C':put(p['reload'],delay)
      word(p['step'],step if effect==1 else limited_step);put(p['branch'],0x1D if effect==1 else 0)
      if effect==1:
       hl=step;de+=3;a=0x1D
       if channel=='C':put(p['gate_counter'],0);a=0;f=0x44
      else:
       restored=target if compose and channel=='C' else current
       de+=5;hl=p['pending'];bc&=255;f=0x44;put(p['target'],target);put(p['pending'],restored);a=target if channel=='C' else current
       if channel=='C':put(p['gate_counter'],0)
      if channel!='C':alt[5]=alt[4]
     elif effect in (3,4):
      key='sample' if effect==3 else 'ornament';put(p[key],delay);de+=1;a=delay
      if channel!='C':put(p[key+'_gate'],6);a=6
     elif effect==5:
      put(p['enabled'],delay);put(p['disabled'],step&255);de+=2
      if channel=='C':put(p['gate_counter'],delay);a=step&255
      else:put(p['gate'],6);a=6
     elif effect==8:
      put(0xDF74,delay);word(0xDF6E,step);put(0xDF6B,6);hl=step;de+=3;a=6
     elif effect==9:put(0xDF62,delay);de+=1;a=delay
     r=s.registers;assert sorted(m.writes)==sorted(expected),('effect_memory',channel,effect,delay,step,m.writes,expected)
     assert r[SP]==0xC000 and r[0]==a and r[1]==f and r[2]*256+r[3]==bc and r[4]*256+r[5]==de and r[6]*256+r[7]==hl,('effect_registers',channel,effect,delay,step,r[:8],a,f,bc,de,hl)
     assert r[16:24]==alt and all(r[i]==initial[i] for i in (8,9,10,11));counts[channel+'.'+str(effect)]+=1
 report={'passed':True,'cases_by_effect':dict(counts),'total_cases':sum(counts.values()),'all_first_parameter_and_flag_bytes':True,
  'ignored_portamento_bytes_preserved':True,'six_step_boundary_words':True,'every_memory_write_observed':True,'real_handlers_executed':True,
  'direct_handler_entries':not compose,'supported_single_effect_stack_composition':compose,'terminal_opcode':0xD0 if compose else None,'full_pattern_decode_proved':False,'irq_executed':False,'native_audio_verified':False,'assembly_executed':False}
 stem='MusicEffectsComposition' if compose else 'MusicEffects';(ROOT/('Tools/Disasm/Reports/'+stem+'Verification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
