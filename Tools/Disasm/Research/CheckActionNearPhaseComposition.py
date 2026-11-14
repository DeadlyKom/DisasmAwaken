"""F087 и родители до внешнего RET, включая общий вычислитель.

Документация: ../../../Docs/ActionNearPhase.md#полный-внешний-возврат
"""
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


from CheckActionNearPhase import profiles, model_entry
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckScreenUpdate import PortTrace

def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();by_entry=Counter();depth=0
    for entry,seed,rows,globals_,phase,r,code,style,profile,marker in (
        (*item,marker) for item in profiles() for marker in (False,True)):
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
        memory[0xA101]=128 if marker else 1
        for offset,byte in {7:seed&255,9:seed>>8,15:(0,3,127,255)[style],16:phase,36:code*73&255}.items():
            memory[0xA100+offset]=byte
        model=NearestMachine(memory.banks,initial);model_entry(model,entry,rows)
        ix=0xA100
        record={offset:model.read(ix+offset) for offset in (1,7,8,9,10,15,16,18,36)}
        wanted,writes,common_path=prepare_reference(model.r,ix,record)
        def apply(writes):
            for address,byte in writes:
                bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                model.banks[bank][address&0x3FFF]=byte
                model.writes.append((bank,address&0x3FFF,byte))
        apply(writes)
        if wanted[24]==0x6D06:
            result=vector_reference(RecordedBanks(banks=model.banks,out7ffd=16),wanted,
                (record[7],(record[8]+128)&255,record[9]),0x3FFF)
            wanted=result['registers'];apply(result['writes'])
        model.r=wanted;paths['common/'+common_path]+=1
        ports=PortTrace(simulator);simulator.set_tracer(ports)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(3000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет общего хвоста',entry,seed))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,hex(entry),model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        assert not ports.writes and memory.o7ffd==16
        for bank,offset,_ in memory.writes:
            if bank not in (2,5):continue
            address=offset+(0x4000 if bank==5 else 0x8000)
            if stack-10<=address<stack:depth=max(depth,stack-address)
        counts[profile]+=1;by_entry[hex(entry)]+=1;paths.update(model.path);cases+=1
        if cases%32768==0:print(str(cases)+' near phase cases passed',flush=True)
    assert cases==150016 and depth==10 and paths['state_06'] and paths['carry_skip_near'] and paths['global_not_small']
    assert paths['common/marker_return'] and paths['common/preserve'] and paths['common/increment']
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),cases_by_entry=dict(by_entry),paths=dict(paths),
        maximum_additional_stack_bytes=depth,real_search_random_target_and_phase_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        all_stream0_words_at_fold_zero=True,all_global_component_bytes=True,
        common_tail_executed=True,full_external_return=True,boundary=0x3FFF,
        actual_coefficient_and_three_multiply_children=True,active_and_marker_each_profile=True,no_OUT=True,exact_T_claimed=False,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionNearPhaseCompositionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
