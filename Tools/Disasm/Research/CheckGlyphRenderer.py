"""Пиксельная проверка исходного XOR-рисователя глифа и сбор достигнутых неизменённых инструкций."""

from pathlib import Path
import hashlib
import json
import sys
from itertools import product

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, PC, SP
from InspectZ80 import decoder
from CheckInsetFrame import bitmap_address


def and_flags(value):
    return 0x10 | (value & 0xA8) | (0x40 if value == 0 else 0) | (4 if value.bit_count() % 2 == 0 else 0)


def compare_flags(left, right):
    result = (left - right) & 255
    return ((result & 0x80) | (right & 0x28) | (0x40 if result == 0 else 0)
            | ((left ^ right ^ result) & 0x10)
            | (4 if (left ^ right) & (left ^ result) & 128 else 0) | 2 | int(left < right))


class ObservedMemory(list):
    def __init__(self):
        super().__init__([0] * 65536)
        self.recording = False
        self.written = set()
        self.targets = []

    def __setitem__(self, index, value):
        if self.recording and isinstance(index, int):
            self.written.add(index)
        super().__setitem__(index, value)
        if self.recording and index == 0xAF0B:
            self.targets.append(self[0xAF0A] + 256*self[0xAF0B])


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = ObservedMemory()
    memory[0x6000:0x6000 + len(source)] = source
    simulator = Simulator(memory)
    # Создание адресных таблиц исходным перенесённым фрагментом загрузчика.
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for instruction in region["instructions"]:
                if 0x41B7 <= instruction["address"] < 0x41E3:
                    data = bytes.fromhex(instruction["hex"])
                    if source[instruction["offset"]:instruction["offset"] + len(data)] != data:
                        raise ValueError("Не совпали байты построителя адресных таблиц")
                    memory[instruction["address"]:instruction["address"] + len(data)] = data
    simulator.run(start=0x41B7, stop=0x41E3)
    # Декодер использует исходное рабочее представление, изменяемый JP проверяется отдельно.
    original_memory = [0] * 65536
    original_memory[0x6000:0x6000 + len(source)] = source
    dis = decoder(original_memory)
    visited = {}
    modified = set()
    lengths = {}
    routes = set()
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases = list(product(range(256), (*range(8), *range(248, 256)), range(8)))
    cases += list(product((0, 32, 65, 128, 255), (*range(16), *range(240, 256)),
                          (*range(56, 64), *range(120, 128), *range(176, 185))))
    checked = 0
    for char, x, y in cases:
        # Создание контрастного фона позволяет сверить XOR, соседние байты и атрибуты.
        memory[0x4000:0x6000] = [0x96] * 0x2000
        expected = memory[0x4000:0x6000].copy()
        glyph = source[0x2A00 + 8*char:0x2A00 + 8*char + 8]
        for row, bits in enumerate(glyph):
            for bit in range(8):
                px = x + bit
                if px < 256 and bits & (128 >> bit):
                    address = bitmap_address(y + row, px >> 3) - 0x4000
                    expected[address] ^= 128 >> (px & 7)
        # Геометрия окна отделена от физического начала, проверяются все восемь сдвигов у правого края.
        for address, value in ((0x6320, 0), (0x6321, 0), (0xAEAB, 192), (0xAEB3, 255),
                               (0xAEBB, x), (0xAEBF, 0), (0xAEC7, y), (0xAECB, 0)):
            memory[address] = value
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = char, char ^ 0xA5
        before = simulator.registers.copy()
        memory.written.clear()
        memory.targets.clear()
        memory.recording = True
        trace = char == 65
        if trace:
            simulator.registers[PC] = 0xAE8D
            for _ in range(1000):
                pc = simulator.registers[PC]
                if pc == 0x3FFF:
                    break
                if not 0xAE55 <= pc < 0xBCAB:
                    raise ValueError(f"Неожиданный вход рисователя #{pc:04X}")
                if pc not in lengths:
                    instruction = dis.disassemble(pc, pc+1, "h")[0]
                    lengths[pc] = len(instruction.bytes)
                length = lengths[pc]
                data = bytes(memory[pc:pc+length])
                if data == bytes(original_memory[pc:pc+length]):
                    visited[f"{pc:04X}"] = data.hex()
                else:
                    modified.add(pc)
                simulator.run()
            else:
                raise ValueError("Рисователь не вернулся за ограниченное число инструкций")
        else:
            simulator.run(start=0xAE8D, stop=0x3FFF)
        memory.recording = False
        if memory[0x4000:0x6000] != expected:
            raise ValueError(f"Не совпали пиксели char={char}, x={x}, y={y}")
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP], memory[0x6320], memory[0x6321]) != (
                0, 0x45, 0x8000, source[0x2900 + char], 0):
            raise ValueError("Не совпал статус, курсор или CPU-стек глифа")
        for register in (*range(2, 12), *range(16, 24)):
            if simulator.registers[register] != before[register]:
                raise ValueError("Рисователь изменил сохраняемый регистр")
        if any(not (0x4000 <= address < 0x5800 or 0x7FE0 <= address < 0x8000
                    or address in (0x6320, 0xAF0A, 0xAF0B)) for address in memory.written):
            raise ValueError("Рисователь записал непредусмотренную область памяти")
        route = (2*(x & 7) + int(x >= 248))*8 + (y & 7)
        routes.add(route)
        target = int.from_bytes(source[0x3200 + 4*route:0x3202 + 4*route], "little")
        targets = [target]
        if y & 7:
            targets.append(int.from_bytes(source[0x3202 + 4*route:0x3204 + 4*route], "little"))
        if memory.targets != targets:
            raise ValueError(f"Не совпали цели char={char}, x={x}, y={y}, actual={memory.targets}, expected={targets}")
        checked += 1
        if checked % 8192 == 0:
            print(f"Проверено глифов и положений {checked}/{len(cases)}", flush=True)
    synthetic_cases = 0
    char = 65
    glyph_address = 0x8A00 + 8*char
    original_glyph = memory[glyph_address:glyph_address+8].copy()
    for bits, x, y in product(range(256), (*range(8), *range(248, 256)), range(8)):
        # Проверка всех битовых строк исключает зависимость вывода только от 40 рисунков исходного шрифта.
        memory[glyph_address:glyph_address+8] = [bits] * 8
        memory[0x4000:0x6000] = [0x96] * 0x2000
        expected = memory[0x4000:0x6000].copy()
        for row in range(8):
            for bit in range(8):
                px = x+bit
                if px < 256 and bits & (128 >> bit):
                    expected[bitmap_address(y+row, px >> 3)-0x4000] ^= 128 >> (px & 7)
        for address, value in ((0x6320, 0), (0x6321, 0), (0xAEAB, 192), (0xAEB3, 255),
                               (0xAEBB, x), (0xAEBF, 0), (0xAEC7, y), (0xAECB, 0)):
            memory[address] = value
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = char, bits ^ 0xA5
        before = simulator.registers.copy()
        memory.written.clear()
        memory.targets.clear()
        memory.recording = True
        simulator.run(start=0xAE8D, stop=0x3FFF)
        memory.recording = False
        if memory[0x4000:0x6000] != expected:
            raise ValueError(f"Граничный рисунок не совпал bits={bits:02X}, x={x}, y={y}")
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP], memory[0x6320]) != (0, 0x45, 0x8000, source[0x2900+char]):
            raise ValueError("Не совпал статус синтетического глифа")
        for register in (*range(2, 12), *range(16, 24)):
            if simulator.registers[register] != before[register]:
                raise ValueError("Синтетический глиф изменил сохраняемый регистр")
        if any(not (0x4000 <= address < 0x5800 or 0x7FE0 <= address < 0x8000
                    or address in (0x6320, 0xAF0A, 0xAF0B)) for address in memory.written):
            raise ValueError("Синтетический глиф записал непредусмотренную область")
        synthetic_cases += 1
    memory[glyph_address:glyph_address+8] = original_glyph
    char = 65
    width = source[0x2900 + char]
    scenarios = (
        ({0xAEAB: 0}, 2, and_flags(0), 0, None),
        ({0x6321: 5, 0xAEAB: 5}, 2, and_flags(5), 0, None),
        ({0x6320: 256-width}, 3, and_flags(0), 256-width, None),
        ({0x6320: 7, 0xAEB3: 7+width}, 3, and_flags(7+width), 7, None),
        ({0xAEBB: 255, 0xAEBF: 255}, 0, 0x45, width, None),
        ({0xAEBB: 255, 0x6320: 1}, 0, 0x44, 1+width, None),
        ({0xAEBB: 255, 0xAEBF: 255, 0x6320: 1}, 0, 0x45, 1+width, (0, 0)),
        ({0xAEC7: 255, 0xAECB: 255}, 0, 0x45, width, None),
        ({0xAEC7: 255, 0x6321: 1}, 1, 0, width, None),
        ({0xAEC7: 255, 0xAECB: 255, 0x6321: 1}, 0, 0x45, width, (0, 0)),
        ({0xAEC7: 185}, 1, compare_flags(185, 185), width, None),
        ({0xAEC7: 192}, 1, compare_flags(192, 185), width, None),
        ({0xAEC7: 255}, 1, compare_flags(255, 185), width, None),
        ({0xAEAB: 1}, 0, 0x45, width, (0, 0)),
        ({0xAEB3: width}, 3, and_flags(width), 0, None),
        ({0xAEB3: 1}, 3, and_flags(width), 0, None),
    )
    error_cases = 0
    for skip_drawing, (changes, expected_a, expected_f, cursor_x, point) in product((False, True), scenarios):
        memory[0x4000:0x6000] = [0x96] * 0x2000
        expected = memory[0x4000:0x6000].copy()
        fields = {0x6320: 0, 0x6321: 0, 0xAEAB: 192, 0xAEB3: 255,
                  0xAEBB: 0, 0xAEBF: 0, 0xAEC7: 0, 0xAECB: 0}
        fields.update(changes)
        for address, value in fields.items():
            memory[address] = value
        # Подстановка трёх исходно изменяемых байтов, используемая измерением текста без вывода.
        memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5] if skip_drawing else list(source[0x4ED5:0x4ED8])
        if point is not None and not skip_drawing:
            x, y = point
            for row, bits in enumerate(source[0x2A00 + 8*char:0x2A00 + 8*char + 8]):
                for bit in range(8):
                    if bits & (128 >> bit):
                        expected[bitmap_address(y+row, (x+bit) >> 3)-0x4000] ^= 128 >> ((x+bit) & 7)
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = char, 0xFF
        before = simulator.registers.copy()
        memory.written.clear()
        memory.targets.clear()
        memory.recording = True
        simulator.run(start=0xAE8D, stop=0x3FFF)
        memory.recording = False
        if (memory[0x4000:0x6000] != expected
                or (simulator.registers[A], simulator.registers[F], simulator.registers[SP], memory[0x6320], memory[0x6321]) != (
                    expected_a, expected_f, 0x8000, cursor_x, fields[0x6321])):
            raise ValueError(f"Не совпал отказ или режим без рисования, changes={changes}, skip={skip_drawing}, AF={simulator.registers[A]:02X}{simulator.registers[F]:02X}")
        for register in (*range(2, 12), *range(16, 24)):
            if simulator.registers[register] != before[register]:
                raise ValueError("Отказ глифа изменил сохраняемый регистр")
        if any(not (0x4000 <= address < 0x5800 or 0x7FE0 <= address < 0x8000
                    or address in (0x6320, 0xAF0A, 0xAF0B)) for address in memory.written):
            raise ValueError("Отказ глифа записал непредусмотренную область")
        if skip_drawing and memory.targets:
            raise ValueError("Режим без рисования изменил JP диспетчера")
        error_cases += 1
    report = {"method": "original_xor_glyph_renderer_against_pixel_reference_without_irq",
              "cases": checked, "routes_checked": len(routes), "passed": True,
              "source_sha256": hashlib.sha256(source).hexdigest(),
              "all_glyph_codes_checked": True, "attribute_writes_forbidden": True,
              "synthetic_row_byte_cases": synthetic_cases, "all_256_row_bytes_checked": True,
              "native_execution_verified": False, "error_paths_checked": True,
              "error_and_measurement_mode_cases": error_cases, "measurement_patch_checked": True,
              "other_runtime_opcode_patches_checked": False, "assembly_executed": False,
              "original_visited": dict(sorted(visited.items())),
              "modified_executed_addresses": [f"{address:04X}" for address in sorted(modified)]}
    (ROOT / "Tools/Disasm/Reports/GlyphRenderVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
