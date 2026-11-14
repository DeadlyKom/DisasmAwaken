"""Четыре пересечения D3D, полные и кэшированные входы, реальные произведение и деление.

Документация: ../../../Docs/PreviewClipIntersections.md#r-полного-и-кэшированного-пересечения
"""
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
from PackedRefreshTrace import PackedRefreshTrace
from CheckPreviewClipBounds import reference_patch
from collections import Counter
ITEMS=((0,0xE664,0xC2DC,0xC2DE),(1,0xE6AF,0xC2EA,0xC2EC),(2,0xE6FA,0xC2EE,0xC2FA),(3,0xE757,0xC2FC,0xC2FE))


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xE664);cases=full=wrapped=extremes=0;offsets=(0,2,126,127,254,255)
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 code=[i for region in flow if region['name']=='D3D' for i in region['instructions']
       if 0xE5E8<=i['address']<0xE7B4 or 0xE869<=i['address']<0xEAB6]
 original={row['address']:bytes.fromhex(row['hex']) for row in code}
 for address,instruction in original.items():assert raw[address-0xC000:address-0xC000+len(instruction)]==instruction
 refresh=PackedRefreshTrace(code,0);entries=Counter();refresh_seeds={};m1_bounds={};total_m1=0
 for profile in range(256):
  min_col=profile;min_row=(profile*37)&255;max_col=255-profile;max_row=(profile*53)&255
  # Настройка исходным E011, H и D строки, L и E колонки, порядок пределов не исправляется.
  m.recording=False;s.registers[:]=initial;r=s.registers;r[6]=max_row;r[7]=max_col;r[4]=min_row;r[5]=min_col;s.run(start=0xE011,stop=0x3FFF)
  # Обновление ожидаемых операндов по независимой формуле настоящей настройки.
  patches=reference_patch(max_row,max_col,min_row,min_col)
  for address,instruction in original.items():
   expected_code=bytes(patches.get(address+offset,value) for offset,value in enumerate(instruction))
   assert bytes(m[address:address+len(instruction)])==expected_code
   refresh.instructions[address]=expected_code
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
     s.registers[:]=initial;r=s.registers;r[1]=0x5C|(index&1);root=entry+3 if cached else entry
     serial=entries[root];entries[root]+=1;r[14]=serial&255;r[15]=(serial*73)&255;r[26]=serial&1;r[27]=serial%3
     system=(r[14],r[26],r[27]);refresh_seeds.setdefault(root,set()).add(r[15]);refresh.initial_r=r[15]
     refresh.m1=refresh.steps=0;refresh.prefix_counts.clear();r[24]=root;multiplies=divisions=0;projection_m1=producer_m1=0
     m.recording=True;m.writes=[]
     for _ in range(1024):
      if r[24]==0x3FFF:break
      multiplies+=r[24]==0xE869;divisions+=r[24]==0xEA01
      refresh.before(m,r[24],r[15])
      if r[24]<0xE664:producer_m1+=refresh.increment
      elif r[24]<0xE7B4:projection_m1+=refresh.increment
      s.run();refresh.after(r[15])
     else:raise AssertionError(('intersection instruction limit',kind,index,cached))
     refresh.finish(r[15]);assert multiplies==int(not cached) and divisions==1
     # Расчёт собственного пути из независимой итоговой координаты до байтового насыщения.
     own=31 if not negative and coordinate>>8 else 29
     if kind>=2:own=28 if negative else 32 if normal else 31
     assert projection_m1==own+int(not cached) and producer_m1==17*int(not cached)
     assert (r[14],r[26],r[27])==system
     bounds=m1_bounds.setdefault(hex(root),[refresh.m1,refresh.m1]);bounds[0]=min(bounds[0],refresh.m1);bounds[1]=max(bounds[1],refresh.m1)
     total_m1+=refresh.m1
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
 assert all(values==set(range(256)) for values in refresh_seeds.values()) and len(entries)==8
 report.update(full_M1_and_each_R_step_checked=True,all_256_R_values_per_entry=True,
  R_bit7_and_I_IM_IFF_preserved=True,original_opcodes_with_independently_configured_operands_checked=True,
  exactly_one_division_and_expected_multiply_per_call=True,entries=dict(entries),
  independent_own_projection_M1_checked=True,FromProduct_own_M1_horizontal=[29,31],
  FromProduct_own_M1_vertical=[28,31,32],full_entry_setup_extra_M1_without_multiply=18,
  full_M1_bounds_by_entry=m1_bounds,total_M1=total_m1,
  independent_whole_intersection_M1_oracle=False,R_full_joint_input_product=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipIntersectionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
