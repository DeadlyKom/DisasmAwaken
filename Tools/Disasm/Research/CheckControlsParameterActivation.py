"""Композиционная проверка DE0A, ранее независимо проверенные дети исполняются без подмен."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckScreenUpdate import PortTrace, put
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionApplyParameters import DESTINATIONS
from ReferenceControlsPointRespawn import refresh
from CheckActionRegionType import reference as region_type


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    for name in ('ControlsParameterTablesVerification','ActionApplyParametersVerification','ActionParameterActivationVerification'):
        assert read(name)['passed']
    flat = flat_action()
    baseline = [bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0] = bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1] = bytearray(base_memory()[0xC000:])
    cases = 0
    count_by_page = Counter()
    def fixture(first,second,control,old):
        memory = RecordedBanks(banks=[bytearray(bank) for bank in baseline],out7ffd=old)
        put(memory,0x9BC1,[first&255,first>>8,second&255,second>>8,control])
        put(memory,0xBFFE,[0xFF,0x3F])
        return memory
    def check(first,second,control,old=0x11):
        nonlocal cases
        initial = get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':(first+73*second)&65535,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xDE0A},None,False)
        initial[14],initial[15],initial[26],initial[27] = control,second&255,control&1,first%3
        oracle = fixture(first,second,control,old)
        put(oracle,0xBFFC,[0x0D,0xDE])
        child_initial = list(initial)
        child_initial[PC],child_initial[SP] = 0xDE10,0xBFFC
        # Учёт настоящего CALL DE10 до композиционного исполнения независимо проверенного ребёнка.
        child_initial[15] = refresh(initial[15],1)
        child_initial[25] += 17
        child = Simulator(oracle)
        child.registers[:] = child_initial
        child_trace = PortTrace(child)
        child.set_tracer(child_trace)
        oracle.writes = []
        oracle.recording = True
        for _ in range(25000):
            if child.registers[PC]==0xDE0D:
                break
            child.run()
        else:
            raise AssertionError(('ребёнок',first,second,control))
        oracle.recording = False
        assert child.registers[SP]==0xBFFE and not child_trace.writes and oracle.o7ffd==old
        assert not any(bank==1 for bank,_,_ in oracle.writes) and oracle.banks[1]==baseline[1]
        expected = [bytearray(bank) for bank in oracle.banks]
        writes = [(2,0x3FFD,0xDE),(2,0x3FFC,0x0D)]+list(oracle.writes)
        # Расчёт хвостовой активации по доказанному прямому маршруту и настоящим рамкам вызовов.
        writes += [(2,0x3FFD,0xAC),(2,0x3FFC,0x49),
            (2,0x3FFB,child.registers[2]),(2,0x3FFA,child.registers[3]),
            (2,0x3FFD,0xAC),(2,0x3FFC,0x4C)]
        parameters = list(oracle[0x9BA4:0x9BB3])
        writes += [(5 if address<0x8000 else 2 if address<0xC000 else 0,
                    address&0x3FFF,parameters[index]) for index,address in DESTINATIONS]
        writes += [(0,0x2CA9,0),(0,0x2CAA,0),(0,0x2CF6,0),(0,0x2CF7,0),(2,0x1B83,0),(2,0x1B82,0)]
        for bank,index,value in writes:
            expected[bank][index] = value
        wanted = list(child.registers)
        wanted[0:2],wanted[6:8] = [0,0x44],[0,0]
        wanted[SP] = 0xC000
        wanted[15] = refresh(wanted[15],63)
        actual_memory = fixture(first,second,control,old)
        actual = Simulator(actual_memory)
        actual.registers[:] = initial
        trace = PortTrace(actual)
        actual.set_tracer(trace)
        actual_memory.writes = []
        actual_memory.recording = True
        for _ in range(25100):
            if actual.registers[PC]==0x3FFF:
                break
            actual.run()
        else:
            raise AssertionError(('обёртка',first,second,control))
        actual_memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==actual.registers[i] for i in compared), (first,second,control,
            [(i,wanted[i],actual.registers[i]) for i in compared if wanted[i]!=actual.registers[i]])
        assert trace.writes==[(0x7FFD,0x10)] and actual_memory.o7ffd==0x10
        assert all(a==b for a,b in zip(actual_memory.banks,expected)) and Counter(actual_memory.writes)==Counter(writes)
        assert min(index for bank,index,_ in actual_memory.writes if bank==2 and index>=0x3F00)>=0x3FF4
        cases += 1
        count_by_page[old] += 1
    # Проверка всех управляющих байтов в каждой исходной координатной области.
    for first in (0x4A36,0x4734,0x4738,0):
        for control in range(256):
            check(first,(first+25173*control)&65535,control)
    # Проверка всех неблокированных значений порта с выбранным исходным банком 1.
    for old in (1,9,17,25):
        for control in (0,1,255):
            check(0x4A36,0xA55A,control,old)
    result = dict(passed=True,total_cases=cases,cases_by_initial_7ffd=dict(count_by_page),
        method='composition_of_independently_verified_children_and_direct_bank_tail',
        independent_complete_child_oracle=False,child_numeric_oracles_previously_passed=True,
        real_parent_children_and_out_without_stubs=True,all_control_bytes_in_every_region=True,
        initial_bank_1_final_bank_0=True,exact_registers_flags_r_and_sp=True,
        every_physical_ram_byte_and_write_checked=True,maximum_additional_stack_bytes=10,
        wrapper_extra_refresh_m1=64,game_field_names_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsParameterActivationVerification.json').write_bytes(
        (json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
