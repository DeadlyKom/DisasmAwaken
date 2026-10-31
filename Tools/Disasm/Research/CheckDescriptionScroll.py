"""Полное действие описания с реальной прокруткой и банковым текстовым callback."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,PC,SP,IFF
from Analyze import payload
from CheckRowHighlight import make_context
from CheckScreenUpdate import put,PortTrace,pointer_image
from CheckTextPagination import reference
from CheckPreviewDescriptions import selected,paint_positions
from CheckScrollBodyClear import rectangle


def main():
 station,_,banks=make_context();raw=payload(6);banks[4][:len(raw)]=list(raw);initial=get_registers({'SP':0x7FFE,'HL':0x6945,'DE':27,'BC':0x36C9,'AF':0x005D,'IX':0xF2AD,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=steps=glyphs=0
 # Проверка всех описаний, двух страниц, направлений и числа удержаний ввода при допустимом окне.
 for selector in (0,1):
  for index in range(4 if selector else 7):
   for page in (0x10,0x18):
    for direction in ('up','down'):
     for presses in (0,1,3):
      m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[PC]=0x6916;r[IFF]=1
      put(m,0x6946,[27,0]);put(m,0x5F00,[0x21,63,0,0xC9]);put(m,0x9CA6,[0,0xB4]);put(m,0xB400,[0,0x5F,0x45,0x69,1,1]+[0]*128);put(m,0xF2AD,[0,0,24,12,6,5]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,[50,80]);m[0x6306]=page;m[0x9E78]=0;m[0xCA20]=6;m[0x9A82]=0xA7;m[0x6548]=1;m[0x9B16]=0;put(m,0x9A90,[0x58,0x9A]);put(m,0x9A8D,[255,255]);put(m,0x6933,[1,0]);put(m,0x692B,[0x7E,0x5A]);m[0x6906]=selector
      for address,value in ((0xAEAB,29),(0xAEB3,92),(0xAEBB,3),(0xAEBF,0),(0xAEC7,3),(0xAECB,0),(0xBD26,0)):m[address]=value
      m.banks[4][0x2146]=index;m.banks[4][0x2148]=0;put(m,0x7FFE,[255,63])
      for addr in (0x66EC,0x6585,0x66ED,0x658A):m[addr]=0
      frame=list(m[0x4000:0x6000]);attrs=bytes(frame[6144:6912]);expected_index=1;poll=wakes=0;expected_screen=None;count=None
      for _ in range(800000):
       pc=r[PC]
       if pc==0x3FFF:break
       if pc==0xA1D6:
        count=m[0x692B]+256*m[0x692C];assert m[0xA235]+256*m[0xA236]==count and m[0xA265:0xA267]==[0x52,0x69]
       if pc==0xA20A:
        assert r[H]*256+r[L]==expected_index;active=poll<presses;m[0x66ED]=int(active)
        if active:
         m[0x6308]=0 if direction=='up' else 191
         if direction=='up':expected_index=max(0,expected_index-1)
         elif expected_index+2<count:expected_index+=1
        poll+=1
       if pc==0xA25C:
        assert m[pc]==0x76 and bytes(m.banks[7][:6144])==bytes(frame[:6144]);snapshot=bytearray(m[0:65536]);snapshot[0xC000:]=bytes(m.banks[4]);cleared=bytearray(frame);rectangle(cleared,3,11,92,36);snapshot[0x4000:0x6000]=cleared;start=selected(snapshot,selector,index);positions=[]
        reference(0xA843,list(snapshot[start:]),list(snapshot[0x8900:0x8A00]),0x0800,92,29,expected_index&255,initial_d=expected_index>>8,positions=positions,origin=(3,3));screen,painted=paint_positions(snapshot,positions,92,29,(3,3));glyphs+=painted;frame=list(cleared);frame[:6912]=screen;expected_screen=bytes(screen);r[PC]+=1;wakes+=1
       elif pc==0xA268:
        assert r[H]*256+r[L]==expected_index and bytes(m[0x4000:0x5B00])==expected_screen,(r[H]*256+r[L],expected_index,next(((hex(0x4000+j),v,expected_screen[j]) for j,v in enumerate(m[0x4000:0x5B00]) if v!=expected_screen[j]),None))
        s.run()
       else:s.run()
      else:raise AssertionError(('instruction_limit',selector,index,page,direction,presses,hex(r[PC])))
      assert m[0x6933]+256*m[0x6934]==expected_index and r[H]*256+r[L]==expected_index and r[SP]==0x8000 and r[IFF]==1
      assert bytes(m.banks[7][6144:6912])==attrs and m.o7ffd==0x10 and m[0x6306]==0x10 and m[0x6307:0x6309]==[50,80]
      assert bytes(m[0x4000:0x6000])==bytes(pointer_image(frame,station,50,80)),(selector,index,direction,presses,'bitmap')
      assert poll==presses+1 and m[0xC6E3]==8 and m[0x9B16]==0 and r[8:12]==initial[8:12] and r[18]==initial[18] and r[20:24]==initial[20:24]
      cases+=1;steps+=wakes
 report=dict(passed=True,whole_action_cases=cases,rendered_steps=steps,independent_glyphs=glyphs,real_repaint_count_scroll_clear_print_and_pointer=True,top_row_word_saved=True,shadow_bitmap_and_attributes_checked=True,input_mutated_at_poll_boundaries=True,explicit_halt_wakeups=steps,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DescriptionScrollVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
