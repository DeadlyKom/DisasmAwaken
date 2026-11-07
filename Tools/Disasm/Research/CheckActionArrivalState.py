"""State08, полный подход и оба эффекта, реальные очереди банка 1 и игровые дети."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckEffects import memory_image
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionArrivalState import ArrivalMachine
from ReferenceControlsTextQueue import QUEUE,PRODUCER


def profiles():
    for cls in range(256):
        for mode in range(4):
            for notify in (0,1):
                for own in (False,True):yield cls,mode,notify,24 if own else 0,cls*257,'all_classes_modes_notify_self'
    for delta in range(65536):yield 16,4,delta&1,0,delta,'all_first_word_differences'
    for target in range(26):
        for mode in range(4):
            for r in (0,1,127,128,254,255):yield (0,5,6,7,8,17)[r%6],mode,1,target,r*257,'all_original_target_slots'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);banks[3]=bytearray(memory_image()[0xC000:])
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();banks[4][:len(objects)]=objects
    rom=bytes((i*71+39+(i>>8)*13)&255 for i in range(0x4000));memory=RecordedBanks(banks=banks,out7ffd=16);memory.roms=(memory.roms[0],rom)
    baseline=[bytearray(b) for b in banks];simulator=Simulator(memory);counts=Counter();paths=Counter();depth=0
    for cls,mode,notify,target,delta,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        memory.out7ffd(16);ix=0xA700;selected=0xA100+64*target;stack=0xBFFE
        for row in range(25):
            p=0xA100+64*row;memory[p],memory[p+1],memory[p+18],memory[p+24]=0,128 if row in (1,2,3) else 1,16,255
        memory[0xA740],memory[0xA741]=128,128
        for base,words in ((selected,(0,0,0)),(ix,(delta if mode==4 else 4096 if mode==1 else 0,4096 if mode==1 else 0,4096 if mode==1 else 0))):
            for axis,word in enumerate(words):memory[base+2*axis],memory[base+2*axis+1]=word&255,word>>8
        memory[selected+6],memory[selected+18],memory[selected+10]=(0,2,136,254)[serial%4],cls,255 if mode==3 else 2
        memory[ix+6],memory[ix+18],memory[ix+15],memory[ix+13],memory[ix+17]=0,cls if mode==0 else 17,target,serial&255,notify
        memory[ix+7],memory[ix+8],memory[ix+9]=serial&255,serial*73&255,serial*109&255
        if mode==0:memory[selected+1]=128
        if target==25:memory[selected],memory[selected+1]=128,128
        memory[0x9BCE],memory[0x9BCF]=serial&255,serial>>8&255
        head=serial%17;cursor=QUEUE+2*head;memory.banks[1][PRODUCER&0x3FFF],memory.banks[1][(PRODUCER+1)&0x3FFF]=cursor&255,cursor>>8
        for row in range(16):memory.banks[1][(QUEUE+2*row)&0x3FFF]=1 if serial&1 and row==serial%16 else 128
        for row in range(8):memory[0xA79C+18*row]=0 if row==serial%9 else 1
        memory[0xA82C]=128;memory[0x6D3D]=serial*73&255;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF57F,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':serial*137&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=ArrivalMachine(memory.banks,initial);model.arrival(rom)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(8000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',serial,cls,mode,target,model.path))
        memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,cls,mode,notify,target,delta,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        assert trace.writes==model.ports and memory.o7ffd==16,(serial,'OUT',trace.writes,model.ports)
        for page,offset,_ in memory.writes:
            if page==2 and stack-32<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
        if counts.total()%16384==0:print(str(counts.total())+' State08 cases passed',flush=True)
    assert counts.total()==70256 and all(paths[p] for p in ('approach_far','approach_near_effect_target','target_missing_effect_current','arrival_counter_incremented','text_dropped','text_accepted')),(counts,paths)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_effect_class_codes=True,all_first_component_differences=True,all_26_original_target_slots=True,
        actual_approach_queue_large_effect_and_game_children_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,real_ports=True,synthetic_ROM_used=True,
        maximum_additional_stack_bytes=depth,third_component_not_stored_on_near_path=True,
        complete_external_return=True,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionArrivalStateVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
