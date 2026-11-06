"""6986, сравнение первой пары слов, второй только при равенстве первой, A сохраняется."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsBufferPoints import sub16_flags


def profiles():
    for word in range(65536):
        for right in (0,1,0x7FFF,0xFFFF):yield (word,right,(word*73)&65535,(word*109+17)&65535),word,'all_first_words'
    for word in range(65536):
        for right in (0,1,0x7FFF,0xFFFF):yield (0x1357,0x1357,word,right),word,'all_second_words'
    for af in range(65536):
        yield (1,0,0x2468,0x369C),af,'all_input_AF'
        yield (1,1,0x2468,0x369C),af,'all_input_AF'
    randomizer=random.Random(0x6986)
    for _ in range(8192):yield tuple(randomizer.randrange(65536) for _ in range(4)),randomizer.randrange(65536),'mixed_words'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);memory[0xBFFE],memory[0xBFFF]=255,63
    baseline=[bytearray(b) for b in memory.banks];simulator=Simulator(memory);counts=Counter();paths=Counter()
    template=get_registers({'AF':0,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6986},None,False)
    addresses=(0x9BC1,0x9BC6,0x9BC3,0x9BC8)
    for values,af,kind in profiles():
        serial=counts.total();memory.recording=False
        for address,value in zip(addresses,values):memory[address],memory[address+1]=value&255,value>>8
        initial=list(template);initial[0:2]=[af>>8,af&255]
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        # Выбор сравниваемого слова по равенству первой пары, без переноса первого вычитания во второе.
        left,right=values[0:2] if values[0]!=values[1] else values[2:4]
        result=(left-right)&65535;wanted=list(initial)
        wanted[4:8]=[right>>8,right&255,result>>8,result&255];wanted[1]=sub16_flags(left,right)
        m1=7 if values[0]!=values[1] else 14
        wanted[15]=refresh(initial[15],m1);wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6986,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(values,af,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert not memory.writes,(values,'RAM_write')
        counts[kind]+=1;paths['first_difference' if m1==7 else 'second_comparison']+=1
    for address,value in zip(addresses,values):baseline[2][address&0x3FFF],baseline[2][(address+1)&0x3FFF]=value&255,value>>8
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_first_words_at_four_other_edges=True,all_second_words_at_four_other_edges=True,
        all_input_AF_for_both_paths=True,exact_registers_including_R=True,A_preserved=True,
        Z_iff_both_word_pairs_equal=True,step_control_bytes_not_compared=True,
        all_physical_ram_bytes_proved=True,no_memory_or_stack_writes_in_any_case=True,
        final_eight_banks_match_input_fixture=True,first_difference_refresh_m1=7,second_comparison_refresh_m1=14,
        complete_four_word_product_exhausted=False,independent_word_pair_oracle=True,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==663552
    (ROOT/'Tools/Disasm/Reports/ActionContextWordPairsVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
