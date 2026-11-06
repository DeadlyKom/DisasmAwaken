"""Фактический блок UpdateFrame исполняется с OBJECT3D в банке 4 и неизменным кодом банка 0."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckScreenUpdate import PortTrace
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import xor_flags
from ReferenceControlsPointRespawn import refresh
from ActionBank4Writes import GROUPS, records


def main():
    flat = flat_action()
    object_data = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    flow = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    writes_registry = records(flow)
    assert all(r['target_offset'] < len(object_data) for r in writes_registry)
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    baseline[4][:len(object_data)] = object_data
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, touched = Counter(), set()
    def check(which=None, value=0, page=16):
        nonlocal touched
        memory.recording = False
        for bank, index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        memory.out7ffd(page)
        for index, (source, targets) in enumerate(GROUPS):
            memory.banks[4][source - 0xC000] = value if index == which else object_data[source - 0xC000]
        initial = get_registers({'AF': 0xA5FF, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xA981}, None, False)
        initial[14], initial[15], initial[26], initial[27] = value, value, value & 1, value % 3
        wanted = list(initial)
        expected = [bytearray(b) for b in memory.banks]
        writes = []
        for source, targets in GROUPS:
            output = memory.banks[4][source - 0xC000] ^ 0x60
            for target in targets:
                expected[4][target - 0xC000] = output
                writes.append((4, target - 0xC000, output))
        # Создание эталона двух CALL и PUSH BC селектора, внешняя рамка блока не потребляется.
        for return_address in (0xA986, 0xAA8A):
            for address, word in ((0xBFFC, return_address), (0xBFFA, 0x369C)):
                for offset, byte in enumerate((word & 255, word >> 8)):
                    expected[2][(address + offset) & 0x3FFF] = byte
                    writes.append((2, (address + offset) & 0x3FFF, byte))
        last = memory.banks[4][0x1873] ^ 0x60
        wanted[0:2] = [16, xor_flags(last)]
        wanted[PC], wanted[15] = 0xAA8A, refresh(initial[15], 102)
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        for _ in range(120):
            if simulator.registers[PC] == 0xAA8A:
                break
            simulator.run()
        else:
            raise AssertionError('граница банкового блока')
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (which, value, page,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes)
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 16)] and memory.o7ffd == 16
        assert memory.banks[0] == baseline[0]
        touched = {(bank, index) for bank, index, value in memory.writes}
        counts['original_resource' if which is None else 'source_' + str(which)] += 1
    # Проверка исходного OBJECT3D и всех байтов каждого из трёх источников в четырёх конфигурациях банка 0.
    for page in (0, 8, 16, 24):
        check(page=page)
        for which in range(3):
            for value in range(256):
                check(which, value, page)
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), registered_data_writes=len(writes_registry),
        execution_boundary='A981..AA8A, previous AY and next panel update not executed',
        physical_eight_banks_and_real_selector_executed=True, exact_registers_flags_refresh_sp=True,
        every_physical_ram_byte_and_write_multiplicity_checked=True, exact_out_values_checked=True,
        object3d_slot=24, target_bank=4, action_bank0_preserved=True, maximum_additional_stack_bytes=4,
        remaining_object_byte_meanings_proved=False, whole_update_frame_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionBank4WritesVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
