"""Сквозная проверка BuildMirroredTexture с изменённым CALL и настоящим ROM."""
from random import Random
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, execute, original_memory
from CheckIntroScrolledInitialization import IntroPorts
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put


def main():
    flat = original_memory()
    execute(flat, {'PC': 0x6C9C}, stop=0x6CF9)
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    rng = Random(0x6DB6)
    count = 0
    for case in range(12):
        banks = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
        banks[5], banks[2], banks[1] = (bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]),
                                      bytearray(flat[0xC000:]))
        memory = RecordedBanks(banks=banks, out7ffd=17)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(17)
        memory[0x5C00] = memory[0x5C04] = 255
        stack = 0x5FFE if case & 1 else 0x7DF0
        memory[stack], memory[stack + 1] = 255, 63
        source = rng.randbytes(256)
        row_bytes = rng.randbytes(608)
        put(memory, 0x6400, source)
        put(memory, 0xF500, row_bytes)
        put(memory, 0x9800, bytes(i >> 4 for i in range(256)))
        put(memory, 0x8000, rng.randbytes(4096))
        pointers = [(rng.randrange(38), rng.randrange(256)) for _ in range(2432)]
        put(memory, 0xAD00, bytes(byte for row, index in pointers for byte in (index, 0xC0 + row)))
        lookup = [((2 * (source[(3 * i) & 255] >> 2) + 2 * (source[(5 * i) & 255] >> 2)) & 255) >> 4
                  for i in range(256)]
        expected = [row_bytes[16 * row + lookup[index]] for row, index in pointers]
        mirrored = []
        for row in range(32):
            start = 0xD0 + 64 * row
            half = [(value - 0x89) & 255 for value in expected[start:start + 32]]
            mirrored.extend(half + half[::-1])
        mirrored += mirrored[::-1]
        sim = Simulator(memory)
        trace = IntroPorts(sim)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6DB6, 'SP': stack, 'IY': 0x5C3A, 'IX': 0xA55A}, None, False)
        initial[25], initial[27] = (0, 100, 69880)[case % 3], 1
        sim.registers[:] = initial
        sim.run(0x6DB6, 0x6DE6, interrupts=True)
        assert sim.registers[SP] == stack and memory[0x6BDA] == 0xC3, case
        assert bytes(memory[0x8000:0x8980]) == bytes(expected), case
        assert bytes(memory[0x9300:0x9400]) == bytes(lookup), case
        sim.run(0x6DE6, 0x3FFF, interrupts=True)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == stack + 2, case
        assert bytes(memory[0x8000:0x9000]) == bytes(mirrored) == bytes(memory.banks[4][:4096]), case
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 17)] and sim.registers[26] == 1, case
        assert int.from_bytes(bytes(memory[0x5C78:0x5C7B]), 'little') >= 1, case
        count += 1
    result = dict(passed=True, total_cases=count, real_renderer_executed=True, rom_interrupts_enabled=True,
                  sampled_bytes=2432, mirrored_bytes=4096, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroMirroredCompositionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
