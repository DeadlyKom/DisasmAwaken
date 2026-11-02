"""Два установщика среднего алгоритма и оба ограниченных края, настоящие вызовы масок."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost
from CheckControlsEvenSpan import and_flags


def logical_flags(value):
    return and_flags(value)&~0x10


def main():
    original=base_memory()
    memory=Memory(original)
    simulator=Simulator(memory)
    touched=set()
    counts=Counter()
    def check(entry,radius,work_x,work_y,center_y,section,mode,flags,kind):
        nonlocal touched
        memory.recording=False
        for address in touched:
            memory[address]=original[address]
        memory[0xD17F:0xD186]=[flags,radius,work_y,work_x,center_y,0xA5,section]
        memory[0xD18C]=mode
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=mode,(radius+work_x)&255,flags&1,work_x%3
        wanted=list(initial)
        wanted[2:4]=[work_x,work_y]
        writes=[]
        if entry==0xD56C:
            wanted[0:2]=[section,sub8_flags(136,work_x)]
            wanted[19]=(136-work_x)&255
            wanted[21]=section
            m1=block_cost(0xD56C,0xD57B)
        else:
            wanted[0:2]=[(-radius)&255,sub8_flags(0,radius)]
            wanted[4:6]=[radius,flags]
            wanted[19],wanted[21]=(-radius)&255,0
            m1=block_cost(0xD504,0xD515)
            if entry==0xD4CB:
                x=(128+work_x-radius)&255
                address=0x8000+32*center_y+x//8
                mask=(255<<(7-(x&7)))&255
                final_low=(address&255)|31
                wanted[0:2]=[final_low,logical_flags(final_low)]
                wanted[2:4]=[mask,255]
                wanted[5]=address&255
                wanted[6:8]=[address>>8,final_low]
                writes=[(0xBFFD,0xD4),(0xBFFC,0xCE),(0xBFFD,0xD4),(0xBFFC,0xD9)]
                left_cost=block_cost(0xD515,0xD532)+(1+(x&7))*block_cost(0xD532,0xD537)+block_cost(0xD537,0xD53C)
                m1+=block_cost(0xD4CB,0xD4E4)+left_cost
            elif entry==0xD4E4:
                x=(128+radius-work_x)&255
                address=0x8000+32*center_y+x//8
                first_low=((address&255)&0xE0)|1
                wanted[0:2]=[first_low,and_flags(mode)]
                wanted[2:4]=[0,255>>(x&7)]
                wanted[5]=first_low
                wanted[6:8]=[address>>8,address&255]
                writes=[(0xBFFD,0xD4),(0xBFFC,0xE7),(0xBFFD,0xD4),(0xBFFC,0xF2),
                    (0xBFFB,x),(0xBFFA,sub8_flags((128+radius)&255,work_x)),(0xD18A,work_x)]
                right_cost=block_cost(0xD53C,0xD562)+(8-(x&7))*block_cost(0xD562,0xD567)+block_cost(0xD567,0xD56C)
                m1+=block_cost(0xD4E4,0xD501)+right_cost
        wanted[SP],wanted[15]=0xC000,refresh(initial[15],m1)
        expected=list(memory)
        for address,value in writes:
            expected[address]=value
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        for _ in range(180):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',entry,radius,work_x))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (entry,radius,work_x,center_y,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (entry,radius,work_x,center_y)
        touched={address for address,_ in writes}
        counts[kind]+=1
    # Проверка каждой пары радиус-рабочее X для установщиков состояния и обоих краёв.
    for radius in range(256):
        for work_x in range(256):
            for entry in (0xD504,0xD56C,0xD4CB,0xD4E4):
                check(entry,radius,work_x,(radius*73+work_x)&255,(radius+31*work_x)&255,
                    (radius*17+work_x)&255,(radius*31+work_x)&255,(work_x*73+radius)&255,format(entry,'04X'))
        if radius%64==63:
            print('Circle setup radii',radius+1,flush=True)
    # Проверка каждого Y и X при фиксированном радиусе, независимо от предыдущего набора.
    for y in range(256):
        for x in range(256):
            for entry in (0xD4CB,0xD4E4):
                check(entry,9,x,0xA5,y,0x5A,(x+y)&255,0xFF,'all_rows')
    report=dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),
        all_radius_work_x_pairs=True,all_row_x_pairs=True,all_mode_and_input_flag_bytes=True,
        real_mask_helpers_without_stubs=True,exact_registers_flags_r_and_sp=True,
        every_ram_byte_and_write_checked=True,right_clip_mode_read_has_no_output_effect=True,
        left_clip_z_returns_mode_not_a=True,whole_large_renderer_proved=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleSetupVerification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
