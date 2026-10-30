"""Проверка образцов строки, отсечения и коррекции экранного адреса на исходных байтах."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP, xA, xF, xH, xL


def result_flags(result):
    return (result & 0xA8) | (0x40 if result == 0 else 0)


def add_flags(left, right):
    result = (left + right) & 255
    return (result_flags(result) | (0x10 if (left & 15) + (right & 15) > 15 else 0)
            | (4 if ~(left ^ right) & (left ^ result) & 128 else 0)
            | int(left + right > 255))


def subtract_flags(left, right):
    result = (left - right) & 255
    return (result_flags(result) | 2 | (0x10 if (left & 15) < (right & 15) else 0)
            | (4 if (left ^ right) & (left ^ result) & 128 else 0) | int(left < right))


def increment_flags(value, carry):
    result = (value + 1) & 255
    return (result_flags(result) | (0x10 if value & 15 == 15 else 0)
            | (4 if value == 127 else 0) | carry)


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    def execute(address, **config):
        simulator.registers[:] = get_registers(
            {"PC": address, "SP": 0xBFFE, "HL": 0x2468, "DE": 0x379A, "BC": 0x4BCD,
             "AF": 0x5A00, "IX": 0x1357, "IY": 0x5C3A,
             "^HL": 0x6789, "^DE": 0x789A, "^BC": 0x89AB, "^AF": 0xA500, **config},
            None, False)
        initial = simulator.registers.copy()
        for _ in range(24):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise ValueError("Станционный помощник не вернулся")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Не восстановлен CPU-стек")
        return initial

    def preserved(initial, changed):
        # Проверка всех обычных и альтернативных регистров, кроме явно объявленного результата.
        for index in (*range(12), *range(16, 24)):
            if index not in changed and simulator.registers[index] != initial[index]:
                raise ValueError("Изменился сохраняемый регистр")

    presets = ((0xC1C0, 0x40, 0, 2), (0xC1CF, 0x5F, 255, 0xFA),
               (0xC1DE, 0x7E, 255, 0x7E), (0xC1F2, 0x3F, 255, 0xFC), (0xC224, 0x40, 0, 2),
               (0xC201, 0x1F, 255, 0xF8), (0xC210, 0x20, 0, 4))
    pattern_cases = 0
    for address, left, middle, right in presets:
        for main_flags in range(256):
            for alternate_flags in range(256):
                # Проверка всех пар F и F', обе пары AF должны сохраниться побитно.
                initial = execute(address, AF=0x5A00 | main_flags, **{"^AF": 0xA500 | alternate_flags})
                expected_left = middle if alternate_flags & 0x40 else left
                expected_right = middle if alternate_flags & 1 else right
                if [simulator.registers[i] for i in (D, E, C)] != [expected_left, middle, expected_right]:
                    raise ValueError("Неверно выбран образец края строки")
                preserved(initial, {D, E, C})
                pattern_cases += 1
    flat_cases = 0
    for address, value in ((0xC1ED, 0), (0xC21F, 255)):
        for main_flags in range(256):
            for alternate_flags in range(256):
                initial = execute(address, AF=0x5A00 | main_flags, **{"^AF": 0xA500 | alternate_flags})
                if [simulator.registers[i] for i in (D, E, C)] != [value] * 3:
                    raise ValueError("Не совпал плоский образец строки")
                preserved(initial, {D, E, C})
                flat_cases += 1
    clip_cases = 0
    for previous in range(256):
        for flags in range(256):
            # Проверка переполнения знакового индекса и независимости результата от входного F.
            initial = execute(0xC165, F=flags, **{"^HL": 0x2300 | previous})
            row = (previous + 1) & 255
            if row & 128:
                expected_a = row
                expected_f = (result_flags(row) & 0xC0) | (row & 0x28) | (4 if previous == 127 else 0) | 1
            else:
                expected_a = row + 1
                expected_f = increment_flags(row, int(row < 24))
            if (simulator.registers[A], simulator.registers[F], simulator.registers[xH], simulator.registers[xL]) != (
                    expected_a, expected_f, 0x23, row):
                raise ValueError("Не совпал контракт знакового счётчика отсечения")
            preserved(initial, {A, F, xL})
            clip_cases += 1
    address_cases = 0
    for pointer in range(65536):
        for flags in (0, 255):
            # Проверка всех адресов HL, включая переходы третей и полный оборот старшего байта.
            initial = execute(0xC16F, HL=pointer, F=flags)
            high, low = pointer >> 8, pointer & 255
            new_low = (low + 32) & 255
            if low + 32 > 255:
                new_high, expected_a, expected_f = high, 0, add_flags(low, 32)
            else:
                new_high = (high - 8) & 255
                expected_a, expected_f = new_high, subtract_flags(high, 8)
            if (simulator.registers[H], simulator.registers[L], simulator.registers[A], simulator.registers[F]) != (
                    new_high, new_low, expected_a, expected_f):
                raise ValueError("Не совпал контракт коррекции экранного адреса")
            preserved(initial, {H, L, A, F})
            address_cases += 1
    duplicate_equal = source[0x61C0:0x61CF] == source[0x6224:0x6233]
    if not duplicate_equal:
        raise ValueError("Ожидаемая исходная копия образца не совпала")
    report = {"method": "original_z80_bytes_without_assembly", "pattern_cases": pattern_cases,
              "flat_pattern_cases": flat_cases, "clip_counter_cases": clip_cases,
              "screen_address_cases": address_cases, "original_outline_copy_identical": duplicate_equal,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "whole_frame_rendering_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/StationSpanVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
