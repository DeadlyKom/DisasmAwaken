"""F69E и вход F68E, настоящий поток 0 и все цели классов до возврата."""
import argparse
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionClassRefresh import RefreshMachine
from ReferenceControlsBufferPoints import sub16_flags


class RandomClassMachine(RefreshMachine):
    def gate(self):
        self.call(0xEB72,0xF6A1,lambda:self.stream(0))
        word=self.r[6]*256+self.r[7];value=(word-0xF000)&65535
        self.pair(4,0xF000);self.pair(6,value);self.r[1]=sub16_flags(word,0xF000)
        self.m1(5)
        if word<0xF000:self.path.append('random_gate_reject');return self.finish()
        self.path.append('random_gate_dispatch');self.m1(1);return self.dispatch_class()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--via-entry', action='store_true')
    via_entry = parser.parse_args().via_entry
    entry = 0xF68E if via_entry else 0xF69E
    flat=flat_action();banks=[bytearray([160+i]*16384) for i in range(8)]
    assert bytes(flat[0xF68E:0xF691]) == bytes.fromhex('C3 9E F6')
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks]
    simulator=Simulator(memory);paths=Counter();maximum_stack=0
    for serial in range(65536):
        memory.recording=False
        for b in range(8):memory.banks[b][:]=baseline[b]
        # Создание ограниченного исходной таблицей кода класса с обоими значениями старшего бита.
        for index in range(25):
            address=0xA100+index*64
            memory[address],memory[address+1],memory[address+18]=index,1,index
        memory[0xA740],memory[0xA741]=128,128
        memory[0xA112],memory[0xA115],memory[0xA116]=(serial%26)|(serial&128),255,serial&255
        memory[0xEBDE],memory[0xEBDF],memory[0xEBE0]=serial&255,serial>>8,(serial*73)&255
        memory[0x9BCD]=serial&255
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':entry,'SP':stack,'AF':serial,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,(serial*17)&255,serial&1,serial%3
        model=RandomClassMachine(memory.banks,initial)
        if via_entry:
            model.m1(1)
        model.gate()
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True;simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM')
        assert not trace.writes and memory.o7ffd==16
        for bank,offset,_ in memory.writes:
            if bank==2 and stack-32<=offset+0x8000<stack:maximum_stack=max(maximum_stack,stack-offset-0x8000)
        paths.update(model.path)
        if (serial+1)%16384==0:print(str(serial+1)+' random class gate cases passed',flush=True)
    assert paths['random_gate_reject'] and paths['random_gate_dispatch'] and all(paths['class_'+str(i)] for i in range(26))
    result=dict(passed=True,total_cases=65536,entry=entry,paths=dict(paths),all_seed_words=True,all_class_table_targets_executed=True,
        actual_random_dispatch_and_handlers_executed=True,exact_registers_flags_r_sp=True,
        all_eight_banks_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=maximum_stack,
        all_input_products_exhausted=False,game_caller_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    report = 'ActionRandomClassGateEntryVerification' if via_entry else 'ActionRandomClassGateVerification'
    path = ROOT / f'Tools/Disasm/Reports/{report}.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
