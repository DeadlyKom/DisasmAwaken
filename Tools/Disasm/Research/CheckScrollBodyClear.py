"""Исходное очищающее ядро против прямоугольника с трёхпиксельными полями окна."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,PC,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address


def rectangle(image,left,top,right,bottom):
    # Исходная коррекция вычитает BF после сравнения с C0, нижняя строка 191 при отсечении не очищается.
    left=max(0,left);right=min(255,right);top=max(0,top);bottom=min(190,bottom)
    if left>right or top>bottom:return False
    first,last=left//8,right//8;lm=255>>(left&7);rm=(255<<(7-(right&7)))&255
    for y in range(top,bottom+1):
        start=bitmap_address(y,first)-0x4000;stop=start+last-first
        if first==last:image[start]&=255^(lm&rm)
        else:
            image[start]&=255^lm;image[stop]&=255^rm
            if stop>start+1:image[start+1:stop]=bytes(stop-start-1)
    return True


def main():
    _,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0])
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    baseline=bytes((i*73+(i>>8)*19+17)&255 for i in range(8192));cases=rendered=0;branches=set()
    for width in range(2,33):
        for height in range(3,25):
            positions={(-width,-height),(-1,-1),(0,0),(31,23),(32-width,24-height),(-1,24-height),(32-width,-1)}
            for x,y in sorted(positions):
                text_height=height*8-11
                for offset in sorted({0,min(8,text_height),min(32,text_height)}):
                    m=bytearray(base);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[A]=text_height-offset;r[PC]=0xC6B0
                    ox=(x*8+3)&65535;oy=(y*8+3)&65535
                    for address,value in ((0xAEB3,width*8-4),(0xAEBB,ox&255),(0xAEBF,ox>>8),(0xAEC7,oy&255),(0xAECB,oy>>8),(0xC6E3,offset)):
                        m[address]=value
                    m[0x4000:0x6000]=baseline;m[0x7FFE:0x8000]=bytes([255,63]);expected=bytearray(baseline)
                    visible=rectangle(expected,x*8+3,y*8+3+offset,(x+width)*8-4,(y+height)*8-4)
                    for _ in range(22000):
                        pc=r[PC]
                        if pc==0x3FFF:break
                        if pc in (0xC74D,0xC7AB,0xC804):branches.add(pc)
                        s.run()
                    else:raise AssertionError(('instruction_limit',x,y,width,height,offset,hex(r[PC])))
                    assert m[0x4000:0x6000]==expected,(x,y,width,height,offset,'bitmap')
                    assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:19]==initial[16:19] and r[20:24]==initial[20:24]
                    cases+=1;rendered+=visible
    boundary=[]
    # Проверка нулевого D после отсечения сверху 191, DEC D тогда задаёт 256 строк, включая область за bitmap.
    for x in (-1,0,31):
        m=bytearray(base);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[A]=9;r[PC]=0xC6B0
        ox=(x*8+3)&65535
        for address,value in ((0xAEB3,12),(0xAEBB,ox&255),(0xAEBF,ox>>8),(0xAEC7,187),(0xAECB,0),(0xC6E3,4)):m[address]=value
        m[0x4000:0x6000]=baseline;m[0x7FFE:0x8000]=bytes([255,63]);reference=bytearray(m);touched=set();iterations=0
        for py in range(191,447):
            for px in range(max(0,x*8+3),min(255,(x+2)*8-4)+1):
                address=0x4000+(py//64)*0x800+(py%8)*256+((py%64)//8)*32+px//8
                reference[address]&=255^(128>>(px&7));touched.add(address)
        for _ in range(30000):
            pc=r[PC]
            if pc==0x3FFF:break
            if pc in (0xC74D,0xC7AB,0xC804):iterations+=1
            s.run()
        else:raise AssertionError(('boundary_instruction_limit',x,hex(r[PC])))
        assert iterations==256 and r[SP]==0x8000 and m[0x4000:0x7800]==reference[0x4000:0x7800]
        outside=sorted(a for a in touched if a>=0x5800)
        boundary.append(dict(x=x,rows=iterations,first_write_outside_bitmap=outside[0],last_write_outside_bitmap=outside[-1],written_bytes_outside_bitmap=len(outside)))
    report=dict(passed=True,cases=cases,visible_rectangles=rendered,all_widths_2_32_and_heights_3_24=True,
                negative_origin_and_both_screen_edges=True,top_offsets=[0,8,32],offset_limited_to_text_height=True,
                visited_clear_loops=sorted(branches),whole_bitmap_and_attributes_compared=True,
                independent_pixel_rectangle_reference=True,original_self_modified_jumps_executed=True,
                bottom_clip_preserves_row_191=True,top_191_zero_height_boundaries=boundary,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ScrollBodyClearVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
