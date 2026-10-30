"""Изолированная проверка перенесённого ядра станции и фактических значений OUT."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, SP


class PortLog:
    def __init__(self):
        self.writes = []

    def write_port(self, registers, port, value, cycles):
        self.writes.append((port, value))


def logic_flags(value):
    return (value & 0xA8) | (0x40 if value == 0 else 0) | (4 if value.bit_count() % 2 == 0 else 0)


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    # Перенос соответствует исходному LDIR, физические смещения не равны рабочим адресам ядра.
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    log = PortLog()
    simulator.set_tracer(log)
    initial = get_registers({"SP": 0xBFFE, "HL": 0x1357, "DE": 0x2468, "BC": 0x369C,
                             "IX": 0x47AD, "IY": 0x5C3A, "^HL": 0x58BE,
                             "^DE": 0x69CF, "^BC": 0x7AD0, "^AF": 0x8BE1}, None, False)
    merged = direct = motion = 0
    for old, value in product(range(256), range(256)):
        # Проверка всех сочетаний тени и входного байта, включая ненулевые старшие биты A.
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = value, old ^ value
        memory[0x6306] = old
        log.writes.clear()
        simulator.run(start=0x6396, stop=0x3FFF)
        expected = (old & 0xF8) | value
        if (memory[0x6306], simulator.registers[A], simulator.registers[F], log.writes) != (
                expected, expected, logic_flags(expected), [(0x7FFD, expected)]):
            raise ValueError("Не совпал объединённый байт страницы")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Не восстановлен стек переключателя")
        for reg in (*range(2, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Переключатель изменил сохраняемый регистр")
        merged += 1
        # Проверка прямого входа со всеми байтами AF, аппаратное переключение здесь не моделируется.
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = value, old
        log.writes.clear()
        simulator.run(start=0x639F, stop=0x3FFF)
        if (memory[0x6306], simulator.registers[A], simulator.registers[F], log.writes) != (
                value, value, old, [(0x7FFD, value)]):
            raise ValueError("Не совпал прямой OUT или сохранённый AF")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Не восстановлен стек прямого входа")
        for reg in (*range(2, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Прямой вход изменил сохраняемый регистр")
        direct += 1
    fields = (0x6586, 0x6587, 0x6588, 0x6589, 0x66E8, 0x66E9, 0x66EA, 0x66EB)
    patterns = [[0] * 8]
    patterns += [[value if index == selected else 0 for index in range(8)]
                 for selected, value in product(range(8), range(256))]
    patterns += [[(seed * (2 * index + 1) + index * 37) & 255 for index in range(8)]
                 for seed in range(256)]
    for pattern in patterns:
        # Проверка каждого входного байта отдельно и смешанных наборов четырёх слов.
        for address, value in zip(fields, pattern):
            memory[address] = value
        simulator.registers[:] = initial
        simulator.registers[F] = motion & 255
        simulator.run(start=0x63F1, stop=0x3FFF)
        expected = 0
        for value in pattern:
            expected |= value
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP]) != (expected, logic_flags(expected), 0xC000):
            raise ValueError("Не совпало объединение восьми байтов параметров")
        for reg in (*range(2, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Проверка параметров изменила сохраняемый регистр")
        motion += 1
    report = {"method": "relocated_original_z80_bytes_and_port_log", "passed": True,
              "merged_page_cases": merged, "direct_page_cases": direct, "parameter_cases": motion,
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "physical_paging_or_lock_bit_simulated": False, "interrupts_simulated": False,
              "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/StationCoreVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
