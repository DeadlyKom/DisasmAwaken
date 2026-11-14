"""Исполнение трёх исходных растровых слоёв START на обеих экранных страницах."""
import json
from itertools import product

from CheckBankStripArchiveConsumer import BANK_OFFSET, FIXED_OFFSET, ExtendedMemory
from CheckInsetFrame import bitmap_address
from CheckStationFlightCycle import DISK, put, run_to
from TraceFlight import ROOT, SP, Simulator


LAYERS = ((0x6573, 0xA42E, 1), (0x657E, 0x885C, 2), (0x6585, 0x6C8A, 4))
SCREENS = (5, 7)
SENTINEL = 0x5BFF
STACK = 0x5BFC


def call(memory, entry, **registers):
    cpu = Simulator(memory, dict(registers, PC=entry, SP=STACK))
    run_to(cpu, SENTINEL)
    assert cpu.registers[SP] == STACK + 2


def original_layer(origin):
    disk_offset = FIXED_OFFSET + origin - 0x6000
    source = DISK[disk_offset:disk_offset + 0x1BD2]
    pixels = {}
    for group in range(21):
        first_line = 24 + 8 * group
        block = group * 339
        assert source[block:block + 3] == b'\x21' + (bitmap_address(first_line, 26) | 0x8000).to_bytes(2, 'little')
        for row in range(8):
            start = block + 3 + row * 42
            assert source[start] == 0xF9 and source[start + 41] == 0x24
            for word in range(10):
                offset = start + 1 + 4 * word
                assert source[offset] == 0x11 and source[offset + 3] == 0xD5
                screen_offset = bitmap_address(first_line + row, 24 - 2 * word) - 0x4000
                pixels[screen_offset] = source[offset + 1]
                pixels[screen_offset + 1] = source[offset + 2]
    assert source[-3:] == b'\xC3\x00\x00' and len(pixels) == 168 * 20
    return pixels


def main():
    bitmap_writes = 0
    attribute_writes = 0
    for (entry, origin, attribute), page in product(LAYERS, SCREENS):
        memory = ExtendedMemory()
        memory.out7ffd(0x10 | page)
        put(memory, 0x6000, DISK[FIXED_OFFSET:BANK_OFFSET])
        for screen in SCREENS:
            memory.banks[screen][:0x1B00] = bytes((i * 17 + screen) & 255 for i in range(0x1B00))
        put(memory, STACK, SENTINEL.to_bytes(2, 'little'))
        # START записывает этот адрес при подключении всех трёх слоёв.
        put(memory, origin + 0x1BD0, b'\x7A\x65')
        other = next(screen for screen in SCREENS if screen != page)
        untouched = bytes(memory.banks[other][:0x1B00])
        expected = bytearray(memory.banks[page][:0x1B00])
        pixels = original_layer(origin)
        for offset, value in pixels.items():
            expected[offset] = value
        call(memory, entry)
        assert memory.banks[page][:0x1B00] == expected, (entry, page)
        assert memory.banks[other][:0x1B00] == untouched
        assert bytes(memory[0x657B:0x657D]) == STACK.to_bytes(2, 'little')
        bitmap_writes += len(pixels)

        for row in range(3, 24):
            begin = 0x1800 + 32 * row + 6
            expected[begin:begin + 20] = bytes((attribute,)) * 20
        call(memory, 0x6552, A=attribute)
        assert memory.banks[page][:0x1B00] == expected, (attribute, page)
        assert memory.banks[other][:0x1B00] == untouched
        assert bytes(memory[0x6570:0x6572]) == STACK.to_bytes(2, 'little')
        attribute_writes += 21 * 20

    report = dict(passed=True, layers=len(LAYERS), screen_pages=SCREENS,
                  bitmap_writes=bitmap_writes, attribute_writes=attribute_writes,
                  source='original.trd', interrupts=False, native_emulator=False)
    encoded = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ArchiveStartLayerProgramsVerification.json').write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()
