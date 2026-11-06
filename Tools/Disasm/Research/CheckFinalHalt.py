"""Остановка на HALT без аппаратного IRQ, все флаги и шесть битов защёлки 7FFD."""
from collections import Counter
import json
from CheckFinal import ROOT,original_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace


def main():
    flat=original_memory();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5]=bytearray(flat[0x4000:0x8000])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0
    for paging in range(64):
        for flags in range(256):
            memory.recording=False
            for bank in range(8):memory.banks[bank][:]=base[bank]
            memory.out7ffd(paging)
            initial=get_registers({'AF':((flags*73)&255)*256+flags,
                'HL':0x1234,'DE':0x5678,'BC':0x9ABC,'IX':0xDEF0,'IY':0x5C3A,
                '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                'SP':0xBFFE,'PC':0x6148},None,False)
            initial[14],initial[26],initial[27]=flags,flags&1,paging%3
            expected=[bytearray(b) for b in memory.banks]
            selected=paging if paging&32 else 31
            bank=selected&7
            # Очистка 768 атрибутов фактически выбранного банка, блокировка 7FFD сохраняет старый банк.
            expected[bank][0x1800:0x1B00]=bytes(768)
            writes=[(bank,i,0) for i in range(0x1800,0x1B00)]
            wanted=list(initial)
            wanted[0:8]=[31,(flags&0xC1)|0x28,0,0,0xDB,0,0xDA,0xFF]
            wanted[14],wanted[PC],wanted[26],wanted[27],wanted[28]=0x3C,0x616B,0,0,1
            simulator.registers[:]=initial
            ports=PortTrace(simulator);simulator.set_tracer(ports)
            memory.writes=[];memory.recording=True
            simulator.run(start=0x6148,stop=0x616B)
            # Проверка остановки при IFF=0, HALT не является возвратом или продолжением в Interrupt.
            simulator.run();memory.recording=False
            compared=(*range(15),*range(16,25),26,27,28)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(paging,flags,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert ports.writes==[(0x7FFD,23),(0x7FFD,31)] and memory.o7ffd==selected
            assert all(a==b for a,b in zip(expected,memory.banks)),(paging,flags,'RAM')
            assert Counter(writes)==Counter(memory.writes),(paging,flags,'writes')
            assert simulator.registers[SP]==initial[SP]
            cases+=1
    report=dict(passed=True,total_cases=cases,all_initial_flags_values=True,
        all_six_bit_initial_paging_values=True,locked_paging_cases=8192,
        paging_write_attempts=[23,31],unlocked_final_paging=31,
        locked_paging_preserved=True,cleared_attribute_bytes=768,final_PC=0x616B,
        halted=True,returns=False,final_I=60,final_IM=0,final_IFF=0,
        all_registers_except_R=True,all_physical_ram_bytes_proved=True,
        write_multiplicity_proved=True,cpu_stack_written=False,
        irq_during_EI_window_executed=False,nmi_executed=False,
        timing_proved=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/FinalHaltVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
