"""Два отдельных входа AC38 и AC44 и настоящий селектор AB1B, включая физические банки и OUT."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from CheckScreenUpdate import PortTrace, put
from skoolkit.pagingtracer import SliceableMemory
from CheckActionApplyParameters import DESTINATIONS
from ReferenceControlsPointRespawn import refresh


class RecordedBanks(SliceableMemory):
    recording = False
    def __setitem__(self,index,value):
        bank = 5 if index<0x8000 else 2 if index<0xC000 else self.o7ffd&7
        assert index>=0x4000
        if self.recording:
            self.writes.append((bank,index&0x3FFF,value))
        super().__setitem__(index,value)


def flat_action():
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    flat = base_memory()
    flat[0x6000:0x10000] = source
    flat[0x6000:0x7F8F] = source[0x23D:0x21CC]
    return flat


def initial_registers(entry,af=0xA55A,ix=0xABCD):
    return get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
        'IX':ix,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)


def execute(simulator,initial,wanted):
    simulator.registers[:] = initial
    for _ in range(100):
        if simulator.registers[PC]==0x3FFF:
            break
        simulator.run()
    else:
        raise AssertionError(('возврат',initial[PC]))
    compared = (*range(13),14,15,*range(16,24),26,27)
    assert all(wanted[i]==simulator.registers[i] for i in compared), (initial[PC],initial[:12],
        [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])


def check_word_reader():
    memory = Memory(flat_action())
    memory[0xBFFE:0xC000] = [0xFF,0x3F]
    simulator = Simulator(memory)
    cases = 0
    def check(ix,af):
        nonlocal cases
        initial = initial_registers(0xAC38,af,ix)
        initial[14],initial[15],initial[26],initial[27] = af&255,(ix+af)&255,ix&1,ix%3
        low,high = memory[ix],memory[(ix+1)&65535]
        wanted = list(initial)
        wanted[2],wanted[6],wanted[7] = initial[3],high,low
        wanted[8],wanted[9] = ((ix+2)&65535)>>8,(ix+2)&255
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],10)
        before = list(memory)
        memory.writes = []
        memory.recording = True
        execute(simulator,initial,wanted)
        memory.recording = False
        assert memory==before and not memory.writes
        cases += 1
    # Проверка каждого IX, включая чтение слова через FFFF и продвижение через границу слова.
    for ix in range(65536):
        check(ix,(ix*73+0xA55A)&65535)
    # Проверка каждого содержимого слова отдельно от адресного набора.
    for value in range(65536):
        memory[0x4000:0x4002] = [value&255,value>>8]
        check(0x4000,value)
    return cases


def check_banked_entries():
    flat = flat_action()
    baseline = [bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5] = bytearray(flat[0x4000:0x8000])
    baseline[2] = bytearray(flat[0x8000:0xC000])
    baseline[0] = bytearray(flat[0xC000:0x10000])
    baseline[1] = bytearray(base_memory()[0xC000:0x10000])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=0x11)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    def check(entry,old,value,field=0,flags=0):
        nonlocal touched
        memory.recording = False
        for bank,index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        memory.out7ffd(old)
        data = [(73*value+17*i+field)&255 for i in range(15)]
        data[field] = value
        put(memory,0x9BA4,data)
        put(memory,0xBFFE,[0xFF,0x3F])
        initial = initial_registers(entry,(value<<8)|flags)
        initial[14],initial[15],initial[26],initial[27] = value,(value+flags)&255,value&1,old%3
        wanted = list(initial)
        if entry==0xAB1B:
            writes = [(2,0x3FFD,initial[2]),(2,0x3FFC,initial[3])]
            page = old if old&32 else value
            m1 = 6
        else:
            assert entry==0xAC44 and not old&32
            writes = [(2,0x3FFD,0xAC),(2,0x3FFC,0x49),
                (2,0x3FFB,initial[2]),(2,0x3FFA,initial[3]),
                (2,0x3FFD,0xAC),(2,0x3FFC,0x4C)]
            writes += [(5 if address<0x8000 else 2 if address<0xC000 else 0,
                        address&0x3FFF,data[index]) for index,address in DESTINATIONS]
            writes += [(0,0x2CA9,0),(0,0x2CAA,0),(0,0x2CF6,0),(0,0x2CF7,0),
                       (2,0x1B83,0),(2,0x1B82,0)]
            wanted[0:2],wanted[6:8] = [0,0x44],[0,0]
            page,m1 = 0x10,62
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],m1)
        expected = [bytearray(bank) for bank in memory.banks]
        for bank,index,new_value in writes:
            expected[bank][index] = new_value
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        execute(simulator,initial,wanted)
        memory.recording = False
        expected_port = value if entry==0xAB1B else 0x10
        assert trace.writes==[(0x7FFD,expected_port)] and memory.o7ffd==page
        assert all(a==b for a,b in zip(memory.banks,expected)) and Counter(memory.writes)==Counter(writes)
        touched = {(bank,index) for bank,index,_ in writes}
        counts[format(entry,'04X')] += 1
    # Проверка каждого A и каждого F селектора, все регистры должны сохраниться.
    for value in range(256):
        for flags in range(256):
            check(0xAB1B,0x11,value,flags=flags)
    print('Memory page all A,F complete',flush=True)
    # Проверка каждого исходного состояния 7FFD, включая аппаратную блокировку записи.
    for old in range(64):
        for value in (0,0x10,0x1F,0x20,0xFF):
            check(0xAB1B,old,value,flags=old)
    # Проверка каждого байта каждого поля у AC44, порт действительно переключает банк 1 в банк 0.
    for field in range(15):
        for value in range(256):
            check(0xAC44,0x11,value,field,flags=value)
    # Проверка всех неблокированных начальных страниц и обоих состояний ROM и экранного бита.
    for old in range(32):
        check(0xAC44,old,old,old%15,flags=old)
    return dict(counts)


def main():
    word_cases = check_word_reader()
    print('Word reader IX and contents complete',flush=True)
    banked_cases = check_banked_entries()
    report = dict(passed=True,total_cases=word_cases+sum(banked_cases.values()),
        cases_by_entry=dict(AC38=word_cases,**banked_cases),all_ix_and_word_values=True,
        every_a_f_pair_for_page_selector=True,locked_7ffd_behavior_checked=True,
        all_field_values_for_activation=True,real_out_and_physical_eight_banks=True,
        exact_registers_flags_r_and_sp=True,every_physical_ram_byte_and_write_checked=True,
        original_return_addresses_and_stack_depth_checked=True,
        full_de0a_chain_proved=False,game_field_names_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionParameterActivationVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
