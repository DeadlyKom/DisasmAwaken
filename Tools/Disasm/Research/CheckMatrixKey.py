"""Исходный одиночный ввод, десять явных пробуждений HALT и таблица всех 40 сигнатур клавиатуры."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,PC,SP


def add_flags(left,right):
    result=(left+right)&255
    return (result&0xA8)|(0x40 if not result else 0)|((left^right^result)&16)|(4 if (~(left^right)&(left^result)&128) else 0)|int(left+right>255)


class Matrix:
    def __init__(self,keys,empty_cycles):
        self.values={row:255 for row in (0x7F,0xBF,0xDF,0xEF,0xF7,0xFB,0xFD,0xFE)}
        for row,mask in keys:self.values[row]&=mask^255
        self.empty_reads=8*empty_cycles;self.reads=[]

    def read_port(self,registers,port,offset=0):
        assert port&255==0xFE
        self.reads.append(port)
        return 255 if len(self.reads)<=self.empty_reads else self.values[port>>8]


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=[0]*65536;memory[0x6000:]=source
    original=memory[:];dis=decoder(original);simulator=Simulator(memory)
    rows=(0x7F,0xBF,0xDF,0xEF,0xF7,0xFB,0xFD,0xFE)
    keys=[(row,1<<bit) for row in rows for bit in range(5)]
    codes={};entries=[]
    for index,address in enumerate(range(0x96AC,0x9728,2)):
        signature=tuple(memory[address:address+2]);entries.append(signature)
        codes.setdefault(signature,0x1D+index)
    assert len(entries)==62 and set(codes)-{(0,0)}==set(keys)
    assert sum(pair!=(0,0) for pair in entries)==40
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'IX':0x2468,
                           'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    observed={};cases=wakeups=0

    def step():
        pc=simulator.registers[PC]
        assert 0xA116<=pc<0xA163
        instruction=dis.disassemble(pc,pc+1,'h')[0]
        raw=bytes(memory[pc:pc+len(instruction.bytes)]);assert raw==bytes(original[pc:pc+len(raw)])
        observed[f'{pc:04X}']=raw.hex();simulator.run()

    # Проверка одиночных клавиш и всех пар с двумя пустыми полными обходами перед нажатием.
    selected=[(key,) for key in keys]+[(left,right) for i,left in enumerate(keys) for right in keys[i+1:]]
    for pressed,empty_cycles in product(selected,(0,2)):
        matrix=Matrix(pressed,empty_cycles);simulator.set_tracer(matrix)
        memory[0x7FFE:0x8000]=[255,63];simulator.registers[:]=initial;r=simulator.registers;r[PC]=0xA116
        local_wakes=0
        for count in range(3000):
            if r[PC]==0x3FFF:break
            if r[PC]==0xA11B:
                assert memory[r[PC]]==0x76
                observed['A11B']='76';r[PC]+=1;local_wakes+=1
            else:step()
        else:raise AssertionError('Ввод не завершился после заданного нажатия')
        winner=min(pressed,key=keys.index);code=codes[winner]
        assert r[A]==code and r[F]==add_flags(code-0x1D,0x1D)
        assert r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
        assert local_wakes==10
        winner_row=rows.index(winner[0])
        assert matrix.reads==[256*row+0xFE for row in rows]*empty_cycles+[256*row+0xFE for row in rows[:winner_row+1]]
        cases+=1;wakeups+=local_wakes
    # Проверка прямого поиска всех штатных сигнатур и первого нулевого пропуска таблицы.
    direct_cases=0
    for row,mask in keys+[(0,0)]:
        simulator.registers[:]=initial;r=simulator.registers;r[B],r[C],r[PC]=row,mask,0xA14A
        memory[0x7FFE:0x8000]=[255,63]
        while r[PC]!=0x3FFF:step()
        code=codes[row,mask];offset=2*(code-0x1D)
        assert r[A]==code and r[F]==add_flags(code-0x1D,0x1D)
        assert r[6]*256+r[7]==offset and r[B]*256+r[C]==0x6954
        assert r[4:6]==initial[4:6] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
        direct_cases+=1
    assert sum(len(bytes.fromhex(v)) for v in observed.values())==0xA163-0xA116
    report=dict(method='original_matrix_key_scan_with_explicit_halt_wakeups_and_port_values',passed=True,
                source_sha256=hashlib.sha256(source).hexdigest(),scan_cases=cases,direct_lookup_cases=direct_cases,
                modeled_wakeups=wakeups,physical_table_entries=62,active_signatures=40,original_visited=observed,
                irq_executed=False,hardware_input=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MatrixKeyVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
