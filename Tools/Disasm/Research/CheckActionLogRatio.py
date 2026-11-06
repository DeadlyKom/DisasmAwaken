"""AE73, фактическая нормализация и две таблицы, знаки, особые нули и изменяемые JR."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from ReferenceActionLogRatio import LOG,EXP,evaluate


def main():
    baseline=flat_action()
    baseline[0x9100:0x9200]=[v&255 for v in LOG];baseline[0x9200:0x9300]=[v>>8 for v in LOG];baseline[0x9300:0x9400]=EXP
    memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();touched=set()
    def check(numerator,denominator):
        nonlocal touched
        memory.recording=False
        for address in touched:memory[address]=baseline[address]
        memory[0xBFFE:0xC000]=[255,63];serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':numerator,'DE':denominator,'BC':0x369C,
            '^AF':(serial*73)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xAE73},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);reference=evaluate(numerator,denominator);expected=list(memory)
        for address,value in reference['writes']:expected[address]=value
        for position,key in ((6,'hl'),(4,'de'),(2,'bc')):
            value=reference[key];wanted[position:position+2]=[value>>8,value&255]
        wanted[0:2]=reference['af'];wanted[16:18]=reference['alternate_af']
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],reference['refresh_m1'])
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0xAE73,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(numerator,denominator,reference,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==reference['writes'],(numerator,denominator,memory.writes,reference['writes'])
        touched={a for a,_ in memory.writes};counts[reference['path']]+=1
    # Проверка каждого слова числителя и знаменателя по независимым сечениям.
    for word in range(65536):check(word,256);check(511,word)
    # Проверка обоих знаков, крайних аргументов и нулей во всех парах выбранных границ.
    edges=(0,1,2,127,128,255,256,257,511,512,32767,32768,32769,65534,65535)
    for numerator in edges:
        for denominator in edges:check(numerator,denominator)
    # Проверка каждой мантиссы в каждом восьмибитовом диапазоне нормализации и при нескольких знаковых числителях.
    for index in range(256):
        for shift in range(8):
            for numerator in (0,1,127,128,511,32767,32768,65535):check(numerator,(index<<shift)&65535)
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),
        method='independent_normalized_table_formula_and_shift_oracle',
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
        actual_tables_from_verified_integer_generator_formulas=True,all_numerator_words=True,all_denominator_words=True,
        original_zero_and_negative_denominator_behavior_preserved=True,self_modifying_shift_displacements_checked=True,
        maximum_additional_stack_bytes=0,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLogRatioVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
