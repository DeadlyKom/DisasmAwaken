"""Условное исполнение исходного хвоста 7497 после фактического переноса вступления."""

import json
import re
from pathlib import Path

from CheckIntro import ROOT, PC, SP, Simulator, execute, original_memory, word
from skoolkit import ROM48, ROM128
from skoolkit.simutils import D, E, R, T, get_registers


ENTRY, STOP = 0x7497, 0x74CD
PREFIX_ENTRY, PREFIX_DESTINATION = 0x7494, 0xFF01
ATTRIBUTES, SAMPLE = 0x5800, 0x8157
RETURN, INITIAL_SP = 0x3FFF, 0xBFFE


class Ports:
    def __init__(self):
        self.writes = []

    def write_port(self, registers, port, value, offset):
        self.writes.append((port, value))


class SampleMemory(list):
    def __init__(self, image):
        super().__init__(image)
        self.samples = []

    def __setitem__(self, address, value):
        if address == SAMPLE:
            self.samples.append(value)
        super().__setitem__(address, value)


def subtraction_flags(left, right, result):
    return (((result >> 8) & 0xA8) | (0x40 if result == 0 else 0) |
            (0x10 if (left & 0xFFF) < (right & 0xFFF) else 0) |
            (0x04 if ((left ^ right) & (left ^ result) & 0x8000) else 0) |
            0x02 | (left < right))


def check(image, count_base, scan, seed, entry=ENTRY, input_de=None, input_af=0xE5D7):
    memory = SampleMemory(image)
    memory[ATTRIBUTES:ATTRIBUTES + 256] = [(i * 53 + seed * 29) & 255 for i in range(256)]
    for address in set(range(count_base, count_base + 8)) | set(range(scan, scan + 7)):
        memory[address] = ((address * 19 + seed * 37) ^ (seed * 11)) & 255
    expected = memory.copy()
    expected[count_base] = count_base & 255
    for offset in range(7):
        expected[scan + offset] = expected[count_base + offset]
    expected[SAMPLE] = (expected[ATTRIBUTES + 254] >> 3) & 7
    expected[count_base] = (expected[count_base] + 255) & 255
    winner = max((count_base, *range(scan, scan + 7)), key=expected.__getitem__)
    candidate = count_base
    replacements = 0
    # Подсчёт строгих улучшений максимума, равные значения не меняют адрес кандидата.
    for address in range(scan, scan+7):
        if expected[address] > expected[candidate]:
            candidate = address
            replacements += 1
    assert candidate == winner
    result = (winner - count_base) & 65535
    flags = subtraction_flags(winner, count_base, result)
    for index, value in enumerate((count_base, scan, count_base, count_base), 1):
        word(expected, INITIAL_SP - 2 * index, value)

    sim = Simulator(memory)
    ports = Ports()
    sim.set_tracer(ports)
    initial = get_registers({'PC': entry, 'SP': INITIAL_SP, 'HL': count_base,
                             'DE': scan if input_de is None else input_de,
                             'AF': input_af, 'BC': 0xCA35, 'IY': 0x5C3A,
                             'I':seed,'R':(seed*73+count_base)&255,
                             '^HL': 0x1357, '^DE': 0x2468, '^BC': 0x369C, '^AF': 0x55AA},
                            {'im':seed%3,'iff':seed&1}, False)
    sim.registers[:] = initial
    if entry == PREFIX_ENTRY:
        expected_entry = initial.copy()
        expected_entry[D], expected_entry[E] = divmod(scan, 256)
        expected_entry[PC] = ENTRY
        expected_entry[R] = (initial[R] & 0x80) | ((initial[R] + 1) & 0x7F)
        expected_entry[T] += 10
        sim.run()
        assert list(sim.registers) == list(expected_entry)
    for _ in range(5000):
        if sim.registers[PC] == RETURN:
            break
        sim.run()
    else:
        raise AssertionError('условный вход 7497 не вернулся')
    registers = sim.registers
    assert memory == expected, (count_base, scan, seed, 'RAM')
    assert registers[:10] == [result & 255, flags, 0, 0, count_base >> 8, count_base & 255,
                               result >> 8, result & 255, count_base >> 8, count_base & 255]
    assert registers[10:12] == initial[10:12] and registers[16:24] == initial[16:24]
    assert registers[SP] == INITIAL_SP + 2
    # Проверка R по двум циклам и числу выполненных замен адреса максимума.
    extra_m1 = {ENTRY:0,PREFIX_ENTRY:1,0x7491:3,0x7492:2}[entry]
    m1 = 2620+2*replacements+extra_m1
    assert registers[R] == (initial[R]&128)|((initial[R]+m1)&127),(entry,replacements,registers[R])
    assert all(registers[index]==initial[index] for index in (14,26,27))
    assert memory.samples == [(value >> 3) & 7 for value in expected[ATTRIBUTES:ATTRIBUTES + 255]]
    assert ports.writes == [(((result & 255) << 8) | 0xFE, result & 255)]


class TailReadMemory(list):
    registers = None

    def __init__(self, image):
        super().__init__(image)
        self.tail_reads = []

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.registers is not None and isinstance(address, int) and 0x7488 <= address < ENTRY:
            self.tail_reads.append((self.registers[PC], address, value))
        return value


def check_preceding_bytes(image):
    prefix = b'\x80' + bytes(28) + bytes.fromhex('EF BB BB B0 00 00 FF C1 FF 87 FE FF')
    assert bytes(image[0x746B:PREFIX_ENTRY]) == prefix
    disk_dir = ROOT / 'Tools/Disasm/Disk'
    disk = (disk_dir / 'original.trd').read_bytes()
    manifest = json.loads((disk_dir / 'Manifest.json').read_bytes())
    allocation = next(row['offset'] for row in manifest['entries'] if row['slot'] == 3)
    assert len(disk) == 655360
    for displacement in (0, 29):
        sequence = prefix[displacement:]
        expected_offset = allocation + 0x2C6B + displacement
        assert disk.find(sequence) == disk.rfind(sequence) == expected_offset
    calculator_reads = [(0x336A, address) for address in (0x7489, 0x748A, 0x748B, 0x748C,
                                                          0x748E, 0x748F, 0x7490, 0x7491)]
    calculator_reads += [(0x33D0, 0x7492), (0x33D7, 0x7492)]
    calculator_reads += [(0x33E8, address) for address in range(0x7493, ENTRY)]
    expected_reads = [(pc, address, image[address])
                      for pc, address in [(0x7488, 0x7488), *calculator_reads]]
    rom_profiles = []
    for rom_path in (ROM48, ROM128[1]):
        rom = Path(rom_path).read_bytes()
        sizes = (0, 1, 2, 8)
        for size in sizes:
            memory = TailReadMemory(image)
            memory[:0x4000] = rom
            word(memory, 0x5C63, 0xA000)
            word(memory, 0x5C65, 0xA000 + 5 * size)
            word(memory, 0x5C3D, 0xBFF0)
            word(memory, 0xBFF0, RETURN)
            for index in range(size):
                start = 0xA000 + 5 * index
                memory[start:start + 5] = [0, 0, index + 1, 0, 0]
            simulator = Simulator(memory, {'PC': 0x7488, 'SP': INITIAL_SP, 'IY': 0x5C3A, 'HL': 0xFF00})
            memory.registers = registers = simulator.registers
            for steps in range(10000):
                if registers[PC] == 8:
                    break
                simulator.run()
            else:
                raise AssertionError('Принудительный вход #7488 не достиг ошибки ROM')
            assert steps == 8083 and memory.tail_reads == expected_reads
            error_address = word(memory, registers[SP])
            assert error_address == 0x31AE and memory[error_address] == 5
            assert word(memory, 0x5C65) == 0xA000 + 5 * size + 30

        suffix_profiles = []
        for address, delta in ((0x748E, 2), (0x748F, 2), (0x7490, 0), (0x7493, 0)):
            memory = image.copy()
            memory[:0x4000] = rom
            simulator, steps = execute(memory, {'PC': address, 'IY': 0x5C3A, 'HL': 0xFF00},
                                       stop=PREFIX_ENTRY, limit=400)
            assert simulator.registers[SP] == INITIAL_SP + delta
            suffix_profiles.append(dict(entry=address, sp_delta=delta, steps=steps))
        rom_profiles.append(dict(rom=Path(rom_path).name, initial_number_counts=sizes,
                                 calculator_steps_to_rst08=8083, rom_error_address=0x31AE,
                                 rom_error_byte=5, suffix_entries_at_7494=suffix_profiles))

    for entry in (0x7491, 0x7492):
        for value in range(256):
            check(image, 0xFF00, PREFIX_DESTINATION, value & 31, entry,
                  input_de=0x2468, input_af=(value << 8) | (value ^ 0xA5))
    return dict(unknown_start=0x746B, unknown_end_exclusive=PREFIX_ENTRY,
                original_image_matches=dict(full_range=1, final_12_bytes=1),
                rom_profiles=rom_profiles,
                calculator_reads=[dict(pc=pc, address=address, value=value)
                                  for pc, address, value in expected_reads],
                add_and_compare_entry_cases=512, natural_execution_proved=False)


def check_displacement_alias(image, original_code, prefix=b''):
    # Вывод модельной базы из совпадения адреса записи и операнда DD 34 d.
    original_code = prefix + original_code
    displacement = original_code.index(bytes.fromhex('DD 34 00')) + 2
    alternative = SAMPLE - displacement
    assert alternative == 0x813B - len(prefix) and original_code[displacement] == 0
    assert bytes(image[alternative:alternative + len(original_code)]) != original_code
    base = PREFIX_DESTINATION - 1 if prefix else 0x9000
    cases = 0
    for color in range(8):
        for kinds in (1, 2, 3):
            papers = [(color + index % kinds) & 7 for index in range(255)]
            memory = SampleMemory(image)
            memory[alternative:alternative + len(original_code)] = original_code
            memory[ATTRIBUTES:ATTRIBUTES + 255] = [
                (paper << 3) | (index & 0xC7) for index, paper in enumerate(papers)]
            memory[ATTRIBUTES + 255] = ((color + 4) & 7) << 3
            memory[base:base + 8] = b'\xFE' * 8
            word(memory, INITIAL_SP, RETURN)
            sim = Simulator(memory, {'PC': alternative, 'SP': INITIAL_SP,
                                     'HL': base, 'DE': 0x2468 if prefix else base + 1})
            ports = Ports()
            sim.set_tracer(ports)
            sim.run(alternative, RETURN)
            expected = bytes(papers.count(paper) for paper in range(8))
            winner = expected.index(max(expected))
            assert bytes(memory[base:base + 8]) == expected and memory.samples == papers
            assert memory[SAMPLE] == papers[-1] and sim.registers[SP] == INITIAL_SP + 2
            assert ports.writes == [((winner << 8) | 0xFE, winner)]
            cases += 1
    return dict(model_entry=alternative, displacement_offset=displacement, cases=cases,
                counter_address=base, original_prefix_used=bool(prefix),
                expected_histogram_and_first_maximum_proved=True, original_code_present_at_model_entry=False,
                relocation_or_original_use_proved=False)


def main():
    image = original_memory()
    expected = bytes(image[0x8F97:0x8FCD])
    assert expected == bytes.fromhex(
        'E5 D5 E5 E5 01 07 00 75 ED B0 06 FF 21 00 58 DD E1 7E 1F 1F 1F E6 07 32 57 81 '
        'DD 34 00 23 10 F1 D1 E1 06 07 1A BE 30 02 5D 54 23 10 F7 E1 B7 EB ED 52 7D D3 FE C9')
    execute(image, {'PC': 0x651D}, stop=0x6528)
    assert bytes(image[ENTRY:STOP]) == expected
    assert bytes(image[PREFIX_ENTRY:ENTRY]) == b'\x11\x01\xFF'
    regions = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    branch = re.compile(r'^(?:CALL|JR|JP|DJNZ) (?:[A-Z]+,\s*)?#([0-9A-F]{4})$')
    for region in regions:
        if region['name'] not in ('Intro', 'IntroUnpack'):
            continue
        for row in region['instructions']:
            if region['name'] == 'IntroUnpack' and ENTRY <= row['address'] < STOP:
                continue
            match = branch.fullmatch(row['operation'])
            if match:
                target = int(match[1], 16)
                assert not 0x746B <= target < STOP and not 0x8F6B <= target < 0x8F94
    cases = 0
    for low in (0, 1, 7, 31, 63, 127, 247, 248):
        base = 0x9000 + low
        for scan in (base - 1, base, base + 1, 0x9200):
            for seed in range(32):
                check(image, base, scan, seed)
                cases += 1
    prefix_cases = 0
    for base in (0x9000, 0x9001, 0xFEF9, 0xFF00, 0xFF01, 0xFF02, 0xFF08, 0xFFF8):
        for seed in range(32):
            check(image, base, PREFIX_DESTINATION, seed, PREFIX_ENTRY, input_de=0x2468)
            prefix_cases += 1
    report = dict(passed=True, total_cases=cases, entry=ENTRY, physical_offset=0x2C97,
                  bytes=STOP - ENTRY, input_attributes=255, sample_destination=SAMPLE,
                  exact_R_for_conditional_original_placement=True,
                  M1_formula='2620+2*strict_maximum_replacements+entry_prefix_M1',
                  I_IM_IFF_preserved_in_conditional_profiles=True,
                  actual_index_displacement=0, direct_game_entry_found=False,
                  prefix=dict(entry=PREFIX_ENTRY, destination=PREFIX_DESTINATION, cases=prefix_cases,
                              exact_registers_at_scan_entry=True,
                              direct_game_entry_found=False),
                  preceding_unknown_bytes=check_preceding_bytes(image),
                  inferred_displacement_alias=check_displacement_alias(image, expected),
                  inferred_prefix_and_displacement_alias=check_displacement_alias(
                      image, expected, bytes(image[PREFIX_ENTRY:ENTRY])),
                  original_relocation_executed=True, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/IntroAttributeCountTailVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
