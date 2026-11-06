"""AAE2..AB1A, копирование исходного потока OBJECT3D с двумя видами маркеров и настоящим paging."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckScreenUpdate import PortTrace
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsPointRespawn import refresh


def packet(data, start):
    position = start + 2
    fixed = 0
    lengths = []
    while data[position] != 0:
        assert position + 4 <= len(data)
        position += 4
        fixed += 1
    position += 1
    while data[position] & 15:
        length = 1 + (data[position] & 15)
        assert position + length <= len(data)
        lengths.append(length)
        position += length
    position += 1
    return bytes(data[start:position]), fixed, lengths


def fixture_packet(fixed=0, lengths=(), terminal=0, tag=1, header=0):
    data = bytearray((header, header ^ 255))
    for index in range(fixed):
        data.extend((tag, (index * 73) & 255, (index * 109) & 255, (index * 151) & 255))
    data.append(0)
    for length in lengths:
        data.append((terminal & 240) | length)
        data.extend((index * 73 + length) & 255 for index in range(length))
    data.append(terminal & 240)
    return bytes(data)


def main():
    flat = flat_action()
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    baseline[4][:len(objects)] = objects
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, flag_counts, touched, fixtures = Counter(), Counter(), set(), set()
    native = []
    for index in range(0, 256, 2):
        pointer = flat[0x9E00 + index] + 256 * flat[0x9E01 + index]
        raw, fixed, lengths = packet(objects, pointer - 0xC000)
        native.append(dict(index=index, pointer=pointer, length=len(raw), fixed_records=fixed, variable_lengths=lengths,
                           terminal=raw[-1], destination_end=0x9F1C + len(raw)))
    assert len(native) == 128 and len({r['pointer'] for r in native}) == 95
    assert max(r['length'] for r in native) == 238 and max(r['destination_end'] for r in native) < 0xA100

    def check(index=0, bc=0x369C, flags=255, page=16, payload=None):
        nonlocal touched, fixtures
        memory.recording = False
        for bank, offset in touched | fixtures:
            memory.banks[bank][offset] = baseline[bank][offset]
        memory.out7ffd(page)
        fixtures = set()
        if payload is not None:
            # Синтетический поток заменяет только данные по уже существующему штатному указателю, новые игровые адреса не назначаются.
            pointer = native[0]['pointer']
            for i, value in enumerate(payload):
                offset = pointer - 0xC000 + i
                memory.banks[4][offset] = value
                fixtures.add((4, offset))
            for address, value in ((0x9E00 + index, pointer & 255), (0x9E00 + ((index + 1) & 255), pointer >> 8)):
                memory[address] = value
                fixtures.add((2, address & 0x3FFF))
        pointer = memory[0x9E00 + index] + 256 * memory[0x9E00 + ((index + 1) & 255)]
        raw, fixed, lengths = packet(memory.banks[4], pointer - 0xC000)
        serial = counts.total()
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        initial = get_registers({'AF': (serial & 255) * 256 + flags, 'HL': ((serial * 73) & 0xFF00) | index,
            'DE': 0x2468, 'BC': bc, '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xAAE2}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        wanted = list(initial)
        expected = [bytearray(b) for b in memory.banks]
        writes = []
        def byte(address, value):
            expected[2][address & 0x3FFF] = value
            writes.append((2, address & 0x3FFF, value))
        def word(address, value):
            byte(address, value & 255)
            byte(address + 1, value >> 8)
        # Расчёт конечного счётчика, любой непустой переменный блок устанавливает BC в нуль до последнего LDI.
        final_bc = 65535 if lengths else (bc - len(raw)) & 65535
        for return_address, saved_bc in ((0xAAED, bc), (0xAB1A, final_bc)):
            word(0xBFFC, return_address)
            word(0xBFFA, saved_bc)
        for i, value in enumerate(raw):
            byte(0x9F1C + i, value)
        source_end, destination_end = pointer + len(raw), 0x9F1C + len(raw)
        wanted[0:2] = [16, 0x40 | (4 if final_bc else 0)]
        for position, value in ((2, final_bc), (4, destination_end), (6, source_end)):
            wanted[position:position + 2] = [value >> 8, value & 255]
        m1 = 37 + 12 * fixed + sum(7 + 2 * length for length in lengths)
        wanted[SP], wanted[PC], wanted[15] = 0xC000, 0x3FFF, refresh(initial[15], m1)
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        for _ in range(4096):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('конец копирования', index, fixed, lengths))
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (index, bc, payload is not None, fixed, lengths,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes), ('RAM', index)
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 16)] and memory.o7ffd == 16
        assert memory.banks[0] == baseline[0]
        touched = {(bank, offset) for bank, offset, value in memory.writes}
        counts['synthetic' if payload is not None else 'native_pointer'] += 1
        flag_counts[str(wanted[1])] += 1
    # Проверка всех штатных чётных указателей оригинального OBJECT3D и четырёх незаблокированных конфигураций банка 0.
    for row in native:
        for bc in (0, 1, 65535, row['length']):
            for page in (0, 8, 16, 24):
                check(row['index'], bc, page=page)
    # Проверка всех слов BC при отсутствии переменных блоков, включая единственный конечный BC=0.
    empty = fixture_packet(terminal=240)
    for bc in range(65536):
        check(bc=bc, flags=bc & 255, payload=empty)
    # Проверка всех входных индексов, включая FF с оборачиванием второго чтения, только на явно синтетических указателях.
    profiles = (fixture_packet(), fixture_packet(1, (1,)), fixture_packet(3, (1, 2, 15), 240),
                fixture_packet(31, (15, 15, 15), 128), fixture_packet(127))
    for index in range(256):
        for payload in profiles:
            check(index, (index * 257) & 65535, index, payload=payload)
    # Проверка всех старших тетрад заголовка и длин 1..15, ненулевой маркер с нулевой младшей тетрадой копируется целиком.
    for high in range(0, 256, 16):
        for length in range(1, 16):
            check(payload=fixture_packet(lengths=(length,), terminal=high))
    for tag in range(1, 256):
        check(payload=fixture_packet(1, tag=tag))
    for header in range(256):
        check(payload=fixture_packet(header=header))
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), final_flags=dict(flag_counts),
        method='independent_packet_parser_counter_refresh_and_physical_banked_copy_oracle',
        native_even_pointers=128, native_unique_packets=95, native_maximum_copy_bytes=238,
        native_destination_end_maximum=0xA00A, original_packet_lengths=[r['length'] for r in native],
        all_bc_words_when_no_variable_blocks=True, all_synthetic_index_bytes_including_ff=True,
        arbitrary_odd_indices_not_claimed_native=True, maximum_additional_stack_bytes=4,
        exact_registers_flags_refresh_sp=True, every_physical_ram_byte_and_write_multiplicity_checked=True,
        physical_eight_banks_and_real_selector_executed=True, exact_out_values_checked=True,
        source_and_bank0_preserved=True, terminal_high_nibble_preserved=True, no_destination_capacity_check_added=True,
        variable_record_game_meanings_proved=False, all_joint_inputs_exhausted=False,
        whole_vertex_transform_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectCopyVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in report.items() if k != 'original_packet_lengths'}, indent=2))


if __name__ == '__main__':
    main()
