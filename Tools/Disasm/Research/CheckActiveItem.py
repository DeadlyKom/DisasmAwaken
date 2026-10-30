"""Проверка активации элемента с исходным закрытием прежнего, двумя рамками и указателем."""

from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1")]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP
from CheckInsetFrame import bitmap_address
from CheckCenteredItem import reference


def frame(bitmap, geometry, flags):
    column, row, width, height = geometry
    for y in range(height*8):
        if flags & 1:
            if y in (0, 1, height*8-2, height*8-1):
                left = middle = right = 255
            elif y in (2, height*8-3):
                left, middle, right = 0x1F, 255, 0xF8
            else:
                left, middle, right = 0x20, 0, 4
        elif y in (0, height*8-1):
            left = middle = right = 255
        elif y in (1, height*8-2):
            left, middle, right = 0x3F, 255, 0xFC
        else:
            left, middle, right = 0x40, 0, 2
        start = bitmap_address(8*row+y, column)-0x4000
        bitmap[start:start+width] = [left]+[middle]*(width-2)+[right]


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
            for i in region["instructions"]:
                if 0x41B7 <= i["address"] < 0x41E3:
                    raw = bytes.fromhex(i["hex"])
                    if source[i["offset"]:i["offset"]+len(raw)] != raw:
                        raise ValueError("Изменились исходные байты построителя")
                    memory[i["address"]:i["address"]+len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7, stop=0x41E3)
    dis = decoder(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    memory[0xE4AA:0xE8AB] = [10]*1025
    memory[0x9CA6:0x9CA8] = [0, 0xE0]
    geometries = {0: (0, 0, 4, 3), 45: (10, 10, 4, 4)}
    observed = {}
    cases = transitions = already_selected = modeled_wakeups = 0
    for flags, key, previous, pointer_active in product(range(256), (0, 45), ("none", "same", "other"), (False, True)):
        other = 45-key
        old_key = key if previous == "same" else other
        original_flags = {key: flags, other: 1}
        final_flags = original_flags.copy()
        for item_key in (0, 45):
            address = 0xF0FD+16*item_key
            geometry = geometries[item_key]
            handler = 0x7000 if item_key == key else 0x7100
            memory[address:address+16] = [*geometry, original_flags[item_key], 0, 0, 0x68,
                                         *geometry, handler & 255, handler >> 8, 0xAB, 0xCD]
        memory[0x7001:0x7003] = list(key.to_bytes(2, "little"))
        memory[0x7101:0x7103] = list(other.to_bytes(2, "little"))
        memory[0xE000:0xE088] = [0x55]*136
        memory[0xE000:0xE006] = [0, 0x70, 0, 0x71, 1, 1]
        memory[0x4000:0x6000] = [0x96]*8192
        memory[0x8500:0x8600] = [0x80, 0xFF]*128
        memory[0x8600:0x8900] = [0]*768
        memory[0x6307:0x6309] = [255, 191]
        memory[0x6548] = 1
        memory[0x6575:0x6585] = [0xA5]*16
        memory[0x9B16] = 0x5A
        memory[0xBD4F] = 0xC3
        memory[0xAED5:0xAED8] = source[0x4ED5:0x4ED8]
        if pointer_active:
            memory[0x7FFE:0x8000] = [0xFF, 0x3F]
            simulator.registers[:] = initial
            simulator.run(start=0x6413, stop=0x3FFF)
        before_bitmap = memory[0x4000:0x6000].copy()
        active_value = 0 if previous == "none" else 0x37
        memory[0x9E78] = active_value
        memory[0x9E7E:0x9E80] = list(old_key.to_bytes(2, "little"))
        memory[0x9E8B:0x9E8D] = [0x34, 0x12]
        memory[0xCCA4:0xCCA6] = [0x77, 0x77]
        action = (flags*149+(45 if key else 17)) & 255
        memory[0x9839] = action
        redraw_order = []
        expected_list = [0x7100, 0x7000]
        expected_wakeups = 0
        # Независимая модель решает по исходному биту контура, не по байту активности.
        if flags & 1:
            before_rotate = 0x10
            expected_active, expected_index = active_value, old_key
            already_selected += 1
        else:
            if previous != "none":
                old_handler = 0x7000 if old_key == key else 0x7100
                expected_list.remove(old_handler)
                expected_list.append(old_handler)
                if final_flags[old_key] & 16 == 0:
                    final_flags[old_key] ^= 1
                    redraw_order.append(old_key)
            expected_active, expected_index = 255, key
            expected_wakeups += 1
            if final_flags[key] & 16:
                before_rotate = (final_flags[key] & 0x28) | 0x10
            else:
                final_flags[key] ^= 1
                redraw_order.append(key)
                column, row, width, height = geometries[key]
                _, _, _, before_rotate, _ = reference([10]*1025, source[0x2900:0x2A00],
                                                       8*width-4, 8*height-11, (8*column+3, 8*row+4))
            expected_wakeups += len(redraw_order)
            transitions += 1
        expected_bitmap = [0x96]*8192 if redraw_order else before_bitmap
        expected_map = [0]*768
        mapping = {}
        for item_key in redraw_order:
            frame(expected_bitmap, geometries[item_key], final_flags[item_key])
            # При повторной регистрации того же ключа используется уже освобождённая первая пара.
            if item_key not in mapping:
                mapping[item_key] = len(mapping)+1
            column, row, width, height = geometries[item_key]
            for y in range(row, row+height):
                expected_map[y*32+column:y*32+column+width] = [mapping[item_key]]*width
        if redraw_order:
            offset = 7*32
            expected_bitmap[0x17FF] = (expected_bitmap[0x17FF] & source[offset]) ^ source[offset+1]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
        simulator.registers[PC] = 0xCC81
        local_wakeups = 0
        for _ in range(150000):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if 0xCC81 <= pc < 0xCCAA and f"{pc:04X}" not in observed:
                instruction = dis.disassemble(pc, pc+1, "h")[0]
                raw = bytes(memory[pc:pc+len(instruction.bytes)])
                original = source[pc-0x6000:pc-0x6000+len(raw)]
                if raw == original:
                    observed[f"{pc:04X}"] = raw.hex()
                elif pc != 0xCCA3:
                    raise ValueError("Непредусмотренная подмена кода активации")
            if pc in (0xCC9B, 0x9EB9):
                if memory[pc] != 0x76:
                    raise ValueError("Изменился HALT активации")
                simulator.registers[PC] += 1
                local_wakeups += 1
            else:
                simulator.run()
        else:
            raise ValueError("Активация не завершилась")
        result_a = ((action << 1) | (before_rotate & 1)) & 255
        result_f = (before_rotate & 0xC4) | (result_a & 0x28) | (action >> 7)
        if (simulator.registers[A], simulator.registers[F], simulator.registers[H]*256+simulator.registers[L],
                simulator.registers[D]*256+simulator.registers[E], simulator.registers[SP]) != (result_a, result_f, 0x7777, key, 0x8000):
            raise ValueError(f"Не совпал регистровый выход активации {flags:02X}/{key}/{previous}")
        for reg in (*range(2, 4), *range(8, 12), *range(18, 23)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Активация изменила сохраняемый регистр")
        if (memory[0x4000:0x6000] != expected_bitmap or memory[0x8600:0x8900] != expected_map
                or local_wakeups != expected_wakeups):
            raise ValueError(f"Не совпал bitmap, карта либо HALT активации {flags:02X}/{key}/{previous}")
        for item_key in (0, 45):
            if memory[0xF101+16*item_key] != final_flags[item_key]:
                raise ValueError("Не совпали флаги прежнего либо нового элемента")
        expected_list_bytes = [byte for pointer in expected_list for byte in pointer.to_bytes(2, "little")]+[1, 1]
        if (memory[0xE000:0xE006] != expected_list_bytes or memory[0x9E78] != expected_active
                or memory[0x9E7E:0x9E80] != list(expected_index.to_bytes(2, "little"))
                or memory[0x9E8B:0x9E8D] != [0x77, 0x77]):
            raise ValueError("Не совпали список и операнды активного элемента")
        if memory[0x9B16] != (0 if redraw_order else 0x5A):
            raise ValueError("Не совпал запрет обновления указателя")
        modeled_wakeups += local_wakeups
        cases += 1
    report = dict(passed=True, method="original_activation_full_close_toggle_list_bitmap_and_pointer",
                  cases=cases, transitions=transitions, already_selected=already_selected,
                  modeled_wakeups=modeled_wakeups, source_sha256=hashlib.sha256(source).hexdigest(),
                  original_visited=observed, next_callback_is_fixture=True, text_fixture="empty_LF_terminated",
                  interrupt_handler_executed=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/ActiveItemVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
