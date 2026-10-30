"""Полная проверка табличных квадратов и разности квадратов на исходном Z80."""

from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, B, C, PC, SP


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 7)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    def pair(high, low):
        return 256 * simulator.registers[high] + simulator.registers[low]

    def run(entry, value, first, carry):
        simulator.registers[:] = get_registers(
            {"PC": entry, "SP": 0xBFFE, "A": value, "F": 0xFE | carry,
             "DE": first * 256 + 0xAB, "HL": 0x1357, "BC": 0x2468,
             "IX": 0x789A, "IY": 0x5C3A}, None, False)
        simulator.registers[16:24] = [3, 17, 31, 43, 59, 71, 89, 101]
        for _ in range(250):
            if simulator.registers[PC] == 0x3FFF:
                return
            simulator.run()
        raise ValueError("Математическая процедура карты не завершилась")

    # Проверка всех 256 физических слов таблицы и сохранения обоих состояний Carry.
    for value in range(256):
        expected = value * value
        if source[0x2900 + value] + 256 * source[0x2A00 + value] != expected:
            raise ValueError("Таблица не содержит точные квадраты 0..255")
        for carry in (0, 1):
            run(0xE65D, value, 0xDB, carry)
            if (pair(D, E) != expected or pair(H, L) != 0x1357 or pair(B, C) != 0x2468
                    or simulator.registers[A] != value or simulator.registers[F] != 0xA8 | carry
                    or simulator.registers[SP] != 0xC000):
                raise ValueError("Неверный контракт LookupSquare")
    # Проверка полного диапазона двух байтовых аргументов и обоих входных заёмов.
    cases = 0
    for first in range(256):
        for second in range(256):
            for carry in (0, 1):
                run(0xE554, second, first, carry)
                target = (first * first - second * second - carry) & 0xFFFF
                if (simulator.registers[A] != math.isqrt(target) or simulator.registers[F] != 0x45
                        or pair(H, L) != 0x1357 or pair(B, C) != 0x2468
                        or pair(D, E) != first * 256 + 0xAB
                        or memory[0xDFB6] + 256 * memory[0xDFB7] != target
                        or simulator.registers[SP] != 0xC000
                        or simulator.registers[8:12] != [0x78, 0x9A, 0x5C, 0x3A]
                        or simulator.registers[16:24] != [3, 17, 31, 43, 59, 71, 89, 101]):
                    raise ValueError("Неверный контракт корня разности квадратов")
                cases += 1
    report = {"method": "original_z80_bytes_without_assembly", "square_table_words": 256,
              "square_lookup_cases": 512, "sqrt_difference_cases": cases,
              "full_byte_arguments_and_carry_domain": True, "flags_checked": True,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "map_rendering_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/MapMathVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
