"""Полное действие с префиксом RepaintAndFlag, настоящий 14-байтовый кадр и вложенные CALL."""
from pathlib import Path
import collections,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckGlyphRenderer import compare_flags
from CheckActionParameterActivation import RecordedBanks
from ReferenceControlsPointRespawn import refresh


def direct_ld_addresses(operation):
 """Адреса прямого LD, слово может начинаться перед исследуемой областью."""
 compact=re.sub(r'\s','',operation)
 read=re.fullmatch(r'LD(A|HL|DE|BC|SP|IX|IY),\(#([0-9A-F]{4})\)',compact)
 write=re.fullmatch(r'LD\(#([0-9A-F]{4})\),(A|HL|DE|BC|SP|IX|IY)',compact)
 if not (read or write):return set()
 register,address=(read[1],int(read[2],16)) if read else (write[2],int(write[1],16))
 width=1 if register=='A' else 2
 return {(address+index)&65535 for index in range(width)}


def offer_literal_references():
 """Литералы адресов предложения в зарегистрированном коде, без вывода об индиректных обращениях."""
 reports=ROOT/'Tools/Disasm/Reports'
 flow=json.loads((reports/'ControlFlow.json').read_bytes())
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 entries={entry['slot']:entry for entry in manifest['entries']}
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 references=[];overlaps=[];instruction_count=0
 # Проверка чувствительности к слову на границе и отсутствия ложного совпадения соседнего байта.
 assert direct_ld_addresses('LD HL,(#98B3)')=={0x98B3,0x98B4}
 assert direct_ld_addresses('LD (#98BB),DE')=={0x98BB,0x98BC}
 assert not direct_ld_addresses('LD A,(#98B3)')&set(range(0x98B4,0x98BC))
 assert not direct_ld_addresses('LD HL,(#98B2)')&set(range(0x98B4,0x98BC))
 for region in flow:
  for row in region['instructions']:
   instruction_count+=1
   operation=row['operation']
   literals=[int(value,16) for value in re.findall(r'#([0-9A-F]{4})\b',operation)]
   # Поиск включает начало слова на байт раньше неизвестной восьмибайтовой области.
   if not any(0x98B0<=value<0x98C0 for value in literals):continue
   entry=entries[row['slot']];data=bytes.fromhex(row['hex'])
   assert row['offset']+len(data)<=entry['allocated_length']
   absolute=entry['offset']+row['offset']
   assert disk[absolute:absolute+len(data)]==data
   references.append(dict(region=region['name'],slot=row['slot'],pc=row['address'],
    operation=operation,original_hex=data.hex(),physical_disk_offset=absolute))
   # Проверка прямого LD, включая двухбайтовый доступ, пересекающий начало области.
   if direct_ld_addresses(operation)&set(range(0x98B4,0x98BC)):
    overlaps.append(references[-1])
 assert not overlaps
 assert not any(0x98B4<=int(value,16)<0x98BC for row in references
  for value in re.findall(r'#([0-9A-F]{4})\b',row['operation']))
 return dict(registered_instruction_views=instruction_count,regions=len(flow),references=references,
  reference_instruction_bytes_matched_to_original_disk=True,
  direct_byte_and_word_LD_overlap_candidates=overlaps,
  boundary_word_and_adjacent_byte_controls_passed=True,
  literals_into_unknown_words_found=False,indirect_indexed_block_or_generated_accesses_excluded=False,
  address_coincidence_is_not_cross_mode_object_identity=True,whole_game_unusedness_proved=False)


class OfferWordWatch(SliceableMemory):
 watch_enabled=False

 def watched(self,index):
  if isinstance(index,int):return (index,) if 0x98B4<=index<0x98BC else ()
  return tuple(address for address in range(*index.indices(65536)) if 0x98B4<=address<0x98BC)

 def __getitem__(self,index):
  if self.watch_enabled:
   for address in self.watched(index):self.offer_reads.append((self.cpu.registers[PC],address))
  return super().__getitem__(index)

 def __setitem__(self,index,value):
  if self.watch_enabled:
   for address in self.watched(index):self.offer_writes.append((self.cpu.registers[PC],address))
  super().__setitem__(index,value)


def check_finish_tail(banks):
 """Прямой общий хвост с настоящими POP, CloseMenuOnRow и RemoveItemDraw, без графических вызовов перед POP."""
 memory=RecordedBanks(banks=[list(b) for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF2,'HL':0xA1B2,'DE':0xC3D4,'BC':0xE5F6,'AF':0x1357,
  'IX':0xABCD,'IY':0x1357,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;costs=set();outcomes=collections.Counter()
 def execute(pointer_y,origin_y,length,found,delta):
  nonlocal cases
  keys=[i+delta if i+delta!=31 else 65535 for i in range(length)]
  if found>=0:keys[found]=31
  pointers=[0x7000+8*i for i in range(length)]
  for pointer,key in zip(pointers,keys):put(memory,pointer,[0xC9,key&255,key>>8])
  raw=[v for pointer in pointers for v in (pointer&255,pointer>>8)]+[1,1]+[0xA5]*160
  put(memory,0xE000,raw);put(memory,0x9CA6,[0,0xE0]);memory[0x6308]=pointer_y;memory[0xAEC7]=origin_y
  memory[0x9A82]=0x5A;memory[0x6F54]=0x31
  saved_bc=(((pointer_y^origin_y)&255)<<8)|0xC9
  frame=b''.join(value.to_bytes(2,'little') for value in (0x5C3A,0x2468,(pointer_y<<8)|origin_y,saved_bc,0x1357,31,0x3FFF))
  put(memory,0x7FF2,frame);sim.registers[:]=initial;r=sim.registers;r[PC]=0x6F23
  r[14]=pointer_y;r[15]=pointer_y^origin_y;r[27]=origin_y%3;before=r.copy()
  memory.writes=[];memory.recording=True;m1=0
  # Проверка полной исходной цепочки до возврата, включая фиксированные 128 итераций сдвига.
  for _ in range(4000):
   if r[PC]==0x3FFF:break
   old_r=r[15];sim.run();increment=(r[15]-old_r)&127
   assert increment in (1,2);m1+=increment
  else:raise AssertionError('Миссионный хвост не завершился')
  memory.recording=False
  matching=pointer_y//8==origin_y//8
  removed=matching and found>=0
  if not matching:
   expected_flags=compare_flags(origin_y//8,pointer_y//8);expected_m1=29;kind='different_rows'
  elif removed:
   expected_flags=0x44;expected_m1=334+21*found;kind='matching_found'
  else:
   expected_flags=0x42|int(bool(keys) and keys[-1]<31);expected_m1=50+21*length;kind='matching_missing'
  assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F],r[SP])==(0x1357,31,saved_bc>>8,pointer_y//8,255,expected_flags,0x8000)
  assert r[8:12]==[0x24,0x68,0x5C,0x3A] and r[16:24]==before[16:24]
  assert all(r[i]==before[i] for i in (14,26,27)) and r[15]==refresh(before[15],expected_m1) and m1==expected_m1,(kind,length,found,m1,expected_m1)
  assert memory[0x7FFE:0x8000]==[255,63] and memory[0x6F54]==255
  expected=raw.copy();shift_writes=[]
  if removed:
   offset=2*found;copied=raw[offset+2:offset+130];expected[offset:offset+128]=copied
   shift_writes=[(0,0x2000+offset+i,v) for i,v in enumerate(copied)]
  assert memory[0xE000:0xE000+len(raw)]==expected
  assert memory[0x9A82]==(0 if removed else 0x5A)
  assert [(bank,offset,v) for bank,offset,v in memory.writes if bank==0 and offset>=0x2000]==shift_writes
  for bank,offset,value in memory.writes:
   address=(0x4000 if bank==5 else 0x8000 if bank==2 else 0xC000)+offset
   assert bank in (0,2,5)
   assert address in (0x6F54,0x9A82) or 0x7FEE<=address<0x7FFE or removed and 0xE000+2*found<=address<0xE080+2*found,(bank,offset,value)
  cases+=1;costs.add(m1);outcomes[kind]+=1
 # Проверка всех пар байтов Y, одновременно все 65536 сохранённых AF кадра, один найденный элемент.
 for pointer_y in range(256):
  for origin_y in range(256):execute(pointer_y,origin_y,1,0,0)
 # Проверка отсутствия индекса, пустоты, первой и последней позиций на смешанных длинах.
 for length in (0,1,3,46):
  positions=(-1,) if not length else tuple(sorted({-1,0,length-1}))
  for found in positions:
   for y in (0,7,8,191,255):
    for delta in (0,128):execute(y,y,length,found,delta)
 return dict(cases=cases,outcomes=dict(outcomes),full_m1_values=sorted(costs),
  all_pointer_and_origin_y_bytes=True,all_saved_af_words=True,exact_restored_context_and_final_flags=True,
  exact_sp_plus_14_and_return_word_preserved=True,all_128_shift_writes_and_tail_checked=True,
  only_declared_memory_writes=True,exact_refresh_and_i_im_iff_preservation=True,iff_fixture=0,
  starts_at_pop_frame_after_graphics=True,graphics_before_frame_restore_executed=False,irq_executed=False,native_execution=False)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));_,_,banks=make_context();banks=[bytearray(b) for b in banks]
 entry=next(e for e in manifest['entries'] if e['slot']==5);lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 memory=OfferWordWatch(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory);memory.cpu=sim
 # Положительный контроль наблюдателя, чтение байта и слова и запись в наблюдаемый диапазон через CPU.
 put(memory,0x7000,bytes.fromhex('3A B4 98 32 B5 98 2A B6 98'));sim.registers[PC]=0x7000
 memory.offer_reads=[];memory.offer_writes=[];memory.watch_enabled=True
 for _ in range(3):sim.run()
 assert memory.offer_reads==[(0x7000,0x98B4),(0x7006,0x98B6),(0x7006,0x98B7)]
 assert memory.offer_writes==[(0x7003,0x98B5)]
 memory.offer_reads=[];memory[0x98B3:0x98B6]
 assert memory.offer_reads==[(0x7009,0x98B4),(0x7009,0x98B5)]
 memory.watch_enabled=False
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':31,'BC':0x36C9,'AF':0x0144,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 fixtures=[('accept',1,0,False,12,100,15,3,2000),('wrap_accept',1,0,False,250,10,15,15,2000),
  ('reject',1,0,False,100,10,15,3,2000),('same_key',1,0,True,12,100,15,3,2000),
  ('other_row',0,0,False,12,100,15,3,2000),
  ('complete_refresh',0,1,True,12,100,15,3,2000),('complete_refresh',1,1,True,12,100,15,3,2000)]
 for credits in (0,999,1000,65535):
  for quantity in (0,15,255):fixtures.append(('cancel',1,1,False,12,100,quantity,3,credits))
 results=[];wakeups=0;max_steps=0
 # Проверка успешного принятия, отказа, пропуска и расторжения через настоящий общий хвост.
 fixtures=[(*fixture,pointer_y) for fixture in fixtures for pointer_y in (0,100)]
 for name,row,active,same,used,capacity,quantity,required,credits,pointer_y in fixtures:
  memory.watch_enabled=False
  memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10)
  memory[0x6306]=0x10;memory[0x6548]=1;memory[0x9B16]=0x5A;put(memory,0x6307,[50,pointer_y])
  put(memory,0x8500,bytes([0x80,255])*128);put(memory,0x8600,bytes(768));memory[0x9E78]=0;put(memory,0x9CA6,[0,0xE0]);put(memory,0xE000,[0xC5,0x6F,1,1])
  put(memory,0xF0FD,[0,0,31,5,0,0]);put(memory,0xF2ED,[6,10,11,4,0,4]);put(memory,0xF2FD,[3,5,26,18,0,4])
  put(memory,0x7F36,[0,0]);put(memory,0x6FC6,[31,0]);put(memory,0xAA86,[32,0])
  current=0x4B38;offer=current if same else 0x4B39
  put(memory,0x983F,current.to_bytes(2,'little')+bytes([0xF3,0x4A]));put(memory,0x98B0,offer.to_bytes(2,'little')+bytes([0xF3,0x4A]))
  memory[0x99A3]=active;memory[0x99A4]=0x5A;memory[0x6F54]=row
  put(memory,0x9850,[used,capacity,quantity,0xC7]);put(memory,0x98BE,[required,0xB3])
  put(memory,0x984E,credits.to_bytes(2,'little'));put(memory,0x7FFE,[255,63])
  opaque=bytes((index*37+len(results)*11+1)&255 for index in range(8))
  put(memory,0x98B4,opaque)
  sim.registers[:]=initial;r=sim.registers;r[PC]=0x6E9C;trace=PortTrace(sim);sim.set_tracer(trace)
  memory.offer_reads=[];memory.offer_writes=[];memory.watch_enabled=True
  halts=0;frame=None;cancel_entry=None;scripts=0
  for steps in range(700000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc==0x6EB1:frame=bytes(memory[r[SP]:r[SP]+14])
   if pc==0x6F5D:cancel_entry=(r[H],r[D])
   if pc==0xC000 and memory.o7ffd&7==6:scripts+=1
   if memory[pc]==0x76:
    assert pc in (0xC089,0x6F3A,0x6F3B,0x6F9A,0x6F9B),hex(pc)
    r[PC]+=1;halts+=1;continue
   sim.opcodes[memory[pc]]()
  else:raise AssertionError(('instruction_limit',name,hex(r[PC]),r[SP]))
  memory.watch_enabled=False
  assert not memory.offer_reads and not memory.offer_writes,(name,memory.offer_reads,memory.offer_writes)
  assert bytes(memory[0x98B4:0x98BC])==opaque,name
  assert frame==bytes.fromhex('3a5c68244200c936c56f1f00ff3f'),(name,frame.hex())
  assert r[H]*256+r[L]==0x6FC5 and r[D:E+1]==initial[D:E+1] and r[B]==initial[B]
  assert (r[C],r[A],r[SP])==(pointer_y>>3,255,0x8000) and r[8:12]==initial[8:12]
  assert memory[0x6F54]==255 and memory.o7ffd==0x10 and memory[0x6306]==0x10
  assert r[F]==(0x44 if pointer_y==0 else compare_flags(0,pointer_y>>3))
  assert bytes(memory[0xE000:0xE002])==(bytes([1,1]) if pointer_y==0 else bytes([0xC5,0x6F]))
  if pointer_y==0:assert memory[0x9A82]==0
  expected_credits=max(0,credits-1000) if name=='cancel' else credits+1000 if name=='complete_refresh' else credits
  assert int.from_bytes(bytes(memory[0x984E:0x9850]),'little')==expected_credits
  if name in ('accept','wrap_accept'):
   assert (memory[0x99A3],memory[0x99A4],memory[0x9850],memory[0x9852],memory[0x9853])==(1,0,(used+required)&255,(quantity+required)&255,10),(name,[memory[x] for x in (0x99A3,0x99A4,0x9850,0x9852,0x9853)],scripts)
  elif name=='cancel':
   high_left,high_right=cancel_entry;expected=0 if high_left*256+quantity<high_right*256+required else (quantity-required)&255
   assert memory[0x99A3]==0 and memory[0x9852]==expected and scripts==1
  elif name=='complete_refresh':assert memory[0x99A3]==0 and memory[0x99A4]==1 and memory[0x9852]==quantity-required and scripts==1
  elif name=='reject':assert memory[0x99A3]==0 and memory[0x9850]==used and memory[0x9852]==quantity
  else:assert memory[0x99A3]==active and memory[0x9852]==quantity
  results.append(dict(branch=name,pointer_y=pointer_y,credits=credits,quantity=quantity,final_quantity=memory[0x9852],halt_wakeups=halts))
  wakeups+=halts;max_steps=max(max_steps,steps)
 report=dict(passed=True,finish_tail=check_finish_tail(banks),cases=len(fixtures),results=results,max_instructions=max_steps,halt_fixture_wakeups=wakeups,
  method='original_complete_mission_action_with_last_draw_handler_no_geometry_action_real_drawers_LANG_and_close',
  entry='6E9C',prefix_RepaintAndFlag_executed=True,close_menu_row_match_and_mismatch=True,frame_bytes=14,
  opaque_offer_words=dict(start=0x98B4,end_exclusive=0x98BC,read_count=0,write_count=0,
                         distinct_test_patterns=len(results),scalar_and_slice_accesses_watched=True,
                         watcher_positive_cpu_and_slice_control_passed=True,
                         whole_game_unusedness_proved=False),
  offer_literal_reference_audit=offer_literal_references(),
  model_rom_sha256=hashlib.sha256(bytes(memory.roms[1])).hexdigest(),emulator_rom_match_verified=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionActionFlowVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
