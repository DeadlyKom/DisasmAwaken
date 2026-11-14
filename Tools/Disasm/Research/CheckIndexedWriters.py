"""Два общих писателя байтов, захваченные операнды и чтение маркера только при сохранении."""
from pathlib import Path
from itertools import product
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWorldSignature import logical_flags
from CheckGeometryReturnEntries import Memory


def store_result(packed,old,result,flags):
 if packed:
  low=127 if result>>8 else result&127;stored=(old&128)|low
  return stored,logical_flags(stored),(result&0xFF00)|low
 stored=(result&255)^(255 if old&128 else 0)
 final_f=(0x92|(stored&0x28)|(flags&1)) if old&128 else (0x54|(old&0x28)|(flags&1))
 return stored,final_f,result


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 # Проверка физического происхождения обоих используемых секторных файлов.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert hashlib.sha256(disk).hexdigest()==manifest['sha256']
 for slot,data in sources.items():
  e=next(e for e in manifest['entries'] if e['slot']==slot)
  assert data==disk[e['offset']:e['offset']+e['allocated_length']]
  assert hashlib.sha256(data).hexdigest()==e['sectors_sha256']
 # Проверка наблюдателя настоящей записью CPU в отдельной памяти.
 probe=Memory(65536);probe[0x4000:0x4003]=bytes.fromhex('320070')
 cpu=Simulator(probe);cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.writes==[(0x7000,0)]
 memory=Memory(65536);memory[:]=original;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 factories=invocations=arithmetic=0
 for entry,field,invoke,pointer_operand,value_operand,packed in ((0xC685,0x9852,0xC695,0xC697,0xC69A,True),
  (0xC6B6,0x9555,0xC695,0xC697,0xC69A,True),(0xC6BC,0x988E,0xC6CB,0xC6CD,0xC6D0,False),
  (0xC6E4,0x98F6,0xC6CB,0xC6CD,0xC6D0,False)):
  for old in range(256):
   memory[:]=original
   for address in (0x7068,0x7026,0x7217,0x71B9,0x73D8,0x737D):memory[address]=0
   memory[field]=old;memory[0xB000]=33;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers
   sim.run(start=entry,stop=0x3FFF)
   captured=old if entry==0xC685 else old&127 if entry==0xC6B6 else old if old<128 else old^255
   assert memory[pointer_operand]+256*memory[pointer_operand+1]==field and memory[value_operand]==captured
   assert memory[0xB800:0xB802]==invoke.to_bytes(2,'little') and r[D]*256+r[E]==invoke and r[22]*256+r[23]==0xB802 and r[SP]==0x8000
   assert memory[field]==old
   factories+=1
 for invoke,store,pointer_operand,value_operand,packed in ((0xC695,0xC6A5,0xC697,0xC69A,True),(0xC6CB,0xC6DB,0xC6CD,0xC6D0,False)):
  target=0xA200;memory[pointer_operand:pointer_operand+2]=target.to_bytes(2,'little')
  for old,low,high in product(range(256),range(256),(0,1,255)):
   captured=(old^0x5A)&(255 if packed else 127);memory[value_operand]=captured;memory[target]=old
   sim.registers[:]=initial;r=sim.registers;r[SP]=0x7FFA;r[F]=0x5C|(old&1);r[B],r[C]=high,low
   memory[0x7FFA:0x7FFE]=bytes([0xD4,0xC4,255,63]);r[15]=low^old
   memory.writes.clear();memory.recording=True;sim.run(start=invoke,stop=0x3FFF);memory.recording=False
   result=high*256+low;stored,flags,de=store_result(packed,old,result,0x5C|(old&1))
   assert (memory[target],r[A],r[F],r[D]*256+r[E],r[H]*256+r[L],r[SP])==(stored,stored,flags,de,target,0x7FFE)
   assert r[B]*256+r[C]==result and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
   assert memory[0x7FF8:0x7FFA]==store.to_bytes(2,'little') and memory[0x7FFA:0x7FFC]==target.to_bytes(2,'little')
   # Проверка рамки SavedTarget, StoreReturn и единственной записи целевого байта.
   assert memory.writes==[(0x7FFA,target&255),(0x7FFB,target>>8),
                          (0x7FF8,store&255),(0x7FF9,store>>8),(target,stored)]
   assert memory[0x7FFC:0x7FFE]==bytes([255,63])
   m1=(25+int(high!=0)) if packed else (20+int(bool(old&128)))
   refresh=low^old
   assert r[15]==((refresh&128)|((refresh+m1)&127))
   invocations+=1
  for captured,old,right,operator in product((0,1,127,128,255),(0,127,128,255),(0,1,127,128,255,256,65535),(0xC488,0xC491)):
   captured&=255 if packed else 127
   sim.registers[:]=initial;r=sim.registers;r[A]=captured;r[H],r[L]=operator>>8,operator&255;r[D]=0;r[E]=captured;r[B],r[C]=right>>8,right&255
   memory[0x7FFE:0x8000]=bytes([255,63]);sim.run(start=operator,stop=0x3FFF);result=sim.registers[D]*256+sim.registers[E];opflags=sim.registers[F]
   assert result==(min(captured+right,65535) if operator==0xC488 else max(captured-right,0))
   memory[value_operand]=captured;memory[target]=old;sim.registers[:]=initial;r=sim.registers;r[SP]=0x7FFA;r[B],r[C]=right>>8,right&255
   memory[0x7FFA:0x7FFE]=bytes([operator&255,operator>>8,255,63]);sim.run(start=invoke,stop=0x3FFF)
   stored,flags,de=store_result(packed,old,result,opflags)
   assert (memory[target],r[A],r[F],r[D]*256+r[E],r[H]*256+r[L],r[SP])==(stored,stored,flags,de,target,0x7FFE)
   arithmetic+=1
 report=dict(passed=True,method='original_indexed_writer_factories_and_two_store_encodings',factory_cases=factories,
  copy_invocations=invocations,arithmetic_invocations=arithmetic,captured_left_differs_from_current_target_tested=True,
  exact_CPU_writes_and_R_checked_for_copy_invocations=True,
  copy_M1_packed_D_zero=25,copy_M1_packed_D_nonzero=26,
  copy_M1_encoded_marker_zero=20,copy_M1_encoded_marker_one=21,
  physical_disk_and_sector_hashes_checked=True,CPU_write_watch_positive_control=True,
  original_return_word_preserved_for_copy=True,stack_bus_cycle_order_verified=False,
  factory_reader_full_RAM_write_domains_proved=False,
  arbitrary_stack_or_target_addresses_checked=False,full_register_joint_product_checked=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/IndexedWritersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
