"""Подготовка колонок списка оснащения и числовая характеристика текущего ключа."""
import collections,itertools,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckWorldSignature import signature,logical_flags
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();f=Fixture(base);m=f.memory;s=f.sim;counts=collections.Counter();observed=set()
 words=(0,1,0xFFFF,0x4A36,0x4D39,0x4734,0x4937,0x4738,0x493A,0x4E3B)
 # Проверка всех Variant и граничных ключей, геометрических областей и двух экранных страниц.
 for first,second,variant,page in itertools.product(words,(0,0xFFFF),range(256),(0x10,0x18)):
  m.out7ffd(page);m[0x6306]=page;put(m,0x983F,(*first.to_bytes(2,'little'),*second.to_bytes(2,'little'),variant));put(m,0x7FFE,(255,63))
  for address in (0xBD26,0xBD73,0xBD7E,0xBD89,0xBD94,0x72DD):m[address]=0xA5
  s.registers[:]=f.initial;f.trace.writes.clear();s.run(start=0x733F,stop=0x3FFF);r=s.registers;expected=signature(first,second,variant)
  assert r[6:8]==[expected['major'],expected['size']] and r[4:6]==[expected['region'],expected['minor']] and r[2:4]==f.initial[2:4]
  assert r[:2]==[expected['size'],expected['flags']] and r[16:18]==[page,logical_flags(page)]
  assert r[8:12]==f.initial[8:12] and r[18:24]==f.initial[18:24] and r[SP]==0x8000 and r[14]==f.initial[14] and r[26:28]==f.initial[26:28]
  assert [m[a] for a in (0xBD26,0xBD73,0xBD7E,0xBD89,0xBD94,0x72DD)]==[0,0x74,0x86,0x9C,0xAE,expected['size']]
  assert bytes(m[0x631C:0x6320])==expected['first'].to_bytes(2,'little')+expected['second'].to_bytes(2,'little')
  assert f.trace.writes==[(0x7FFD,page|1),(0x7FFD,page)] and m.o7ffd==m[0x6306]==page
  assert f.wakes==0;counts['real_current_key_and_column_setup']+=1;observed.add(expected['size'])
 assert observed==set(range(1,17))
 report=dict(passed=True,cases_by_path=dict(counts),all_variants=True,all_key_sizes_observed=sorted(observed),
  independent_signature_reference=True,exact_column_bytes=True,original_bank_switches=True,
  key_size_gameplay_name_unproved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentListSetupVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
