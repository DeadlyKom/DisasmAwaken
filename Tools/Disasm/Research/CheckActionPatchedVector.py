"""AF43, девять настоящих умножений, перенос от отрицания, частичные выходы и временный SP."""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory,xor_flags
from ReferenceControlsBufferPoints import sub16_flags
from ReferenceControlsPointRespawn import refresh
from CheckActionScaledMultiply import signed
INPUTS=(0xAF48,0xAF56,0xAF69)
COEFFICIENTS=((0xCB3E,0xCB54,0xCB6F),(0xCB8B,0xCBA1,0xCBBC),(0xCBD8,0xCBEE,0xCC09))
OUTPUTS=(0xD9B6,0xD7C4,0xD7A2)


def adc16(a,b,carry):
    total=a+b+carry;value=total&65535
    flags=((value>>8)&0xA8)|(64 if not value else 0)|(16 if (a&4095)+(b&4095)+carry>4095 else 0)|(
        4 if (~(a^b)&(a^value)&32768) else 0)|int(total>65535)
    return value,flags


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set()
    def check(vector,matrix,kind):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=baseline[address]
        for address,value in zip(INPUTS,vector):memory[address:address+2]=[value&255,value>>8]
        for addresses,values in zip(COEFFICIENTS,matrix):
            for address,value in zip(addresses,values):memory[address]=value
        for n,address in enumerate(OUTPUTS):memory[address:address+2]=[n+0x42,n+0x53]
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x3FFF,
            'SP':0xBFFE,'PC':0xAF43},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[(0xAFF1,0xCD),(0xAFF2,0xAB)];m1=2;outcome='complete';stop=False
        # Расчёт компонентов по проверенному договору реального дочернего умножителя.
        for row in range(3):
            partial=0
            for column in range(3):
                coefficient=matrix[row][column];value=vector[column]
                cv,vv=signed(coefficient,8),signed(value,16);factor=abs(cv)&127
                product=factor*abs(vv);magnitude=product//128;negative=bool((coefficient^(value>>8))&128)
                result=(-magnitude if negative else magnitude)&65535;sign=coefficient^(value>>8)
                flags=sub16_flags(0,magnitude) if negative else xor_flags(sign)
                de=magnitude if negative else abs(vv);upper=product>>15;previous=product>>16;carry=(product>>15)&1
                wanted[0:2]=[sign,flags];wanted[3]=0;wanted[4:6]=[de>>8,de&255]
                wanted[16:18]=[upper,(upper&0x28)|(64 if not upper else 0)|(16 if (previous&15)*2+carry>15 else 0)]
                child=(35+factor.bit_length()-1+2*factor.bit_count() if factor else 32)+7*(vv<0)+2*(cv<0)+4*negative
                m1+=(5 if row==0 else 6) if column==0 else (6 if row==0 else 7)
                m1+=child
                if column:
                    # Расчёт исходного ADC с Carry от SBC отрицательного произведения, он не очищается.
                    result,flags=adc16(result,partial,flags&1);wanted[1]=flags;m1+=3
                    if flags&4:outcome='overflow_'+str(row)+'_'+str(column);stop=True
                wanted[6:8]=[result>>8,result&255]
                if stop:break
                if column<2:partial=result;wanted[SP]=partial
            if stop:break
            address=OUTPUTS[row];writes.extend([(address,result&255),(address+1,result>>8)]);m1+=1
        m1+=4;wanted[PC],wanted[15]=0x3FFF,refresh(initial[15],m1)
        for address,value in writes:expected[address]=value
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(0xAF43,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(vector,matrix,outcome,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(vector,matrix,outcome,memory.writes,writes)
        touched={address for address,_ in writes};counts[kind]+=1;paths[outcome]+=1
    # Проверка всех слов каждой входной компоненты с диагональными коэффициентами 7F.
    for axis in range(3):
        for value in range(65536):
            vector=[0,0,0];vector[axis]=value;check(vector,((127,0,0),(0,127,0),(0,0,127)),'all_axis_words')
        print('Axis '+str(axis)+' complete',flush=True)
    # Проверка каждого коэффициента каждой позиции на граничных входных векторах.
    for row in range(3):
        for column in range(3):
            for value in range(256):
                matrix=[[0]*3 for _ in range(3)];matrix[row][column]=value
                for word in (0,1,32767,32768,65535):check((word,word,word),matrix,'all_matrix_byte_positions')
    # Проверка каждой точки аварийного выхода, обоих знаков переполнения и сохранения частичных выходов.
    for row in range(3):
        matrix=[[0]*3 for _ in range(3)];matrix[row]=[127]*3
        for word in (32767,32768,16000,(-16000)&65535):check((word,word,word),matrix,'six_overflow_sites')
    # Проверка смешанных матриц и знаков с воспроизводимой последовательностью.
    randomizer=random.Random(0xAF43)
    for _ in range(4096):check([randomizer.randrange(65536) for _ in range(3)],
        [[randomizer.randrange(256) for _ in range(3)] for _ in range(3)],'mixed_vectors_and_matrices')
    assert all(paths['overflow_'+str(row)+'_'+str(column)] for row in range(3) for column in (1,2))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        method='parent_component_oracle_composed_with_independently_checked_real_scaled_multiplier',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        all_words_on_each_axis=True,all_matrix_byte_positions=True,all_six_overflow_sites=True,
        original_carry_from_negative_products_preserved=True,partial_output_writes_preserved=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        sp_is_arithmetic_scratch_and_not_restored=True,ix_restored_through_self_modification=True,jp_iy_continuation=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPatchedVectorVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
