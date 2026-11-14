"""F24F, создание записи и общий вычислитель до внешнего RET.

Документация: ../../../Docs/ActionSpawnContinue.md#полный-внешний-возврат
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionSpawnCurrentLink import CurrentLinkMachine
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckScreenUpdate import PortTrace


def main(only_serial=None,links=None):
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0;target_is_child_cases=0
    for linked in (range(256) if links is None else links):
        for reuse in range(256):
            for no_free in (False,True):
                serial=linked*512+reuse*2+int(no_free)
                if only_serial is not None and serial!=only_serial:continue
                memory.recording=False
                for page in (0,2,5):memory.banks[page][:]=baseline[page]
                ix=0xA100+64*(serial%25);slot=(serial//2+1)%25
                if slot==serial%25:slot=(slot+1)%25
                for row in range(25):
                    pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row==slot and not no_free else 1,0
                memory[0xA740],memory[0xA741]=128,128
                for axis,word in enumerate((serial*73&65535,serial*109&65535,serial*137&65535)):
                    memory[ix+2*axis],memory[ix+2*axis+1]=word&255,word>>8
                memory[ix+11],memory[ix+24]=linked,reuse
                stack=0xBFFE;memory[stack],memory[stack+1]=255,63
                initial=get_registers({'PC':0xF24F,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
                for offset,byte in {7:reuse,8:linked,9:(linked+reuse)&255,10:2,15:(0,3,127,255)[reuse&3],16:reuse,18:3 if reuse&16 else 20,36:linked*73&255}.items():
                    memory[ix+offset]=byte
                model=CurrentLinkMachine(memory.banks,initial)
                model.call(0xF255,0xF252,model.spawn_current_link);model.m1(1)
                child_address=model.r[10]*256+model.r[11];child_index=model.r[0]
                creator_writes=list(model.writes)
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
                        (record[7],(record[8]+128)&255,record[9]),0x3FFF,
                        phase_steps=tuple(model.read(a) for a in (0xB04B,0xB056,0xB062)),
                        second_mix='rlc_c_use_e' if (model.read(0xB08B),model.read(0xB08C))==(1,0x6B) else None)
                    wanted=result['registers'];apply(result['writes'])
                model.r=wanted;paths['common/'+common_path]+=1
                ports=PortTrace(simulator);simulator.set_tracer(ports)
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                measured_m1=0
                for _ in range(2000):
                    if simulator.registers[24]==0x3FFF:break
                    old_r=simulator.registers[15]
                    simulator.run()
                    increment=(simulator.registers[15]-old_r)&127
                    assert increment in (1,2),(serial,'неожиданное изменение R',increment)
                    measured_m1+=increment
                else:raise AssertionError(('нет возврата',serial,model.path))
                assert not ports.writes and memory.o7ffd==16
                memory.recording=False;compared=(*range(25),26,27)
                if any(model.r[i]!=simulator.registers[i] for i in compared):
                    diagnostic=dict(full_verification_passed=False,serial=serial,linked=linked,reuse=reuse,no_free=no_free,
                        path=model.path,child_address=child_address,
                        modified_coefficient_code=[dict(address=a,original=flat[a],expected=model.banks[2][a&0x3FFF],actual=memory[a]) for a in range(0xB044,0xB060) if flat[a]!=memory[a]],
                        creator_writes_in_full_coefficient_builder=[dict(address=0x8000+offset,value=value,original=flat[0x8000+offset]) for bank,offset,value in creator_writes if bank==2 and 0xB044<=0x8000+offset<0xB0E9],
                        creator_writes_in_coefficient_code=[dict(address=0x8000+offset,value=value) for bank,offset,value in creator_writes if bank==2 and 0xB044<=0x8000+offset<0xB060],
                        register_differences=[dict(index=i,expected=model.r[i],actual=simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]],
                        assembly_executed=False,native_execution=False)
                    (ROOT/f'Tools/Disasm/Reports/ActionSpawnContinueCodeAliasDiagnostic_{linked}.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
                assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
                assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
                # Проверка полей ребёнка после обратной связи при совпадении цели с выделенной записью.
                if 'class17_created' in model.path:
                    child=child_address
                    same_target=child==0xA100+64*linked
                    assert memory[child+12]==(2 if same_target else 0)
                    assert memory[child+11]==(child_index if same_target else 0)
                    target_is_child_cases+=int(same_target)
                for page,offset,_ in memory.writes:
                    if page==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
                counts['no_free' if no_free else 'allocated']+=1;paths.update(model.path)
                if counts.total()%32768==0:print(str(counts.total())+' current link spawn cases passed',flush=True)
    if only_serial is not None:
        assert counts.total()==1
        result=dict(passed=True,serial=only_serial,full_matrix_passed=False,actual_phase_steps_used=True,
            exact_registers_including_R=True,all_eight_banks_and_write_multiplicity=True,
            full_external_return=True,assembly_executed=False,native_execution=False)
        (ROOT/f'Tools/Disasm/Reports/ActionSpawnContinueTargeted_{only_serial}Verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result));return
    assert counts.total()==(131072 if links is None else 512*len(links)) and depth==8 and target_is_child_cases,(counts,depth,target_is_child_cases)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_link_codes_by_256_ReuseByte_values_by_allocation=(links is None),
        linked_indices=list(range(256) if links is None else links),all_ReuseByte_values_and_both_allocation_outcomes=True,all_25_parent_slots=True,
        actual_ix_index_and_class17_creator_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=depth,
        AF_prime_cleared_before_child=True,phase_scale_class_profiles_correlated_with_link_and_reuse=True,complete_input_product_exhausted=False,
        full_M1_count_compared_not_only_R_modulo_128=False,
        full_external_return=True,common_tail_executed=True,no_OUT=True,exact_T_claimed=False,target_is_child_cases=target_is_child_cases,
        self_target_final_LinkFlags_2_and_LinkedIndex_child=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/('Tools/Disasm/Reports/ActionSpawnContinueCompositionVerification.json' if links is None else 'Tools/Disasm/Reports/ActionSpawnContinueStableTargetsVerification.json')
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
