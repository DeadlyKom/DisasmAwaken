"""Проверка десятичного считывателя на исходных байтах LANG.C, без сборки."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, H, L, PC, SP, IXh, IXl, IYh, IYl


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    memory = [0] * 65536
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    def check(data, digits):
        # Проверка значения, положения курсора и сохранения альтернативного набора.
        memory[0x7000:0x7000 + len(data)] = data
        simulator.registers[:] = get_registers(
            {"PC": 0xC6EA, "SP": 0xBFFE, "IX": 0x7000, "IY": 0x5C3A,
             "HL": 0x1357, "DE": 0x2468, "BC": 0x9ABC}, None, False)
        simulator.registers[16:24] = [3, 17, 31, 43, 59, 71, 89, 101]
        for _ in range(150):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise ValueError("Десятичный считыватель не вернулся")
        value = int(bytes(data[:digits])) & 0xFFFF
        actual = simulator.registers[H] * 256 + simulator.registers[L]
        cursor = simulator.registers[IXh] * 256 + simulator.registers[IXl]
        if actual != value or cursor != 0x7000 + digits:
            raise ValueError(f"Неверно прочитано число {bytes(data)!r}, результат {actual}, курсор {cursor:04X}")
        if (simulator.registers[SP] != 0xC000
                or simulator.registers[IYh] * 256 + simulator.registers[IYl] != 0x5C3A
                or simulator.registers[16:24] != [3, 17, 31, 43, 59, 71, 89, 101]):
            raise ValueError("Не сохранён стек, IY или альтернативные регистры")

    # Проверка полного диапазона чисел длиной от одной до пяти цифр.
    for number in range(100000):
        text = str(number).encode("ascii")
        check(list(text + b";"), len(text))
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
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "first_character_must_be_digit": True, "passed": True, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/DecimalVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
