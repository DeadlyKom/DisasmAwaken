"""Восстановление одиннадцати панелей карты с физическими хвостами списка."""
import collections,json,random
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckHelpNewsOpening import move
from skoolkit.simutils import SP


GROUP=((0x7B51,21),(0x7CF8,18),(0x768F,19),(0x7BA8,12),(0x7C1E,13),(0x7C7E,14),(0x7CB6,15),(0x7D24,17),(0x7D53,16),(0x6DA8,11),(0x788C,20))


def main():
 _,_,base=make_context();counts=collections.Counter();rng=random.Random(0x7AC4)
 # Проверка всех старших геометрий, перестановок, алиасов, отсутствующих ключей и C9 без запуска рисователей.
 for kind in range(8):
  for disabled in (False,True):
   for height in range(256):
    f=Fixture(base,page=0x18 if kind&1 else 0x10);m=f.memory;r=f.sim.registers;keys={0x5F00:20,0x5F08:63};put(m,0x5F00,(0xC9,20,0,0xC9));put(m,0x5F08,(0x21,63,0,0xC9));original={}
    for j,(pointer,index) in enumerate(GROUP):
     p=0xF0FD+16*index;assert m[p+12]+256*m[p+13]==pointer
     put(m,pointer,(0xC9 if disabled else 0x21,index,0));keys[pointer]=index
     record=bytes((0xA0,0xB0,1,1,0x26,m[p+5],0,0,(height+index)&255,(height*3+index)&255,(height*5+index)&255,height if j==10 else (height+j+1)&255,0,0,0,0));put(m,p,record);original[index]=record
    if kind==0:pointers=[]
    elif kind==1:pointers=[p for p,_ in reversed(GROUP)]+[0x5F08]
    elif kind==2:pointers=[0x5F00,0x5F08]
    elif kind==3:pointers=[GROUP[0][0],GROUP[0][0],0x5F08]
    else:
     pointers=[p for p,_ in GROUP]+[0x5F00,0x5F08];rng.shuffle(pointers)
    blob=bytearray(rng.randrange(256) for _ in range(512));prefix=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1));blob[:len(prefix)]=prefix;expected=blob
    for pointer,index in GROUP:expected,selected=move(expected,keys,pointer,index)
    put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,blob);m[0x9A82]=0xA7;m[0x78D7]=height;screen=bytes(m[0x4000:0x5B00]);page=m.o7ffd;f.trace.writes.clear();s=f.sim;s.run(start=0x7AC4,stop=0x3FFF)
    assert bytes(m[0xF3DE:0xF5DE])==bytes(expected) and m[0x78D7]==1 and m[0x9A82]==0
    for pointer,index in GROUP:
     p=0xF0FD+16*index;record=bytearray(original[index]);record[:4]=record[8:12]
     assert bytes(m[p:p+16])==bytes(record) and m[pointer]==(0xC9 if disabled else 0x21)
    assert tuple(r[:8])==(height,0xA4,f.initial[2],f.initial[3],0,20,selected>>8,selected&255)
    assert r[8:12]==f.initial[8:12] and r[16:24]==f.initial[16:24] and r[SP]==0x8000 and r[14]==f.initial[14] and r[26:28]==f.initial[26:28]
    assert bytes(m[0x4000:0x5B00])==screen and m.o7ffd==page and not f.trace.writes;counts['eleven_panels_whole_physical_list']+=1
 report=dict(passed=True,cases_by_path=dict(counts),ordered_panel_keys=[i for _,i in GROUP],entire_512_byte_list=True,
  all_saved_height_bytes=True,all_prior_request_bytes=True,independent_128_byte_shift_reference=True,
  aliases_duplicates_reversed_missing_and_c9=True,immediate_drawing=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapPanelOpeningVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
