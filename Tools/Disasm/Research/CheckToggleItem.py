"""Проверка смены контура с настоящими рисователями рамки и указателя, HALT пробуждается фикстурой."""

from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, PC, SP
from CheckInsetFrame import bitmap_address
from CheckCenteredItem import reference


def main(close=False):
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for i in region["instructions"]:
                if 0x41B7 <= i["address"] < 0x41E3:
                    raw = bytes.fromhex(i["hex"])
                    if source[i["offset"]:i["offset"]+len(raw)] != raw:
                        raise ValueError("Изменились исходные байты построителя таблиц")
                    memory[i["address"]:i["address"]+len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7, stop=0x41E3)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    memory[0xE4AA:0xE8AB] = [10]*1025
    memory[0x9CA6:0x9CA8] = [0, 0xE0]
    memory[0xE000:0xE004] = [0, 0x70, 1, 1]
    cases = redraws = skipped = wakeups = 0
    geometries = ((0, 0, 2, 2), (3, 4, 8, 4), (0, 0, 32, 24), (20, 22, 12, 2))
    for flags, key, active, (column, row, width, height) in product(range(256), (0, 45), (False, True), geometries):
        record = 0xF0FD+16*key
        memory[record:record+16] = [column, row, width, height, flags, 0, 0, 0x68,
                                   column, row, width, height, 0, 0x70, 0xAB, 0xCD]
        old_record = memory[record:record+16].copy()
        memory[0x4000:0x6000] = [0x96]*8192
        memory[0x8500:0x8600] = [0x80, 0xFF]*128
        memory[0x8600:0x8900] = [0]*768
        memory[0x6307:0x6309] = [255, 191]
        memory[0x6548] = 1
        memory[0x6575:0x6585] = [0xA5]*16
        memory[0x9B16] = 0x5A
        if close:
            # Создание непустого списка, закрываемый обработчик находится между двумя другими.
            memory[0x7001:0x7003] = list(key.to_bytes(2, "little"))
            memory[0x7101:0x7103] = list((key+100).to_bytes(2, "little"))
            memory[0x7201:0x7203] = list((key+200).to_bytes(2, "little"))
            memory[0xE000:0xE088] = [0x55]*136
            memory[0xE000:0xE008] = [0, 0x71, 0, 0x70, 0, 0x72, 1, 1]
            memory[0x9E78] = 1
            memory[0x9E7E:0x9E80] = list(key.to_bytes(2, "little"))
            memory[0x9E8B:0x9E8D] = [0x58, 0x9A]
        else:
            memory[0xE000:0xE004] = [0, 0x70, 1, 1]
        memory[0xBD4F] = 0xC3
        memory[0xAED5:0xAED8] = source[0x4ED5:0x4ED8]
        if active:
            memory[0x7FFE:0x8000] = [0xFF, 0x3F]
            simulator.registers[:] = initial
            simulator.run(start=0x6413, stop=0x3FFF)
        before_bitmap = memory[0x4000:0x6000].copy()
        before_saved = memory[0x6575:0x6585].copy()
        before_gate = memory[0x6548]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
        simulator.registers[PC] = 0x9E77 if close else 0x9EA5
        local_wakeups = 0
        for _ in range(100000):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if pc == 0x9EB9:
                # Пробуждение без исполнения IRQ, исходный HALT подтверждается, но временная точность не проверяется.
                if memory[pc] != 0x76:
                    raise ValueError("Изменился исходный HALT переключателя")
                simulator.registers[PC] += 1
                local_wakeups += 1
            else:
                simulator.run()
        else:
            raise ValueError("Переключатель не вернулся")
        # Проверка сохранения основного контекста, DE возвращает входной индекс, а не рабочий адрес Flags.
        for reg in (*range(2, 12), *range(18, 23)):
            expected = key >> 8 if reg == D else key & 255 if reg == E else initial[reg]
            if simulator.registers[reg] != expected:
                raise ValueError("Переключатель изменил сохраняемый регистр")
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Не восстановлен динамический кадр переключателя")
        if flags & 16:
            expected_af = (0, 0x45) if close else (flags, (flags & 0x28) | 0x10)
            if (simulator.registers[A], simulator.registers[F]) != expected_af:
                raise ValueError("Не совпал AF запрещённого переключения")
            if (memory[0x4000:0x6000] != before_bitmap or memory[0x6575:0x6585] != before_saved
                    or memory[record:record+16] != old_record or memory[0x9B16] != 0x5A
                    or memory[0x6548] != before_gate or local_wakeups):
                raise ValueError("Запрещённое переключение изменило состояние")
            if simulator.registers[16:24] != initial[16:24]:
                raise ValueError("Запрещённое переключение изменило альтернативные регистры")
            skipped += 1
        else:
            expected_flags = flags ^ 1
            _, _, _, last_flags, positions = reference([10]*1025, source[0x2900:0x2A00],
                                                      width*8-4, (height*8-11) & 255,
                                                      (column*8+3, row*8+4))
            expected_af = (0, 0x45) if close else (0xC3, last_flags)
            if positions or (simulator.registers[A], simulator.registers[F]) != expected_af:
                raise ValueError("Не совпал выход пустого центрируемого текста")
            expected = [0x96]*8192
            for local_y in range(height*8):
                if expected_flags & 1:
                    if local_y in (0, 1, height*8-2, height*8-1):
                        left = middle = right = 255
                    elif local_y in (2, height*8-3):
                        left, middle, right = 0x1F, 255, 0xF8
                    else:
                        left, middle, right = 0x20, 0, 4
                elif local_y in (0, height*8-1):
                    left = middle = right = 255
                elif local_y in (1, height*8-2):
                    left, middle, right = 0x3F, 255, 0xFC
                else:
                    left, middle, right = 0x40, 0, 2
                address = bitmap_address(row*8+local_y, column)-0x4000
                expected[address:address+width] = [left]+[middle]*(width-2)+[right]
            expected_map = [0]*768
            for iy in range(row, row+height):
                expected_map[32*iy+column:32*iy+column+width] = [1]*width
            # Выбор формы в новой карте, последний пиксель экрана принадлежит только двум нижним прямоугольникам.
            page = 0
            if expected_map[-1] and expected_flags & 0xC0 == 0:
                if row == 23 and expected_flags & 4 == 0:
                    page = 1
                elif row+height-1 == 23 and expected_flags & 2 == 0:
                    page = 2
            offset = 256*page+32*7
            expected_saved = [expected[0x17FF], expected[0x1800]]
            expected[0x17FF] = (expected[0x17FF] & source[offset]) ^ source[offset+1]
            if memory[0x4000:0x6000] != expected or memory[0x6575:0x6577] != expected_saved:
                raise ValueError("Не совпала новая рамка с указателем либо захват его нового фона")
            if memory[0x8600:0x8900] != expected_map or memory[0x8500:0x8502] != list(key.to_bytes(2, "little")):
                raise ValueError("Не совпала регистрация перерисованного элемента")
            old_record[4] = expected_flags
            if (memory[record:record+16] != old_record or memory[0x9B16] != 0
                    or memory[0x6548] != 0 or local_wakeups != 1):
                raise ValueError("Не совпали флаги, разрешение указателя либо пробуждение")
            redraws += 1
        if close and (memory[0x9E78] != 0 or memory[0x9E8B:0x9E8D] != [0x58, 0x9A]
                      or memory[0xE000:0xE008] != [0, 0x71, 0, 0x72, 0, 0x70, 1, 1]):
            raise ValueError("Закрытие не сбросило активность либо не переместило обработчик в конец")
        wakeups += local_wakeups
        cases += 1
    report = dict(method="original_item_toggle_full_frame_and_pointer_after_modeled_halt", passed=True,
                  cases=cases, redrawn=redraws, skipped=skipped, modeled_wakeups=wakeups,
                  source_sha256=hashlib.sha256(source).hexdigest(), bitmap_and_attributes_compared=True,
                  text_fixture="empty_LF_terminated", native_execution_verified=False,
                  interrupt_handler_executed=False, interrupt_timing_verified=False, assembly_executed=False)
    if close:
        report.update(method="original_active_item_close_full_frame_pointer_and_empty_callback", close_callback="EmptyCallback")
    filename = "CloseItemVerification.json" if close else "ToggleItemVerification.json"
    (ROOT / "Tools/Disasm/Reports" / filename).write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--close", action="store_true")
    main(parser.parse_args().close)
