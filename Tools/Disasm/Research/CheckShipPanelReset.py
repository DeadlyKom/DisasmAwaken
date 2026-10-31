"""Сброс выбора корабельных панелей, полное сравнение банков и пересекающихся записей."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import logical_flags


def main():
 _,_,base=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 for page in (0x10,0x18):
  for selector in (0,1,7,255):
   for set_index,clear_index in ((29,28),(28,29),(0,63),(63,0),(28,28)):
    for flags in range(256):
     m=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[A]=selector
     # Подготовка разных исходных флагов и одинаковых индексов проверяет порядок SET, затем RES.
     put(m,0x7A83,set_index.to_bytes(2,'little'));put(m,0x7A56,clear_index.to_bytes(2,'little'))
     first=0xF101+16*set_index;last=0xF101+16*clear_index;m[first]=flags;m[last]=flags^0xA5
     m[0x6306]=page;m[0x68EB]=0xD3;m[0x7068]=0x81;m[0x67D7]=0x82;m[0x79DD]=0x83;m.banks[4][0x2146]=0x84;put(m,0x7FFE,[255,63]);expected=[b.copy() for b in m.banks]
     # Независимый результат меняет только перечисленные исходным алгоритмом байты и рабочие места CPU-стека.
     expected[5][0x2906]=selector;expected[5][0x28EB]=1;expected[5][0x27D7]=255;expected[5][0x39DD]=0
     expected[0][first-0xC000]|=1;expected[0][last-0xC000]&=254;expected[4][0x2146]=0;expected[5][0x2306]=page
     s.run(start=0x7E1F,stop=0x3FFF)
     assert r[H]*256+r[L]==last and r[A]==page and r[F]==logical_flags(page) and r[SP]==0x8000
     assert r[2:6]==initial[2:6] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
     assert trace.writes==[(0x7FFD,page|4),(0x7FFD,page)] and m.o7ffd==page
     # PUSH служебных вызовов оставляет байты под вершиной стека, они не являются игровыми данными.
     expected[5][0x3FF8:0x3FFE]=m.banks[5][0x3FF8:0x3FFE]
     assert all(actual==want for actual,want in zip(m.banks,expected)),(page,selector,set_index,clear_index,flags)
     cases+=1
 report=dict(passed=True,cases=cases,all_frame_flag_bytes=True,aliased_records_set_then_clear=True,all_eight_banks_compared_except_six_stack_scratch_bytes=True,original_banked_write_and_port_trace=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ShipPanelResetVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
