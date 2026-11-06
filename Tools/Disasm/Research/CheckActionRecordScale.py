"""Полный E55C до фактической цели изменённого JR, оригинальные 128 указателей OBJECT3D."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


def sub_flags(a,b):
    value=(a-b)&255
    return 2|(value&0xA8)|(64 if value==0 else 0)|(16 if (a^b^value)&16 else 0)|(
        4 if (a^b)&(a^value)&128 else 0)|int(a<b)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();base[4][:len(objects)]=objects
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0;headers=Counter();targets=Counter()
    for index in range(128):
        pointer=flat[0x9E00+2*index]+256*flat[0x9E01+2*index]
        exponent=objects[pointer-0xC000+1]
        assert 1<=exponent<=5
        headers[exponent]+=1
        for code in range(256):
            # Создание записи с исходным индексом модели и полным кодом класса.
            memory.recording=False
            for page in (0,2,5):memory.banks[page][:]=base[page]
            memory.out7ffd(16);memory[0xA106],memory[0xA112]=2*index,code
            initial=get_registers({'AF':((index*73)&255)*256+((index+code)&255),'HL':0x1357,
                'DE':0x2468,'BC':0x369C,'^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,
                '^AF':0x3210,'IX':0xA100,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE55C},None,False)
            initial[14],initial[15],initial[26],initial[27]=code,index+code&255,code&1,code%3
            # Создание независимых перестановок исходных вычитаемых слов.
            values=((index*509+code*73)&65535,(code*257+index*17)&65535,((code*109+index*997)&65535)^32768)
            for address,value in zip((0xE5B3,0xE5D2,0xE5ED),values):memory[address],memory[address+1]=value&255,value>>8
            expected=[bytearray(b) for b in memory.banks];writes=[]

            def put(address,value):
                bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

            def word(address,value):put(address,value&255);put(address+1,value>>8)

            word(0xE605,0xBFFE)
            if code==0x14:
                for active,saved,value in zip((0xE5B3,0xE5D2,0xE5ED),(0xE68C,0xE692,0xE698),values):
                    word(saved,value);word(active,(value>>1)|(value&0x8000))
            # Создание эталона вложенных возвратов и сохранения BC в настоящем селекторе банка.
            word(0xBFFC,0xE594)
            word(0xBFFA,0xAAD8);word(0xBFF8,0x369C)
            word(0xBFFA,0xAAE1);word(0xBFF8,0x369C)
            displacement=6-exponent;put(0xE59E,displacement)
            target=0xE59F+displacement;targets[target]+=1
            wanted=list(initial);wanted[0:2]=[displacement,sub_flags(6,exponent)]
            wanted[6:8]=[0,200];wanted[PC]=target
            wanted[15]=refresh(initial[15],62 if code==0x14 else 41)
            simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
            memory.writes=[];memory.recording=True;simulator.run(start=0xE55C,stop=target);memory.recording=False
            compared=(*range(25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(index,code,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert all(a==b for a,b in zip(expected,memory.banks)),(index,code,'RAM')
            assert Counter(memory.writes)==Counter(writes),(index,code,'writes',memory.writes,writes)
            assert trace.writes==[(0x7FFD,20),(0x7FFD,16)] and memory.o7ffd==16
            cases+=1
    report=dict(passed=True,total_cases=cases,all_128_original_model_pointers=True,all_256_class_codes=True,
        original_header_high_histogram=dict(headers),dispatch_targets={format(k,'04X'):v for k,v in sorted(targets.items())},
        whole_E55C_to_actual_JR_target_proved=True,following_component_update_proved=False,
        actual_banked_header_reader_executed=True,real_page_outputs=[20,16],maximum_additional_stack_bytes=6,
        exact_registers_including_R=True,matched_class_refresh_m1=62,other_class_refresh_m1=41,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,hardware_bus_write_order_proved=False,
        original_header_range=[1,5],odd_indices_and_modified_headers_proved=False,
        independent_numeric_oracle=True,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordScaleVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
