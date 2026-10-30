"""Все слова счётчика ранга и исходный вывод на пограничных значениях."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckScreenUpdate import put


def main():
 _,_,banks=make_context();memory=bytearray(65536)
 for address,bank in ((0x4000,5),(0x8000,2),(0xC000,0)):memory[address:address+16384]=bytes(banks[bank])
 original=memory.copy();sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 thresholds=[int.from_bytes(memory[a:a+2],'big') for a in range(0xAD21,0xAD2D,2)]
 assert thresholds==[10000,3000,1000,300,100,30]
 texts=(0xACEB,0xACF4,0xACFD,0xAD06,0xAD0F,0xAD17,0xACE3);selection=rendered=0
 def index(score):return next((i for i,value in enumerate(thresholds) if score>=value),6)
 for score in range(65536):
  sim.registers[:]=initial;r=sim.registers;memory[0x984C:0x984E]=score.to_bytes(2,'little')
  sim.run(start=0xAC7A,stop=0xBD08);rank=index(score)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(texts[rank],score,6-rank,rank,rank,0x44 if rank==0 else 0x42 if rank<6 else 2,0x7FFE)
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];selection+=1
 # Проверка полного префикса и выбранного имени с настоящим PrintText без заглушек.
 for score in sorted({0,65535,*[n+d for n in thresholds for d in (-1,0,1)]}):
  memory[:]=original;memory[0x984C:0x984E]=score.to_bytes(2,'little');memory[0x7FFE:0x8000]=bytes([255,63])
  for address,value in ((0x6320,0),(0x6321,0),(0xAEAB,192),(0xAEB3,255),(0xAEBB,0),(0xAEBF,0),(0xAEC7,0),(0xAECB,0),(0xBD26,1)):memory[address]=value
  sim.registers[:]=initial;r=sim.registers;r[PC]=0xAC74;seen=[];previous=None
  for _ in range(30000):
   if r[PC]==0x3FFF:break
   if r[PC]==0xBD08 and previous in (0xAC77,0xACBC,0xACC2,0xACC8,0xACCE,0xACD4,0xACDA,0xACE0):seen.append(r[H]*256+r[L])
   previous=r[PC];sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('limit',score))
  rank=index(score);end=memory.index(10,texts[rank])+1
  assert seen==[0xAD2D,texts[rank]] and (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(end,score,6-rank,rank,10,0x4A,0x8000)
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];rendered+=1
 report=dict(passed=True,selection_cases=selection,full_print_cases=rendered,
  method='original_big_endian_threshold_scan_all_words_and_actual_rank_print',thresholds=thresholds,
  equality_chooses_higher_rank=True,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PlayerRankVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
