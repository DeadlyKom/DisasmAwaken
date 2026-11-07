"""EA29, классы 0..15, все R, разные игровые слоты и эффектные записи, настоящие четыре OUT."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckEffects import memory_image
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLargeClassEffect import LargeClassMachine


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[3]=bytearray(memory_image()[0xC000:]);objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();banks[4][:len(objects)]=objects
    rom=bytes((i*71+39+(i>>8)*13)&255 for i in range(0x4000));memory=RecordedBanks(banks=banks,out7ffd=16);memory.roms=(memory.roms[0],rom)
    baseline=[bytearray(b) for b in banks];simulator=Simulator(memory);cases=0;paths=Counter();depth=0;samples=set()
    for cls in range(16):
        for r in range(256):
            for available in (0,1,3,6):
                memory.recording=False
                for page in range(8):memory.banks[page][:]=baseline[page]
                memory.out7ffd(16);ix=0xA700;stack=0xBFFE
                for row in range(25):
                    pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row<available else 1,255
                memory[0xA740],memory[0xA741]=128,128
                for axis,word in enumerate((0x1234,r*257,0xFFFF)):memory[ix+2*axis],memory[ix+2*axis+1]=word&255,word>>8
                memory[ix+6],memory[ix+18],memory[ix+24]=(0,2,136,254)[r%4],cls,cases&255
                memory[0x6D3D]=r*73&255
                for row in range(8):memory[0xA79C+18*row]=0 if row==r%9 else 1
                memory[0xA82C]=128;memory[stack],memory[stack+1]=255,63
                initial=get_registers({'PC':0xEA29,'SP':stack,'AF':cases*109&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':cases*73&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
                model=LargeClassMachine(memory.banks,initial);model.large_class_effect(rom)
                simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
                simulator.run(start=0xEA29,stop=0x3FFF);memory.recording=False;compared=(*range(25),26,27)
                assert all(model.r[i]==simulator.registers[i] for i in compared),(cases,cls,r,available,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
                assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
                assert trace.writes==model.ports and memory.o7ffd==16,(cases,'OUT')
                for page,offset,_ in memory.writes:
                    if page==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
                paths.update(model.path);cases+=1
                samples.update(getattr(model,'rom_samples',[]))
    assert cases==16384 and depth==8 and all(paths['children_requested_'+str(n)] for n in range(2,6)) and 256 in samples
    result=dict(passed=True,total_cases=cases,paths=dict(paths),all_classes_0_through_15_by_all_initial_R=True,
        game_slots_available=[0,1,3,6],synthetic_ROM_used=True,ROM_read_addresses_include_0100=True,ROM_0000_and_0100_distinct=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        actual_banked_effect_and_game_child_generator_executed=True,real_four_ports=True,
        maximum_additional_stack_bytes=depth,complete_external_return=True,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionFullLargeEffectVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
