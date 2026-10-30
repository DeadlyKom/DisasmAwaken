"""Генератор предложения с настоящим RNG, чтением ROM, расстоянием и двумя умножениями."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckRandomState import reference as random_step
from CheckCoordinateDistance import reference as distance
from CheckWorldSignature import logical_flags


def main():
 _,map_source,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);original_roms=memory.roms
 original_rom=bytes(original_roms[1]);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=retries=wrapped=0;maximum_attempts=0;quantities=set()
 def check(page,first,second,seed,synthetic):
  nonlocal cases,retries,wrapped,maximum_attempts
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None]
  if synthetic:
   rom=bytearray(original_rom);rom[:256]=bytes(((i%31+1)<<3)|(i&7) for i in range(256));memory.roms=(original_roms[0],rom)
  else:memory.roms=original_roms
  memory.out7ffd(page);memory[0x6306]=page;put(memory,0x7FFE,[255,63]);put(memory,0x983F,first.to_bytes(2,'little')+second.to_bytes(2,'little'))
  put(memory,0xA8AF,[seed,0xA5,0x5A]);put(memory,0x98B4,bytes([0xA7])*8);memory[0x98BF]=0x6B
  # Независимый поиск принятого кандидата по точной арифметике RNG и фактической выбранной ROM.
  low=seed;expected_reads=[];visited=set()
  for attempt in range(1,257):
   if low in visited:raise AssertionError(('nonterminating_low_state',first,second,seed,synthetic))
   visited.add(low);word,high,_,t=random_step(low|((second&255)<<8),second>>8);expected_reads.append(t)
   quantity=memory.roms[1][t]>>3
   if quantity:break
   low=word&255
  else:raise AssertionError('Не найдена принятая попытка')
  x0=((first&255)<<8)|(word&255);y0=(first&0xFF00)|(word>>8)
  x1=((first&255)<<8)|(second&255);y1=(first&0xFF00)|(second>>8)
  value,_,bc,_,alt=distance(map_source,x0,y0,x1,y1,1)
  amount=value*20*quantity;final_bc=bc&0xFF00 if value*20>=256 else bc
  sim.registers[:]=initial;r=sim.registers;r[PC]=0xAC14;trace=PortTrace(sim);sim.set_tracer(trace);seen=[]
  for _ in range(300000):
   if r[PC]==0x3FFF:break
   if r[PC]==0xAC2D:seen.append(r[B]*256+r[C])
   sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('instruction_limit',first,second,seed))
  assert seen==expected_reads and bytes(memory[0x98B0:0x98B4])==first.to_bytes(2,'little')+word.to_bytes(2,'little')
  assert bytes(memory[0x98B4:0x98BC])==bytes([0xA7])*8 and bytes(memory[0xA8AF:0xA8B2])==word.to_bytes(2,'little')+bytes([high])
  assert int.from_bytes(bytes(memory[0x98BC:0x98BE]),'little')==(amount&65535) and memory[0x98BE]==quantity and memory[0x98BF]==0
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(amount>>16,amount&65535,final_bc,page,logical_flags(page),0x8000)
  assert (r[22]*256+r[23],r[20]*256+r[21],r[18]*256+r[19])==(0xA8AF,first,second)
  assert (r[16],r[17])==(alt if alt is not None else tuple(initial[16:18]))
  assert r[8:12]==initial[8:12] and trace.writes==[(0x7FFD,page&0xF8|0x11),(0x7FFD,page)] and memory.o7ffd==page
  quantities.add(quantity);cases+=1;retries+=attempt-1;maximum_attempts=max(maximum_attempts,attempt);wrapped+=amount>=65536
 for page in (0x10,0x18):
  for second in (0,1,255,256,0x4AF3,32767,32768,65535):
   for seed in range(256):check(page,(seed*193+0x4B38)&65535,second,seed,False)
 for seed in range(256):check(0x10,0x4B38,0x4AF3,seed,True)
 report=dict(passed=True,cases=cases,rejected_attempts=retries,maximum_attempts=maximum_attempts,
  reward_word_wrap_cases=wrapped,accepted_quantities=sorted(quantities),
  method='complete_original_offer_generation_rng_rom_read_distance_and_two_products',
  model_rom_sha256=hashlib.sha256(original_rom).hexdigest(),synthetic_rom_cases=256,
  unreal_rom_verified=False,real_rom_execution=False,rom_used_only_as_read_data=True,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionOfferVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
