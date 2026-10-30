"""Проверка фактической записи полосы с изменяемой шириной на исходных байтах."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, PC, SP


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    patterns = ((0, 0, 0), (255, 255, 255), (0x40, 0, 2), (0x5F, 255, 0xFA), (0x12, 0x34, 0x56))
    cases = 0
    for left_enabled, right_enabled, count in product((False, True), (False, True), range(31)):
        # Настройка всех трёх участков самомодификации, применяемых исходным подготовителем рамки.
        memory[0xC17C:0xC17E] = [0x72, 0x2C] if left_enabled else [0, 0]
        memory[0xC1BC] = 0x71 if right_enabled else 0
        memory[0xC17F] = 2 * (30 - count)
        byte_count = count + int(left_enabled) + int(right_enabled)
        for high in (0x40, 0x57, 0x7F, 0xFF):
            for group in range(8):
                for x in range(33 - max(byte_count, 1)):
                    low = 32 * group + x
                    for carry in (0, 1):
                        for left, middle, right in patterns:
                            # Проверка всех допустимых положений полосы в байтовой строке экрана.
                            page = high * 256
                            memory[page:page + 256] = [0x96] * 256
                            expected = memory[page:page + 256].copy()
                            expected[low:low + byte_count] = ([left] if left_enabled else []) + [middle] * count + ([right] if right_enabled else [])
                            simulator.registers[:] = get_registers(
                                {"PC": 0xC17B, "SP": 0xBFFE, "HL": page + low,
                                 "DE": left * 256 + middle, "BC": 0xAB00 + right,
                                 "AF": 0x5A00 | 0xFE | carry, "IX": 0x1357, "IY": 0x5C3A,
                                 "^HL": 0x2468, "^DE": 0x369C, "^BC": 0x47AD, "^AF": 0x58BE}, None, False)
                            before = simulator.registers.copy()
                            for _ in range(80):
                                if simulator.registers[PC] == 0x3FFF:
                                    break
                                simulator.run()
                            else:
                                raise ValueError("Писатель полосы не вернулся")
                            new_high = (high + 1) & 255
                            expected_flags = ((new_high & 0xA8) | (0x40 if new_high == 0 else 0)
                                              | (0x10 if high & 15 == 15 else 0)
                                              | (4 if high == 127 else 0) | carry)
                            if (memory[page:page + 256] != expected or simulator.registers[H] != new_high
                                    or simulator.registers[L] != low or simulator.registers[A] != low
                                    or simulator.registers[F] != expected_flags or simulator.registers[SP] != 0xC000):
                                raise ValueError("Не совпали пиксельные байты или контракт писателя полосы")
                            for index in (*range(2, 6), *range(8, 12), *range(16, 24)):
                                if simulator.registers[index] != before[index]:
                                    raise ValueError("Писатель полосы изменил сохраняемый регистр")
                            cases += 1
    report = {"method": "original_z80_bytes_with_original_raster_patches", "cases": cases,
              "edge_opcode_combinations": 4,
              "interior_widths_checked": 31, "all_valid_byte_columns_and_groups_checked": True,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "whole_frame_rendering_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/StationSpanWriterVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
