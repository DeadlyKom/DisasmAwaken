"""Четыре пересечения D3D, полные и кэшированные входы, реальные произведение и деление."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewFaceProductOracle import product,signed
from CheckSignedDivision import expected as divide
from CheckSignedMultiply import sbc16_flags
from PreviewEdgeRasterOracle import column_context
ITEMS=((0,0xE664,0xC2DC,0xC2DE),(1,0xE6AF,0xC2EA,0xC2EC),(2,0xE6FA,0xC2EE,0xC2FA),(3,0xE757,0xC2FC,0xC2FE))


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xE664);cases=full=wrapped=extremes=0;offsets=(0,2,126,127,254,255)
 for profile in range(256):
  min_col=profile;min_row=(profile*37)&255;max_col=255-profile;max_row=(profile*53)&255
  # Настройка исходным E011, H и D строки, L и E колонки, порядок пределов не исправляется.
  m.recording=False;s.registers[:]=initial;r=s.registers;r[6]=max_row;r[7]=max_col;r[4]=min_row;r[5]=min_col;s.run(start=0xE011,stop=0x3FFF)
  for kind,entry,low_addr,high_addr in ITEMS:
   boundary=(min_row,max_row,min_col,max_col)[kind]
   fixtures=[tuple(rng.randrange(-600,601)&65535 for _ in range(4)) for _ in range(128)]
   fixtures += [(0x8000 if kind<3 else 0x80FF,511 if kind==1 else 256,0 if kind<2 else 1000,1000 if kind<2 else 0),(0,0,1,1),(0,0,65535,65535),(1,191,255,192),(255,256,0,257),(256,511,255,510)]
   for index,(c0,r0,c1,r1) in enumerate(fixtures):
    a=((r0-boundary)&65535) if kind<2 else ((r0-r1)&65535)
    b=((c0-c1)&65535) if kind<2 else ((c0-boundary)&65535)
    denword=((r1-r0)&65535) if kind<2 else ((c1-c0)&65535)
    if not denword:continue
    multiplied=product(a,b,initial_bc=boundary if kind<2 else r1);number=multiplied['result'];number=number-(1<<32) if number&(1<<31) else number
    unsigned=~(number&0xFFFFFFFF)&0xFFFFFFFF if number<0 else number;denominator=signed(denword)
    if unsigned>=abs(denominator)*65536:continue
    denominator_flags=sbc16_flags(r1 if kind<2 else c1,r0 if kind<2 else c0,0);origin=c0 if kind<2 else r0
    first=c0.to_bytes(2,'little')+r0.to_bytes(2,'little')+b'\xA7';second=c1.to_bytes(2,'little')+r1.to_bytes(2,'little')+b'\x5A'
    for cached in (False,True):
     cursor=offsets[index%6];pre_flags=(0x5C|(index&1)) if cached else multiplied['af'][1]
     bc_before=0x36C9 if cached else multiplied['bc'];ix_before=0x2468 if cached else multiplied['ix']
     quotient,_,alt_flags,bc,_,ix=divide(number,denominator,denominator_flags&1,pre_flags&1,bc_before)
     coordinate=(quotient+origin)&65535;negative=bool(coordinate&32768);low=coordinate&255
     if kind<2:
      projected=min_col if negative else max_col if coordinate>>8 else low;pair=(projected,boundary);carry=0;de=origin if negative else (origin&0xFF00)|projected
     else:
      normal=not negative and low<192;projected=low if normal else min_row if negative else max_row;pair=(boundary,projected);carry=int(normal);de=(projected<<8)|(origin&255) if normal else origin
      wrapped+=normal and coordinate>=256
     m.recording=False;m[0xC22C:0xC231]=first;m[0xC23C:0xC241]=second;m[0xC22B]=cursor;m[0xC7FF:0xC901]=[0xA7]*258
     m[0xC2DC:0xC300]=[0xA7]*36
     if cached:
      value=multiplied['result'];m[low_addr:low_addr+2]=[value&255,(value>>8)&255];m[high_addr:high_addr+2]=[(value>>16)&255,value>>24]
     s.registers[:]=initial;r=s.registers;r[1]=0x5C|(index&1);m.recording=True;m.writes=[];s.run(start=entry+3 if cached else entry,stop=0x3FFF)
     expected=bytearray([0xA7]*256);expected[cursor]=pair[0];expected[(cursor+1)&255]=pair[1];next_cursor=(cursor+2)&255
     assert bytes(m[0xC800:0xC900])==expected and m[0xC7FF]==m[0xC900]==0xA7,(profile,kind,index,cached,pair,coordinate)
     assert tuple(r[:8])==(next_cursor,column_context(next_cursor,1,carry),bc>>8,bc&255,de>>8,de&255,0xC8,next_cursor)
     assert r[8]*256+r[9]==(ix_before&0xFF00)|(ix&255) and tuple(r[16:18])==(quotient&255,alt_flags)
     assert r[10:12]==initial[10:12] and r[12]==0x8000 and r[18:24]==initial[18:24]
     assert bytes(m[0xC22C:0xC231])==first and bytes(m[0xC23C:0xC241])==second and m[0xC22B]==next_cursor
     value=multiplied['result'];assert m[low_addr]+256*m[low_addr+1]+65536*(m[high_addr]+256*m[high_addr+1])==value
     allowed={0xC22B,0xC800+cursor,0xC800+((cursor+1)&255),*range(0x7FFC if cached else 0x7FF8,0x7FFE)}
     if not cached:allowed.update((low_addr,low_addr+1,high_addr,high_addr+1))
     assert {p for p,v in m.writes}==allowed and len(m.writes)==(5 if cached else 15)
     cases+=1;full+=not cached;extremes+=multiplied['extreme_multiplier_lost']
 report=dict(passed=True,cases=cases,full_entry_cases=full,cached_entry_cases=cases-full,positive_high_row_low_byte_preserved_cases=wrapped,propagated_second_8000_cases=extremes,configured_profiles=256,real_configurer_multiply_and_division=True,zero_denominator_and_quotient_overflow_excluded=True,unordered_limits_preserved=True,all_six_cursor_positions=list(offsets),exact_main_alternate_and_index_context=True,entire_output_page_and_guard_bytes_checked=True,exact_stack_and_cache_write_addresses_and_count=True,input_points_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipIntersectionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
