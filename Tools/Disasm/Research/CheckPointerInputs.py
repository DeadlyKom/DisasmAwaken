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
from CheckGlyphRenderer import and_flags,compare_flags
from CheckStationSpans import add_flags,subtract_flags
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh


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


def dispatch_result(bits,x,y,handler):
    # Расчёт результата исходного шага независимо от исполняемого Z80-кода.
    direction=bits&15
    if direction&3==3 or direction&12==12 or not direction:
        flags=0x20 | (0x40 if bits==0 else 0) | (4 if bits.bit_count()%2==0 else 0)
        return handler,255,flags,68
    hl=(handler&0xFF00)|255 if direction&1 else handler
    if direction&8:
        a=(y-2)&255;flags=subtract_flags(y,2)
    elif direction&4:
        a=y+2;flags=compare_flags(a,191)
    elif direction&2:
        a=(x-2)&255;flags=subtract_flags(x,2)
    else:
        a=(x+2)&255;flags=add_flags(x,2) if x>=254 else compare_flags(a,255)
    # Расчёт M1 выбранного обработчика, 64 выборки подготовки и три фиксации добавляются отдельно.
    if direction==1:step=6 if x>=254 else 7+2*int(x==253)
    elif direction in (2,8):step=4+2*int((x if direction==2 else y)<2)
    elif direction==4:step=5+2*int(y>=189)
    elif direction==6:step=9+int(x<2)+2*int(y>=189)
    elif direction==10:step=8+int(x<2)+2*int(y<2)
    elif direction==9:step=(10 if x>=254 else 11+int(x==253))+2*int(y<2)
    elif direction==5:step=(11 if x>=254 else 12+int(x==253))+2*int(y>=189)
    else:raise AssertionError(direction)
    return hl,a,flags,67+step


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=Memory([0]*65536);memory[0x6000:]=source
    memory[0x6322:0x7F8C]=source[0x5CE:0x2238]
    original=memory[:];dis=decoder(original)
    bindings=[tuple(memory[a:a+2]) for a in range(0x99B6,0x99C2,2)]
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    simulator=Simulator(memory);observed={};cases=0;direct_cases=0;direct_m1=set();entry_m1={start:set() for start in (0x6638,0x6641,0x6688)}

    def execute(start,bits,x,y,old,disabled=0):
        nonlocal cases,direct_cases
        memory[0x6639]=disabled
        # Восстановление трёх исходных операндов после штатной инициализации StartStation.
        memory[0x66CD],memory[0x66CF],memory[0x66D1]=2,191,255
        memory[0x6307:0x6309]=[x,y]
        memory[0x66E8:0x66EE]=old
        memory[0x7FFE:0x8000]=[255,63]
        ports=Ports(bindings,bits);simulator.set_tracer(ports)
        simulator.registers[:]=initial;r=simulator.registers;r[PC]=start
        if start==0x6688:r[A]=bits
        r[F]=(x^y^bits^old[0])&255
        r[14]=(bits+x)&255;r[15]=(bits^y^old[0])&255;r[27]=(x+y)%3
        before=r.copy();memory.writes=[];memory.recording=True
        m1=0
        for step in range(180):
            pc=r[PC]
            if pc==0x3FFF:break
            assert 0x6638<=pc<0x6771 and not 0x66D8<=pc<0x670E,hex(pc)
            instruction=dis.disassemble(pc,pc+1,'h')[0]
            raw=bytes(memory[pc:pc+len(instruction.bytes)])
            if raw==bytes(original[pc:pc+len(raw)]):observed[f'{pc:04X}']=raw.hex()
            else:assert pc in (0x6638,0x66CC,0x66CE,0x66D0)
            old_r=r[15]
            simulator.run()
            delta=(r[15]-old_r)&127
            assert delta in (1,2)
            m1+=delta
        else:raise AssertionError('Опрос не завершился')
        memory.recording=False
        assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        if start==0x6638 and disabled:
            expected_m1=3
            assert not memory.writes
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
            expected_ports=[] if start==0x6688 else [0x1F] if start==0x6638 else [256*row+0xFE for row,mask in bindings]
            assert ports.reads==expected_ports,(ports.reads,expected_ports)
        if not (start==0x6638 and disabled):
            handler=original[0x66EE+2*(bits&15)]+256*original[0x66EF+2*(bits&15)]
            hl,a,flags,expected_m1=dispatch_result(bits,x,y,handler)
            assert (r[6]*256+r[7],r[A],r[F])==(hl,a,flags),(bits,x,y,r[6:8],r[A],r[F],hl,a,flags)
            expected_m1+=0 if start==0x6688 else 5 if start==0x6638 else 39+2*bits.bit_count()
            assert m1==expected_m1,(bits,x,y,m1,expected_m1)
            assert r[15]==refresh(before[15],expected_m1) and all(r[i]==before[i] for i in (14,26,27))
            assert memory.writes==[(0x66E8+i,value) for i,value in enumerate(expected)]+[(0x7FFC,0xD3),(0x7FFD,0x66),(0x6307,xy[0]),(0x6308,xy[1])],memory.writes
            if start==0x6688:direct_cases+=1;direct_m1.add(m1)
        assert m1==expected_m1 and r[15]==refresh(before[15],expected_m1)
        assert all(r[i]==before[i] for i in (14,26,27))
        entry_m1[start].add(m1)
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
    # Проверка прямого общего входа с точными HL/AF, R и всеми десятью CPU-записями.
    for bits,x,y,value in product(range(64),(0,1,2,253,254,255),(0,1,2,189,190,191),(0,1,0x80,255)):
        execute(0x6688,bits,x,y,[value]*6)
    # Проверка всех координат каждой оси отдельно для всех шестнадцати направлений.
    for direction in range(16):
        for x in range(256):execute(0x6688,direction,x,96,[0]*6)
        for y in range(192):execute(0x6688,direction,128,y,[0]*6)
    # Проверка всех начальных F и всех старых байтов накопителя для каждой шестибитной выборки.
    for bits,value in product(range(64),range(256)):
        execute(0x6688,bits,128,96,[value]*6)
    report=dict(method='original_keyboard_joystick_and_direction_dispatch_with_explicit_port_bytes',passed=True,
                source_sha256=hashlib.sha256(source).hexdigest(),cases=cases,sequence_cases=sequence_cases,
                bindings=[dict(row=row,mask=mask) for row,mask in bindings],original_visited=observed,
                all_entry_full_m1_values={f"{k:04X}":sorted(v) for k,v in entry_m1.items()},
                all_entry_exact_hl_af_refresh_and_i_im_iff=True,all_entry_exact_simulator_cpu_writes=True,
                joystick_enabled_prefix_m1=5,joystick_disabled_m1=3,keyboard_prefix_m1="39+2*pressed_bits",
                all_entry_iff_fixture=0,direct_dispatch_cases=direct_cases,direct_full_m1_values=sorted(direct_m1),
                direct_exact_hl_af_and_refresh=True,direct_exact_simulator_memory_write_sequence=True,
                direct_i_im_iff_preserved=True,direct_iff_fixture=0,
                input_upper_bits_zero=True,step=2,max_x=255,max_y=191,irq_executed=False,hardware_input=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/PointerInputsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
