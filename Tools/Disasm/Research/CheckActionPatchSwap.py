"""AD1D, обмен полных слов в коде, включая байты префиксов, без исполнения потребителя."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
PAIRS=((0xCB8B,0xCB54),(0xCBD8,0xCB6F),(0xCBEE,0xCBBC))


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory);counts=Counter()
    def check(words,kind,twice=False):
        memory.recording=False
        for pair,values in zip(PAIRS,words):
            for address,value in zip(pair,values):memory[address:address+2]=[value&255,value>>8]
        memory[0xBFFE:0xC000]=[255,63];serial=counts.total()
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xAD1D},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[];before=list(memory)
        # Расчёт трёх независимых обменов полных слов, значения не ограничены исходным префиксом CB.
        for (left,right),(a,b) in zip(PAIRS,words):
            writes.extend([(right,a&255),(right+1,a>>8),(left,b&255),(left+1,b>>8)])
        for address,value in writes:expected[address]=value
        wanted[6:8]=[words[-1][0]>>8,words[-1][0]&255];wanted[4:6]=[words[-1][1]>>8,words[-1][1]&255]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],19)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(0xAD1D,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(words,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes)
        if twice:
            # Проверка восстановления исходных двенадцати байтов вторым настоящим вызовом.
            simulator.registers[SP]=0xBFFE;simulator.run(0xAD1D,0x3FFF);assert memory==before
        counts[kind]+=1
    # Проверка всех 65536 значений каждого из двух слов по каждой независимой паре.
    for pair in range(3):
        for value in range(65536):
            words=[(0x1234,0xABCD),(0x5678,0x9ABC),(0xDEF0,0x1357)]
            words[pair]=(value,value^65535);check(words,'all_words_by_pair')
        print('Pair '+str(pair)+' complete',flush=True)
    # Проверка каждого одинакового байта всех шести слов и обратимости двух вызовов.
    for value in range(256):check([(value*257,value*257)]*3,'identical_words_and_involution',True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        method='independent_three_word_permutations_against_original_instructions',
        all_word_values_in_each_pair=True,all_joint_word_tuples_exhausted=False,
        full_words_including_opcode_prefixes_swapped=True,involution_with_real_second_call_checked=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        no_cpu_stack_writes=True,refresh_m1=19,consumer_executed=False,
        game_meaning_of_patch_pairs_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPatchSwapVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
