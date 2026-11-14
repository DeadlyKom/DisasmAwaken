"""Четыре исходных селектора характеристик ключа, фактические символы s/c/u и p/g."""
from pathlib import Path
import json,sys
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import signature,step_key
from CheckBank4Index import WriteMemory
from CheckGlyphRenderer import compare_flags


def main(with_expression_wrappers=False):
 _,_,banks=make_context();banks=[bytearray(b) for b in banks]
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 lang=(ROOT/(e['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=lang
 # Проверка физических секторов трёх исполняемых областей.
 disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
 assert sha256(disk).hexdigest()==manifest['sha256']
 for slot in (4,5,7):
  item=next(row for row in manifest['entries'] if row['slot']==slot)
  sectors=(ROOT/(item['path']+'.sectors.bin')).read_bytes()
  assert sectors==disk[item['offset']:item['offset']+item['allocated_length']]
  assert sha256(sectors).hexdigest()==item['sectors_sha256']
 # Проверка наблюдателя настоящей записью CPU в отдельном контексте.
 probe=WriteMemory(banks=[bytearray(0x4000) for _ in range(8)],out7ffd=0x16)
 put(probe,0x4000,bytes.fromhex('320070'));cpu=Simulator(probe)
 cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
 assert probe.cpu_writes==[(0x7000,0)]
 memory=WriteMemory(banks=[b.copy() for b in banks],out7ffd=0x16);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0xB000,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 for entry,default,anchor,count,fields in ((0xC383,0,0xCA25,3,{'s':'major','c':'minor','u':'size'}),
  (0xC399,1,0xCA25,3,{'s':'major','c':'minor','u':'size'}),
  (0xC3AF,0,0xCA2E,2,{'p':'result','g':'region'}),(0xC3C5,1,0xCA2E,2,{'p':'result','g':'region'})):
  for variant in (0,1,255):
   current=(0x4B38,0x1357,variant);other=(0xFFFF,0x2468,255-variant)
   for prefix in [b'']+[str(n).encode() for n in range(257)]+[b'65535',b'99999']:
    for suffix in ['']+list(fields):
     memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
     memory[0x6306]=0x16;put(memory,0x7FFE,[255,63])
     for address,(a,b,v) in ((0x983F,current),(0x9844,other)):put(memory,address,list(a.to_bytes(2,'little')+b.to_bytes(2,'little')+bytes([v])))
     text=prefix+(b'.'+suffix.encode() if suffix else b'!')+b'\r';put(memory,0xB000,list(text));sim.registers[:]=initial;r=sim.registers
     trace=PortTrace(sim);sim.set_tracer(trace);index=((int(prefix)-1)&65535) if prefix else default
     put(memory,0xB800,[0xCC,0xDD])
     if with_expression_wrappers:r[22],r[23]=0xB8,0
     memory.cpu_writes.clear();memory.recording=True
     sim.run(start=entry-6 if with_expression_wrappers else entry,stop=0x3FFF);memory.recording=False
     # Расчёт постоянных записей парсера и выбранной банковой характеристики.
     expected_writes=[(0xC804,(entry+15)&255),(0xC805,(entry+15)>>8)]
     if suffix:
      u,v,key_variant=other if index&255==1 else current
      expected_writes.append((0x6306,0x11))
      def key_writes(u,v):
       data=u.to_bytes(2,'little')+v.to_bytes(2,'little')
       return [(0x631C+i,value) for i,value in enumerate(data)]
      expected_writes+=key_writes(u,v)
      for iteration in range(key_variant+1):
       u,v,_=step_key(u,v);expected_writes+=key_writes(u,v)
      expected_writes.extend(((0x6306,0x10),(0x6306,0x16)))
     if with_expression_wrappers:
      result=r[D]*256+r[E]
      expected_writes.extend(((0xB800,result&255),(0xB801,result>>8)))
      assert (r[20]*256+r[21],r[22]*256+r[23])==(result,0xB802)
      assert bytes(memory[0x7FFC:0x7FFE])==result.to_bytes(2,'little')
     actual=[(a,v) for a,v in memory.cpu_writes if not (0x7FEE if with_expression_wrappers else 0x7FF0)<=a<0x7FFE]
     assert actual==expected_writes,(entry,prefix,suffix,actual,expected_writes)
     assert bytes(memory[0x7FFE:0x8000])==bytes([255,63])
     if not with_expression_wrappers and not prefix and not suffix:assert memory.cpu_writes==expected_writes
     if suffix:
      info=signature(*(other if index&255==1 else current));hl=info['region']*256+info['minor'] if suffix=='u' else info['major']*256+info['size']
      assert (r[D]*256+r[E],r[H]*256+r[L],r[B],r[C],r[A],r[F])==(info[fields[suffix]],hl,index>>8,((index&255)-1)&255,info['result'],info['flags'])
      assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10),(0x7FFD,0x16)]
     else:
      assert (r[D]*256+r[E],r[H]*256+r[L],r[B],r[C],r[A],r[F])==(anchor,index,0x36,default,33,compare_flags(33,46 if prefix else 48))
      assert not trace.writes
     assert r[8]*256+r[9]==0xB000+len(prefix)+(2 if suffix else 0) and r[SP]==0x8000
     assert r[10:12]==initial[10:12] and r[18]==count and r[19]==initial[19]
     if not with_expression_wrappers:assert r[20:24]==initial[20:24]
     cases+=1
 # Проверка каждого недопустимого байта суффикса до настоящего сброса стека.
 invalid_cases=0
 for entry,fields in ((0xC383,b'scu'),(0xC399,b'scu'),(0xC3AF,b'pg'),(0xC3C5,b'pg')):
  for prefix in (b'',b'0',b'2',b'65535',b'99999'):
   for symbol in range(256):
    if symbol in fields:continue
    memory.recording=False
    memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x16)
    memory[0x6306]=0x16;put(memory,0x7FFE,[255,63])
    put(memory,0xC01C,[0xFE,0x7F]);memory[0xC028]=0
    text=prefix+b'.'+bytes([symbol])+b'X\r\0'
    put(memory,0xB000,text);sim.registers[:]=initial;r=sim.registers
    trace=PortTrace(sim);sim.set_tracer(trace)
    put(memory,0xB800,[0xCC,0xDD])
    if with_expression_wrappers:r[22],r[23]=0xB8,0
    memory.cpu_writes.clear();memory.recording=True
    sim.run(start=entry-6 if with_expression_wrappers else entry,stop=0xC01B)
    # Проверка отброшенного слова выбора и поиска, обычный RET ещё не выполнялся.
    assert r[SP]==(0x7FF8 if with_expression_wrappers else 0x7FFA),(entry,prefix,symbol,r[SP])
    assert r[8]*256+r[9]==0xB000+len(prefix)+2
    assert not trace.writes and memory[0x6306]==0x16
    persistent=[(a,v) for a,v in memory.cpu_writes if not (0x7FEE if with_expression_wrappers else 0x7FF0)<=a<0x7FFE]
    assert persistent==[(0xC804,(entry+15)&255),(0xC805,(entry+15)>>8)]
    assert bytes(memory[0x7FFE:0x8000])==bytes([255,63])
    before_skip=list(memory.cpu_writes)
    # Проверка продолжения после CR с восстановленным SavedSP и возврата по NUL.
    sim.run(start=0xC01B,stop=0xC010)
    assert r[SP]==0x7FFE and r[8]*256+r[9]==0xB000+len(text)-1
    sim.run(start=0xC010,stop=0x3FFF)
    memory.recording=False
    assert r[SP]==0x8000 and memory.cpu_writes==before_skip
    assert not trace.writes
    assert bytes(memory[0xB800:0xB802])==bytes([0xCC,0xDD])
    if with_expression_wrappers:assert r[22]*256+r[23]==0xB800
    invalid_cases+=1
 report=dict(passed=True,cases=cases,invalid_suffix_cases=invalid_cases,
  invalid_suffix_all_256_bytes_classified=True,
  invalid_suffix_original_SkipLine_and_root_return_executed=True,
  invalid_suffix_no_banking_or_WorkKey_writes=True,
  invalid_suffix_error_SP=0x7FF8 if with_expression_wrappers else 0x7FFA,invalid_suffix_reset_SP=0x7FFE,
  method='original_key_field_expression_wrappers' if with_expression_wrappers else 'original_four_key_field_selectors_and_banked_handlers',
  expression_wrappers_executed=with_expression_wrappers,physical_disk_and_sector_hashes_checked=True,
  invalid_suffix_expression_not_written=True,
  no_suffix_returns_table_anchor=True,all_choice_bytes=True,
  exact_non_stack_write_sequence_checked=True,CPU_write_watch_positive_control=True,
  bounded_stack_write_interval=[0x7FEE if with_expression_wrappers else 0x7FF0,0x7FFE],original_return_word_preserved=True,
  no_number_no_suffix_has_no_stack_writes=not with_expression_wrappers,full_R_proved=False,
  all_keys_variants_stack_addresses_checked=False,
  stack_bus_cycle_order_verified=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports'/('KeyFieldExpressionWrappersVerification.json' if with_expression_wrappers else 'KeyFieldSelectorsVerification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main('--expression-wrappers' in sys.argv)
