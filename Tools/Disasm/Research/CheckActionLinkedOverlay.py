"""E804, полные словарные срезы и все пары R/порог, реальные дети до внешнего RET."""
from collections import Counter
import json,random,sys
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionLinkedOverlay import LinkedOverlayMachine
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def profiles():
    for r in range(256):
        for limit in range(256):yield (0,0,0xFFFF,0,0,0xFFFF),r,limit,0,'all_R_and_thresholds'
    for axis in range(6):
        for word in range(65536):
            values=[0,0,256,0,0,256];values[axis]=word
            yield values,word&255,74,0,'all_six_word_slices'
    randomizer=random.Random(0xE804)
    for serial in range(4096):
        yield tuple(randomizer.randrange(65536) for _ in range(6)),serial&255,serial*73&255,serial%4,'mixed_and_link_modes'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    counts=Counter();paths=Counter();depth=0;r_cases=0
    for values,r,limit,mode,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100;pointer=0xA100 if mode==3 else 0xA140;stack=0xBFFE
        for base,words in ((ix,values[:3]),(pointer,values[3:])):
            for k,word in enumerate(words):memory[base+26+2*k],memory[base+27+2*k]=word&255,word>>8
        memory[ix+11]=26 if mode==2 else 1
        if mode==1:memory[pointer+27]=128
        memory[0xE796],memory[0xE797]=pointer&255,pointer>>8;memory[0xE823]=limit
        memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xE804,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=LinkedOverlayMachine(memory.banks,initial);model.linked_overlay(ops)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(30000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',serial,values,model.path))
        memory.recording=False;compared=[i for i in (*range(25),26,27) if i!=15 or not model.rendered]
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,values,r,limit,mode,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        for page,offset,_ in memory.writes:
            if page==2 and stack-40<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path);r_cases+=int(not model.rendered)
        if counts.total()%65536==0:print(str(counts.total())+' linked overlay cases passed',flush=True)
    assert counts.total()==462848 and all(paths['overflow_'+str(i)] for i in range(3)),(counts,paths)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_R_by_256_thresholds=True,all_six_word_domains_on_slices=True,
        actual_linked_vector_projection_clipping_and_raster_children_executed=True,
        exact_registers_except_R_on_renderer=True,exact_R_on_nonrenderer_cases=r_cases,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_observed_additional_stack_bytes=depth,
        original_unbalanced_EXX_on_linked_marker_preserved=True,renderer_R_proved=False,
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionLinkedOverlayVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
