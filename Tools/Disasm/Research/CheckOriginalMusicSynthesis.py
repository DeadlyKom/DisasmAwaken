"""Исходная композиция до петли, каждый звуковой кадр сравнивается с независимыми формулами."""
from pathlib import Path
import collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator,AyPorts,get_registers,PC,SP,invoke,word
from CheckMusicGateTicks import Memory,xor_flags
from ReferenceMusicSynthesis import PROFILES,synthesize
from ReferenceMusicPattern import PROFILES as PATTERN_PROFILES, decode
from ReferenceMusicPhases import advance_bc, advance_a


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);s.registers[:]=get_registers({'IY':0x5C3A},None,False);ports=AyPorts(raw);s.set_tracer(ports);invoke(s,0xDB00)
 previous=word(m,0xDF98);events=collections.Counter();samples=collections.defaultdict(set);ornaments=collections.defaultdict(set);checks=0;instructions=0;looped=False
 decoder_counts=collections.Counter();command_counts=collections.Counter();pattern_entries={p['entry']:name for name,p in PATTERN_PROFILES.items()};phase_checks=0;advance_a_checks=0;position_changes=0;position_loops=0
 # Обычный кадровый вызов и реальный последующий разбор строк, без дисковых и ISR-заглушек.
 for tick in range(12000):
  m.recording=False;m.writes=[];m[0xBFFE:0xC000]=[255,63];s.registers[SP]=0xBFFE;s.registers[PC]=0xDB05;expected=None;checked=False;pattern=None;phase=None;advance=None
  for n in range(100000):
   pc=s.registers[PC]
   if pattern is not None and pc==pattern['return_address'] and s.registers[SP]==pattern['sp']:
    r=s.registers;assert m==pattern['memory'],('original_pattern_memory',tick,pattern['channel'])
    assert sorted(m.writes[pattern['write_start']:])==sorted(pattern['writes']),('original_pattern_writes',tick)
    assert r[:8]==pattern['main'] and r[16:24]==pattern['alternate'],('original_pattern_registers',tick,r[:8],pattern['main'])
    decoder_counts[pattern['channel']]+=1;command_counts.update(pattern['channel']+'.'+format(op,'02X') for op in pattern['commands']);pattern=None
   if pc==0x3FFF:break
   if pc in pattern_entries and pattern is None:
    r=s.registers;name=pattern_entries[pc];pattern=decode(m,name,de=r[4]*256+r[5],hl=r[6]*256+r[7],alternate=r[16:24],stack=r[SP])
    pattern.update(channel=name,return_address=word(m,r[SP]),write_start=len(getattr(m,'writes',[])));m.recording=True
   if pc==0xDF7F:
    assert advance is None;r=s.registers;advance=advance_a(m,r[:8],r[16:24],r[SP]);advance['write_start']=len(m.writes);m.recording=True
   if pc==0xDFE3:
    if advance is not None:
     assert m==advance['memory'] and sorted(m.writes[advance['write_start']:])==sorted(advance['writes']),('original_advance_a_memory',tick)
     assert s.registers[:8]==advance['main'] and s.registers[16:24]==advance['alternate'] and s.registers[SP]==advance['sp'],('original_advance_a_registers',tick)
     advance_a_checks+=1;position_changes+=int(advance['position_changed']);position_loops+=int(advance['looped'])
    assert expected is None;expected=synthesize(m,s.registers[SP],s.registers[18]*256+s.registers[19]);m.writes=[];m.recording=True;ports.events=[]
    for p in PROFILES:
     if m[p['disabled']]==0:samples[p['name']].add(word(m,p['sample']));ornaments[p['name']].add(word(m,p['ornament']))
   if pc==0xE37C:
    assert expected is not None and not checked;m.recording=False
    diff=[(a,m[a],expected['memory'][a]) for a in expected['writes'] if m[a]!=expected['memory'][a]]
    assert not diff,('original_tune_memory',tick,diff)
    assert {a for a,v in m.writes}==expected['writes'],('original_tune_write_set',tick)
    assert [(e['port'],e['value']) for e in ports.events]==expected['ports'],('original_tune_ports',tick)
    r=s.registers;shape=expected['shape'];assert r[0]==shape and r[1]==xor_flags(shape) and r[8]*256+r[9]==expected['ix'] and r[18]*256+r[19]==expected['last_bc'] and r[SP]==0xBFFE
    checks+=1;events.update(expected['events']);checked=True
    phase=advance_bc(m,r[:8],r[16:24],r[SP]);phase['write_start']=len(m.writes);m.recording=True
   s.run()
  else:raise AssertionError(('original_tune_frame_limit',tick))
  instructions+=n;assert checked and s.registers[SP]==0xC000 and s.registers[10]*256+s.registers[11]==0x5C3A
  assert pattern is None and phase is not None
  assert m==phase['memory'] and sorted(m.writes[phase['write_start']:])==sorted(phase['writes']),('original_phase_memory',tick)
  assert s.registers[:8]==phase['main'] and s.registers[16:24]==phase['alternate'],('original_phase_registers',tick)
  phase_checks+=1
  position=word(m,0xDF98)
  if position<previous:assert position==word(m,0xDF9F)+1;looped=True;break
  previous=position
  if tick%512==0:print('Original synthesis tick',tick,flush=True)
 assert looped and checks==tick+1
 report={'passed':True,'source_sha256':hashlib.sha256(raw).hexdigest(),'frames':checks,'frame_instructions':instructions,'position_loop_reached':True,
  'independent_core_reference_events':dict(events),'sample_pointers':{k:sorted(v) for k,v in samples.items()},'ornament_pointers':{k:sorted(v) for k,v in ornaments.items()},
  'original_initialize_and_pattern_decoders_executed':True,'every_core_write_and_raw_ay_port_event_compared':True,'full_stack_and_iy_restored_each_frame':True,
  'pattern_decoder_algorithm_independently_proved':True,'pattern_calls_by_channel':dict(decoder_counts),'pattern_opcodes_observed':dict(command_counts),
  'independently_checked_bc_phases':phase_checks,'all_actual_pattern_memory_and_registers_compared':True,
  'independently_checked_advance_a':advance_a_checks,'independently_checked_position_changes':position_changes,'independently_checked_position_loops':position_loops,
  'arbitrary_or_reserved_pattern_streams_proved':False,'irq_executed':False,'native_audio_verified':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/OriginalMusicSynthesisVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
