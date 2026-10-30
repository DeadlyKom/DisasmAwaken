"""Три самостоятельные подготовки дуги, исходные табличные помощники и побочная запись LeftMask."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckWorldSignature import logical_flags


def neg_flags(value):
 result=(-value)&255
 return (result&0xA8)|(0x40 if not result else 0)|(0x10 if value&15 else 0)|(4 if value==128 else 0)|2|int(value!=0)


def main(configured=False):
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 counts={0xE278:0,0xE248:0,0xE260:0,0xE208:0,0xE299:0}
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
    memory[0xDFB8]=0xA7;sim.registers[:]=initial;sim.run(start=entry,stop=0x3FFF);r=sim.registers
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
 report=dict(passed=True,cases=sum(counts.values()),cases_by_entry={format(k,'04X'):v for k,v in counts.items()},
  configured_by_original_D0C3=configured,setup_profiles=256 if configured else 0,
  method='five_original_arc_preparations_all_radius_bytes_and_offsets_actual_edge_helpers_flags_and_alternate_registers',
  right_preparation_LeftMask_side_effect_checked=True,screen_tables_from_original_builder=True,
  full_arc_raster_algorithm_proved=False,calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/('Tools/Disasm/Reports/ConfiguredArcPreparationVerification.json' if configured else 'Tools/Disasm/Reports/ArcPreparationVerification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main('--configured' in sys.argv)
