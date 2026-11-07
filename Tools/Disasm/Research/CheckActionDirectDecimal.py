"""Две исходные обёртки 6010 и 6029, реальный вывод и игнорируемая запись в ROM."""
from collections import Counter
from itertools import product
import json
from CheckActionTextQueueCalls import Memory, Ports, payload
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
import ReferenceControlsTextDisplay as reference


def main():
    memory=Memory(banks=[[0xA5]*16384 for _ in range(8)],out7ffd=16)
    action=payload(17)
    for index,value in enumerate(action):memory[0x6000+index]=value
    for index,value in enumerate(action[0x23D:0x21CC]):memory[0x6000+index]=value
    for slot,offset in ((22,0),(23,0x1ADE)):
        raw=payload(slot);memory.banks[1][offset:offset+len(raw)]=raw
    memory.out7ffd(17)
    virtual=list(memory[0:65536]);reference.initialize(virtual)
    memory.banks[1][:]=virtual[0xC000:]
    memory.out7ffd(16)
    baseline=[list(bank) for bank in memory.banks]
    roms=[list(rom) for rom in memory.roms]
    simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports)
    cases=0;counts=Counter();targets=set();depth=0
    for entry,value,column in product((0x6010,0x6029),range(256),(0,1,21,22,23,24,255)):
        memory.recording=False
        for bank in (1,2,5):memory.banks[bank][:]=baseline[bank]
        memory.out7ffd(17)
        for address in range(0x4000,0x5B00):memory[address]=(address*73+(address>>8)*29+cases*31)&255
        memory[reference.COLUMN]=column
        virtual=list(memory[0:65536]);events=[]
        # Расчёт настоящего десятичного текста независимой моделью рисователя и прокрутки.
        reference.decimal(virtual,value,events)
        if entry==0x6010:
            events.append(('scroll',));reference.scroll(virtual)
        target=virtual[reference.COLUMN]*256+15
        assert 0x010F<=target<=0x180F
        targets.add(target)
        expected=[list(bank) for bank in memory.banks]
        expected[5][:]=virtual[0x4000:0x8000];expected[1][:]=virtual[0xC000:]
        memory.out7ffd(16)
        stack=0xBFFE
        memory[stack],memory[stack+1]=255,63
        expected[2][stack&0x3FFF]=255;expected[2][(stack+1)&0x3FFF]=63
        initial=get_registers({'PC':entry,'SP':stack,'AF':value*256+(cases&255),
            'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0x6900|((cases^0xA5)&255),'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC},None,False)
        initial[14],initial[26],initial[27]=cases&255,cases&1,cases%3
        simulator.registers[:]=initial
        ports.events=[];memory.writes=[];memory.recording=True
        observed=[];child_state=None
        for _ in range(16000):
            pc=simulator.registers[PC]
            if pc==0x3FFF:break
            if pc==0xEFC4:observed.append(('glyph',simulator.registers[0]))
            if pc==0xED28:observed.append(('scroll',))
            if pc==(0x601D if entry==0x6010 else 0x6033):child_state=list(simulator.registers)
            simulator.run()
        else:raise AssertionError(('нет возврата',hex(entry),value,column))
        memory.recording=False
        assert observed==events and child_state is not None
        assert simulator.registers[6]*256+simulator.registers[7]==target
        assert simulator.registers[0]==16
        # Проверка регистров обёртки относительно результата настоящего последнего дочернего вызова.
        wanted=list(child_state)
        wanted[6],wanted[7]=target>>8,target&255
        wanted[0]=16;wanted[PC]=0x3FFF;wanted[SP]=stack+2
        if entry==0x6029:
            old=roms[1][target];new=(old+1)&255
            wanted[1]=(child_state[1]&1)|(new&0xA8)|(0x40 if new==0 else 0)|(
                0x10 if old&15==15 else 0)|(0x04 if old==127 else 0)
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared)
        assert all(initial[i]==simulator.registers[i] for i in (8,9,10,11,14,22,23,26,27))
        # Проверка всей RAM вне фактически использованного временного CPU-стека и операнда его сохранения.
        stack_writes=[offset for bank,offset,_ in memory.writes if bank==2 and 0x3F00<=offset<0x3FFE]
        low=min(stack_writes);depth=max(depth,0x3FFE-low)
        expected[2][low:0x3FFE]=memory.banks[2][low:0x3FFE]
        for address in (0xEFC1,0xEFC2):expected[1][address&0x3FFF]=memory.banks[1][address&0x3FFF]
        assert memory.banks==expected
        assert [list(rom) for rom in memory.roms]==roms
        assert ports.events==[(0x7FFD,17),(0x7FFD,16)] and memory.o7ffd==16
        counts[hex(entry)]+=1;cases+=1
    result=dict(passed=True,total_cases=cases,cases_by_entry=dict(counts),
        input_bytes_exhausted=True,column_fixtures=[0,1,21,22,23,24,255],
        actual_decimal_glyphs_and_scrolling_executed=True,independent_screen_and_glyph_event_model=True,
        actual_registers_compared_with_post_child_boundary=True,independent_full_child_register_oracle=False,
        all_ram_outside_stack_and_saved_sp_operand_compared=True,
        ignored_rom_targets=sorted(targets),both_roms_unchanged=True,
        maximum_stack_bytes=depth,temporary_stack_values_independently_proved=False,
        runtime_caller_found=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionDirectDecimalVerification.json').write_text(
        json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key!='ignored_rom_targets'},indent=2))


if __name__=='__main__':main()

