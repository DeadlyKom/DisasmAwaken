"""624B, обычный полный индекс, недоступная/ближняя/дальняя цель и настоящая геометрия."""
from collections import Counter
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


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);ratio=bytes(flat[0x9A00:0x9B00]);root=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0
    for linked,mode,r,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        memory.out7ffd(16);ix=0xA100;selected=0xA100+64*linked;stack=0xBFFE
        for base,words in ((ix,(0,0,0)),(selected,(0,0,0) if mode==1 else (2560,4096,65535))):
            if base!=ix and linked>=26:continue
            for axis,word in enumerate(words):memory[base+2*axis],memory[base+2*axis+1]=word&255,word>>8
        if mode==0 and linked<26:memory[selected+1]=128
        memory[ix+8],memory[ix+9],memory[ix+10],memory[ix+11],memory[ix+37]=serial*73&255,serial*109&255,2,linked,(0,1,2,255)[serial%4]
        memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x624B,'SP':stack,'AF':serial&65535,'HL':serial*73&65535,'DE':serial*109&65535,'BC':serial*137&65535,
            '^AF':0xDEF0,'^HL':serial*257&65535,'^DE':serial*379&65535,'^BC':serial*503&65535,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=MotionGateMachine(memory.banks,initial);model.ports=[];model.motion_gate(ratio,root)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0x624B,stop=0x3FFF);memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,linked,mode,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        assert trace.writes==model.ports and memory.o7ffd==16,(serial,'OUT')
        for page,offset,_ in memory.writes:
            if page==2 and stack-24<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
    assert counts.total()==8704 and paths['enter_timed_state'] and paths['ordinary_geometry'] and depth==16,(counts,paths,depth)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),all_256_link_indices=True,
        actual_selected_distance_and_banked_geometry_children_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,real_ports=True,maximum_additional_stack_bytes=depth,
        FF_is_ordinary_index=True,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionLinkedMotionGateVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
