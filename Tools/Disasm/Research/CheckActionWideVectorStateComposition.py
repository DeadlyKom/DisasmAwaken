"""State01 до внешнего RET, банковая геометрия и полный вычислитель.

Документация: ../../../Docs/ActionWideVectorState.md#полный-внешний-возврат
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionFoldedRandom import step
from ReferenceActionRecordFilters import STREAM_POINTERS
from ReferenceActionWideVectorState import WideVectorMachine
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference


def profiles():
    for r in range(256):
        for code in range(256):yield (r+code)&255,r,code,1,0,(r+code)%4,'all_R_and_classes'
    for index in range(256):
        for mode in (0,1,128,255):
            for kind in range(4):yield index,index*73&255,1,mode,kind,kind,'all_indices_modes_random_branches'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);ratio=bytes(flat[0x9A00:0x9B00]);root=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks]
    simulator=Simulator(memory);paths=Counter();counts=Counter();depth=0
    seeds={}
    for seed in range(65536):
        word=step(seed,0)['word'];kind=0 if word>>8!=65 else 1 if word&255<90 else 2
        seeds.setdefault(kind,seed)
    assert len(seeds)==3
    for index,r,code,mode,kind,style,profile in profiles():
        memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        memory.out7ffd(16);ix=0xA100;pointer=0x9B27+12*index;stack=0xBFFE
        for axis,value in enumerate((0x12345678,0xFFFF8001,0x00800000)):
            for offset in range(4):memory[pointer+4*axis+offset]=(value>>(8*offset))&255
        for axis,value in enumerate((0x1357,0x2468,0x369C)):
            memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
        memory[ix+8],memory[ix+9],memory[ix+10]=r*73&255,r*109&255,1
        memory[ix+18],memory[ix+37],memory[ix+38]=code,(0,1,2,255)[style],index
        memory[ix+27],memory[ix+29],memory[ix+31]=(0,0,0) if kind==3 else (128,0,0)
        memory[0x9B83]=mode
        for number,seed in ((2,seeds[min(kind,2)]),(5,0x1357)):
            address=STREAM_POINTERS[number];memory[address],memory[address+1],memory[address+2]=seed&255,seed>>8,0
        memory[0xA01C]=254;memory[0xE9FE]=r^255
        memory[stack],memory[stack+1]=255,63
        serial=counts.total();initial=get_registers({'PC':0xF0BE,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=WideVectorMachine(memory.banks,initial);model.wide_state(ratio,root)
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
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(6000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет общего хвоста',index,r,code,kind))
        memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,index,r,code,kind,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        assert trace.writes==model.ports and memory.o7ffd==16,(serial,'OUT')
        for page,offset,_ in memory.writes:
            if page==2 and stack-24<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        paths.update(model.path);counts[profile]+=1
        if counts.total()%16384==0:print(str(counts.total())+' State01 cases passed',flush=True)
    required=('transition_carry','zero_mode','zero_class','class_ge_5','random_high_reject','random_low_reject','state_0C')
    assert all(paths[p] for p in required),(paths,required)
    assert counts.total()==69632 and depth==18,(counts,depth)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_initial_R_by_all_classes=True,all_256_vector_indices=True,index_FF_runs_256_additions=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        actual_wide_geometry_root_ratio_step_and_random_children_executed=True,real_ports=True,
        maximum_additional_stack_bytes=depth,final_7ffd=16,common_F0F8_executed=True,full_external_return=True,actual_coefficient_and_three_multiply_children=True,exact_T_claimed=False,
        all_candidate_lists_exhausted=False,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionWideVectorStateCompositionVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
