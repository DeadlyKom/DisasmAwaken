"""F222, все пары A/H и все полные классы с байтом Unknown14, настоящий создатель."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionSpawnWindow import SpawnWindowMachine


def profiles():
    for a in range(256):
        for high in range(256):yield a,high,(a+high)&255,0,'all_A_H_pairs'
    for code in range(256):
        for counter in range(256):yield 240,95,code,counter,'all_classes_counters'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0
    for a,high,code,counter,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for row in range(25):
            pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row==1 and not serial&1 else 1,0
        ix=0xA100;memory[0xA740],memory[0xA741]=128,128
        memory[ix+11],memory[ix+18],memory[ix+20],memory[ix+24]=2,code,counter,serial&8
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF222,'SP':stack,'AF':a*256+(serial&255),'HL':high*256+0xF0,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=SpawnWindowMachine(memory.banks,initial);model.spawn_window()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(2500):
            if simulator.registers[24]==0xF0F8:break
            simulator.run()
        else:raise AssertionError(('нет общего хвоста',serial,model.path))
        memory.recording=False;compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        for page,offset,_ in memory.writes:
            if page==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
    assert counts.total()==131072 and depth==8,(counts,depth)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_A_by_256_H=True,all_256_classes_by_256_Unknown14=True,full_class_table_index_not_clamped=True,
        actual_current_link_and_class17_children_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=depth,
        common_F0F8_executed=False,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionSpawnWindowVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
