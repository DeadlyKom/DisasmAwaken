"""Четыре исходных хвостовых JP и прямые получатели, полное сравнение регистров и банков."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put

PANELS=((0x6771,0x67D0,25,0x67E0,0x67E1,0x67D7,0x67D2),
 (0x69DD,0x6A4B,22,0x6A5B,0x6A5C,0x6A52,0x6A4D),
 (0x741E,0x7482,43,0x7492,0x7493,0x7489,None),
 (0x74A7,0x750B,44,0x751B,0x751C,0x7512,None))


def main():
 _,_,base=make_context();counts=collections.Counter()
 for wrapper,helper,key,draw,index_operand,hover,count_operand in PANELS:
  for count in ((0,1,2,30,31,255) if count_operand else (40,)):
   for y in (0,3,11,24,27,32,80,191):
    for old in (0,255):
     for last in (False,True):
      outputs=[]
      for start in (wrapper,helper):
       f=Fixture(base,page=0x10 if y&1 else 0x18);m=f.memory;r=f.sim.registers;p=0xF0FD+16*key;put(m,p,(0,0,32,24,6,m[p+5]));r[8:10]=[p>>8,p&255];r[1]=y;put(m,index_operand,key.to_bytes(2,'little'));m[hover]=old
       if count_operand:m[count_operand]=count
       put(m,0x5F00,(0x21,63,0,0xC9));pointers=(0x5F00,draw) if last else (draw,0x5F00);put(m,0xF3DE,b''.join(p.to_bytes(2,'little') for p in pointers)+bytes((1,1)));put(m,0x6307,(42,y))
       f.run(start);assert f.wakes==0
       if count_operand:assert m[count_operand]==count
       outputs.append((list(r[:12]),list(r[16:24]),[bytes(b) for b in m.banks],list(f.trace.writes)))
      assert outputs[0]==outputs[1],(hex(wrapper),count,y,old,last);counts[format(wrapper,'04X')]+=1
 report=dict(passed=True,per_wrapper=dict(counts),whole_memory_and_register_equivalence=True,
  mutable_ship_and_help_row_counts=[0,1,2,30,31,255],pixel_slot_height_remains_40=True,last_and_nonlast_draw_pointer=True,
  independent_bitmap=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ListHoverAdaptersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
