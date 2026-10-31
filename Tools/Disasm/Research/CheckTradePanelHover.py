"""Торговая строка наведения с изменяемым числом реально нарисованных строк."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,SP
from CheckRowHighlight import make_context,band_parameters
from CheckScreenUpdate import put,PortTrace,pointer_image
from CheckSelectionBand import xor_band


def main():
    station,_,banks=make_context();initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0xF31D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)];cases=changed=0
    def execute(rows,py,last,previous):
        nonlocal cases,changed
        m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
        put(m,0xF31D,[6,2,11,9,0x26]);put(m,0x9CA6,[0,0xE0]);put(m,0xE000,[0,0x5F,0x71,0x70,1,1] if last else [0x71,0x70,0,0x5F,1,1]);put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768))
        put(m,0x6307,[50,py]);m[0x6306]=0x10;m[0x6548]=1;m[0x9B16]=0x5A;m[0x7063]=rows;m[0x7068]=previous
        scene=baseline.copy()
        def invert(image,row):
            params=band_parameters(6,2,11,35,row)
            if params is not None:xor_band(image,*params)
        if previous!=255:invert(scene,previous)
        expected=scene.copy();extent=min(32,(rows*8)&255);hit=51<=py<51+extent;row=(py-51)//8 if hit else None;update=last and hit and row!=previous
        if update:
            if previous!=255:invert(expected,previous)
            invert(expected,row);expected=pointer_image(expected,station,50,py)
        put(m,0x4000,scene);put(m,0x7FFE,[255,63]);s.registers[:]=initial;s.run(start=0x6FEE,stop=0x3FFF);r=s.registers
        assert m[0x4000:0x6000]==expected and m[0x7068]==(row if update else previous)
        assert bool(r[F]&0x40)==(not update) and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
        assert m[0x6306]==0x10 and m.o7ffd==0x10 and m[0x7063]==rows
        cases+=1;changed+=update
    # Проверка всей высоты указателя на основных значениях динамического счётчика.
    for rows in (0,1,5,30):
        for py in range(192):
            for last in (False,True):
                for previous in (255,0,64):execute(rows,py,last,previous)
    # Проверка каждого байта счётчика, в том числе 32, превращающегося в нулевой пиксельный запрос.
    for rows in range(256):
        for py in (0,50,51,58,59,191):
            for last in (False,True):execute(rows,py,last,255)
    report=dict(passed=True,cases=cases,changed_cases=changed,all_dynamic_row_count_bytes=True,entry_hover_jump_executed=True,
                bitmap_and_attributes_compared=True,real_row_hover_and_pointer=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/TradePanelHoverVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
