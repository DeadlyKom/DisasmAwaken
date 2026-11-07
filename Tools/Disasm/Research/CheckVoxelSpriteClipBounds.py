"""Отсечение прямоугольника EC7F до расчёта шагов ресурса в ED06."""
from collections import Counter
from itertools import product
import json

from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import xor_flags


def comparison(value, limit):
    result = (value - limit) & 255
    return ((result & 128) | (limit & 0x28) | (64 if not result else 0)
            | (16 if (value & 15) < (limit & 15) else 0)
            | (4 if (value ^ limit) & (value ^ result) & 128 else 0)
            | 2 | int(value < limit))


def rejected_axis(start, length, bound):
    unsigned = start & 65535
    high = unsigned >> 8
    if start < 0:
        total = unsigned + length
        result = total & 65535
        flags = ((result >> 8) & 0xA8) | (64 if not result else 0)
        flags |= 16 if (unsigned & 4095) + length >= 4096 else 0
        flags |= int(total >= 65536)
        return result, high, flags
    if high:
        return unsigned, high, xor_flags(high) | 16
    return unsigned, unsigned, comparison(unsigned, bound)


def verify_rejected(registers, initial, x, y, width, height):
    expected = list(initial)
    expected[PC], expected[SP] = 0x3FFF, 0xC000
    if not width or not height:
        expected[0:2] = [0, 0x44]
    else:
        expected[2], expected[10], expected[11] = 0, height, width
        expected[18:20] = [0, 0]
        expected[5] = height
        if x + width <= 0 or x >= 64:
            coordinate, a, flags = rejected_axis(x, width, 64)
        else:
            expected[3] = min(x + width, 64) - max(x, 0)
            expected[19] = int(x < 0)
            expected[4] = 0
            coordinate, a, flags = rejected_axis(y, height, 24)
        expected[6:8] = [coordinate >> 8, coordinate & 255]
        expected[0:2] = [a, flags]
    checked = (*range(13), 14, *range(16, 25), 26, 27)
    assert all(registers[i] == expected[i] for i in checked), (
        x, y, width, height, [(i, registers[i], expected[i]) for i in checked if registers[i] != expected[i]]
    )


def main():
    baseline = memory_image()
    baseline[0xBFFE:0xC000] = [255, 63]
    memory = baseline.copy()
    sim = Simulator(memory)
    counts = Counter()
    xs = (-32768, -256, -255, -64, -63, -32, -2, -1, 0, 1, 31, 32, 62, 63, 64, 65, 255, 256, 32767)
    ys = (-32768, -256, -255, -24, -23, -12, -2, -1, 0, 1, 11, 12, 22, 23, 24, 25, 255, 256, 32767)
    sizes = (0, 1, 2, 23, 24, 25, 63, 64, 65, 127, 128, 255)
    for x, y, width, height in product(xs, ys, sizes, sizes):
        for addr in (0xED7E, 0xEC9D, 0xEC9E, 0xECD2, 0xECD3):
            memory[addr] = baseline[addr]
        initial = get_registers({'PC': 0xEC7F, 'SP': 0xBFFE, 'HL': x & 65535,
                                 'DE': y & 65535, 'BC': height * 256 + width, 'IX': 0x1234,
                                 'IY': 0x5678, '^BC': 0x9ABC, '^HL': 0x1122,
                                 '^DE': 0x3344, '^AF': 0x5566, 'AF': 0x7788}, None, False)
        sim.registers[:] = initial
        for _ in range(80):
            if sim.registers[PC] in (0x3FFF, 0xED06):
                break
            sim.run()
        r = sim.registers
        left, top = max(0, x), max(0, y)
        right, bottom = min(64, x + width), min(24, y + height)
        context = (x, y, width, height)
        if not width or not height or right <= left or bottom <= top:
            assert r[PC] == 0x3FFF and r[SP] == 0xC000, context
            verify_rejected(r, initial, x, y, width, height)
            counts['rejected'] += 1
            continue
        assert r[PC] == 0xED06 and r[SP] == 0xBFFE, context
        assert r[3] == right - left and r[5] == bottom - top, context
        assert r[10:12] == [height, width], context
        assert r[18:20] == [top - y, (left > x) + 2 * (top > y)], context
        assert memory[0xED7E] == left - x, context
        assert memory[0xEC9D] + memory[0xEC9E] * 256 == x & 65535, context
        assert memory[0xECD2] + memory[0xECD3] * 256 == y & 65535, context
        counts['clipped'] += 1
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  stopped_before_resource_steps=True, exact_rejected_registers_except_r=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelSpriteClipBoundsVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
