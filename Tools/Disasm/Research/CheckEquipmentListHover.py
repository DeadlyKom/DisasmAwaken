"""JP наведения оснащения, текущий старший операнд числа строк и прямой помощник."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from ReferenceControlsPointRespawn import refresh


def main():
 _,_,base=make_context();counts=collections.Counter()
 # Проверка JP-обёртки на разных высотах запроса, пиксельных Y и прежних XOR-строках.
 for row_count in (0,1,2,30,31,255):
  for y in (0,3,24,27,31,32,80,191):
   for old_row in (0,255):
    for flags in (0,1,0xFF):
     states=[];refreshes=[]
     for entry in (0x7172,0x7210):
      f=Fixture(base);m=f.memory;r=f.sim.registers;p=0xF0FD+16*38;put(m,p,(0,0,32,24,6,m[p+5]));r[8:10]=[p>>8,p&255];r[1]=flags;put(m,0x7228,(38,0));put(m,0x9CA6,(0xDE,0xF3));put(m,0xF3DE,(0x27,0x72,1,1));put(m,0x6307,(42,y));m[0x7212]=row_count;m[0x7217]=old_row
      r[14]=row_count^y;r[15]=(row_count^y^old_row)&255;r[27]=flags%3;context=r.copy()
      f.run(entry);assert m[0x7212]==row_count and f.wakes==0
      assert all(r[i]==context[i] for i in (14,26,27))
      refreshes.append(r[15])
      states.append((list(r[:12]),list(r[16:24]),[bytes(b) for b in m.banks],list(f.trace.writes)))
     assert refreshes[0]==refresh(refreshes[1],1)
     assert states[0]==states[1];counts['wrapper_helper_equivalence']+=1
 report=dict(passed=True,cases_by_path=dict(counts),row_counts=[0,1,2,30,31,255],mutable_row_count_preserved=True,
  real_hover_xor_and_pointer_helpers=True,ordinary_context_and_whole_memory_equivalence=True,wrapper_extra_refresh_m1=1,
  i_im_iff_preserved=True,iff_fixture=1,independent_hover_bitmap=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/EquipmentListHoverVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
