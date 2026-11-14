"""Исходные пятибайтовые записи, отдельные базы и общие стековые входы."""
from pathlib import Path
import json
import sys
from hashlib import sha256
from CheckGeometryReturnEntries import Memory
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP


def add16_flags(left,right,old):
 result=left+right
 return (old&0xC4)|((result>>8)&0x28)|(0x10 if (left&0xFFF)+(right&0xFFF)>0xFFF else 0)|(result>0xFFFF)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 # Проверка происхождения исходных секторов и наблюдателя записей CPU.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 for slot,source in sources.items():
  item=next(e for e in manifest['entries'] if e['slot']==slot)
  assert source==disk[item['offset']:item['offset']+item['allocated_length']]
  assert sha256(source).hexdigest()==item['sectors_sha256']
 probe=Memory(65536);probe[0x4000:0x4003]=bytes.fromhex('320070')
 cpu=Simulator(probe);cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.writes==[(0x7000,0)]
 memory=Memory(65536);memory[0x6000:]=sources[4];memory[0xC000:0xC000+len(sources[5])]=sources[5]
 simulator=Simulator(memory)
 initial=get_registers({'SP':0x7FFA,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A00,
  'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts={};bits=0
 # Проверка всех индексов и флагов для трёх штатных входов и двух общих хвостов.
 for entry,base,word in ((0xC5E9,0x9803,True),(0xC5F9,0x9802,False),(0xC609,0x9806,False),
                         (0xC60F,0x9826,True),(0xC615,0x9829,False),
                         (0xC5EC,0xAFFF,True),(0xC5FC,0x9FFF,False)):
  count=0
  for index in range(256):
   for flags in range(256):
    simulator.registers[:]=initial;r=simulator.registers;r[F]=flags
    if entry in (0xC5EC,0xC5FC):r[D],r[E]=base>>8,base&255
    # Создание старшего байта индекса, который обработчик обязан отбросить.
    memory[0x7FFA:0x7FFE]=bytes((index,(index*73+flags)&255,255,63))
    address=(base+5*index)&0xFFFF
    memory[address]=(index*17+flags*13)&255;memory[address+1]=(index*29+flags*7)&255
    expected=memory[address]+(memory[address+1]*256 if word else 0)
    refresh=(index+flags)&255;r[15]=refresh
    r[14]=index;r[26]=flags&1;r[27]=flags%3
    memory.writes.clear();memory.recording=True
    simulator.run(start=entry,stop=0x3FFF);memory.recording=False
    # Проверка единственного PUSH в уже снятое слово индекса и неизменности возврата.
    assert memory.writes==[(0x7FFA,index),(0x7FFB,0)]
    assert bytes(memory[0x7FFC:0x7FFE])==bytes([255,63])
    # Расчёт M1 общего хвоста и входной настройки базы без ветвления по данным.
    cost={0xC5E9:13,0xC5F9:12,0xC609:13,0xC60F:14,0xC615:13,0xC5EC:12,0xC5FC:11}[entry]
    assert r[15]==((refresh&128)|((refresh+cost)&127))
    assert (r[14],r[26],r[27])==(index,flags&1,flags%3)
    assert r[SP]==0x7FFE and r[H]*256+r[L]==address+int(word)
    assert r[D]*256+r[E]==expected and r[B]*256+r[C]==index
    assert r[A]==0x5A and r[F]==add16_flags(5*index,base,flags)
    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    count+=1
  counts[hex(entry)]=count
 # Проверка всех баз двух общих хвостов с нулевым и максимальным индексом.
 memory[:]=bytes(65536);memory[0x6000:]=sources[4];memory[0xC000:0xC000+len(sources[5])]=sources[5]
 arbitrary=wrap=stack_reads=0;witnesses=[]
 for entry,word,cost in ((0xC5EC,True,12),(0xC5FC,False,11)):
  for index in (0,255):
   for base in range(65536):
    simulator.registers[:]=initial;r=simulator.registers
    flags=((base>>8)^index)&255;refresh=base&255
    r[F]=flags;r[15]=refresh;r[D],r[E]=base>>8,base&255
    memory[0x7FFA:0x7FFE]=bytes((index,0xA5,255,63))
    address=(base+5*index)&65535
    # Расчёт чтения после PUSH, который уже обнулил старший байт снятого индекса.
    def after_push(pointer):
     return index if pointer==0x7FFA else 0 if pointer==0x7FFB else memory[pointer]
    result=after_push(address)+(after_push((address+1)&65535)*256 if word else 0)
    memory.writes.clear();memory.recording=True
    simulator.run(start=entry,stop=0x3FFF);memory.recording=False
    assert memory.writes==[(0x7FFA,index),(0x7FFB,0)]
    assert bytes(memory[0x7FFC:0x7FFE])==bytes([255,63])
    assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[SP])==((address+int(word))&65535,result,index,0x7FFE)
    assert r[A]==0x5A and r[F]==add16_flags(5*index,base,flags)
    assert r[15]==((refresh&128)|((refresh+cost)&127))
    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    if word and address==65535:wrap+=1
    if any(0x7FFA<=pointer<0x7FFE for pointer in (address,((address+1)&65535) if word else address)):
     stack_reads+=1
     witnesses.append(dict(entry=entry,index=index,base=base,address=address,result=result))
    arbitrary+=1
 report=dict(passed=True,method='original_stride5_accessors_and_shared_stack_entries',accessor_cases=counts,
             arbitrary_base_cases=arbitrary,all_65536_bases_for_index_profiles=[0,255],
             word_read_wrap_cases=wrap,stack_read_overlap_cases=stack_reads,stack_overlap_witnesses=witnesses,
             all_byte_indices=True,all_initial_flags=True,index_high_byte_discarded=True,
             physical_disk_and_sector_hashes_checked=True,CPU_write_watch_positive_control=True,
             exact_CPU_write_sequence_checked=True,original_return_word_preserved=True,
             exact_R_M1={'C5E9':13,'C5F9':12,'C609':13,'C60F':14,'C615':13,'C5EC':12,'C5FC':11},
             I_IFF_IM_and_R_bit7_checked=True,all_stack_addresses_and_bases_checked=False,
             stack_bus_cycle_order_verified=False,
             irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StrideFiveVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
