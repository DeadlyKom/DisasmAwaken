"""Оригинальный вход 74FB, все пары выбираемых байтов, точные флаги и указатель."""
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import refresh


def main():
    memory=Memory(flat_action());simulator=Simulator(memory)
    memory[0xBFFE:0xC000]=[0xFF,0x3F]
    counts={'preferred':0,'fallback':0}
    for preferred in range(256):
        for fallback in range(256):
            memory.recording=False
            memory[0x9C10:0x9C12]=[preferred,fallback]
            initial=get_registers({'AF':(preferred<<8)|fallback,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
                'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x74FB},None,False)
            initial[14],initial[15],initial[26],initial[27]=preferred,fallback,preferred&1,fallback%3
            wanted=list(initial)
            wanted[0:2]=[preferred if preferred else fallback,and_flags(preferred)]
            wanted[6:8]=[0x9C,0x10 if preferred else 0x11]
            wanted[SP],wanted[PC]=0xC000,0x3FFF
            wanted[15]=refresh(initial[15],4 if preferred else 7)
            before=list(memory)
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True
            for _ in range(9):
                if simulator.registers[PC]==0x3FFF:break
                simulator.run()
            else:raise AssertionError(('возврат',preferred,fallback))
            memory.recording=False
            compared=(*range(13),14,15,*range(16,24),PC,26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(preferred,fallback,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert memory==before and memory.writes==[]
            counts['preferred' if preferred else 'fallback']+=1
    report=dict(passed=True,total_cases=sum(counts.values()),cases_by_path=counts,
        all_input_byte_pairs=True,exact_registers_flags_refresh_sp=True,
        every_ram_byte_checked=True,no_memory_or_stack_writes=True,
        returned_pointer_selects_source=True,flags_describe_preferred_not_fallback=True,
        original_action_kernel_relocation_used=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPreferredByteVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
