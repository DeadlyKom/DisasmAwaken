"""Три самостоятельные подготовки дуги, исходные табличные помощники и побочная запись LeftMask."""
from pathlib import Path
import collections,json,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,R,I,IM,IFF
from ReferenceControlsPointRespawn import refresh
from CheckRowHighlight import make_context
from CheckWorldSignature import logical_flags


def neg_flags(value):
 result=(-value)&255
 return (result&0xA8)|(0x40 if not result else 0)|(0x10 if value&15 else 0)|(4 if value==128 else 0)|2|int(value!=0)


def main(configured=False):
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,7):
  row=next(x for x in manifest['entries'] if x['slot']==slot)
  assert (ROOT/(row['path']+'.sectors.bin')).read_bytes()==disk[row['offset']:row['offset']+row['allocated_length']]
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 counts={0xE278:0,0xE248:0,0xE260:0,0xE208:0,0xE299:0}
 baseline=bytes(memory);refresh_costs=collections.Counter();initial_R_codes={e:set() for e in counts};witnesses=[];phase_witnesses=[]
 def run_refresh(entry,cost,initial_r,witness=False,phase=False):
  sim.registers[R]=initial_r;sim.registers[I]=initial_r
  sim.registers[IM]=initial_r%3;sim.registers[IFF]=initial_r&1
  preserved_special=tuple(sim.registers[i] for i in (I,IM,IFF))
  if witness:
   sim.registers[PC]=entry;m1=0
   # Проверка абсолютного счёта M1 составного вызова с настоящими помощниками.
   for _ in range(256):
    pc=sim.registers[PC]
    if pc==0x3FFF:break
    opcode=memory[pc];assert opcode not in (0xDD,0xFD)
    assert memory[pc:pc+2] not in (b'\xed\x4f',b'\xed\x5f')
    m1+=2 if opcode in (0xCB,0xED) else 1
    sim.opcodes[opcode]()
    assert sim.registers[R]==refresh(initial_r,m1)
   else:raise AssertionError(('arc_preparation_instruction_limit',entry))
   assert m1==cost,(entry,m1,cost)
   (phase_witnesses if phase else witnesses).append(dict(entry=entry,initial_R=initial_r,final_R=sim.registers[R],observed_M1=m1))
  else:sim.run(start=entry,stop=0x3FFF)
  assert sim.registers[R]==refresh(initial_r,cost),(entry,cost)
  assert tuple(sim.registers[i] for i in (I,IM,IFF))==preserved_special
  if not phase:
   refresh_costs[entry,cost]+=1;initial_R_codes[entry].add(initial_r)
 def preparation_M1(entry,radius,offset_x,origin,center):
  if entry in (0xE278,0xE299):return 12
  if entry==0xE248:return 47+4*((origin+offset_x-radius)&7)
  if entry==0xE260:return 82-4*((origin+radius-offset_x)&7)
  assert entry==0xE208
  return 98+4*(((center-radius)&7)-((center+radius)&7))
 # Проверка всех радиусов и кодов квадранта, а также всех пар радиуса и горизонтального смещения для обоих краёв.
 for radius in range(256):
  if configured:
   # Настройка крайних колонок настоящим D0C3 перед независимыми входами помощников.
   sim.registers[:]=initial;r=sim.registers;r[H],r[L]=(radius*37)&255,radius;r[D]=r[E]=0
   sim.run(start=0xD0C3,stop=0x3FFF)
  left_column=memory[0xF000] if configured else 1
  right_column=memory[0xF000+radius] if configured else 30
  for variable in range(256):
   offset_x=variable;offset_y=(radius*17+variable*13)&255;quadrant=variable;row=(radius*31+variable)&255;origin=(radius+variable*7)&255
   center=(radius*3+variable*11)&255;start_y=(radius*7+variable*19)&255
   fields=bytes([quadrant,radius,offset_y,offset_x,row,center,start_y]);memory[0xDFAD:0xDFB4]=fields;memory[0xDFBF]=origin
   for entry in counts:
    memory[0xDFB8]=0xA7;sim.registers[:]=initial
    cost=preparation_M1(entry,radius,offset_x,origin,center)
    run_refresh(entry,cost,(radius+variable)&255,radius in (0,255) and variable in (0,127));r=sim.registers
    alt_c=(-radius)&255;alt_e=0
    if entry==0xE299:
     seed=(origin+offset_x)&255;expected=(0x1357,0x247A,offset_x*256+offset_y,start_y,neg_flags(seed));left_mask=0xA7;alt_c=(-seed)&255;alt_e=start_y
    elif entry==0xE208:
     left_x=(center-radius)&255;right_x=(center+radius)&255;high=memory[0xEE00+row]
     left_low=(memory[0xEF00+row]+memory[0xF000+left_x])&255;right_low=(memory[0xEF00+row]+memory[0xF000+right_x])&255
     left_mask=128>>(left_x&7);right_mask=128>>(right_x&7)
     expected=(high*256+right_low,radius*256+left_low,left_mask*256+right_mask,left_mask,0x43 if right_x&7==7 else 0x42)
    elif entry==0xE278:
     expected=(0x1357,radius*256+quadrant,offset_x*256+offset_y,(-radius)&255,neg_flags(radius));left_mask=0xA7
    else:
     x=(origin+offset_x-radius)&255 if entry==0xE248 else (origin+radius-offset_x)&255
     high=memory[0xEE00+row];low=(memory[0xEF00+row]+memory[0xF000+x])&255;mask=128>>(x&7)
     if entry==0xE248:
      edge=(low&224)|right_column;expected=(high*256+edge,radius*256+low,mask*256+1,edge,logical_flags(edge));left_mask=0xA7
     else:
      edge=(low&224)|left_column;expected=(high*256+low,radius*256+edge,0x8000+mask,edge,logical_flags(edge));left_mask=offset_x
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F])==expected,(entry,radius,variable,list(r),expected)
    assert memory[0xDFB8]==left_mask and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:18]==initial[16:18]
    expected_alt=list(initial[18:24]);expected_alt[1]=alt_c;expected_alt[3]=alt_e
    assert r[18:24]==expected_alt and memory[0xDFAD:0xDFB4]==fields
    counts[entry]+=1
 # Дополнительные независимые фазы не меняют прежние коррелированные сценарии и их числа.
 for entry in (0xE248,0xE260):
  for k in range(8):
   for initial_r in (0,0x95):
    memory[:]=baseline;radius=10;offset_x=5;offset_y=3;row=17;center=64;start_y=12
    origin=(k-offset_x+radius)&255 if entry==0xE248 else (k-radius+offset_x)&255
    memory[0xDFAD:0xDFB4]=bytes((0,radius,offset_y,offset_x,row,center,start_y));memory[0xDFBF]=origin;memory[0xDFB8]=0xA7
    sim.registers[:]=initial;run_refresh(entry,preparation_M1(entry,radius,offset_x,origin,center),initial_r,True,True)
    phase_witnesses[-1].update(X=k,ReferenceX=origin,Radius=radius,OffsetX=offset_x,original_table_profile=True)
    r=sim.registers;low=(memory[0xEF00+row]+memory[0xF000+k])&255;mask=128>>k
    if entry==0xE248:
     expected=(memory[0xEE00+row]*256+((low&224)|30),radius*256+low,mask*256+1,0xA7)
    else:expected=(memory[0xEE00+row]*256+low,radius*256+((low&224)|1),0x8000+mask,offset_x)
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],memory[0xDFB8])==expected
    edge=expected[0]&255 if entry==0xE248 else expected[1]&255
    assert (r[A],r[F])==(edge,logical_flags(edge))
    assert r[8:12]==initial[8:12] and r[16:18]==initial[16:18]
    expected_alt=list(initial[18:24]);expected_alt[1]=(-radius)&255;expected_alt[3]=0
    assert r[18:24]==expected_alt and r[SP]==0x8000
 assert all(codes==set(range(256)) for codes in initial_R_codes.values())
 assert sum(refresh_costs.values())==sum(counts.values())
 report=dict(passed=True,cases=sum(counts.values()),cases_by_entry={format(k,'04X'):v for k,v in counts.items()},
  configured_by_original_D0C3=configured,setup_profiles=256 if configured else 0,
  method='five_original_arc_preparations_all_radius_bytes_and_offsets_actual_edge_helpers_flags_and_alternate_registers',
  right_preparation_LeftMask_side_effect_checked=True,screen_tables_from_original_builder=True,
  full_arc_raster_algorithm_proved=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False,
  refresh_verification=dict(cases=sum(counts.values()),original_disk_sha256=manifest['sha256'],
   initial_R_codes_by_entry={format(e,'04X'):sorted(c) for e,c in initial_R_codes.items()},
   cost_profiles=[dict(entry=e,M1=m1,cases=n) for (e,m1),n in sorted(refresh_costs.items())],
   witnesses=witnesses,witness_count=len(witnesses),independent_phase_witnesses=phase_witnesses,independent_phase_witness_count=len(phase_witnesses),
   original_fixture_left_X_phases=[0],original_fixture_right_X_phases=[0,2,4,6],
   phase_witnesses_use_original_table_profile=True,I_IM_IFF_preserved=True,
   independent_R_all_input_product_proved=False,every_instruction_R_checked_only_in_witnesses=True))
 report_path=ROOT/('Tools/Disasm/Reports/ConfiguredArcPreparationVerification.json' if configured else 'Tools/Disasm/Reports/ArcPreparationVerification.json')
 old=json.loads(report_path.read_bytes());assert all(report[k]==v for k,v in old.items())
 report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(passed=True,configured=configured,cases=sum(counts.values()),witnesses=len(witnesses),phase_witnesses=len(phase_witnesses)),ensure_ascii=False))


if __name__=='__main__':main('--configured' in sys.argv)
