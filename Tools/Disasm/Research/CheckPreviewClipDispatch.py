"""Точный контекст EAB6 перед непрямым JP, все 81 пары и 256 входных AF/BC-контекстов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from Analyze import payload
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=swapped=0;targets=set()
 for c0 in (0,1,2,4,5,6,8,9,10):
  for c1 in (0,1,2,4,5,6,8,9,10):
   for context in range(256):
    first=bytes((context,context^0xA5,context^0x37,255-context,((~c0&15)<<4)|c0));second=bytes((context^0x5C,context^0x91,context^0xDB,context^0x63,((~c1&15)<<4)|c1))
    index=(c1*16+c0) if c0==0 else (c0*16+c1);target=m[0xCC00+index]+256*m[0xCD00+index]
    m.recording=False;m[0xC22C:0xC231]=first;m[0xC23C:0xC241]=second;m[0xC250]=context;m[0xC24F]=context^0xA7;m[0xC22B]=context;m[0x7FF8:0x8000]=[0xA7]*8
    initial[14],initial[15],initial[26],initial[27]=context,(cases*73)&255,0,cases%3
    s.registers[:]=initial;r=s.registers;r[0]=context;r[1]=context^0xA5;r[2]=context;r[3]=255-context
    # Проверка полного исходного префикса, стоп перед JP, обработчик не подменяется заглушкой.
    m.recording=True;m.writes=[];r[24]=0xEAB6;measured_m1=0
    for _ in range(64):
     if r[24]==0xEB07:break
     old_r=r[15];s.run();increment=(r[15]-old_r)&127
     assert increment in (1,2)
     measured_m1+=increment
    else:raise AssertionError('префикс не достиг JP HL')
    wanted_m1=41 if c0==0 else 24
    assert measured_m1==wanted_m1 and r[15]==refresh(initial[15],wanted_m1)
    assert all(r[i]==initial[i] for i in (14,26,27))
    # Расчёт F от последнего INC H страницы CC в CD, Carry сброшен предыдущим OR L.
    flags=0x88
    assert tuple(r[:8])==(index,flags,0xF0 if c0==0 else context,255-context,0xEB,8,target>>8,target&255),(c0,c1,context,r[:8])
    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[12]==0x7FF8
    assert m[0x7FF8:0x7FFE]==[8,0xEB]*3 and m[0x7FFE:0x8000]==[0xA7]*2
    assert bytes(m[0xC22C:0xC231])==(second if c0==0 else first) and bytes(m[0xC23C:0xC241])==(first if c0==0 else second)
    assert m[0xC250]==1 and m[0xC22B]==0 and m[0xC24F]==context^0xA7
    allowed={0xC250,0xC22B,*range(0x7FF8,0x7FFE)}
    if c0==0:allowed.update((*range(0xC22C,0xC231),*range(0xC23C,0xC241)))
    assert {p for p,v in m.writes}==allowed and len(m.writes)==(18 if c0==0 else 8)
    # Проверка одного настоящего JP HL, остановка до первой инструкции обработчика.
    wanted=list(r);wanted[24]=target;wanted[15]=refresh(r[15],1);writes_before=list(m.writes)
    s.run()
    assert r[:25]==wanted[:25] and r[26:28]==wanted[26:28] and m.writes==writes_before
    targets.add(target);cases+=1;swapped+=c0==0
 report=dict(passed=True,cases=cases,swapped_cases=swapped,physical_pairs=81,effective_targets=len(targets),exact_all_main_alternate_index_context_before_jp=True,exact_five_byte_swap=True,
  exact_three_frame_words_and_write_set=True,all_input_corner_bytes_preserved=True,all_output_points_preserved=True,
  full_handlers_separately_checked_in='PreviewClipSegmentVerification.json',direct_prefix_M1_and_R_checked=True,before_JP_M1_without_swap=24,before_JP_M1_with_swap=41,real_JP_HL_plus_one_M1_checked=True,I_IM_IFF_preserved_checked=True,handler_instructions_executed=False,full_handler_R_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipDispatchVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
