"""Условная инверсия старой строки с настоящими указателем и банковым XOR."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,PC,SP
from CheckRowHighlight import make_context,band_parameters
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckSelectionBand import xor_band


def main():
    station,_,banks=make_context()
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x0203,'BC':0x36C9,'AF':0x5A5D,'IX':0xF2ED,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)];cases=early=drawn=rejected=0
    for page in (0x10,0x18):
        for y,height in ((0,3),(20,4)):
            for row in range(256):
                m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
                put(m,0xF2ED,[6,y,11,height,0x26]);put(m,0x8500,[31,0]);put(m,0x8600,bytes(768))
                put(m,0x6307,[50,83]);m[0x6306]=page;m[0x6548]=0xA5;m[0x9B16]=0x5A
                put(m,0x4000,baseline);put(m,0x7FFE,[255,63]);s.registers[:]=initial;r=s.registers;r[A]=row;r[PC]=0xA26F
                s.run(stop=0x3FFF)
                expected=baseline.copy()
                if row==255:
                    assert not trace.writes and m[0x6548]==0xA5
                    assert (r[A],r[F])==(0,0x51) and r[2:12]==initial[2:12] and r[16:24]==initial[16:24];early+=1
                else:
                    params=band_parameters(6,y,11,3,row)
                    if params is not None:xor_band(expected,*params);drawn+=1
                    else:rejected+=1
                    expected=pointer_image(expected,station,50,83)
                    assert m[0x9B16]==0 and m[0x6548]==0
                assert m[0x4000:0x6000]==expected,(page,y,height,row)
                assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and r[SP]==0x8000
                assert m[0x6306]==page and m.o7ffd==page;cases+=1
    # Проверка обоих состояний Carry и всех остальных входных F на маркере FF без дочерних вызовов.
    m=bytearray(65536);m[0x4000:0x8000]=bytes(banks[5]);m[0x8000:0xC000]=bytes(banks[2]);m[0xC000:]=bytes(banks[0]);s=Simulator(m)
    for flags in range(256):
        m[0x7FFE:0x8000]=bytes([255,63]);s.registers[:]=initial;r=s.registers;r[A]=255;r[F]=flags;s.run(start=0xA26F,stop=0x3FFF)
        assert (r[A],r[F],r[SP])==(0,(flags&1)|0x50,0x8000)
        assert r[2:12]==initial[2:12] and r[16:24]==initial[16:24]
    report=dict(passed=True,whole_cases=cases,early_ff_cases=early,rendered_bands=drawn,rejected_bands=rejected,
                all_input_flags_for_ff=256,all_row_bytes=True,real_pointer_and_banked_xor=True,
                bitmap_and_attributes_compared=True,row_not_limited_to_clamped_height=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/SelectedRowToggleVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
