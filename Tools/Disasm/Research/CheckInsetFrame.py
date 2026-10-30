"""Изолированная сверка рамки #C436 с моделью экранных строк, без сборки и IRQ."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, PC, SP


def bitmap_address(y, x=0):
    return 0x4000 | ((y & 7) << 8) | ((y & 0x38) << 2) | ((y & 0xC0) << 5) | x


def main(style="inset"):
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    dis = decoder([0]*0x6000+list(source))
    observed = {}
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    # Перенос исходного фрагмента построителя с дисковых смещений на его рабочие адреса.
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for instruction in region["instructions"]:
                if 0x41B7 <= instruction["address"] < 0x41E3:
                    raw = bytes.fromhex(instruction["hex"])
                    if source[instruction["offset"]:instruction["offset"] + len(raw)] != raw:
                        raise ValueError("Байты построителя не соответствуют оригиналу")
                    start = instruction["address"]
                    memory[start:start + len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7, stop=0x41E3)
    if style == "band_filled":
        # Включение заполненного режима выполняется исходным настройщиком, а не ручной заменой CALL.
        memory[0x99B4] = 0
        memory[0xBFFE:0xC000] = [0xFF, 0x3F]
        simulator.registers[:] = get_registers({"SP": 0xBFFE}, None, False)
        simulator.run(start=0xCCAF, stop=0x3FFF)
    # Проверка всех элементов трёх игровых таблиц через независимую формулу адреса Spectrum.
    for y in range(256):
        address = bitmap_address(y)
        if memory[0x8200 + y] != address >> 8 or memory[0x8300 + y] != address & 255:
            raise ValueError("Неверная таблица строк")
        if memory[0x8400 + y] != y // 8:
            raise ValueError("Неверная таблица горизонтальных вкладов")
    cases = 0
    tested_rows = set()
    rows = (-24, -3, -1, 0, 1, 20, 23, 24)
    height_min = {"inset": 2, "band": 3, "fill": 1, "item": 1, "inner": 2, "band_filled": 3}[style]
    presets = (0,) if style == "inset" else (0, 1)
    widths = range(1 if style in ("fill", "item") else 2, 33)
    row_samples = range(24) if style == "fill" else rows
    for width, height, row, preset in product(widths, range(height_min, 25), row_samples, presets):
        if style == "fill" and row + height > 24:
            continue
        if style == "item" and (row >= 24 or row + height <= 0):
            continue
        columns = {0, (32 - width) // 2, 32 - width}
        if style != "fill":
            columns |= {1 - width, -1, 31}
        for column in sorted(columns):
            for carry in (0, 1):
                # Создание непустого фона позволяет обнаружить лишние записи, включая атрибуты.
                memory[0x4000:0x6000] = [0x96] * 0x2000
                expected = memory[0x4000:0x6000].copy()
                for local_y in range(height * 8):
                    y = row * 8 + local_y
                    if not 0 <= y < 192:
                        continue
                    if style in ("fill", "item"):
                        left = middle = right = 0 if preset else 255
                    elif style == "inset" or (style == "inner" and preset == 0):
                        if local_y in (0, height * 8 - 1):
                            left, middle, right = 255, 255, 255
                        elif local_y in (1, height * 8 - 2):
                            left, middle, right = 0x3F, 255, 0xFC
                        else:
                            left, middle, right = 0x40, 0, 2
                    elif style == "inner":
                        if local_y in (0, 1, height*8-2, height*8-1):
                            left = middle = right = 255
                        elif local_y in (2, height*8-3):
                            left, middle, right = 0x1F, 255, 0xF8
                        else:
                            left, middle, right = 0x20, 0, 4
                    elif style == "band_filled":
                        if local_y in (0, height*8-1):
                            left = middle = right = 0
                        elif local_y in (1, height*8-2):
                            left, middle, right = 0x7E, 255, 0x7E
                        elif local_y in (2, 11, height*8-3):
                            left, middle, right = 0x40, 0, 2
                        else:
                            left, middle, right = 0x5F, 255, 0xFA
                    else:
                        if local_y in (0, 12, height * 8 - 8, height * 8 - 1):
                            left, middle, right = 0, 0, 0
                        elif local_y in (1, height * 8 - 2):
                            left, middle, right = 0x7E, 255, 0x7E
                        elif preset and 3 <= local_y <= 10:
                            left, middle, right = 0x5F, 255, 0xFA
                        else:
                            left, middle, right = 0x40, 0, 2
                    pattern = [middle] * width if style in ("fill", "item") else [left] + [middle] * (width - 2) + [right]
                    # Отсечение независимой модели выполняется по геометрии, без кодов ветвления игры.
                    for offset, value in enumerate(pattern):
                        x = column + offset
                        if 0 <= x < 32:
                            expected[bitmap_address(y, x) - 0x4000] = value
                # Адрес стека является только фикстурой модели, он не меняет раскладку игры.
                stack = 0x7FFE if style == "item" else 0xBFFE
                memory[stack:stack + 2] = [0xFF, 0x3F]
                if style in ("fill", "item"):
                    memory[0x99B4] = 0xA4 | preset
                item_index = 45 if preset else 0
                if style == "item":
                    record = 0xF0FD + 16 * item_index
                    memory[record:record + 4] = [column & 255, row & 255, width, height]
                simulator.registers[:] = get_registers(
                    {"PC": {"inset": 0xC436, "band": 0xC093, "fill": 0xC626, "item": 0xBFF5, "inner": 0xC3A4, "band_filled": 0xC093}[style],
                     "SP": stack, "HL": item_index if style == "item" else 0x1357, "DE": height * 256 + width,
                     "BC": ((row & 255) << 8) | (column & 255), "AF": ((0x5A | preset) << 8) | 0xFE | carry,
                     "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x36AA,
                     "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
                before = simulator.registers.copy()
                # Ограничение числа инструкций отделяет корректное завершение от зависания модели.
                for _ in range(40000):
                    if simulator.registers[PC] == 0x3FFF:
                        break
                    pc = simulator.registers[PC]
                    if style == "inner" and (0xC201 <= pc < 0xC21F or 0xC3A4 <= pc < 0xC436):
                        # Сохранение только действительно исполненных неизменённых инструкций нового участка.
                        key = f"{pc:04X}"
                        if key not in observed:
                            instruction = dis.disassemble(pc, pc+1, "h")[0]
                            raw = bytes(memory[pc:pc+len(instruction.bytes)])
                            if raw != source[pc-0x6000:pc-0x6000+len(raw)]:
                                raise ValueError("Изменённая инструкция нового варианта рамки")
                            observed[key] = raw.hex()
                    simulator.run()
                else:
                    raise ValueError("Рамка не вернулась")
                if memory[0x4000:0x6000] != expected:
                    differences = [(f"{0x4000+i:04X}", actual, planned) for i, (actual, planned)
                                   in enumerate(zip(memory[0x4000:0x6000], expected)) if actual != planned]
                    raise ValueError(f"Не совпала рамка row={row}, col={column}, w={width}, h={height}: {differences[:12]}")
                if simulator.registers[SP] != stack + 2:
                    raise ValueError("Неверный CPU-стек")
                preserved = (*range(8, 12), *range(18, 23))
                if style in ("fill", "item"):
                    preserved = (*range(6, 12), *range(16, 24))
                    if style == "fill":
                        preserved = (*range(2, 4), *preserved)
                    end_row = min(24, row + height)
                    row_carry = int(end_row % 8 == 0)
                    expected_a = max(0, column) if row_carry else bitmap_address(end_row * 8) >> 8
                    output_width = min(32, column + width) - max(0, column)
                    if (simulator.registers[D], simulator.registers[E], simulator.registers[A], simulator.registers[F]) != (0, output_width, expected_a, 0x42 | row_carry):
                        raise ValueError("Не совпали выходные DE и AF заполнителя")
                    if style == "item" and (simulator.registers[2], simulator.registers[3]) != (max(0, row), max(0, column)):
                        raise ValueError("Не совпали отсечённые координаты элемента")
                for index in preserved:
                    if simulator.registers[index] != before[index]:
                        raise ValueError("Изменён сохраняемый индексный или альтернативный регистр")
                cases += 1
                tested_rows.add(row)
        if width % 8 == 0 and height == 24 and row == (0 if style == "fill" else 24):
            print(f"Проверена ширина {width}/32", flush=True)
    report = {"method": "original_z80_frame_and_original_table_builder_without_irq", "style": style,
              "cases": cases, "table_entries_checked": 768, "passed": True,
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "widths": [min(widths), 32], "heights": [height_min, 24], "rows": sorted(tested_rows), "band_presets": list(presets),
              "horizontal_clipping_checked": style != "fill", "vertical_clipping_checked": style != "fill",
              "input_domain": "bounded dimensions, sampled rows, sampled columns with horizontal intersection",
              "bitmap_and_attributes_compared": True, "native_execution_verified": False,
              "assembly_executed": False}
    if style == "item":
        report.update(item_indices=[0, 45], item_geometry_is_synthetic=True,
                      fully_invisible_rectangles_checked=False)
    if style == "inner":
        report["original_visited"] = dict(sorted(observed.items()))
    if style == "band_filled":
        report.update(code_patch_setup_executed="#CCAF", band_static_words_modified=True)
    report_name = {"inset": "InsetFrameVerification.json", "band": "BandFrameVerification.json", "fill": "FillRectangleVerification.json", "item": "ItemBitmapVerification.json", "inner": "InnerFrameVerification.json", "band_filled": "FilledBandFrameVerification.json"}[style]
    (ROOT / "Tools/Disasm/Reports" / report_name).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=("inset", "band", "fill", "item", "inner", "band_filled"), default="inset")
    main(parser.parse_args().style)
