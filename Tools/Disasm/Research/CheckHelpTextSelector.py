"""Все 65536 AF исходного SelectText, единственная запись в операнд HELP банка 7."""
import json
from ProbePreviewPolygon import ROOT
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers


def main():
 raw=payload(8);assert raw[0x57:0x5B]==bytes.fromhex('3201dbc9') and raw[:8]==bytes.fromhex('3e0021e2e3cd90a3')
 m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF,'I':0x80},{'im':2,'iff':1},False);cases=0
 for value in range(256):
  for flags in range(256):
   s.registers[:]=initial;r=s.registers;r[0]=value;r[1]=flags;before=tuple(r[:30]);m.recording=True;m.writes=[]
   # Проверка исходных STORE и RET, следующий индексатор не подменяется и не исполняется.
   s.run(start=0xDB57,stop=0x3FFF)
   assert tuple(r[:12])==before[:12] and tuple(r[16:24])==before[16:24] and r[12]==0x8000 and r[14]==before[14] and r[26:28]==list(before[26:28])
   assert m.writes==[(0xDB01,value)] and m[0xDB01]==value and m[0xDB00]==0x3E and m[0x7FFE:0x8000]==[255,63];cases+=1
 report=dict(passed=True,cases=cases,all_256_a_by_256_f=True,source_slot=8,source_bank=7,exact_main_alternate_index_i_im_iff_preserved=True,
  exact_single_byte_write_to_ld_a_operand=True,target_instruction=0xDB00,target_operand=0xDB01,sp_plus_two_and_cpu_return=True,
  subsequent_indexer_not_executed=True,selected_record_existence_not_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpTextSelectorVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
