"""Открытие справки и новостей, физические хвосты MoveItemToTail и сохранённая геометрия."""
import collections,json,random
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from skoolkit.simutils import SP


GROUPS=((0x7A92,((0x69A8,23),(0x6A5B,22))),(0x7AAE,((0x6DD4,24),)))


def move(blob,keys,pointer,index):
 result=bytearray(blob);entries=[];end=0
 while result[end+1]!=1:entries.append(result[end]+256*result[end+1]);end+=2
 found=next((i for i,p in enumerate(entries) if keys[p]==index),None)
 if found is None:selected=pointer
 else:
  offset=2*found;selected=entries[found];result[offset:offset+128]=result[offset+2:offset+130];end=offset
  while result[end+1]!=1:end+=2
 result[end:end+4]=selected.to_bytes(2,'little')+bytes((1,1))
 return result,selected


def main():
 _,_,base=make_context();counts=collections.Counter();rng=random.Random(0x7A92)
 for entry,group in GROUPS:
  for kind in range(8):
   for disabled in (False,True):
    for height in range(256):
     f=Fixture(base,page=0x18 if kind&1 else 0x10);m=f.memory;r=f.sim.registers;keys={0x5F00:group[-1][1],0x5F08:63};put(m,0x5F00,(0xC9,group[-1][1],0,0xC9));put(m,0x5F08,(0x21,63,0,0xC9));original={}
     for j,(pointer,index) in enumerate(group):
      assert m[0xF0FD+16*index+12]+256*m[0xF0FD+16*index+13]==pointer
      put(m,pointer,(0xC9 if disabled else 0x21,index,0));keys[pointer]=index
      record=bytes((0xA0,0xB0,1,1,0x26,m[0xF0FD+16*index+5],0,0,(height+index)&255,(height*3+index)&255,(height*5+index)&255,height if j==len(group)-1 else (height+j+1)&255,0,0,0,0));put(m,0xF0FD+16*index,record);original[index]=record
     if kind==0:pointers=[]
     elif kind==1:pointers=[p for p,_ in reversed(group)]+[0x5F08]
     elif kind==2:pointers=[0x5F00,0x5F08]
     elif kind==3:pointers=[group[0][0],group[0][0],0x5F08]
     else:
      pointers=[p for p,_ in group]+[0x5F00,0x5F08];rng.shuffle(pointers)
     blob=bytearray(rng.randrange(256) for _ in range(512));prefix=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1));blob[:len(prefix)]=prefix;expected=blob;selected=None
     for pointer,index in group:expected,selected=move(expected,keys,pointer,index)
     put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,blob);m[0x9A82]=0xA7;m.banks[7][0x1B01]=0xA5;screen=bytes(m[0x4000:0x5B00]);page=m.o7ffd;f.trace.writes.clear();f.sim.run(start=entry,stop=0x3FFF)
     assert bytes(m[0xF3DE:0xF5DE])==bytes(expected)
     for pointer,index in group:
      record=bytearray(original[index]);record[:4]=record[8:12];assert bytes(m[0xF0FD+16*index:0xF10D+16*index])==bytes(record) and m[pointer]==(0xC9 if disabled else 0x21)
     assert tuple(r[:8])==(height,0xA4,f.initial[2],f.initial[3],0,group[-1][1],selected>>8,selected&255)
     assert r[8:12]==f.initial[8:12] and r[16:24]==f.initial[16:24] and r[SP]==0x8000 and m[0x9A82]==0
     assert bytes(m[0x4000:0x5B00])==screen and m.banks[7][0x1B01]==0xA5 and m.o7ffd==page and not f.trace.writes
     counts['help_two_panels' if entry==0x7A92 else 'news_one_panel']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_saved_height_bytes=True,all_restored_geometry_bytes_and_other_fields_checked=True,
  entire_physical_512_byte_list_and_128_byte_shifts=True,aliases_duplicates_disabled_and_reversed_lists=True,
  no_immediate_drawing_or_help_selection=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpNewsOpeningVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
