"""Настоящий MUZ1.Stop, AY-порты, IM 1 и двухсловный CPU-вход станционного StopMusic."""
import collections,json,re
from hashlib import sha256
from zipfile import ZipFile
from CheckControlsArchivedHyperEffect import read_entry
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from skoolkit.simutils import SP,I,IFF,IM,R
from ReferenceControlsPointRespawn import refresh
from ArchivedSourceInventory import load_sources
from ArchivedStormSources import load_storm_sources,SymbolWalker
from CheckActionParameterActivation import RecordedBanks


def reference_evidence():
 # Проверка именованных входов архивного EXAS во всех действующих текстовых исходниках.
 archive_path=ROOT/'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
 digest=sha256(archive_path.read_bytes()).hexdigest()
 assert digest=='d3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
 hits=[];sources,_,_=load_sources();checked=len(sources)
 for source in sources:
  for line_number,line in enumerate(source['content'].split(b'\r'),1):
   if re.search(rb'(?<![A-Z0-9_])EXAS(?![A-Z0-9_])',line,re.I):
    hits.append(dict(member=source['member'],slot=source['slot'],line=line_number,raw_hex=line.hex()))
 # Поиск в STORM различает имена, комментарии и строки, бинарные записи не трактуются как CR-текст.
 structured=load_storm_sources();structured_hits=[];structured_records=0
 for source in structured:
  for row in source['records']:
   structured_records+=1;walker=SymbolWalker(row['data'])
   mentions=[dict(kind='definition' if item['byte_offset']==0 and 'definition' in row else 'operand_symbol',
    byte_offset=item['byte_offset']) for item in walker.walk() if item['name'].upper()=='EXAS']
   for kind,parts in (('comment',walker.comments),('string_literal',walker.literals)):
    for part in parts:
     if re.search(r'(?<![A-Z0-9_])EXAS(?![A-Z0-9_])',part['text'],re.I):
      mentions.append(dict(kind=kind,byte_offset=part['byte_offset'],text=part['text']))
   structured_hits.extend(dict(member=source['member'],slot=source['slot'],source=source['name'],
    line=row['line'],file_offset=row['file_offset'],original_record_hex=row['data'].hex(),**mention)
    for mention in mentions)
 assert len(structured)==31 and structured_records==18123 and not structured_hits
 with ZipFile(archive_path) as archive:
  _,body,_=read_entry(archive.read('awk6.trd'),b'BODYOCURa')
  _,buttons,_=read_entry(archive.read('awk6.trd'),b'OBR2    a')
  _,dispatcher,_=read_entry(archive.read('awk6.trd'),b'BODY    a')
 assert checked==129 and [(h['member'],h['slot'],h['line']) for h in hits]==[
  ('awk6.trd',45,883),('awk6.trd',46,3),('awk6.trd',46,307)]
 assert b'\r\xfeEXIT TO XAS\r\x06\x8c\x053\x06\x83EXAS\r' in buttons
 rows=body.split(b'\r');entry=rows.index(b'EXAS');sequence=rows[entry:entry+13]
 assert sequence[1:4]==[b'\x06\x8cPAGE\x06\x82PGMUZ',b'\x06\x8c\x054 #DB08',b'\x06\x8c\x05"\x06\x831']
 assert sequence[-2:]==[b'\x06\x8c\x05.\x06\x82\x03\x8c',b'\x06\x8c\x05$']
 # Старый Fire передаёт обработчику свой возврат без отдельного CALL обработчика.
 dispatch_rows=dispatcher.split(b'\r')
 assert dispatch_rows[112:114]==[b'\x06\x8c\x054 Fire',b'\x06\x8c\x053\x06\x83M1']
 assert dispatch_rows[505]==b'\x06\x8c\x05- \x05\x89'
 assert dispatch_rows[539]==b'\x06\x8c\x05.\x06\x82\x05\x89'
 assert dispatch_rows[542]==b'\x06\x8c\x053\x06\x83\x05}'
 dispatch_evidence=[dict(line=index+1,raw_hex=dispatch_rows[index].hex())
                    for index in (112,113,505,524,525,526,530,539,540,541,542)]
 # Проверка полного физического TRD, отдельно от логической длины его файлов.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 literals=[]
 for offset in range(len(disk)-1):
  if disk[offset:offset+2]!=bytes.fromhex('AA63'):continue
  owner,= [e for e in manifest['entries'] if e['offset']<=offset<e['offset']+e['allocated_length']]
  relative=offset-owner['offset']
  literals.append(dict(disk_offset=offset,slot=owner['slot'],file_offset=relative,
                       inside_logical_file=relative+2<=owner['length']))
 assert [(h['slot'],h['file_offset']) for h in literals]==[(0,0x47DE),(0,0x8D48),(9,0x42C),(9,0xB48C)]
 assert [h['slot'] for h in literals if h['inside_logical_file']]==[9]
 return dict(archive_sha256=digest,active_source_entries_checked=checked,
  structured_source_entries_checked=len(structured),structured_records_checked=structured_records,
  total_source_entries_checked=checked+len(structured),structured_exas_occurrences=structured_hits,
  structured_names_comments_and_string_literals_separated=True,
  archived_exas_occurrences=hits,archived_exas_sequence_hex=[s.hex() for s in sequence],
  archived_exit_button_jumps_to_exas=True,original_disk_sha256=sha256(disk).hexdigest(),
  archived_dispatcher_source='awk6.trd:BODY.a',archived_dispatcher_stack_lines=dispatch_evidence,
  archived_dispatcher_source_interpretation='with_balanced_child_returns_POP_HL_discards_Fire_return_to_main_loop',
  archived_dispatcher_machine_code_matched=False,archived_whole_exit_path_executed=False,
  literal_63AA_occurrences=literals,encoded_or_computed_targets_excluded=False,
  archived_call_stack_origin_proved=False,current_caller_origin_proved=False)


def word_frame_sweep(base,stack=0x7FFC,words=range(65536)):
 # Один подготовленный стенд повторно исполняет исходные StopMusic и MUZ1.Stop без перезагрузки GUI.
 f=Fixture(base,memory_type=RecordedBanks);m=f.memory;r=f.sim.registers
 expected_ports=[(0x7FFD,0x13)]+[item for reg in range(13,-1,-1)
  for item in ((0xFFFD,reg),(0xBFFD,0))]+[(0x7FFD,0x10)]
 def physical(address,value):
  assert 0x4000<=address<0xC000
  return (5 if address<0x8000 else 2,address&0x3FFF,value)
 expected_writes=[physical(stack-2,0xAF),physical(stack-1,0x63),physical(stack-4,0xC9),physical(stack-3,0x36),
  (5,0x2306,0x13),physical(stack-2,0xB2),physical(stack-1,0x63),physical(stack-2,0xC1),physical(stack-1,0x63),
  physical(stack-4,0xFD),physical(stack-3,0xBF),(5,0x2306,0x10)]
 # Младший байт первого слова не является кодом, старший не является адресом банкового порта.
 for word in words:
  m.recording=False;m.out7ffd(word&31);m[0x6306]=word&31
  put(m,stack,word.to_bytes(2,'little')+bytes((255,63)))
  r[:]=f.initial;r[SP]=stack;r[1]=word&255;r[R]=(word*73)&255
  r[I]=(word>>8)&255;r[IM]=word%3;r[IFF]=word&1
  r[10:12]=[(word^0xBEEF)>>8,(word^0xBEEF)&255]
  wanted=list(r);wanted[:8]=[0x10,0x42|(word&1),0xBF,0xFD,0,0,word>>8,word&255]
  wanted[10:12]=[0x5C,0x3A];wanted[SP]=stack+4;wanted[I]=0x3F;wanted[IM]=1;wanted[24]=0x3FFF
  wanted[R]=refresh(r[R],143)
  initial_R=r[R];f.trace.ay=list(range(16));f.trace.writes.clear()
  m.writes=[];m.recording=True
  f.sim.run(start=0x63AA,stop=0x3FFF);m.recording=False
  # Проверка полного первого слова, сохранения второго слова и точного результата процедуры.
  assert r[:8]==[0x10,0x42|(word&1),0xBF,0xFD,0,0,word>>8,word&255],word
  assert r[SP]==stack+4 and r[R]==refresh(initial_R,143)
  assert r[I]==0x3F and r[IM]==1 and r[IFF]==word&1
  assert r[8:10]==f.initial[8:10] and r[10:12]==[0x5C,0x3A] and r[16:24]==f.initial[16:24]
  assert all(r[index]==wanted[index] for index in range(len(wanted)) if index!=25),word
  assert bytes(m[stack:stack+4])==word.to_bytes(2,'little')+bytes((255,63))
  assert m.writes==expected_writes and m.o7ffd==m[0x6306]==0x10,(word,m.writes)
  assert f.trace.writes==expected_ports and f.trace.ay==[0]*14+[14,15],word
 return dict(passed=True,cases=len(words),all_HLWord_values=words==range(65536),exact_output_HL=True,
  entry_frame_four_bytes_unchanged=True,exact_all_CPU_writes=True,exact_ports_and_AY=True,
  exact_registers_except_T=True,all_initial_IY_words=words==range(65536),
  source_entry_frame_SP=stack,return_PC=0x3FFF,stack_delta=4,
  native_caller_origin_established=False,full_input_cartesian_product_checked=False,
  irq_executed=False,native_execution=False,assembly_executed=False)


def frame_alias_probes(base):
 # Положительные рамки остаются в двух фиксированных окнах, включая переход через 8000.
 fixed=[word_frame_sweep(base,stack,(0,1,0x1234,0x7FFF,0x8000,0xFFFF))
        for stack in (0x4004,0x8000,0xBFFC)]
 f=Fixture(base);m=f.memory;r=f.sim.registers
 # Если первое входное слово пересекает CurrentPage, две записи страницы меняют его до POP HL.
 put(m,0x6306,bytes.fromhex('3412FF3F'));r[:]=f.initial;r[SP]=0x6306
 f.sim.run(start=0x63AA,stop=0x3FFF)
 assert r[6:8]==[0x12,0x10] and r[SP]==0x630A and m[0x6306]==0x10
 shadow=dict(input_SP=0x6306,input_HLWord=0x1234,output_HL=0x1210)
 # До POP BC первого помощника банковое окно уже сменилось с банка 0 на музыкальный банк 3.
 f=Fixture(base);m=f.memory;r=f.sim.registers;r[:]=f.initial;r[SP]=0xD000
 put(m,0xD000,bytes.fromhex('3412FF3F'))
 f.sim.run(start=0x63AA,stop=0x63A8)
 assert m.o7ffd==0x13 and r[SP]==0xCFFC
 assert bytes(m.banks[0][0x0FFE:0x1000])==bytes.fromhex('AF63')
 assert bytes(m[0xCFFE:0xD000])!=bytes.fromhex('AF63')
 return dict(passed=True,fixed_frames=fixed,shadow_alias=shadow,
  banked_stack=dict(input_SP=0xD000,stop_PC=0x63A8,physical_return_bank_before=0,physical_return_bank_after=3),
  all_stack_addresses_exhausted=False,native_execution=False,assembly_executed=False)


def main():
 _,_,base=make_context();raw=payload(10);base[3][0x1B00:0x1B00+len(raw)]=list(raw);counts=collections.Counter();refresh_profiles=[]
 structure=(ROOT/'Includes/Structs/Include.inc').read_text('utf-8').split('struct FStopMusicReturnFrame',1)[1].split('                ends',1)[0]
 assert re.findall(r'(?m)^(\w+)\s+dw #0000\s*;',structure)==['HLWord','ReturnAddress']
 # Проверка каждой достигнутой инструкции по физическим байтам оригинального диска.
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 entries={x['slot']:x for x in manifest['entries']}
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes());original_code={}
 for group in flow:
  for row in group['instructions']:
   pc=row['address'];slot=row['slot']
   if (slot==4 and 0x639F<=pc<0x63C3) or (slot==10 and (pc==0xDB08 or 0xDB7C<=pc<0xDB8C)):
    data=bytes.fromhex(row['hex']);entry=entries[slot]
    assert disk[entry['offset']+row['offset']:entry['offset']+row['offset']+len(data)]==data
    assert pc not in original_code
    original_code[pc]=data
 def execute(flags,im,iff,hl_word,page,old_i):
  f=Fixture(base,page=page);m=f.memory;r=f.sim.registers;r[1]=flags;r[R]=flags;r[I]=old_i;r[IFF]=iff;r[IM]=im;r[SP]=0x7FFC;put(m,0x7FFC,hl_word.to_bytes(2,'little')+bytes((255,63)));f.trace.ay=list(range(16));f.trace.writes.clear();observed=[];m1=0;minimum_sp=r[SP];parts=collections.Counter()
  def observe(f,pc):
   nonlocal m1,minimum_sp
   assert r[R]==refresh(flags,m1)
   minimum_sp=min(minimum_sp,r[SP])
   assert pc in original_code and bytes(m[pc:pc+len(original_code[pc])])==original_code[pc]
   opcode=m[pc]
   assert opcode != 0xCB and bytes(m[pc:pc+2]) not in (bytes.fromhex("ed4f"),bytes.fromhex("ed5f"))
   step=2 if opcode in (0xED,0xDD,0xFD) else 1
   m1+=step
   parts["page" if 0x639F<=pc<0x63AA else "station" if pc<0xC000 else "music"]+=step
   if pc==0xDB08:
    assert r[SP]==0x7FFA and bytes(m[0x7FFA:0x8000])==bytes((0xB2,0x63))+hl_word.to_bytes(2,'little')+bytes((255,63));observed.append(pc)
   if pc==0x63C1:assert r[SP]==0x7FFC and bytes(m[0x7FFC:0x8000])==hl_word.to_bytes(2,'little')+bytes((255,63))
  f.run(0x63AA,observe)
  assert parts==dict(page=14,station=14,music=115)
  assert m1==143 and r[R]==refresh(flags,143) and minimum_sp==0x7FF8
  refresh_profiles.append(dict(initial_R=flags,final_R=r[R],M1=m1,input_SP=0x7FFC,minimum_SP=minimum_sp,final_SP=r[SP]))
  expected_ports=[(0x7FFD,0x13)]+[item for reg in range(13,-1,-1) for item in ((0xFFFD,reg),(0xBFFD,0))]+[(0x7FFD,0x10)]
  assert observed==[0xDB08] and f.trace.writes==expected_ports and f.trace.ay==[0]*14+[14,15]
  assert r[:8]==[0x10,0x42|(flags&1),0xBF,0xFD,0,0,hl_word>>8,hl_word&255] and r[8:10]==f.initial[8:10] and r[10:12]==[0x5C,0x3A]
  assert r[16:24]==f.initial[16:24] and r[I]==0x3F and r[IM]==1 and r[IFF]==iff and m.o7ffd==m[0x6306]==0x10 and f.wakes==0
  counts['complete_stop']+=1
 # Проверка всех F, каждого исходного I, всех незаблокированных байтов страницы и разных слов POP HL.
 for flags in range(256):execute(flags,flags%3,flags&1,(flags*257)^0xBEEF,flags&31,(flags*73)&255)
 # Проверка всех сочетаний IM, IFF и Carry на крайних значениях входного слова.
 for im in (0,1,2):
  for iff in (0,1):
   for carry in (0,1):
    for word in (0,1,0x7FFF,0x8000,0xFFFF):execute(carry,im,iff,word,0x18,0xA7)
 report=dict(passed=True,cases_by_path=dict(counts),all_initial_flag_bytes=True,all_initial_i_bytes=True,
  exact_14_ay_register_zero_writes=True,ay_io_registers_14_15_preserved=True,real_music_stop_executed=True,
  exact_physical_two_word_entry_frame=True,stack_delta=4,im_forced_to_1=True,iff_preserved=True,
  refresh_verification=dict(exact_M1=143,station_own_M1=14,two_page_helpers_M1=14,music_stop_with_clear_M1=115,
   all_initial_R_codes=sorted({x["initial_R"] for x in refresh_profiles})==list(range(256)),
   R_checked_before_each_instruction_and_after_return=True,temporary_stack_bytes=4,all_reached_instruction_bytes_match_original_disk=True,profiles=refresh_profiles),
  hl_word_caller_origin_established=False,reference_evidence=reference_evidence(),
  exhaustive_word_frame=word_frame_sweep(base),
  entry_frame_alias_probes=frame_alias_probes(base),
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StopMusicVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
