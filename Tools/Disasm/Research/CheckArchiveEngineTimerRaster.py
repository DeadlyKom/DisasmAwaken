"""Проверка адреса, композиции, возврата фона и видимости цифр ENGINE."""
import json

from CheckArchiveEngineMeters import screen_offset
from CheckArchiveEngineStartup import ENGINE, call, init_prefix
from CheckFighterArchiveConsumer import word
from CheckStationFlightCycle import payload, put
from TraceFlight import A, ROOT
from skoolkit.simutils import B, C, D, E, H, L


SCENE = 0x7700
STRIDE = 92
FONT = ENGINE[0x0B28:0x0C68]


def check_multiply(cpu):
    registers = cpu.registers
    words = {0, 1, 92, 0x80, 0x100, 0x8000, 0xFFFF}
    words.update(index * 257 ^ 0x53E1 for index in range(256))
    for left in range(256):
        for right in words:
            registers[A] = left
            registers[D], registers[E] = divmod(right, 256)
            registers[C] = 0xA5
            call(cpu, 0x502D)
            assert registers[H] * 256 + registers[L] == left * right & 0xFFFF
            assert registers[D] * 256 + registers[E] == right << 8 & 0xFFFF
            assert (registers[A], registers[B], registers[C]) == (0, 0, 0xA5)
    return 256 * len(words)


def locate(cpu, x, y):
    memory = cpu.memory
    memory[0x4A55] = y
    put(memory, 0x4A57, (SCENE + x).to_bytes(2, 'little'))
    call(cpu, 0x4AF2)
    base = SCENE + (y + 189) * STRIDE + x + 15
    assert word(memory, 0x4C88) == base
    assert cpu.registers[H] * 256 + cpu.registers[L] == base
    return base


def draw(cpu, base, seconds, original):
    memory = cpu.memory
    digits = divmod(seconds, 10)
    memory[0x4C8A] = 16 * digits[0] + digits[1]
    expected, saved = bytearray(original), bytearray()
    for row in range(16):
        offset = base - SCENE - row * STRIDE
        for column, digit in enumerate(digits):
            source = 32 * digit + 2 * row
            mask, pixels = FONT[source:source + 2]
            saved.append(original[offset + column])
            expected[offset + column] = (original[offset + column] & mask) | pixels
    call(cpu, 0x4A95)
    assert bytes(memory[0x4C68:0x4C88]) == saved
    assert bytes(memory[SCENE:SCENE + len(original)]) == expected
    return expected


def main():
    cpu = init_prefix(0)
    memory = cpu.memory
    multiply_cases = check_multiply(cpu)
    for y in range(12):
        for x in range(59):
            locate(cpu, x, y)

    original = payload(30)
    put(memory, SCENE, original)
    call(cpu, 0x492D)
    draw_cases = 0
    for y in (0, 11):
        for x in (0, 29, 58):
            base = locate(cpu, x, y)
            for seconds in range(100):
                expected = draw(cpu, base, seconds, original)
                if seconds == 89:
                    call(cpu, 0x4974)
                    for row in range(16):
                        screen = screen_offset(2 + row, 15)
                        source = base - SCENE - row * STRIDE
                        assert bytes(memory.banks[7][screen:screen + 2]) == expected[source:source + 2]
                call(cpu, 0x4B0B)
                assert bytes(memory[SCENE:SCENE + len(original)]) == original
                draw_cases += 1
    result = dict(passed=True, multiply_cases=multiply_cases, timer_address_cases=708,
                  timer_draw_and_restore_cases=draw_cases, font_bytes=len(FONT),
                  first_screen_row=2, last_screen_row=17, screen_columns=[15, 16],
                  integrated_viewport_cases=6, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveEngineTimerRasterVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
