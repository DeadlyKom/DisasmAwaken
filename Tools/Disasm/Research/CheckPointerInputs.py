"""Исходный клавиатурный и джойстиковый опрос с таблицей 16 сочетаний направлений."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,PC,SP
from CheckGlyphRenderer import and_flags


class Ports:
    def __init__(self,bindings,bits):
        self.values={0x1F:bits}
        self.reads=[]
        # Создание согласованных байтов строк, одна строка может содержать несколько проверяемых клавиш.
        for row,mask in bindings:self.values.setdefault(256*row+0xFE,255)
        for (row,mask),bit in zip(bindings,(3,2,1,0,4,5)):
            if bits&(1<<bit):self.values[256*row+0xFE]&=mask^255

    def read_port(self,registers,port,offset=0):
        self.reads.append(port)
        return self.values[port]


def advance(x,y,bits):
    direction=bits&15
    if direction&3==3 or direction&12==12:return x,y
    if direction&1:x=min(255,x+2)
    if direction&2:x=max(0,x-2)
    if direction&4:y=min(191,y+2)
    if direction&8:y=max(0,y-2)
    return x,y


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=[0]*65536;memory[0x6000:]=source
    memory[0x6322:0x7F8C]=source[0x5CE:0x2238]
    original=memory[:];dis=decoder(original)
    bindings=[tuple(memory[a:a+2]) for a in range(0x99B6,0x99C2,2)]
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    simulator=Simulator(memory);observed={};cases=0

    def execute(start,bits,x,y,old,disabled=0):
        nonlocal cases
        memory[0x6639]=disabled
        # Восстановление трёх исходных операндов после штатной инициализации StartStation.
        memory[0x66CD],memory[0x66CF],memory[0x66D1]=2,191,255
        memory[0x6307:0x6309]=[x,y]
        memory[0x66E8:0x66EE]=old
        memory[0x7FFE:0x8000]=[255,63]
        ports=Ports(bindings,bits);simulator.set_tracer(ports)
        simulator.registers[:]=initial;r=simulator.registers;r[PC]=start
        for step in range(180):
            pc=r[PC]
            if pc==0x3FFF:break
            assert 0x6638<=pc<0x6771 and not 0x66D8<=pc<0x670E,hex(pc)
            instruction=dis.disassemble(pc,pc+1,'h')[0]
            raw=bytes(memory[pc:pc+len(instruction.bytes)])
            if raw==bytes(original[pc:pc+len(raw)]):observed[f'{pc:04X}']=raw.hex()
            else:assert pc in (0x6638,0x66CC,0x66CE,0x66D0)
            simulator.run()
        else:raise AssertionError('Опрос не завершился')
        assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        if start==0x6638 and disabled:
            assert not ports.reads and r[2:12]==initial[2:12]
            assert r[A]==disabled and r[F]==and_flags(disabled)
            assert memory[0x6307:0x6309]==[x,y] and memory[0x66E8:0x66EE]==old
        else:
            expected=[value|((bits>>bit)&1) for bit,value in enumerate(old)]
            assert memory[0x66E8:0x66EE]==expected
            xy=advance(x,y,bits)
            assert tuple(memory[0x6307:0x6309])==xy,(start,bits,x,y,memory[0x6307:0x6309],xy)
            assert r[B]*256+r[C]==xy[1]*256+xy[0]
            assert r[D]*256+r[E]==0xBF02
            expected_ports=[0x1F] if start==0x6638 else [256*row+0xFE for row,mask in bindings]
            assert ports.reads==expected_ports,(ports.reads,expected_ports)
        cases+=1

    # Проверка сочетаний, границ и накопления всех старших разрядов входных байтов через OR.
    for start,bits,x,y,value in product((0x6638,0x6641),range(64),(0,1,2,253,254,255),(0,1,2,189,190,191),(0,1,0x80,255)):
        execute(start,bits,x,y,[value]*6)
    # Проверка всех исходных координат для каждого сочетания четырёх направлений.
    for start,direction in product((0x6638,0x6641),range(16)):
        for x in range(256):execute(start,direction,x,96,[0]*6)
        for y in range(192):execute(start,direction,128,y,[0]*6)
    # Проверка любого ненулевого программного запрета джойстика.
    for disabled in range(1,256):execute(0x6638,63,255,191,[0xA5]*6,disabled)
    # Проверка последовательного джойстика и клавиатуры, движение выполняется дважды, флаги объединяются.
    sequence_cases=0
    for first,second in product(range(64),repeat=2):
        execute(0x6638,first,128,96,[0]*6)
        xy=memory[0x6307:0x6309];old=memory[0x66E8:0x66EE]
        execute(0x6641,second,*xy,old)
        assert tuple(memory[0x6307:0x6309])==advance(*advance(128,96,first),second)
        assert memory[0x66E8:0x66EE]==[((first|second)>>b)&1 for b in range(6)]
        sequence_cases+=1
    report=dict(method='original_keyboard_joystick_and_direction_dispatch_with_explicit_port_bytes',passed=True,
                source_sha256=hashlib.sha256(source).hexdigest(),cases=cases,sequence_cases=sequence_cases,
                bindings=[dict(row=row,mask=mask) for row,mask in bindings],original_visited=observed,
                input_upper_bits_zero=True,step=2,max_x=255,max_y=191,irq_executed=False,hardware_input=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/PointerInputsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
