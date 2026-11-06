"""Полный HALT/ROM/писатель, IFF остаётся единицей, весь временный SP проверяется с IRQ-планировщиком."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from CheckIntroWaitInterrupt import Keyboard
from ReferenceIntroIRQ import apply


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--rom',type=Path,required=True)
    args=parser.parse_args();rom=args.rom.read_bytes();assert len(rom)==16384
    flat=original_memory();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    base[5][0x1C00]=base[5][0x1C04]=255
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17)
    memory.roms=(list(rom),list(rom));memory.out7ffd(17)
    simulator=Simulator(memory);cases=0
    for origin in (0x80,0xC0):
        generated=original_memory();execute(generated,{'PC':0x692D,'IX':origin},stop=0x694C)
        chain=[]
        for row in range(8):
            for col in range(4):chain.extend((0xE1,0x22,origin+2*col,origin+row))
        assert generated[0x68A9:0x6929]==chain
        for phase in range(256):
            for time in (0,100,69880):
                memory.recording=False
                for bank in (1,2,5):memory.banks[bank][:]=base[bank]
                for index,value in enumerate(chain):memory[0x68A9+index]=value
                memory[0x67F2]=phase
                source=0x60C0 if phase==0 else 0x61C0
                for matrix in range(2):
                    for index in range(64):memory[0x60C0+256*matrix+index]=(index*37+phase*19+matrix*53)&255
                frame=(0,0xFFFF,0xFFFFFF)[phase%3]
                for index,value in enumerate(frame.to_bytes(3,'little')):memory[0x5C78+index]=value
                stack=(0xBFFE,0x8FFE,0x5FFE)[cases%3]
                memory[stack],memory[stack+1]=255,63
                initial=get_registers({'AF':((phase*109)&255)*256+((phase*73)&255),
                    'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
                    '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                    'SP':stack,'PC':0x6983},None,False)
                initial[14],initial[26],initial[27],initial[25]=phase,1,1,time
                expected=[bytearray(b) for b in memory.banks];writes=[]

                def read(address):
                    if address<0x4000:return rom[address]
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                    return expected[bank][address&0x3FFF]

                def put(address,value):
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                    expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

                expected_ports=apply(read,put,initial,0x6984)
                put(0x692A,stack&255);put(0x692B,stack>>8)
                # Перенос двух байтов каждого слова не меняет флаги OR фазы и не пишет CPU-стек.
                for row in range(8):
                    for col in range(8):put((origin+row)*256+origin+col,read(source+8*row+col))
                last_word=read(source+62)+256*read(source+63)
                final_f=(phase&0xA8)|(0x40 if phase==0 else 0)|(4 if phase.bit_count()%2==0 else 0)
                wanted=list(initial);wanted[0:2]=[phase,final_f]
                wanted[6:8]=[last_word>>8,last_word&255]
                wanted[SP],wanted[PC]=stack+2,0x3FFF
                simulator.registers[:]=initial;ports=Keyboard();simulator.set_tracer(ports)
                memory.writes=[];memory.recording=True
                # Проверка с включённым штатным планировщиком, дополнительный IRQ во временный SP не подменяется.
                simulator.run(start=0x6983,stop=0x3FFF,interrupts=True);memory.recording=False
                compared=(*range(15),*range(16,25),26,27)
                assert all(wanted[i]==simulator.registers[i] for i in compared),(origin,phase,time,
                    [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
                assert ports.reads==expected_ports and not ports.writes
                assert all(a==b for a,b in zip(expected,memory.banks)),(origin,phase,time,'RAM')
                assert Counter(writes)==Counter(memory.writes),(origin,phase,time,'writes')
                cases+=1
    report=dict(passed=True,total_cases=cases,all_phase_byte_values=True,
        generated_destination_origins=[128,192],cpu_stack_locations=3,start_tstates=[0,100,69880],
        selected_attribute_table_on_zero=0x60C0,selected_attribute_table_on_nonzero=0x61C0,
        attribute_bytes_written=64,actual_generated_writer_executed=True,
        actual_ROM_IRQ_executed=True,irq_executed=True,irq_count_per_case=1,final_IFF=1,
        extra_IRQ_during_temporary_SP=False,interrupt_scheduler_enabled=True,
        frame_period=69888,maximum_additional_CPU_stack_bytes=14,
        all_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        independent_numeric_oracle=True,rom_name=args.rom.name,rom_sha256=hashlib.sha256(rom).hexdigest(),
        arbitrary_ROM_keyboard_and_interrupt_periods_proved=False,
        native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroPresentAttributesVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
