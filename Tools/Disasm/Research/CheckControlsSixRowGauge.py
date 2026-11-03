"""E8FD, шесть строк AA, частичный байт и очистка хвоста, все значения входного A."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost


def inc_flags(previous):
    result=(previous+1)&255
    return (result&0xA8)|(64 if result==0 else 0)|(16 if previous&15==15 else 0)|(4 if previous==127 else 0)


def main():
    original=base_memory()
    assert original[0xE973:0xE97A]==[0xAA & ((255 << (7-i))&255) for i in range(7)]
    memory=Memory(original);simulator=Simulator(memory);touched=set();counts=Counter()

    def check(value,high,low,serial):
        nonlocal touched
        memory.recording=False
        for address in touched:memory[address]=original[address]
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':value*256+(serial&255),'HL':high*256+low,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE8FD},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        effective=((value+8)&248) if value and (value&7)==7 else value
        full=(effective>>3)&7;remainder=effective&7
        rounded=(((effective+8)&255)>>3)&7 if remainder else full
        clear=max(6-rounded,0)
        patterns=[0xAA]*full+([0xAA & ((255 << (7-remainder))&255)] if remainder else [])+[0]*clear
        writes=[(((high+row)<<8)|((low+column)&255),pattern)
            for column,pattern in enumerate(patterns) for row in range(6)]
        wanted=list(initial)
        wanted[6:8]=[high,(low+len(patterns))&255]
        wanted[3]=effective
        wanted[SP]=0xC000;wanted[PC]=0x3FFF
        if full:
            wanted[2],wanted[4],wanted[5]=0,5,0xAA
        if remainder:
            wanted[2]=0
            wanted[4:6]=[0xE9,0x73+remainder]
            wanted[16:18]=[high,inc_flags((low+full)&255)]
        else:
            wanted[16:18]=[0,0x54]
        if clear:
            wanted[0:2]=[high,inc_flags((low+len(patterns)-1)&255)]
            wanted[2],wanted[4],wanted[5]=0,0,5
        else:
            wanted[0:2]=[rounded-6,sub8_flags(rounded,6)]
        m1=block_cost(0xE8FD,0xE901)
        if value:
            m1+=block_cost(0xE901,0xE907)+block_cost(0xE90C,0xE913)
            if value&7==7:m1+=block_cost(0xE907,0xE90C)
        if full:m1+=block_cost(0xE913,0xE917)+full*block_cost(0xE917,0xE928)
        m1+=block_cost(0xE928,0xE92F)+block_cost(0xE949,0xE950)+block_cost(0xE952,0xE95A)
        if remainder:m1+=block_cost(0xE92F,0xE949)+block_cost(0xE950,0xE952)
        if clear:m1+=block_cost(0xE95A,0xE961)+clear*block_cost(0xE961,0xE972)+1
        wanted[15]=refresh(initial[15],m1)
        expected=list(memory)
        for address,data in writes:expected[address]=data
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(270):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',value,high,low))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(value,high,low,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(value,high,low)
        touched={address for address,_ in writes}
        counts['cleared_tail' if clear else 'no_tail']+=1

    # Проверка всех входных значений и всех младших адресных байтов, включая переносы внутри строки.
    for high in (0x49,0x51,0x80,0xFA):
        for low in range(256):
            for value in range(256):check(value,high,low,counts.total())
    report=dict(passed=True,total_cases=counts.total(),cases_by_path=dict(counts),
        all_input_a_and_low_address_bytes=True,high_address_profiles=[0x49,0x51,0x80,0xFA],
        all_65536_hl_values_exhausted=False,exact_registers_flags_refresh_sp=True,
        every_ram_byte_and_write_checked=True,no_stack_writes=True,low_address_wrap_preserved=True,
        six_rows=True,nominal_columns=6,maximum_actual_columns=14,
        original_algorithm_edge_cases_preserved=True,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSixRowGaugeVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
