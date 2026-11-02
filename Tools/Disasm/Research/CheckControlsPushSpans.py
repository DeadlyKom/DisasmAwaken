"""Три динамические цепочки PUSH AF, восстановление SP и настоящие помощники строки."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsRasterStep import add_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh,cp_flags

PROFILES = ((0xD706,0xD716,0xD727,0xD6C9,0xD734,0xD739),
    (0xD7FE,0xD80E,0xD81F,0xD7CC,0xD82C,0xD831),
    (0xD8F0,0xD900,0xD911,0xD8BB,0xD91E,0xD923))


def main():
    original=base_memory()
    memory=Memory(original)
    simulator=Simulator(memory)
    touched=set()
    counts,outcomes,targets=Counter(),Counter(),{entry:set() for entry,*_ in PROFILES}

    def check(profile,count,h,l,fill,mode):
        nonlocal touched
        entry,operand,resume,loop,return_up,return_down=profile
        upward=mode==0
        left=(l*73+count)&255
        toggle=(h*17+l)&255
        saved_af=((l+fill)&255)*256+((h*31+count)&255)
        memory.recording=False
        for address in touched:
            memory[address]=original[address]
        memory[0xD186:0xD188]=[0xFC,0xBF]
        memory[0xD18B]=mode
        memory[0xBFFC:0xC000]=[saved_af&255,saved_af>>8,0xFF,0x3F]
        initial=get_registers({'AF':count*256+0x5A,'HL':h*256+0x39,'DE':l*256+left,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':toggle*256+fill,
            'IY':0x5C3A,'SP':0xBFFC,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=fill,(l+count)&255,fill&1,h%3
        wanted=list(initial)
        end=h*256+l
        delta=-32 if upward else 32
        wrapped=l<32 if upward else l>=224
        new_h=(h+(-1 if upward else 1))&255 if wrapped else h
        limit=0x7F if upward else 0x8C
        boundary=wrapped and new_h==limit
        wanted[5]=(left+delta)&255
        wanted[6:8]=[new_h,(l+delta)&255]
        wanted[9]=fill^toggle
        if boundary:
            wanted[0:2]=[saved_af>>8,saved_af&255]
            wanted[SP],end_pc,m1=0xC000,0x3FFF,41+count
        else:
            wanted[0:2]=[limit,cp_flags(limit,new_h)] if wrapped else [(l+delta)&255,sub8_flags(l,32) if upward else add_flags(l,32)]
            wanted[SP],end_pc,m1=0xBFFC,loop,20+count+(17 if wrapped else 13)
        wanted[15]=refresh(initial[15],m1)
        helper_return=return_up if upward else return_down
        writes=[(operand,16-count),(0xBFFB,l),(0xBFFA,left),(0xBFF9,fill),(0xBFF8,fill)]
        # Вычисление физических записей SP, в отличие от DEC L заём меняет старшую страницу.
        writes += [(end-index,fill) for index in range(1,2*count+1)]
        writes += [(0xBFFB,helper_return>>8),(0xBFFA,helper_return&255)]
        expected=list(memory)
        for address,value in writes:
            expected[address]=value
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        reached=set()
        for _ in range(110):
            pc=simulator.registers[PC]
            if pc in (loop,0x3FFF):
                break
            reached.add(pc)
            simulator.run()
        else:
            raise AssertionError(('граница фазы',entry,count,h,l))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),26,27)
        assert simulator.registers[PC]==end_pc
        assert all(wanted[i]==simulator.registers[i] for i in compared), (entry,count,h,l,mode,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (entry,count,h,l,mode)
        assert resume-count in reached
        targets[entry].add(resume-count)
        touched={address for address,_ in writes}
        counts[format(entry,'04X')]+=1
        outcomes['unwind' if boundary else 'continue_loop']+=1

    # Проверка всех длин, каждого младшего адреса и обоих направлений во всех копиях пути.
    for profile in PROFILES:
        for count in range(17):
            for h in (0x80,0x81,0x8A,0x8B):
                for l in range(256):
                    check(profile,count,h,l,(l*31+count)&255,0 if (l+count)&1 else 255)
    # Проверка каждого байта Mode и заполнения при всех длинах и противоположном выборе краёв.
    for profile in PROFILES:
        for fill in range(256):
            for count in range(17):
                check(profile,count,0x80 if fill&1 else 0x8B,(fill*17+count)&255,fill,fill)
    result=dict(passed=True,total_cases=sum(counts.values()),cases_by_entry=dict(counts),outcomes=dict(outcomes),
        dynamic_targets={format(entry,'04X'):[format(a,'04X') for a in sorted(addresses)] for entry,addresses in targets.items()},
        all_pair_counts_0_to_16=True,all_endpoint_low_bytes=True,all_fill_and_mode_bytes=True,
        all_three_original_copies=True,real_row_helpers_without_stubs=True,
        exact_registers_flags_r_sp_and_target=True,every_ram_byte_and_write_checked=True,
        original_stack_then_buffer_stack_then_saved_stack=True,whole_rasterizer_proved=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsPushSpansVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
