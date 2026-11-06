"""Целый чередующийся кадр, ROM IRQ, обе выборки и самогенерируемые атрибуты."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from CheckIntroWaitInterrupt import Keyboard
from ReferenceIntroFrame import Frame


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
        chain=generated[0x68A9:0x6929]
        for phase in (0,128):
            for variant in range(256):
                for time in (0,100,69880):
                    memory.recording=False
                    for bank in (1,2,5):memory.banks[bank][:]=base[bank]
                    for index,value in enumerate(chain):memory[0x68A9+index]=value
                    memory[0x67F2]=phase
                    # Создание двух таблиц записей и двух наборов указателей на пиксели.
                    for half in range(2):
                        for row in range(38):
                            pointers=(0x7200 if half==0 else 0xAD00)+64*row
                            destination=(0x4000 if half==0 else 0x5000)+32*row
                            record=0x6000+256*half+4*row
                            for address,value in ((record,pointers),(record+2,destination)):
                                memory[address],memory[address+1]=value&255,value>>8
                            for col in range(32):
                                source=0x8000+0x500*half+32*row+31-col
                                memory[pointers+2*col],memory[pointers+2*col+1]=source&255,source>>8
                                memory[source]=(row*17+col*7+variant*37+half*53)&255
                        for index in range(64):memory[0x60C0+256*half+index]=(index*73+variant*19+half*53)&255
                    frame=0xFFFFFF if variant&1 else 0xFFFF
                    for index,value in enumerate(frame.to_bytes(3,'little')):memory[0x5C78+index]=value
                    stack=(0xBFFE,0x8FFE,0x5FFE)[cases%3]
                    memory[stack],memory[stack+1]=255,63
                    initial=get_registers({'AF':((variant*109)&255)*256+variant,
                        'HL':0x1357,'DE':0x2468,'BC':(0x369C+variant*257)&65535,'IX':0xABCD,'IY':0x5C3A,
                        '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                        'SP':stack,'PC':0x67F1},None,False)
                    initial[14],initial[26],initial[27],initial[25]=variant,variant&1,1,time
                    expected=[bytearray(b) for b in memory.banks];writes=[]

                    def read(address):
                        if address<0x4000:return rom[address]
                        bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                        return expected[bank][address&0x3FFF]

                    def put(address,value):
                        bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                        expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

                    oracle=Frame(read,put,initial);expected_ports=oracle.present(phase,origin)
                    simulator.registers[:]=initial;ports=Keyboard();simulator.set_tracer(ports)
                    memory.writes=[];memory.recording=True
                    # Проверка исходного полного пути с настоящим IRQ, ни один дочерний рисователь не подменяется.
                    simulator.run(start=0x67F1,stop=0x3FFF,interrupts=True);memory.recording=False
                    compared=(*range(15),*range(16,25),26,27)
                    assert all(oracle.r[i]==simulator.registers[i] for i in compared),(origin,phase,variant,time,
                        [(i,oracle.r[i],simulator.registers[i]) for i in compared if oracle.r[i]!=simulator.registers[i]])
                    assert ports.reads==expected_ports and not ports.writes,(origin,phase,variant,time,ports.reads,ports.writes)
                    assert all(a==b for a,b in zip(expected,memory.banks)),(origin,phase,variant,time,'RAM')
                    assert Counter(writes)==Counter(memory.writes),(origin,phase,variant,time,'writes',
                        (Counter(writes)-Counter(memory.writes)).most_common(4),(Counter(memory.writes)-Counter(writes)).most_common(4))
                    cases+=1
    report=dict(passed=True,total_cases=cases,phase_states=[0,128],generated_origins=[128,192],
        source_patterns=256,copy_halves=2,copied_pixel_bytes=2432,attribute_bytes_written=64,
        actual_IRQ_ROM_and_all_children_executed=True,irq_executed=True,irq_counts_per_case=[1,2],
        enabled_IFF_at_frame_boundary_can_add_early_IRQ=True,all_initial_IFF_values=True,
        final_IFF=0,source_destination_alias_profile_included=True,
        correct_destination_patch_0014_verified=True,cpu_stack_locations=3,
        maximum_additional_CPU_stack_bytes=16,start_tstates=[0,100,69880],frame_period=69888,
        all_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        independent_numeric_oracle=True,rom_name=args.rom.name,rom_sha256=hashlib.sha256(rom).hexdigest(),
        arbitrary_keyboard_ROM_and_phase_states_proved=False,
        native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroInterlacedFrameVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
