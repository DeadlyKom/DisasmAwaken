"""Настоящая обёртка E69E и преобразователь E6A7, числовой эталон адреса, все AF."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0
    for code in range(256):
        for flags in range(256):
            # Создание вариантов стека, два варианта пересекают границу физических банков.
            memory.recording=False
            for page in (0,2,5):memory.banks[page][:]=base[page]
            stack=(0x8002,0xC002,0xBFFE)[(code+flags)%3]
            memory[stack],memory[stack+1]=255,63
            initial=get_registers({'AF':code*256+flags,'HL':(code*257+flags*73)&65535,
                'DE':0x2468,'BC':0x369C,'^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,
                '^AF':0x3210,'IX':0xABCD,'IY':code*257,'SP':stack,'PC':0xE69E},None,False)
            initial[14],initial[15],initial[26],initial[27]=flags,flags,flags&1,flags%3
            pointer=0xA100+64*code;wanted=list(initial)
            wanted[0:2]=[pointer>>8,add_flags(code>>2,0xA1)]
            wanted[10:12]=[pointer>>8,pointer&255]
            wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],19),stack+2,0x3FFF
            expected=[bytearray(b) for b in memory.banks];writes=[]
            # Создание эталона временного HL, возврата CALL и перезаписи этого возврата адресом записи.
            # Модель записывает слово младшим байтом вперёд, это не временной порядок шинных циклов Z80.
            for address,value in ((stack-2,initial[7]),(stack-1,initial[6]),
                (stack-4,0xA2),(stack-3,0xE6),(stack-4,pointer&255),(stack-3,pointer>>8)):
                bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True
            simulator.run(start=0xE69E,stop=0x3FFF);memory.recording=False
            compared=(*range(25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(code,flags,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert all(a==b for a,b in zip(expected,memory.banks)),(code,flags,'RAM')
            assert memory.writes==writes,(code,flags,'write_order',memory.writes,writes)
            cases+=1
    report=dict(passed=True,total_cases=cases,all_input_AF=True,real_RecordIndexToAddress_executed=True,
        exact_registers_including_R=True,refresh_m1=19,all_physical_ram_bytes_proved=True,
        simulator_write_order_and_multiplicity_proved=True,hardware_bus_write_order_proved=False,
        maximum_additional_stack_bytes=4,
        stack_profiles=[0x8002,0xC002,0xBFFE],all_AF_cross_stack_product_exhausted=False,
        independent_numeric_oracle=True,record_contents_checked=False,irq_executed=False,
        native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordSelectionVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
