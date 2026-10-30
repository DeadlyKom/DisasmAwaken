"""Проверка исходного указателя, масок, сохранения фона и временного запрета обновления."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP, IXh, IXl, xA, xF
from CheckGlyphRenderer import and_flags, compare_flags
from CheckStationSpans import add_flags, subtract_flags
from CheckInsetFrame import bitmap_address


def advance(address):
    high, low = address >> 8, address & 255
    high = (high+1) & 255
    value = high & 7
    flags = and_flags(value)
    if value == 0:
        summed = low+32
        value, flags = summed & 255, add_flags(low, 32)
        low = value
        if summed < 256:
            value, flags = (high-8) & 255, subtract_flags(high, 8)
            high = value
    return high*256+low, value, flags


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for instruction in region["instructions"]:
                if 0x41B7 <= instruction["address"] < 0x41E3:
                    raw = bytes.fromhex(instruction["hex"])
                    if source[instruction["offset"]:instruction["offset"]+len(raw)] != raw:
                        raise ValueError("Изменились байты построителя адресных таблиц")
                    memory[instruction["address"]:instruction["address"]+len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7, stop=0x41E3)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    baseline = [(i*73+(i >> 8)*19+17) & 255 for i in range(0x2000)]
    memory[0x8600:0x8900] = [0]*768
    counts = {}
    mask_rows = 0
    # Проверка всех предвычисленных сдвигов по независимому 16-битному преобразованию маски и XOR.
    for page, shift, row in product(range(3), range(8), range(8)):
        base = page*256+4*row
        mask = source[base]*256+source[base+2]
        xor = source[base+1]*256+source[base+3]
        expected_mask = (mask >> shift) | (((1 << shift)-1) << (16-shift))
        expected_xor = xor >> shift
        expected = bytes([expected_mask >> 8, expected_xor >> 8, expected_mask & 255, expected_xor & 255])
        offset = page*256+32*shift+4*row
        if source[offset:offset+4] != expected:
            raise ValueError("Не совпали исходные сдвиги маски указателя")
        mask_rows += 1

    def run(start):
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.run(start=start, stop=0x3FFF)
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Указатель не восстановил CPU-стек")
        counts[f"{start:04X}"] = counts.get(f"{start:04X}", 0)+1

    def preserved(except_regs):
        for reg in (*range(12), *range(16, 24)):
            if reg not in except_regs and simulator.registers[reg] != initial[reg]:
                raise ValueError("Изменён сохраняемый регистр указателя")

    def expected_draw(x, y, page):
        rows = min(8, 192-y)
        expected = baseline.copy()
        saved = [0xA5]*16
        address = bitmap_address(y, x//8)
        first = address
        last_a, last_f = 0, 0
        for row in range(rows):
            offset = page*256+32*(x & 7)+4*row
            mask_left, xor_left, mask_right, xor_right = source[offset:offset+4]
            saved[2*row:2*row+2] = baseline[address-0x4000:address-0x4000+2]
            expected[address-0x4000] = (expected[address-0x4000] & mask_left) ^ xor_left
            if x < 248:
                expected[address-0x4000+1] = (expected[address-0x4000+1] & mask_right) ^ xor_right
            address, last_a, last_f = advance(address)
        return expected, saved, rows, first, address, last_a, last_f

    def cycle(x, y, page=0, key=None, flags=0, item_y=0, height=8, last_matches=False, kind="normal"):
        memory[0x4000:0x6000] = baseline
        memory[0x6575:0x6585] = [0xA5]*16
        memory[0x6320:0x6322] = [0x99, 0x88]
        memory[0x6307:0x6309] = [x, y]
        memory[0x6548] = 1
        memory[0x9A8D:0x9A8F] = [0x11, 0x11]
        memory[0x9A90:0x9A92] = [0x58, 0x9A]
        cell = 0x8600+32*(y//8)+x//8
        owner = 0 if key is None else 128
        memory[cell] = owner
        if key is not None:
            memory[0x85FE:0x8600] = [key & 255, key >> 8]
            base = 0xF0FD+16*key
            memory[base:base+16] = [0, item_y, 32, height, flags, 0, 0x00, 0x68, 0, 0, 0, 0, 0x00, 0x70, 0, 0]
            memory[0x9CA6:0x9CA8] = [0, 0xE0]
            memory[0xE000:0xE004] = [0, 0x70 if last_matches else 0x71, 0xA5, 1]
        expected, saved, rows, first, after, last_a, last_f = expected_draw(x, y, page)
        run(0x6413)
        expected_hl = 0x6000+256*page+((32*(x & 7)+4*rows) & 255)
        actual = (simulator.registers[H]*256+simulator.registers[L], simulator.registers[D]*256+simulator.registers[E],
                  simulator.registers[B], simulator.registers[C], simulator.registers[A], simulator.registers[F])
        if actual != (expected_hl, after, 0, 191-2*rows, last_a, last_f):
            raise ValueError(f"Не совпал выход рисования x={x}, y={y}, page={page}: {actual}")
        if memory[0x4000:0x6000] != expected or memory[0x6575:0x6585] != saved:
            raise ValueError("Не совпал указатель либо сохранённый фон")
        if (memory[0x6548], memory[0x6501], memory[0x6550]+256*memory[0x6551],
                memory[0x64B3]+256*memory[0x64B4]) != (0, rows, first, 0x6000+256*page):
            raise ValueError("Не совпали изменяемые операнды состояния указателя")
        hover = key is not None and flags & 0xC0 == 0 and last_matches
        expected_hover = 0xF0FD+16*key if hover else 0x1111
        if (memory[0x9A8D]+256*memory[0x9A8E], memory[0x9A90]+256*memory[0x9A91]) != (
                expected_hover, 0x6800 if hover else 0x9A58):
            raise ValueError("Не совпала установка обработчика наведения")
        expected_ix = initial[IXh]*256+initial[IXl] if key is None else 0xF0FD+16*key
        if simulator.registers[IXh]*256+simulator.registers[IXl] != expected_ix:
            raise ValueError("Не совпал временный IX записи наведения")
        if key is None or flags & 0xC0:
            expected_alt = initial[xA], initial[xF]
        elif y//8 == item_y or flags & 2:
            expected_alt = y//8, compare_flags(y//8, item_y)
        else:
            expected_alt = 0, and_flags(0)
        if (simulator.registers[xA], simulator.registers[xF]) != expected_alt:
            raise ValueError("Не совпал альтернативный AF выбора формы")
        preserved({A, F, B, C, D, E, H, L, IXh, IXl, xA, xF})
        # Повторный Draw при нулевом флаге не накладывает курсор и не сохраняет его собственные пиксели как фон.
        run(0x6413)
        if (simulator.registers[A], simulator.registers[F]) != (0, 0x44) or memory[0x4000:0x6000] != expected or memory[0x6575:0x6585] != saved:
            raise ValueError("Повторный рисователь испортил активный курсор")
        run(0x6547)
        if memory[0x4000:0x6000] != baseline or memory[0x6548] != 1:
            raise ValueError("Фон указателя не восстановлен, включая атрибуты")
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[D]*256+simulator.registers[E],
                simulator.registers[B], simulator.registers[C], simulator.registers[A], simulator.registers[F]) != (
                0x6575+2*rows, after, 0, 255-2*rows, last_a, last_f):
            raise ValueError("Не совпал договор восстановления фона")
        preserved({A, F, B, C, D, E, H, L})
        memory[cell] = 0
        return expected, rows

    for y in range(192):
        for x in range(256):
            cycle(x, y)
    normal_cases = 256*192
    hover_cases = 0
    coordinates = ((0, 0), (7, 7), (247, 63), (248, 64), (128, 184), (255, 191))
    for flags, role, key, matches, (x, y) in product(range(256), (0, 1, 2), (0, 45), (False, True), coordinates):
        item_y = y//8 if role == 0 else ((y//8-3) & 255) if role == 1 else (y//8+2)
        height = 4 if role == 1 else 8
        page = 0
        if flags & 0xC0 == 0:
            if role == 0 and flags & 4 == 0:
                page = 1
            elif role == 1 and flags & 2 == 0:
                page = 2
        cycle(x, y, page, key, flags, item_y, height, matches, "hover")
        hover_cases += 1
    # Проверка всех ненулевых значений флага уже восстановленного фона.
    for value in range(1, 256):
        memory[0x6548] = value
        memory[0x4000:0x6000] = baseline
        run(0x6547)
        if (simulator.registers[A], simulator.registers[F]) != (value, and_flags(value)) or memory[0x4000:0x6000] != baseline:
            raise ValueError("Ранний выход восстановления изменил экран")
        preserved({A, F})
    # Проверка защитных обёрток на разных строках экрана, с настоящим фоном и рисованием.
    guard_cases = 0
    for x, y in product((0, 7, 248, 255), (0, 7, 63, 184, 185, 191)):
        expected, rows = cycle(x, y)
        memory[0x6548] = 1
        run(0x63D8)
        if memory[0x4000:0x6000] != expected or memory[0x9B16] != 0:
            raise ValueError("Возобновление указателя не восстановило рисунок")
        preserved(set())
        run(0x63C3)
        if memory[0x4000:0x6000] != baseline or memory[0x9B16] != 1:
            raise ValueError("Приостановка указателя не восстановила фон")
        preserved(set())
        guard_cases += 1
    # Проверка нулевого набора параметров UpdatePointer без изменения исходных регистров и экрана.
    for address in (0x6586, 0x6588, 0x66E8, 0x66EA):
        memory[address:address+2] = [0, 0]
    memory[0x4000:0x6000] = baseline
    run(0x640C)
    if (simulator.registers[A], simulator.registers[F]) != (0, 0x44) or memory[0x4000:0x6000] != baseline:
        raise ValueError("Пустое обновление движения изменило указатель")
    preserved({A, F})
    # Проверка полного обновления после перемещения, каждый из восьми байтов движения проверяется независимо.
    motion_bytes = (0x6586, 0x6587, 0x6588, 0x6589, 0x66E8, 0x66E9, 0x66EA, 0x66EB)
    update_cases = 0
    for motion_address, bit, (x, y) in product(motion_bytes, range(8), ((0, 0), (7, 63), (248, 185), (255, 191))):
        old_x, old_y = (x+37) & 255, (y+23) % 192
        cycle(old_x, old_y)
        run(0x6413)
        for address in motion_bytes:
            memory[address] = 0
        memory[motion_address] = 1 << bit
        memory[0x6307:0x6309] = [x, y]
        expected, saved, rows, first, after, last_a, last_f = expected_draw(x, y, 0)
        # Незаписанный хвост буфера принадлежит предыдущему сохранению, не обязан быть #A5.
        previous_tail = memory[0x6575+2*rows:0x6585]
        run(0x640C)
        if memory[0x4000:0x6000] != expected or memory[0x6575:0x6575+2*rows] != saved[:2*rows]:
            raise ValueError("Обновление не восстановило старый фон перед рисованием в новой позиции")
        if memory[0x6575+2*rows:0x6585] != previous_tail or memory[0x6548] != 0:
            raise ValueError("Обновление изменило хвост фона либо флаг состояния")
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[D]*256+simulator.registers[E],
                simulator.registers[B], simulator.registers[C], simulator.registers[A], simulator.registers[F]) != (
                0x6000+((32*(x & 7)+4*rows) & 255), after, 0, 191-2*rows, last_a, last_f):
            raise ValueError("Не совпал выход полного обновления указателя")
        preserved({A, F, B, C, D, E, H, L})
        run(0x6547)
        if memory[0x4000:0x6000] != baseline:
            raise ValueError("Фон после перемещения не восстановлен")
        update_cases += 1
    # Проверка опасного пути невалидной индексной пары до POP IX, не выдавая его за успешный запуск.
    memory[0x6307:0x6309] = [0, 0]
    memory[0x8600] = 1
    memory[0x8500:0x8502] = [0, 0xFF]
    memory[0x7FFE:0x8000] = [0xFF, 0x3F]
    simulator.registers[:] = initial
    simulator.run(start=0x6413, stop=0x646B)
    invalid_pop = (simulator.registers[SP], simulator.registers[IXh]*256+simulator.registers[IXl]) == (0x8000, 0x3FFF)
    if not invalid_pop:
        raise ValueError("Не подтверждён несимметричный стек невалидной индексной пары")
    report = dict(method="original_pointer_masks_pixels_background_and_guard_comparison", passed=True,
                  normal_coordinate_cases=normal_cases, hover_cases=hover_cases, mask_rows=mask_rows,
                  guard_cases=guard_cases, full_update_cases=update_cases, early_restore_flag_cases=255, by_entry=counts,
                  source_sha256=hashlib.sha256(source).hexdigest(), attributes_unchanged=True,
                  invalid_owner_consumes_return_address=invalid_pop, saved_row_count_is_draw_immediate=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/PointerVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
