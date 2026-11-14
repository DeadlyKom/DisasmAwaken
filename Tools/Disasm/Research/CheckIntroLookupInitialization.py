"""Композиция генераторов и первого вывода табличного эффекта."""
from itertools import product
from random import Random
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckIntroScrolledFrame import advance
from CheckIntroScrolledInitialization import IntroPorts
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put
from CheckMusicGateTicks import xor_flags


def main():
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    flat = original_memory()
    rng = Random(0x6C9C)
    cases = 0
    for phase, stack, time in product((0, 128), (0x5FFE, 0x7DF0), (0, 69880)):
        banks = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        texture = rng.randbytes(0x1300)
        banks[4][:len(texture)] = texture
        memory = RecordedBanks(banks=banks, out7ffd=17)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(17)
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x67F2] = phase
        memory[stack], memory[stack + 1] = 255, 63
        source = rng.randbytes(256)
        put(memory, 0x6400, source)
        states = []
        for index in range(3):
            addr = 0x6C8A + index * 6
            state = tuple(int.from_bytes(bytes(memory[pos:pos + 2]), 'little') for pos in range(addr, addr + 6, 2))
            for _ in range(40):
                state = advance(*state)
            states.append(state)
        cursor = (memory[0x6C12] + 120) & 255
        sim = Simulator(memory)
        trace = IntroPorts(sim)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6C9C, 'SP': stack, 'IY': 0x5C3A, '^AF':0xA55A}, None, False)
        initial[25], initial[26], initial[27] = time, 1, 1
        sim.registers[:] = initial
        sim.run(0x6C9C, 0x3FFF, interrupts=True)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == stack + 2
        assert bytes(memory[0xAD00:0xC000]) == texture
        chain = bytes(flat[0x6D78:0x6D7E]) * 64
        assert bytes(memory[0x9100:0x9282]) == chain[:-1] + bytes.fromhex('c3ed6b')
        sums = bytearray(flat[0x6D7E:0x6D8D] * 256)
        sums[-2] = 0xC9
        assert bytes(memory[0x9900:0xA800]) == sums
        transfer = bytes(byte for row, column in product(range(38), range(8))
                         for byte in (0xE1, 0x22, column * 2, 0xC0 + row))
        assert bytes(memory[0xA800:0xACC3]) == transfer + bytes.fromhex('c3bc6b')
        for index, step in enumerate((9, 6, 8, 5)):
            addr = 0x9400 + 256 * index
            assert bytes(memory[addr:addr + 256]) == bytes(source[(index * step) & 255] >> 2 for index in range(256))
        assert bytes(memory[0x9800:0x9900]) == bytes(index >> 4 for index in range(256))
        pointers = bytes(0x89 + (min(0x7F, max(0x70, 0xB0 - (row + 1) // 2 - col)) - 0x70) // 2
                         for row, col in product(range(256), range(16)))
        assert bytes(memory[0xF000:0x10000]) == pointers
        for index, addr in enumerate((0x6BA2, 0x6BA6, 0x6BA9)):
            assert memory[addr] == states[index][0] >> 8
            state_address = 0x6C8A + 6 * index
            assert bytes(memory[state_address:state_address + 6]) == b''.join(
                word.to_bytes(2, 'little') for word in states[index])
        assert memory[0x6C12] == cursor and memory[0x6BAC] == source[cursor] >> 1
        assert memory[0x6993] == 0x88
        matrix = list(flat[0x6993 + (8 if phase else 0):0x699B + (8 if phase else 0)])
        if not phase:
            matrix[0] = 0x88
        for row, col in product(range(8), repeat=2):
            assert memory[0x8989 + row * 256 + col] == ((matrix[col] & 240) | (matrix[row] & 15))
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 17)]
        selected = 0x61C0 if phase else 0x60C0
        last_word = memory[selected + 62] + 256 * memory[selected + 63]
        assert sim.registers[:12] == [phase, xor_flags(phase), 0x69, 0x9B, 0x61, 0,
                                      last_word >> 8, last_word & 255, 0, 0, 0x5C, flat[0x69A2] & 15]
        assert sim.registers[16:24] == [0xA5, 0x5A, 0, 0, 0x91, 0x91, 0x69, 0x29]
        cases += 1
    result = dict(passed=True, total_cases=cases, generated_chains=3, exact_pointer_bytes=4096,
                  phase_updates_per_case=40, actual_rom_executed=True, assembly_executed=False,
                  output_registers_compared=True, nonzero_alternate_AF_preserved=True)
    (ROOT / 'Tools/Disasm/Reports/IntroLookupInitializationVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
