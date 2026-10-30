"""Самостоятельный вход A499, настоящий OUT, полный F и отсутствие возобновления указателя."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put


def main():
 _,_,banks=make_context();memory=SliceableMemory(banks=[bank.copy() for bank in banks],out7ffd=0x10);sim=Simulator(memory);trace=PortTrace(sim);sim.set_tracer(trace)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 # Проверка всех 32 незаблокированных конфигураций порта и всех 256 значений полного входного F.
 for old in range(32):
  for flags in range(256):
   sim.registers[:]=initial;r=sim.registers;r[F]=flags
   # Настройка только модельной начальной конфигурации, этот OUT не засчитывается как инструкция игры.
   trace.write_port(r,0x7FFD,old,0);trace.writes.clear();memory[0x6306]=old;memory[0x6548]=0xA5;put(memory,0x7FFE,[255,63])
   before_base=bytes(memory.banks[5][:6912]);before_shadow=bytes(memory.banks[7][:6912]);pointer_before=bytes(memory[0x6540:0x6585]);sim.run(start=0xA499,stop=0x3FFF)
   assert r[A]==0x10 and r[F]==flags and r[SP]==0x8000 and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[14]==initial[14]
   assert memory.o7ffd==0x10 and memory[0x6306]==0x10 and trace.writes==[(0x7FFD,0x10)]
   assert bytes(memory.banks[5][:6912])==before_base and bytes(memory.banks[7][:6912])==before_shadow and bytes(memory[0x6540:0x6585])==pointer_before
   cases+=1
 report=dict(passed=True,cases=cases,method='original_A499_real_SelectMemoryPage_OUT_all_unlocked_pages_and_full_F_without_pointer_resume',
  initial_paging_values=list(range(32)),pointer_state_and_both_screens_unchanged=True,alternate_AF_preserved=True,
  calls_stubbed=False,hardware_paging_lock_emulated=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShowBaseScreenVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
