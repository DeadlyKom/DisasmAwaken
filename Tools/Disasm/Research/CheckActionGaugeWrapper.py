"""Композиционная проверка 6639 с настоящими OUT, доказанной шкалой и восемью банками."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace,put
from CheckActionParameterActivation import RecordedBanks,flat_action
from ReferenceControlsPointRespawn import refresh


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    assert read('ControlsSixRowGaugeVerification')['passed'] and read('ActionParameterActivationVerification')['passed']
    flat=flat_action()
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:])
    counts=Counter()

    def fixture(old):
        memory=RecordedBanks(banks=[bytearray(bank) for bank in baseline],out7ffd=old)
        put(memory,0xBFFE,[0xFF,0x3F])
        return memory

    def check(value,address,old=0x10):
        serial=counts.total()
        initial=get_registers({'AF':value*256+(serial&255),'HL':address,'DE':0x2468,
            'BC':(serial*73+0x369C)&65535,'^AF':(serial*37+0xDEF0)&65535,'^HL':0x1234,
            '^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6639},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        oracle=fixture(0x11)
        # Подготовка рамки перед настоящим CALL шкалы после первого выбора банка.
        put(oracle,0xBFFA,[initial[3],initial[2],0x43,0x66])
        child_initial=list(initial)
        child_initial[PC],child_initial[SP]=0xE8FD,0xBFFC
        child_initial[16]=0x11
        child_initial[15]=refresh(initial[15],11)
        child=Simulator(oracle);child.registers[:]=child_initial
        child_trace=PortTrace(child);child.set_tracer(child_trace)
        oracle.writes=[];oracle.recording=True
        for _ in range(270):
            if child.registers[PC]==0x6643:break
            child.run()
        else:raise AssertionError(('шкала',value,address,old))
        oracle.recording=False
        assert child.registers[SP]==0xBFFE and child_trace.writes==[]
        expected=[bytearray(bank) for bank in oracle.banks]
        writes=[(2,0x3FFD,0x66),(2,0x3FFC,0x3F),(2,0x3FFB,initial[2]),(2,0x3FFA,initial[3]),
            (2,0x3FFD,0x66),(2,0x3FFC,0x43)]+list(oracle.writes)
        writes += [(2,0x3FFD,0x66),(2,0x3FFC,0x48),
                   (2,0x3FFB,child.registers[2]),(2,0x3FFA,child.registers[3])]
        for bank,index,data in writes:expected[bank][index]=data
        wanted=list(child.registers)
        wanted[0],wanted[SP],wanted[PC]=0x10,0xC000,0x3FFF
        wanted[15]=refresh(wanted[15],9)
        actual_memory=fixture(old)
        actual=Simulator(actual_memory);actual.registers[:]=initial
        trace=PortTrace(actual);actual.set_tracer(trace)
        actual_memory.writes=[];actual_memory.recording=True
        for _ in range(300):
            if actual.registers[PC]==0x3FFF:break
            actual.run()
        else:raise AssertionError(('обёртка',value,address,old))
        actual_memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==actual.registers[i] for i in compared),(value,address,old,
            [(i,wanted[i],actual.registers[i]) for i in compared if wanted[i]!=actual.registers[i]])
        assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10)] and actual_memory.o7ffd==0x10
        assert all(a==b for a,b in zip(actual_memory.banks,expected)) and Counter(actual_memory.writes)==Counter(writes)
        stack_writes=[index for bank,index,_ in actual_memory.writes if bank==2 and index>=0x3FF0]
        assert stack_writes and min(stack_writes)==0x3FFA
        counts[old]+=1

    # Проверка каждого значения шкалы на шести исходных местах интерфейса и пяти граничных адресах.
    for address in (0x49A1,0x49E1,0x5121,0x5181,0x51C1,0x49B9,0x8000,0xB000,0xC100,0xC1FD,0xFAF8):
        for value in range(256):check(value,address)
    # Проверка всех неблокированных исходных конфигураций порта, включая его экранный и ROM-биты.
    for old in range(32):
        for value in (0,6,7,47,48,62,63,255):check(value,0x49A1,old)
    report=dict(passed=True,total_cases=counts.total(),cases_by_initial_page=dict(counts),
        method='composition_of_independently_checked_gauge_and_page_selector',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_checked=True,
        real_out_and_physical_eight_banks=True,all_unlocked_initial_pages=True,
        locked_port_outside_contract=True,maximum_additional_stack_bytes=4,wrapper_extra_refresh_m1=20,
        final_page=0x10,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionGaugeWrapperVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
