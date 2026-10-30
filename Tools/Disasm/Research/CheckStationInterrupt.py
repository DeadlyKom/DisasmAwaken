"""Исходный ISR с реальным опросом и указателем, музыкальный тик заменён договором, физические банки не переключаются."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,PC,SP,I,IFF
from CheckPointerInputs import Ports,advance
from CheckScreenUpdate import pointer_image


class InterruptPorts(Ports):
    def __init__(self,bindings,bits,mixer):
        super().__init__(bindings,bits)
        self.values.update({0xFADF:255,0xFBDF:43,0xFFDF:212})
        self.ay=[0]*16;self.ay[7:11]=[mixer,7,8,9]
        self.selected=0;self.outputs=[]

    def read_port(self,registers,port,offset=0):
        if port==0xFFFD:
            self.reads.append(port)
            return self.ay[self.selected]
        return super().read_port(registers,port,offset)

    def write_port(self,registers,port,value,offset=0):
        self.outputs.append((port,value))
        if port==0xFFFD:self.selected=value
        elif port==0xBFFD:self.ay[self.selected]=value
        else:assert port==0x7FFD


def bcd(value):return (value//10)*16+value%10


def packed(value):
    result=[]
    for index in range(4):result.append(bcd(value%100));value//=100
    return result


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=[0]*65536;memory[0x6000:]=source
    memory[0x6322:0x7F8C]=source[0x5CE:0x2238]
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    for region in flow:
        if region['name']=='StationBoot':
            for instruction in region['instructions']:
                if 0x41B7<=instruction['address']<0x41E3:
                    raw=bytes.fromhex(instruction['hex']);assert raw==source[instruction['offset']:instruction['offset']+len(raw)]
                    memory[instruction['address']:instruction['address']+len(raw)]=raw
    simulator=Simulator(memory);simulator.run(start=0x41B7,stop=0x41E3)
    original=memory[:];dis=decoder(original)
    bindings=[tuple(memory[a:a+2]) for a in range(0x99B6,0x99C2,2)]
    initial=get_registers({'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0xA5CF,
                          'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                          '^BC':0x58BE,'^AF':0x69CF,'I':0x9A},None,False)
    words=bytes(memory[0xA104:0xA116]);assert words==b''.join(a.to_bytes(2,'little') for a in range(0xA0A6,0xA0B8,2))
    clock_addresses=(0x983E,0x983D,0x983B,0x983C)
    counters=(0,1,2,50,255);times=(0,98,99,9999,999999,99999999)
    cases=music_calls=stack_repairs=0;observed={}
    mutable={0x9B15,0x9B61,0x9B71,0x9B7D,0x9C0C,0x9C10}

    def execute(old,mode,cached,blocked,counter,time,cpu_sp,bits,mixer):
        nonlocal cases,music_calls,stack_repairs
        memory[0x6306]=old;memory[0x99B2]=mode
        memory[0x9B62],memory[0x9B72],memory[0x9B16],memory[0x9B7E]=cached,0x5A,blocked,counter
        for address,value in zip(clock_addresses,packed(time)):memory[address]=value
        memory[0x9A99]=0xA5
        memory[0x66CD],memory[0x66CF],memory[0x66D1]=2,191,255
        memory[0x6639]=0;memory[0x65A8]=0
        memory[0x65C7:0x65C9]=[0,0];memory[0x65CC],memory[0x65D1]=0,5
        memory[0x6585:0x658E]=[0]*7+[43,212]
        memory[0x66E8:0x66EE]=[0xA5]*6
        memory[0x6307:0x6309]=[100,100]
        memory[0x6548]=0xA5;memory[0x8600:0x8900]=[0]*768
        screen=[0x96]*6912;memory[0x4000:0x5B00]=screen
        memory[0xA104:0xA116]=words
        # Создание только аппаратного PUSH PC в исходном стеке, SP может указывать внутрь таблицы возвратов рисователя.
        interrupt_sp=cpu_sp-2;memory[interrupt_sp:interrupt_sp+2]=[0,0x50]
        ports=InterruptPorts(bindings,bits,mixer);simulator.set_tracer(ports)
        simulator.registers[:]=initial;r=simulator.registers;r[SP]=interrupt_sp;r[PC]=0x9AEA
        ticks=0
        for step in range(1800):
            pc=r[PC]
            if pc==0x5000:break
            if pc==0xDB05:
                ticks+=1
                assert r[IFF]==0
                # Подмена музыкального тика намеренно меняет все сохраняемые ISR регистры.
                for reg in (*range(12),*range(16,24)):r[reg]=(reg*37+0x51)&255
                sp=r[SP];r[PC]=memory[sp]+256*memory[sp+1];r[SP]=sp+2
                continue
            if 0x9AEA<=pc<0x9C13:
                instruction=dis.disassemble(pc,pc+1,'h')[0]
                raw=bytes(memory[pc:pc+len(instruction.bytes)])
                if raw==bytes(original[pc:pc+len(raw)]):observed[f'{pc:04X}']=raw.hex()
                else:assert pc in mutable,hex(pc)
            simulator.run()
        else:raise AssertionError('ISR не завершился')
        assert r[SP]==cpu_sp and r[I]==initial[I] and r[IFF]==1
        for reg in (*range(12),*range(16,24)):assert r[reg]==initial[reg],(reg,r[reg],initial[reg])
        assert memory[0xA104:0xA116]==list(words)
        assert memory[0x9C0D:0x9C0F]==list(cpu_sp.to_bytes(2,'little')) and memory[0x9C11:0x9C13]==[0,0x50]
        assert memory[0x6306]==old
        pages=[value for port,value in ports.outputs if port==0x7FFD]
        assert pages==[(old&0xF8)|0x10]+([(old&0xF8)|0x13] if mode==0x81 else [])+[old]
        assert ticks==int(mode==0x81)
        assert memory[0x9B62]==(0x81 if mode==0x81 else cached)
        if mode==0x81:
            assert ports.ay[7:11]==([0x5A if cached!=0x81 else mixer,7,8,9])
            assert memory[0x9B72]==0x5A
        elif cached!=mode:
            assert ports.ay[7:11]==[255,0,0,0] and memory[0x9B72]==mixer
        else:
            assert ports.ay[7:11]==[mixer,7,8,9] and memory[0x9B72]==0x5A
        updated_time=(time+1)%100000000 if counter==1 else time
        assert [memory[a] for a in clock_addresses]==packed(updated_time)
        assert memory[0x9B7E]==(50 if counter==1 else (counter-1)&255)
        assert memory[0x9A99]==(int(time%100==99) if counter==1 else 0xA5)
        xy=advance(*advance(100,100,bits),bits)
        assert tuple(memory[0x6307:0x6309])==xy
        assert memory[0x66E8:0x66EE]==[(bits>>b)&1 for b in range(6)]
        drawn=not blocked and bool(bits&15)
        assert memory[0x4000:0x5B00]==(pointer_image(screen,source,*xy) if drawn else screen)
        music_calls+=ticks;stack_repairs+=cpu_sp!=0x8000;cases+=1

    # Проверка ветвей звука, делителя и переноса BCD при обычном и заимствованном CPU-стеке.
    for old,mode,cached,blocked,counter,time in product((0,8,16,31),(0,7,0x81),(0,7,0x81),(0,1),counters,times):
        index=cases
        execute(old,mode,cached,blocked,counter,time,0x8000 if index&1 else 0xA104+2*(index%10),
                (0,1,2,4,8,15,16,32,63)[index%9],(0,0xA5,255)[index%3])
    # Проверка всех 256 значений делителя, полных байтов режима и всех незаблокированных исходных страниц.
    for value in range(256):execute(value%32,value,value^0x81,value&1,value,99999999,0xA104+2*(value%10),value&63,0xA5)
    report=dict(method='original_station_isr_with_real_inputs_and_pointer_music_contract_stub',passed=True,cases=cases,
                source_sha256=hashlib.sha256(source).hexdigest(),music_contract_calls=music_calls,borrowed_stack_cases=stack_repairs,
                original_visited=observed,physical_bank_switching=False,hardware_interrupt_entry=False,
                modeled_hardware_pc_push=True,irq_hardware_timing=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/StationInterruptVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
