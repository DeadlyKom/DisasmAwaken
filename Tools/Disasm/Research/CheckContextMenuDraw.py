"""Полный рисователь меню с настоящим ресурсом, рамкой, глифами и фикстурой пробуждения HALT."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,PC,SP
from CheckScreenUpdate import put
from CheckRowHighlight import make_context
from CheckTextStream import reference
from CheckInsetFrame import bitmap_address


def main():
    source,_,banks=make_context();widths=source[0x2900:0x2A00]
    text=list(source[0x832E:0x839A]);assert len(text)==108 and text[-1]==10
    assert source[0x8399:0x839B]==b'\n\n'
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0xF37D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=full=truncated=wakeups=0
    # Проверка всей сетки штатных положений 9 на 9, а также меньших и больших допустимых геометрий.
    geometries=list(product(range(16),range(24),(9,),(9,)))
    geometries += [(row,column,width,height) for width,height in ((2,3),(3,4),(8,8),(10,10),(32,24))
                   for row,column in sorted({(0,0),(24-height,32-width)})]
    for row,column,width,height in geometries:
        memory=SliceableMemory(banks=[bank.copy() for bank in banks],out7ffd=0x10)
        put(memory,0xF37D,[column,row,width,height,0x26,0])
        memory[0x7584]=40;memory[0x757A]=7
        put(memory,0x8500,[0x80,255]*128);put(memory,0x8600,[0x33]*768)
        put(memory,0x4000,[0x96]*8192);put(memory,0x7FFE,[255,63]);memory[0xBD4F]=0xC3
        simulator=Simulator(memory);simulator.registers[:]=initial;r=simulator.registers
        r[PC]=0x7583;positions=[];wakes=0
        for _ in range(150000):
            if r[PC]==0x3FFF:break
            if r[PC]==0xC089:
                assert memory[r[PC]]==0x76
                r[PC]+=1;wakes+=1
            else:
                if r[PC]==0xAE8D:positions.append((r[A],memory[0x6320],memory[0x6321]))
                simulator.run()
        else:raise AssertionError('Рисователь меню не завершился')
        expected=[0x96]*8192
        # Построение полосовой рамки независимо от команд и таблиц рисователя.
        for local_y in range(8*height):
            if local_y in (0,12,8*height-8,8*height-1):left=middle=right=0
            elif local_y in (1,8*height-2):left,middle,right=0x7E,255,0x7E
            else:left,middle,right=0x40,0,2
            address=bitmap_address(row*8+local_y,column)-0x4000
            expected[address:address+width]=[left]+[middle]*(width-2)+[right]
        origin=(8*column+3,8*row+3);ww,wh=8*width-4,(8*height-11)&255
        expected_positions=[]
        consumed,cursor_x,cursor_y,result_a,result_f,_=reference(text,widths,0,0,ww,wh,1,
                  (0,0,0,0,0),origin,0,positions=expected_positions)
        assert positions==expected_positions,(row,column,width,height)
        # Инверсия принятых глифов по физическому шрифту, отвергнутые попытки в поток позиций тоже входят.
        for code,gx,gy in expected_positions:
            if gy>=wh or gx+widths[code]>=ww or gx+widths[code]>255:continue
            px,py=origin[0]+gx,origin[1]+gy
            if px>=256 or py>=185:continue
            for glyph_y in range(8):
                value=source[0x2A00+8*code+glyph_y];address=bitmap_address(py+glyph_y,px//8)-0x4000
                shift=px&7;expected[address]^=value>>shift
                if shift and px//8!=31:expected[address+1]^=(value<<(8-shift))&255
        assert memory[0x4000:0x6000]==expected,(row,column,width,height)
        assert (r[H]*256+r[L],r[A],r[F],r[SP])==(0xE32E+consumed,result_a,result_f,0x8000)
        assert memory[0x6320:0x6322]==[cursor_x,cursor_y]
        assert memory[0x757A]==255 and memory[0xBD26]==1 and wakes==1
        for reg in (*range(2,6),*range(8,12),*range(18,24)):
            assert r[reg]==initial[reg],(reg,r[reg],initial[reg])
        expected_map=[0x33]*768
        for cell_y in range(row,row+height):
            expected_map[32*cell_y+column:32*cell_y+column+width]=[1]*width
        assert memory[0x8600:0x8900]==expected_map
        assert memory[0x8500:0x8502]==[40,0] and memory[0x8502:0x8600]==[0x80,255]*127
        cases+=1;full+=result_a==10 and result_f==0x4A;truncated+=not(result_a==10 and result_f==0x4A);wakeups+=wakes
    report=dict(passed=True,method='original_context_menu_caption_frame_and_font_with_independent_text_and_bitmap_reference',
                cases=cases,full_text=full,truncated_text=truncated,halt_wakeups=wakeups,
                menu_resource_bytes=108,caption_anchor_shared_final_lf=True,caption_text_index=0,
                actual_menu_text_used=True,loader_index_patch_fixture=40,irq_executed=False,
                halt_wakeup_is_fixture=True,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ContextMenuDrawVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
