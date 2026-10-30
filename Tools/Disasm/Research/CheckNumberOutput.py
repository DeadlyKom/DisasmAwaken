"""Проверка исходного числового вывода с исполнением глифа в режиме продвижения без пикселей."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, PC, SP
from InspectZ80 import decoder
from CheckGlyphRenderer import and_flags


def legacy_digits(value):
    if value < 1000:
        return [ord(char) for char in str(value)]
    return [48+value//1000, 48+(value//100)%10, 48+(value//10)%10, 48+value%10]


def expected_codes(entry, value, budget):
    if entry == 0xBC01:
        digits = [ord(char) for char in str(value)]
        if value >= 10000:
            return digits
        # Подсчёт дополнения повторяет байтовый DEC и проверку Sign, включая нетипичные A.
        zeros = 0
        for threshold in (9999, 999, 99, 9):
            if value <= threshold:
                budget = (budget-1) & 255
                zeros += budget < 128
        return [48]*zeros + digits
    minimum = {0xBCAB: 1, 0xBBBE: 2, 0xBBD7: 3, 0xBBA8: 4}[entry]
    digits = legacy_digits(value)
    return [48]*max(0, minimum-len(digits)) + digits


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:0x6000+len(source)] = source
    # Это тот же временный JP, который исходный код использует для расчёта продвижения.
    memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5]
    simulator = Simulator(memory)
    dis = decoder([0]*0x6000 + list(source))
    visited, lengths = {}, {}
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "IX": 0x2468,
                             "IY": 0x5C3A, "^HL": 0x369C, "^DE": 0x47AD,
                             "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    counts = {}
    cases = 0

    def execute(start, value, budget=0, limit=255, cursor=0, height=192):
        nonlocal cases
        codes = expected_codes(start, value, budget)
        expected_attempts = []
        next_cursor = cursor
        expected_a, expected_f = 0, 0x45
        for code in codes:
            expected_attempts.append(code)
            total = next_cursor + source[0x2900+code]
            if height == 0:
                expected_a, expected_f = 2, and_flags(0)
                break
            if total > 255 or total >= limit:
                expected_a, expected_f = 3, and_flags(total & 255)
                break
            next_cursor = total
        for address, byte in ((0x6320, cursor), (0x6321, 0), (0xAEAB, height), (0xAEB3, limit),
                              (0xAEBB, 0), (0xAEBF, 0), (0xAEC7, 0), (0xAECB, 0)):
            memory[address] = byte
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[PC] = start
        simulator.registers[A], simulator.registers[F] = budget, (value ^ budget) & 255
        simulator.registers[B], simulator.registers[C] = value >> 8, value & 255
        before = simulator.registers.copy()
        attempts = []
        last_bc = None
        for _ in range(1800):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if pc == 0xAE8D:
                attempts.append(simulator.registers[A])
                last_bc = simulator.registers[B]*256 + simulator.registers[C]
                sp = simulator.registers[SP]
                return_pc = memory[sp] + 256*memory[sp+1]
                simulator.run(stop=return_pc)
                continue
            if not 0xBBA8 <= pc <= 0xBD00:
                raise ValueError(f"Неожиданный вход числового вывода #{pc:04X}")
            if pc not in lengths:
                instruction = dis.disassemble(pc, pc+1, "h")[0]
                lengths[pc] = len(instruction.bytes)
            length = lengths[pc]
            data = bytes(memory[pc:pc+length])
            if data != source[pc-0x6000:pc-0x6000+length]:
                raise ValueError("Числовой код изменён во время проверки")
            visited[f"{pc:04X}"] = data.hex()
            simulator.run()
        else:
            raise ValueError("Числовой вывод не завершился")
        if attempts != expected_attempts:
            raise ValueError(f"Не совпали коды start={start:04X}, value={value}, A={budget}, actual={attempts}, expected={expected_attempts}")
        if (simulator.registers[A], simulator.registers[F], memory[0x6320], simulator.registers[SP]) != (
                expected_a, expected_f, next_cursor, 0x8000):
            raise ValueError("Не совпали статус или продвижение числового вывода")
        if simulator.registers[B]*256+simulator.registers[C] != last_bc:
            raise ValueError("После последнего глифа неожиданно изменён BC")
        for reg in (*range(4, 12), *range(16, 24)):
            if simulator.registers[reg] != before[reg]:
                raise ValueError("Числовой вывод изменил сохраняемый регистр")
        counts[f"{start:04X}"] = counts.get(f"{start:04X}", 0)+1
        cases += 1

    for value in range(65536):
        execute(0xBCAB, value)
        execute(0xBC01, value, 0)
        execute(0xBC01, value, 4)
        if value < 10000:
            for start in (0xBBBE, 0xBBD7, 0xBBA8):
                execute(start, value)
            for budget in (1, 2, 3):
                execute(0xBC01, value, budget)
        if (value+1) % 8192 == 0:
            print(f"Проверены числовые значения {value+1}/65536", flush=True)
    # Проверка всех байтов бюджета на границах десятичных разрядов и знакового перехода DEC.
    budget_values = (0, 1, 8, 9, 10, 11, 98, 99, 100, 101, 998, 999,
                     1000, 1001, 9998, 9999, 10000, 10001, 65534, 65535)
    for value in budget_values:
        for budget in range(256):
            execute(0xBC01, value, budget)
    for value in (0, 1, 9, 10, 99, 100, 999, 1000, 9999, 10000, 65535):
        for start in (0xBCAB, 0xBC01, 0xBBBE, 0xBBD7, 0xBBA8):
            for limit, cursor, height in ((0, 0, 192), (1, 0, 192), (5, 0, 192),
                                           (10, 1, 192), (20, 0, 192), (255, 254, 192), (255, 0, 0)):
                execute(start, value, 4 if start == 0xBC01 else 0, limit, cursor, height)
    report = dict(method="original_number_output_with_original_glyph_measurement_mode",
                  cases=cases, by_entry=counts, passed=True,
                  source_sha256=hashlib.sha256(source).hexdigest(),
                  glyph_function_stubbed=False, glyph_pixels_disabled=True,
                  integer_word_full_range_checked=True, legacy_core_over_9999_is_not_full_decimal=True,
                  budget_byte_cases=256*len(budget_values),
                  native_execution_verified=False, assembly_executed=False,
                  original_visited=dict(sorted(visited.items())))
    (ROOT / "Tools/Disasm/Reports/NumberOutputVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
