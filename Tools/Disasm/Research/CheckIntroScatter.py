"""Адресация приёмника реальными вставками 00 00 и 00 14, полный контракт переноса."""
from collections import Counter
import json
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP


def main():
    base_memory=original_memory();patches=[]
    for phase in (0,128):
        memory=original_memory();memory[0x67F2]=phase
        # Получение вставки из исходных инструкций до CALL WaitInterrupt, аппаратный IRQ не подменяется.
        execute(memory,{'PC':0x67F1},stop=0x6802)
        patch=tuple(memory[0x6839:0x683B])
        assert patch==((0,0) if phase==0 else (0,0x14))
        patches.append(patch)
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(base_memory[0x4000:0x8000]),bytearray(base_memory[0x8000:0xC000]),bytearray(base_memory[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0
    for patch in patches:
        for flags in range(256):
            for stack in (0xBFFE,0x5FFE,0x9FFE):
                memory.recording=False
                for bank in (0,2,5):memory.banks[bank][:]=base[bank]
                memory[stack],memory[stack+1]=255,63
                memory[0x6839],memory[0x683A]=patch
                # Создание непересекающихся таблиц, разрозненных источников и двух вариантов назначения.
                for row in range(38):
                    pointer_table=0x7200+64*row;destination=0x9000+32*row
                    for address,value in ((0x7100+4*row,pointer_table),(0x7102+4*row,destination)):
                        memory[address],memory[address+1]=value&255,value>>8
                    for column in range(32):
                        source=0x8000+row*32+(31-column)
                        memory[pointer_table+2*column],memory[pointer_table+2*column+1]=source&255,source>>8
                        memory[source]=(row*17+column*7+flags)&255
                initial=get_registers({'AF':((flags*73)&255)*256+flags,'HL':0x7100,
                    'DE':0x2468,'BC':(flags*257)&65535,'IX':0xABCD,'IY':0x5C3A,
                    '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                    'SP':stack,'PC':0x6827},None,False)
                initial[14],initial[26],initial[27]=flags,flags&1,flags%3
                expected=[bytearray(b) for b in memory.banks];writes=[]

                def put(address,value):
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                    expected[bank][address&0x3FFF]=value
                    writes.append((bank,address&0x3FFF,value))

                def word(address,value):
                    put(address,value&255);put(address+1,value>>8)

                word(0x6831,0x7100);word(0x68A1,stack)
                shift=0x100 if patch[1] else 0
                for row in range(38):
                    word(0x6831,0x7104+4*row)
                    for column in range(32):
                        put(0x9000+shift+32*row+column,(row*17+column*7+flags)&255)
                wanted=list(initial);wanted[0:2]=[0,0x42|(flags&1)]
                final_bc=((flags*257)-1216)&65535
                final_de=0x94C0+shift
                wanted[2:8]=[final_bc>>8,final_bc&255,final_de>>8,final_de&255,0x84,0xA1]
                wanted[SP],wanted[PC]=stack+2,0x3FFF
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                simulator.run(start=0x6827,stop=0x3FFF);memory.recording=False
                # Проверка всех физических записей, включая операнды, при сохранении исходного кода вставки.
                compared=(*range(15),*range(16,25),26,27)
                assert all(wanted[i]==simulator.registers[i] for i in compared),(patch,flags,
                    [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
                assert all(a==b for a,b in zip(expected,memory.banks)),(patch,flags,'RAM')
                assert Counter(writes)==Counter(memory.writes),(patch,flags,'writes')
                cases+=1
    report=dict(passed=True,total_cases=cases,patches_from_actual_phase_code=[list(p) for p in patches],
        correction_register='D',source_pointer_unchanged_by_patch=True,destination_page_increment=1,
        transferred_bytes_per_case=1216,table_records=38,all_initial_flags_values=True,
        cpu_stack_locations=3,all_registers_except_R=True,all_physical_ram_bytes_proved=True,
        write_multiplicity_proved=True,independent_numeric_oracle=True,
        arbitrary_source_destination_aliases_proved=False,irq_executed=False,native_execution=False,
        timing_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/IntroScatterVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
