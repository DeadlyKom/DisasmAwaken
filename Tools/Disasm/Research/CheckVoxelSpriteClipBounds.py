"""Отсечение прямоугольника EC7F до расчёта шагов ресурса в ED06."""
from collections import Counter
from itertools import product
import json

from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers


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
        sim.registers[:] = get_registers({'PC': 0xEC7F, 'SP': 0xBFFE, 'HL': x & 65535,
                                         'DE': y & 65535, 'BC': height * 256 + width}, None, False)
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
                  stopped_before_resource_steps=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/VoxelSpriteClipBoundsVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
