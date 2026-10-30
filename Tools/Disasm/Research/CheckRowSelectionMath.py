"""Точные байтовые договоры начала строки, ограничения высоты и выбора строки указателем."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMatrixKey import add_flags
from CheckGlyphRenderer import compare_flags,and_flags


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=bytearray(65536);memory[0x6000:]=source
    simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0xF37D,
                           'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    counts={'coordinates':0,'height':0,'selection':0};selection={'above':0,'below':0,'inside':0}

    def run(start,y,height,offset,extent,pointer_y):
        memory[0xF37E]=y;memory[0xF380]=height;memory[0x6308]=pointer_y
        memory[0x7FFE:0x8000]=bytes([255,63]);simulator.registers[:]=initial;r=simulator.registers
        r[D],r[E]=extent,offset
        simulator.run(start=start,stop=0x3FFF)
        assert r[SP]==0x8000 and r[H]*256+r[L]==0x1357
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        return r

    # Проверка всех сочетаний байта Y и смещения, PointerY дополнительно проходит полный байтовый диапазон.
    for y,offset in product(range(256),repeat=2):
        pointer_y=(y*19+offset*7)&255
        r=run(0xA280,y,9,offset,0x24,pointer_y)
        left=(8*y)&255;top=(left+offset)&255
        assert r[A]==top and r[F]==add_flags(left,offset)
        assert r[B]==top and r[C]==pointer_y and r[D]==0x24 and r[E]==offset
        counts['coordinates']+=1
    # Проверка полного диапазона высоты и отступа, включая байтовые вращения и переполнение числа строк.
    for height,offset,requested in product(range(256),range(256),(0,1,2,8,24,31,32,255)):
        r=run(0xA28F,0,height,offset,requested,0)
        rotated=((height<<3)|(height>>5))&255
        available=(rotated-offset-5)&0xF8;wanted=(requested<<3)&255
        assert r[A]==available and r[F]==compare_flags(available,wanted)
        assert r[D]==min(available,wanted) and r[E]==offset
        assert r[B]*256+r[C]==0x36C9
        counts['height']+=1
    # Проверка каждого unsigned начала и PointerY с отказом выше, ниже и внутри выбранной высоты.
    for top,pointer_y,extent in product(range(256),range(256),(0,1,7,8,9,64,191,255)):
        r=run(0xA2A4,0,9,top,extent,pointer_y)
        delta=(pointer_y-top)&255
        if pointer_y<top:
            kind='above';expected_a=delta;expected_c=pointer_y
            expected_f=(compare_flags(pointer_y,top)&~0x28)|(delta&0x28)
        elif delta>=extent:
            kind='below';expected_a=delta;expected_c=pointer_y
            expected_f=(compare_flags(delta,extent)&0xC4)|(delta&0x28)|1
        else:
            kind='inside';expected_a=expected_c=delta//8;expected_f=and_flags(expected_a)
        assert r[A]==expected_a and r[F]==expected_f,(top,pointer_y,extent,r[A],r[F],expected_a,expected_f)
        assert r[B]==top and r[C]==expected_c and r[D]==extent and r[E]==top
        selection[kind]+=1;counts['selection']+=1
    report=dict(method='original_row_selection_byte_arithmetic_with_full_flags',passed=True,
                source_sha256=hashlib.sha256(source).hexdigest(),cases=sum(counts.values()),by_function=counts,
                selection_results=selection,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RowSelectionMathVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
