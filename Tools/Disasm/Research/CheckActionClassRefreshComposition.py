"""F003 до внешнего RET через все классы и полный вычислитель смещений.

Документация: ../../../Docs/ActionClassRefresh.md#полный-внешний-возврат
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionClassRefresh import RefreshMachine
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference
from CheckScreenUpdate import PortTrace


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();depth=0
    for kind in range(26):
        for alias in (0,128):
            for r in range(256):
                for override in (0,1,255):
                    memory.recording=False
                    for page in (0,2,5):memory.banks[page][:]=baseline[page]
                    for index,code in enumerate((0,5,6,7,14,18)):
                        pointer=0xA100+64*index;memory[pointer],memory[pointer+1],memory[pointer+18]=index,1,code
                    memory[0xA280],memory[0xA281]=128,128
                    ix=0xA700;memory[ix],memory[ix+1]=0,128 if r&2 else 1
                    for offset,byte in {7:r,8:r*73&255,9:(r+kind)&255,10:2,15:(0,3,127,255)[r&3],16:r,36:(0,1,128,255)[kind&3]}.items():
                        memory[ix+offset]=byte
                    memory[ix+18],memory[ix+21],memory[ix+22]=kind+alias,override,13 if r&1 else 12
                    memory[0x9BCD]=r
                    for pointer in (0xEBDE,0xEBE1,0xEBE7):
                        word=(5254 if r%4==0 and pointer==0xEBDE else (r*257+kind*137)&65535)
                        memory[pointer],memory[pointer+1],memory[pointer+2]=word&255,word>>8,0
                    stack=0xBFFE;memory[stack],memory[stack+1]=255,63
                    initial=get_registers({'PC':0xF003,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                    initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
                    model=RefreshMachine(memory.banks,initial);model.refresh_class()
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
                    model.r=wanted
                    paths['common/'+common_path]+=1
                    ports=PortTrace(simulator);simulator.set_tracer(ports)
                    simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                    for _ in range(3000):
                        if simulator.registers[24]==0x3FFF:break
                        simulator.run()
                    else:raise AssertionError(('нет общего хвоста',kind,r,override))
                    memory.recording=False
                    assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(kind,r,override,model.path)
                    assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes)
                    assert not ports.writes and memory.o7ffd==16
                    for bank,offset,_ in memory.writes:
                        if bank==2 and stack-14<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
                    cases+=1;counts[str(kind)]+=1;paths.update(model.path)
    assert cases==39936 and depth==12,(cases,depth,dict(paths))
    result=dict(passed=True,total_cases=cases,cases_by_class=dict(counts),paths=dict(paths),
        all_26_classes_both_bit7_aliases_and_all_R=True,all_eleven_distinct_class_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_additional_stack_bytes=depth,common_tail_executed=True,full_external_return=True,boundary=0x3FFF,
        actual_coefficient_and_three_multiply_children=True,no_OUT=True,correlated_phase_scale_profiles=True,
        active_and_marker_current_records=True,exact_T_claimed=False,
        all_input_products_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClassRefreshCompositionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('paths','cases_by_class')},indent=2))


if __name__=='__main__':main()
