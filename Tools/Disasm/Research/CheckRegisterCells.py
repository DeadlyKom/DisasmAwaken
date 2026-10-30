"""Регистрация интерфейсного элемента в таблице пар и видимом прямоугольнике карты."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, SP, xA, xF
from CheckInsetFrame import bitmap_address


def main(fill_item=False):
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    stack = 0x7FFE if fill_item else 0xBFFE
    memory[stack:stack + 2] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    if fill_item:
        # Перенос и исполнение исходного построителя адресных таблиц только для проверки заливки bitmap.
        flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
        for region in flow:
            if region["name"] == "StationBoot":
                for instruction in region["instructions"]:
                    if 0x41B7 <= instruction["address"] < 0x41E3:
                        raw = bytes.fromhex(instruction["hex"])
                        if source[instruction["offset"]:instruction["offset"] + len(raw)] != raw:
                            raise ValueError("Не совпали байты построителя таблиц")
                        start = instruction["address"]
                        memory[start:start + len(raw)] = raw
        simulator.run(start=0x41B7, stop=0x41E3)
    initial = get_registers({"SP": stack, "IX": 0x1357, "IY": 0x5C3A,
                             "^HL": 0x2468, "^DE": 0x369C, "^BC": 0x47AD, "^AF": 0x58BE}, None, False)
    cases = 0
    keys = (0, 45) if fill_item else (0, 45, 0x1234, 0xFFF0)
    for key, free, previous, row, column, height, width in product(
            keys, (0, 63, 64, 127), (False, True),
            (-2, 0, 12, 23), (-2, 0, 17, 31), (1, 3, 24), (1, 3, 32)):
        end_x, end_y = min(32, column + width), min(24, row + height)
        x, y = max(0, column), max(0, row)
        if end_x <= x or end_y <= y:
            continue
        # Создание таблицы с известной свободной парой и необязательной предыдущей регистрацией.
        pairs = [0x80 + index for index in range(128)]
        pairs[free] = 0xFF80
        if previous:
            old = {0: 63, 63: 0, 64: 127, 127: 64}[free]
            pairs[old] = key
        expected_pairs = pairs.copy()
        for index, value in enumerate(expected_pairs):
            if value == key:
                expected_pairs[index] = (value & 255) | 0xFF00
                break
        slot = next(index for index, value in enumerate(expected_pairs) if value >> 8 == 255)
        expected_pairs[slot] = key
        data = [byte for value in pairs for byte in value.to_bytes(2, "little")]
        memory[0x8500:0x8600] = data
        # Проверка всей страницы таблицы и всей видимой карты обнаруживает лишние записи.
        background = [(index * 73 + 19) & 255 for index in range(0x400)]
        memory[0x8600:0x8A00] = background
        expected_map = background.copy()
        owner = slot + 1
        for visible_y in range(y, end_y):
            expected_map[32 * visible_y + x:32 * visible_y + end_x] = [owner] * (end_x - x)
        if fill_item:
            record = 0xF0FD + 16 * key
            memory[record:record + 4] = [column & 255, row & 255, width, height]
            fill = 0 if (height ^ width ^ free) & 1 else 255
            memory[0x99B4] = int(fill == 0)
            memory[0x4000:0x6000] = [0x96] * 0x2000
            expected_bitmap = memory[0x4000:0x6000].copy()
            for py in range(8 * y, 8 * end_y):
                start = bitmap_address(py, x) - 0x4000
                expected_bitmap[start:start + end_x - x] = [fill] * (end_x - x)
        simulator.registers[:] = initial
        simulator.registers[H], simulator.registers[L] = key >> 8, key & 255
        simulator.registers[B], simulator.registers[C] = row & 255, column & 255
        simulator.registers[D], simulator.registers[E] = height, width
        simulator.registers[A], simulator.registers[F] = (key + width) & 255, (height ^ row) & 255
        before = simulator.registers.copy()
        simulator.run(start=0xBFAD if fill_item else 0xBEAE, stop=0x3FFF)
        expected_data = [byte for value in expected_pairs for byte in value.to_bytes(2, "little")]
        if memory[0x8500:0x8600] != expected_data or memory[0x8600:0x8A00] != expected_map:
            raise ValueError("Не совпали индексные пары или видимая карта владельцев")
        pointer = 0x8600 + 32 * end_y + x
        if end_x - x == 1:
            saved_flags = 0x84 if owner == 128 else 0
        else:
            last_low = (32 * (end_y - 1) + end_x - 1) & 255
            saved_flags = last_low & 0x80
        flags = saved_flags | ((pointer >> 8) & 0x28)
        stride = 32 - (end_x - x)
        alternate_flags = ((stride + 1) & 0x28) | (0x10 if stride & 15 == 15 else 0)
        expected_a = owner
        if fill_item:
            pointer = record + 4
            expected_a = x if end_y % 8 == 0 else bitmap_address(end_y * 8) >> 8
            flags = 0x43 if end_y % 8 == 0 else 0x42
            if memory[0x4000:0x6000] != expected_bitmap or memory[0x6320:0x6322] != [0, 0]:
                raise ValueError("Не совпал bitmap или сброс текстового курсора обёртки")
            if (simulator.registers[D], simulator.registers[E], simulator.registers[B], simulator.registers[C]) != (0, end_x-x, y, x):
                raise ValueError("Не совпали отсечённые геометрические параметры обёртки")
        if (simulator.registers[H] * 256 + simulator.registers[L], simulator.registers[A], simulator.registers[F],
                simulator.registers[xA], simulator.registers[xF], simulator.registers[SP]) != (
                    pointer, expected_a, flags, 2 * stride, alternate_flags, stack + 2):
            raise ValueError(f"Контракт row={row}, col={column}, h={height}, w={width}, owner={owner}, "
                             f"actual={[simulator.registers[r] for r in (H,L,A,F,xA,xF,SP)]}, "
                             f"expected={[pointer>>8,pointer&255,expected_a,flags,2*stride,alternate_flags,stack+2]}")
        preserved = (*range(8, 12), *range(18, 24)) if fill_item else (*range(2, 6), *range(8, 12), *range(18, 24))
        for reg in preserved:
            if simulator.registers[reg] != before[reg]:
                raise ValueError("Регистрация изменила сохраняемый регистр")
        cases += 1
    report = {"method": "original_z80_bytes_against_pair_allocation_and_clipped_cell_rectangle",
              "cases": cases, "passed": True, "source_sha256": hashlib.sha256(source).hexdigest(),
              "free_slots": [0, 63, 64, 127], "keys": list(keys), "previous_registration_checked": True,
              "bitmap_fill_checked": fill_item,
              "synthetic_pair_table": True, "no_free_slot_checked": False,
              "fully_invisible_rectangles_checked": False, "assembly_executed": False}
    report_name = "RegisteredBitmapVerification.json" if fill_item else "RegisterCellsVerification.json"
    (ROOT / "Tools/Disasm/Reports" / report_name).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fill-item", action="store_true")
    main(parser.parse_args().fill_item)
