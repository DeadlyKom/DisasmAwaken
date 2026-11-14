"""Все 32 входа развёрнутой строки и маска правого края, до общего продолжения D207.

Документация: ../../../Docs/PreviewPolygonFill.md#стоимость-развёрнутой-записи-строки
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewPolygonOracle import PATTERNS
from PreviewEdgeRasterOracle import logical,column_context


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0xC069,'BC':0x5000,'AF':0xFF5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 baseline=bytes((i*37+11)&255 for i in range(256));cases=0;refresh_seeds=set()
 # Проверка 31 исходной пары LD (BC),A / INC C и девяти байтов общего края.
 assert bytes(m[0xD1C0:0xD207])==bytes.fromhex('020c')*31+bytes.fromhex('08fd5deb0aa62cb602')
 # Проверка каждого числа полных байтов, всех начальных C и пяти рабочих шаблонов.
 for count in range(32):
  entry=0xD1FE-2*count
  for column in range(256):
   for mode,(first,delta) in enumerate(PATTERNS[:5]):
    for phase in range(2):
     for bit in range(8):
      pattern=first^(delta if phase else 0);index=bit*32+mode*2+16
      expected=bytearray(baseline);writes=[]
      for offset in range(count):pointer=(column+offset)&255;expected[pointer]=pattern;writes.append((0x5000+pointer,pattern))
      end=(column+count)&255;preserve=255>>bit;value=(expected[end]&preserve)|(pattern&~preserve);expected[end]=value;writes.append((0x5000+end,value))
      m.recording=False;m[0x5000:0x5100]=baseline;s.registers[:]=initial;r=s.registers
      r[0]=pattern;r[1]=(initial[1]&254)|(column&1);r[3]=column;r[4]=0xC0+phase;r[6]=entry>>8;r[7]=entry&255;r[11]=index
      r[14]=column;r[15]=(cases*73)&255;r[26]=cases&1;r[27]=cases%3
      saved=r[:];refresh_seeds.add(r[15]);m.recording=True;m.writes=[];s.run(start=entry,stop=0xD207)
      assert bytes(m[0x5000:0x5100])==expected and m.writes==writes,(count,column,mode,phase,bit)
      assert tuple(r[:8])==(value,logical(value),0x50,end,entry>>8,entry&255,0xC0+phase,index+1)
      alt_flags=column_context(end,1,saved[1]&1) if count else saved[1]
      assert tuple(r[16:18])==(pattern,alt_flags)
      assert r[8:13]==saved[8:13] and r[18:24]==saved[18:24]
      # Расчёт M1 прямой развёртки, две выборки на полный байт и девять на край.
      m1=2*count+9
      assert r[15]==(saved[15]&128)|((saved[15]+m1)&127)
      assert r[14]==saved[14] and r[26:28]==saved[26:28]
      cases+=1
 report=dict(passed=True,cases=cases,all_32_even_span_entries=True,all_256_initial_columns=True,all_eight_right_pixel_positions=True,consistent_modes=[0,1,2,3,4],both_pattern_phases=True,carry_zero_and_one_checked=True,exact_bitmap_and_ordered_write_trace=True,exact_main_and_alternate_af=True,all_other_registers_and_sp_checked=True,continuation=0xD207,cpu_return_executed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 assert refresh_seeds==set(range(256))
 report.update(R_formula='2*full_bytes+9',M1_bounds=[9,71],R_initial_values=256,
  R_bit7_and_I_IM_IFF_preserved=True,entire_original_71_byte_span_checked=True,
  full_joint_R_input_product=False,row_loop_R_cost_proved=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonSpanVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
