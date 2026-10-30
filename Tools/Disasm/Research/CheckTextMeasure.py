"""Проверка двух измерителей текста с исходными и граничными таблицами ширин."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, SP


def add_flags(left, right):
    result = (left + right) & 255
    return ((result & 0xA8) | (0x40 if result == 0 else 0)
            | (0x10 if (left & 15) + (right & 15) > 15 else 0)
            | (4 if ~(left ^ right) & (left ^ result) & 128 else 0)
            | int(left + right > 255))


def reference(text, delimiter, widths):
    total = 0
    for consumed, char in enumerate(text):
        if char in (13, 10, delimiter):
            return total, 0x42 | (char & 0x28), consumed
        width = widths[char]
        next_total = total + width
        if next_total > 255 or next_total == 0:
            return 255, add_flags(width, total), consumed
        total = next_total
    raise ValueError("В тестовой строке нет достижимого ограничителя")


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    actual_widths = list(source[0x2900:0x2A00])
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    cases = 0
    tables = [actual_widths] + [[value] * 256 for value in (0, 1, 127, 128, 255)]
    for table_index, widths in enumerate(tables):
        memory[0x8900:0x8A00] = widths
        for char, count, delimiter, terminal_kind in product(
                range(256), (0, 1, 2, 31, 42, 43, 127, 256), (0, 32, 254), (0, 1, 2)):
            terminal = (13, 10, delimiter)[terminal_kind]
            text = [char] * count + [terminal]
            memory[0x5000:0x5000 + len(text)] = text
            expected_a, expected_flags, consumed = reference(text, delimiter, widths)
            for start, preserve_pointer in ((0xBDA6, False), (0xBDCA, True)):
                # Проверка точного AF и позиции HL, ограничитель или переполнивший сумму символ не потребляется первым входом.
                simulator.registers[:] = get_registers(
                    {"SP": 0xBFFE, "HL": 0x5000, "DE": 0x1357, "BC": delimiter * 256 + 0x68,
                     "AF": (char << 8) | (count & 255), "IX": 0x2468, "IY": 0x5C3A,
                     "^HL": 0x369C, "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
                before = simulator.registers.copy()
                simulator.run(start=start, stop=0x3FFF)
                pointer = 0x5000 if preserve_pointer else 0x5000 + consumed
                if (simulator.registers[A], simulator.registers[F], simulator.registers[H] * 256 + simulator.registers[L],
                        simulator.registers[SP]) != (expected_a, expected_flags, pointer, 0xC000):
                    raise ValueError(f"Не совпал измеритель {start:04X}, char={char}, count={count}, table={table_index}")
                for reg in (*range(2, 6), *range(8, 12), *range(16, 24)):
                    if simulator.registers[reg] != before[reg]:
                        raise ValueError("Измеритель изменил сохраняемый регистр")
                cases += 1
        print(f"Проверено таблиц ширины {table_index + 1}/{len(tables)}", flush=True)
    report = {"method": "original_z80_text_measurers_against_independent_width_accumulator",
              "cases": cases, "passed": True, "source_sha256": hashlib.sha256(source).hexdigest(),
              "original_widths_sha256": hashlib.sha256(bytes(actual_widths)).hexdigest(),
              "original_width_min": min(actual_widths), "original_width_max": max(actual_widths),
              "synthetic_constant_widths": [0, 1, 127, 128, 255], "glyph_rendering_verified": False,
              "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/TextMeasureVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
