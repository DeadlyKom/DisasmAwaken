"""Построение столбцового эффекта до возврата после вывода атрибутов."""
from itertools import product
from random import Random
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckIntroScrolledInitialization import IntroPorts
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import xor_flags


def main():
    flat = original_memory()
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    rng = Random(0x6AC1)
    cases = 0
    for phase, stack, time in product((0, 128), (0x5FFE, 0x7DF0), (0, 69880)):
        banks = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        texture = rng.randbytes(4096)
        banks[4][:4096] = texture
        memory = RecordedBanks(banks=banks, out7ffd=17)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(17)
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x67F2] = phase
        memory[stack], memory[stack + 1] = 255, 63
        expected = bytearray()
        for row in range(64):
            next_row = (row + 1) % 64
            samples = []
            for column in range(64):
                next_column = (column + 1) % 64
                samples.append((texture[64 * row + column] + texture[64 * row + next_column]
                                + texture[64 * next_row + column] + texture[64 * next_row + next_column]
                                + 64) & 255)
            expected.extend(bytes(samples) * 4)
        sim = Simulator(memory)
        trace = IntroPorts(sim)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6AC1, 'SP': stack, 'IY': 0x5C3A}, None, False)
        initial[25], initial[26], initial[27] = time, 1, 1
        sim.registers[:] = initial
        sim.run(0x6AC1, 0x3FFF, interrupts=True)
        context = (phase, stack, time)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == stack + 2, context
        assert bytes(memory.banks[2]) == expected, context
        assert bytes(memory[0xD000:0xD641]) == bytes(flat[0x6B5A:0x6B73]) * 64 + b'\xC9'
        for row in range(16):
            table = []
            for column in range(96):
                high = ((0xD800 + (256 - 5 * row) * column) & 65535) >> 8
                table.append(high if 0xD8 <= high <= 0xE7 else 0)
            start = 0xD840 + row * 256
            assert bytes(memory[start:start + 96]) == bytes(table)
        for page in range(0xDA, 0xFA):
            start = (page << 8) + 0xE0
            assert bytes(memory[start:start + 32]) == bytes(flat[0x6B73:0x6B93])
        assert bytes(memory[0xC000:0xC0C0]) == texture[:64] * 3
        matrix = list(flat[0x6993 + (8 if phase else 0):0x699B + (8 if phase else 0)])
        if not phase:
            matrix[0] = 0
        for row, column in product(range(8), repeat=2):
            assert memory[0xC0C0 + row * 256 + column] == (matrix[column] & 240) | (matrix[row] & 15)
        assert trace.writes == [(0x7FFD, 17), (0x7FFD, 20), (0x7FFD, 17)]
        assert memory[0x67FE] == 0 and memory[0x6993] == 0
        for index in range(38):
            for base in (0x6000, 0x6100):
                address = base + 4 * index
                assert int.from_bytes(bytes(memory[address:address + 2]), 'little') == 0xD800 + index * 256
        r = sim.registers
        assert r[0:12] == [phase, xor_flags(phase), 0x69, 0x9B, 0x61, 0,
                           memory[0xC7C7], memory[0xC7C6], 0, 0, 0x5C, flat[0x69A2] & 15], context
        assert r[16:24] == [0, 0, 0, 0, 0xC8, 0xC8, 0x69, 0x29] and r[26] == 1 and r[27] == 1
        assert int.from_bytes(bytes(memory[0x5C78:0x5C7B]), 'little') != 0
        cases += 1
    report = dict(passed=True, total_cases=cases, entire_texture_compared=True, generated_code_compared=True,
                  all_column_tables_compared=True, output_registers_compared=True, actual_rom_and_attribute_writer_executed=True,
                  assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroColumnInitializationVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
