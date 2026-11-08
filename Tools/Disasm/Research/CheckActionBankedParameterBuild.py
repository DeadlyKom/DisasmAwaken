"""697E, банковая обёртка и настоящий построитель до внешнего RET без сборки."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import PortTrace,put
from ReferenceControlsPointRespawn import refresh


def main():
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ControlsParameterActivationVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['exact_registers_flags_r_and_sp']
    flat=flat_action();baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:]);counts=Counter()
    def check(first,second,control,old):
        serial=counts.total();stack=0xBFFE
        def fixture(page):
            memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=page)
            put(memory,0x9BC1,[first&255,first>>8,second&255,second>>8,control]);put(memory,stack,[255,63])
            return memory
        initial=get_registers({'AF':serial*73&65535,'HL':0x1357,'DE':0x2468,'BC':(first+73*second)&65535,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x697E},None,False)
        initial[14],initial[15],initial[26],initial[27]=control,second&255,control&1,first%3
        # Расчёт побочных записей CALL селектора и его PUSH BC до настоящего дочернего входа.
        prefix=[(2,0x3FFC,0x83),(2,0x3FFD,0x69),(2,0x3FFA,initial[3]),(2,0x3FFB,initial[2])]
        oracle=fixture(17)
        for bank,offset,value in prefix:oracle.banks[bank][offset]=value
        child_initial=list(initial);child_initial[0]=17;child_initial[15]=refresh(initial[15],9);child_initial[PC]=0xDE0A
        child=Simulator(oracle);child.registers[:]=child_initial;child_trace=PortTrace(child);child.set_tracer(child_trace)
        oracle.writes=[];oracle.recording=True
        for _ in range(30000):
            if child.registers[PC]==0x3FFF:break
            child.run()
        else:raise AssertionError(('дочерний вход не завершён',serial))
        oracle.recording=False
        memory=fixture(old);simulator=Simulator(memory);simulator.registers[:]=initial
        trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(30100):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('обёртка не завершена',serial))
        memory.recording=False
        compared=(*range(25),26,27)
        assert all(child.registers[i]==simulator.registers[i] for i in compared),(serial,'регистры')
        assert memory.banks==oracle.banks and Counter(memory.writes)==Counter(prefix+oracle.writes),(serial,'RAM')
        assert trace.writes==[(0x7FFD,17)]+child_trace.writes==[(0x7FFD,17),(0x7FFD,16)]
        assert memory.o7ffd==16 and simulator.registers[12]==stack+2
        counts[str(old)]+=1
    # Проверка каждого управляющего байта в четырёх исходных координатных областях.
    for first in (0x4A36,0x4734,0x4738,0):
        for control in range(256):check(first,(first+25173*control)&65535,control,16)
    # Проверка всех 32 неблокированных исходных конфигураций paging.
    for old in range(32):
        for control in (0,1,255):check(0x4A36,0xA55A,control,old)
    assert counts.total()==1120
    result=dict(passed=True,total_cases=1120,cases_by_initial_7ffd=dict(counts),
        method='wrapper_composition_with_real_previously_verified_child_not_independent_full_child_oracle',
        real_children_executed_without_stubs=True,all_control_bytes_in_four_regions=True,
        all_32_unlocked_initial_paging_values=True,exact_registers_flags_r_sp=True,
        all_eight_banks_and_write_multiplicity_checked=True,extra_wrapper_refresh_m1=9,
        maximum_additional_stack_bytes=10,initial_paging_restored=False,final_paging=16,
        original_697D_byte_classified=False,game_caller_proved=False,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/ActionBankedParameterBuildVerification.json'
    temporary=target.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(target)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
