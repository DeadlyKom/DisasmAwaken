"""E91E, допуск R, класса и списка, выбор цели либо реальный хвост E935."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionCandidateEligibility import CLASSES
from CheckActionPhaseTransition import transition
from CheckActionNearestCandidate import NearestMachine
from CheckActionRecordSearch import inc_flags
from ReferenceControlsPointRespawn import cp_flags


def class_gate(model):
    pointer=model.r[8]*256+model.r[9];code=model.read(pointer+18)
    compared=CLASSES.index(code)+1 if code in CLASSES else len(CLASSES)
    model.r[0:2]=[code,cp_flags(code,CLASSES[compared-1])]
    return model.finish(2+2*compared)


def ready(model):
    model.call(0xEA00,0xEA18,lambda:class_gate(model));model.m1(1)
    if not model.r[1]&64:model.r[0:2]=[0,0x44];return model.finish(2)
    cursor=0xA01C;model.m1(1)
    while model.read(cursor)==255:cursor+=1;model.m1(6)
    value=model.read(cursor);model.pair(6,cursor)
    model.r[0:2]=[254,cp_flags(254,254)] if value==254 else [value+1,inc_flags(value,1)]
    return model.finish(4 if value==254 else 7)


def run_model(model):
    model.m1(2);value=model.r[15];model.r[0:2]=[value,cp_flags(value,100)];model.m1(2)
    if value<100:model.path.append('low_R_phase');return transition(model)
    model.call(0xEA15,0xE927,lambda:ready(model));model.m1(1)
    if model.r[1]&64:model.path.append('gate_Z_phase');return transition(model)
    model.call(0xE9C2,0xE92C,model.nearest)
    pointer=model.r[8]*256+model.r[9];model.put(pointer+10,14);model.put(pointer+11,model.r[0])
    model.r[1]=0x41|(model.r[0]&0x28);model.path.append('linked_state_0E')
    return model.finish(6)


def profiles():
    for r in range(256):
        for code in range(256):yield r,code,(r*73+code)&255,(r+code)%6,'all_R_and_classes'
    for code in CLASSES:
        for old in range(256):yield 128,code,old,3,'all_stale_results'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();stale=0
    for r,code,old,style,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for index,values in enumerate(((0,0,0),(511,256,0),(256,0,65535))):
            pointer=0xA100+64*index
            for axis,value in enumerate(values):memory[pointer+2*axis],memory[pointer+2*axis+1]=value&255,value>>8
        if style==3:memory[0xA141]=128
        items=((254,),(1,254),(255,2,1,254),(1,254),(255,255,254),(253,254))[style]
        for index,value in enumerate(items):memory[0xA01C+index]=value
        memory[0xA112],memory[0xA10A],memory[0xA10B]=code,(cases*37)&255,old^255
        for offset in (27,29,31):memory[0xA100+offset]=0 if cases&1 else (r*17+code)&255
        word=(r*257+code*137)&65535
        memory[0xEC05],memory[0xEC06],memory[0xEC07]=word&255,word>>8,code
        memory[0xE9FE]=old;stack=0x8002 if cases&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xE91E,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=NearestMachine(memory.banks,initial);run_model(model)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(3000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',r,code,style))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        if profile=='all_stale_results':
            assert memory[0xA10A]==14 and memory[0xA10B]==old and memory[0xE9E7]==255
            stale+=1
        counts[profile]+=1;paths.update(model.path);cases+=1
        if cases%32768==0:print(str(cases)+' target transition cases passed',flush=True)
    assert cases==67072 and stale==1536
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),stale_result_link_cases=stale,
        all_256_initial_R_by_256_classes=True,all_256_old_results_for_each_allowed_class=True,
        actual_gate_nearest_distance_and_phase_children_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=8,
        carry_not_equivalent_to_found_candidate=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionTargetTransitionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
