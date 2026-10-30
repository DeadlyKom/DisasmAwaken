"""Физические изменения двух пятибайтовых списков, исходные поиски и точные направления LDIR/LDDR."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace
from CheckMapViewCenter import reference as center


def main():
 _,_,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);counts=dict(toggle_a=0,insert_b=0,delete_b=0,clear_b=0,seek_b=0,cycle_a=0,center_key=0);shifted=0
 def put(address,data):
  for i,b in enumerate(data):m[address+i]=b
 def fixture(a,b,selected,cursor):
  m.out7ffd(0x10);m[0x6306]=0x10;m[0x78D7]=0xA7;put(0x990A,b''.join(a)+bytes([0x80]));put(0x993D,b''.join(b)+bytes([0x80]));put(0x9844,selected);put(0x6309,cursor.to_bytes(2,'little'));put(0x7FFE,[255,63]);s.registers[:]=initial
 def run(entry):
  r=s.registers;r[PC]=entry
  for _ in range(10000):
   if r[PC] in (0x7B9B,0x7C4A,0x7D14,0x3FFF):return r[PC]
   s.run()
  raise AssertionError(('instruction_limit',hex(entry),hex(r[PC])))
 def assert_common(expected_a,expected_b,pending=1):
  assert bytes(m[0x990A:0x993D])==b''.join(expected_a)+bytes([0x80]) and bytes(m[0x993D:0x9970])==b''.join(expected_b)+bytes([0x80])
  assert m[0x78D7]==pending and m[0x6306]==0x10 and s.registers[8:12]==initial[8:12] and s.registers[18:24]==initial[18:24]
 empty=[bytes([255,17+i,33+i,49+i,65+i]) for i in range(10)];filled=[bytes([i+1,18+i,34+i,50+i,66+i]) for i in range(10)];selected=bytes([0x34,0x12,0x78,0x56,0x9A])
 # Проверка добавления A в первую пустоту и удаления совпадения, пятый байт при поиске намеренно различается.
 for position in range(11):
  for variant in range(256):
   rows=filled.copy();expected=rows.copy();key=selected[:4]+bytes([variant])
   if position<10:rows[position]=empty[position];expected=rows.copy();expected[position]=key
   fixture(rows,empty,key,0x993D);stop=run(0x7B61);assert stop==(0x7B9B if position<10 else 0x3FFF);assert_common(expected,empty);counts['toggle_a']+=1
   if position<10:
    rows=filled.copy();rows[position]=key;expected=rows.copy();expected[position]=bytes([255])+key[1:]
    fixture(rows,empty,key[:4]+bytes([variant^255]),0x993D);assert run(0x7B61)==0x7B9B;assert_common(expected,empty);counts['toggle_a']+=1
 # Проверка всех схем пустот B и каждого курсора, разнесённая пустота сдвигает начиная с текущей записи.
 for mask in range(1024):
  rows=[empty[i] if mask&(1<<i) else filled[i] for i in range(10)]
  for cursor in range(10):
   expected=rows.copy();target=None;was_shifted=False
   if rows[cursor][0]==255:target=cursor
   elif cursor+1<10:
    if rows[cursor+1][0]==255:target=cursor+1
    else:
     hole=next((i for i in range(cursor+2,10) if rows[i][0]==255),None)
     if hole is not None:expected[cursor+1:hole+1]=rows[cursor:hole];target=cursor;was_shifted=True
   if target is not None:expected[target]=selected
   fixture(filled,rows,selected,0x993D+5*cursor);stop=run(0x7BC0);assert stop==(0x7C4A if target is not None else 0x3FFF),(mask,cursor,stop)
   assert_common(filled,expected)
   assert m[0x6309]+256*m[0x630A]==0x993D+5*(cursor if target is None else target),(mask,cursor,target,m[0x6309:0x630B])
   assert s.registers[SP]==0x7FFE if target is not None else s.registers[SP]==0x8000
   shifted+=was_shifted;counts['insert_b']+=1
 # Проверка удаления B с сохранением физических пустот и байтов уже освобождённой последней записи.
 for position in range(10):
  for mask in range(1024):
   rows=[empty[i] if mask&(1<<i) else filled[i] for i in range(10)];rows[position]=selected;expected=rows.copy()
   expected[position:9]=rows[position+1:];expected[9]=bytes([255])+rows[9][1:]
   fixture(filled,rows,selected,0x993D+5*position);assert run(0x7BC0)==0x7C4A;assert_common(filled,expected);counts['delete_b']+=1
 # Проверка очистки только первого байта каждой записи, остальных четырёх байтов и курсора.
 for mask in range(1024):
  rows=[empty[i] if mask&(1<<i) else filled[i] for i in range(10)];expected=[bytes([255])+p[1:] for p in rows]
  fixture(filled,rows,selected,0x993D+45);assert run(0x7C64)==0x7C4A;assert_common(filled,expected);assert m[0x6309:0x630B]==[0x3D,0x99];counts['clear_b']+=1
 # Проверка установки курсора на первую совпавшую запись B без изменения списков, Variant не является ключом поиска.
 for position in range(11):
  for variant in range(256):
   rows=filled.copy();key=selected[:4]+bytes([variant])
   if position<10:rows[position]=key
   fixture(filled,rows,key[:4]+bytes([variant^255]),0x993D+45);stop=run(0x7D34);assert stop==(0x7B9B if position<10 else 0x3FFF);assert_common(filled,rows)
   assert m[0x6309]+256*m[0x630A]==0x993D+5*(position if position<10 else 9);counts['seek_b']+=1
 # Проверка циклического выбора A, пустота в первой записи запрещает действие даже при последующих занятых.
 for mask in range(1024):
  rows=[empty[i] if mask&(1<<i) else filled[i] for i in range(10)]
  for cursor in range(10):
   fixture(rows,empty,selected,0x993D);put(0x7C99,(0x990A+5*cursor).to_bytes(2,'little'));stop=run(0x7C8E)
   if rows[0][0]==255:assert stop==0x3FFF and m[0x7C99]+256*m[0x7C9A]==0x990A+5*cursor
   else:
    target=next((i for i in range(cursor+1,10) if rows[i][0]!=255),0);key=rows[target]
    assert stop==0x7D14 and s.registers[D]*256+s.registers[E]==int.from_bytes(key[:2],'little') and s.registers[H]*256+s.registers[L]==int.from_bytes(key[2:4],'little')
    assert m[0x7C99]+256*m[0x7C9A]==0x990A+5*target
   assert_common(rows,empty);counts['cycle_a']+=1
 # Проверка общего центрирования до общего рисунка, текущий Variant намеренно отличается от сохранённого в A.
 for first in (0,0x7F7F,0x0038,0x4B38):
  for size in range(256):
   for matched in (False,True):
    second=(size*257)^0xA75D;key=first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([size]);rows=filled.copy()
    if matched:rows[0]=key
    fixture(rows,empty,selected,0x993D);put(0x6304,[size,255-size]);put(0x983F,key[:4]+bytes([size^255]));r=s.registers;r[D],r[E]=first>>8,first&255;r[H],r[L]=second>>8,second&255
    entry=0x7D08 if size&1 else 0x7D14;r[PC]=entry
    # Продолжение через 7D14 разрешено только в этой проверке, в циклическом выборе это граница наблюдения.
    for _ in range(3000):
     if r[PC]==0x7B9B:break
     s.run()
    else:raise AssertionError('Центрирование не достигло хвоста рисунка')
    x=((first&255)<<8)|(second&255);y=(first&0xFF00)|(second>>8);cx,cy,flags=center(x,y,size,255-size)
    assert bytes(m[0x6300:0x6304])==bytes([cx&255,cy&255,cx>>8,cy>>8]) and bytes(m[0x9844:0x9849])==key[:4]+bytes([size if matched else 0])
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F],r[SP])==(((cy>>8)<<8)|(cx>>8),((cy&255)<<8)|(cx&255),0xFF00|(-((255-size)>>1)&255),0x10,flags,0x7FFE)
    assert m[0x78D7]==(1 if entry==0x7D08 else 0xA7) and m[0x6306]==0x10 and r[10:12]==initial[10:12];counts['center_key']+=1
 report=dict(passed=True,cases=counts,shifted_insert_cases=shifted,variant_ignored_by_lookup=True,all_ten_slot_hole_masks=True,insertion_immediate_hole_and_shifted_hole_have_different_target=True,first_byte_only_tombstones=True,scope='original_mutations_and_banked_lookup_until_refresh_or_secondary_order_entry',redraw_executed=False,secondary_order_executed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StoredPointEditsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
