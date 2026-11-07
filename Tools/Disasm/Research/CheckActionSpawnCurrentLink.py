"""F255, все индексы связи и ReuseByte, полный создатель до внешнего RET."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionSpawnCurrentLink import CurrentLinkMachine


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0
    for linked in range(256):
        for reuse in range(256):
            for no_free in (False,True):
                serial=counts.total();memory.recording=False
                for page in (0,2,5):memory.banks[page][:]=baseline[page]
                ix=0xA100+64*(serial%25);slot=(serial//2+1)%25
                if slot==serial%25:slot=(slot+1)%25
                for row in range(25):
                    pointer=0xA100+64*row;memory[pointer],memory[pointer+1],memory[pointer+24]=0,128 if row==slot and not no_free else 1,0
                memory[0xA740],memory[0xA741]=128,128
                for axis,word in enumerate((serial*73&65535,serial*109&65535,serial*137&65535)):
                    memory[ix+2*axis],memory[ix+2*axis+1]=word&255,word>>8
                memory[ix+11],memory[ix+24]=linked,reuse
                stack=0xBFFE;memory[stack],memory[stack+1]=255,63
                initial=get_registers({'PC':0xF255,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
                model=CurrentLinkMachine(memory.banks,initial);model.spawn_current_link()
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                for _ in range(2000):
                    if simulator.registers[24]==0x3FFF:break
                    simulator.run()
                else:raise AssertionError(('нет возврата',serial,model.path))
                memory.recording=False;compared=(*range(25),26,27)
                assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
                assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
                for page,offset,_ in memory.writes:
                    if page==2 and stack-12<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
                counts['no_free' if no_free else 'allocated']+=1;paths.update(model.path)
                if counts.total()%32768==0:print(str(counts.total())+' current link spawn cases passed',flush=True)
    assert counts.total()==131072 and depth==6,(counts,depth)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_link_codes_by_256_ReuseByte_values_by_allocation=True,all_25_parent_slots=True,
        actual_ix_index_and_class17_creator_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=depth,
        AF_prime_cleared_before_child=True,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionSpawnCurrentLinkVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
