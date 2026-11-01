"""Исходное ядро A/B/C и AY против независимых формул, без разбора строк и IRQ."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from CheckMusic import Simulator,AyPorts,get_registers,PC,SP
from CheckMusicGateTicks import Memory,xor_flags
from ReferenceMusicSynthesis import PROFILES,synthesize
from skoolkit.simutils import I,IFF,IM
from VerifySources import structure_symbols


def main():
 layout=structure_symbols();assert layout['FMUSICLOOPHEADER']==2 and layout['FMUSICLOOPHEADER.LOOPPOSITION']==0 and layout['FMUSICLOOPHEADER.LENGTH']==1
 assert layout['FMUSICSAMPLESTEP']==4 and [layout['FMUSICSAMPLESTEP.'+f] for f in ('SHIFTCONTROL','LEVELMODES','TONEDELTA')]==[0,1,2]
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);ports=AyPorts(raw);s.set_tracer(ports);base=list(m);ramp=bytes(range(256))*3;ornament_pattern=bytes((v*73)&255 for v in range(256))*2;counts=collections.Counter();events=collections.Counter();samples=(0x6000,0x6800,0x7000);ornaments=(0x4000,0x4200,0x4400)
 vectors=[(value,0) for value in range(65536)]+[(value,mask) for mask in range(1,8) for value in range(256)]
 for number,(seed,disabled_mask) in enumerate(vectors):
  low=seed&255;high=seed>>8;m.recording=False;m[0xDB00:0xE700]=base[0xDB00:0xE700]
  def byte(a,v):m[a]=v&255
  def word(a,v):m[a:a+2]=[v&255,(v>>8)&255]
  for channel,p in enumerate(PROFILES):
   control=(high+channel*31)&255;modes=(low+channel*73)&255;tone=(seed+channel*0x369C)^0xA55A;tone&=65535;lo=tone&255;hi=tone>>8;data=bytearray(1024);data[0::4]=bytes([control])*256;data[1::4]=bytes([modes])*256;data[2::4]=ramp[lo:lo+256];cut=256-lo;data[3::4]=ramp[hi:hi+cut]+ramp[hi+cut+1:hi+257]
   sample=samples[channel];ornament=ornaments[channel];m[sample:sample+2]=[(low*31+channel)&255,(high*73+channel)&255];m[sample+2:sample+1026]=list(data);shift=(high+channel*31)&255;m[ornament:ornament+2]=[(high+channel*73)&255,(low*31+channel)&255];m[ornament+2:ornament+258]=list(ornament_pattern[shift:shift+256])
   byte(p['disabled'],255 if disabled_mask&(1<<channel) else 0);word(p['sample'],sample);word(p['ornament'],ornament);byte(p['sample_pos'],low+high*73+channel*31);byte(p['orn_pos'],high+low*31+channel*73)
   for key,value in (('adjust',(low*73+high+channel*31)&255),('volume',((low+channel)&15)*16),('envelope',0x10 if (low+channel)&1 else 0),('noise',high+channel*31),('env_shift',low+channel*73),('note',low+high+channel*31),('counter',high+channel*73),('reload',low*31+channel),('branch',0 if low&2 else 0x1D),('target',low*31+high+channel*73),('gate',high+channel*31),('off',low+channel*73),('on',high+channel*31)):byte(p[key],value)
   word(p['tone_shift'],seed^((channel+1)*0x369C));word(p['slide'],seed^((channel+1)*0x1357));word(p['step'],seed*73+channel*0x1234)
  byte(0xDFE4,high);byte(0xDFE8,low);byte(0xDFE9,high^0xA5);word(0xE2F1,seed^0x5AA5);word(0xE2EE,seed^0xA55A);word(0xE302,seed*31);byte(0xE2FA,high);byte(0xE309,low)
  m[0xDC00:0xDC0E]=[(seed+n*19)&255 for n in range(14)];initial=get_registers({'HL':0x1357,'DE':0x2468,'BC':0x369C,'AF':0x9800|low,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0x7FFE,'PC':0xDFE3},None,False);initial[I]=high;initial[IM]=low%3;initial[IFF]=0
  expected=synthesize(m,0x7FFE,0x9ABC);s.registers[:]=initial;m.writes=[];m.recording=True;ports.events=[];stage_inputs={};checked=set();starts=(0xDFE3,0xE0ED,0xE1ED);finishes=(0xE0CD,0xE1CD,0xE2CB)
  for step_count in range(1200):
   if s.registers[PC]==0xE37C:break
   pc=s.registers[PC]
   if pc in starts:
    channel=starts.index(pc);stage_inputs[channel]=(s.registers[16:18].copy(),s.registers[SP],s.registers[1])
   for channel,finish in enumerate(finishes):
    if channel in checked or pc not in (finish,finish+2,finish+5,finish+6):continue
    cp=expected['checkpoints'][channel];kind={'reload':finish,'store':finish+2,'restore':finish+5,'disabled':finish+6}[cp['exit_kind']];assert pc==kind,('synthesis_exit_kind',seed,disabled_mask,channel,hex(pc),hex(kind))
    r=s.registers;assert all(m[a]==value for a,value in cp['values'].items()) and {a for a,v in m.writes}==cp['writes'],('synthesis_body_memory',seed,disabled_mask,channel)
    assert r[8]*256+r[9]==cp['ix'] and r[2]*256+r[3]==cp['bc'] and r[23]==cp['envelope'] and r[22]==0x13 and r[20]*256+r[21]==0x2468 and r[18]*256+r[19]==0x369C,('synthesis_body_context',seed,disabled_mask,channel)
    if cp['active']:assert r[16]==cp['level'] and r[17]==cp['level_flags'] and r[SP]==cp['data_sp'],('synthesis_saved_amplitude',seed,disabled_mask,channel,r[16:18],cp['level'],cp['level_flags'])
    else:assert r[0]==0 and r[1]==0x50|(stage_inputs[channel][2]&1) and r[16:18]==stage_inputs[channel][0] and r[SP]==stage_inputs[channel][1]
    if cp['exit_kind']=='store':assert r[0]==cp['counter_result']
    checked.add(channel)
   s.run()
  else:raise AssertionError(('synthesis_boundary',seed,disabled_mask))
  assert len(checked)==3;m.recording=False;differences=[(a,m[a],expected['memory'][a]) for a in expected['writes'] if m[a]!=expected['memory'][a]]
  assert not differences,('synthesis_memory',seed,disabled_mask,differences)
  assert {a for a,v in m.writes}==expected['writes'],('synthesis_write_set',seed,disabled_mask,sorted({a for a,v in m.writes}^expected['writes']))
  actual_ports=[(v['port'],v['value']) for v in ports.events];assert actual_ports==expected['ports'],('synthesis_ports',seed,disabled_mask,[(n,x,y) for n,(x,y) in enumerate(zip(actual_ports,expected['ports'])) if x!=y],len(actual_ports),len(expected['ports']))
  r=s.registers;shape=expected['shape'];assert r[0]==shape and r[1]==xor_flags(shape) and r[2]*256+r[3]==(0xBFFD if shape else 0xBEFD) and r[4]*256+r[5]==0xFFBF and r[6]*256+r[7]==0xDC0D
  assert r[8]*256+r[9]==expected['ix'] and r[18]*256+r[19]==expected['last_bc'] and r[SP]==0x7FFE and all(r[i]==initial[i] for i in (10,11,I,IFF,IM)),('synthesis_registers',seed,disabled_mask,r[:24],expected['ix'],expected['last_bc'])
  counts[str(disabled_mask)]+=1;events.update(expected['events'])
  if number%4096==0:print('Synthesis case',number,'of',len(vectors),flush=True)
 report={'passed':True,'cases_by_disabled_mask':dict(counts),'total_cases':sum(counts.values()),'reference_events':dict(events),'all_sample_control_and_mode_byte_pairs':True,'all_disabled_channel_combinations':True,
  'independent_numeric_sample_ornament_tone_noise_mixer_envelope_oracle':True,'every_memory_write_address_checked':True,'all_expected_written_values_checked':True,'all_raw_ay_port_events_checked':True,
  'source_ab_sample_offset_low_byte_quirk_preserved':True,'source_note_table_overrun_read_semantics_preserved':True,'source_tone_limit_residual_high_byte_preserved':True,'per_channel_body_boundaries_checked':True,'per_channel_saved_amplitude_af_prime_checked':True,'physical_header_and_sample_step_layout_checked':True,'disabled_path_exact_flags_checked':True,'stack_restored':True,
  'stop_address':0xE37C,'pattern_phase_executed':False,'irq_executed':False,'native_audio_verified':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicSynthesisVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
