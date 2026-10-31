"""Развилки торгового действия, реальные список и снятие полосы, выходы к отдельно проверенным дочерним входам."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put


def main():
    _,_,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x7071,'DE':34,'BC':0x36C9,'AF':0x5A5D,'IX':0xF31D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    flat=bytearray(65536);flat[0x4000:0x8000]=bytes(banks[5]);flat[0x8000:0xC000]=bytes(banks[2]);flat[0xC000:]=bytes(banks[0]);s=Simulator(flat);gates=0;codes={9:0,10:0};no_row=0
    def gate(origin,x,row):
        nonlocal gates,no_row
        flat[0xAEBB]=origin;flat[0x6307:0x6309]=bytes([x,83]);flat[0x7068]=row;flat[0x7FFE:0x8000]=bytes([255,63]);s.registers[:]=initial;r=s.registers;r[PC]=0x702F
        for _ in range(25):
            if r[PC] in (0x7044,0x3FFF):break
            s.run()
        else:raise AssertionError('Не завершается выбор торговой колонки')
        if row==255:assert r[PC]==0x3FFF and r[A]==0 and r[SP]==0x8000;no_row+=1
        else:
            expected=10 if ((x-origin)&255)<135 else 9
            assert r[PC]==0x7044 and r[A]==expected and r[H]*256+r[L]==83*256+x and r[SP]==0x7FFE;codes[expected]+=1
        gates+=1
    for origin in range(256):
        for x in range(256):gate(origin,x,0)
    for row in range(256):
        for x in (0,134,135,255):gate(0,x,row)
    whole=early=closed=scrolled=script=empty=0
    for selector in range(256):
        for same_row in (False,True):
            for selected in (0,255):
                m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);s=Simulator(m);s.set_tracer(PortTrace(s));s.registers[:]=initial;r=s.registers;r[A]=selector;r[PC]=0x6FF1
                put(m,0x7072,[34,0]);put(m,0x7D78,[35,0]);put(m,0x5F00,[0x21,63,0,0xC9]);put(m,0x9CA6,[0,0xB4]);put(m,0xB400,[0,0x5F,0x77,0x7D,0x71,0x70,1,1]+[0]*128)
                put(m,0xF31D,[0,0,24,12,6,5]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x6307,[50,3 if same_row else 80]);m[0xAEC7]=3;m[0xAECB]=0;m[0xAEBB]=3;m[0x6306]=0x10
                m[0x9E78]=0;m[0xCA20]=6;m[0x9A82]=0xA7;m[0x6548]=1;m[0x9B16]=0;put(m,0x9A90,[0x58,0x9A]);put(m,0x9A8D,[255,255]);m[0x7068]=selected;m[0x7063]=30;put(m,0x7026,[5,0]);put(m,0x7FFE,[255,63])
                for _ in range(40000):
                    if r[PC] in (0xA1D6,0x7044,0x3FFF):break
                    s.run()
                else:raise AssertionError(('instruction_limit',selector,same_row,selected,hex(r[PC])))
                if selector&128:
                    assert r[PC]==0x3FFF and (r[A],r[F])==(selector,(selector&0xA8)|1) and m[0x9A82]==0xA7;early+=1
                elif selector==1:
                    if selected==255:assert r[PC]==0x3FFF and r[A]==0;empty+=1
                    else:assert r[PC]==0x7044 and r[A]==10;script+=1
                elif same_row:
                    assert r[PC]==0x3FFF and m[0xB400:0xB404]==[0,0x5F,1,1] and m[0x9A82]==0 and r[D]*256+r[E]==35;closed+=1
                else:
                    assert r[PC]==0xA1D6 and (r[A],r[H]*256+r[L],r[SP])==(32,5,0x7FFC)
                    assert m[0x7068]==255 and m[0xA235:0xA237]==[29,0] and m[0xA265:0xA267]==[0x8E,0x70];scrolled+=1
                whole+=1
    report=dict(passed=True,column_gate_cases=gates,column_event_codes=codes,no_selection_gate_cases=no_row,whole_dispatch_cases=whole,
                early_bit7_cases=early,two_panel_close_cases=closed,scroll_dispatch_cases=scrolled,event_dispatch_cases=script,no_selection_returns=empty,
                all_pointer_x_and_origin_low_bytes=True,all_selector_bytes=True,real_repaint_list_and_row_toggle=True,
                child_scroll_report='ScrollWindowVerification.json',script_body_not_executed=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/TradePanelEventVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
