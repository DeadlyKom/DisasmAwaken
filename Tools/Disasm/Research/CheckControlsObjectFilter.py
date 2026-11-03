"""Фильтр одной записи и маркер окончания E4B1, без геометрии и вывода."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh,cp_flags
from ReferenceControlsPointMotion import block_cost


def main():
    original=base_memory()
    memory=Memory(original)
    simulator=Simulator(memory)
    counts=Counter()

    def check(status,kind,x,y,z,marker,serial,sentinel=False):
        memory.recording=False
        memory[0xA100],memory[0xA101],memory[0xA112]=marker,status,kind
        memory[0xA11B],memory[0xA11D],memory[0xA11F]=x,y,z
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xA100 if sentinel else 0xA0C0,'IY':0x5C3A,'SP':0xBFFE,
            'PC':0xE4B1 if sentinel else 0xE4B7},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial)
        if sentinel:
            wanted[0:2]=[marker,cp_flags(marker,128)]
            wanted[PC]=0x3FFF if marker==128 else 0xE4B7
            wanted[SP]=0xC000 if marker==128 else 0xBFFE
            m1=block_cost(0xE4B1,0xE4B7)
            path='sentinel_return' if marker==128 else 'sentinel_continue'
        else:
            wanted[4:6]=[0,0x40]
            wanted[8:10]=[0xA1,0]
            m1=block_cost(0xE4B7,0xE4C3)
            if status==128:
                path='check_marker'
                wanted[0:2]=[128,0x42]
                wanted[PC]=0xE4B1
            else:
                m1+=block_cost(0xE4C3,0xE4CA)
                if kind==20:
                    path='type_14'
                    wanted[0:2]=[20,cp_flags(20,20)]
                    wanted[PC]=0xE4BA
                else:
                    m1+=block_cost(0xE4CA,0xE4CE)
                    if kind==21:
                        path='type_15'
                        wanted[0:2]=[21,cp_flags(21,21)]
                        wanted[PC]=0xE4BA
                    else:
                        m1+=block_cost(0xE4CE,0xE4D5)
                        if x==128:
                            path='x_80'
                            wanted[0:2]=[128,0x42]
                            wanted[PC]=0xE4BA
                        else:
                            wanted[3]=x
                            m1+=block_cost(0xE4D5,0xE4DA)+(2 if x>=128 else 0)+block_cost(0xE4DC,0xE4E0)
                            wanted[2]=y
                            m1+=block_cost(0xE4E0,0xE4E8)+(2 if y>=128 else 0)+block_cost(0xE4EA,0xE4EE)
                            if y==128:
                                path='height_80'
                                wanted[0:2]=[128,0x42]
                                wanted[PC]=0xE4BA
                            else:
                                wanted[5]=z
                                m1+=block_cost(0xE4EE,0xE4F6)+(2 if z>=128 else 0)+block_cost(0xE4F8,0xE4FC)
                                magnitude=z if z<128 else 256-z
                                wanted[0:2]=[magnitude,cp_flags(magnitude,128)]
                                wanted[PC]=0xE4B7 if z==128 else 0xE4FC
                                path='z_80' if z==128 else 'accepted'
        wanted[15]=refresh(initial[15],m1)
        expected=list(memory)
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        # Проверка одной записи прекращается до следующего шага IX или до первого расчёта координат.
        for step in range(45):
            if step>1 and simulator.registers[PC]==wanted[PC]:
                break
            simulator.run()
        else:
            raise AssertionError(('граница',status,kind,x,y,z,marker,sentinel,simulator.registers[PC]))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(status,kind,x,y,z,marker,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==[]
        counts[path]+=1

    # Проверка всех комбинаций байта состояния и типа, включая типы за пределами таблицы значков.
    for status in range(256):
        for kind in range(256):
            check(status,kind,1,2,3,0,counts.total())
    # Проверка трёх попарных сочетаний полей, каждый особый байт 80 также попадает в ранние выходы.
    for first in range(256):
        for second in range(256):
            check(0,0,first,second,3,0,counts.total())
            check(0,0,first,2,second,0,counts.total())
            check(0,0,1,first,second,0,counts.total())
    # Проверка маркера по смещению 0 при всех входных AF, младший входной байт варьируется независимо.
    for marker in range(256):
        for flags in range(256):
            check(128,0,1,2,3,marker,(marker<<8)|flags,True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_path=dict(counts),
        all_status_type_pairs=True,all_pairwise_coordinate_field_values=True,
        all_marker_values_and_initial_flag_bytes=True,exact_registers_flags_refresh_sp_and_targets=True,
        every_ram_byte_checked=True,no_memory_writes=True,record_stride=64,
        rejected_type_codes=[20,21],accepted_type_domain_not_limited_to_0_19=True,
        full_joint_field_space_exhausted=False,full_e291_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsObjectFilterVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
