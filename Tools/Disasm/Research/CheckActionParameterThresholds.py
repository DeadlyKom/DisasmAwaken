"""Все 256x256 пары входа и изменяемого CP для класса 0, класса 3 и общего фильтра."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC
from ReferenceActionClassHandlers import ClassMachine
from ReferenceActionFoldedRandom import step


def main():
    # Поиск независимых состояний, выдающих каждый из 256 младших байтов нового слова при FoldByte=0.
    seeds={}
    for word in range(65536):
        seeds.setdefault(step(word,0)['word']&255,word)
    assert set(seeds)==set(range(256))
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);counts=Counter();paths=Counter();cases=0
    for threshold in range(256):
        for value in range(256):
            for entry in (0x660E,0x65DE,0xE6E2):
                memory.recording=False
                for page in (0,2,5):memory.banks[page][:]=baseline[page]
                style=(threshold+value)%4
                rows=() if style==0 else ((1,5),(1,6),(1,7),(1,14),(1,18)) if style==1 else (
                    (1,0),(128,18),(1,16),(1,18)) if style==2 else ((1,0),)*26
                for index,(header,code) in enumerate(rows):
                    address=0xA100+64*index;memory[address],memory[address+1],memory[address+18]=index+1,header,code
                marker=0xA100+64*len(rows);memory[marker],memory[marker+1]=128,128
                ix=0xA100+64*(cases%26);override=0 if cases&1 else 255
                memory[ix+21],memory[ix+10],memory[ix+11]=override,(cases*37)&255,(cases*109)&255
                memory[0x6615]=threshold if entry==0x660E else 112
                memory[0x65E5]=threshold if entry==0x65DE else 6
                memory[0xE6E7]=threshold if entry==0xE6E2 else (threshold*17+value)&255
                seed=seeds[value] if entry==0xE6E2 else seeds[(value+17*threshold)&255]
                memory[0xEBE7],memory[0xEBE8],memory[0xEBE9]=seed&255,seed>>8,0
                word=seeds[(value*7+threshold)&255]
                memory[0xEBE1],memory[0xEBE2],memory[0xEBE3]=word&255,word>>8,(value+threshold)&255
                memory[0x9BCD]=(threshold*17+value*29)&255
                stack=0x8002 if cases&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
                initial=get_registers({'PC':entry,'SP':stack,'AF':(cases*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                r=(value&128)|((value-(14 if override==0 else 8))&127) if entry!=0xE6E2 else cases&255
                initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
                model=ClassMachine(memory.banks,initial)
                if entry==0x660E:model.class0();cp_address=0x6614
                elif entry==0x65DE:model.handle(3);cp_address=0x65E4
                else:model.filtered(0xE6E2);cp_address=0xE6E6
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True;observed=False
                for _ in range(5000):
                    pc=simulator.registers[PC]
                    if pc==0x3FFF:break
                    if pc==cp_address:
                        assert simulator.registers[0]==value,(hex(entry),threshold,value,'CP input')
                        observed=True
                    simulator.run()
                else:raise AssertionError('не достигнут внешний RET')
                memory.recording=False
                assert observed
                assert all(model.r[index]==simulator.registers[index] for index in (*range(25),26,27)),(hex(entry),threshold,value,model.path)
                assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(hex(entry),threshold,value,'RAM')
                counts[hex(entry)]+=1;paths.update(model.path);cases+=1
                if cases%65536==0:print(str(cases)+' threshold cases passed',flush=True)
    assert cases==196608
    result=dict(passed=True,total_cases=cases,cases_by_entry=dict(counts),paths=dict(paths),
        class0_all_256_r_by_256_thresholds=True,class3_all_256_r_by_256_thresholds=True,
        filter_all_256_new_low_bytes_by_256_thresholds=True,actual_compared_input_observed=True,
        thresholds_patched_in_model_ram=True,apply_parameter_set_executed=False,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        all_three_threshold_and_state_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionParameterThresholdsVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key!='paths'},indent=2))


if __name__=='__main__':main()
