"""Проверка арифметики и записи эффектов VOXAL на оригинальных байтах."""

from pathlib import Path
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, SP, H, L, D, E, IYh, IYl


def memory_image():
    memory = [0] * 65536
    for name, origin in (("20_VOXAL0.C.bin", 0xC000), ("21_VOXAL.C.bin", 0xEC00)):
        data = (ROOT / "Tools/Disasm/Extracted/Active" / name).read_bytes()
        memory[origin:origin + len(data)] = data
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    return memory


def run(simulator, registers):
    simulator.registers[:] = get_registers({"SP": 0xBFFE, **registers}, None, False)
    for steps in range(2000):
        if simulator.registers[PC] == 0x3FFF:
            if simulator.registers[SP] != 0xC000:
                raise ValueError("Не восстановлен стек процедуры VOXAL")
            return
        simulator.run()
    raise ValueError("Не достигнут возврат из процедуры VOXAL")


def pair(simulator, high, low):
    return 256 * simulator.registers[high] + simulator.registers[low]


def require(condition, text):
    if not condition:
        raise ValueError(text)


def signed(value):
    return value if value < 32768 else value - 65536


def seeded_formula(left, right, seed):
    magnitude_left, magnitude_right = abs(signed(left)), abs(signed(right))
    high_partial = (2 * magnitude_left * ((magnitude_right >> 6) & 255)) & 0xFFFF0000
    wide = (high_partial + seed) * 64 + 2 * magnitude_left * (magnitude_right & 63)
    magnitude = wide >> 15
    return (-magnitude if (left ^ right) & 0x8000 else magnitude) & 65535


def main():
    simulator = Simulator(memory_image())
    multiply_count = 0
    # Проверка игнорируемого старшего бита множителя на всём диапазоне A и граничных BC.
    for multiplier, value in itertools.product(range(256), (0, 1, 127, 65535)):
        run(simulator, {"PC": 0xF931, "A": multiplier, "BC": value})
        require(pair(simulator, H, L) == ((multiplier & 127) * value) & 65535,
                "Не совпало умножение младших семи битов")
        multiply_count += 1
    division_count = 0
    division_outside_domain = []
    division_outside_mismatches = 0
    # Проверка частного с восемью дробными битами, A имеет только семь значащих битов.
    for numerator, denominator in itertools.product(range(256), range(1, 256)):
        run(simulator, {"PC": 0xF957, "A": numerator, "DE": denominator})
        expected = ((numerator & 127) << 8) // denominator
        actual = pair(simulator, D, E)
        if denominator <= 128:
            require(actual == expected, f"Не совпало деление, A={numerator}, E={denominator}")
        elif actual != expected:
            division_outside_mismatches += 1
            if len(division_outside_domain) < 10:
                division_outside_domain.append(dict(numerator=numerator, denominator=denominator,
                                                    actual=actual, expected=expected))
        division_count += 1
    # Проверка зависимости знакового обработчика от входного IY, включая пределы значений.
    words = (0, 1, 1000, 16383, 16384, 32767, 32768, 64536, 65535)
    seeded_count = 0
    for left, right, seed in itertools.product(words, words, (0, 1, 0x5C3A, 65535)):
        run(simulator, {"PC": 0xE8A1, "HL": left, "BC": right, "IY": seed})
        expected = seeded_formula(left, right, seed)
        require(pair(simulator, H, L) == expected,
                f"Не совпала формула с входным IY, HL={left}, BC={right}, IY={seed}")
        seeded_count += 1
    records = []
    # Проверка обхода трёх преобразований при нулевых углах, девять исходных слов должны сохраниться.
    memory = memory_image()
    matrix = [(index * 43 + 17) & 255 for index in range(18)]
    memory[0x9B00:0x9B12] = matrix
    memory[0x9B12:0x9B15] = [0, 0, 0]
    simulator = Simulator(memory)
    run(simulator, {"PC": 0xE500, "IY": 0x5C3A})
    require(memory[0x9B00:0x9B12] == matrix, "Нулевые углы изменили исходные векторы")
    # Проверка заполнения свободной записи, пропуска занятой и остановки по отрицательному признаку.
    for address, source, parameter, field0d, last in ((0xEC00, 0xD800, 0x00C0, 0x0D, 0x0C),
                                                    (0xEC1B, 0xC400, 0x0280, 0x08, 0x14)):
        for occupied in (0, 1):
            memory = memory_image()
            memory[0x7000:0x7036] = [0xA5] * 0x36
            memory[0x7007] = occupied
            memory[0x7019] = 0
            memory[0x702B] = 0x80
            simulator = Simulator(memory)
            run(simulator, {"PC": address, "IY": 0x6FEE, "A": 0x23, "^A": 2,
                            "^HL": 0x1122, "^DE": 0x3344, "^BC": 0x5566})
            selected = 0x7000 + 18 * occupied
            expected = [0x22, 0x11, 0x44, 0x33, 0x66, 0x55, 0x23, 2,
                        source & 255, source >> 8, source & 255, source >> 8,
                        1, field0d, parameter & 255, parameter >> 8, last, last]
            require(memory[selected:selected + 18] == expected, "Не совпала структура созданного эффекта")
            require(pair(simulator, IYh, IYl) == selected, "IY не указывает на выбранную запись")
            records.append(dict(entry=address, skipped_occupied=occupied, record=expected))
        memory = memory_image()
        memory[0x7007] = 0x80
        simulator = Simulator(memory)
        before = memory[0x7000:0x7012]
        run(simulator, {"PC": address, "IY": 0x6FEE})
        require(memory[0x7000:0x7012] == before, "Отрицательная завершающая запись изменена")
    report = dict(method="isolated_original_z80_bytes", passed=True,
                  multiply_fixtures=multiply_count, division_fixtures=division_count,
                  division_proved_denominator_range=[1, 128], division_full_nonzero_byte_domain=False,
                  division_outside_mismatches=division_outside_mismatches,
                  division_outside_examples=division_outside_domain, seeded_fixtures=seeded_count,
                  seeded_multiply_is_ordinary_product=False, effect_records=records,
                  zero_angle_basis_preserved=True,
                  full_game_verified=False)
    (ROOT / "Tools/Disasm/Reports/EffectsVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
