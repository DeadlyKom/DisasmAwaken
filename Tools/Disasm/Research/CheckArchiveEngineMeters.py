"""Сверка растров и покадрового заполнения индикаторов ENGINE."""
import json

from CheckArchiveEngineStartup import ENGINE, RETURN, STACK, call, enter_call, init_prefix
from CheckFighterArchiveConsumer import word
from CheckStationFlightCycle import put, run_to
from TraceFlight import A, ROOT, SP
from skoolkit.simutils import D, E, H, L


def screen_offset(y, column):
    return ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | column


def check_rows(cpu):
    registers = cpu.registers
    for y in range(192):
        for column in range(32):
            address = 0xC000 + screen_offset(y, column)
            registers[D], registers[E] = divmod(address, 256)
            call(cpu, 0x501E)
            expected = 0xC000 + screen_offset(y + 1, column)
            assert registers[D] * 256 + registers[E] == expected
    return 192 * 32


def check_templates(cpu):
    memory, registers = cpu.memory, cpu.registers
    image = [ENGINE[offset:offset + 150] for offset in (0xD4F, 0xDE5, 0xE7B, 0xF11)]
    assert len({image[0], image[1]}) == 2 and image[0] == image[2] and image[1] == image[3]
    assert all(data[:15] == data[-15:] == b'\xFF' * 15 for data in image)
    for y in range(1, 9):
        left, right = (image[i][15 * y:15 * (y + 1)] for i in (0, 3))
        assert left[:5] == right[10:] and left[5:] == right[:10] == bytes(10)

    expected = bytearray((index * 43 + 13) & 255 for index in range(0x4000))
    memory.banks[7][:] = expected
    for column, template in ((0, image[0]), (17, image[3])):
        for index in range(10):
            offset = screen_offset(15 + index, column)
            expected[offset:offset + 15] = template[15 * index:15 * (index + 1)]
        attr = 0x1840 + column
        expected[attr:attr + 15] = b'\x14' * 15
    sources = []

    def observe(pc):
        if pc == 0x4CCD:
            sources.append(registers[H] * 256 + registers[L])

    enter_call(cpu, 0x4C8C)
    run_to(cpu, RETURN, observe)
    assert sources == [address + offset for address in (0x4D4F, 0x4F11) for offset in range(150)]
    assert registers[SP] == STACK and memory.o7ffd == 0x1F
    assert bytes(memory.banks[7]) == expected
    assert bytes(memory[0x4FA7:0x4FB1]) == b'\x78\x78' + ENGINE[0xFA9:0xFB1]
    return expected


def cursor_for(side, count):
    byte, bit = divmod(count, 8)
    return ((0xC040 + byte, 0x80 >> bit) if side == 0 else (0xC05F - byte, 1 << bit))


def check_fill(cpu, expected):
    memory, registers = cpu.memory, cpu.registers
    for count in range(121):
        code = count % 16
        registers[A] = code
        call(cpu, 0x4FB1)
        selector = memory.o7ffd
        call(cpu, 0x4CD7)
        assert memory.o7ffd == selector and memory[0x5012] == memory[0x5013] == code
        for side in range(2):
            address, mask = cursor_for(side, count)
            if count < 120:
                for row in range(8):
                    offset = address - 0xC000 + 256 * row
                    expected[offset] ^= mask
            result_count = min(120, count + 1)
            cursor, bit_mask = cursor_for(side, result_count)
            assert memory[0x4FA9 + side] == result_count
            assert word(memory, 0x4FAB + 2 * side) == cursor
            assert memory[0x4FAF + side] == bit_mask
        assert bytes(memory.banks[7]) == expected
    return 121


def check_comparisons(cpu):
    memory = cpu.memory
    memory.out7ffd(0x1F)
    cases = 0
    for side, entry in enumerate((0x4CEF, 0x4D1E)):
        for shown in range(121):
            address, mask = cursor_for(side, shown)
            for target in range(121):
                memory[0x4FA7 + side], memory[0x4FA9 + side], memory[0x4FAF + side] = target, shown, mask
                put(memory, 0x4FAB + 2 * side, address.to_bytes(2, 'little'))
                points = [address + 256 * row for row in range(8)]
                initial = [memory[point] for point in points]
                call(cpu, entry)
                advance = shown < target
                assert memory[0x4FA9 + side] == shown + advance
                cursor, next_mask = cursor_for(side, shown + advance)
                assert word(memory, 0x4FAB + 2 * side) == cursor and memory[0x4FAF + side] == next_mask
                assert [memory[point] for point in points] == [value ^ (mask if advance else 0) for value in initial]
                cases += 1
    return cases


def main():
    cpu = init_prefix(0)
    rows = check_rows(cpu)
    image = check_templates(cpu)
    frames = check_fill(cpu, image)
    comparisons = check_comparisons(cpu)
    result = dict(passed=True, screen_row_cases=rows, physical_bitmap_bytes=600,
                  bitmap_addresses=[0x4D4F, 0x4DE5, 0x4E7B, 0x4F11],
                  bytes_read_during_initialization=300, continuous_updates=frames,
                  comparison_cases=comparisons, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveEngineMetersVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
