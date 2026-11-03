"""Пустой обработчик 704B, настоящий косвенный вызов и восстановление рамки, без подмен."""
import json
from collections import Counter
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionKeyDispatchPrefix import Inputs
from CheckActionNearZeroWord import cost
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import refresh


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory)
    index=24;pointer=0x7017+2*index;next_ix=0x9D4E+2*index
    assert original[pointer]|original[pointer+1]<<8==0x704B and original[0x704B]==0xC9
    row=original[0x9D4C+2*index]
    for mode in range(256):
        memory.recording=False;memory[0xA85F]=mode;memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6F1D},None,False)
        initial[14],initial[15],initial[26],initial[27]=mode,mode,mode&1,mode%3
        saved_hl=0x1300|27-index
        wanted=list(initial)
        wanted[0:8]=[mode,and_flags(mode),row,0xFE,pointer>>8,pointer&255,saved_hl>>8,saved_hl&255]
        wanted[8:10]=[next_ix>>8,next_ix&255]
        wanted[PC]=0x6F28
        m1=cost(0x6F1D,0x6F28)+(index+1)*cost(0x6F28,0x6F3B)+cost(0x6F3B,0x6F4E)+1+6
        wanted[15]=refresh(initial[15],m1)
        writes=[]
        for i,word in enumerate((saved_hl,pointer,(row<<8)|0xFE,next_ix,0x6F4E)):
            writes.extend([(0xBFFD-2*i,word>>8),(0xBFFC-2*i,word&255)])
        expected=list(memory)
        for address,value in writes:expected[address]=value
        simulator.registers[:]=initial;inputs=Inputs(index,0);simulator.set_tracer(inputs)
        memory.writes=[];memory.recording=True;seen_handler=False;seen_restore=False
        for _ in range(500):
            pc=simulator.registers[PC]
            seen_handler|=pc==0x704B;seen_restore|=pc==0x6F4E
            if seen_restore and pc==0x6F28:break
            simulator.run()
        else:raise AssertionError(('возврат',mode))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert seen_handler and seen_restore
        assert all(wanted[i]==simulator.registers[i] for i in compared),(mode,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes)
        assert len(inputs.reads)==25
    report=dict(passed=True,total_cases=256,method='actual_prefix_ret_and_restore_chain',
        all_mode_values=True,handler_opcode='C9',handler_refresh_m1=1,
        original_dispatch_and_restore_executed=True,exact_registers_flags_refresh_sp=True,
        every_ram_byte_and_write_checked=True,no_handler_or_restore_memory_writes=True,
        other_keyboard_handlers_proved=False,overlapping_pointer_bytes_preserved=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionIgnoreKeyVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
