"""State0E до внешнего RET, полный большой эффект и общий вычислитель.

Документация: ../../../Docs/ActionLinkedProximity.md#полный-внешний-возврат
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from CheckActionNearestCandidate import NearestMachine
from ReferenceActionClassRefresh import RefreshMachine
from ReferenceControlsPointRespawn import cp_flags,refresh
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes
from CheckActionSelectedRecordStep import arguments


from CheckActionLinkedProximity import LinkedMachine
from ReferenceActionLargeClassEffect import LargeClassMachine
from CheckEffects import memory_image
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference

class FullLinkedMachine(LinkedMachine,LargeClassMachine):
    pass


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);ratio=bytes(flat[0x9A00:0x9B00]);root=bytes(banks[1][:768])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    banks[3][:]=bytes(memory_image()[0xC000:])
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();banks[4][:len(objects)]=objects
    rom=bytes((i*71+39+(i>>8)*13)&255 for i in range(0x4000));memory.roms=(memory.roms[0],rom)
    baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);cases=0;paths=Counter();depth=0;r_proved=0
    for index in range(256):
        for mode in range(4):
            for code in (*range(26),*range(128,154)):
                for bit4 in (0,16):
                    memory.recording=False
                    for page in range(8):memory.banks[page][:]=baseline[page]
                    memory.out7ffd(16)
                    for row,kind in enumerate((0,5,6,7,14,18)):
                        pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+18]=row,1,kind
                    memory[0xA740],memory[0xA741]=128,128
                    ix=0xA100;selected=0xA100+64*index
                    for axis,value in enumerate((0x1234,0x2345,0x3456)):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
                    memory[ix+18],memory[ix+11],memory[ix+21],memory[ix+22]=code,index,0 if cases&1 else 255,13 if cases&2 else 12
                    memory[ix+8],memory[ix+9],memory[ix+37]=cases*73&255,cases*109&255,(0,1,2,3,127,128,255)[cases%7]
                    if index<25:
                        for axis,delta in enumerate((0,255,65535) if mode!=3 else (256,1024,0xF000)):
                            value=(memory[ix+2*axis]+256*memory[ix+2*axis+1]+delta)&65535
                            memory[selected+2*axis],memory[selected+2*axis+1]=value&255,value>>8
                        memory[selected+18]=18 if mode==1 else 19
                        memory[selected+24]=(cases*37&0xEF)|bit4
                        if mode==0:memory[selected+1]=128
                    stack=0xBFFE;memory[stack],memory[stack+1]=255,63
                    initial=get_registers({'PC':0xF009,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                    initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
                    for offset,byte in {7:index,10:14,15:(0,3,127,255)[mode],16:index,36:code*73&255}.items():
                        memory[ix+offset]=byte
                    model=FullLinkedMachine(memory.banks,initial);model.ports=[];model.linked(ratio,root)
                    if model.r[24]==0xEA29:
                        model.large_class_effect(rom);assert model.r[24]==0xF03A
                        model.m1(1);model.r[24]=0xF0F8
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
                    simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
                    for _ in range(5000):
                        if simulator.registers[24]==0x3FFF:break
                        simulator.run()
                    else:raise AssertionError(('нет границы',index,mode,code,bit4))
                    memory.recording=False
                    compared=[*range(25),26,27]
                    assert all(model.r[i]==simulator.registers[i] for i in compared),(cases,index,mode,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
                    assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
                    assert trace.writes==model.ports and memory.o7ffd==16
                    for bank,offset,_ in memory.writes:
                        if bank==2 and stack-20<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
                    r_proved+=1;paths.update(model.path);cases+=1
                    if cases%32768==0:print(str(cases)+' linked proximity cases passed',flush=True)
    assert cases==106496 and paths['large_effect_boundary'] and paths['far_geometry'] and paths['near_class_refresh']
    result=dict(passed=True,total_cases=cases,paths=dict(paths),all_256_indices_with_modes_and_class_aliases=True,
        exact_registers_flags_sp_and_all_ram=True,exact_R_cases=r_proved,far_geometry_R_proved=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,real_ports_compared=True,
        maximum_additional_stack_bytes=depth,large_effect_body_executed=True,common_tail_executed=True,full_external_return=True,
        synthetic_ROM_used=True,correlated_phase_scale_profiles=True,exact_T_claimed=False,
        boundaries=[0x3FFF],all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedProximityCompositionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
