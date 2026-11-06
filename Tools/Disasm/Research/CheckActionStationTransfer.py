"""6CE4, настоящий селектор страницы и хвостовой JP, цель DCE3 не исполняется."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory);counts=Counter()
    for old in range(64):
        for flags in range(256):
            memory.recording=False;memory.out7ffd(old);put(memory,0xBFFE,[255,63])
            put(memory,0xBFFA,[0xA5,0x5A,0xC3,0x3C]);serial=sum(counts.values())
            initial=get_registers({'AF':0xA500|flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6CE4},None,False)
            initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
            wanted=list(initial);wanted[0]=17;wanted[4:6]=[0,0];wanted[PC],wanted[15]=0xDCE3,refresh(initial[15],10)
            expected=[bytearray(b) for b in memory.banks];expected[2][0x3FFA:0x3FFE]=bytes([0x9C,0x36,0xEC,0x6C])
            writes=[(2,0x3FFC,0xEC),(2,0x3FFD,0x6C),(2,0x3FFA,0x9C),(2,0x3FFB,0x36)]
            simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
            for _ in range(16):
                if simulator.registers[PC]==0xDCE3:break
                simulator.run()
            else:raise AssertionError('граница перехода')
            memory.recording=False;compared=(*range(13),14,15,*range(16,24),PC,26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(old,flags,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(memory.writes)==Counter(writes)
            assert trace.writes==[(0x7FFD,17)] and memory.o7ffd==(old if old&32 else 17)
            counts['paging_locked' if old&32 else 'paging_changed']+=1
    report=dict(passed=True,total_cases=sum(counts.values()),cases_by_paging=dict(counts),
        method='actual_selector_and_eight_physical_banks_with_tail_jump_boundary',
        all_64_initial_paging_values=True,all_input_flags=True,exact_registers_flags_refresh_sp=True,
        every_physical_ram_byte_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=4,
        external_return_not_consumed=True,refresh_m1=10,
        execution_boundary='6CE4..DCE3, target instruction not executed',
        controls_target_requires_bank1_selected=True,station_disk_load_executed=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionStationTransferVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
