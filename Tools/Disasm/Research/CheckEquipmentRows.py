"""Четыре колонки оснащения, независимые таблицы, все пиксели и ранний RET внутри EXX."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckTextStream import reference as stream
from CheckKeyLabel import glyph
from CheckNumberOutput import expected_codes
from CheckEnvironmentRows import inc_flags
from CheckGlyphRenderer import compare_flags
from skoolkit.simutils import SP


def reference(m,top,width,height,origin=(3,3)):
 columns=[m[a] for a in (0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F)];text=list(m[0xEE57:0x10000])+[10]*1024;offset=0
 for _ in range((top&255)+1):offset=text.index(13,offset)+1
 positions=[];stream(text[offset:],list(m[0x8900:0x8A00]),0,24,width,height,0,columns,origin,24,positions=positions)
 screen=bytearray(m[0x4000:0x5B00])
 for code,x,y in positions:glyph(m,code,x,y,width,height,origin,screen)
 q=(0x988E+top)&65535;p=(0x9592+2*top)&65535;t=(0x95F0+2*top)&65535;c=(0x9400+4*top)&65535
 bc=(2*top)&65535;altbc=(4*top)&65535;count=0;cf=0x44;y=24;x=0;trace=[]
 def result(a,f,swapped=False):
  main=(altbc,t,c) if swapped else (bc,p,q);other=(bc,p,q) if swapped else (altbc,c,t)
  return dict(af=(a,f),main=main,alternate=other,counter=(count,cf),x=x,y=y,screen=screen,trace=trace,swapped=swapped)
 def number(entry,value):
  nonlocal x,bc
  codes=expected_codes(entry,value,0)
  register_values=[]
  if entry==0xBC01 and value>=10000:
   remainder=value%10000;register_values=[remainder]*(1+4-len(str(remainder)))
   register_values += [max(10,10**power) for power in range(len(str(remainder))-1,-1,-1)]
  else:register_values=[max(10,10**power) for power in range(len(codes)-1,-1,-1)]
  assert len(register_values)==len(codes)
  for index,code in enumerate(codes):
   # Расчёт BC глифа, старшая пятизначная цифра и дополнение сохраняют остаток, ядро оставляет делитель.
   bc=register_values[index];x,a,f=glyph(m,code,x,y,width,height,origin,screen)
   if not f&1:return a,f
  return a,f
 for _ in range(512):
  x=columns[0];cf=inc_flags(count);count=(count+1)&255;value=m[q];q=(q+1)&65535
  if value==128:return result(128,0x42)
  quantity=value if value<128 else value^255;trace.append(('quantity',quantity))
  if quantity:a,f=number(0xBCAB,quantity)
  else:x,a,f=glyph(m,45,x,y,width,height,origin,screen)
  if not f&1 and a in (1,2):return result(0,0x42)
  x=columns[1];price=m[p]+256*m[(p+1)&65535];p=(p+2)&65535;trace.append(('price',price));a,f=number(0xBC01,price)
  if not f&1 and a in (1,2):return result(0,0x42)
  x=(columns[2]+4)&255;threshold=m[t];weight=m[(t+1)&65535];t=(t+2)&65535
  if m[0x72DD]>=threshold:trace.append(('weight',weight));a,f=number(0xBCAB,weight)
  else:trace.append(('weight_dash',));x,a,f=glyph(m,45,x,y,width,height,origin,screen)
  if not f&1 and a in (1,2):return result(0,0x42)
  x=(columns[3]+4)&255;ship=m[0x9849];mark=ship<128 and all(ship!=m[(c+j)&65535] for j in range(4));trace.append(('mark',mark))
  if mark:
   x,a,f=glyph(m,0xFB,x,y,width,height,origin,screen)
   if not f&1 and a in (1,2):return result(0,0x42,True)
  c=(c+4)&65535;altbc=4;bc=(bc&0xFF00)|height;next_y=(y+8)&255
  if next_y>=height:return result(next_y,compare_flags(next_y,height))
  y=next_y
 raise AssertionError('equipment_rows_reference_limit')


def main():
 _,_,base=make_context();counts=collections.Counter();paths=collections.Counter()
 def prepare(top,width,height,origin):
  f=Fixture(base);m=f.memory;r=f.sim.registers;r[6:8]=[top>>8,top&255]
  for a,v in ((0xAEB3,width),(0xAEAB,height),(0xAEBB,origin[0]&255),(0xAEBF,(origin[0]>>8)&255),(0xAEC7,origin[1]&255),(0xAECB,(origin[1]>>8)&255),(0xBD26,0),(0xBD73,116),(0xBD7E,134),(0xBD89,156),(0xBD94,174),(0x72DD,8)):m[a]=v
  return f
 def check(top=0,width=188,height=192,origin=(3,3),quantity=None,price=1,threshold=1,weight=1,ship=0,restriction=(1,2,3,4),synthetic=False):
  f=prepare(top,width,height,origin);m=f.memory;r=f.sim.registers;m[0x9849]=ship
  if synthetic:
   # Создание ограниченного читаемого CR-текста, его поиск остаётся настоящим.
   put(m,0xEE57,bytes([13])*257+b'A\rB\n')
   q=(0x988E+top)&65535;p=(0x9592+2*top)&65535;t=(0x95F0+2*top)&65535;c=(0x9400+4*top)&65535
   put(m,q,(quantity,128));put(m,p,price.to_bytes(2,'little'));put(m,t,(threshold,weight));put(m,c,restriction)
  expected=reference(m,top,width,height,origin)
  def observe(f,pc):
   sp=r[SP]
   if pc==0x726C:
    # Проверка FEquipmentRowsFrame после шести PUSH, до вложенного вызова печати имён.
    words=[m[sp+j]+256*m[sp+j+1] for j in range(0,14,2)]
    assert sp==0x7FF2 and words==[top,0x988E,0x95F0,0x9400,(ship<<8)|f.initial[1],0x9592,0x3FFF]
    counts['physical_setup_frames']+=1
   if pc==0x7305:
    # Проверка FEquipmentMarkFrame с сохранённым указателем четырёх типов и внешним возвратом.
    assert sp==0x7FFC and m[sp]+256*m[sp+1]==r[6]*256+r[7] and m[sp+2:sp+4]==[255,63]
    counts['physical_marker_frames']+=1
  f.run(0x724C,observe)
  values=tuple(r[2:8]);words=tuple(byte for word in expected['main'] for byte in (word>>8,word&255));other=tuple(byte for word in expected['alternate'] for byte in (word>>8,word&255))
  assert tuple(r[:2])==expected['af'] and values==words and tuple(r[18:24])==other,(top,quantity,width,height,origin,r[:8],r[18:24],expected['af'],words,other)
  assert tuple(r[16:18])==expected['counter'] and (m[0x6320],m[0x6321])==(expected['x'],expected['y'])
  assert bytes(m[0x4000:0x5B00])==bytes(expected['screen']) and r[8:12]==f.initial[8:12] and r[SP]==0x8000
  assert m[0x7306]==m[0x9849] and not f.trace.writes and f.wakes==0
  assert r[14]==f.initial[14] and r[26:28]==f.initial[26:28]
  for phase,*_ in expected['trace']:paths[phase]+=1
  counts['swapped_register_early_return' if expected['swapped'] else 'ordinary_register_return']+=1
 # Проверка исходных тридцати смещений, полного и ограниченных окон.
 for top in range(30):
  for width in (92,156,188):
   for height in (8,24,29,40,192):check(top,width,height)
 # Проверка всех кодов количества, нуля, инверсного кодирования и маркера 80.
 for code in range(256):
  for width in (116,134,160,188):check(quantity=code,width=width,synthetic=True)
 # Проверка полного байта типа корабля, включая все отрицательные значения и четыре позиции совпадения.
 for ship in range(256):check(quantity=1,ship=ship,synthetic=True)
 for position in range(4):
  restriction=[1,2,3,4];restriction[position]=0;check(quantity=1,restriction=restriction,synthetic=True)
 # Проверка границ порога, байтов веса и десятичных границ цен.
 for threshold in (0,7,8,9,255):
  for weight in (0,1,9,10,99,100,127,255):check(quantity=1,threshold=threshold,weight=weight,synthetic=True)
 for price in (0,1,9,10,99,100,999,1000,9999,10000,65535):check(quantity=1,price=price,synthetic=True)
 # Проверка полного слова смещения, имена используют только младший байт, четыре таблицы используют всё слово.
 for top in (30,255,256,257,65535):check(top,quantity=1,synthetic=True)
 # Проверка особого выхода внутри EXX, первые колонки невидимы слева, только маркер достигает нижней границы.
 check(quantity=1,origin=(-170,161),synthetic=True)
 # Проверка физического отказа первой, второй и третьей колонки при невидимых предшествующих глифах.
 for ox in (3,-130,-150):check(quantity=1,origin=(ox,161),synthetic=True)
 assert counts['swapped_register_early_return']>0
 report=dict(passed=True,cases_by_path=dict(counts),field_phases=dict(paths),all_quantity_codes=True,all_ship_codes=True,
  exact_main_alternate_registers_and_counter=True,independent_all_bitmap_and_numeric_status_reference=True,
  sentinel_counted_before_test=True,early_marker_return_leaves_exx_swapped=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentRowsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
