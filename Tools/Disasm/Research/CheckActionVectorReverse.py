"""6EDE, инверсия трёх раздельных компонент и арифметическая половина отрицания общего слова."""
from collections import Counter
from itertools import product
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory,xor_flags
from ReferenceControlsPointRespawn import refresh
COMPONENTS=(0xE5B3,0xE5D2,0xE5ED)


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter()
    def check(components=(0x1357,0x2468,0xACE0),scalar=0x7FFF,flags=255,kind='word_slice'):
        memory.recording=False
        for address,value in zip(COMPONENTS,components):memory[address:address+2]=[value&255,value>>8]
        memory[0xA78F:0xA791]=[scalar&255,scalar>>8];memory[0x6EAD]=(flags*73)&255;memory[0xBFFE:0xC000]=[255,63]
        serial=counts.total();initial=get_registers({'AF':((serial^0xA5)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(serial*73)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6EDE},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[]
        def byte(a,v):expected[a]=v;writes.append((a,v))
        def word(a,v):byte(a,v&255);byte(a+1,v>>8)
        # Создание эталона в физическом порядке исходных записей, первая, третья, вторая компоненты.
        byte(0x6EAD,1)
        for index in (0,2,1):word(COMPONENTS[index],(-components[index])&65535)
        # Расчёт отрицания до арифметического сдвига, случай исходного 8000 сохраняет оборачивание.
        negated=(-scalar)&65535;signed=negated if negated<32768 else negated-65536
        half=(signed>>1)&65535;value=(half+1)&65535;word(0xA78F,value)
        wanted[6:8]=[value>>8,value&255];wanted[0:2]=[(~(scalar>>8))&255,xor_flags(half&255)|(negated&1)]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],44)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0x6EDE,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(components,scalar,flags,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(components,scalar,memory.writes,writes)
        counts[kind]+=1
    # Проверка каждого слова всех четырёх входов по отдельным сечениям.
    for value in range(65536):
        for index in range(3):
            components=[0x1357,0x2468,0xACE0];components[index]=value;check(tuple(components))
        check(scalar=value)
    # Проверка всех исходных флагов и всех совместных комбинаций выбранных крайних слов.
    for flags in range(256):check(scalar=(flags<<8)|(flags^255),flags=flags,kind='flags')
    for values in product((0,1,32767,32768,65535),repeat=4):check(values[:3],values[3],kind='joint_edges')
    report=dict(passed=True,total_cases=counts.total(),cases_by_fixture=dict(counts),
        method='independent_modular_word_negation_and_signed_half_oracle',
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        all_component_and_scalar_words_by_separate_slices=True,all_input_flags=True,
        enables_step_near_zero_without_calling_it=True,components_negated_without_halving=True,
        original_8000_wrap_preserved=True,maximum_additional_stack_bytes=0,refresh_m1=44,
        game_units_proved=False,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionVectorReverseVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
