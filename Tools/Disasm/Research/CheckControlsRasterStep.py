"""Переход на соседнюю строку и нелокальный возврат за верхним или нижним краем."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh,cp_flags


def add_flags(a,b):
    result=(a+b)&255
    return (result&0xA8)|(0x40 if not result else 0)|(0x10 if (a&15)+(b&15)>15 else 0)|(4 if (~(a^b)&(a^result)&128) else 0)|int(a+b>255)


def main():
    memory=Memory(base_memory())
    simulator=Simulator(memory)
    counts=Counter()
    outcomes=Counter()

    def check(entry,h,l,saved_af,saved_sp=0xBFFC):
        upward=entry==0xD925
        e=(h*73+l)&255
        fill=(l*31+h)&255
        toggle=(h*17+l)&255
        memory.recording=False
        memory[0xD186:0xD188]=[saved_sp&255,saved_sp>>8]
        memory[0xBFFA:0xBFFC]=[0xF0,0x3F]
        memory[saved_sp:saved_sp+4]=[saved_af&255,saved_af>>8,0xFF,0x3F]
        initial=get_registers({'AF':0xA55A,'HL':h*256+l,'DE':0x2400+e,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':toggle*256+fill,
            'IY':0x5C3A,'SP':0xBFFA,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=l,h^l,l&1,h%3
        wanted=list(initial)
        delta=-32 if upward else 32
        wrapped=l<32 if upward else l>=224
        new_h=(h+(-1 if upward else 1))&255 if wrapped else h
        limit=0x7F if upward else 0x8C
        boundary=wrapped and new_h==limit
        wanted[5]=(e+delta)&255
        wanted[6:8]=[new_h,(l+delta)&255]
        wanted[9]=fill^toggle
        if boundary:
            wanted[0:2]=[saved_af>>8,saved_af&255]
            wanted[SP]=saved_sp+4
            end_pc,m1=0x3FFF,22
        else:
            wanted[0:2]=[limit,cp_flags(limit,new_h)] if wrapped else [(l+delta)&255,sub8_flags(l,32) if upward else add_flags(l,32)]
            wanted[SP]=0xBFFC
            end_pc,m1=0x3FF0,17 if wrapped else 13
        wanted[15]=refresh(initial[15],m1)
        expected=list(memory)
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        measured_m1=0
        for _ in range(30):
            if simulator.registers[PC] in (0x3FF0,0x3FFF):
                break
            old_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-old_r)&127
            assert increment in (1,2)
            measured_m1+=increment
        else:
            raise AssertionError(('возврат',entry,h,l))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),26,27)
        assert simulator.registers[PC]==end_pc and measured_m1==m1
        assert all(wanted[i]==simulator.registers[i] for i in compared), (entry,h,l,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and not memory.writes
        counts[format(entry,'04X')]+=1
        outcomes['unwind' if boundary else 'page_carry' if wrapped else 'same_page']+=1

    # Проверка каждого HL при обоих направлениях, включая перенос только по младшему адресу E.
    for entry in (0xD925,0xD940):
        for h in range(256):
            for l in range(256):
                check(entry,h,l,(h*256+l)^0xA55A)
    # Проверка восстановления каждого возможного AF через нелокальное завершение рамки рисования.
    for saved_af in range(65536):
        entry=0xD925 if saved_af&1 else 0xD940
        check(entry,0x80 if entry==0xD925 else 0x8B,0 if entry==0xD925 else 255,saved_af)
    # Проверка отдельных сохранённых рамок, границ фиксированных банков и перекрытия с непосредственным возвратом.
    for entry in (0xD925,0xD940):
        for saved_sp in (0x7FFE,0x7FFF,0x8000,0x8FFE,0x9FFE,0xAFFE,0xBFFA,0xBFFE):
            for saved_af in (0,65535,0xA55A,0x5AA5):
                check(entry,0x80 if entry==0xD925 else 0x8B,0 if entry==0xD925 else 255,saved_af,saved_sp)
    result=dict(passed=True,total_cases=sum(counts.values()),cases_by_entry=dict(counts),outcomes=dict(outcomes),
        all_hl_both_directions=True,all_saved_af_words=True,exact_registers_flags_r_and_sp=True,
        every_ram_byte_checked=True,no_memory_writes=True,actual_nonlinear_stack_return=True,
        e_wrap_does_not_change_d=True,ixl_toggled_before_early_return=True,
        direct_full_M1_count_checked=True,saved_frame_7fff_8000_address_boundary_and_overlap_checked=True,
        complete_context_product_exhausted=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsRasterStepVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
