"""624B, обычный полный индекс, недоступная/ближняя/дальняя цель и настоящая геометрия."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionLinkedMotionGate import MotionGateMachine


def profiles():
    for linked in range(256):
        for mode in range(3):
            for r in (0,1,127,128,254,255):yield linked,mode,r,'all_indices_modes_R_edges'
    randomizer=random.Random(0x624B)
    for _ in range(4096):yield randomizer.randrange(256),randomizer.randrange(3),randomizer.randrange(256),'mixed_arguments'
    # Проверка ближней ветви со всеми знаками и порядками ненулевых старших байтов модулей.
    for magnitudes in product((1,255,256,511,2304,2559),repeat=3):
        for signs in product((1,-1),repeat=3):
            words=tuple((value*sign)&65535 for value,sign in zip(magnitudes,signs))
            for r in (0,255):yield 1,words,r,'near_signs_and_order'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);ratio=bytes(flat[0x9A00:0x9B00]);root=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0;refresh_by_path={};timer_reads=0
    for linked,mode,r,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        memory.out7ffd(16);ix=0xA100;selected=0xA100+64*linked;stack=0xBFFE
        selected_words=mode if isinstance(mode,tuple) else (0,0,0) if mode==1 else (2560,4096,65535)
        for base,words in ((ix,(0,0,0)),(selected,selected_words)):
            if base!=ix and linked>=26:continue
            for axis,word in enumerate(words):memory[base+2*axis],memory[base+2*axis+1]=word&255,word>>8
        if mode==0 and linked<26:memory[selected+1]=128
        memory[ix+8],memory[ix+9],memory[ix+10],memory[ix+11],memory[ix+37]=serial*73&255,serial*109&255,2,linked,(0,1,2,255)[serial%4]
        memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x624B,'SP':stack,'AF':serial&65535,'HL':serial*73&65535,'DE':serial*109&65535,'BC':serial*137&65535,
            '^AF':0xDEF0,'^HL':serial*257&65535,'^DE':serial*379&65535,'^BC':serial*503&65535,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=MotionGateMachine(memory.banks,initial);model.ports=[];model.motion_gate(ratio,root)
        if profile=='near_signs_and_order':assert 'enter_timed_state' in model.path
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        measured_m1=0
        # Проверка полного приращения M1, не только совпадения младших семи битов R.
        for _ in range(20000):
            if simulator.registers[24]==0x3FFF:break
            pc=simulator.registers[24]
            previous_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-previous_r)&127
            assert increment in (1,2),(serial,'неожиданное изменение R',increment)
            measured_m1+=increment
            # Проверка момента аппаратного чтения R, определяющего таймер ближнего пути.
            if pc==0x62BE:
                assert measured_m1==model.timer_read_m1
                assert simulator.registers[0]==simulator.registers[15]
                timer_reads+=1
        else:raise AssertionError(('нет возврата',serial))
        assert measured_m1==model.total_refresh_m1,(serial,'M1',measured_m1,model.total_refresh_m1)
        path_kind='timed' if 'enter_timed_state' in model.path else 'geometry'
        bounds=refresh_by_path.setdefault(path_kind,[measured_m1,measured_m1])
        bounds[:]=[min(bounds[0],measured_m1),max(bounds[1],measured_m1)]
        memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,linked,mode,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        assert trace.writes==model.ports and memory.o7ffd==16,(serial,'OUT')
        for page,offset,_ in memory.writes:
            if page==2 and stack-24<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
    assert counts.total()==12160 and counts['near_signs_and_order']==3456 and paths['enter_timed_state'] and paths['ordinary_geometry'] and depth==16,(counts,paths,depth)
    assert timer_reads==paths['enter_timed_state']
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),all_256_link_indices=True,
        actual_selected_distance_and_banked_geometry_children_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,real_ports=True,maximum_additional_stack_bytes=depth,
        full_M1_count_compared_not_only_R_modulo_128=True,observed_M1_bounds_by_path=refresh_by_path,
        actual_timer_R_read_M1_compared=True,timer_R_reads=timer_reads,
        FF_is_ordinary_index=True,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionLinkedMotionGateVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
