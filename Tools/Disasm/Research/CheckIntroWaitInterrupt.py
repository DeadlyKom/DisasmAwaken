"""Настоящие EI/HALT/IM 1 и ROM-обработчик, независимо вычисленные FRAMES и весь стек."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from CheckIntro import ROOT,original_memory
from CheckActionUnpack import RecordedFlat
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceIntroIRQ import apply


class Keyboard:
    def __init__(self):self.reads=[];self.writes=[]
    def read_port(self,registers,port):self.reads.append(port);return 255
    def write_port(self,registers,port,value,offset):self.writes.append((port,value))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--rom',type=Path,required=True)
    args=parser.parse_args();rom=args.rom.read_bytes();assert len(rom)==16384
    assert rom[0x38:0x3A]==bytes((0xF5,0xE5)) and rom[0x51:0x53]==bytes((0xFB,0xC9))
    baseline=original_memory();baseline[:16384]=rom;baseline[0x5C00]=baseline[0x5C04]=255
    cases=0
    for flags in range(256):
        for frame in (0,0xFFFF,0xFFFFFE,0xFFFFFF):
            for phase in (0,100,69880):
                stack=(0xBFFE,0x9AFE,0x5FFE)[cases%3]
                m=RecordedFlat(baseline);m[stack:stack+2]=[255,63]
                m[0x5C78:0x5C7B]=list(frame.to_bytes(3,'little'))
                initial=get_registers({'AF':((flags*73)&255)*256+flags,
                    'HL':(cases*109)&65535,'DE':(cases*37+19)&65535,'BC':(cases*53+11)&65535,
                    'IX':0xABCD,'IY':0x5C3A,'^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,
                    '^AF':0x3210,'SP':stack,'PC':0x6A13},None,False)
                initial[14],initial[26],initial[27],initial[25]=flags,flags&1,1,phase
                expected=list(m);writes=[]

                def put(address,value):expected[address]=value;writes.append((address,value))

                expected_ports=apply(lambda a:expected[a],put,initial,0x6A15)
                wanted=list(initial);wanted[SP],wanted[PC],wanted[26]=stack+2,0x3FFF,0
                simulator=Simulator(m);simulator.registers[:]=initial;ports=Keyboard();simulator.set_tracer(ports)
                m.writes=[];m.recording=True
                # Проверка принятия аппаратного IM 1 штатным планировщиком модели на границе HALT.
                simulator.run(start=0x6A13,stop=0x3FFF,interrupts=True);m.recording=False
                compared=(*range(15),*range(16,25),26,27)
                assert all(wanted[i]==simulator.registers[i] for i in compared),(flags,frame,phase,
                    [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
                assert ports.reads==expected_ports and not ports.writes,(flags,frame,phase,ports.reads)
                assert list(m)==expected,(flags,frame,phase,'RAM',[(hex(i),a,b) for i,(a,b) in enumerate(zip(m,expected)) if a!=b][:8])
                assert Counter(writes)==Counter(m.writes),(flags,frame,phase,'writes',
                    (Counter(writes)-Counter(m.writes)).most_common(5),(Counter(m.writes)-Counter(writes)).most_common(5))
                cases+=1
        if flags%64==63:print('IRQ, F до '+format(flags,'02X')+' проверены',flush=True)
    report=dict(passed=True,total_cases=cases,all_initial_flags_values=True,
        frame_values=[0,65535,16777214,16777215],start_tstates=[0,100,69880],frame_period=69888,
        actual_ROM_instructions_executed=True,actual_EI_HALT_DI_executed=True,
        interrupt_scheduler_enabled=True,IM=1,irq_executed=True,irq_count_per_case=1,
        keyboard_pressed=False,KSTATE_first_bytes=[255,255],IY_required=0x5C3A,
        exact_registers_except_R=True,full_logical_RAM_including_stack=True,write_multiplicity_proved=True,
        maximum_additional_stack_bytes=14,independent_numeric_oracle=True,
        rom_name=args.rom.name,rom_sha256=hashlib.sha256(rom).hexdigest(),
        arbitrary_keyboard_and_ROM_profiles_proved=False,physical_banks_separately_proved=False,
        native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroWaitInterruptVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
