"""Проверка исходного контроля геометрии элемента, включая байтовое переполнение сумм."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, H, L, SP
from CheckGlyphRenderer import compare_flags


def inverted_carry_flags(value, compared):
    flags = compare_flags(value, compared)
    return (flags & 0xC4) | (value & 0x28) | (0x10 if flags & 1 else 1)


def reference(key, x, y, width, height):
    base = (0xF0FD+16*key) & 65535
    if x >= 128:
        return base+1, 0x24, x, 0xF0, 0x90 | (x & 0x28)
    if y >= 128:
        return base+2, y, x, 0xF0, 0x90 | (y & 0x28)
    packed = 256*height+width
    summed = (width+x) & 255
    if summed >= 33:
        return packed, y, x, summed, compare_flags(summed, 33)
    summed = (height+y) & 255
    if summed >= 25:
        return packed, y, x, summed, compare_flags(summed, 25)
    if width < 4:
        return packed, y, x, width, inverted_carry_flags(width, 4)
    return packed, y, x, height, inverted_carry_flags(height, 4)


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases, wrapped_accepted = 0, 0

    def execute(key, x, y, width, height):
        nonlocal cases, wrapped_accepted
        base = 0xF0FD+16*key
        memory[base:base+4] = [x, y, width, height]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[H], simulator.registers[L] = key >> 8, key & 255
        simulator.run(start=0xA6C4, stop=0x3FFF)
        actual = (simulator.registers[H]*256+simulator.registers[L], simulator.registers[D],
                  simulator.registers[E], simulator.registers[A], simulator.registers[F])
        expected = reference(key, x, y, width, height)
        if actual != expected:
            raise ValueError(f"Не совпала проверка геометрии {key}/{x}/{y}/{width}/{height}: {actual} != {expected}")
        predicate = x < 128 and y < 128 and ((x+width) & 255) <= 32 and ((y+height) & 255) <= 24 and width >= 4 and height >= 4
        if bool(simulator.registers[F] & 1) != predicate:
            raise ValueError("Не совпал смысл Carry геометрии")
        if predicate and (x+width > 255 or y+height > 255):
            wrapped_accepted += 1
        for reg in (*range(2, 4), *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Проверка геометрии изменила сохраняемый регистр")
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Нарушен стек проверки геометрии")
        cases += 1

    for x, y, dimensions in product(range(256), range(256), ((0, 0), (3, 3), (4, 4), (32, 24), (128, 129), (255, 255))):
        execute(0, x, y, *dimensions)
    for width, height, position in product(range(256), range(256), ((0, 0), (1, 1), (31, 23), (127, 127), (128, 0), (0, 128))):
        execute(45, *position, width, height)
    report = dict(method="original_item_rectangle_validation_against_byte_predicate", passed=True,
                  cases=cases, wrapped_accepted_cases=wrapped_accepted,
                  source_sha256=hashlib.sha256(source).hexdigest(), full_af_and_partial_outputs_checked=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/ItemRectVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
