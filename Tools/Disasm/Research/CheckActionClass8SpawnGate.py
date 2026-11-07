"""E863, полный класс 8, состояние ребёнка 2 и реальный физический хвост E86B."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionChildSpawn import SpawnMachine
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import cp_flags


def main():
    # Поиск исходных слов с младшими результатами по обе стороны допуска потока 11.
    seeds={}
    for word in range(65536):
        low=step(word,0)['word']&255
        if low in (0,9,10,255):seeds.setdefault(low,word)
    assert set(seeds)=={0,9,10,255}
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter()
    for code in range(256):
        for reuse in (0,4):
            for r in (0,1,63,64,127,128,254,255):
                for seed in seeds.values():
                    memory.recording=False
                    for page in (0,2,5):memory.banks[page][:]=baseline[page]
                    for index in range(25):
                        address=0xA100+64*index;memory[address],memory[address+1],memory[address+24]=0,1,0
                    memory[0xA101],memory[0xA141]=128,128;memory[0xA740],memory[0xA741]=128,128
                    ix=0xA700
                    for axis,value in enumerate((0x1234,0x2345,0x3456)):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
                    memory[ix+18],memory[ix+24],memory[ix+11]=code,reuse,24
                    memory[0xEBED],memory[0xEBEE],memory[0xEBEF]=seed&255,seed>>8,0
                    stack=0xBFFE;memory[stack],memory[stack+1]=255,63
                    initial=get_registers({'PC':0xE863,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                    initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
                    model=SpawnMachine(memory.banks,initial);model.r[0:2]=[code,cp_flags(code,8)]
                    if code==8:model.m1(5);model.r[0]=2;model.spawn();paths['class8']+=1
                    else:model.m1(4);model.finish();paths['other_class']+=1
                    simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                    for _ in range(3000):
                        if simulator.registers[24]==0x3FFF:break
                        simulator.run()
                    else:raise AssertionError('нет внешнего возврата')
                    memory.recording=False
                    assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(code,reuse,r,model.path)
                    assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes)
                    paths.update(model.path);cases+=1
    assert cases==16384 and paths['class8']==64 and paths['child_written']
    result=dict(passed=True,total_cases=cases,paths=dict(paths),all_full_class_bytes=True,
        real_child_spawn_tail_executed=True,child_state_argument=2,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_additional_stack_bytes=4,complete_external_return=True,
        all_input_products_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass8SpawnGateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
