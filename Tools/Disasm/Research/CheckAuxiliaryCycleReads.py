"""Неразобранный 7CC6, проверка фактических абсолютных чтений 0001 вместо предположения о чтении кода списка."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context


def main():
 _,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0]);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 assert base[0x7CCF:0x7CD2]==base[0x7CDE:0x7CE1]==bytes([0x3A,1,0]);selected=early=zero_iterations=0
 for cursor in range(11):
  for first in range(256):
   for second_zero in ((False,True) if first else (False,)):
    m=bytearray(base);m[1]=first;m[0x98BF]=0xA7;m[0x7CCC:0x7CCE]=(0x99A3+cursor).to_bytes(2,'little');m[0x7FFE:0x8000]=bytes([255,63]);s=Simulator(m);r=s.registers;r[:]=initial;r[PC]=0x7CC6;cycles=0
    for step in range(1000):
     if r[PC] in (0x7D14,0x3FFF):break
     if r[PC]==0x7CDE and second_zero:m[1]=0
     if r[PC]==0x7CCE:
      if cycles:
       assert first==0 and r[H]*256+r[L]==(0x99A3+cursor+cycles)&65535 and m[0x7CCC:0x7CCE]==(0x99A3+cursor).to_bytes(2,'little')
       zero_iterations+=1
      cycles+=1
      if cycles==65:break
     s.run()
    else:raise AssertionError(('instruction_limit',cursor,first,second_zero,hex(r[PC])))
    assert m[0x98BF]==1 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[B]*256+r[C]==0x36C9
    if first==0:assert cycles==65 and r[SP]==0x7FFE
    else:
     expected_cursor=0x99A3 if first&128 else 0x99A3+cursor+1
     assert m[0x7CCC:0x7CCE]==expected_cursor.to_bytes(2,'little')
     if second_zero:assert r[PC]==0x3FFF and (r[A],r[F],r[SP])==(0,0x54,0x8000);early+=1
     else:
      address=(0x98B0+4*(expected_cursor-0x99A3))&65535
      assert r[PC]==0x7D14 and r[D]*256+r[E]==int.from_bytes(m[address:address+2],'little') and r[H]*256+r[L]==int.from_bytes(m[address+2:address+4],'little') and r[SP]==0x7FFE;selected+=1
 report=dict(passed=True,known_semantic_role=False,absolute_rom_reads=['#7CCF -> #0001','#7CDE -> #0001'],all_first_rom_byte_values=True,selected_key_cases=selected,second_read_zero_return_cases=early,zero_first_read_loop_iterations=zero_iterations,initial_cursor_offsets=list(range(11)),constant_zero_read_has_no_local_exit=True,center_and_redraw_executed=False,real_emulator_rom_verified=False,message_index_98BF=1,field_is_numeric_message_selector=True,method='original_fixed_and_changed_ROM_byte_fixture_until_shared_center_or_early_return',irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/AuxiliaryCycleReadsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
