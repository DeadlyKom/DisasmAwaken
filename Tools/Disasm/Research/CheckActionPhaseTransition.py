"""Переходы E935, реальный поток 5, независимый расчёт ветвей и всех записей."""
from collections import Counter
from itertools import product
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionRecordFilters import Machine
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import cp_flags


def transition(model):
    pointer=model.r[8]*256+model.r[9]
    model.call(0xEB8E,0xE938,lambda:model.stream(5))
    high,low=model.r[6:8]
    model.m1(3)
    if high>=250:
        model.m1(3)
        if low>=239:
            saved=model.read(pointer+10)
            model.put(pointer+22,saved);model.put(pointer+10,19)
            model.m1(6);model.path.append('random_wait')
    # Проверка свёрнутых байтов не зависит от результата случайного перехода.
    for offset,limit in ((27,2),(29,2),(31,6)):
        value=model.read(pointer+offset)
        folded=value if value<128 else value^255
        model.r[0:2]=[folded,cp_flags(folded,limit)]
        model.m1(6+int(value>=128))
        if folded>=limit:
            model.path.append('reject_'+str(offset));return model.finish()
    saved=model.read(pointer+10)
    model.put(pointer+22,saved);model.put(pointer+10,20);model.put(pointer+23,30)
    model.r[0]=saved;model.m1(9);model.path.append('offset_rise')
    return model.finish()


def profiles():
    # Проверка всего исходного слова потока при нулевом байте свёртки и трёх различных исходах полей.
    for seed in range(65536):
        yield seed,0,((0,0,0),(128,0,0),(255,255,255))[seed%3],seed&255,'all_words'
    # Поиск представителя каждой комбинации двух случайных порогов по независимой формуле потока.
    seeds={}
    for seed in range(65536):
        word=step(seed,0)['word'];seeds.setdefault((word>>8>=250,(word&255)>=239),seed)
    assert len(seeds)==4
    edges=(0,1,2,5,6,127,128,249,250,253,254,255)
    for seed in seeds.values():
        for values in product(edges,repeat=3):yield seed,0,values,0xA5,'joint_boundaries'
        for axis in range(3):
            for value in range(256):
                values=[0,0,0];values[axis]=value
                yield seed,0,tuple(values),value,'all_field_bytes'
        for state in range(256):
            yield seed,0,(0,0,0),state,'all_states'
            yield seed,0,(128,0,0),state,'all_states'
    for fold in range(256):
        for seed in (0,1,0x7FFF,0x8000,0xFFFF):
            yield seed,fold,(fold,fold^255,(fold*17)&255),fold,'all_fold_bytes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();overwritten=0
    for seed,fold,values,state,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100+64*(cases%26);stack=0x8002 if cases&1 else 0xBFFE
        memory[stack],memory[stack+1]=255,63
        memory[0xEC05],memory[0xEC06],memory[0xEC07]=seed&255,seed>>8,fold
        memory[ix+10],memory[ix+22],memory[ix+23]=state,(cases*37)&255,(cases*73)&255
        for offset,value in zip((27,29,31),values):memory[ix+offset]=value
        initial=get_registers({'PC':0xE935,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        model=Machine(memory.banks,initial);transition(model)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xE935,stop=0x3FFF)
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,profile,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        assert memory[stack]==255 and memory[stack+1]==63
        if 'random_wait' in model.path and 'offset_rise' in model.path:
            assert memory[ix+22]==19 and memory[ix+10]==20 and memory[ix+23]==30
            overwritten+=1
        paths.update(model.path);counts[profile]+=1;cases+=1
        if cases%32768==0:print(str(cases)+' phase transition cases passed',flush=True)
    assert cases==78848 and overwritten and all(paths['reject_'+str(v)] for v in (27,29,31))
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),double_transition_cases=overwritten,
        real_stream5_executed=True,exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        stack_bytes=4,original_return_word_preserved=True,all_words_at_fold_zero=True,all_input_state_bytes=True,
        all_field_bytes_and_joint_boundaries=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPhaseTransitionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
