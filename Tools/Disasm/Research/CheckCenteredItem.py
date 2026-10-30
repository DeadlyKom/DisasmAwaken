"""Проверка полного рисователя центрируемого элемента, рамки, карты и физического стека."""

from pathlib import Path
import hashlib
import json
import random
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, H, L, PC, SP
from CheckTextStream import reference as stream
from CheckJustifiedText import reference as justify
from CheckInsetFrame import bitmap_address


def line_width(text, widths):
    total = 0
    for char in text:
        if char in (0, 10, 13):
            return total
        total += widths[char]
        if total > 255 or (total & 255) == 0:
            return 255
    raise ValueError("Не найден ограничитель измеряемой строки")


def reference(text, widths, width, height, origin):
    pointer, x, y, positions = 0, 0, 0, []
    for _ in range(300):
        stop = pointer
        while text[stop] not in (10, 13):
            stop += 1
        if text[stop] == 10:
            result = justify(0xADCD, text[pointer:], widths, 0, y, width, height,
                             positions=positions, origin=origin)
            consumed, x, y, a, flags, _, _, _, _ = result
            return pointer+consumed, x, y, flags, positions
        measured = line_width(text[pointer:], widths)
        x = max(0, width-measured)//2
        result = stream(text[pointer:], widths, x, y, width, height, 1, (0, 0, 0, 0, 0),
                        origin, 0, stop_on_cr=True, positions=positions)
        consumed, x, y, a, flags, _ = result
        pointer += consumed
        if flags & 1:
            return pointer, x, y, flags, positions
    raise ValueError("Центрирование не достигло общего выхода")


def main(caption=False, filled=False):
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    # Создание таблиц адресации тем же перенесённым построителем, что использует игра.
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for instruction in region["instructions"]:
                if 0x41B7 <= instruction["address"] < 0x41E3:
                    raw = bytes.fromhex(instruction["hex"])
                    if source[instruction["offset"]:instruction["offset"]+len(raw)] != raw:
                        raise ValueError("Не совпали байты построителя")
                    memory[instruction["address"]:instruction["address"]+len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7, stop=0x41E3)
    widths = source[0x2900:0x2A00]
    initial = get_registers({"SP": 0x7FFE, "HL": 0, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    if filled:
        # Включение режима выполняется исходным настройщиком, шесть слов вручную не подменяются.
        memory[0x99B4] = 0
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.run(start=0xCCAF, stop=0x3FFF)
    cases = 0
    texts = (b"A\rB\n", b"ONE TWO\rTHREE FOUR\n", b"A\rB\rC\rD\n", b"LAST WORDS WITHOUT CR\n")
    resource_base = 0xE399 if caption else 0xE4AA

    def execute(key, row, column, width, height, flags, text, text_index=0):
        nonlocal cases
        records = [b"OTHER\n", text, b"TAIL\n"] if text_index else [text, b"OTHER\n"]
        resource = [10]
        starts = []
        for record in records:
            starts.append(len(resource))
            resource.extend(record)
        resource += [10]*1024
        memory[resource_base:resource_base+len(resource)] = resource
        logical = resource[starts[text_index]:]
        win_width, win_height = 8*width-4, (8*height-11) & 255
        origin = (8*column+3, 8*row+(3 if caption else 4))
        if caption:
            positions = []
            consumed, _, _, _, _, _ = stream(logical, widths, 1, 0, win_width, win_height, 0,
                                             (0, 0, 0, 0, 0), origin, 0, positions=positions)
            x, y = 0, 8 if flags & 1 else 0
            last_flags = 8 if flags & 1 else (0x80 if (row+height-1) % 8 >= 4 else 0) | ((flags >> 1) & 0x28)
            expected_a = y
        else:
            consumed, x, y, last_flags, positions = reference(logical, widths, win_width, win_height, origin)
            expected_a = 0xC3
        # Независимое построение исходного контура на непустом фоне, затем XOR ожидаемых глифов.
        expected = [0x96]*0x2000
        for local_y in range(8*height):
            if caption and filled:
                if local_y in (0, 8*height-1):
                    left = middle = right = 0
                elif local_y in (1, 8*height-2):
                    left, middle, right = 0x7E, 255, 0x7E
                elif local_y in (2, 11, 8*height-3):
                    left, middle, right = 0x40, 0, 2
                else:
                    left, middle, right = 0x5F, 255, 0xFA
            elif caption:
                if local_y in (0, 12, 8*height-8, 8*height-1):
                    left = middle = right = 0
                elif local_y in (1, 8*height-2):
                    left, middle, right = 0x7E, 255, 0x7E
                elif flags & 1 and 3 <= local_y <= 10:
                    left, middle, right = 0x5F, 255, 0xFA
                else:
                    left, middle, right = 0x40, 0, 2
            elif flags & 1:
                if local_y in (0, 1, 8*height-2, 8*height-1):
                    left = middle = right = 255
                elif local_y in (2, 8*height-3):
                    left, middle, right = 0x1F, 255, 0xF8
                else:
                    left, middle, right = 0x20, 0, 4
            elif local_y in (0, 8*height-1):
                left = middle = right = 255
            elif local_y in (1, 8*height-2):
                left, middle, right = 0x3F, 255, 0xFC
            else:
                left, middle, right = 0x40, 0, 2
            address = bitmap_address(row*8+local_y, column)-0x4000
            expected[address:address+width] = [left]+[middle]*(width-2)+[right]
        for code, gx, gy in positions:
            if gy >= win_height or gx+widths[code] > 255 or gx+widths[code] >= win_width:
                continue
            px, py = origin[0]+gx, origin[1]+gy
            if px >= 256 or py >= 185:
                continue
            for glyph_y in range(8):
                value = source[0x2A00+8*code+glyph_y]
                address = bitmap_address(py+glyph_y, px//8)-0x4000
                shift = px & 7
                expected[address] ^= value >> shift
                if shift and px//8 != 31:
                    expected[address+1] ^= (value << (8-shift)) & 255
        record = 0xF0FD+16*key
        memory[record:record+6] = [column, row, width, height, flags, text_index]
        memory[0x8500:0x8600] = [0x80, 0xFF]*128
        memory[0x8600:0x8900] = [0x33]*768
        memory[0x4000:0x6000] = [0x96]*0x2000
        memory[0xBD4F] = 0xC3
        memory[0xAED5:0xAED8] = source[0x4ED5:0x4ED8]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[H], simulator.registers[L] = key >> 8, key & 255
        simulator.registers[PC] = 0xC287 if caption else 0xC2DF
        actual_positions = []
        wakeups = 0
        for _ in range(150000):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if caption and pc == 0xC089:
                # Только фикстура пробуждения HALT, IRQ и его обработчик здесь не исполняются.
                if memory[pc] != 0x76:
                    raise ValueError("Изменён исходный HALT обёртки")
                simulator.registers[PC] += 1
                wakeups += 1
                continue
            if pc == 0xAE8D:
                actual_positions.append((simulator.registers[A], memory[0x6320], memory[0x6321]))
            simulator.run()
        else:
            raise ValueError("Центрируемый элемент не завершился")
        if actual_positions != positions or memory[0x4000:0x6000] != expected:
            raise ValueError(f"Не совпал bitmap либо поток глифов key={key}, geometry={column}/{row}/{width}/{height}, flags={flags:02X}, text={text}")
        expected_map = [0x33]*768
        for iy in range(row, row+height):
            expected_map[32*iy+column:32*iy+column+width] = [1]*width
        if memory[0x8600:0x8900] != expected_map or memory[0x8500:0x8502] != list(key.to_bytes(2, "little")):
            raise ValueError("Не совпала регистрация центрируемого элемента")
        if memory[0x8502:0x8600] != [0x80, 0xFF]*127:
            raise ValueError("Повреждён остаток индексной таблицы")
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP], memory[0xBD4F],
                *memory[0x6320:0x6322], memory[0xBD26]) != (expected_a, last_flags, 0x8000, 0xC3, x, y, 0 if caption else 1):
            raise ValueError("Не совпал статус, курсор либо восстановление кода центрирования")
        for reg in (*range(2, 12), *range(18, 23)):
            expected_reg = key >> 8 if reg == H else key & 255 if reg == L else initial[reg]
            if simulator.registers[reg] != expected_reg:
                raise ValueError("Рисователь не восстановил сохранённый регистр")
        if memory[0xAED5:0xAED8] != list(source[0x4ED5:0x4ED8]):
            raise ValueError("Глиф остался в режиме без пикселей")
        if caption:
            if wakeups != 1 or simulator.registers[23] != initial[23]:
                raise ValueError("Не совпало пробуждение либо сохранение альтернативного HL")
        cases += 1

    for width, height, flags, text, key, text_index in product(
            (2, 3, 8, 16, 32), ((3, 4, 8, 16, 24) if caption else (2, 3, 4, 8, 24)), (0, 1, 0xE0, 0xFF), texts, (0, 45), (0, 1)):
        for row, column in {(0, 0), (24-height, 32-width), ((24-height)//2, (32-width)//2)}:
            execute(key, row, column, width, height, flags, text, text_index)
    generator = random.Random(0xC2DF)
    for _ in range(500):
        width, height = generator.randrange(2, 33), generator.randrange(3 if caption else 2, 25)
        text = bytes(generator.choice([32, 32, 13, 65, 66, 67, 128, 255]) for _ in range(generator.randrange(1, 90)))+b"\n"
        execute(generator.choice((0, 45)), generator.randrange(25-height), generator.randrange(33-width),
                width, height, generator.randrange(256), text, generator.randrange(2))
    report = dict(method="original_centered_item_with_full_bitmap_map_and_stack_comparison", passed=True,
                  cases=cases, source_sha256=hashlib.sha256(source).hexdigest(), glyph_pixels_executed=True,
                  bitmap_and_attributes_compared=True, geometry_and_text_are_synthetic=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    if caption:
        report.update(method="original_caption_item_after_modeled_halt_wakeup", halt_wakeup_is_fixture=True,
                      interrupt_handler_executed=False, interrupt_timing_verified=False)
    if filled:
        report.update(band_filled_mode=True, band_mode_setup_executed="#CCAF")
    filename = "FilledCaptionItemVerification.json" if filled else "CaptionItemVerification.json" if caption else "CenteredItemVerification.json"
    (ROOT / "Tools/Disasm/Reports" / filename).write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caption", action="store_true")
    parser.add_argument("--filled", action="store_true")
    args = parser.parse_args()
    if args.filled and not args.caption:
        parser.error("--filled используется только вместе с --caption")
    main(args.caption, args.filled)
