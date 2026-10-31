"""Обход E171 против последовательности явных действий рёбер, включая B=0 и оборачивание C8."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from Analyze import payload
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from CheckClipGeometry import classify
from CheckPreviewClipCaseSemantics import expected
from CheckGlyphRenderer import compare_flags
from PreviewEdgeRasterOracle import column_context


def main():
 raw=payload(6);m=bytearray(65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x8CF0,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases={(c['first'],c['second']):c for c in json.loads((ROOT/'Tools/Disasm/Reports/PreviewClipDecisionPaths.json').read_text('utf-8'))['cases']}
 rng=random.Random(0xE171);counts=collections.Counter();cases_run=edges=wraps=0;lengths=(1,2,3,4,7,15,31,127,128,255,256)
 profiles=((15,23,16,24),(63,63,64,64),(127,95,128,96),(207,111,208,112),(239,175,240,176),(255,255,256,256))
 for profile in profiles:
  max_col,max_row,_,_=profile;m[0x7FFE:0x8000]=bytes((255,63));s.registers[:]=initial;r=s.registers;r[6]=max_row;r[7]=max_col;r[4]=r[5]=0
  # Настройка исходных операндов, модель не заменяет дисковые команды константами рабочего окна.
  s.run(start=0xE011,stop=0x3FFF)
  vertices=[(x,y) for x in (-256,-1,0,max_col//2,max_col,max_col+1,max_col+256) for y in (-256,-1,0,max_row//2,max_row,max_row+1,max_row+256)]
  for i,point in enumerate(vertices):
   code=classify(point,profile);m[0xC600+i*5:0xC605+i*5]=b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes((((~code&15)<<4)|code,))
  for length in lengths:
   fixtures=[[rng.randrange(len(vertices)) for _ in range(length)] for _ in range(24)]
   # Проверка длинных замкнутых внутренних контуров без специального досрочного выхода.
   fixtures.extend([[i]*length for i in (16,17,23,24,30,32)])
   for number,indices in enumerate(fixtures):
    points=[vertices[i] for i in indices];seen=cursor=0;page=bytearray([0xA7]*256);special=False;processed=0;total=0
    for j,second in enumerate(points):
     first=points[j-1];a,b=classify(first,profile),classify(second,profile)
     appended,seen,exit,_=expected(cases[a,b],first,second,seen,0,profile)
     for col,row in appended:page[cursor]=col;page[(cursor+1)&255]=row;cursor=(cursor+2)&255;total+=2
     processed=j+1
     if exit=='special':special=True;break
    start=0x8CF0+(number&1)*15;m[start:start+length]=bytes(i*5 for i in indices);m[0xC7FF:0xC901]=bytes([0xA7])*258
    m[0xC24F]=0xFF;m[0xC250]=0xFF;m[0xC22B]=0xFF;m[0x7FFE:0x8000]=bytes((255,63));s.registers[:]=initial;r=s.registers
    r[6]=start>>8;r[7]=start&255;r[2]=length&255;r[3]=number*37&255
    # Проверка реального обхода и всех помощников, включая его собственный кадр E1E2 и общую инструкцию RET E1EB.
    s.run(start=0xE171,stop=0x3FFF);r=s.registers;remaining=length-processed
    assert bytes(m[0xC800:0xC900])==page and m[0xC7FF]==m[0xC900]==0xA7,(profile,length,number,special)
    assert m[0xC22B]==cursor and m[0xC24F]==seen and m[0xC250]==0
    assert r[6]*256+r[7]==start+length and r[12]==0x8000 and r[10:12]==initial[10:12] and r[18:24]==initial[18:24]
    if special:
     flags=(column_context(remaining,-1,0)&0xC4)|(0xE1&0x28)|1
     assert (r[0],r[1],r[2]*256+r[3])==(0xE1,flags,remaining)
    else:assert (r[0],r[1],r[2],r[3])==(cursor,compare_flags(cursor,6),0,number*37&255)
    def packed(point):
     code=classify(point,profile);return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes((((~code&15)<<4)|code,))
    assert m[0xC22C:0xC231]==packed(points[processed-2]) and m[0xC23C:0xC241]==packed(points[processed-1])
    counts['special' if special else 'normal']+=1;cases_run+=1;edges+=processed;wraps+=total>=256
 report=dict(passed=True,cases=cases_run,edges_checked=edges,cases_by_return=dict(counts),output_page_wrap_cases=wraps,lengths=list(lengths),input_b_zero_means_256=True,
  all_output_page_and_guard_bytes_checked=True,exact_final_hl_bc_af_sp=True,seen_and_block_cleared_from_ff=True,real_all_d3d_arithmetic=True,
  original_input_indices_cross_page_boundary=True,independent_geometry_proof=False,nonzero_minima_checked=False,all_final_de_afprime_ix_proved=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipPolygonVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
