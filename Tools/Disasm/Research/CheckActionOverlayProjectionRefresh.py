"""ADC5, повтор числовых углов с точным R и несколькими адресами внешнего стека."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers
from CheckMusicGateTicks import Memory
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionOverlayProjection import evaluate


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    memory=Memory(flat);simulator=Simulator(memory);counts=Counter();touched=set()
    edges=(0,1,2,127,128,255,256,257,511,512,1024,32767,32768,32769,65534,65535)
    randomizer=random.Random(0xADC5);inputs=list(product(edges,repeat=3))+[tuple(randomizer.randrange(65536) for _ in range(3)) for _ in range(4096)]
    for horizontal,vertical,depth in inputs:
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=flat[address]
        stack=(0xBFFE,0xBFE0,0x8008)[serial%3];memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xADC5,'SP':stack,'AF':serial&65535,'HL':vertical,'DE':depth,'BC':horizontal,
            '^AF':0xABCD,'^HL':0x1357,'^DE':0x2468,'^BC':0x369C,'IX':0xA100,'IY':0xA140},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=evaluate(initial);expected=list(memory)
        for address,value in model['writes']:expected[address]=value
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(start=0xADC5,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(model['registers'][i]==simulator.registers[i] for i in compared),(serial,horizontal,vertical,depth,model['path'],[(i,model['registers'][i],simulator.registers[i]) for i in compared if model['registers'][i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==model['writes'],(serial,'RAM')
        touched={a for a,_ in model['writes']}|{stack,stack+1};counts[model['path']]+=1
    result=dict(passed=True,total_cases=counts.total(),outcomes=dict(counts),exact_registers_flags_r_sp=True,
        entire_64K_and_write_order_compared=True,external_stack_addresses=[0xBFFE,0xBFE0,0x8008],
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionOverlayProjectionRefreshVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
