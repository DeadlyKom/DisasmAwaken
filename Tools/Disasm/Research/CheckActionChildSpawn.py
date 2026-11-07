"""E86B, фактические поиск, индекс, поток 11 и все поля одной либо двух дочерних записей."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionChildSpawn import SpawnMachine
from ReferenceActionFoldedRandom import step


def profiles():
    for seed in range(65536):yield seed,0,seed&255,2,14,0,seed&1,'all_stream11_words'
    seed=next(seed for seed in range(65536) if step(seed,0)['word']&255==0)
    for r in range(256):
        for style in range(6):
            for state in (0,2,14,255):yield seed,0,r,style,state,0,r&1,'all_R_styles_and_states'
    for reuse in range(256):
        for carry in (0,1):yield seed,0,reuse,2,14,reuse,carry,'all_reuse_bytes_and_carry'
    for fold in range(256):
        for word in (0,1,0x7FFF,0x8000,0xFFFF):yield word,fold,fold,2,14,0,fold&1,'all_fold_bytes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();depth=0
    for seed,fold,r,style,state,reuse,carry,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for index in range(25):
            pointer=0xA100+64*index;memory[pointer],memory[pointer+1],memory[pointer+24]=0,1,0
        free_count=(0,1,2,3,2,2)[style]
        for index in range(free_count):memory[0xA101+64*index]=128
        if style==3:memory[0xA118]=255
        memory[0xA740],memory[0xA741]=128,128
        ix=0xA700;parent=(0x7F00,0x2345,0x3456) if style==4 else (0xFF80,0x2345,0x3456) if style==5 else (0x1234,0x2345,0x3456)
        for axis,value in enumerate(parent):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
        memory[ix+24],memory[ix+11]=reuse,(cases*73)&255
        memory[0xEBED],memory[0xEBEE],memory[0xEBEF]=seed&255,seed>>8,fold
        memory[0xE8F1]=(cases*109)&255
        stack=0x8002 if cases&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xE86B,'SP':stack,'AF':(state<<8)|(0xFE|carry),'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=SpawnMachine(memory.banks,initial);model.spawn()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(3000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',seed,style))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,profile,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        for bank,offset,_ in memory.writes:
            if bank not in (2,5):continue
            address=offset+(0x4000 if bank==5 else 0x8000)
            if stack-8<=address<stack:depth=max(depth,stack-address)
        counts[profile]+=1;paths.update(model.path);cases+=1
        if cases%32768==0:print(str(cases)+' child spawn cases passed',flush=True)
    assert cases==73472 and depth==4 and paths['requested_2'] and paths['allocation_return_with_EXX'] and paths['skip_once'],(cases,depth,dict(paths))
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),maximum_additional_stack_bytes=depth,
        all_stream11_words_at_fold_zero=True,all_256_R_values_and_four_state_arguments=True,
        all_reuse_bytes_and_input_carry=True,all_fold_bytes=True,real_reuse_index_and_stream_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        early_allocation_return_preserves_unbalanced_EXX=True,allocation_failure_does_not_clear_parent_bit2=True,
        all_input_products_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionChildSpawnVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
