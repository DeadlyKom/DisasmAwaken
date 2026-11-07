"""State0A, реальные большие эффекты и полный внешний RET, отдельные игровые и эффектные списки."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckEffects import memory_image
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionClass17Sweep import SweepMachine


def profiles():
    for phase in range(256):
        for matched in range(3):
            for candidates in range(5):
                for free in range(9):yield phase,matched,candidates,free,phase,phase&1,phase&255,'all_phase_and_list_styles'
    for old in range(256):
        for mode in (0,1):
            for matched in (0,1):yield 1,matched,0,8,old,mode,old,'all_delta_state_bytes'
    for mode in range(256):
        for old in (0,31,32,127,128):
            for matched in (0,1):yield 1,matched,0,8,old,mode,mode,'all_mode_bytes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[3]=bytearray(memory_image()[0xC000:]);objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();banks[4][:len(objects)]=objects
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();depth=0;max_effects=0
    for phase,matched,candidates,free,old,mode,r,profile in profiles():
        memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        memory.out7ffd(16)
        link=(0,26,255)[(matched+candidates+free)%3] if profile=='all_phase_and_list_styles' else 26
        for row in range(25):
            address=0xA100+64*row
            for axis,value in enumerate((0x1234+row,0x2345+row,0x3456+row)):memory[address+2*axis],memory[address+2*axis+1]=value&255,value>>8
            memory[address+18],memory[address+13],memory[address+15],memory[address+6]=0,link,23,(row*2)&255
        for row in range(candidates):
            memory[0xA112+64*row]=17;memory[0xA10F+64*row]=22 if cases%3==0 else 23
        for row in range(10,10+matched):
            memory[0xA112+64*row],memory[0xA10A+64*row],memory[0xA10B+64*row]=3,2,link
        if cases&1:memory[0xA300],memory[0xA301]=0,128
        memory[0xA6D2]=18;memory[0xA740],memory[0xA741]=128,128
        for row in range(8):memory[0xA79C+18*row]=0 if row==free else 1
        memory[0xA82C]=128;memory[0xF49D]=phase
        memory[0x9B83],memory[0x9BCD]=mode,old;memory[0x6D3D]=old
        ix=0xA700;memory[ix+10]=10;memory[ix+18]=17 if cases%7==0 else 8
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF49C,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(cases*73)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        model=SweepMachine(memory.banks,initial);model.ports=[];model.sweep(memory.roms[1])
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(6000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет внешнего RET',phase,matched,candidates,free))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,profile,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM')
        assert trace.writes==model.ports and memory.o7ffd==16
        for bank,pos,_ in memory.writes:
            if bank==2 and stack-24<=pos+0x8000<stack:depth=max(depth,stack-pos-0x8000)
        max_effects=max(max_effects,model.path.count('class17_effect'));counts[profile]+=1;paths.update(model.path);cases+=1
        if cases%16384==0:print(str(cases)+' class17 sweep cases passed',flush=True)
    assert cases==38144 and depth==18 and max_effects==3
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),maximum_additional_stack_bytes=depth,
        maximum_effect_calls_per_sweep=max_effects,all_phase_bytes=True,all_old_delta_state_and_mode_bytes=True,
        real_large_effect_bank3_count_delta_and_reset_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        real_ports_compared=True,complete_external_return=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass17SweepVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
