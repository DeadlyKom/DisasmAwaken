"""Проверка подготовителя рамки с параметризованными таблицами адресации, без рисования."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP, xA, xF, xH, xL


def rotate_three(value):
    return ((value << 3) | (value >> 5)) & 255


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    # Подстановка различимых таблиц проверяет их роли, не выдавая их за реальные данные запуска.
    memory[0x8200:0x8300] = [(index * 37 + 29) & 255 for index in range(256)]
    memory[0x8300:0x8400] = [(index * 73 + 19) & 255 for index in range(256)]
    memory[0x8400:0x8500] = [(index * 109 + 43) & 255 for index in range(256)]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0xBFFE, "HL": 0x1357, "DE": 0x6700,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x23AA,
                             "^DE": 0x369C, "^BC": 0x47AD, "^AF": 0x58BE}, None, False)
    # Независимое описание горизонтальных интервалов для всех допустимых внутренних ширин.
    expected_spans = {}
    for column in range(256):
        signed_column = column if column < 128 else column - 256
        for width in range(31):
            if signed_column < 0:
                expected_spans[column, width] = (max(0, width + signed_column),
                                                 0x2C72 if width + signed_column >= 0 else 0,
                                                 0x71, 0x0044)
            elif column + width >= 31:
                expected_spans[column, width] = (max(0, 30 - column), 0x2C72,
                                                 0x71 if column <= 30 else 0, 0x0101)
            else:
                expected_spans[column, width] = (width, 0x2C72, 0x71, 0x0100)
    cases = 0
    for row in range(256):
        row_index = rotate_three(0 if row & 128 else row)
        row_high = memory[0x8200 + row_index]
        row_low = memory[0x8300 + row_index]
        for column in range(256):
            actual_column = 0 if column & 128 else column
            pointer_low = row_low | memory[0x8400 + rotate_three(actual_column)]
            expected_flags = (pointer_low & 0xA8) | (0x40 if pointer_low == 0 else 0)
            expected_flags |= 4 if pointer_low.bit_count() % 2 == 0 else 0
            for width in range(31):
                # Проверка полного совместного диапазона B, C и E=0..30 на оригинальном коде.
                simulator.registers[:] = initial
                simulator.registers[B], simulator.registers[C], simulator.registers[E] = row, column, width
                simulator.registers[A], simulator.registers[F] = (row + column) & 255, (row ^ column ^ width) & 255
                simulator.run(start=0xBF4E, stop=0x3FFF)
                expected_width, left_pair, right_opcode, alternate_af = expected_spans[column, width]
                if (simulator.registers[H], simulator.registers[L], simulator.registers[B], simulator.registers[C],
                    simulator.registers[D], simulator.registers[E], simulator.registers[A], simulator.registers[F],
                    simulator.registers[xH], simulator.registers[xL], simulator.registers[xA], simulator.registers[xF]) != (
                        row_high, pointer_low, row_high, actual_column, 0x67, expected_width, pointer_low, expected_flags,
                        0x23, (row - 1) & 255, alternate_af >> 8, alternate_af & 255):
                    raise ValueError(f"Не совпал контракт подготовителя рамки B={row}, C={column}, E={width}")
                if (memory[0xC17C] + 256 * memory[0xC17D] != left_pair or memory[0xC1BC] != right_opcode
                        or simulator.registers[SP] != 0xC000 or simulator.registers[PC] != 0x3FFF
                        or simulator.registers[8:12] != initial[8:12]
                        or simulator.registers[18:22] != initial[18:22]):
                    raise ValueError("Неверно восстановлены коды краёв или сохраняемые регистры")
                cases += 1
        if (row + 1) % 64 == 0:
            print(f"Проверено строк B: {row + 1}/256", flush=True)
    report = {"method": "original_z80_bytes_with_synthetic_address_tables", "cases": cases,
              "all_B_C_bytes_and_interior_widths_checked": True, "real_address_tables_used": False,
              "left_and_right_opcode_restoration_checked": True,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "whole_frame_rendering_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/FrameRasterSetupVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
