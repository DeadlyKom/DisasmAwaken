"""Точные экранные преобразования, мигание и альтернативные клавиши RUN."""
import json

from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckStartArchiveMenu import DISK_OFFSET, FONT, FONT_BYTES, MENU_ENTRY, MENU_HALT
from CheckStationFlightCycle import DISK, put, run_to
from TraceFlight import A, H, IFF, L, PC, ROOT, SP, T, Simulator
from skoolkit.simutils import D, E


RAW = DISK[DISK_OFFSET:DISK_OFFSET + FONT + FONT_BYTES - MENU_ENTRY]
RETURN = 0x5BFF


class MenuPorts(ArchivePorts):
    pressed = ()

    def read_port(self, registers, port, offset=0):
        mask = 0
        for row, bits in self.pressed:
            if port == row:
                mask |= bits
        return mask ^ 255


def init_cpu():
    memory = ExtendedMemory()
    put(memory, MENU_ENTRY, RAW)
    cpu = Simulator(memory, {'PC': MENU_ENTRY, 'SP': 0x6790},
                    config={'fast_ldir': False, 'fast_djnz': False})
    memory.cpu = cpu
    cpu.set_tracer(MenuPorts(memory))
    return cpu


def screen_address(y, column):
    return 0x4000 + ((y & 0xC0) << 5) + ((y & 7) << 8) + ((y & 0x38) << 2) + column


def check_graphics():
    cpu = init_cpu()
    memory, registers = cpu.memory, cpu.registers
    put(memory, 0x5FFE, RETURN.to_bytes(2, 'little'))

    def call(entry):
        registers[SP], registers[PC] = 0x5FFE, entry
        run_to(cpu, RETURN)
        assert registers[SP] == MENU_ENTRY

    for y in range(192):
        for x in range(256):
            registers[D], registers[E] = y, x
            call(0x638F)
            assert registers[H] * 256 + registers[L] == screen_address(y, x // 8)
            assert registers[A] == x & 7
        for column in range(32):
            address = screen_address(y, column)
            following = screen_address(y + 1, column)
            preceding = screen_address(y - 1, column) if y else 0x3FE0 + column
            registers[H], registers[L] = divmod(address, 256)
            call(0x63AA)
            assert registers[H] * 256 + registers[L] == following
            registers[D], registers[E] = divmod(address, 256)
            call(0x63B9)
            assert registers[D] * 256 + registers[E] == following
            registers[H], registers[L] = divmod(address, 256)
            call(0x63C8)
            assert registers[H] * 256 + registers[L] == preceding

    memory.out7ffd(0x17)
    screen = memory.banks[7]
    screen[:] = b'\xA5' * len(screen)
    call(0x6144)
    assert bytes(screen) == bytes(6144) + b'\x07' * 769 + b'\xA5' * (len(screen) - 6913)
    return dict(pixel_cases=192 * 256, row_cases=192 * 32 * 3, clear_writes=6913,
                clear_last_address=0xDB00)


def check_menu_keys_and_blink():
    cpu = init_cpu()
    memory, registers = cpu.memory, cpu.registers
    run_to(cpu, MENU_HALT)

    def frame(*keys):
        cpu.tracer.pressed = keys
        assert registers[PC] == MENU_HALT and registers[IFF]
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        cpu.run()
        assert cpu.accept_interrupt(registers, memory, MENU_HALT) and registers[PC] == 0x5F5F
        run_to(cpu, MENU_HALT)
        assert registers[SP] == MENU_ENTRY

    initial = [bytes(memory.banks[page][0x8ED + 256 * row] for row in range(8)) for page in (5, 7)]
    glyph = RAW[0x3ACD:0x3AD5]
    assert memory[0x61A6] == 8
    for tick in range(1, 18):
        frame()
        assert memory[0x6189] == -tick & 7
        for page, original in zip((5, 7), initial):
            mask = glyph if ((tick - 1) // 8) % 2 == 0 else bytes(8)
            observed = bytes(memory.banks[page][0x8ED + 256 * row] for row in range(8))
            assert observed == bytes(a ^ b for a, b in zip(original, mask))

    previous = (((0xEFFE, 2),), ((0xFBFE, 1),), ((0xFBFE, 2),), ((0xFEFE, 1), (0xEFFE, 8)))
    following = (((0xEFFE, 4),), ((0xFDFE, 1),), ((0xFDFE, 2),), ((0xFEFE, 1), (0xEFFE, 16)))
    for advance, retreat in zip(following, previous):
        frame(*advance)
        assert memory[0x62C8] == 2 and memory[0x609A] == 2
        frame(*advance)
        assert memory[0x62C8] == 2
        frame()
        frame(*retreat)
        assert memory[0x62C8] == 1 and memory[0x609A] == 1
        frame(*retreat)
        assert memory[0x62C8] == 1
        frame()

    confirmations = ((0xEFFE, 1), (0xBFFE, 1), (0x7FFE, 1))
    for expected_mode, key in enumerate(confirmations, 1):
        frame((0xFDFE, 1))
        frame()
        frame(key)
        assert bytes(memory[0x62CA:0x62CC]) == b'\x55\x63'
        frame(key)
        assert memory[0x6330] == (expected_mode - 1) % 3
        frame()
        frame(key)
        assert memory[0x6330] == expected_mode % 3
        frame()
        frame((0xFDFE, 1))
        frame()
        frame(key)
        assert bytes(memory[0x62CA:0x62CC]) == b'\x39\x63' and memory[0x62C8] == 1
        frame()
    return dict(irq_blink_frames=17, blink_period_frames=8, previous_key_profiles=len(previous),
                following_key_profiles=len(following), confirm_key_profiles=len(confirmations))


def main():
    result = dict(passed=True, graphics=check_graphics(), keyboard_and_blink=check_menu_keys_and_blink(),
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveRunPrimitivesVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
