"""Исходные переходы сценария, восстановление SP и оба варианта условия."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC,R
from CheckWorldSignature import logical_flags
from CheckGlyphRenderer import compare_flags
from CheckGeometryReturnEntries import Memory


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
 # Проверка физического происхождения всей секторной области LANG перед исполнением.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert hashlib.sha256(disk).hexdigest()==manifest['sha256']
 assert source==disk[e['offset']:e['offset']+e['allocated_length']]
 assert hashlib.sha256(source).hexdigest()==e['sectors_sha256']
 memory=Memory(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF0,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB802,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 def prepare(text,flag=0):
  sim.registers[:]=initial;memory[0xB000:0xB000+len(text)]=text
  memory[0x7FFE:0x8000]=bytes([255,63]);memory[0xC01C:0xC01E]=bytes([254,127]);memory[0xC028]=flag
 def run(entry,stops):
  r=sim.registers;r[PC]=entry
  memory.writes.clear();memory.recording=True
  for _ in range(4096):
   if r[PC] in stops:
    memory.recording=False
    return r[PC]
   sim.opcodes[memory[r[PC]]]()
  raise AssertionError(('limit',hex(entry),hex(r[PC])))
 conditions=lines=commands=0
 # Проверка всех слов при обоих направлениях условия, без исполнения следующей команды.
 for entry,inverse in ((0xC057,False),(0xC080,True)):
  for word in range(65536):
   prepare(b'x\r');memory[0xB800:0xB802]=word.to_bytes(2,'little');sim.registers[R]=word&255
   accepted=(word==0) if inverse else (word!=0)
   target=run(entry,{0xC00C,0xC061});r=sim.registers;v=(word&255)|(word>>8)
   assert target==(0xC00C if accepted else 0xC061)
   assert (r[A],r[F])==(v,logical_flags(v)) and r[2:13]==initial[2:13] and r[16:24]==initial[16:24]
   # Проверка локального R и отсутствия записей RAM до получателя условия.
   m1=9+int(inverse and not accepted)
   assert r[R]==((word&128)|((word+m1)&127)) and not memory.writes
   conditions+=1
 # Проверка поиска первой закрывающей скобки, включая вложенную скобку и CR перед блоком.
 for entry,word in ((0xC057,0),(0xC080,1)):
  for text,offset in ((b'x\r',0),(b'\rx\r',0),(b'{abc}tail\r',4),(b'\r{abc}tail\r',5),(b'{a{b}c}tail\r',4)):
   prepare(text);memory[0xB800:0xB802]=word.to_bytes(2,'little')
   assert run(entry,{0xC01B})==0xC01B;r=sim.registers
   assert r[8]*256+r[9]==0xB000+offset and r[SP]==initial[SP]
   assert r[2:8]==initial[2:8] and r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
   assert not memory.writes
   conditions+=1
 # Проверка флага завершения строки для всех его байтов и разных длин строки.
 for flag in range(256):
  for prefix in (b'',b'abc',b'\x00x',b' '*31):
   prepare(prefix+b'\rZ',flag);sim.registers[R]=flag;target=run(0xC01B,{0xC010,0x3FFF});r=sim.registers
   assert target==(0xC010 if flag==0 else 0x3FFF)
   assert r[8]*256+r[9]==0xB001+len(prefix) and r[SP]==(0x7FFE if flag==0 else 0x8000)
   assert (r[A],r[F])==(flag,logical_flags(flag)) and r[2:8]==initial[2:8] and r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
   # Проверка M1 на полном пропуске строки, включая DD-префиксы и конечный RET.
   m1=6*(len(prefix)+1)+4+(flag!=0)
   assert r[R]==(flag&128)|((flag+m1)&127)
   assert not memory.writes
   lines+=1
 # Проверка NUL, CR, пробела, неизвестного символа и всех 15 реальных команд диспетчера.
 records=[(memory[0xC932+3*i],memory[0xC933+3*i]+256*memory[0xC934+3*i]) for i in range(1,16)]
 handlers={h for _,h in records}
 for code in range(256):
  prepare(bytes([code,13,0]));sim.registers[R]=code;target=run(0xC00C,handlers|{0xC01B,0xC027,0x3FFF});r=sim.registers
  match=next(((i,h) for i,(c,h) in enumerate(records) if c==code),None)
  if code==0:
   assert target==0x3FFF and r[SP]==0x8000 and r[8]*256+r[9]==0xB000
   # Проверка M1 короткого пути Entry с NUL, включая ED и DD.
   assert r[R]==6
  elif code==32:
   assert target==0xC01B and r[SP]==0x7FFE and r[8]*256+r[9]==0xB001
  elif code==13:
   assert target==0xC027 and r[SP]==0x7FFE and r[8]*256+r[9]==0xB001
  elif match:
   i,h=match;assert target==h and r[SP]==0x7FFE and r[8]*256+r[9]==0xB001
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[A],r[F])==(h,3,15-i,0xC9,h&255,compare_flags(code,code))
  else:
   assert target==0xC01B and r[SP]==0x7FFC and r[8]*256+r[9]==0xB001
  commands+=1
 # Проверка независимости простых хвостовых команд и FinishScript от мусорного входного SP.
 for entry in (0xC08D,0xC0D5,0xC0D8,0xC10B):
  prepare(b'');sim.registers[R]=0xFF
  assert run(entry,{0xC00C})==0xC00C and sim.registers[:13]==initial[:13] and sim.registers[16:24]==initial[16:24]
  assert sim.registers[R]==0x80 and not memory.writes
  commands+=1
 prepare(b'');sim.registers[R]=0xFD
 assert run(0xC0E7,{0x3FFF})==0x3FFF
 assert sim.registers[R]==0x80 and not memory.writes
 assert sim.registers[SP]==0x8000 and sim.registers[:12]==initial[:12] and sim.registers[16:24]==initial[16:24];commands+=1
 # Проверка инициализации изменяемых операндов самим входом RunMarketScript.
 prepare(b'');memory[0xCA8F]=0;memory[0x7FF0:0x7FF2]=bytes([255,63]);memory[0xC028]=255
 # Проверка шести M1 инициализации отдельно от чтения первой команды.
 sim.registers[R]=0xFD
 assert run(0xC000,{0xC00C})==0xC00C
 assert sim.registers[R]==0x83
 assert run(0xC00C,{0x3FFF})==0x3FFF;r=sim.registers
 assert memory[0xC01C:0xC01E]==bytes([240,127]) and memory[0xC028]==0
 assert r[SP]==0x7FF2 and r[8]*256+r[9]==0xCA8F and (r[A],r[F])==(0,0x44)
 commands+=1
 report=dict(passed=True,condition_cases=conditions,line_cases=lines,command_cases=commands,
  method='original_script_control_instructions_and_command_dispatch_table',all_16_bit_conditions=True,
  first_closing_brace_without_nesting=True,nul_does_not_stop_skip_line=True,calls_stubbed=False,
  physical_disk_and_sector_hashes_checked=True,refresh_line_cases=lines,
  refresh_nul_m1=6,refresh_initializer_m1=6,all_refresh_values_in_line_cases=True,
  condition_local_M1_normal=9,condition_local_M1_inverse_accepted=9,
  condition_local_M1_inverse_rejected=10,finish_M1=3,tail_command_M1=1,
  no_own_RAM_writes_in_condition_skip_line_finish_and_tail_boundaries=True,
  condition_refresh_cases=131072,condition_word_and_R_full_joint_product=False,
  full_refresh_flag_length_cartesian_product=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ScriptControlVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
