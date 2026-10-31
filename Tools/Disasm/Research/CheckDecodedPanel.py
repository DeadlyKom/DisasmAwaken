"""Условия перехода панели в финал, исходная рамка, сообщения и весь загрузчик до TR-DOS."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP,IFF
from CheckRowHighlight import make_context
from CheckScreenUpdate import put
from CheckFinalExit import KeyboardTrace
from CheckSignedMultiply import sbc16_flags
from CheckGlyphRenderer import compare_flags


def main():
 _,map_source,banks=make_context();flat=bytearray(65536);flat[0x4000:0x8000]=bytes(banks[5]);flat[0x8000:0xC000]=bytes(banks[2]);flat[0xC000:]=bytes(banks[0]);sim=Simulator(flat)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 # Проверка точного имени фиксированного ключа настоящим банковым BuildSystemName.
 flat[0xC000:]=bytes(banks[1]);flat[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[H],r[L],r[D],r[E]=0x4B,0x37,0x4E,0x25
 sim.run(start=0xE6AB,stop=0x3FFF);fixed_name='Дзета-43/78-Д';raw_name=fixed_name.encode('cp866')+bytes([10]);assert flat[0x630B:0x630B+len(raw_name)]==raw_name;flat[0xC000:]=bytes(banks[0])
 gates=whole=finals=messages=0
 def gate(first,second,code):
  nonlocal gates
  flat[0x983F:0x9843]=first.to_bytes(2,'little')+second.to_bytes(2,'little');flat[0x98A0]=code;sim.registers[:]=initial;r=sim.registers;r[PC]=0x6DDA;r[IFF]=1
  for _ in range(30):
   if r[PC] in (0x6E02,0x6E76):break
   sim.run()
  else:raise AssertionError('Условия панели не завершились')
  if first!=0x4B37:expected=(0x6E76,(first-0x4B37)&65535,0x4B37,0,sbc16_flags(first,0x4B37,0))
  elif second!=0x4E25:expected=(0x6E76,(second-0x4E25)&65535,0x4E25,0,sbc16_flags(second,0x4E25,0))
  else:expected=(0x6E02 if code==0xFE else 0x6E76,0,0x4E25,code,compare_flags(code,0xFE))
  assert (r[PC],r[H]*256+r[L],r[D]*256+r[E],r[A],r[F])==expected
  assert r[B:C+1]==initial[B:C+1] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x7FFE and r[IFF]==1 and flat[0xBD26]==1;gates+=1
 # Проверка каждого первого и второго слова и каждого значения необъяснённого байта 98A0 без исполнения выбранного выхода.
 for word in range(65536):gate(word,0x4E25,0xFE);gate(0x4B37,word,0xFE)
 for code in range(256):gate(0x4B37,0x4E25,code)
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==10);music=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[3][0x1B00:0x1B00+len(music)]=list(music)
 for page in (0x10,0x18):
  for flags in (0,1):
   for message in (0,1):
    for first,second,code in ((0,0,0xFE),(0x4B37,0x4E24,0xFE),(0x4B37,0x4E25,0),(0x4B37,0x4E25,0xFE)):
     m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);m[0x6306]=page;s=Simulator(m);trace=KeyboardTrace(s,[0xFF,0xBE]);s.set_tracer(trace)
     put(m,0x6DD5,[24,0]);put(m,0xF0FD+24*16,[4,3,24,18,flags,14]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x983F,first.to_bytes(2,'little')+second.to_bytes(2,'little'));m[0x98A0]=code;m[0x98BF]=message;put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;r[PC]=0x6DD4;wakes=0;is_final=first==0x4B37 and second==0x4E25 and code==0xFE;observed_message=False;caption_af=None;expected_copy=bytes(m[0x6E11:0x7011])
     for _ in range(150000):
      if r[PC]==(0x3D13 if is_final else 0x3FFF):break
      if r[PC]==0x6DDA:caption_af=list(r[16:18])
      if r[PC]==0x6E76:observed_message=True
      if r[PC]==0xC089:assert m[r[PC]]==0x76;r[PC]+=1;wakes+=1
      else:s.run()
     else:raise AssertionError(('instruction_limit',page,flags,message,first,second,code,hex(r[PC])))
     assert wakes==1 and m[0xBD26]==1 and m[0x98BF]==message
     if is_final:
      assert not observed_message and bytes(m[0x4000:0x4200])==expected_copy and r[SP]==0x5FFD and r[IFF]==0 and m[0x5CDD:0x5CE6]==list(b'FINALF  C');finals+=1
     else:
      assert observed_message and r[SP]==0x8000 and m[0x6306]==page and not trace.reads and not trace.writes and r[8:12]==initial[8:12] and r[16:18]==caption_af and r[18:24]==initial[18:24];messages+=1
     whole+=1
 report=dict(passed=True,gate_cases=gates,fixed_system_name=fixed_name,all_first_words=True,all_second_words=True,all_98A0_bytes=True,whole_panel_cases=whole,whole_final_paths=finals,whole_message_paths=messages,real_caption_message_and_music=True,final_copy_512_bytes_checked=True,explicit_halt_wakeups=whole,unknown_98A0_game_role_retained=True,trdos_executed=False,final_entry_executed=False,whole_frame_bitmap_independent_oracle=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DecodedPanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
