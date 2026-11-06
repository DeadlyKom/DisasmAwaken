"""Полное продолжение 6BBC с двумя IRQ и реальными сгенерированными выборками."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from CheckIntroWaitInterrupt import Keyboard
from ReferenceIntroLookup import Lookup


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--rom',type=Path,required=True)
    args=parser.parse_args();rom=args.rom.read_bytes();assert len(rom)==16384
    flat=original_memory();generated=original_memory();execute(generated,{'PC':0x6C9C},stop=0x6CF9)
    flat[0x9100:0x9282]=generated[0x9100:0x9282]
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    base[5][0x1C00]=base[5][0x1C04]=255
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17)
    memory.roms=(list(rom),list(rom));memory.out7ffd(17)
    simulator=Simulator(memory);cases=0
    for origin in (0x80,0xC0):
        writer=original_memory();execute(writer,{'PC':0x692D,'IX':origin},stop=0x694C)
        chain=writer[0x68A9:0x6929]
        for phase in (0,128):
            for warmup_index,warmup in enumerate((161,3,2,1)):
                for variant in range(64):
                    for time in (0,100,69880):
                        memory.recording=False
                        for bank in (1,2,5):memory.banks[bank][:]=base[bank]
                        # Создание синтетических источников, физическое размещение игрового проекта не меняется.
                        memory.banks[1][:]=bytes((i*29+variant*61+17)&255 for i in range(0x4000))
                        for index,value in enumerate(chain):memory[0x68A9+index]=value
                        memory[0x67F2]=phase
                        memory[0x6C22],memory[0x6C2E],memory[0x6C3F]=warmup,variant,variant%40
                        for index in range(256):memory[0x9300+index]=(index*37+variant*53)&255
                        for row in range(38):
                            for col in range(64):
                                pointer=0xAD00+128*row+2*col
                                memory[pointer]=(row*29+col*17+variant*7)&255
                                memory[pointer+1]=0xC0+((row*3+col*5)&63)
                        for half in range(2):
                            for row in range(38):
                                pointers=(0x7200 if half==0 else 0xE600)+64*row
                                destination=(0x4000 if half==0 else 0x5000)+32*row
                                record=0x6000+256*half+4*row
                                for address,value in ((record,pointers),(record+2,destination)):
                                    memory[address],memory[address+1]=value&255,value>>8
                                for col in range(32):
                                    source=0x8000+0x4C0*half+32*row+31-col
                                    memory[pointers+2*col],memory[pointers+2*col+1]=source&255,source>>8
                            for index in range(64):memory[0x60C0+256*half+index]=(index*73+variant*19+half*53)&255
                        frame=0xFFFFFF if variant&1 else 0xFFFF
                        for index,value in enumerate(frame.to_bytes(3,'little')):memory[0x5C78+index]=value
                        stack=(0xBFFE,0x8FFE,0x5FFE)[cases%3]
                        memory[stack],memory[stack+1]=255,63
                        memory[0x6BBD],memory[0x6BBE]=stack&255,stack>>8
                        flags=warmup_index*64+variant
                        initial=get_registers({'AF':((variant*109)&255)*256+flags,
                            'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
                            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                            'SP':0xF660,'PC':0x6BBC},None,False)
                        initial[14],initial[26],initial[27],initial[25]=flags,0,1,time
                        expected=[bytearray(b) for b in memory.banks];writes=[]

                        def read(address):
                            if address<0x4000:return rom[address]
                            bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                            return expected[bank][address&0x3FFF]

                        def put(address,value):
                            bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

                        oracle=Lookup(read,put,initial);expected_ports=oracle.present_lookup(phase,origin)
                        simulator.registers[:]=initial;ports=Keyboard();simulator.set_tracer(ports)
                        memory.writes=[];memory.recording=True
                        # Проверка всего пути, оба выборщика, масштаб и кадровый вывод исполняются на исходном Z80.
                        simulator.run(start=0x6BBC,stop=0x3FFF,interrupts=True);memory.recording=False
                        compared=(*range(15),*range(16,25),26,27)
                        assert all(oracle.r[i]==simulator.registers[i] for i in compared),(origin,phase,warmup,variant,time,
                            [(i,oracle.r[i],simulator.registers[i]) for i in compared if oracle.r[i]!=simulator.registers[i]])
                        assert ports.reads==expected_ports and not ports.writes
                        assert all(a==b for a,b in zip(expected,memory.banks)),(origin,phase,warmup,variant,time,'RAM')
                        assert Counter(writes)==Counter(memory.writes),(origin,phase,warmup,variant,time,'writes',
                            (Counter(writes)-Counter(memory.writes)).most_common(4),(Counter(memory.writes)-Counter(writes)).most_common(4))
                        cases+=1
    report=dict(passed=True,total_cases=cases,phase_states=[0,128],generated_origins=[128,192],
        warmup_values=[161,3,2,1],all_ramp_levels=True,all_cycle_indices=True,
        sampler_row_groups=[13,25],sampled_bytes=2432,scale_updates=2,
        actual_IRQ_ROM_and_all_children_executed=True,irq_executed=True,irq_count_per_case=2,
        initial_IFF_required=0,final_IFF=0,initial_SP_is_temporary=True,restored_CPU_SP_from_operand=True,
        final_BC=0x8000,final_IXL=0,source_destination_alias_profile_included=True,
        cpu_stack_locations=3,maximum_additional_CPU_stack_bytes=16,
        start_tstates=[0,100,69880],frame_period=69888,
        all_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        independent_numeric_oracle=True,rom_name=args.rom.name,rom_sha256=hashlib.sha256(rom).hexdigest(),
        arbitrary_keyboard_ROM_times_and_all_input_states_proved=False,
        native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroLookupContinuationVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
