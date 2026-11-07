"""State12, выбор связи, настоящий запрос детей и полный расчёт локальных фаз до RET."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionNearestCandidate import NearestMachine
from CheckActionTargetTransition import ready
from ReferenceActionChildSpawn import SpawnMachine
from ReferenceActionObjectOffsetVector import evaluate
from CheckActionRecordIndex import add_flags


class CombinedMachine(SpawnMachine,NearestMachine):pass


def local_tail(model,flat):
    ix=model.r[8]*256+model.r[9]
    model.put(ix+7,(model.read(ix+7)+1)&255)
    first,second,third=[model.read(ix+o) for o in (13,14,15)]
    offsets=(first,(second+128)&255,third)
    for address,value in zip((0xB045,0xB04F,0xB05C),offsets):model.put(address,value)
    model.r[4:6]=[0,model.read(ix+16)];model.r[0:2]=[third,add_flags(second,128)];model.m1(16)
    result=evaluate(flat,model.r,offsets,model.word(model.r[12]))
    for address,value in result['writes']:model.put(address,value)
    model.r=result['registers'];model.m1_count+=result['refresh_m1'];model.path.append('local_offset_return')
    return model


def run_model(model,flat):
    model.call(0xEA15,0xF6C0,lambda:ready(model));model.m1(1)
    if not model.r[1]&64:
        model.call(0xE9C2,0xF6C5,model.nearest)
        ix=model.r[8]*256+model.r[9];model.put(ix+11,model.r[0]);model.r[0]=14;model.m1(3)
        model.call(0xE86B,0xF6CD,model.spawn)
    else:model.path.append('gate_skips_link_and_spawn')
    return local_tail(model,flat)


def profiles():
    for seed in range(65536):yield 8,seed&255,3,seed,0,'all_stream11_words'
    for code in range(256):
        for r in (0,1,63,64,127,128,254,255):
            for style in range(4):yield code,r,style,(code*137+r*257)&65535,0,'all_classes_with_R_edges'
    for reuse in range(256):yield 8,reuse,3,reuse*257,reuse,'all_parent_reuse_bytes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();depth=0
    for code,r,style,seed,reuse,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for index in range(25):
            address=0xA100+64*index;memory[address],memory[address+1],memory[address+24]=0,1,0
        for index in range((0,1,2,2)[style]):memory[0xA101+64*index]=128
        memory[0xA740],memory[0xA741]=128,128
        items=((254,),(24,254),(1,254),(255,24,254))[style]
        for index,value in enumerate(items):memory[0xA01C+index]=value
        ix=0xA700;parent=(0x1234,0x2345,0x3456)
        for axis,value in enumerate(parent):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
        values={7:r,8:seed&255,9:seed>>8,10:18,11:(cases*73)&255,13:seed&255,14:r,15:(r*73+code)&255,
                16:(seed+r)&255,18:code,24:reuse}
        for offset,value in values.items():memory[ix+offset]=value
        memory[0xEBED],memory[0xEBEE],memory[0xEBEF]=seed&255,seed>>8,0
        memory[0xE9FE]=(cases*37)&255
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF6BD,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=CombinedMachine(memory.banks,initial);run_model(model,flat)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(4000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',code,r,style))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        for bank,offset,_ in memory.writes:
            if bank==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path);cases+=1
        if cases%32768==0:print(str(cases)+' acquire local state cases passed',flush=True)
    assert cases==73984 and depth==8 and paths['child_written'] and paths['allocation_return_with_EXX'] and paths['gate_skips_link_and_spawn']
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),maximum_additional_stack_bytes=depth,
        all_stream11_words_at_fold_zero=True,all_classes_with_eight_R_edges_and_four_lists=True,
        all_parent_reuse_bytes=True,real_gate_nearest_spawn_coefficients_and_multiply_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        complete_external_return=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionAcquireLocalStateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
