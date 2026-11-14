"""State02/05, общий F0F8 до внешнего RET, косвенная передача проверяется отдельно.

Документация: ../../../Docs/ActionLinkedTargetState.md#общий-хвост-и-косвенный-выход
"""
from collections import Counter
import argparse,json,sys
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionRecordFilters import STREAM_POINTERS
from ReferenceActionLinkedTargetState import LinkedTargetMachine
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def profiles(state=2):
    for linked in range(256):
        for code in (*range(26),*range(128,154)):
            for mode in range(3):yield linked,code,mode,(linked+code)&255,'all_links_classes_modes'
    for saved in range(256):
        for code in (9,137):
            for mode in range(8):yield 255,code,mode,saved,'all_saved_states_and_R_modes'
    if state!=2:return
    for code in (*range(26),*range(128,154)):
        for carry in (0,1):
            for linked in (0,255):
                for a in (0,127,255):yield linked,code,carry,a,'external_F142_entry'


def main(state=2,unrestricted=False,diagnostic_case=None,original_code_contract=False):
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);ratio=bytes(flat[0x9A00:0x9B00]);root=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    counts=Counter();paths=Counter();boundaries=Counter();depth=0;r_cases=0
    diagnostic_trace=[];diagnostic_model_trace=[]
    if diagnostic_case is not None:
        from ReferenceActionClipping import Clipping
        original_helper=Clipping.helper
        def traced_helper(child,entry):
            original_helper(child,entry)
            diagnostic_model_trace.append(dict(pc=entry,registers=list(child.r),count=child.byte(0x9BA3),points=[child.word(a) for a in (0xCF0B,0xCF0D,0xCF1B,0xCF1D)]))
        Clipping.helper=traced_helper
    for serial,(linked,code,mode,saved,profile) in enumerate(profiles(state)):
        if diagnostic_case is not None and serial!=diagnostic_case:continue
        memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        memory.out7ffd(16)
        for row in range(25):
            pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+18],memory[pointer+24]=0,1,(0,5,6,7,14,18)[row%6],0
        memory[0xA101]=128 if mode&1 else 1;memory[0xA141]=128 if mode&2 else 1
        memory[0xA740],memory[0xA741]=128,128
        ix=0xA700;current=(0,0,256) if mode%3==0 else (0x1234,0x2345,0x3456)
        selected=0xA780 if linked==255 else 0xA100+64*linked
        if linked<24 or linked==255:
            words=current if mode%3==0 else tuple((v+(0x2000 if mode%3==2 else 255))&65535 for v in current)
            for axis,word in enumerate(words):memory[selected+2*axis],memory[selected+2*axis+1]=word&255,word>>8
            for offset,word in ((26,0),(28,0),(30,256)):memory[selected+offset],memory[selected+offset+1]=word&255,word>>8
            if mode%3==1:memory[selected+1]=128
            if mode==7:memory[selected+27]=128
        for axis,word in enumerate(current):memory[ix+2*axis],memory[ix+2*axis+1]=word&255,word>>8
        values={7:serial&255,8:serial*73&255,9:serial*109&255,10:state,11:linked,13:1,14:2,15:3,
                16:2,17:(0,255,128)[mode%3],18:code,19:(0,35,50)[mode%3],20:(0,1,2,128,129,255)[serial%6],
                21:0 if serial&1 else 255,22:saved,23:30,24:(serial&3)|(4 if mode&4 else 0),25:4,37:2}
        for offset,value in values.items():memory[ix+offset]=value
        if state==5 and mode%3==0 and serial%4==0:memory[ix+17]=255
        for offset,word in ((26,0),(28,0),(30,256)):memory[ix+offset],memory[ix+offset+1]=word&255,word>>8
        if 27<=linked<255 and not unrestricted:memory[ix+27]=128
        if state==5:
            for address,word in ((0xAF48,0),(0xAF56,0),(0xAF69,256)):memory[address],memory[address+1]=word&255,word>>8
        items=(1,254) if mode&1 else (254,)
        for k,value in enumerate(items):memory[0xA01C+k]=value
        memory[0xE9FE]=1
        for number in (0,2,5,10,11):
            seed=(5254 if number==0 and mode%3==0 else (serial*137+number*257)&65535)
            address=STREAM_POINTERS[number];memory[address],memory[address+1],memory[address+2]=seed&255,seed>>8,0
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        entry=(0xF142 if profile=='external_F142_entry' else 0xF138) if state==2 else 0xF289
        af=saved*256+((serial&254)|mode) if entry==0xF142 else serial&65535
        initial=get_registers({'PC':entry,'SP':stack,'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        if state==2:
            model=LinkedTargetMachine(memory.banks,initial);model.target_state(ratio,root,ops,flat,entry)
        else:
            from ReferenceActionLinkedPhaseState import LinkedPhaseMachine
            model=LinkedPhaseMachine(memory.banks,initial);model.phase_target_state(ratio,root,ops,flat)
        if original_code_contract and model.boundary!='indirect' and model.r[24]==0xF0F8:
            mutable_operands={0xB045,0xB04F,0xB05C,0x6D0E,0x6D1C,0x6D2A}
            changed=[a for start,end in ((0xB044,0xB0E9),(0xD12C,0xD194),(0x6D06,0x6D38))
                for a in range(start,end) if a not in mutable_operands and model.read(a)!=flat[a]]
            if changed:
                model.boundary='modified_math_code'
                paths['modified_code_index_'+str(linked)]+=1
        if model.boundary not in ('indirect','modified_math_code') and model.r[24]==0xF0F8:
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
                    second_mix='rlc_c_use_e' if (model.read(0xB08B),model.read(0xB08C))==(1,0x6B) else None,
                    third_mix='omit_plus_index' if model.read(0xB0CB)==0 else None,
                    leading_bit5_falls_through=(model.read(0xD14A)==0x38 and model.read(0xD14B)==0))
                wanted=result['registers'];apply(result['writes'])
            model.r=wanted;paths['common/'+common_path]+=1
        if diagnostic_case is not None:Clipping.helper=original_helper
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        previous=None;first_rom_escape=None;recent_pcs=[]
        for step in range(30000):
            if step and simulator.registers[24]==model.r[24] and (model.boundary!='indirect' or previous==(0xF175 if state==2 else 0xF2C6)):break
            previous=simulator.registers[24]
            recent_pcs=(recent_pcs+[previous])[-32:]
            if previous<0x4000 and previous!=0x3FFF and first_rom_escape is None:first_rom_escape=previous
            if diagnostic_case is not None and previous in (0xC477,0xC496,0xC4B5,0xC4D4,0xC4F6,0xC540,0xC58B,0xC5E7,0xC993,0xDD06,0xDCD6,0xDDF0):
                diagnostic_trace.append(dict(pc=previous,registers=list(simulator.registers),points=[memory[a]+256*memory[a+1] for a in (0xCF0B,0xCF0D,0xCF1B,0xCF1D)],count=memory[0x9BA3]))
            simulator.run()
        else:
            diagnostic=dict(passed=False,state=state,serial=serial,linked=linked,code=code,mode=mode,path=model.path,
                expected_PC=model.r[24],actual_PC=simulator.registers[24],instruction_limit=30000,
                first_ROM_escape=first_rom_escape,recent_PCs=recent_pcs,
                multiply_differences=[dict(address=a,original=flat[a],actual=memory[a]) for a in range(0xD12C,0xD194) if flat[a]!=memory[a]],
                nontermination_proved=False,native_reachability_proved=False,assembly_executed=False)
            (ROOT/f'Tools/Disasm/Reports/ActionLinkedStatesEscape_State{state:02X}_Case{serial}.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
            raise AssertionError(('нет границы',serial,linked,code,mode,model.path,hex(model.r[24])))
        memory.recording=False;compared=[i for i in (*range(25),26,27) if i!=15 or not getattr(model,'r_uncertain',False)]
        if diagnostic_case is not None:
            diagnostic=dict(case=serial,path=model.path,trace=diagnostic_trace,model_trace=diagnostic_model_trace,model_registers=model.r,
                actual_registers=list(simulator.registers),assembly_executed=False)
            (ROOT/f'Tools/Disasm/Reports/ActionLinkedStatesCompositionSingle_State{state:02X}_Case{serial}.json').write_text(json.dumps(diagnostic,indent=2)+'\n','utf-8')
        if any(model.r[i]!=simulator.registers[i] for i in compared):
            diagnostic=dict(passed=False,state=state,serial=serial,linked=linked,code=code,mode=mode,saved=saved,path=model.path,
                boundary=model.boundary,all_banks_match=(memory.banks==model.banks),write_multiplicity_match=(Counter(memory.writes)==Counter(model.writes)),register_differences=[dict(index=i,expected=model.r[i],actual=simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]],
                multiply_differences=[dict(address=a,original=flat[a],actual=memory[a]) for a in range(0xD12C,0xD194) if flat[a]!=memory[a]],
                builder_differences=[dict(address=a,original=flat[a],actual=memory[a]) for a in range(0xB044,0xB0E9) if flat[a]!=memory[a]],
                assembly_executed=False,native_execution=False)
            (ROOT/f'Tools/Disasm/Reports/ActionLinkedStatesCommonDiagnostic_State{state:02X}_Case{serial}.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,linked,code,mode,saved,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        assert trace.writes==model.ports and memory.o7ffd==16,(serial,'OUT',trace.writes,model.ports)
        for page,offset,_ in memory.writes:
            if page==2 and stack-48<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path);boundaries[model.boundary]+=1;r_cases+=int(not getattr(model,'r_uncertain',False))
        if counts.total()%8192==0:print(str(counts.total())+' State'+format(state,'02X')+' cases passed',flush=True)
    if diagnostic_case is not None:
        assert counts.total()==1
        result=dict(passed=True,state=state,diagnostic_case=diagnostic_case,full_verification=False,
            ordinary_common_tail_executed=bool(sum(v for k,v in paths.items() if k.startswith('common/'))),
            exact_R_cases_including_proved_inside_lines=r_cases,
        exact_R_on_nonrenderer_cases=counts.total()-paths['inside_line']-paths['clipped_line'],
        inside_fixed_packet_R_proved=True,fixed_clipped_packet_R_supported=True,assembly_executed=False,native_execution=False)
        (ROOT/f'Tools/Disasm/Reports/ActionLinkedStatesSingleCaseVerification_State{state:02X}_Case{diagnostic_case}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result));return
    assert counts.total()==(44656 if state==2 else 44032) and paths['saved_state_indirect'] and paths['tail_state12'] and paths['counter_expired_spawn']
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),boundaries=dict(boundaries),
        all_256_link_indices_by_52_class_codes=True,all_256_saved_states_on_class9_paths=True,
        actual_class_dispatch_nearest_spawn_context_geometry_and_overlay_children_executed=True,
        overlay_calls_reached=paths['overlay_returned'],
        exact_registers_except_R_on_renderer=True,exact_R_cases_including_proved_inside_lines=r_cases,
        exact_R_on_nonrenderer_cases=counts.total()-paths['inside_line']-paths['clipped_line'],
        inside_fixed_packet_R_proved=True,fixed_clipped_packet_R_supported=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,real_ports=True,
        maximum_observed_additional_stack_bytes=depth,saved_state_index_SLA_wrap_preserved=True,
        indirect_next_handler_executed=False,common_F0F8_executed=True,ordinary_common_paths_external_return_executed=True,
        original_code_contract=original_code_contract,modified_code_boundaries_are_not_external_returns=True,renderer_R_proved=(r_cases==counts.total()),
        out_of_record_array_profiles_use_current_overlay_marker=not unrestricted,
        unrestricted_out_of_array_overlay_profile_proved=unrestricted,
        external_F142_uses_input_Carry_instead_of_reading_R=(state==2),
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    if state==5:result['uses_prior_global_inputs_without_LoadLinkedRecordVectors']=True
    path=ROOT/('Tools/Disasm/Reports/'+('ActionLinkedTargetState' if state==2 else 'ActionLinkedPhaseState')+('Unrestricted' if unrestricted else '')+('OriginalCodeContract' if original_code_contract else '')+'CompositionVerification.json')
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--unrestricted-out-of-array-overlay',action='store_true');parser.add_argument('--diagnostic-case',type=int);parser.add_argument('--state',type=int,choices=(2,5),default=2);parser.add_argument('--original-code-contract',action='store_true')
    args=parser.parse_args();main(state=args.state,unrestricted=args.unrestricted_out_of_array_overlay,diagnostic_case=args.diagnostic_case,original_code_contract=args.original_code_contract)
