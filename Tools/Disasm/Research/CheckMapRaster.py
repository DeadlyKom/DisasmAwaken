"""Проверка переходов строк Spectrum и нелокального выхода на исходных байтах карты."""

from pathlib import Path
import hashlib
import json
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
    simulator = Simulator(memory)

    def word(address, value):
        memory[address:address + 2] = [value & 255, value >> 8]

    def row(base, y, x=0):
        return base | ((y & 7) << 8) | ((y & 0x38) << 2) | ((y & 0xC0) << 5) | x

    def pair(high, low):
        return 256 * simulator.registers[high] + simulator.registers[low]

    def run(entry, pointer, other, upper, lower):
        word(0xDFBA, upper)
        word(0xDFBC, lower)
        word(0xDFB4, 0xBFFA)
        word(0xBFF0, 0x3FFE)
        word(0xBFFA, 0x5AA5)
        word(0xBFFC, 0x3FFF)
        simulator.registers[:] = get_registers(
            {"PC": entry, "SP": 0xBFF0, "HL": pointer, "DE": 0x7700 | other,
             "BC": 0x1357, "AF": 0xDBA5, "IX": 0x789A, "IY": 0x5C3A,
             "^HL": 0x2468, "^DE": 0x369C, "^BC": 0x47AD, "^AF": 0x58BE}, None, False)
        preserved = simulator.registers[8:12] + simulator.registers[16:24]
        for _ in range(64):
            if simulator.registers[PC] in (0x3FFE, 0x3FFF):
                break
            simulator.run()
        else:
            raise ValueError("Растровый переход не завершился")
        if pair(B, C) != 0x1357 or preserved != simulator.registers[8:12] + simulator.registers[16:24]:
            raise ValueError("Изменились сохраняемые регистры растрового перехода")

    normal_cases = 0
    for base in (0x4000, 0x6000, 0x8000, 0xA000):
        for x in (0, 1, 15, 31):
            for other_x in (0, 31):
                for entry, delta, ys in ((0xE57E, -1, range(1, 192)), (0xE5AC, 1, range(191))):
                    for y in ys:
                        # Проверка всех внутренних строк, переходов третей и переноса обеих колонок.
                        upper, lower = row(base, 0), row(base, 192)
                        run(entry, row(base, y, x), row(base, y, other_x) & 255, upper, lower)
                        boundary = upper if delta < 0 else lower
                        if (pair(H, L) != row(base, y + delta, x)
                                or simulator.registers[E] != row(base, y + delta, other_x) & 255
                                or simulator.registers[D] != boundary >> 8
                                or simulator.registers[PC] != 0x3FFE or simulator.registers[SP] != 0xBFF2):
                            raise ValueError("Неверно перенесены адреса растровых колонок")
                        normal_cases += 1
    exits = 0
    for base in (0x4000, 0x6000, 0x8000, 0xA000):
        for x in (0, 1, 15, 31):
            for y in (0, 1, 7, 8, 63, 64, 127, 128, 191):
                for entry in (0xE57E, 0xE5AC):
                    # Проверка пропуска внутреннего возврата и восстановления независимого внешнего стека.
                    upper = row(base, y) if entry == 0xE57E else row(base, 0)
                    lower = row(base, y + 1) if entry == 0xE5AC else row(base, 192)
                    run(entry, row(base, y, x), row(base, y, 31 - x) & 255, upper, lower)
                    expected_y = y if entry == 0xE57E else y + 1
                    if (pair(H, L) != row(base, expected_y, x) or simulator.registers[PC] != 0x3FFF
                            or simulator.registers[SP] != 0xBFFE
                            or simulator.registers[A] != 0x5A or simulator.registers[F] != 0xA5):
                        raise ValueError("Неверно завершён внешний растровый вызов")
                    exits += 1
    resets = 0
    for entry, direction in ((0xE666, 1), (0xE674, 0)):
        for flags in range(256):
            for alternate in (0, 0x1357, 0xFFFF):
                word(0xBFF0, 0x3FFE)
                simulator.registers[:] = get_registers(
                    {"PC": entry, "SP": 0xBFF0, "HL": 0x1357, "DE": 0x2468,
                     "BC": 0x9ABC, "AF": 0xDB00 | flags, "^HL": alternate,
                     "^DE": 0x67CD, "^BC": 0x89EF, "^AF": 0x5AA5,
                     "IX": 0x789A, "IY": 0x5C3A}, None, False)
                # Проверка полного входного F, частичного сброса альтернативного набора и байта направления.
                for _ in range(12):
                    if simulator.registers[PC] == 0x3FFE:
                        break
                    simulator.run()
                else:
                    raise ValueError("Сброс растрового состояния не вернулся")
                expected_f = flags if direction else 0x44
                if (pair(H, L), pair(D, E), pair(B, C), simulator.registers[A], simulator.registers[F]) != (
                        0x1357, 0x2468, 0x9ABC, direction, expected_f):
                    raise ValueError("Неверен основной контракт сброса растрового состояния")
                if (simulator.registers[16:24] != [0x5A, 0xA5, 0xFF, 0xEF, 0, 0xCD, 0, 0]
                        or simulator.registers[8:12] != [0x78, 0x9A, 0x5C, 0x3A]
                        or memory[0xDFB9] != direction or simulator.registers[SP] != 0xBFF2):
                    raise ValueError("Неверен альтернативный контракт сброса растрового состояния")
                resets += 1
    report = {"method": "original_z80_bytes_without_assembly", "normal_row_cases": normal_cases,
              "nonlocal_exit_cases": exits, "reset_cases": resets,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "whole_raster_algorithm_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/MapRasterVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
