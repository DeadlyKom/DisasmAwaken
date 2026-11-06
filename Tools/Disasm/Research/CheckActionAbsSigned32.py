"""7F76, модуль 32-битного DE:HL по модулю 2^32, минимальное отрицательное значение сохранено."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh
from CheckActionPatchedVector import adc16


def profiles():
    for high in (0,0x7FFF,0x8000,0xFFFF):
        for low in range(65536):yield (high<<16)|low,low&255,'all_low_words'
    for high in range(65536):
        for low in (0,1,0x7FFF,0x8000,0xFFFF):yield (high<<16)|low,high&255,'all_high_words'
    for af in range(65536):
        for value in (0x12345678,0xFEDCBA98):yield value,af,'all_input_AF'
    randomizer=random.Random(0x7F76)
    for _ in range(8192):yield randomizer.getrandbits(32),randomizer.randrange(65536),'mixed_dwords'


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=base,out7ffd=16);memory[0xBFFE],memory[0xBFFF]=255,63
    baseline=[bytes(b) for b in memory.banks];simulator=Simulator(memory);counts=Counter();paths=Counter()
    template=get_registers({'AF':0,'HL':0,'DE':0,'BC':0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
        '^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x7F76},None,False)
    for value,af,kind in profiles():
        serial=counts.total();high,low=value>>16,value&65535;negative=bool(value&0x80000000)
        initial=list(template);initial[0:2]=[af>>8,af&255];initial[2:4]=[(serial*109>>8)&255,(serial*109)&255]
        initial[4:8]=[high>>8,high&255,low>>8,low&255]
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial)
        # Расчёт полного модуля отдельно от последовательности дополнений и переносов исходного кода.
        result=(-value)&0xFFFFFFFF if negative else value
        if negative:
            wanted[2:4]=[0,0];wanted[0]=initial[7]^255
            _,wanted[1]=adc16(high^65535,0,int(low==0));m1=23
        else:wanted[1]=0x54|(initial[4]&0x28)|(initial[1]&1);m1=3
        wanted[4:8]=[result>>24,(result>>16)&255,(result>>8)&255,result&255]
        wanted[15]=refresh(initial[15],m1);wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x7F76,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(hex(value),af,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert not memory.writes,(hex(value),'unexpected_RAM_write')
        counts[kind]+=1;paths['negative' if negative else 'nonnegative']+=1
        if counts.total()%131072==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(bytes(b)==reference for b,reference in zip(memory.banks,baseline))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_low_words_at_four_high_boundaries=True,all_high_words_at_five_low_boundaries=True,
        all_input_AF_for_both_sign_paths=True,exact_registers_including_R=True,
        all_physical_ram_bytes_proved=True,no_memory_or_stack_writes_in_any_case=True,
        final_eight_banks_match_initial_state=True,minimum_80000000_preserved=True,
        minimum_signed_overflow_PV_preserved=True,nonnegative_refresh_m1=3,negative_refresh_m1=23,
        complete_32_bit_domain_exhausted=False,independent_integer_abs_oracle=True,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==729088
    (ROOT/'Tools/Disasm/Reports/ActionAbsSigned32Verification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
