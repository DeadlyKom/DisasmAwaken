"""D12C, независимые произведение, знаковые флаги и M1, выход настоящим JP (IX)."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub16_flags
from ReferenceControlsPointRespawn import refresh
from CheckMusicGateTicks import xor_flags


def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory);counts=Counter()
    def check(coefficient,value,kind):
        serial=counts.total();cv=signed(coefficient,8);vv=signed(value,16);factor=abs(cv)&127
        product=factor*abs(vv);magnitude=product//128;negative=bool((coefficient^(value>>8))&128)
        result=(-magnitude if negative else magnitude)&65535;sign_byte=coefficient^(value>>8)
        upper=product>>15;previous=product>>16;carry=(product>>15)&1
        alt_flags=(upper&0x28)|(64 if upper==0 else 0)|(16 if (previous&15)*2+carry>15 else 0)
        flags=sub16_flags(0,magnitude) if negative else xor_flags(sign_byte)
        initial=get_registers({'AF':coefficient*256+(serial&255),'HL':0x1357,'DE':value,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0x3FFF,'IY':0x5C3A,'SP':0xBFFE,'PC':0xD12C},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);wanted[0:2]=[sign_byte,flags];wanted[3]=0
        de=magnitude if negative else abs(vv);wanted[4:6]=[de>>8,de&255];wanted[6:8]=[result>>8,result&255]
        wanted[16:18]=[upper,alt_flags];wanted[PC]=0x3FFF
        # Расчёт стоимости по старшему установленному разряду и числу единиц семибитного модуля.
        m1=(35+factor.bit_length()-1+2*factor.bit_count() if factor else 32)+7*(vv<0)+2*(cv<0)+4*negative
        wanted[15]=refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(0xD12C,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(coefficient,value,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==original and not memory.writes
        counts[kind]+=1
    # Проверка всех знаковых координат с граничными коэффициентами и нештатным 80.
    for coefficient in (0,1,127,128,129,255):
        for value in range(65536):check(coefficient,value,'all_words_for_six_coefficients')
        print('Coefficient '+format(coefficient,'02X')+' complete',flush=True)
    # Проверка всех коэффициентов на каждой старшей части координаты и шести младших границах.
    for coefficient in range(256):
        for high in range(256):
            for low in (0,1,127,128,254,255):check(coefficient,high*256+low,'all_coefficients_and_high_bytes')
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        method='independent_integer_product_flags_and_bitcount_cost_against_original_instructions',
        all_words_for_coefficients=[0,1,127,128,129,255],all_coefficients_and_coordinate_high_bytes=True,
        coefficient_80_original_zero_result_preserved=True,exact_registers_flags_refresh_sp=True,
        every_ram_byte_checked=True,no_memory_writes=True,sp_unchanged=True,jp_ix_continuation=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionScaledMultiplyVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
