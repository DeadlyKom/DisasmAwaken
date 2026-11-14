"""Вход 6B93 до рендера, два IY и перенос FRAMES настоящим ROM.

Документация: ../../../Docs/IntroGeneratedEffects.md#контекст-irq-кадра-табличного-эффекта
"""
from hashlib import sha256
from itertools import product
import json

from CheckIntro import ROOT, original_memory
from CheckIntroScrolledFrame import advance
from CheckIntroWaitInterrupt import Keyboard
from CheckMusic import PC, SP, Simulator, get_registers
from CheckStationFlightCycle import DISK, ENTRIES


class FrameCPU(Simulator):
    def accept_interrupt(self, registers, memory, prev_pc):
        if super().accept_interrupt(registers, memory, prev_pc):
            self.interrupts.append(prev_pc)
            return True
        return False


def main():
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    flat = original_memory()
    assert sha256(rom).hexdigest() == 'd55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42'
    code = bytes(flat[0x6B93:0x6B9C])
    offset = ENTRIES[3]['offset'] + 0x893
    assert code == DISK[offset:offset + len(code)]
    count = 0
    for warmup, cursor, signs, iy, frames in product((1, 2, 3, 161), (0, 253, 254, 255), range(8), (0x5C3A, 0x5C0F), (0, 0xFFFF)):
        memory = flat.copy()
        memory[:0x4000] = rom
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x5C78:0x5C7B] = frames.to_bytes(3, 'little')
        memory[0x5C4F] = 0x63
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
        simulator = FrameCPU(memory, config={'frame_duration':69888, 'int_active':36})
        simulator.interrupts = []
        ports = Keyboard()
        simulator.set_tracer(ports)
        initial = get_registers({'PC': 0x6B93, 'SP': 0x5FFE, 'IY': iy, 'IX': 0xABCD, 'I':0x3C,
            '^HL':0x1357, '^DE':0x2468, '^BC':0x369A, '^AF':0xA55A}, {'im':1, 'iff':0}, False)
        simulator.registers[:] = initial
        simulator.run(0x6B93, 0x6B9C, interrupts=True)
        r = simulator.registers
        context = (warmup, cursor, signs, iy, frames)
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
        # Проверка регистров последнего AdvanceParameters и табличного SRL.
        phase_before = 0x9876 if signs & 4 else 0x1234
        delta = (-0x32 if signs & 4 else 0x32) & 65535
        sample = memory[0x6400 + new_cursor]
        half = sample >> 1
        flags = (half & 0xA8) | (0x40 if half == 0 else 0) | (4 if half.bit_count() % 2 == 0 else 0) | (sample & 1)
        assert r[:8] == [half, flags, phase_before >> 8, phase_before & 255, delta >> 8, delta & 255, 0x64, new_cursor], context
        assert all(r[index] == initial[index] for index in (*range(8,12),14,*range(16,24),27)), context
        assert simulator.interrupts == [0x6A14], context
        assert ports.reads == [0xFEFE,0xFDFE,0xFBFE,0xF7FE,0xEFFE,0xDFFE,0xBFFE,0x7FFE] and not ports.writes, context
        # Проверка переноса счётчика по фактическому IY обработчика ROM.
        expected_frames = 1 if frames == 0 else 0x10000 if iy == 0x5C3A else 0
        assert int.from_bytes(memory[0x5C78:0x5C7B], 'little') == expected_frames, context
        assert memory[0x5C4F] == 0x63 + int(frames == 0xFFFF and iy == 0x5C0F), context
        count += 1
    report = dict(passed=True, total_cases=count, actual_rom_executed=True,
                  untouched_outer_stack_pointer=True, stopped_before_renderer=True, assembly_executed=False,
                  original_entry_sha256=sha256(code).hexdigest(), rom_sha256=sha256(rom).hexdigest(),
                  tested_IY=[0x5C3A,0x5C0F], prepared_FRAMES=[0,0xFFFF],
                  exact_data_registers_and_preserved_context_compared=True,
                  exactly_one_IRQ_at_WaitInterrupt_HALT=True, IFF_after_phase_updates=1,
                  I=0x3C, IM=1, timing_and_refresh_R_proved=False,
                  natural_IY_5C0F_frame_entry_reachability_proved=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroLookupFrameEntryVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
