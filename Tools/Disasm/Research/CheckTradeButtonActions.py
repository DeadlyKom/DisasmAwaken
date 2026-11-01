"""Активация кнопок и немедленное физическое продолжение в выборе режима."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from skoolkit.simutils import SP

ENTRIES=((0x7A1B,28,0x7A55,0x7A24,'ship_sale'),(0x7A5B,29,0x7A82,0x7A64,'ship_buy'),
 (0x7B11,37,0x7B25,0x7B1A,'equipment_buy'),(0x7B2B,36,0x7B40,0x7B34,'equipment_sale'))


def main():
 _,_,base=make_context();raw=payload(6);base[4][:len(raw)]=list(raw);counts=collections.Counter()
 def execute(entry,selector,event,owned=0):
  wrapper,key,draw,target,kind=entry;outputs=[]
  for direct in (False,True):
   f=Fixture(base);m=f.memory;r=f.sim.registers
   for address,index in ((0x7A56,28),(0x7A83,29),(0x7B26,37),(0x7B41,36)):put(m,address,index.to_bytes(2,'little'))
   for index,x in ((28,1),(29,12),(37,1),(36,12)):
    p=0xF0FD+16*index;put(m,p,(x,1,9,4,1 if index==key else 0x26,m[p+5]))
   put(m,0xAED5,(0x68,0x48,0x26));put(m,0xF3DE,draw.to_bytes(2,'little')+bytes((1,1)))
   m[0xCA20]=6;m[0x9E78]=0;m[0x9839]=event;put(m,0x9E8B,(0x58,0x9A));m[0x79DD]=m[0x71EC]=0x5A;m[0x68EB]=0xA5;m.banks[4][0x2146]=0xA7;m[0x6906]=0;m[0x9849]=owned
   r[0]=selector;r[4:6]=[0,key];p=0xF0FD+16*key;r[8:10]=[p>>8,p&255]
   if direct:
    r[6:8]=[target>>8,target&255];f.run(0xCC21);r[SP]=0x7FFE;put(m,0x7FFE,(255,63));f.run(target)
   else:f.run(wrapper)
   allowed=selector!=0 and event<128
   wanted=(int(owned!=255) if kind=='ship_sale' else int(kind=='equipment_sale')) if allowed else 0x5A
   assert m[0x79DD if kind.startswith('ship') else 0x71EC]==wanted,(kind,selector,event,owned,wanted)
   assert m[0xCCA4]+256*m[0xCCA5]==target and m[0x9E8B]+256*m[0x9E8C]==(target if selector else 0x9A58)
   if kind.startswith('ship'):
    assert m.banks[4][0x2146]==(0 if allowed else 0xA7) and m[0x68EB]==(1 if allowed else 0xA5)
   assert f.wakes==0
   banks=[bytes(b) for b in m.banks];banks[5]=banks[5][:-256];outputs.append((list(r[:12]),list(r[16:24]),banks,list(f.trace.writes)))
  assert outputs[0]==outputs[1],(kind,selector,event,owned);counts[kind]+=1
 # Проверка каждого байта селектора, обеих ветвей Carry события и независимого результата режима.
 for entry in ENTRIES:
  for selector in range(256):
   for event in (0,128):execute(entry,selector,event)
 # Проверка возврата продажи к покупке при отсутствии собственного корабля.
 for selector in (1,2,127,128,255):
  for event in (0,128):execute(ENTRIES[0],selector,event,255)
 report=dict(passed=True,per_button=dict(counts),all_selector_bytes=True,event_bit7_guards_mode=True,
  actual_activation_and_mode_helpers=True,immediate_physical_continuations=True,independent_mode_and_callback_oracle=True,
  full_register_and_nonstack_memory_equivalence=True,fixture_stack_bytes_excluded=256,independent_bitmap=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/TradeButtonActionsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
