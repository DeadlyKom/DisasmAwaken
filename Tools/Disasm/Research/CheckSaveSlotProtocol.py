"""Протокол SAVE-секторов, явные подмены 3D13 и отсутствие реальных дисковых записей."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put,payload
from skoolkit.simutils import SP,PC,I,IFF,IM


MODES=((0x7421,0x742E,0x7492,43,0x7489,0x7471,6),(0x74AA,0x74B7,0x751B,44,0x7512,0x74FF,5))


def main():
 _,_,base=make_context();manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entries={int(e['name'][4]):e for e in manifest['entries'] if e['name'].startswith('SAVE')};saved_data={row:payload(e['slot']) for row,e in entries.items()};assert all(len(data)==512 for data in saved_data.values());counts=collections.Counter()
 def prepare(mode,row,old_i=0x80):
  _,_,draw,key,hover,_,_=mode;f=Fixture(base);m=f.memory;r=f.sim.registers;p=0xF0FD+16*key;put(m,p,(0,0,12,8,6,m[p+5]));put(m,draw+1,(key,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(*draw.to_bytes(2,'little'),1,1));m[hover]=row;m[0x9E78]=0;m[0xCA20]=6;m[0x9A82]=0xA7;r[6:8]=[draw>>8,draw&255];r[4:6]=[0,key];r[8:10]=[p>>8,p&255];r[10:12]=[0x13,0x57];r[I]=old_i;r[:2]=[0,0x42]
  return f
 def execute(mode,row,old_i=0x80,final_iff=0,whole_entry=False,missing=False,last_carry=1):
  entry,selected,draw,key,hover,restore,command=mode;f=prepare(mode,row,old_i);m=f.memory;s=f.sim;r=s.registers;r[PC]=entry if whole_entry else selected
  if whole_entry:r[0]=1
  initial_i=r[I];original_iy=tuple(r[10:12]);snapshot=bytes((j*37+row*11+old_i)&255 for j in range(512));put(m,0x983B,snapshot);calls=[];saved=None;found=entries.get(row);filename=b'SAVE'+bytes([(row+48)&255])+b'   s';stack_frames=0;saved_flags=None
  for _ in range(30000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc in (0x7430,0x74C2):
    # Проверка фактических флагов LD A,I, P/V зависит также от моделируемого окна INT, протокол их не превращает в EI.
    saved_flags=r[1];assert saved_flags&1==int(command==5 and row+48>255)
   if pc!=0x3D13:s.run();continue
   number=r[3];sp=r[SP];frame=[m[sp+j]+256*m[sp+j+1] for j in range(2,12,2)];calls.append(number)
   assert sp==0x7FF4 and frame[-1]==0x3FFF
   flags=saved_flags;assert flags is not None
   expected_frame=[key,(0x3F<<8)|flags,draw,0x1357,0x3FFF] if command==6 else [0x1357,(0x3F<<8)|flags,key,0x7534,0x3FFF]
   assert frame==expected_frame,(mode,row,initial_i,frame,expected_frame);stack_frames+=1
   if number==10:
    assert len(calls)==1 and bytes(m[0x5CDD:0x5CE6])==filename and r[I]==0x3F and r[IM]==1 and r[IFF]==0 and r[10:12]==[0x5C,0x3A]
    r[2:4]=[0xA7,255 if missing else found['slot']];r[:2]=[0xE1,1]
   elif number==8:
    assert len(calls)==2 and r[0]==(255 if missing else found['slot'])
    if missing:
     counts['missing_search_continues_to_descriptor_ff']+=1;return
    descriptor=bytes.fromhex(found['raw_name_hex'])+b's'+found['parameter'].to_bytes(2,'little')+found['length'].to_bytes(2,'little')+bytes((found['sector_count'],found['first_sector'],found['first_track']))
    assert len(descriptor)==16;put(m,0x5CDD,descriptor);r[:8]=[0xE2,1,0xA1,0xB2,0xC3,0xD4,0xE5,0xF6]
   else:
    assert number==command and len(calls)==3 and r[2:8]==[2,command,found['first_track'],found['first_sector'],0x98,0x3B]
    if command==6:saved=bytes(m[0x983B:0x9A3B]);assert saved==snapshot
    else:put(m,0x983B,saved_data[row])
    # Подмена последнего DOS-возврата намеренно меняет разрешённый контекст, включая I, IM, IFF и Carry.
    r[:8]=[0xD2,2|last_carry,0xBE,0xEF,0x22,0x22,0x11,0x11];r[8:12]=[0x88,0x99,0x65,0x43];r[16:24]=list(range(0x91,0x99));r[I]=0x55;r[IM]=0;r[IFF]=final_iff
   r[PC]=m[sp]+256*m[sp+1];r[SP]=(sp+2)&65535
  else:raise AssertionError(('slot_protocol_limit',mode,row,hex(r[PC])))
  assert calls==[10,8,command] and r[SP]==0x8000 and r[I]==initial_i and r[IM]==2 and r[IFF]==final_iff
  assert r[:2]==[row,0x44] and r[2:6]==[0xBE,0xEF,0,key] and r[6:8]==([draw>>8,draw&255] if command==6 else [0x75,0x34])
  assert r[8:12]==[0x88,0x99,*original_iy] and r[16:24]==list(range(0x91,0x99))
  assert m[restore]==initial_i and bytes(m[0xF3DE:0xF3E0])==bytes((1,1)) and m[0x9A82]==0 and bytes(m[0x7530:0x7539])==filename
  expected=snapshot if command==6 else saved_data[row];assert bytes(m[0x983B:0x9A3B])==expected and len(expected)==512
  assert not f.trace.writes and f.wakes==0;counts['save_state_block' if command==6 else 'load_state_block']+=1;counts['physical_dos_frames']+=stack_frames
  if whole_entry:counts['whole_action_selection']+=1
 # Проверка всех I, двух исходов IFF последнего DOS-вызова и противоположного порядка PUSH двух процедур.
 for mode in MODES:
  for old_i in range(256):
   for final_iff in (0,1):execute(mode,0,old_i,final_iff)
  for row in range(6):
   for old_i in (0,0x3F,0x80,255):
    for final_iff in (0,1):execute(mode,row,old_i,final_iff)
   execute(mode,row,whole_entry=True)
   execute(mode,row,last_carry=0)
  # Проверка всех байтов имени до второй команды, ошибка поиска FF в исходнике не проверяется.
  for row in range(256):execute(mode,row,missing=True)
 # Проверка всех неселективных входов без подмены DOS, список уже последний, Track запрещён кэшем флагов.
 for mode in MODES:
  for selector in range(256):
   if selector==1:continue
   f=prepare(mode,0);m=f.memory;r=f.sim.registers;r[0]=selector;put(m,0x6307,(42,80));m[0xAEBF]=3;filename=bytes(m[0x7530:0x7539]);f.run(mode[0],lambda f,pc:(_ for _ in ()).throw(AssertionError('unexpected_dos')) if pc==0x3D13 else None)
   assert bytes(m[0x7530:0x7539])==filename and r[I]==0x80;counts['nonselection_without_dos']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_original_i_values=True,all_slot_filename_bytes=True,
  six_original_save_files_checked=True,read_write_blocks_exactly_512_bytes=True,load_final_hl_is_filename_digit=True,
  iff_inherited_from_dos_not_restored=True,missing_file_ff_not_guarded=True,last_dos_carry_not_checked=True,last_dos_carry_values=[0,1],
  method='original_action_instructions_with_explicit_3d13_contract_stubs_and_memory_only_sector_transfer',
  actual_trdos_executed=False,physical_disk_written=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SaveSlotProtocolVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
