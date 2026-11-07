"""Композиционная проверка подготовки прокрутки и настоящего вывода с IM 1."""
from itertools import product
from random import Random
import hashlib
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import xor_flags
from CheckScreenUpdate import PortTrace


class IntroPorts(PortTrace):
    def read_port(self, registers, port):
        return 255


def main():
    rom_path = ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom'
    rom = rom_path.read_bytes()
    assert hashlib.sha256(rom).hexdigest() == 'd55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42'
    flat = original_memory()
    rng = Random(0x66FB)
    cases = 0
    for phase, tstates, stack in product((0, 1, 128, 255), (0, 100, 69880), (0x5FFE, 0x7DF0)):
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
            source = bytes((value + 128) & 255 for value in texture[row * 64:(row + 1) * 64])
            expected.extend(source * 4)
        matrix = flat[0x6993 + (8 if phase else 0):0x699B + (8 if phase else 0)]
        for row, col in product(range(8), repeat=2):
            expected[0x80 + 256 * row + col] = (matrix[col] & 240) | (matrix[row] & 15)
        chain = bytes(flat[0x6722:0x6729]) * 64 + bytes.fromhex('c3f366')
        writer = bytes(byte for row, col in product(range(8), range(4))
                       for byte in (0xE1, 0x22, 0x80 + 2 * col, 0x80 + row))
        sim = Simulator(memory)
        trace = IntroPorts(sim)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x66FB, 'SP': stack, 'IY': 0x5C3A, 'IX': 0xABCD,
                                 '^AF': 0xA55A, '^HL': 0x1234, '^BC': 0x5678, '^DE': 0x9ABC}, None, False)
        initial[25], initial[26], initial[27] = tstates, 1, 1
        sim.registers[:] = initial
        sim.run(0x66FB, 0x3FFF, interrupts=True)
        r = sim.registers
        assert r[PC] == 0x3FFF and r[SP] == stack + 2 and r[26] == 1
        assert bytes(memory[0x7E00:0x7FC3]) == chain
        assert bytes(memory[0x68A9:0x6929]) == writer
        assert bytes(memory.banks[2]) == expected
        for index in range(38):
            for base in (0x6000, 0x6100):
                address = base + index * 4
                assert memory[address] + 256 * memory[address + 1] == 0x80C0 + index * 256
        assert (memory[0x692A], memory[0x692B]) == (stack & 255, stack >> 8)
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 17)]
        assert bytes(memory.banks[4][:4096]) == texture
        assert r[0:12] == [phase, xor_flags(phase), 0x69, 0x9B, 0x61, 0,
                           expected[0x787], expected[0x786], 0, 0, 0x5C, flat[0x69A2] & 15]
        assert r[16:24] == [0xA5, 0x5A, 0, 0, 0x88, 0x88, 0x69, 0x29]
        assert r[14] == initial[14] and r[27] == 1
        frame_count = int.from_bytes(bytes(memory[0x5C78:0x5C7B]), 'little')
        assert frame_count != int.from_bytes(bytes(flat[0x5C78:0x5C7B]), 'little')
        cases += 1
    result = dict(passed=True, total_cases=cases, rom_sha256=hashlib.sha256(rom).hexdigest(),
                  generated_sampler_bytes=451, generated_writer_bytes=128, expanded_bytes=16384,
                  exact_output_bank=True, registers_except_r_compared=True, genuine_rom_interrupts=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroScrolledInitializationVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
