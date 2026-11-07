"""EB41, настоящий XOR-сегмент с реальными проекциями, отсечением и растеризацией."""
from collections import Counter
from itertools import product
import json,random,sys
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionOverlayPair import OverlayPairMachine
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    assert bytes(flat[0xEB6E:0xEB72])==bytes((0xB2,0,5,0))
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    edges=(0,1,95,96,127,128,255,256,511,32767,32768,32769,65534,65535)
    vectors=list(product((0,128,65535),(0,48,65535),(1,256,65535)))
    inputs=list(product(vectors,repeat=2));randomizer=random.Random(0xEB41)
    inputs += [(tuple(randomizer.choice(edges) for _ in range(3)),tuple(randomizer.choice(edges) for _ in range(3))) for _ in range(4096)]
    counts=Counter();r_cases=0;depth=0
    for first,second in inputs:
        serial=sum(counts.values());memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        memory.banks[2][:3072]=bytes((i*37+serial*11)&255 for i in range(3072))
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xEB41,'SP':stack,'AF':serial&65535,'HL':first[1],'DE':first[2],'BC':first[0],
            '^AF':0xDEF0,'^HL':second[1],'^DE':second[2],'^BC':second[0],'IX':0xA100,'IY':0xA140},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=OverlayPairMachine(memory.banks,initial);model.overlay_pair(ops)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(30000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',first,second,model.path))
        memory.recording=False;compared=[i for i in (*range(25),26,27) if i!=15 or not model.rendered]
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,first,second,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        for page,offset,_ in memory.writes:
            if page==2 and stack-32<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[model.path[-1]]+=1;r_cases+=int(not model.rendered)
    assert sum(counts.values())==4825 and counts['inside_line'] and counts['clipped_line'] and counts['common_outside_side']
    result=dict(passed=True,total_cases=sum(counts.values()),outcomes=dict(counts),
        actual_projection_pair_codes_clipping_and_XOR_raster_executed=True,
        exact_registers_except_R_on_renderer=True,exact_R_on_nonrenderer_cases=r_cases,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_observed_additional_stack_bytes=depth,
        second_projection_reject_leaves_EXX_exchanged=True,all_input_products_exhausted=False,
        renderer_R_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionOverlayPairVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
