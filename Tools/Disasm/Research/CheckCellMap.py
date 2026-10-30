"""Адресация карты владельцев знакомест и точечное удаление индексной пары."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, SP


def add_flags(left, right):
    result = (left + right) & 255
    return ((result & 0xA8) | (0x40 if result == 0 else 0)
            | (0x10 if (left & 15) + (right & 15) > 15 else 0)
            | (4 if ~(left ^ right) & (left ^ result) & 128 else 0)
            | int(left + right > 255))


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0xBFFE, "HL": 0x1357, "DE": 0x2468, "BC": 0x369C,
                             "IX": 0x47AD, "IY": 0x5C3A, "^HL": 0x58BE,
                             "^DE": 0x69CF, "^BC": 0x7AD0, "^AF": 0x8BE1}, None, False)
    # Создание различимых содержимых четырёх страниц, включая внеэкранную четвёртую.
    memory[0x8600:0x8A00] = [(offset * 73 + (offset >> 8) * 19) & 255 for offset in range(1024)]
    lookup_cases = cursor_cases = search_cases = 0
    for row, column in product(range(256), range(256)):
        simulator.registers[:] = initial
        simulator.registers[B], simulator.registers[C] = row, column
        simulator.registers[F] = row ^ column
        simulator.run(start=0x9DA6, stop=0x3FFF)
        address = ((0x86 + ((row >> 3) & 3)) << 8) | ((((row & 7) << 5) + column) & 255)
        if (simulator.registers[H] * 256 + simulator.registers[L], simulator.registers[A], simulator.registers[F]) != (
                address, memory[address], add_flags((row & 7) << 5, column)):
            raise ValueError("Не совпал указатель или байт владельца знакоместа")
        for reg in (*range(2, 6), *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != (row if reg == B else column if reg == C else initial[reg]):
                raise ValueError("Изменён сохраняемый регистр адресации")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Неверный стек адресации")
        lookup_cases += 1
        # Проверка всех пиксельных координат, исходные байты курсора записаны как X, Y.
        memory[0x6307:0x6309] = [column, row]
        simulator.registers[:] = initial
        simulator.run(start=0x9D96, stop=0x3FFF)
        char_row, char_column = row >> 3, column >> 3
        pointer = 0x8600 + char_row * 32 + char_column
        if (simulator.registers[H] * 256 + simulator.registers[L], simulator.registers[A],
                simulator.registers[B], simulator.registers[C], simulator.registers[F]) != (
                    pointer, memory[pointer], char_row, char_column,
                    add_flags((char_row & 7) << 5, char_column)):
            raise ValueError("Не совпала выборка владельца под пиксельным курсором")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Неверный стек пиксельного входа")
        for reg in (*range(4, 6), *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Пиксельный вход изменил сохраняемый регистр")
        cursor_cases += 1
    keys = [((value << 8) | 0x34) for value in range(256)]
    keys += [0x1200 | value for value in range(256)]
    for key, position in product(keys, (0, 63, 64, 127, None, -1)):
        # Поиск должен удалить только первое совпадение, фоновый ключ отличается обоими байтами.
        background = (key ^ 0xFF00) if position == -1 else key ^ 0xFFFF
        data = list(background.to_bytes(2, "little")) * 128
        if position is not None and position >= 0:
            data[2 * position:2 * position + 2] = list(key.to_bytes(2, "little"))
            if position < 127:
                data[254:256] = list(key.to_bytes(2, "little"))
        memory[0x8500:0x8600] = data
        simulator.registers[:] = initial
        simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
        simulator.run(start=0xBE91, stop=0x3FFF)
        expected = data.copy()
        if position is not None and position >= 0:
            expected[2 * position + 1] = 255
            expected_a, expected_flags = key >> 8, 0x42 | ((key >> 8) & 0x28)
        else:
            compared = (background >> 8) if position == -1 else background & 255
            target = key >> 8 if position == -1 else key & 255
            expected_a, expected_flags = compared, 0x50 | int(compared < target)
        if memory[0x8500:0x8600] != expected:
            raise ValueError("Изменён неверный байт индексной пары")
        if (simulator.registers[A], simulator.registers[F]) != (expected_a, expected_flags):
            raise ValueError("Не совпали A или флаги результата поиска пары")
        if simulator.registers[SP] != 0xC000:
            raise ValueError("Неверный стек удаления индексной пары")
        for reg in (*range(2, 12), *range(16, 24)):
            if simulator.registers[reg] != (key >> 8 if reg == D else key & 255 if reg == E else initial[reg]):
                raise ValueError("Удаление пары изменило сохраняемый регистр")
        search_cases += 1
    buffer_cases = 0
    configs = [(value, flags) for value, flags in product(range(256), (0, 1, 0x40, 0x41, 0x80, 0x81, 0xC0, 0xC1))]
    configs += [(flags ^ 0x5A, flags) for flags in range(256)]
    for start, begin, size, fill in ((0x9EC4, 0x8600, 0x300, 0), (0x9ED7, 0x8500, 0x80, 255)):
        for value, flags in configs:
            # Создание различимого окружения проверяет размер записи и неизменность соседних областей.
            data = [(offset * 73 + value) & 255 for offset in range(0x600)]
            memory[0x8400:0x8A00] = data
            expected = data.copy()
            expected[begin - 0x8400:begin - 0x8400 + size] = [fill] * size
            simulator.registers[:] = initial
            simulator.registers[A], simulator.registers[F] = value, flags
            simulator.run(start=start, stop=0x3FFF)
            total = (value + fill) & 255
            expected_flags = (flags & 0xC1) | (total & 8) | ((total & 2) << 4)
            if memory[0x8400:0x8A00] != expected or (simulator.registers[A], simulator.registers[F]) != (value, expected_flags):
                raise ValueError("Не совпали границы заполнения или флаги LDIR")
            if simulator.registers[SP] != 0xC000:
                raise ValueError("Неверный стек заполнения таблицы")
            for reg in (*range(2, 12), *range(16, 24)):
                if simulator.registers[reg] != initial[reg]:
                    raise ValueError("Заполнение таблицы изменило сохраняемый регистр")
            buffer_cases += 1
    report = {"method": "original_z80_bytes_against_cell_address_and_pair_search",
              "lookup_cases": lookup_cases, "pixel_cursor_cases": cursor_cases,
              "pair_search_cases": search_cases, "buffer_cases": buffer_cases, "passed": True,
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "fourth_page_is_not_visible_screen": True,
              "full_background_restore_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/CellMapVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
