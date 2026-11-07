"""EC54, все четыре словарных среза, границы и точный R обоих проходов."""
from collections import Counter
from itertools import product
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers
from CheckMusicGateTicks import Memory
from ReferenceActionProjectedPairCodes import evaluate


def profiles():
    for position in range(4):
        for word in range(65536):
            words=[255,95,256,96];words[position]=word
            yield words,'all_four_word_slices'
    for values in product((0,95,96,255,256,32767,32768,33024,65535),repeat=4):yield values,'four_word_corners'


def main():
    memory=Memory(flat_action());memory[0xBFFE],memory[0xBFFF]=255,63
    simulator=Simulator(memory);counts=Counter();paths=Counter();expected=list(memory)
    for words,kind in profiles():
        memory.recording=False
        for index,word in enumerate(words):
            address=0x8E00+(index//2)*5+(index%2)*2;memory[address],memory[address+1]=word&255,word>>8
            expected[address],expected[address+1]=word&255,word>>8
        serial=counts.total();memory[0x8E04],memory[0x8E09]=serial&255,serial*73&255
        initial=get_registers({'PC':0xEC54,'SP':0xBFFE,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':serial*109&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0xA140},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=evaluate(initial,(words[:2],words[2:]))
        for address,value in model['writes']:expected[address]=value
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xEC54,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(model['registers'][i]==simulator.registers[i] for i in compared),(serial,words,[(i,model['registers'][i],simulator.registers[i]) for i in compared if model['registers'][i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==model['writes'],(serial,'RAM')
        paths['/'.join(model['outcomes'])]+=1;counts[kind]+=1
        if counts.total()%65536==0:print(str(counts.total())+' pair code cases passed',flush=True)
    assert counts.total()==268705 and len(paths)==4,(counts,paths)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_four_word_domains_on_slices=True,exact_registers_flags_r_sp=True,entire_64K_and_write_order_compared=True,
        both_codes_always_written=True,marker_does_not_abort_second_point=True,stack_writes=False,
        complete_four_word_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionProjectedPairCodesVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
