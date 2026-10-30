"""Изолированная проверка контрактов вступления на оригинальных Z80-байтах.

Не является запуском игры или её сборкой. Проверяет адресацию и формулы,
включая развёрнутый код и восстановление SP, на явно указанных входах.
"""

from pathlib import Path
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, SP, A, H, L, D, E


def original_memory():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    item = next(e for e in manifest["entries"] if e["slot"] == 3)
    data = (ROOT / (item["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6300:0x6300 + len(data)] = data
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    return memory


def word(memory, address, value=None):
    if value is None:
        return memory[address] + 256 * memory[address + 1]
    memory[address:address + 2] = [value & 255, (value >> 8) & 255]


def execute(memory, registers, stop=0x3FFF, limit=20000):
    simulator = Simulator(memory)
    simulator.registers[:] = get_registers({"SP": 0xBFFE, **registers}, None, False)
    # Проверка выхода по адресу возврата либо по явной границе исследуемого участка.
    for steps in range(limit):
        if simulator.registers[PC] == stop:
            return simulator, steps
        simulator.run()
    raise ValueError("Превышена граница исполнения процедуры вступления")


def require(condition, description):
    if not condition:
        raise ValueError(description)


def main():
    results = []
    values = [0, 1, 0x7FFF, 0x8000, 0xFFFF]
    # Проверка формулы всех трёх слов, сохранения третьего слова и возврата через исходный SP.
    for s0, s1, s2 in itertools.product(values, repeat=3):
        memory = original_memory()
        for index, value in enumerate((s0, s1, s2)):
            word(memory, 0x7000 + 2 * index, value)
        simulator, _ = execute(memory, {"PC": 0x6A2C, "HL": 0x7000})
        updated_s1 = (s1 + (-s2 if s0 & 0x8000 else s2)) & 65535
        expected = ((s0 + updated_s1) & 65535, updated_s1, s2)
        actual = tuple(word(memory, 0x7000 + 2 * index) for index in range(3))
        require(actual == expected, "Неверна формула AdvanceParameters")
        require(simulator.registers[A] == expected[0] >> 8, "Не совпал возвращаемый старший байт")
        require(simulator.registers[SP] == 0xC000, "SP не восстановлен в AdvanceParameters")
    results.append(dict(name="AdvanceParameters", fixtures=len(values) ** 3, passed=True))

    # Проверка всех 256 допустимых индексов строки указателей и изменяемого операнда.
    for index in range(256):
        memory = original_memory()
        simulator, _ = execute(memory, {"PC": 0x6C53, "A": index})
        expected = 0xF000 + 16 * index
        require(word(memory, 0x6BB2) == expected, "Неверный операнд адреса стека выборок")
        require(256 * simulator.registers[H] + simulator.registers[L] == expected, "Неверный выход HL")
        require(simulator.registers[A] == index, "A изменён в SelectTexturePointerRow")
    results.append(dict(name="SelectTexturePointerRow", fixtures=256, passed=True))

    # Проверка переноса последней пары таблицы через границу #FFFF в контролируемые байты ПЗУ.
    for rom_high in (0x00, 0x2C, 0xCE):
        memory = original_memory()
        memory[0xFE:0x100] = [0x49, rom_high]
        word(memory, 0x5FFE, 0x3FFF)
        simulator, _ = execute(memory, {"PC": 0x69B6, "SP": 0x5FFE})
        pointer = simulator.registers[H] * 256 + simulator.registers[L]
        simulator, _ = execute(memory, {"PC": 0x6763, "SP": 0x5FFE, "HL": pointer,
                                        "A": 0x2C, "IY": 0xC0}, limit=1000000)
        require(memory[0xFFFE:0x10000] == [0x49, rom_high], "Не подтверждено оборачивание указателя последней записи")
        require(simulator.registers[A] == rom_high, "Не подтверждена зависимость A от хвоста заполнения")
    results.append(dict(name="BuildTextureLookupRomBoundary", fixtures=3,
                        synthetic_rom_bytes=True, original_rom_required=False, passed=True))

    # Проверка адресации таблицы, шагов с переполнением младшего байта и неполной первой страницы.
    phase_cases = list(itertools.product((0, 3, 6, 9, 255), (0, 0x40, 0xFF)))
    for step, first_e in phase_cases:
        memory = original_memory()
        source = [(i * 37 + 11) & 255 for i in range(256)]
        memory[0x7000:0x7100] = source
        simulator, _ = execute(memory, {"PC": 0x6D6A, "HL": 0x70F9, "DE": 0x7400 + first_e, "BC": step})
        expected = [source[(0xF9 + i * step) & 255] >> 2 for i in range(256 - first_e)]
        require(memory[0x7400 + first_e:0x7500] == expected, "Неверный шаг BuildPhaseTable")
        require((simulator.registers[D], simulator.registers[E]) == (0x75, 0), "Неверный выход DE")
    results.append(dict(name="BuildPhaseTable", fixtures=len(phase_cases), passed=True))

    # Проверка порядка строк и столбцов при объединении двух независимых полубайтов.
    memory = original_memory()
    low = [(i * 19 + 13) & 255 for i in range(8)]
    high = [(i * 31 + 7) & 255 for i in range(8)]
    memory[0x7000:0x7008], memory[0x7100:0x7108] = low, high
    execute(memory, {"PC": 0x6964, "HL": 0x7000, "BC": 0x7100, "DE": 0x74C0})
    expected = [(h & 0xF0) | (l & 15) for l in low for h in high]
    require(memory[0x74C0:0x7500] == expected, "Переставлены строки либо столбцы атрибутов")
    results.append(dict(name="CombineAttributeNibbles", fixtures=64, passed=True))

    # Проверка фактически созданных цепочек, включая замену последних команд на RET и JP.
    memory = original_memory()
    pointer_template = memory[0x6D78:0x6D7E]
    sum_template = memory[0x6D7E:0x6D8D]
    execute(memory, {"PC": 0x6C9C}, stop=0x6CF9)
    expected_pointer = pointer_template * 64
    expected_pointer[-1:] = [0xC3, 0xED, 0x6B]
    require(memory[0x9100:0x9100 + len(expected_pointer)] == expected_pointer,
            "Неверно место завершающего JP цепочки #9100")
    expected_sum = sum_template * 256
    expected_sum[-2] = 0xC9
    require(memory[0x9900:0xA800] == expected_sum, "Неверно место RET цепочки #9900")
    expected_transfer = []
    for row in range(38):
        for column in range(8):
            expected_transfer.extend([0xE1, 0x22, 2 * column, 0xC0 + row])
    expected_transfer.extend([0xC3, 0xBC, 0x6B])
    require(memory[0xA800:0xA800 + len(expected_transfer)] == expected_transfer,
            "Неверны адреса либо завершающий JP цепочки #A800")
    results.append(dict(name="InitializeLookupEffectGeneratedCode", chains=3, passed=True))

    # Проверка писателя, созданного исходными инструкциями, и восстановления настоящего SP.
    memory = original_memory()
    execute(memory, {"PC": 0x692D, "IX": 0x80}, stop=0x694C)
    expected_code = []
    destinations = []
    for row in range(8):
        for column in range(4):
            destination = 0x8080 + 256 * row + 2 * column
            destinations.append(destination)
            expected_code.extend([0xE1, 0x22, destination & 255, destination >> 8])
    require(memory[0x68A9:0x6929] == expected_code, "Не совпало тело генерируемого писателя")
    payload = [(index * 23 + 3) & 255 for index in range(64)]
    memory[0x7000:0x7040] = payload
    simulator, _ = execute(memory, {"PC": 0x68A4, "HL": 0x7000})
    for index, destination in enumerate(destinations):
        require(memory[destination:destination + 2] == payload[2 * index:2 * index + 2], "Неверный адрес записи атрибутов")
    require(simulator.registers[SP] == 0xC000, "SP не восстановлен после генерируемого писателя")
    results.append(dict(name="BuildAttributeWriterAndRun", words=32, generated_code_bytes=128, passed=True))

    # Проверка двух исполняемых вариантов вставки, разрозненных источников и всех 38 строк.
    for patch in ([0, 0], [0x24, 0]):
        memory = original_memory()
        memory[0x6839:0x683B] = patch
        for row in range(38):
            pointer_table = 0x7200 + row * 64
            word(memory, 0x7100 + row * 4, pointer_table - (0x100 if patch[0] else 0))
            word(memory, 0x7102 + row * 4, 0x9000 + row * 32)
            for column in range(32):
                source_address = 0x8000 + row * 32 + (31 - column)
                word(memory, pointer_table + 2 * column, source_address)
                memory[source_address] = (row * 17 + column * 7) & 255
        simulator, _ = execute(memory, {"PC": 0x6827, "HL": 0x7100})
        expected = [(row * 17 + column * 7) & 255 for row in range(38) for column in range(32)]
        require(memory[0x9000:0x94C0] == expected, "Не совпала адресация ScatterTextureToScreen")
        require(simulator.registers[SP] == 0xC000, "SP не восстановлен после экранного переноса")
    results.append(dict(name="ScatterTextureToScreen", patches=2, bytes_per_patch=1216, passed=True))

    report = dict(method="isolated_original_z80_bytes", assembled_code_used=False,
                  emulator_boot_test=False, full_domain_proof=False, results=results)
    (ROOT / "Tools/Disasm/Reports/IntroVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
