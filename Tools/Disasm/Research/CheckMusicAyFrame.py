"""Независимая проверка общей огибающей, реальных портов AY и восстановления SP."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, AyPorts, get_registers, PC, SP
from CheckMusicGateTicks import Memory, xor_flags
from skoolkit.simutils import I, IFF, IM


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);ports=AyPorts(raw);s.set_tracer(ports);cases=0;wrapped=0;shape_writes=0
 # Проверка всех счётчиков и всех младших вкладов огибающей, включая потерянный перенос ADD A,L.
 for counter in range(256):
  for contribution in range(256):
   base=(contribution*257)^0x5AA5;offset=(counter*256+contribution)^0xA55A;step=(0,1,0x7FFF,0x8000,0xA55A,0xFFFF)[(counter+contribution)%6];reload=(counter*73+contribution)&255
   noise=counter^contribution;ixh=(contribution*31+counter)&255;ixl=(counter*17+contribution)&255;shape=contribution
   frame=[(n*19+counter+contribution)&255 for n in range(14)];frame[6]=noise;frame[13]=shape
   m.recording=False;m[0xDC00:0xDC0E]=frame
   for a,v in ((0xE2EE,offset),(0xE2F1,base),(0xE302,step),(0xE30E,0xBFFE)):m[a:a+2]=[v&255,v>>8]
   m[0xE2FA]=counter;m[0xE309]=reload;m[0xDFE9]=0xA5
   initial=get_registers({'HL':0x1357,'DE':0x2468,'BC':0x369C,'AF':0x9876,'IX':ixh*256+ixl,'IY':0x5C3A,'^HL':0xAB00+contribution,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xDD00,'PC':0xE2EB},None,False)
   initial[I]=counter;initial[IFF]=counter&1;initial[IM]=counter%3;s.registers[:]=initial;m.writes=[];m.recording=True;ports.events=[]
   for n in range(120):
    if s.registers[PC]==0xE37C:break
    s.run()
   else:raise AssertionError(('ay_frame_boundary',counter,contribution))
   m.recording=False;low=(base+contribution)&255;period=(((base&0xFF00)|low)+offset)&65535;expected_writes=[(0xDC0B,period&255),(0xDC0C,period>>8)];next_offset=offset;next_counter=counter
   if 1<=counter<=128:
    if counter==1:
     next_offset=(offset+step)&65535;expected_writes += [(0xE2EE,next_offset&255),(0xE2EF,next_offset>>8)];next_counter=reload
    else:next_counter=counter-1
    expected_writes.append((0xE2FA,next_counter))
   expected_writes.append((0xDFE9,ixh))
   if shape:expected_writes.append((0xDC0D,0));shape_writes+=1
   assert m.writes==expected_writes,('memory_writes',counter,contribution,m.writes,expected_writes)
   assert m[0xE2EE]+256*m[0xE2EF]==next_offset and m[0xE2FA]==next_counter
   frame[6]=(noise+ixh)&255;frame[7]=ixl;frame[11]=period&255;frame[12]=period>>8
   expected=[]
   for register in range(14 if shape else 13):expected += [dict(port=0xFFFD,value=register),dict(port=0xBFFD if register in (6,7,13) else 0xBEFD,value=frame[register])]
   assert ports.events==expected,('ay_ports',counter,contribution,ports.events,expected)
   r=s.registers;assert r[0]==shape and r[1]==xor_flags(shape) and r[2]*256+r[3]==(0xBFFD if shape else 0xBEFD) and r[4]*256+r[5]==0xFFBF and r[6]*256+r[7]==0xDC0D
   assert r[SP]==0xBFFE and r[16:24]==[initial[16],initial[17],initial[2],initial[3],initial[4],initial[5],initial[6],initial[7]]
   assert all(r[i]==initial[i] for i in (8,9,10,11,I,IFF,IM))
   wrapped+=int((base&255)+contribution>255);cases+=1
 report={'passed':True,'cases':cases,'all_counter_and_contribution_bytes':True,'discarded_low_byte_carry_cases':wrapped,'shape_port_writes':shape_writes,
  'all_raw_ay_port_events_compared':True,'outi_mirror_befd_checked':True,'envelope_step_affects_next_frame':True,'saved_sp_restored':True,
  'alternate_register_exchange_checked':True,'every_memory_write_observed':True,'stop_address':0xE37C,'pattern_parse_phase_executed':False,'irq_executed':False,'independent_audio_synthesis':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicAyFrameVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
