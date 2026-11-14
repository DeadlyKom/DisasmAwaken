"""Проверка записи бинарного вызова и возврата результата на оригинальном Z80."""

from pathlib import Path
import hashlib
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from CheckGeometryReturnEntries import Memory
from skoolkit.simutils import get_registers, A, B, C, D, E, H, L, PC, SP, xD, xE, xH, xL


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    # Проверка физических секторных байтов исходного LANG.
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_bytes())
    entry = next(e for e in manifest["entries"] if e["slot"] == 5)
    sectors = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    disk = (ROOT / "Tools/Disasm/Disk/original.trd").read_bytes()
    assert hashlib.sha256(disk).hexdigest() == manifest["sha256"]
    assert source == sectors[:entry["length"]]
    assert sectors == disk[entry["offset"]:entry["offset"] + entry["allocated_length"]]
    assert hashlib.sha256(sectors).hexdigest() == entry["sectors_sha256"]
    # Проверка наблюдателя собственных записей инструкцией CPU.
    probe = Memory(65536)
    probe[0x4000:0x4003] = bytes.fromhex("320070")
    probe_cpu = Simulator(probe)
    probe_cpu.registers[24] = 0x4000
    probe.recording = True
    probe_cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(65536)
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    def word(address, value):
        memory[address:address + 2] = [value & 255, value >> 8]

    def pair(high, low):
        return 256 * simulator.registers[high] + simulator.registers[low]

    def run(left, handler, right):
        memory.recording = False
        word(0x9000, left)
        word(0x9002, handler)
        word(0x9004, right)
        simulator.registers[:] = get_registers(
            {"PC": 0xC825, "SP": 0xBFFE, "^HL": 0x9006,
             "^BC": 0x1357, "^AF": 0x2468, "IX": 0x789A, "IY": 0x5C3A, "A": 0xDB}, None, False)
        memory.writes.clear()
        memory.recording = True
        for _ in range(150):
            if simulator.registers[PC] == 0x3FFF:
                memory.recording = False
                if handler == 0x3FFF:
                    # Расчёт записей до хвостового входа, без исполнения обработчика.
                    expected = [(0xBFFC, 0xB9), (0xBFFD, 0xC1)]
                    for value in (left, handler, right):
                        expected.extend(((0xBFFA, value & 255), (0xBFFB, value >> 8)))
                    assert memory.writes == expected, (left, right, memory.writes)
                    assert memory[0xBFFE:0xC000] == bytes([0xFF, 0x3F])
                    assert bytes(memory[0x9000:0x9006]) == b''.join(
                        value.to_bytes(2, "little") for value in (left, handler, right))
                return
            simulator.run()
        raise ValueError("Диспетчер бинарного выражения не завершился")

    # Проверка состояния непосредственно при хвостовом входе в произвольный обработчик.
    run(0x1357, 0x3FFF, 0x2468)
    if (pair(D, E), pair(H, L), pair(B, C), pair(xH, xL), pair(xD, xE), simulator.registers[SP], simulator.registers[A]) != (
            0x1357, 0x3FFF, 0x2468, 0x9000, 0xFFFB, 0xBFFC, 0xDB):
        raise ValueError("Неверно извлечены поля записи вызова")
    if memory[0xBFFC:0xBFFE] != bytes([0xB9, 0xC1]):
        raise ValueError("Не создан возврат в PushExpressionWord")
    # Проверка всех правых слов при различающемся левом слове на границе обработчика.
    boundary_cases = 1
    for right in range(65536):
        left = right ^ 0x5AA5
        run(left, 0x3FFF, right)
        assert (pair(D, E), pair(H, L), pair(B, C), pair(xH, xL),
                pair(xD, xE), simulator.registers[SP], simulator.registers[A]) == (
                left, 0x3FFF, right, 0x9000, 0xFFFB, 0xBFFC, 0xDB)
        boundary_cases += 1
    functions = {
        0xC488: lambda left, right: min(left + right, 65535),
        0xC491: lambda left, right: max(left - right, 0),
        0xC4C6: lambda left, right: left & right,
        0xC4CD: lambda left, right: left | right,
        0xC3D5: lambda left, right: int(left == right),
        0xC49C: lambda left, right: int(left < right),
    }
    values = (0, 1, 2, 127, 128, 255, 256, 257, 32767, 32768, 65535)
    cases = 0
    for handler, calculate in functions.items():
        for left, right in itertools.product(values, repeat=2):
            # Проверка полного пути через реальный обработчик и возврат результата на стек выражений.
            run(left, handler, right)
            expected = calculate(left, right)
            if (memory[0x9000] + 256 * memory[0x9001] != expected
                    or pair(xH, xL) != 0x9002 or pair(D, E) != expected
                    or simulator.registers[SP] != 0xC000):
                raise ValueError("Три слова вызова не заменились одним правильным результатом")
            cases += 1
    report = {"method": "original_z80_bytes_without_assembly", "entry": 0xC825,
              "call_boundary_checked": True, "handlers": len(functions), "full_calls_checked": cases,
              "boundary_cases": boundary_cases, "all_right_words_with_correlated_left_checked": True,
              "full_left_handler_right_cartesian_product_checked": False,
              "exact_own_CPU_writes_at_boundary_checked": True, "no_expression_writes_before_handler": True,
              "CPU_write_watch_positive_control": True, "stack_bus_cycle_order_verified": False,
              "physical_disk_and_sector_hashes_checked": True,
              "original_disk_sha256": hashlib.sha256(disk).hexdigest(),
              "arbitrary_stack_and_expression_addresses_checked": False,
              "irq_executed": False, "native_execution": False,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "arbitrary_handler_correctness_proved": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/ExpressionCallVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
