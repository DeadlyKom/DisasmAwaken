"""Пустое событие счётчика, исходный JP во внутренний RET для всех AF."""
import json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();f=Fixture(base);m=f.memory;s=f.sim;before=[bytes(b) for b in m.banks]
 assert bytes(m[0xA6EA:0xA6EE])==bytes.fromhex('c3eda6c9')
 # Проверка полного сохранения AF и остальных регистров при входе через JP и внутренний RET.
 for entry in (0xA6EA,0xA6ED):
  for af in range(65536):
   s.registers[:]=f.initial;r=s.registers;r[:2]=[af>>8,af&255];s.run(start=entry,stop=0x3FFF)
   assert r[:12]==[af>>8,af&255,*f.initial[2:12]] and r[16:24]==f.initial[16:24] and r[SP]==0x8000
   assert r[15]==(f.initial[15]&128)|((f.initial[15]+(2 if entry==0xA6EA else 1))&127)
 assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 report=dict(passed=True,entry_all_af=65536,internal_return_all_af=65536,all_memory_general_index_and_alternate_registers_preserved=True,refresh_register_increments_checked=True,
  no_counter_tick_or_input_side_effect=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/CounterEventVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
