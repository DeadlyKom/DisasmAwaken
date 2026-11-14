"""60E8, все пары B/C и режимы выделения, реальные исходные команды и связывание."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionClass17Spawn import Class17Machine


def profiles():
    for bc in range(65536):yield bc,bc&255,bc*109&65535,bc%25,False,'all_BC_pairs'
    for a in range(256):
        for mode in range(4):yield 0x071A,a,a*257,mode,mode==3,'parameter_and_allocation_modes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0;target_is_child_cases=0
    for bc,a,alternate,slot,no_free,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for row in range(25):
            pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row>=slot and not no_free else 1,255 if row==slot and slot==2 else 0
        memory[0xA740],memory[0xA741]=128,128
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x60E8,'SP':stack,'AF':a*256+(serial&255),'HL':0x1357,'DE':0x2468,'BC':bc,
            '^AF':alternate,'^HL':serial*73&65535,'^DE':serial*109&65535,'^BC':serial*137&65535,'IX':0xA600,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=Class17Machine(memory.banks,initial);model.class17_spawn()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        measured_m1=0
        for _ in range(2000):
            if simulator.registers[24]==0x3FFF:break
            old_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-old_r)&127
            assert increment in (1,2),(serial,'неожиданное изменение R',increment)
            measured_m1+=increment
        else:raise AssertionError(('нет возврата',serial,bc,model.path))
        assert measured_m1==model.m1_count,(serial,'M1',measured_m1,model.m1_count)
        memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,bc,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        # Проверка окончательных полей после обратной связи, цель может совпасть с новым ребёнком.
        if 'class17_created' in model.path:
            child=256*simulator.registers[10]+simulator.registers[11]
            same_target=child==0xA100+64*(bc&255)
            assert memory[child+12]==(2 if same_target else 0)
            assert memory[child+11]==(simulator.registers[0] if same_target else 0)
            assert simulator.registers[1]==(0x45|(simulator.registers[0]&0x28))
            target_is_child_cases+=int(same_target)
        for page,offset,_ in memory.writes:
            if page==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
        if counts.total()%32768==0:print(str(counts.total())+' class17 spawn cases passed',flush=True)
    assert counts.total()==66560 and depth==6 and target_is_child_cases,(counts,depth,target_is_child_cases)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_B_C_index_pairs=True,all_256_initial_parameters=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=depth,
        actual_reusable_index_address_and_index_children_executed=True,uninitialized_child_fields_preserved=True,
        full_M1_count_compared_not_only_R_modulo_128=True,
        target_is_child_cases=target_is_child_cases,self_target_final_LinkFlags_2_and_LinkedIndex_child=True,
        successful_aligned_child_F_45_or_index_28=True,
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionClass17SpawnVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
