"""Исходный EAB6, разнесённая таблица и независимая рациональная геометрия отрезка."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from Analyze import payload
from CheckClipGeometry import expected,classify
from CheckGlyphRenderer import compare_flags


def main():
 raw=payload(6);m=bytearray(65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 profiles=((15,23,16,24),(63,63,64,64),(127,95,128,96),(207,111,208,112),(239,175,240,176));codes=(0,1,2,4,5,6,8,9,10)
 table={x*16+y:m[0xCC00+x*16+y]+256*m[0xCD00+x*16+y] for x in codes for y in codes}
 rng=random.Random(0xEAB6);cases=0;pairs=collections.Counter();outcomes=collections.Counter();targets=set();mismatches=[];mismatch_count=0
 for profile in profiles:
  max_x,max_y,_,_=profile;m[0x7FFE:0x8000]=bytes((255,63));s.registers[:]=initial;r=s.registers;r[H]=max_y;r[L]=max_x;r[D]=r[E]=0
  # Настройка настоящим входом, H ограничивает строки FirstAxis, L колонки SecondAxis.
  s.run(start=0xE011,stop=0x3FFF)
  vx=sorted(set((-512,-256,-1,0,1,127,254,255,256,511,512,767,max_x-1,max_x,max_x+1)))
  vy=sorted(set((-512,-256,-1,0,1,127,254,255,256,511,512,767,max_y-1,max_y,max_y+1)))
  points=[(x,y) for x in vx for y in vy];fixtures=[(a,b) for a in points for b in points]
  fixtures.extend(((rng.randrange(-512,768),rng.randrange(-512,768)),(rng.randrange(-512,768),rng.randrange(-512,768))) for _ in range(4096))
  def packed(point):
   code=classify(point,profile)
   return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes((((~code&15)<<4)|code,))
  for first,second in fixtures:
   c1=classify(first,profile);c2=classify(second,profile);wanted,kind=expected(first,second,True,profile)
   for seen in (0,255):
    m[0xC22C:0xC231]=packed(first);m[0xC23C:0xC241]=packed(second);m[0xC24F]=seen;m[0xC250]=0
    m[0xC7FF:0xC901]=bytes([0xA7])*258;m[0x7FFE:0x8000]=bytes((255,63));s.registers[:]=initial;r=s.registers
    # Проверка перестановки полных пятибайтовых записей и трёх подставных CPU-возвратов.
    s.run(start=0xEAB6,stop=0xEB07);index=c2*16+c1 if c1==0 else c1*16+c2;target=r[H]*256+r[L]
    assert target==table[index] and r[SP]==0x7FF8 and m[0x7FF8:0x7FFE]==bytes((8,0xEB))*3
    assert m[0xC250]==1 and m[0xC22B]==0
    selected=(second,first) if c1==0 else (first,second)
    assert m[0xC22C:0xC231]==packed(selected[0]) and m[0xC23C:0xC241]==packed(selected[1])
    targets.add(target);s.run(stop=0x3FFF);size=m[0xC22B];assert size in (0,2,4)
    actual=list(zip(m[0xC800:0xC800+size:2],m[0xC801:0xC800+size:2]))
    if actual!=wanted:
     mismatch_count+=1
     if len(mismatches)<8:mismatches.append(dict(profile=profile,first=first,second=second,seen=seen,actual=actual,expected=wanted,kind=kind))
    normal=(r[A],r[F],r[D]*256+r[E])==(size,compare_flags(size,4),0xEB08)
    special=(r[A],r[F],r[B]*256+r[C],r[H]*256+r[L])==(0xEB,0xA9,0xEA,0xEBF2)
    assert normal or special,(profile,first,second,size,r[:8])
    assert r[SP]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
    assert m[0xC7FF]==m[0xC900]==0xA7 and m[0xC800+size:0xC900]==bytes([0xA7])*(256-size)
    assert m[0xC250]==1 and all(m[0xCC00+i]+256*m[0xCD00+i]==v for i,v in table.items())
    outcomes['normal_return' if normal else 'special_return']+=1;outcomes['output_'+str(size)]+=1;pairs[c1,c2]+=1;cases+=1
 report=dict(passed=mismatch_count==0,cases=cases,profiles=profiles,outcode_pairs_checked=len(pairs),effective_handler_targets_executed=len(targets),cases_by_outcome=dict(outcomes),independent_rational_interval_and_original_quantization=True,real_e011_configuration=True,real_eab6_dispatch_and_all_arithmetic=True,both_corner_seen_states=True,exact_five_byte_swap_and_three_stack_copies=True,normal_return_de_eb08_checked=True,special_return_eb_a9_00ea_ebf2_checked=True,output_guard_bytes_and_tail_preserved=True,all_final_registers_proved=False,full_handler_contracts_proved=False,mismatch_count=mismatch_count,examples=mismatches,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipSegmentVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
