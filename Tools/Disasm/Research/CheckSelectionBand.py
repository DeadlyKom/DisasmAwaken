"""Побайтовая XOR-полоса банка 1, все маски краёв и длины развёрнутого ядра без физического переключения банков."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckInsetFrame import bitmap_address


def xor_band(screen,y,x,width,edges):
    """Независимый эталон физических XOR-масок, результат меняет переданный экран."""
    # Расчёт отдельных масок по исходным двум битам каждой строки, младшие адреса работают по модулю 256.
    for row in range(8):
        address=bitmap_address(y+row,x);page=address&0xFF00;low=address&255
        if not edges&(1<<((2*row)%8)):
            screen[page+low-0x4000]^=0x1F;low=(low+1)&255
        for column in range(width):screen[page+((low+column)&255)-0x4000]^=255
        if not edges&(1<<((2*row+1)%8)):screen[page+((low+width)&255)-0x4000]^=0xF8


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==7)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source
    simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0,'DE':0x247A,'BC':0x36C9,'IX':0x2468,
                           'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    baseline=bytes((i*73+(i>>8)*19+17)&255 for i in range(8192));cases=0

    def execute(y,x,width,edges):
        nonlocal cases
        memory[0x4000:0x6000]=baseline;memory[0x7FFE:0x8000]=bytes([255,63])
        simulator.registers[:]=initial;r=simulator.registers
        start=bitmap_address(y,x);r[H],r[L]=start>>8,start&255;r[B],r[E]=width,edges
        simulator.run(start=0xC908,stop=0x3FFF)
        expected=bytearray(baseline)
        xor_band(expected,y,x,width,edges)
        assert memory[0x4000:0x6000]==expected,(y,x,width,edges)
        final=bitmap_address(y+8,x)
        carry=not y&7 and (bitmap_address(y+7,x)&255)+32>255
        if y&7:expected_a=y&7
        elif carry:expected_a=(bitmap_address(y+7,x)+32)&255
        else:expected_a=final>>8
        assert r[H]*256+r[L]==final and r[B]==0 and r[C]==(bitmap_address(y+7,x)&255)
        assert r[D]==0x24 and r[E]==edges and r[A]==expected_a and r[F]==0x42|int(carry)
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
        assert memory[0xC91D]==4*(31-width)
        cases+=1

    # Проверка всех 256 чередований двух краёв со всеми 32 длинами и граничными переходами экранного адреса.
    for edges,width,(y,x) in product(range(256),range(32),((0,0),(7,31),(56,0),(120,31),(184,0))):execute(y,x,width,edges)
    # Проверка каждого допустимого Y и столбца с основными режимами обоих, левого и правого краёв.
    for y,x,width,edges in product(range(185),range(32),(0,1,7,15,30,31),(0,0x55,0xAA,255)):execute(y,x,width,edges)
    report=dict(method='original_bank1_xor_selection_band_with_independent_byte_mask_reference',passed=True,
                source_slot=7,source_sha256=hashlib.sha256(source).hexdigest(),cases=cases,
                full_bytes_domain=[0,31],edge_values=256,y_domain=[0,184],x_domain=[0,31],
                physical_byte_wrapping_included=True,physical_bank_switching=False,irq_executed=False,
                native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/SelectionBandVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
