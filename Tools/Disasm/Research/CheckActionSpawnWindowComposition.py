"""F222 до внешнего RET, допуски создания и полный вычислитель.

Документация: ../../../Docs/ActionSpawnWindow.md#полный-внешний-возврат
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionSpawnWindow import SpawnWindowMachine


from CheckActionSpawnWindow import profiles
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckScreenUpdate import PortTrace

def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0
    for a,high,code,counter,profile,marker in ((*item,marker) for item in profiles() for marker in (False,True)):
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for row in range(25):
            pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row==1 and not (serial>>1)&1 else 1,0
        ix=0xA100;memory[0xA740],memory[0xA741]=128,128
        memory[ix+11],memory[ix+18],memory[ix+20],memory[ix+24]=2,code,counter,serial&8
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF222,'SP':stack,'AF':a*256+(serial&255),'HL':high*256+0xF0,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        memory[ix+1]=128 if marker else 1
        for offset,byte in {7:a,8:high,9:code,10:2,15:(0,3,127,255)[a&3],16:a,36:code*73&255}.items():
            memory[ix+offset]=byte
        model=SpawnWindowMachine(memory.banks,initial);model.spawn_window()
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
        for _ in range(2500):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет общего хвоста',serial,model.path))
        memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        assert not ports.writes and memory.o7ffd==16
        for page,offset,_ in memory.writes:
            if page==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
    assert counts.total()==262144 and depth==8,(counts,depth)
    assert paths['class17_no_slot'] and paths['class17_created']
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_A_by_256_H=True,all_256_classes_by_256_class17_delay=True,full_class_table_index_not_clamped=True,
        actual_current_link_and_class17_children_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=depth,
        common_F0F8_executed=True,full_external_return=True,active_and_marker_each_profile=True,
        initial_LinkedIndex=2,correlated_phase_scale_profiles=True,no_OUT=True,exact_T_claimed=False,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionSpawnWindowCompositionVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
