"""Проверка десятичного считывателя на исходных байтах LANG.C, без сборки."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, H, L, PC, SP, IXh, IXl, IYh, IYl, R

from CheckGeometryReturnEntries import Memory


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    # Проверка физического происхождения логического LANG.
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_bytes())
    entry = next(row for row in manifest["entries"] if row["slot"] == 5)
    sectors = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    disk = (ROOT / "Tools/Disasm/Disk/original.trd").read_bytes()
    assert hashlib.sha256(disk).hexdigest() == manifest["sha256"]
    assert disk[entry["offset"]:entry["offset"] + entry["allocated_length"]] == sectors
    assert hashlib.sha256(sectors).hexdigest() == entry["sectors_sha256"]
    assert source == sectors[:entry["length"]]
    # Проверка наблюдателя настоящей записью CPU в отдельной памяти.
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex("320070")
    cpu = Simulator(probe)
    cpu.registers[24] = 0x4000
    probe.recording = True
    cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(65536)
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    cases = 0

    def check(data, digits):
        nonlocal cases
        # Проверка значения, положения курсора и сохранения альтернативного набора.
        memory.recording = False
        memory[0x7000:0x7000 + len(data)] = bytes(data)
        memory[0xBFFC:0xBFFE] = bytes([0xA5, 0x5A])
        simulator.registers[:] = get_registers(
            {"PC": 0xC6EA, "SP": 0xBFFE, "IX": 0x7000, "IY": 0x5C3A,
             "HL": 0x1357, "DE": 0x2468, "BC": 0x9ABC}, None, False)
        simulator.registers[16:24] = [3, 17, 31, 43, 59, 71, 89, 101]
        # Проверка сохранения I, IFF, IM и старшего бита R.
        refresh = cases & 255
        simulator.registers[14] = (cases >> 8) & 255
        simulator.registers[R] = refresh
        simulator.registers[26] = cases & 1
        simulator.registers[27] = cases % 3
        initial = list(simulator.registers)
        memory.writes.clear()
        memory.recording = True
        for _ in range(150):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise ValueError("Десятичный считыватель не вернулся")
        memory.recording = False
        # Расчёт ожидаемых записей каждого PUSH в повторно используемую пару.
        expected_writes = []
        if digits > 1:
            expected_writes.extend(((0xBFFC, 2 * (data[digits - 2] - 48)), (0xBFFD, 0)))
            for index in range(digits - 3, -1, -1):
                expected_writes.extend(((0xBFFC, data[index] - 48), (0xBFFD, 0)))
        assert memory.writes == expected_writes, (bytes(data), memory.writes, expected_writes)
        assert memory[0xBFFE:0xC000] == bytes([0xFF, 0x3F])
        assert all(simulator.registers[i] == initial[i] for i in (10, 11, 14, 26, 27))
        assert simulator.registers[R] & 128 == refresh & 128
        value = int(bytes(data[:digits])) & 0xFFFF
        # Расчёт рабочих остатков после последнего десятичного разряда.
        expected_de = 0x2468 if digits == 1 else int(bytes(data[1:digits]))
        expected_c = 0xBC if digits == 1 else (2 if digits == 2 else 1) * (data[0] - 48)
        expected_a = data[0] - 48 if digits in (1, 5) else 1
        assert simulator.registers[4] * 256 + simulator.registers[5] == expected_de
        assert (simulator.registers[2], simulator.registers[3], simulator.registers[0]) == (0, expected_c, expected_a)
        actual = simulator.registers[H] * 256 + simulator.registers[L]
        cursor = simulator.registers[IXh] * 256 + simulator.registers[IXl]
        if actual != value or cursor != 0x7000 + digits:
            raise ValueError(f"Неверно прочитано число {bytes(data)!r}, результат {actual}, курсор {cursor:04X}")
        if (simulator.registers[SP] != 0xC000
                or simulator.registers[IYh] * 256 + simulator.registers[IYl] != 0x5C3A
                or simulator.registers[16:24] != [3, 17, 31, 43, 59, 71, 89, 101]):
            raise ValueError("Не сохранён стек, IY или альтернативные регистры")
        cases += 1

    # Проверка всех цифровых строк каждой длины, включая все ведущие нули.
    widths = {}
    for width in range(1, 6):
        widths[width] = 0
        for number in range(10 ** width):
            text = f"{number:0{width}d}".encode("ascii")
            check(list(text + b";"), width)
            widths[width] += 1
    # Проверка ведущих нулей, ограничения пяти цифр и всех недесятичных разделителей.
    special = 0
    for width in range(1, 6):
        for number in (0, 1, 9):
            text = f"{number:0{width}d}".encode("ascii")
            check(list(text + b";"), len(text))
            special += 1
    for text in (b"123456", b"999999", b"000001"):
        check(list(text), 5)
        special += 1
    for length in range(1, 5):
        for delimiter in range(256):
            if not 0x30 <= delimiter <= 0x39:
                check(list(b"7" * length) + [delimiter], length)
                special += 1
    report = {"method": "original_z80_bytes_without_assembly", "entry": 0xC6EA,
              "canonical_numbers_checked": 100000, "special_cases": special,
              "all_digit_strings_by_width": widths, "digit_strings_checked": sum(widths.values()),
              "total_cases": cases, "exact_CPU_stack_write_sequence_checked": True, "DE_BC_A_checked": True,
              "stack_bus_cycle_order_verified": False, "return_word_unchanged": True, "no_other_CPU_writes": True,
              "CPU_write_watch_positive_control": True, "physical_disk_and_sectors_checked": True,
              "original_disk_sha256": hashlib.sha256(disk).hexdigest(),
              "all_initial_R_values_covered": True, "R_bit7_preserved": True,
              "full_input_register_joint_product_checked": False,
              "arbitrary_input_or_stack_addresses_checked": False,
              "irq_executed": False, "native_execution": False,
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "first_character_must_be_digit": True, "passed": True, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/DecimalVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
