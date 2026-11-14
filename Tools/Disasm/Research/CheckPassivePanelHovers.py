"""Пять пустых наведений, их JP-обёртки, физические FInterfaceItem и точный R.

Документация: ../../../Docs/PassivePanelHovers.md#r-пустого-возврата-и-jp-обёртки
"""
import collections,json,re
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context
from skoolkit.simutils import SP,R


PANELS=((11,0x6D43,'Карта галактики'),(19,0x7687,'Инфо о системе'),(20,0x7884,'Карта системы'),(32,0xAA84,'Контракт'),(45,0x7954,'Добро пожаловать!'))


def check_adjacent_ret_bytes(memory):
 start,end=0xAA82,0xAA84
 assert bytes(memory[start:end])==b'\xC9\xC9'
 records=range(0xF0FD,0xF0FD+46*16,16)
 hover=[int.from_bytes(memory[record+6:record+8],'little') for record in records]
 draw=[int.from_bytes(memory[record+12:record+14],'little') for record in records]
 action=[entry+3 for entry in hover]
 assert all(not start<=entry<end for entry in (*hover,*action,*draw))
 assert (hover[32],action[32],bytes(memory[hover[32]:action[32]]))==(0xAA55,0xAA58,b'\xC3\x84\xAA')
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
 direct=re.compile(r'^(?:CALL|JP|JR|DJNZ) (?:[A-Z]+,\s*)?#(AA82|AA83)$')
 assert not [(group['name'],row['address']) for group in flow for row in group['instructions']
             if direct.fullmatch(row['operation'])]
 return dict(start=start,end_exclusive=end,physical_interface_records=len(hover),
  contract_hover_entry=hover[32],contract_action_entry=action[32],contract_ret=0xAA84,
  physical_hover_action_or_draw_targets=0,registered_direct_branch_targets=0,
  dynamic_indirect_targets_exhausted=False)


def main():
 _,_,base=make_context();f=Fixture(base);m=f.memory;s=f.sim;initial=f.initial;counts=collections.Counter();roles=[];before=[bytes(b) for b in m.banks]
 adjacent_bytes=check_adjacent_ret_bytes(m)
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
    s.registers[:]=initial;r=s.registers;r[:2]=[af>>8,af&255]
    initial_R=(af>>8)^(af&255);r[R]=initial_R
    s.run(start=start,stop=0x3FFF)
    # Проверка одного M1 непосредственного RET либо двух M1 последовательности JP и RET.
    m1=2 if start==entry else 1
    assert r[R]==((initial_R&128)|((initial_R+m1)&127))
    assert r[:2]==[af>>8,af&255] and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and r[14]==initial[14] and r[26:28]==initial[26:28]
    counts['proxy_calls' if start==entry else 'direct_noop_calls']+=1
 assert [bytes(b) for b in m.banks]==before and not f.trace.writes
 report=dict(passed=True,cases_by_path=dict(counts),physical_interface_records_and_captions=roles,
  adjacent_ret_bytes=adjacent_bytes,
  all_af_values_for_each_entry=True,all_gpr_alternates_index_and_flags_preserved=True,no_memory_or_port_writes=True,
  exact_R_checked=True,R_inputs_cover_all_byte_values=True,proxy_M1=2,direct_RET_M1=1,
  full_AF_by_R_cartesian_product_checked=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PassivePanelHoversVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
