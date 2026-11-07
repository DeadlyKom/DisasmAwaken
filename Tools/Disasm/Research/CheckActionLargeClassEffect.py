"""EA29 для классов 10..FF, полный банковый большой эффект и освобождение до внешнего RET."""
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
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();depth=0
    for cls in range(16,256):
        for free in range(9):
            for ttl in (0,1,15,16,17,255):
                for offset in (0,2,136,254):
                    memory.recording=False
                    for page in range(8):memory.banks[page][:]=baseline[page]
                    memory.out7ffd((cases%4)*8);ix=0xA700;stack=0xBFFE
                    for axis,value in enumerate((cases&65535,(cases*73)&65535,cases^65535)):
                        value&=65535;memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
                    memory[ix+6],memory[ix+18]=offset,cls;memory[ix+24]=cases&255
                    memory[0x6D39],memory[0x6D3D]=cases&255,ttl
                    for row in range(8):memory[0xA79C+18*row]=0 if row==free else 1
                    memory[0xA82C]=128;memory[stack],memory[stack+1]=255,63
                    initial=get_registers({'PC':0xEA29,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                        '^AF':(cases*73)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                    initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
                    model=LargeClassMachine(memory.banks,initial);model.large_class_effect(memory.roms[1])
                    simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
                    for _ in range(1000):
                        if simulator.registers[24]==0x3FFF:break
                        simulator.run()
                    else:raise AssertionError(('нет возврата',cls,free,ttl,offset))
                    memory.recording=False
                    assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
                    assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM')
                    assert trace.writes==model.ports and memory.o7ffd==16
                    for bank,pos,_ in memory.writes:
                        if bank==2 and stack-12<=pos+0x8000<stack:depth=max(depth,stack-pos-0x8000)
                    paths.update(model.path);cases+=1
                    if cases%32768==0:print(str(cases)+' large class effect cases passed',flush=True)
    assert cases==51840 and depth==8
    result=dict(passed=True,total_cases=cases,paths=dict(paths),all_full_classes_16_through_255=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        real_OBJECT3D_large_effect_bank3_and_return_children_executed=True,real_four_port_writes_compared=True,
        maximum_additional_stack_bytes=depth,complete_external_return=True,classes_below_16_covered=False,
        all_input_products_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLargeClassEffectVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
