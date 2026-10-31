"""Цикл прокрутки с исходными двумя экранами, очисткой и настоящим торговым callback."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP,IFF
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckScrollBodyClear import rectangle
from CheckTradeNumericColumns import expected as trade_expected


def main():
    station,_,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':5,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    flat=bytearray(65536);flat[0x4000:0x8000]=bytes(banks[5]);flat[0x8000:0xC000]=bytes(banks[2]);flat[0xC000:]=bytes(banks[0]);s=Simulator(flat);put(flat,0xA235,[29,0]);gates=accepted=0
    # Проверка двух последовательных SBC, включая перенос первой разности на недопустимых индексах.
    for visible in (1,8,31):
        for index in range(65536):
            s.registers[:]=initial;r=s.registers;r[H],r[L]=index>>8,index&255;r[C]=visible;r[PC]=0xA234
            difference=29-index;second=(difference&65535)-visible-int(difference<0);allow=second>0
            for _ in range(20):
                if r[PC] in (0xA20A,0xA245):break
                s.run()
            else:raise AssertionError('Не завершается проверка прокрутки вниз')
            assert (r[PC]==0xA245)==allow and r[H]*256+r[L]==((index+int(allow))&65535)
            assert r[D]*256+r[E]==(second&65535) and r[B]==0 and r[C]==visible
            gates+=1;accepted+=allow
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)];cases=wakes=steps=early=0
    def execute(page,height,top,index,direction,presses):
        nonlocal cases,wakes,steps,early
        m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
        put(m,0x4000,baseline);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,[50,83]);m[0x6306]=page;m[0x6548]=1;m[0x9B16]=0x5A
        for address,value in ((0xAEAB,height),(0xAEB3,188),(0xAEBB,3),(0xAEBF,0),(0xAEC7,3),(0xAECB,0),(0xBD26,0),(0xBD73,96),(0xBD7E,114),(0xBD89,136),(0xBD94,154),(0xBD9F,176)):m[address]=value
        for row in range(30):put(m,0x9555+2*row,[1,3]);put(m,0x9852+2*row,[2,4])
        m[0x9555+60]=255;put(m,0xA235,[29,0]);put(m,0xA265,[0x8E,0x70]);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;r[A]=top;r[H],r[L]=index>>8,index&255;r[PC]=0xA1D6;r[IFF]=1
        for address in (0x66EC,0x6585,0x66ED,0x658A):m[address]=0
        frame=baseline.copy();poll=0;expected_index=index;expected_steps=0;case_wakes=0;expected_count=None;is_early=top>=height
        for _ in range(800000):
            pc=r[PC]
            if pc==0x3FFF:break
            if pc==0xA20A:
                assert r[H]*256+r[L]==expected_index
                active=poll<presses;m[0x66ED]=int(active)
                if active:
                    py=191 if direction=='down' else 0;m[0x6308]=py;visible=(height-top)//8
                    threshold=((height//2+3)&255)+(top//2);threshold&=255
                    if visible:
                        if py>threshold:
                            diff=29-expected_index;second=(diff&65535)-visible-int(diff<0)
                            if second>0:expected_index=(expected_index+1)&65535;expected_steps+=1
                        elif expected_index:expected_index-=1;expected_steps+=1
                poll+=1
            if pc==0xA25C:
                assert m[pc]==0x76 and bytes(m.banks[7][:6144])==bytes(frame[:6144])
                reference=bytearray(m[0:65536]);cleared=bytearray(frame);rectangle(cleared,3,3+top,188,3+height+4);reference[0x4000:0x6000]=cleared
                image,_,_,expected_count,_,_,_,_=trade_expected(reference,expected_index,188,height,(3,3));frame=cleared;frame[:6912]=image
                r[PC]+=1;case_wakes+=1
            elif pc==0xA268:
                assert r[H]*256+r[L]==expected_index and m[0x4000:0x6000]==list(frame)
                assert m[0x7063]==expected_count
                s.run()
            else:s.run()
        else:raise AssertionError(('instruction_limit',page,height,top,index,direction,presses,hex(r[PC])))
        assert m[0xC6E3]==top and bytes(m.banks[7][6144:6912])==bytes(baseline[6144:6912])
        assert m[0x6306]==0x10 and m.o7ffd==0x10 and r[SP]==0x8000 and r[IFF]==1
        assert r[8:12]==initial[8:12] and r[18]==initial[18] and r[20:24]==initial[20:24]
        if is_early:
            assert poll==0 and case_wakes==0 and r[H]*256+r[L]==index and m[0x4000:0x6000]==baseline and m[0x9B16]==0x5A;early+=1
        else:
            assert poll==presses+1 and case_wakes==expected_steps and r[H]*256+r[L]==expected_index
            assert (r[A],r[F],r[D],r[E])==(0,0x44,83,50) and m[0x6307:0x6309]==[50,83] and m[0x9B16]==0
            assert bytes(m[0x4000:0x6000])==bytes(pointer_image(frame,station,50,83)),(page,height,top,index,direction,presses,'final_bitmap')
        assert trace.writes==[(0x7FFD,0x17),(0x7FFD,0x10)]+[(0x7FFD,p) for _ in range(case_wakes) for p in (0x17,0x18,0x10)]
        cases+=1;wakes+=case_wakes;steps+=expected_steps
    for page in (0x10,0x18):
        for height in (37,85,181):
            for top in (0,32):
                for index in (0,1,28,29):
                    for direction in ('up','down'):
                        for presses in (1,3):execute(page,height,top,index,direction,presses)
            for top in (height,height+1):execute(page,height,top,5,'down',1)
    report=dict(passed=True,down_gate_cases=gates,accepted_down_gates=accepted,all_index_words=True,visible_row_gate_values=[1,8,31],
                whole_cases=cases,early_height_rejections=early,rendered_steps=steps,explicit_halt_wakeups=wakes,
                real_clear_trade_callback_and_pointer=True,base_bitmap_and_shadow_bitmap_and_attributes_compared=True,
                input_codes_and_pointer_y_mutated_at_poll_boundaries=True,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ScrollWindowVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
