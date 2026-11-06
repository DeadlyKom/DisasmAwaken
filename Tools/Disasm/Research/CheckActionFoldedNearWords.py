"""6A29, три верхних слова с инверсией отрицательных, без математического abs."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh,cp_flags


def profiles():
    for words in product((0,59,60,0x7FFF,0x8000,0xFFC3,0xFFC4,0xFFFF),repeat=3):
        yield words,0xA55A,'boundary_products'
    for position in range(3):
        for word in range(65536):
            words=[0,0xFFFF,1];words[position]=word
            yield tuple(words),word,'all_words_each_position'
    for af in range(65536):
        for words in ((0x1234,0,0),(60,0,0),(0,0,0)):
            yield words,af,'all_input_AF_three_exits'
    randomizer=random.Random(0x6A29)
    for _ in range(8192):
        yield tuple(randomizer.randrange(65536) for _ in range(3)),randomizer.randrange(65536),'mixed_words'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);simulator=Simulator(memory)
    counts=Counter();paths=Counter();costs=set();touched=set();baseline=[bytearray(b) for b in memory.banks]
    for words,af,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        iy=0xA900 if serial&1 else 0x8100;stack=0xBFFE
        setup={stack:255,stack+1:63}
        for offset,word in zip((2,6,10),words):setup[iy+offset],setup[iy+offset+1]=word&255,word>>8
        for address,value in setup.items():memory[address]=value
        touched={(2,address&0x3FFF) for address in setup};old=serial&63;memory.out7ffd(old)
        initial=get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':iy,'SP':stack,'PC':0x6A29},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        # Проверка независимого числового предиката с сохранением инверсии вместо прибавления единицы.
        m1=0
        for position,word in enumerate(words):
            folded=word if word<0x8000 else word^65535;m1+=10+6*(word>=0x8000)
            high=folded>>8
            if high:
                a=high;flags=(high&0xA8)|(4 if high.bit_count()%2==0 else 0);reason='high_nonzero';break
            m1+=3;a=folded&255;flags=cp_flags(a,60)
            if a>=60:reason='low_at_least_60';break
            if position==2:reason='all_three_near'
        wanted=list(initial);wanted[0:2]=[a,flags];wanted[6:8]=[folded>>8,folded&255]
        wanted[15]=refresh(initial[15],m1);wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6A29,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,words,af,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert bool(flags&1)==all(-60<=((w^0x8000)-0x8000)<=59 for w in words)
        assert not memory.writes and memory.o7ffd==old,(serial,'RAM_or_page_write')
        counts[kind]+=1;paths[str(position)+'_'+reason]+=1;costs.add(m1)
    for address,value in setup.items():baseline[2][address&0x3FFF]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        every_word_at_every_component=True,all_input_AF_for_three_exit_types=True,
        exact_registers_including_R=True,carry_iff_each_signed_word_in_minus60_through59=True,
        complement_instead_of_negation_preserved=True,all_physical_ram_bytes_proved=True,
        no_memory_or_stack_writes=True,observed_m1=sorted(costs),complete_three_word_product_exhausted=False,
        lower_two_bytes_per_component_not_read=True,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==401920 and max(costs)==57
    (ROOT/'Tools/Disasm/Reports/ActionFoldedNearWordsVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
