"""Полная торговая панель, заголовок и содержимое против независимых текстовых моделей."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,B,C,PC,SP
from CheckRowHighlight import make_context
from CheckTextStream import reference
from CheckTradeNumericColumns import expected as trade_expected
from CheckInsetFrame import bitmap_address


def main():
    _,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0])
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=numeric=skipped=0
    for height in (3,6,12,24):
        for flags in (0,1):
            for index in (0,1,29):
                for stock in (1,255):
                    m=bytearray(base);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[PC]=0x7071;m[0x7072:0x7074]=bytes([34,0]);m[0x7026:0x7028]=index.to_bytes(2,'little')
                    m[0xF0FD+34*16:0xF0FD+34*16+6]=bytes([0,0,24,height,flags,5]);m[0x8500:0x8600]=bytes([0x80,255])*128;m[0x8600:0x8900]=bytes(768)
                    for row in range(30):m[0x9555+row*2:0x9557+row*2]=bytes([1,3]);m[0x9852+row*2:0x9854+row*2]=bytes([2,4])
                    m[0x9555+2*index]=stock;m[0x9555+60]=255;m[0x7FFE:0x8000]=bytes([255,63]);expected=None;wakes=0;expected_count=None
                    for _ in range(220000):
                        pc=r[PC]
                        if pc==0x3FFF:break
                        if pc==0x707F:
                            widths=m[0x8900:0x8A00];positions=[];origin=(m[0xAEBB]+256*m[0xAEBF],m[0xAEC7]+256*m[0xAECB]);width=m[0xAEB3];height_px=m[0xAEAB]
                            offset,ex,ey,a,f,_=reference(m[0xEBF3:],widths,m[0x6320],m[0x6321],width,height_px,0,(96,114,136,154,176),origin,32,positions=positions)
                            expected=bytearray(m[0x4000:0x5B00])
                            for code,gx,gy in positions:
                                if gy>=height_px or gx+widths[code]>255 or gx+widths[code]>=width:continue
                                px=origin[0]+gx;py=origin[1]+gy
                                if px>255 or py>184:continue
                                for line,bits in enumerate(m[0x8A00+8*code:0x8A08+8*code]):
                                    for bit in range(8):
                                        if px+bit<256 and bits&(128>>bit):expected[bitmap_address(py+line,(px+bit)//8)-0x4000]^=128>>((px+bit)&7)
                            if f&1:
                                expected_count=0;expected_hl=0xEBF3+offset;expected_de=0x247A;expected_cursor=(ex,ey);skipped+=1
                            else:
                                virtual=bytearray(m);virtual[0x4000:0x5B00]=expected;virtual[0x6320],virtual[0x6321]=ex,ey
                                expected,_,expected_cursor,expected_count,expected_de,expected_hl,_,_=trade_expected(virtual,index,width,height_px,origin);numeric+=1
                        if pc==0xC089:assert m[pc]==0x76;r[PC]+=1;wakes+=1
                        else:s.run()
                    else:raise AssertionError(('instruction_limit',height,flags,index,stock,hex(r[PC])))
                    count_flags=0x44 if expected_count==0 else ((expected_count&0xA8)|(0x40 if expected_count==0 else 0)|(0x10 if expected_count%16==0 else 0)|(4 if expected_count==128 else 0))
                    assert (r[A],r[F],m[0x7063],m[0x7068])==(expected_count,count_flags,expected_count,255)
                    assert (r[H]*256+r[L],r[D]*256+r[E],m[0x6320],m[0x6321])==(expected_hl,expected_de,*expected_cursor)
                    assert m[0x4000:0x5B00]==expected and wakes==1 and r[SP]==0x8000
                    assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and m[0xBD26]==0;cases+=1
    # Проверка стандартного отключающего RET в первом байте, callback DrawColumns остаётся отдельным входом.
    for flags in range(256):
        m=bytearray(base);m[0x7071]=0xC9;m[0x7063]=0xA7;m[0x7068]=0x5A;m[0x7FFE:0x8000]=bytes([255,63]);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[F]=flags;before=bytes(m)
        s.run(start=0x7071,stop=0x3FFF)
        assert bytes(m)==before and r[A]==initial[A] and r[F]==flags and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
    report=dict(passed=True,cases=cases,numeric_paths=numeric,header_rejection_paths=skipped,disabled_entry_cases=256,
                row_count_written_to_hover_operand=True,selection_reset_to_ff=True,header_and_numeric_bitmap_compared=True,
                caption_uses_separate_contract=True,real_caption_header_names_numbers_and_glyphs=True,
                explicit_halt_wakeups=cases,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/TradePanelDrawVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
