"""Пять исходных пустых наведений и их JP-обёртки, связь с физическими FInterfaceItem."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context
from skoolkit.simutils import SP


PANELS=((11,0x6D43,'Карта галактики'),(19,0x7687,'Инфо о системе'),(20,0x7884,'Карта системы'),(32,0xAA84,'Контракт'),(45,0x7954,'Добро пожаловать!'))


def main():
 _,_,base=make_context();f=Fixture(base);m=f.memory;s=f.sim;initial=f.initial;counts=collections.Counter();roles=[];before=[bytes(b) for b in m.banks]
 for index,noop,caption in PANELS:
  record=0xF0FD+16*index;entry=m[record+6]+256*m[record+7];assert bytes(m[entry:entry+3])==bytes((0xC3,noop&255,noop>>8)) and m[noop]==0xC9
  p=0xE399
  for _ in range(m[record+5]+1):
   while m[p]!=10:p+=1
   p+=1
  end=p
  while m[end]!=10:end+=1
  assert bytes(m[p:end]).decode('cp866').rstrip('\r')==caption
  roles.append(dict(index=index,hover_entry=entry,noop_entry=noop,caption=caption))
  # Проверка всех AF с настоящим исходным JP и непосредственным RET, GPR и обе альтернативные пары сохраняются.
  for start in (entry,noop):
   for af in range(65536):
    s.registers[:]=initial;r=s.registers;r[:2]=[af>>8,af&255];s.run(start=start,stop=0x3FFF)
    assert r[:2]==[af>>8,af&255] and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and r[14]==initial[14] and r[26:28]==initial[26:28]
    counts['proxy_calls' if start==entry else 'direct_noop_calls']+=1
 assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 report=dict(passed=True,cases_by_path=dict(counts),physical_interface_records_and_captions=roles,
  all_af_values_for_each_entry=True,all_gpr_alternates_index_and_flags_preserved=True,no_memory_or_port_writes=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PassivePanelHoversVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
