"""Вход 6B93 до последовательной передачи в RenderLookupTexture."""
from itertools import product
import json

from CheckIntro import ROOT, original_memory
from CheckIntroScrolledFrame import advance
from CheckIntroWaitInterrupt import Keyboard
from CheckMusic import PC, SP, Simulator, get_registers


def main():
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    flat = original_memory()
    count = 0
    for warmup, cursor, signs in product((1, 2, 3, 161), (0, 253, 254, 255), range(8)):
        memory = flat.copy()
        memory[:0x4000] = rom
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x6C22], memory[0x6C2E], memory[0x6C3F] = warmup, 17, 39
        memory[0x6C12], memory[0x6C13] = cursor, 0x64
        outcomes = []
        for index in range(3):
            address = 0x6C8A + 6 * index
            phase = 0x9876 if signs & (1 << index) else 0x1234
            words = phase, 0x0142, 0x0030 + index
            memory[address:address + 6] = b''.join(word.to_bytes(2, 'little') for word in words)
            outcomes.append(advance(*words))
        selected = 39 + 18 // 2 if warmup > 2 else 56 + flat[0x6C62]
        simulator = Simulator(memory)
        ports = Keyboard()
        simulator.set_tracer(ports)
        initial = get_registers({'PC': 0x6B93, 'SP': 0x5FFE, 'IY': 0x5C3A, 'IX': 0xABCD}, None, False)
        initial[27] = 1
        simulator.registers[:] = initial
        simulator.run(0x6B93, 0x6B9C, interrupts=True)
        r = simulator.registers
        context = (warmup, cursor, signs)
        assert r[PC] == 0x6B9C and r[SP] == 0x5FFE and r[26] == 1, context
        assert memory[0x6C22] == max(1, warmup - 1)
        assert memory[0x6C2E] == (18 if warmup > 2 else 17)
        assert memory[0x6C3F] == (39 if warmup > 2 else 0)
        assert memory[0x6BB2] + 256 * memory[0x6BB3] == 0xF000 + 16 * selected
        new_cursor = (cursor + 3) & 255
        assert memory[0x6C12:0x6C14] == [new_cursor, 0x64]
        assert memory[0x6BAC] == memory[0x6400 + new_cursor] >> 1
        for index, (address, target) in enumerate(zip(range(0x6C8A, 0x6C9C, 6), (0x6BA2, 0x6BA6, 0x6BA9))):
            words = outcomes[index]
            assert bytes(memory[address:address + 6]) == b''.join(word.to_bytes(2, 'little') for word in words)
            assert memory[target] == words[0] >> 8
        assert len(ports.reads) == 8 and not ports.writes and memory[0x5C78:0x5C7B] == [1, 0, 0]
        count += 1
    report = dict(passed=True, total_cases=count, actual_rom_executed=True,
                  untouched_outer_stack_pointer=True, stopped_before_renderer=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroLookupFrameEntryVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
