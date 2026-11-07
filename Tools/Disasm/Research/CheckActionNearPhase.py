"""F087 и два родительских состояния, реальные широкие векторы, потоки и фазовые хвосты."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionNearestCandidate import NearestMachine
from CheckActionPhaseTransition import transition
from CheckActionTargetTransition import run_model as target_transition
from ReferenceActionNearVectorSearch import evaluate
from ReferenceControlsPointRespawn import cp_flags
from CheckActionRecordSearch import inc_flags


def near_vector(model,rows):
    return_address=model.word(model.r[12]);result=evaluate(model.r,rows)
    for address,value in result['writes']:model.put(address,value)
    model.r=result['registers'];model.r[24]=return_address;model.m1_count+=result['refresh_m1']


def folded_high(model):
    raw=[model.read(a) for a in (0x9B71,0x9B74,0x9B77)]
    x,y,z=[value if value<128 else value^255 for value in raw]
    model.r[7]=max(x,y,z);model.r[0:2]=[z,cp_flags(z,max(x,y))]
    return model.finish(15+sum(value>>7 for value in raw)+int(y>=x)+int(z>=max(x,y)))


def core(model,rows):
    model.call(0x69BE,0xF08A,lambda:near_vector(model,rows));low=model.r[7]
    model.r[0:2]=[low,cp_flags(low,4)];model.m1(3)
    if low<4:
        limit=40+4*low;model.put(0xF09D,limit);model.m1(4)
        model.call(0xEB72,0xF099,lambda:model.stream(0))
        half=model.r[6]>>1;model.r[0:2]=[half,cp_flags(half,limit)];model.m1(5)
        if half>=limit:
            low=model.r[7];model.r[0:2]=[low,cp_flags(low,127)];model.m1(3)
            if low==127:
                pointer=model.r[8]*256+model.r[9];model.put(pointer+10,6);model.m1(3)
                model.r[24]=0xF0F8;model.path.append('state_06');return model
        model.path.append('random_no_state_06')
    else:model.path.append('wide_not_small')
    model.call(0x699C,0xF0AF,lambda:folded_high(model));value=model.r[7]
    model.r[0:2]=[value,cp_flags(value,4)];model.m1(3)
    if value<4:
        pointer=model.r[8]*256+model.r[9];old=model.read(pointer+8);model.r[0:2]=[(old+1)&255,inc_flags(old,1)]
        model.put(pointer+8,(old+1)&255);model.m1(6);model.path.append('increment_phase1')
    else:model.path.append('global_not_small')
    model.r[24]=0xF0F8;return model


def model_entry(model,entry,rows):
    if entry==0xF07C:
        model.call(0xE935,0xF07F,lambda:transition(model));model.m1(1)
    elif entry==0xF081:
        model.call(0xE91E,0xF084,lambda:target_transition(model));model.m1(1)
        if model.r[1]&1:
            model.r[24]=0xF0F8;model.path.append('carry_skip_near');return model
    return core(model,rows)


ROWS=((),((0,0,0),),((0x10000,0,0),),((0x30000,0,0),),((0x40000,0,0),),
      ((0x3B0000,0,0),),((0x7FFFFFFF,0,0),),((0x7FFFFFFF,0,0),(0,0,0)))


def profiles():
    for seed in range(65536):yield 0xF087,seed,((seed%4<<16,0,0),),(0,0,0),seed&255,0,0,0,'all_stream0_words'
    for rows in ROWS:
        for axis in range(3):
            for value in range(256):
                values=[0,0,0];values[axis]=value
                yield 0xF087,value*257,rows,tuple(values),value,0,0,0,'all_global_bytes_and_rows'
    for entry in (0xF07C,0xF081):
        for code in range(26):
            for r in range(0,256,17):
                for style in range(4):
                    values=(0,0,0) if style&1 else (128,128,128)
                    yield entry,(code*137+r*257)&65535,ROWS[(code+r+style)%8],values,r,r,code,style,'parent_states'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();by_entry=Counter();depth=0
    for entry,seed,rows,globals_,phase,r,code,style,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        memory[0x688B]=len(rows)
        for index,values in enumerate(rows):
            for axis,value in enumerate(values):
                for byte in range(4):memory[0x9B27+12*index+4*axis+byte]=value>>(8*byte)&255
        for address,value in zip((0x9B71,0x9B74,0x9B77),globals_):memory[address]=value
        memory[0xA108],memory[0xA112],memory[0xA10A]=phase,code,3 if entry==0xF081 else 15
        for offset in (27,29,31):memory[0xA100+offset]=0 if style&1 else 128
        for pointer,word in ((0xEBDE,seed),(0xEC05,seed^0x5A5A)):
            memory[pointer],memory[pointer+1],memory[pointer+2]=word&255,word>>8,0
        items=((254,),(1,254),(255,1,254),(1,254))[style]
        for index,value in enumerate(items):memory[0xA01C+index]=value
        memory[0xA140],memory[0xA141]=0,128 if style==3 else 1
        stack=0x8002 if cases&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':entry,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=NearestMachine(memory.banks,initial);model_entry(model,entry,rows)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(3000):
            if simulator.registers[24]==0xF0F8:break
            simulator.run()
        else:raise AssertionError(('нет общего хвоста',entry,seed))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,hex(entry),model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        for bank,offset,_ in memory.writes:
            if bank not in (2,5):continue
            address=offset+(0x4000 if bank==5 else 0x8000)
            if stack-10<=address<stack:depth=max(depth,stack-address)
        counts[profile]+=1;by_entry[hex(entry)]+=1;paths.update(model.path);cases+=1
        if cases%32768==0:print(str(cases)+' near phase cases passed',flush=True)
    assert cases==75008 and depth==10 and paths['state_06'] and paths['carry_skip_near'] and paths['global_not_small']
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),cases_by_entry=dict(by_entry),paths=dict(paths),
        maximum_additional_stack_bytes=depth,real_search_random_target_and_phase_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        all_stream0_words_at_fold_zero=True,all_global_component_bytes=True,
        common_tail_executed=False,boundary=0xF0F8,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionNearPhaseVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
