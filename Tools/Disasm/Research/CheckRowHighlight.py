"""Банковый вызов подсветки строки, исходные инструкции и независимая пиксельная модель."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckScreenUpdate import PortTrace,put
from CheckSelectionBand import xor_band
from CheckInsetFrame import bitmap_address


def rotate3(value):
    return ((value<<3)|(value>>5))&255


def band_parameters(x,y,width,offset,row):
    top=(rotate3(row)+((y*8+offset)&255))&255
    if top>=184:return None
    signed=x if x<128 else x-256
    if x+width>=33 and x+width<256:
        count,edges=(31-x)&255,0xAA
    elif signed<0:
        count,edges=(width+x-1)&255,0x55
    else:
        count,edges=(width-2)&255,0
    return top,max(signed,0),count,edges


def make_context():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    def load(slot):
        entry=next(e for e in manifest['entries'] if e['slot']==slot)
        return (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    station,map_source=load(4),load(7)
    memory=SliceableMemory(banks=[[0]*16384 for _ in range(8)],out7ffd=0x10)
    put(memory,0x6000,station);put(memory,0x6322,station[0x5CE:0x2238])
    memory.banks[1][:len(map_source)]=list(map_source)
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    for region in flow:
        if region['name']=='StationBoot':
            for instruction in region['instructions']:
                if 0x41B7<=instruction['address']<0x41E3:
                    raw=bytes.fromhex(instruction['hex'])
                    assert raw==station[instruction['offset']:instruction['offset']+len(raw)]
                    put(memory,instruction['address'],raw)
    Simulator(memory).run(start=0x41B7,stop=0x41E3)
    return station,map_source,[bank.copy() for bank in memory.banks]


def main():
    station,map_source,base=make_context()
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)]
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0xF37D,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=rendered=rejected=ports=0

    def execute(x,y,width,offset,row,old,pointer_entry=False,pointer_y=0,height=64):
        nonlocal cases,rendered,rejected,ports
        memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=old)
        put(memory,0x4000,baseline);put(memory,0xF37D,[x,y,width,9])
        memory[0x6306]=old;memory[0x6308]=pointer_y
        put(memory,0x7FFE,[255,63])
        simulator=Simulator(memory);trace=PortTrace(simulator);simulator.set_tracer(trace)
        simulator.registers[:]=initial;r=simulator.registers
        r[A],r[D],r[E]=row,height,offset
        start=0xA2B4 if pointer_entry else 0xA2BB
        before0=memory.banks[0].copy();before1=memory.banks[1].copy()
        simulator.run(start=start,stop=0x3FFF)
        expected=baseline.copy();base_y=(y*8+offset)&255
        hit=pointer_y>=base_y and pointer_y-base_y<height
        chosen=(pointer_y-base_y)//8 if pointer_entry and hit else row
        params=band_parameters(x,y,width,offset,chosen) if not pointer_entry or hit else None
        if params is not None:
            top,column,count,edges=params
            assert 0<=count<=31,(x,y,width,offset,row,params)
            xor_band(expected,top,column,count,edges)
            final=(old&0xF8)|0x10
            parity=not final.bit_count()%2
            expected_f=(final&0xA8)|(0x80 if final&128 else 0)|(4 if parity else 0)
            assert (r[A],r[F],r[D],r[E],r[B])==(final,expected_f,chosen,edges,0)
            assert r[H]*256+r[L]==bitmap_address(top+8,column)
            assert r[C]==bitmap_address(top+7,column)&255
            assert trace.writes==[(0x7FFD,(old&0xF8)|0x11),(0x7FFD,final)]
            before1[0x91D]=4*(31-count)
            assert memory[0x6306]==final and memory.o7ffd==final
            rendered+=1
        else:
            assert not trace.writes and memory[0x6306]==old and memory.o7ffd==old
            assert r[H]*256+r[L]==0x1357
            assert r[D]==(height if pointer_entry and not hit else chosen) and r[E]==offset
            assert r[B]==base_y
            assert r[C]==((pointer_y-base_y)//8 if pointer_entry and hit else pointer_y)
            if pointer_entry and not hit:assert r[F]&1
            rejected+=1
        assert memory[0x4000:0x6000]==expected,(start,x,y,width,offset,row,pointer_y)
        assert memory.banks[0]==before0 and memory.banks[1]==before1
        for page in (3,4,6,7):assert memory.banks[page]==base[page]
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
        cases+=1;ports+=len(trace.writes)

    # Проверка нормальных и отсечённых ширин, байтовых переполнений Y и старых управляющих битов страницы.
    for width in range(2,33):
        for x,y,offset,row in product(sorted({1-width,-1,0,31,32-width}),(0,1,15,22,23),(0,3,255),(0,1,7,31,64,255)):
            execute(x&255,y,width,offset,row,(0,8,0x10,0x18)[cases%4])
    # Проверка всех штатных строк, включая нижнюю область, которую сравнение с 184 отвергает.
    for y,width,row in product(range(24),range(2,33),range(8)):
        execute(0,y,width,3,row,(0,8,0x10,0x18)[cases%4])
    # Проверка повторного определения строки указателя, все значения Y и граничные высоты области.
    for pointer_y,y,height in product(range(256),(0,1,15,22,23),(0,1,8,64,255)):
        execute(0,y,9,3,0,(0,8,0x10,0x18)[cases%4],True,pointer_y,height)
    report=dict(passed=True,method='original_station_row_highlight_with_eight_physical_banks_and_independent_xor_reference',
                cases=cases,rendered=rendered,rejected=rejected,out_writes=ports,banks_modeled=8,
                station_sha256=hashlib.sha256(station).hexdigest(),map_sha256=hashlib.sha256(map_source).hexdigest(),
                bank0_preserved=True,bank1_only_width_operand_changes=True,rom1_forced=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RowHighlightVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
