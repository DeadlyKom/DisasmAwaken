"""Опрос исходных инструкций мыши с заданными байтами портов, без IRQ и физического устройства."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm'), str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckGlyphRenderer import and_flags


class Ports:
    def __init__(self,buttons,x,y):
        self.buttons=list(buttons)
        self.x,self.y=x,y
        self.reads=[]

    def read_port(self,registers,port,offset=0):
        self.reads.append(port)
        if port==0xFADF:
            assert self.buttons
            return self.buttons.pop(0)^255
        return {0xFBDF:self.x,0xFFDF:self.y}[port]


def signed(value):return value-256 if value&128 else value


def axis(position,delta,limit):
    if delta<0:return max(0,position+2*delta)
    if delta>0:return min(limit,position+2*delta)
    return position


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=[0]*65536
    memory[0x6000:]=source
    memory[0x6322:0x7F8C]=source[0x5CE:0x2238]
    original=memory[:]
    dis=decoder(original)
    simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    observed={}
    cases=0
    calibrated=0

    def execute(x,y,dx,dy,buttons,configured=True,swap=False,disabled=0):
        nonlocal cases,calibrated
        memory[0x65C7:0x65C9]=[0,0] if configured else original[0x65C7:0x65C9]
        memory[0x65CC],memory[0x65D1]=(5,0) if swap else (0,5)
        memory[0x65A8]=disabled
        memory[0x6585:0x658E]=[0xA5]*7+[43,212]
        memory[0x6307:0x6309]=[x,y]
        memory[0x7FFE:0x8000]=[255,63]
        rawx,rawy=(43+dx)&255,(212-dy)&255
        ports=Ports(buttons,rawx,rawy)
        simulator.set_tracer(ports)
        simulator.registers[:]=initial
        r=simulator.registers
        r[PC]=0x65A7
        # Создание независимого результата по знаковым разностям и порядку первого нажатия.
        expected=[0]*7
        effective_buttons=buttons[-1] if buttons else 0
        new_swap=swap
        stays_unconfigured=not configured and not (buttons[0]&3) if buttons else False
        if not disabled:
            if not configured and buttons[0]&3:
                new_swap=swap if buttons[0]&3==1 else True
                calibrated+=1
            if not stays_unconfigured:
                expected[5 if new_swap else 0]=effective_buttons&1
                expected[0 if new_swap else 5]=(effective_buttons>>1)&1
                expected[6]=(effective_buttons>>2)&1
            expected[4 if dx<0 else 3]=int(dx!=0)
            expected[1 if dy<0 else 2]=int(dy!=0)
        for step in range(220):
            pc=r[PC]
            if pc==0x3FFF:break
            assert 0x658E<=pc<0x6638,hex(pc)
            instruction=dis.disassemble(pc,pc+1,'h')[0]
            raw=bytes(memory[pc:pc+len(instruction.bytes)])
            if raw==bytes(original[pc:pc+len(raw)]):observed[f'{pc:04X}']=raw.hex()
            elif pc in (0x65C7,0x65C8):assert memory[pc]==0
            else:assert pc in (0x65A7,0x65CA,0x65CF)
            simulator.run()
        else:raise AssertionError('Опрос не завершился')
        assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        if disabled:
            assert not ports.reads and memory[0x6585:0x658E]==[0xA5]*7+[43,212]
            assert memory[0x6307:0x6309]==[x,y]
            assert r[2:12]==initial[2:12] and r[A]==disabled and r[F]==and_flags(disabled)
        else:
            assert memory[0x6585:0x658C]==expected,(x,y,dx,dy,buttons,configured,swap,memory[0x6585:0x658C],expected)
            xy=[axis(x,dx,254),axis(y,dy,191)]
            assert memory[0x6307:0x6309]==xy,(x,y,dx,dy,memory[0x6307:0x6309],xy)
            assert memory[0x658C:0x658E]==[rawx,rawy]
            assert r[H]*256+r[L]==xy[1]*256+xy[0]
            assert r[D]*256+r[E]==212*256+43 and r[B]*256+r[C]==0xFFDF
            assert not ports.buttons
            assert ports.reads==[0xFADF]*(1 if configured or stays_unconfigured else 2)+[0xFBDF,0xFFDF]
            assert memory[0x65C7:0x65C9]==(original[0x65C7:0x65C9] if stays_unconfigured else [0,0])
            assert (memory[0x65CC],memory[0x65D1])==((5,0) if new_swap else (0,5))
        cases+=1

    # Проверка всех знаковых разностей для каждого байтового положения каждой оси.
    for position in range(256):
        for delta in range(-128,128):
            execute(position,96,delta,0,[0])
            execute(128,position,0,delta,[0])
    # Проверка всех байтов кнопок в обоих вариантах настройки и первого обмена кнопок.
    for buttons in range(256):
        for swap in (False,True):execute(128,96,1,-1,[buttons],swap=swap)
        for first in (0,1,2,3,4,5,6,7):
            execute(128,96,1,-1,[first,buttons] if first&3 else [first],configured=False)
    # Проверка любого ненулевого программного запрета без чтения портов и очистки состояния.
    for disabled in range(1,256):execute(255,255,0,0,[],disabled=disabled)
    assert sum(len(bytes.fromhex(v)) for v in observed.values())==0x6638-0x658E
    report=dict(method='original_mouse_poll_with_explicit_port_bytes',passed=True,cases=cases,
                source_sha256=hashlib.sha256(source).hexdigest(),axis_cases=131072,calibration_cases=calibrated,
                original_visited=observed,irq_executed=False,hardware_mouse=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MouseInputVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
