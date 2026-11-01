"""Настоящий MUZ1.Stop, AY-порты, IM 1 и двухсловный CPU-вход станционного StopMusic."""
import collections,json,re
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from skoolkit.simutils import SP,I,IFF,IM


def main():
 _,_,base=make_context();raw=payload(10);base[3][0x1B00:0x1B00+len(raw)]=list(raw);counts=collections.Counter()
 structure=(ROOT/'Includes/Structs/Include.inc').read_text('utf-8').split('struct FStopMusicReturnFrame',1)[1].split('                ends',1)[0]
 assert re.findall(r'(?m)^(\w+)\s+dw #0000\s*;',structure)==['HLWord','ReturnAddress']
 def execute(flags,im,iff,hl_word,page,old_i):
  f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;r[1]=flags;r[I]=old_i;r[IFF]=iff;r[IM]=im;r[SP]=0x7FFC;put(m,0x7FFC,hl_word.to_bytes(2,'little')+bytes((255,63)));f.trace.ay=list(range(16));f.trace.writes.clear();observed=[]
  def observe(f,pc):
   if pc==0xDB08:
    assert r[SP]==0x7FFA and bytes(m[0x7FFA:0x8000])==bytes((0xB2,0x63))+hl_word.to_bytes(2,'little')+bytes((255,63));observed.append(pc)
   if pc==0x63C1:assert r[SP]==0x7FFC and bytes(m[0x7FFC:0x8000])==hl_word.to_bytes(2,'little')+bytes((255,63))
  f.run(0x63AA,observe)
  expected_ports=[(0x7FFD,0x13)]+[item for reg in range(13,-1,-1) for item in ((0xFFFD,reg),(0xBFFD,0))]+[(0x7FFD,0x10)]
  assert observed==[0xDB08] and f.trace.writes==expected_ports and f.trace.ay==[0]*14+[14,15]
  assert r[:8]==[0x10,0x42|(flags&1),0xBF,0xFD,0,0,hl_word>>8,hl_word&255] and r[8:10]==f.initial[8:10] and r[10:12]==[0x5C,0x3A]
  assert r[16:24]==f.initial[16:24] and r[I]==0x3F and r[IM]==1 and r[IFF]==iff and m.o7ffd==m[0x6306]==0x10 and f.wakes==0
  counts['complete_stop']+=1
 # Проверка всех F, каждого исходного I, всех незаблокированных байтов страницы и разных слов POP HL.
 for flags in range(256):execute(flags,flags%3,flags&1,(flags*257)^0xBEEF,flags&31,(flags*73)&255)
 # Проверка всех сочетаний IM, IFF и Carry на крайних значениях входного слова.
 for im in (0,1,2):
  for iff in (0,1):
   for carry in (0,1):
    for word in (0,1,0x7FFF,0x8000,0xFFFF):execute(carry,im,iff,word,0x18,0xA7)
 report=dict(passed=True,cases_by_path=dict(counts),all_initial_flag_bytes=True,all_initial_i_bytes=True,
  exact_14_ay_register_zero_writes=True,ay_io_registers_14_15_preserved=True,real_music_stop_executed=True,
  exact_physical_two_word_entry_frame=True,stack_delta=4,im_forced_to_1=True,iff_preserved=True,
  hl_word_caller_origin_established=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StopMusicVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
