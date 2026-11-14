"""IY вызова PresentAttributes из столбцового эффекта и перенос FRAMES.

Документация: ../../../Docs/IntroGeneratedEffects.md#iy-столбцового-вывода-и-перенос-frames
"""
from hashlib import sha256
from itertools import product
import json

from CheckIntro import original_memory, ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckIntroScrolledInitialization import IntroPorts
from CheckStationFlightCycle import DISK, ENTRIES
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, IYh, IYl


class IrqCPU(Simulator):
    def __init__(self, memory, stack, entry=0x6AC1):
        super().__init__(memory, dict(PC=entry, SP=stack, IY=0x5C3A), {'im':1, 'iff':1},
                         config={'frame_duration':69888, 'int_active':36})
        self.interrupts = []

    def accept_interrupt(self, registers, memory, prev_pc):
        iy = registers[IYh] * 256 + registers[IYl]
        if super().accept_interrupt(registers, memory, prev_pc):
            self.interrupts.append(dict(interrupted_instruction=prev_pc, IY=iy))
            return True
        return False


def check_initializer(entry=0x6AC1, end=0x6B5A, texture_bytes=4096):
    flat = original_memory()
    code = bytes(flat[entry:end])
    offset = ENTRIES[3]['offset']
    assert code == DISK[offset + entry - 0x6300:offset + end - 0x6300]
    assert flat[0x69A2] == DISK[offset + 0x6A2] == 0xFF
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    digest = sha256(rom).hexdigest()
    assert digest == 'd55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42'
    assert rom[0x0045:0x0048] == bytes.fromhex('fd3440')
    profiles = []
    for phase, stack, frame in product((0, 128), (0x5FFE, 0x7DF0), (0, 0xFFFF)):
        banks = [bytearray([0xA0 + index] * 16384) for index in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[4][:texture_bytes] = bytes((index * 73 + (index >> 6) * 19) & 255 for index in range(texture_bytes))
        memory = RecordedBanks(banks=banks, out7ffd=17)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(17)
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x67F2] = phase
        memory[stack], memory[stack + 1] = 255, 63
        cpu = IrqCPU(memory, stack, entry)
        cpu.set_tracer(IntroPorts(cpu))
        # Реальная подготовка без IRQ до границы, счётчик задаётся перед исследуемым HALT.
        cpu.run(entry, 0x6983)
        assert cpu.registers[IYh] * 256 + cpu.registers[IYl] == 0x5C0F
        assert cpu.registers[SP] == stack
        for index, value in enumerate(frame.to_bytes(3, 'little')):
            memory[0x5C78 + index] = value
        alias_before = memory[0x5C4F]
        memory.writes = []
        memory.recording = True
        cpu.run(0x6983, 0x3FFF, interrupts=True)
        memory.recording = False
        assert cpu.interrupts == [dict(interrupted_instruction=0x6983, IY=0x5C0F)]
        carry = frame == 0xFFFF
        assert memory[0x5C4F] == (alias_before + int(carry)) & 255
        assert bytes(memory[0x5C78:0x5C7B]) == (b'\0\0\0' if carry else b'\1\0\0')
        alias_writes = [row for row in memory.writes if row[:2] == (5, 0x1C4F)]
        assert alias_writes == ([(5, 0x1C4F, (alias_before + 1) & 255)] if carry else [])
        assert cpu.registers[SP] == stack + 2
        profiles.append(dict(phase=phase, stack=stack, IY_at_HALT=0x5C0F,
                             prepared_frames=frame, final_frames=int.from_bytes(memory[0x5C78:0x5C7B], 'little'),
                             indexed_increment_address=0x5C4F if carry else None,
                             alias_before=alias_before, alias_after=memory[0x5C4F],
                             accepted_interrupts=cpu.interrupts))
    report = dict(passed=True, total_cases=len(profiles), rom_sha256=digest, profiles=profiles,
                  original_initializer_sha256=sha256(code).hexdigest(),
                  original_69A2_byte=0xFF, actual_initializer_and_attribute_writer_executed=True,
                  IRQ_before_attribute_HALT_executed=False, real_ROM_IRQ_at_HALT_executed=True,
                  frame_counter_prepared_at_boundary=True, standard_IY_5C3A_contract_not_applicable=True,
                  natural_game_counter_carry_reachability_proved=False,
                  native_execution=False, assembly_executed=False)
    return report


def main():
    report = check_initializer()
    (ROOT / 'Tools/Disasm/Reports/IntroColumnIrqContextVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены IY=5C0F и перенос ROM INC (IY+40) в 5C4F при переполнении FRAMES.')


if __name__ == '__main__':
    main()
