"""Проверка настройки текстового окна и одноместного сохранения его изменяемых операндов."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, SP

FIELDS = (0xAEBB, 0xAEC7, 0xAEBF, 0xAECB, 0xAEB3, 0xAEAB, 0xBD26, 0x6320, 0x6321)
SNAPSHOT = (0xA437, 0xA43C, 0xA441, 0xA446, 0xA44B, 0xA450, 0xA455, 0xA45A, 0xA45F)


def original_scale(value):
    # Независимая битовая формула отражает два RLCA и один RLA, включая старшие разряды.
    return ((value & 31) << 3) | ((value >> 7) << 2) | (3 if value & 64 else 0)


def subtract_flags(left, right):
    result = (left - right) & 255
    return ((result & 0xA8) | (0x40 if result == 0 else 0)
            | ((left ^ right ^ result) & 0x10)
            | (4 if (left ^ right) & (left ^ result) & 0x80 else 0)
            | 2 | int(left < right))


def main(inset=False, centered=False):
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0xBFFE, "HL": 0x1357, "IX": 0x2468, "IY": 0x5C3A,
                             "^HL": 0x369C, "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    setup_cases = 0
    dimensions = ((1, 1), (24, 32), (31, 63), (64, 127), (128, 192), (255, 255))
    for row, column, (height, width) in product(range(256), range(256), dimensions):
        # Проверка всех байтов координат с размерами по обе стороны границ 32, 64 и 128.
        simulator.registers[:] = initial
        simulator.registers[B], simulator.registers[C] = row, column
        simulator.registers[D], simulator.registers[E] = height, width
        simulator.registers[A], simulator.registers[F] = row ^ column, (row + column) & 255
        before = simulator.registers.copy()
        simulator.run(start=0xC34B if centered else 0xC233 if inset else 0xC039, stop=0x3FFF)
        x = original_scale(column if column < 128 else 256 - column)
        y = original_scale(row if row < 128 else 256 - row)
        expected = ((-x) & 255 if column >= 128 else x,
                    (-y) & 255 if row >= 128 else y,
                    255 if column >= 128 else 0, 255 if row >= 128 else 0,
                    original_scale(width), original_scale(height))
        if inset or centered:
            expected = ((expected[0] + 3) & 255, (expected[1] + (4 if centered else 3)) & 255, expected[2], expected[3],
                        (expected[4] - 4) & 255, (expected[5] - 11) & 255)
        if tuple(memory[p] for p in FIELDS[:6]) != expected or memory[0x6320:0x6322] != [int(inset), 0]:
            raise ValueError("Не совпали операнды текстового окна")
        flags = (0x80 if row >= 128 else 0x44) | (original_scale(height) & 0x28) | ((height >> 5) & 1)
        if inset or centered:
            flags = subtract_flags(original_scale(height), 11)
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP]) != (expected[5], flags, 0xC000):
            raise ValueError("Не совпал выходной AF настройки окна")
        for index in (*range(2, 12), *range(16, 24)):
            if simulator.registers[index] != before[index]:
                raise ValueError("Изменён сохраняемый регистр настройки")
        setup_cases += 1
    snapshot_cases = 0
    for value, flags in product(range(256), range(256)):
        # Проверка сохранения всех разрядов девяти полей и флагов, снимок намеренно одноместный.
        pattern = [(value + index * 37) & 255 for index in range(9)]
        for address, byte in zip(FIELDS, pattern):
            memory[address] = byte
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = value, flags
        simulator.run(start=0xA3FF, stop=0x3FFF)
        if [memory[p] for p in SNAPSHOT] != pattern or simulator.registers[A] != pattern[6] or simulator.registers[F] != flags:
            raise ValueError("Не совпал сохранённый снимок или AF сохранения")
        for address in FIELDS:
            memory[address] = 0x96
        simulator.registers[SP] = 0xBFFE
        simulator.run(start=0xA436, stop=0x3FFF)
        if [memory[p] for p in FIELDS] != pattern or simulator.registers[A] != pattern[8] or simulator.registers[F] != flags:
            raise ValueError("Не совпало восстановленное окно или AF восстановления")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Не восстановлен стек снимка")
        for index in (*range(2, 12), *range(16, 24)):
            if simulator.registers[index] != initial[index]:
                raise ValueError("Изменён сохраняемый регистр снимка")
        snapshot_cases += 1
    report = {"method": "original_z80_bytes_against_window_operands_and_snapshot",
              "setup_entry": "#C34B" if centered else "#C233" if inset else "#C039",
              "setup_cases": setup_cases, "snapshot_cases": snapshot_cases, "passed": True,
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "text_pixels_or_font_verified": False, "assembly_executed": False}
    report_name = "CenterTextWindowVerification.json" if centered else "InsetTextWindowVerification.json" if inset else "TextWindowVerification.json"
    (ROOT / "Tools/Disasm/Reports" / report_name).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    variants = parser.add_mutually_exclusive_group()
    variants.add_argument("--inset", action="store_true")
    variants.add_argument("--centered", action="store_true")
    args = parser.parse_args()
    main(args.inset, args.centered)
