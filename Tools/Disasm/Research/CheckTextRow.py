"""Проверка байтового перехода текстового курсора на восемь пикселей вниз."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, SP
from CheckGlyphRenderer import compare_flags


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0x7FFE:0x8000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x2468, "BC": 0x369C,
                             "IX": 0x47AD, "IY": 0x5C3A, "^HL": 0x58BE,
                             "^DE": 0x69CF, "^BC": 0x7AD0, "^AF": 0x8BE1}, None, False)
    cases = 0
    for row, height in product(range(256), range(256)):
        memory[0x6320:0x6322] = [0x96, row]
        memory[0xAEAB] = height
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = row ^ height, (row + height) & 255
        simulator.run(start=0xAE55, stop=0x3FFF)
        next_row = (row + 8) & 255
        if next_row < height:
            expected_a, expected_f = 0, 0x44
            expected_cursor = [0, next_row]
        else:
            expected_a = next_row
            expected_f = (compare_flags(next_row, height) & 0xC4) | (next_row & 0x28) | 1
            expected_cursor = [0x96, row]
        if (memory[0x6320:0x6322] != expected_cursor
                or (simulator.registers[A], simulator.registers[F], simulator.registers[B], simulator.registers[C], simulator.registers[SP]) != (
                    expected_a, expected_f, height, next_row, 0x8000)):
            raise ValueError("Не совпал текстовый переход или полный AF")
        for reg in (*range(4, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Текстовый переход изменил сохраняемый регистр")
        cases += 1
    report = {"method": "original_z80_text_row_against_byte_wrap_and_height_limit",
              "cases": cases, "passed": True, "source_sha256": hashlib.sha256(source).hexdigest(),
              "byte_wrap_preserved": True, "glyph_rendering_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/TextRowVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
