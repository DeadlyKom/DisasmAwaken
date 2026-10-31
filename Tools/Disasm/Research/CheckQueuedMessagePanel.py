"""Исходная панель уведомлений и независимая компоновка текста после рамки."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckJustifiedText import reference
from CheckInsetFrame import bitmap_address


def main():
    _,_,banks=make_context();base=bytearray(65536)
    base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0])
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    starts=[];cursor=0xCE19;rows=[]
    # Чтение исходных четырнадцати проверяемых сообщений без вывода о конце всей таблицы.
    for _ in range(14):
        assert base[cursor]==10;start=cursor+1;end=base.index(10,start)
        starts.append(start);rows.append(bytes(base[start:end]).decode('cp866'));cursor=end
    cases=glyphs=0
    for row,start in enumerate(starts):
        for x,y,w,h in ((7,5,18,8),(2,1,28,20),(4,3,12,3)):
            for flags in (0,1):
                m=bytearray(base);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[PC]=0x6E8A
                m[0x6E8B:0x6E8D]=bytes([10,0]);m[0x6E91]=row
                m[0xF0FD+160:0xF0FD+166]=bytes([x,y,w,h,flags,20]);m[0x8500:0x8600]=bytes([0x80,255])*128;m[0x8600:0x8900]=bytes(768)
                m[0x7FFE:0x8000]=bytes([255,63]);expected=None;caption_af=None;wakes=0
                for _ in range(150000):
                    pc=r[PC]
                    if pc==0x3FFF:break
                    if pc==0x6E90:caption_af=list(r[16:18])
                    if pc==0xADCD:
                        assert r[H]*256+r[L]==start
                        widths=m[0x8900:0x8A00];positions=[];origin=(m[0xAEBB]+256*m[0xAEBF],m[0xAEC7]+256*m[0xAECB])
                        layout=reference(pc,m[start:],widths,m[0x6320],m[0x6321],m[0xAEB3],m[0xAEAB],r[B]*256+r[C],r[D],r[E],positions,origin)
                        expected=bytearray(m[0x4000:0x5B00])
                        for code,gx,gy in positions:
                            if gy>=m[0xAEAB] or gx+widths[code]>255 or gx+widths[code]>=m[0xAEB3]:continue
                            px=(origin[0]+gx)&65535;py=(origin[1]+gy)&65535
                            if px>255 or py>184:continue
                            for line,bits in enumerate(m[0x8A00+8*code:0x8A08+8*code]):
                                for bit in range(8):
                                    if px+bit<256 and bits&(128>>bit):expected[bitmap_address(py+line,(px+bit)//8)-0x4000]^=128>>((px+bit)&7)
                            glyphs+=1
                    if pc==0xC089:assert m[pc]==0x76;r[PC]+=1;wakes+=1
                    else:s.run()
                else:raise AssertionError(('instruction_limit',row,x,y,w,h,flags,hex(r[PC])))
                offset,ex,ey,a,f,bc,d,e,_=layout
                actual=(r[H]*256+r[L],m[0x6320],m[0x6321],r[A],r[F],r[B]*256+r[C],r[D],r[E])
                assert actual==(start+offset,ex,ey,a,f,bc,d,e),(row,x,y,w,h,flags,actual,layout)
                assert expected is not None and m[0x4000:0x5B00]==expected
                assert wakes==1 and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and r[16:18]==caption_af
                assert m[0x6E91]==row and m[0xBD26]==0;cases+=1
    report=dict(passed=True,cases=cases,source_rows_checked=rows,row_indices_checked=list(range(14)),
                independently_composed_glyphs=glyphs,whole_content_bitmap_and_attributes_compared=True,
                frame_uses_separate_caption_contract=True,real_caption_justify_and_glyph_code=True,
                explicit_halt_wakeups=cases,full_table_size_not_inferred=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/QueuedMessagePanelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='source_rows_checked'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
