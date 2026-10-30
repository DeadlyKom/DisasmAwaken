"""Полный табличный вход D48B, исходные помощники и проверка протокола двух выходов."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,B,C,SP
from CheckRowHighlight import make_context
from CheckGlyphRenderer import compare_flags


def outcode(x,y):return (2 if x<0 else 1 if x>=255 else 0)|(8 if y<0 else 4 if y>=255 else 0)


def encoded(x,y):
 code=outcode(x,y);return ((~code&15)<<4)|code


def record(point):return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes([encoded(*point)])


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 values=(-512,-256,-1,0,127,254,255,511,767);points=[(x,y) for x in values for y in values]
 counts=collections.Counter();pairs=collections.Counter();targets=set();swaps=0
 table={index:memory[0xDE00+index]|memory[0xDF00+index]<<8 for first in (0,1,2,4,5,6,8,9,10) for second in (0,1,2,4,5,6,8,9,10) for index in (first*16+second,)}
 # Проверка всех пар девяти кодов на разных расстояниях от каждой границы, при двух исходных состояниях углов.
 for first in points:
  for second in points:
   c1,c2=outcode(*first),outcode(*second)
   for corner_bits in (0,255):
    memory[0xDE2F:0xDE39]=record(first)+record(second);memory[0xDE39]=corner_bits;memory[0xDE3A]=0;memory[0xDE3B]=0xA7
    memory[0xF8FF:0xFA01]=bytes([0xA7])*258;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers
    # Проверка фактического косвенного перехода после полного пролога обмена и трёх PUSH.
    sim.run(start=0xD48B,stop=0xD4DC);index=(c2*16+c1) if c1==0 else (c1*16+c2)
    assert r[H]*256+r[L]==table[index] and r[SP]==0x7FF8
    assert memory[0x7FF8:0x7FFE]==bytes([0xDD,0xD4])*3 and memory[0xDE3A]==1 and memory[0xDE3B]==0
    expected_points=record(second)+record(first) if c1==0 else record(first)+record(second)
    assert memory[0xDE2F:0xDE39]==expected_points
    targets.add(table[index]);sim.run(stop=0x3FFF)
    size=memory[0xDE3B];assert size in (0,2,4),(first,second,size)
    normal=(r[A],r[F])==(size,compare_flags(size,4));special=(r[A],r[F],r[H]*256+r[L],r[B]*256+r[C])==(0xD4,0x81,0xD5B0,0xD3)
    assert normal or special,(first,second,size,list(r))
    assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
    assert memory[0xDE2F:0xDE39]==expected_points and memory[0xDE3A]==1
    assert memory[0xF900+size:0xFA00]==bytes([0xA7])*(256-size) and memory[0xF8FF]==memory[0xFA00]==0xA7
    assert all(memory[0xDE00+i]|memory[0xDF00+i]<<8==target for i,target in table.items())
    if c1&c2:assert size==0 and not(r[F]&0x40)
    elif c1==c2==0:
     assert size==2 and memory[0xF900:0xF902]==bytes(first)
    elif c1==0 or c2==0:assert size==4 and r[F]&0x40
    else:assert size in (0,4)
    counts['normal_return' if normal else 'special_return']+=1;counts['output_'+str(size)]+=1;pairs[c1,c2]+=1;swaps+=c1==0
 report=dict(passed=True,cases=sum(pairs.values()),cases_by_outcome=dict(counts),outcode_pairs_checked=len(pairs),
  effective_handler_targets_executed=len(targets),inside_first_swaps=swaps,
  method='original_D48B_full_dispatch_real_table_products_division_output_and_stack_protocol',
  reachable_table_entries_preserved=True,all_case_algorithms_independently_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ClipSegmentVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
