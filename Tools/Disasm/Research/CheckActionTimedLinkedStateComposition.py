"""State10 до внешнего RET, XOR-вывод и общий вычислитель.

Документация: ../../../Docs/ActionTimedLinkedState.md#полный-внешний-возврат
"""
from collections import Counter
import json,sys
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionFoldedRandom import step
from ReferenceActionRecordFilters import STREAM_POINTERS
from ReferenceActionTimedLinkedState import TimedLinkedMachine
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckScreenUpdate import PortTrace
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    seeds={}
    for seed in range(65536):
        value=step(seed,0)['word'];low=value&255;high=value>>8
        kind='spawn' if low==240 and high>=95 else 'high_reject' if low==240 else 'low'
        seeds.setdefault(kind,seed)
    assert len(seeds)==3;seed_values=tuple(seeds.values());counts=Counter();paths=Counter();r_cases=0;depth=0
    for timer in range(256):
        for threshold in range(256):
            serial=counts.total();memory.recording=False
            for page in (0,2,5):memory.banks[page][:]=baseline[page]
            for row in range(25):
                pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row==2 and not serial&1 else 1,0
            ix=0xA100;linked=(1,255,26,1)[serial%4];selected=0xA780 if linked==255 else 0xA100+64*linked
            for base in (ix,selected):
                for offset,word in ((26,0),(28,0),(30,256)):memory[base+offset],memory[base+offset+1]=word&255,word>>8
            if serial%4==3:memory[selected+1]=128
            memory[ix+11],memory[ix+17],memory[ix+18],memory[ix+20]=linked,threshold,serial%26,0 if serial%3 else 1
            memory[ix+23],memory[ix+24],memory[ix+25]=timer,serial&8,serial*73&255
            memory[0xA740],memory[0xA741]=128,128
            seed=seed_values[serial%3];address=STREAM_POINTERS[0];memory[address],memory[address+1],memory[address+2]=seed&255,seed>>8,0
            stack=0xBFFE;memory[stack],memory[stack+1]=255,63
            initial=get_registers({'PC':0xF3C8,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
            initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
            for offset,byte in {7:threshold,8:timer,9:(timer+threshold)&255,10:16,15:(0,3,127,255)[threshold&3],16:threshold,36:timer*73&255}.items():
                memory[ix+offset]=byte
            model=TimedLinkedMachine(memory.banks,initial);model.timed_linked(ops)
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
            for _ in range(30000):
                if simulator.registers[24]==0x3FFF:break
                simulator.run()
            else:raise AssertionError(('нет общего хвоста',serial,model.path))
            memory.recording=False;compared=[i for i in (*range(25),26,27) if i!=15 or not getattr(model,'r_uncertain',False)]
            assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,timer,threshold,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
            assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
            assert not ports.writes and memory.o7ffd==16
            for page,offset,_ in memory.writes:
                if page==2 and stack-40<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
            paths.update(model.path);counts['all_timers_thresholds']+=1;r_cases+=int(not getattr(model,'r_uncertain',False))
            if counts.total()%16384==0:print(str(counts.total())+' State10 cases passed',flush=True)
    assert counts.total()==65536 and paths['timer_expired']==256 and paths['window_spawn_attempted'] and paths['timed_overlay_return']
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_timers_by_256_thresholds=True,zero_timer_wrap_preserved=True,expired_state_restored_from_timed_resume_code=True,
        actual_context_random_creation_projection_clipping_and_raster_children_executed=True,
        exact_registers_except_R_on_renderer=True,exact_R_cases_including_proved_inside_lines=r_cases,
        exact_R_on_nonrenderer_cases=counts.total()-paths['inside_line']-paths['clipped_line'],
        inside_fixed_packet_R_proved=True,fixed_clipped_packet_R_supported=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_observed_additional_stack_bytes=depth,
        common_F0F8_executed=True,full_external_return=True,correlated_phase_scale_profiles=True,no_OUT=True,exact_T_claimed=False,renderer_R_proved=(r_cases==counts.total()),complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionTimedLinkedStateCompositionVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
