"""Два исходных рисователя окна, включая ручную инъекцию аппаратного PUSH PC в заимствованный стек."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP,IFF
from CheckInsetFrame import bitmap_address
from CheckStationInterrupt import InterruptPorts


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
    initial=get_registers({'SP':0x7FFE,'HL':0x7000,'DE':0x247A,'BC':0x36C9,'IX':0x2468,
                           'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    bindings=[tuple(memory[a:a+2]) for a in range(0x99B6,0x99C2,2)]
    observed={};body_cases=icon_cases=injections=icon_overflow_cases=icon_attribute_cases=0;irq_stack_positions=set()
    baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)]

    def setup(x,y,width,height):
        memory[0x7FFE:0x8000]=[255,63]
        simulator.registers[:]=initial;r=simulator.registers
        r[B],r[C],r[D],r[E]=y,x,height,width
        simulator.run(start=0xC233,stop=0x3FFF)
        assert memory[0xAEBB]==8*x+3 and memory[0xAEC7]==8*y+3

    def run_body(x,y,width,height,mode,interrupt_slot=None):
        nonlocal body_cases,injections
        setup(x,y,width,height)
        memory[0x4000:0x6000]=baseline
        memory[0x99B4]=mode
        memory[0xA102:0xA116]=original[0xA102:0xA116]
        memory[0x6306]=0x10;memory[0x99B2]=0;memory[0x9B62]=0;memory[0x9B16]=1;memory[0x9B7E]=2
        memory[0x6639]=1;memory[0x65A8]=1
        memory[0x7FFE:0x8000]=[255,63]
        simulator.registers[:]=initial;r=simulator.registers;r[PC]=0xA05B;r[IFF]=1
        simulator.set_tracer(InterruptPorts(bindings,0,0xA5))
        injected=False
        for step in range(18000):
            pc=r[PC]
            if pc==0x3FFF:break
            # Создание аппаратного слова PC только после перехода рисователя на таблицу возвратов.
            if interrupt_slot is not None and not injected and r[SP]==0xA104+2*interrupt_slot:
                saved=r[:];sp=r[SP]-2;memory[sp:sp+2]=list(pc.to_bytes(2,'little'));r[SP]=sp;r[PC]=0x9AEA;r[IFF]=0
                for irq_step in range(1000):
                    if r[PC]==pc:break
                    simulator.run()
                else:raise AssertionError('ISR не вернулся внутрь рисователя')
                assert r[SP]==saved[SP] and r[IFF]==1
                for reg in (*range(12),*range(16,24)):assert r[reg]==saved[reg]
                assert memory[0xA104:0xA116]==original[0xA104:0xA116]
                injections+=1;irq_stack_positions.add(sp);injected=True
            assert 0xA05B<=r[PC]<0xA102,hex(r[PC])
            instruction=dis.disassemble(r[PC],r[PC]+1,'h')[0]
            raw=bytes(memory[r[PC]:r[PC]+len(instruction.bytes)])
            if raw==bytes(original[r[PC]:r[PC]+len(raw)]):observed[f'{r[PC]:04X}']=raw.hex()
            else:assert r[PC] in (0xA0A2,0xA0C0)
            simulator.run()
        else:raise AssertionError('Заливка не завершилась')
        assert interrupt_slot is None or injected
        expected=baseline[:];fill=0 if mode&1 else 255
        for row in range(8*(y+2),8*(y+height-1)):
            address=bitmap_address(row,x+1)-0x4000
            expected[address:address+width-2]=[fill]*(width-2)
        assert memory[0x4000:0x6000]==expected,(x,y,width,height,mode)
        assert r[SP]==0x8000 and r[H]*256+r[L]==0xA102-2*(width-1)
        assert r[D]*256+r[E]==bitmap_address(8*(y+height-1),x+1)
        assert r[B]==0 and r[C]==(bitmap_address(8*(y+height-2),x+1)&255)
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        assert memory[0xA0A3]==fill and memory[0xA0C1:0xA0C3]==[0xFE,0x7F]
        body_cases+=1

    # Проверка всех штатных размеров тела на противоположных краях и обоих значениях разряда заливки.
    for width,height,side,mode in product(range(2,33),range(4,25),(0,1),(0,1)):
        run_body(0 if not side else 32-width,0 if not side else 24-height,width,height,mode)
    # Проверка каждого положения SP, которое достигается восемью возвратами одного знакоместа.
    for width,height,slot,mode in product((2,3,16,32),(4,12,24),range(9),(0,255)):
        run_body(0,0,width,height,mode,slot)
    # Проверка четырёхбайтовой иконки в 32 пиксельные строки с произвольным исходным BC.
    image=[(i*19+0x35)&255 for i in range(128)]
    for x,y,bc in product(range(28),range(20),(0,1,127,128,65535)):
        setup(x,y,6,5);memory[0x4000:0x6000]=baseline;memory[0x7000:0x7080]=image
        memory[0x7FFE:0x8000]=[255,63];simulator.registers[:]=initial;r=simulator.registers
        r[B],r[C],r[PC]=bc>>8,bc&255,0xA020
        for step in range(1100):
            pc=r[PC]
            if pc==0x3FFF:break
            assert 0xA020<=pc<0xA05B
            instruction=dis.disassemble(pc,pc+1,'h')[0]
            raw=bytes(memory[pc:pc+len(instruction.bytes)]);assert raw==bytes(original[pc:pc+len(raw)])
            observed[f'{pc:04X}']=raw.hex();simulator.run()
        else:raise AssertionError('Иконка не завершилась')
        expected=baseline[:];address=bitmap_address(8*(y+1),x+1)
        overflows=attributes=False
        for row in range(32):
            assert 0x4000<=address<0x5FFD
            attributes|=address>=0x5800
            expected[address-0x4000:address-0x4000+4]=image[4*row:4*row+4]
            # Расчёт физического следующего адреса учитывает перенос четырёхбайтового LDI через младший байт.
            end=address+4
            overflows|=end>>8!=address>>8
            high=((end>>8)+1)&255;low=address&255
            if not high&7:
                new_low=low+32
                high=(high-(0 if new_low>255 else 8))&255
                low=new_low&255
            address=256*high+low
        assert memory[0x4000:0x6000]==expected,(x,y,bc,[(hex(0x4000+i),a,b) for i,(a,b) in enumerate(zip(memory[0x4000:0x6000],expected)) if a!=b][:12])
        assert r[SP]==0x8000 and r[H]*256+r[L]==0x7080 and r[B]*256+r[C]==(bc-128)&65535
        assert r[D]*256+r[E]==address
        if x<27:
            assert not overflows and not attributes
            for row in range(32):
                offset=bitmap_address(8*(y+1)+row,x+1)-0x4000
                assert expected[offset:offset+4]==image[4*row:4*row+4]
        assert r[A]==0 and r[F]==0x42
        assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
        icon_cases+=1
        icon_overflow_cases+=overflows;icon_attribute_cases+=attributes
    report=dict(method='original_window_icon_body_and_manual_irq_pc_push',passed=True,
                source_sha256=hashlib.sha256(source).hexdigest(),body_cases=body_cases,icon_cases=icon_cases,
                injected_isr_calls=injections,irq_pc_word_addresses=[f'{a:04X}' for a in sorted(irq_stack_positions)],
                icon_low_byte_overflow_cases=icon_overflow_cases,icon_attribute_write_cases=icon_attribute_cases,
                original_visited=observed,physical_bank_switching=False,hardware_irq_timing=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/WindowGraphicsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
