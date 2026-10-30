"""Проверка поиска физических записей и записи бинарных операторов, без сборки."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP, IXh, IXl, xD, xE, xH, xL


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    memory = [0] * 65536
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    def pair(high, low):
        return 256 * simulator.registers[high] + simulator.registers[low]

    def execute(config, stop=0x3FFF):
        simulator.registers[:] = get_registers({"SP": 0xBFFE, "IY": 0x5C3A, **config}, None, False)
        for _ in range(2000):
            if simulator.registers[PC] == stop:
                return
            simulator.run()
        raise ValueError("Поиск токена не достиг ожидаемого выхода")

    # Проверка поиска первого совпадения в каждой из четырёх физических групп.
    records_checked = 0
    for begin, end in ((0x935, 0x962), (0x962, 0x983), (0x983, 0x9EF), (0x9EF, 0xA67)):
        symbols = list(source[begin:end:3])
        for symbol in symbols:
            index = symbols.index(symbol)
            execute({"PC": 0xC7E3, "HL": 0xC000 + begin - 3,
                     "BC": len(symbols) * 256 + 0x5A, "A": symbol})
            if (pair(H, L) != 0xC000 + begin + index * 3 or pair(D, E) != 3
                    or simulator.registers[B] != len(symbols) - index or simulator.registers[C] != 0x5A
                    or simulator.registers[A] != symbol or not simulator.registers[F] & 0x40
                    or simulator.registers[SP] != 0xC000):
                raise ValueError("Не совпало состояние найденной записи FScriptToken")
            records_checked += 1
    # Проверка нулевого счётчика на синтетической таблице из 256 разных символов.
    for index in range(256):
        memory[0x7000 + index * 3:0x7003 + index * 3] = [index, 0, 0]
    for symbol in range(256):
        execute({"PC": 0xC7E3, "HL": 0x6FFD, "BC": 0x005A, "A": symbol})
        if pair(H, L) != 0x7000 + symbol * 3 or simulator.registers[B] != (256 - symbol) & 255:
            raise ValueError("B=0 не соответствует 256 записям")
    # Проверка неуспешного поиска до хвостового входа SkipLine, без исполнения остального сценария.
    execute({"PC": 0xC7E3, "HL": 0xC95F, "BC": 11 * 256, "A": 0xFF}, stop=0xC01B)
    if simulator.registers[B] != 0:
        raise ValueError("Неуспешный поиск не исчерпал таблицу")
    # Проверка записи всех одиннадцати адресов операторов через альтернативный HL.
    for offset in range(0x962, 0x983, 3):
        symbol = source[offset]
        target = int.from_bytes(source[offset + 1:offset + 3], "little")
        memory[0x7000] = symbol
        execute({"PC": 0xC79C, "IX": 0x7000, "^HL": 0x9000, "^BC": 0x1357, "^AF": 0x2468})
        if (memory[0x9000] + 256 * memory[0x9001] != target
                or pair(xH, xL) != 0x9002 or pair(xD, xE) != target
                or pair(D, E) != target or pair(IXh, IXl) != 0x7001
                or simulator.registers[SP] != 0xC000):
            raise ValueError("EmitOperator не записал правильный указатель")
    report = {"method": "original_z80_bytes_without_assembly", "table_records_checked": records_checked,
              "zero_counter_cases": 256, "missing_symbol_tail_checked": True,
              "operators_emitted": 11, "source_sha256": hashlib.sha256(source).hexdigest(),
              "whole_script_verified": False, "passed": True, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/TokenDispatchVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
