"""Проверка построителя финального экрана и созданной им цепочки, без IRQ."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, SP, H, L


def screen_offset(y):
    return ((y & 7) << 8) | ((y & 0x38) << 2) | ((y & 0xC0) << 5)


def word(memory, address, value=None):
    if value is None:
        return memory[address] + 256 * memory[address + 1]
    memory[address:address + 2] = [value & 255, value >> 8]


def original_memory():
    memory = [0] * 65536
    data = (ROOT / "Tools/Disasm/Extracted/Active/29_FINALF.C.bin").read_bytes()
    memory[0x6000:0x6000 + len(data)] = data
    word(memory, 0xBFFE, 0x3FFF)
    return memory


def require(condition, text):
    if not condition:
        raise ValueError(text)


def run(simulator, registers, limit=100000):
    simulator.registers[:] = get_registers({"SP": 0xBFFE, **registers}, None, False)
    for steps in range(limit):
        if simulator.registers[PC] == 0x3FFF:
            require(simulator.registers[SP] == 0xC000, "Не восстановлен стек финального обработчика")
            return steps
        simulator.run()
    raise ValueError("Не достигнут возврат из финального обработчика")


class Keyboard:
    def __init__(self, key):
        self.key = key

    def read_port(self, registers, port):
        return 0xFE if port == ({"Q": 0xFBFE, "A": 0xFDFE}.get(self.key)) else 0xFF


def main():
    memory = original_memory()
    simulator = Simulator(memory)
    # Проверка всех допустимых строк и столбцов стандартной экранной адресации.
    for y in range(192):
        for column in (0, 15, 16, 31):
            run(simulator, {"PC": 0x6296, "HL": 0x4000 + screen_offset(y) + column})
            expected = 0x4000 + screen_offset(y + 1) + column if y < 191 else 0x5800 + column
            require(simulator.registers[H] * 256 + simulator.registers[L] == expected,
                    "Не совпал адрес следующей строки bitmap")
    # Проверка ограничений задержки и точного выбора двух строк клавиатуры.
    key_cases = []
    for key in (None, "Q", "A"):
        simulator.set_tracer(Keyboard(key))
        for delay in (0, 1, 50, 99, 100):
            memory[0x60D4] = delay
            run(simulator, {"PC": 0x6123})
            expected = max(0, delay - 1) if key == "Q" else min(100, delay + 1) if key == "A" else delay
            require(memory[0x60D4] == expected, "Не совпал счётчик задержки по клавише")
            key_cases.append(dict(key=key, initial_delay=delay, actual_delay=expected))

    # Создание независимого ожидаемого размещения 192 строк, 24 рядов атрибутов и двух вставок.
    memory = original_memory()
    bitmap_template = memory[0x6247:0x627B]
    attribute_template = memory[0x627D:0x6294]
    expected = [0xED, 0x73, 0, 0]
    slots = {}
    for cell_row in range(24):
        for line in range(8):
            offset = screen_offset(8 * cell_row + line)
            chunk = bitmap_template.copy()
            for field, value in ((1, 0xC000 + offset), (14, 0x4010 + offset),
                                 (27, 0xC010 + offset), (40, 0x4020 + offset)):
                word(chunk, field, value)
            expected += chunk
        chunk = attribute_template.copy()
        word(chunk, 5, 0x5820 + 32 * cell_row)
        expected += chunk
        counter = 24 - cell_row
        if counter in (7, 15):
            address = 0x8000 + len(expected)
            slots[counter] = address
            expected += memory[address:address + 4]
    restore_operand = 0x8000 + len(expected) + 1
    word(expected, 2, restore_operand)
    expected += [0x31, memory[restore_operand], memory[restore_operand + 1], 0xC9]
    simulator = Simulator(memory)
    build_steps = run(simulator, {"PC": 0x6196})
    differences = [(0x8000 + index, actual, reference) for index, (actual, reference)
                   in enumerate(zip(memory[0x8000:0x8000 + len(expected)], expected)) if actual != reference]
    require(not differences, "Созданная цепочка отличается от схемы экранных строк " + repr(differences[:8]))
    require(word(memory, 0x62A5) == slots[7] and word(memory, 0x62A7) == slots[15],
            "Не совпали адреса двух мест синхронизации")
    # Исполнение цепочки с отключёнными вставками IRQ на контролируемом bitmap и цвете.
    for address in slots.values():
        memory[address:address + 4] = [0, 0, 0, 0]
    source = [(index * 47 + 19) & 255 for index in range(6144)]
    memory[0xC000:0xD800] = source
    memory[0x4000:0x5B00] = [0] * 6912
    run_steps = run(simulator, {"PC": 0x8000, "^A": 0x90})
    require(memory[0x4000:0x5800] == source, "Созданная цепочка исказила bitmap")
    require(memory[0x5800:0x5B00] == [0x90] * 768, "Созданная цепочка исказила атрибуты")
    report = dict(method="original_builder_and_generated_code_in_isolated_model",
                  passed=True, native_final_scene_verified=False, real_irq_verified=False,
                  bitmap_line_fixtures=192 * 4, keyboard_cases=key_cases,
                  generated_size=len(expected), generated_start=0x8000,
                  synchronization_slots={str(key): value for key, value in slots.items()},
                  build_steps=build_steps, generated_execution_steps=run_steps,
                  bitmap_bytes_verified=6144, attribute_bytes_verified=768,
                  stack_restored=True)
    (ROOT / "Tools/Disasm/Reports/FinalVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Final: 768 line fixtures, 15 key cases,", len(expected), "generated bytes, full bitmap and attributes verified")


if __name__ == "__main__":
    main()
