"""Установщики отложенных callback, реальные ветви ActivateInterfaceCallback без исполнения новой цели."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put

ENTRIES=((0x79BD,30,0x7A15,0x7A16,0x79C7),(0x7A88,9,0x7A9E,0x7A9F,0x7A92),(0xAA33,33,0xAA4F,0xAA50,0xAA3D),
 (0x7B46,21,0x7B51,0x7B52,0x7B50),(0x7CBC,18,0x7CF8,0x7CF9,0x7CC6),
 (0x7AA4,2,0x7AB4,0x7AB5,0x7AAE),(0x7ABA,3,0x7B0B,0x7B0C,0x7AC4))


def main():
 _,_,base=make_context();counts=collections.Counter()
 # Проверка всех селекторов на установленном контуре и на запрещённом переключении контура.
 for wrapper,key,draw,index_operand,target in ENTRIES:
  for selector in range(256):
   for event in (0,0x80):
    for flags in (1,0x10):
     outputs=[]
     for direct in (False,True):
      f=Fixture(base);m=f.memory;r=f.sim.registers;p=0xF0FD+16*key;put(m,p,(1,1,12,5,flags,m[p+5]));put(m,index_operand,key.to_bytes(2,'little'));put(m,0xF3DE,draw.to_bytes(2,'little')+bytes((1,1)))
      m[0xCA20]=6;m[0x9E78]=0;m[0x9839]=event;put(m,0x9E8B,(0x58,0x9A));r[0]=selector;r[4:6]=[0,key];r[8:10]=[p>>8,p&255]
      if direct:r[6:8]=[target>>8,target&255]
      forbidden=[]
      def observe(f,pc):
       if pc==target:forbidden.append(pc)
      f.run(0xCC21 if direct else wrapper,observe)
      assert not forbidden and m[0xCCA4]+256*m[0xCCA5]==target
      assert m[0x9E8B]+256*m[0x9E8C]==(target if selector else 0x9A58)
      # Исключение 256 байтов объявленного CPU-стека фикстуры, CALL обёртки меняет физические адреса временных возвратов.
      banks=[bytes(b) for b in m.banks];banks[5]=banks[5][:-256]
      if f.wakes:
       # Проверка сохранённого SP настоящего IRQ с учётом дополнительного CALL обёртки.
       assert m[0x9C0D]+256*m[0x9C0E]==(0x7FFE if direct else 0x7FFC)
       banks[2]=banks[2][:0x1C0D]+bytes(2)+banks[2][0x1C0F:]
      outputs.append((list(r[:12]),list(r[16:24]),banks,list(f.trace.writes),f.wakes))
     if outputs[0]!=outputs[1]:
      left,right=outputs
      raise AssertionError((hex(wrapper),selector,event,flags,'registers',left[:2],right[:2],
       'memory',[(bank,[(i,a,b) for i,(a,b) in enumerate(zip(lb,rb)) if a!=b][:12]) for bank,(lb,rb) in enumerate(zip(left[2],right[2])) if lb!=rb],
       'ports',left[3:],right[3:]))
     counts[format(wrapper,'04X')]+=1
 report=dict(passed=True,per_wrapper=dict(counts),all_selector_bytes=True,event_carry_0_and_1=True,
  actual_activation_and_bounds_helpers=True,no_new_callback_executed=True,exact_next_and_active_callback_addresses=True,
  full_register_and_nonstack_memory_equivalence=True,fixture_stack_bytes_excluded=256,physical_irq_saved_sp_checked_separately=True,independent_bitmap=False,
  real_im2_at_activation_halt=True,music_disabled=True,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DeferredActionAdaptersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
