"""Проверка исходного временного XOR-контура и двух его пиксельных ядер."""

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


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for i in region["instructions"]:
                if 0x41B7 <= i["address"] < 0x41E3:
                    raw = bytes.fromhex(i["hex"])
                    if source[i["offset"]:i["offset"]+len(raw)] != raw:
                        raise ValueError("Изменился построитель адресных таблиц")
                    memory[i["address"]:i["address"]+len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7, stop=0x41E3)
    dis = decoder(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    baseline = [(i*73+(i >> 8)*19+17) & 255 for i in range(8192)]
    observed = {}

    def run(start, hl, de, bc, flags=0xA4, trace=False):
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        for high, low, value in ((H, L, hl), (D, E, de), (B, C, bc)):
            simulator.registers[high], simulator.registers[low] = value >> 8, value & 255
        simulator.registers[F] = flags
        before = simulator.registers.copy()
        if trace:
            simulator.registers[PC] = start
            while simulator.registers[PC] != 0x3FFF:
                pc = simulator.registers[PC]
                instruction = dis.disassemble(pc, pc+1, "h")[0]
                raw = bytes(memory[pc:pc+len(instruction.bytes)])
                if 0xC4BE <= pc < 0xC626:
                    if raw == source[pc-0x6000:pc-0x6000+len(raw)]:
                        observed[f"{pc:04X}"] = raw.hex()
                    elif pc not in (0xC56F, 0xC5F4):
                        raise ValueError("Непредусмотренная самомодификация XOR-контура")
                simulator.run()
        else:
            simulator.run(start=start, stop=0x3FFF)
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Не восстановлен CPU-стек XOR-контура")
        corrupt = {A, F, H, L} if start == 0xC4BE else {A, F} if start == 0xC566 else {A, F, B, C}
        for reg in (*range(2, 12), *range(16, 24)):
            if reg not in corrupt and simulator.registers[reg] != before[reg]:
                raise ValueError("XOR-контур изменил сохраняемый регистр")

    def outline(width, height, column, row, carry=0, trace=False):
        left, right, top, bottom = max(0, column), min(32, column+width), max(0, row), min(24, row+height)
        expected = baseline.copy()
        # Четыре независимых XOR-отрезка, угловые пиксели инвертируются дважды.
        if row >= 0:
            for x in range(left, right):
                expected[bitmap_address(8*row, x)-0x4000] ^= 255
        if column >= 0:
            for y in range(8*top, 8*bottom):
                expected[bitmap_address(y, column)-0x4000] ^= 0x80
        if column+width <= 32:
            for y in range(8*top, 8*bottom):
                expected[bitmap_address(y, column+width-1)-0x4000] ^= 1
        if row+height <= 24:
            for x in range(left, right):
                expected[bitmap_address(8*(row+height)-1, x)-0x4000] ^= 255
        memory[0x4000:0x6000] = baseline
        args = (0xC4BE, 0x1357, height*256+width, (row & 255)*256+(column & 255), 0xA4|carry)
        run(*args, trace=trace)
        expected_hl = bitmap_address(8*bottom-1, left)
        if row+height <= 24:
            result_a = expected[bitmap_address(8*bottom-1, right-1)-0x4000]
            last_low = bitmap_address(8*bottom-1, right-1) & 255
            result_f = (last_low & 0x80 if right-left > 1 else 0) | (result_a & 0x28) | 0x12
        else:
            result_a, result_f = 0, 0x42
        if memory[0x4000:0x6000] != expected:
            raise ValueError(f"Не совпал XOR-контур {width}/{height}/{column}/{row}")
        if (simulator.registers[A], simulator.registers[F], simulator.registers[H]*256+simulator.registers[L]) != (
                result_a, result_f, expected_hl):
            raise ValueError(f"Не совпал выход XOR-контура {width}/{height}/{column}/{row}, "
                             f"actual={(simulator.registers[A], simulator.registers[F], simulator.registers[H]*256+simulator.registers[L])}, "
                             f"expected={(result_a, result_f, expected_hl)}")
        run(*args)
        if memory[0x4000:0x6000] != baseline:
            raise ValueError("Повторный XOR-контур не вернул исходный экран")

    # Чтение покрытия отдельно на трёх исходных ветвях отсечения и полном развёрнутом ядре.
    for values in ((32, 24, 0, 0), (32, 24, -1, -1), (32, 24, 1, 1), (1, 1, 31, 23)):
        outline(*values, trace=True)
    if sum(len(bytes.fromhex(value)) for value in observed.values()) != 0x168:
        raise ValueError("Не достигнута вся непрерывная кодовая область XOR-контура")
    parent_cases = 0
    for width, height, row in product(range(1, 33), range(1, 25), (-23, -1, 0, 1, 22, 23)):
        if row+height <= 0:
            continue
        for column in {1-width, -1, 0, (32-width)//2, 32-width, 31}:
            if column+width <= 0:
                continue
            for carry in (0, 1):
                outline(width, height, column, row, carry)
                parent_cases += 1
    row_cases = 0
    for width, y in product(range(1, 33), (0, 7, 63, 64, 191)):
        for column in {0, (32-width)//2, 32-width}:
            expected = baseline.copy()
            start = bitmap_address(y, column)
            for x in range(width):
                expected[start-0x4000+x] ^= 255
            memory[0x4000:0x6000] = baseline
            run(0xC566, start, 0x1200+width, 0x36C9)
            result_a = expected[start-0x4000+width-1]
            result_f = ((start+width-1) & 0x80 if width > 1 else 0) | (result_a & 0x28) | 0x12
            if memory[0x4000:0x6000] != expected or (simulator.registers[A], simulator.registers[F]) != (result_a, result_f):
                raise ValueError("Не совпала горизонтальная развёртка")
            row_cases += 1
    column_cases = 0
    for mask, row in product(range(256), (0, 7, 23)):
        for height, column in product(range(1, 25-row), (0, 31)):
            expected = baseline.copy()
            for y in range(row*8, (row+height)*8):
                expected[bitmap_address(y, column)-0x4000] ^= mask
            memory[0x4000:0x6000] = baseline
            memory[0xC5F5] = mask
            run(0xC5F2, bitmap_address(row*8, column), height*256+0xA5, 0x36C9)
            boundary = (row+height) % 8 == 0
            result_a = column if boundary else bitmap_address((row+height)*8, column) >> 8
            if memory[0x4000:0x6000] != expected or (simulator.registers[A], simulator.registers[F],
                    simulator.registers[B], simulator.registers[C]) != (result_a, 0x42|int(boundary), mask, 0):
                raise ValueError("Не совпало вертикальное ядро")
            column_cases += 1
    report = dict(passed=True, method="original_xor_outline_against_four_clipped_pixel_segments_and_full_kernels",
                  parent_cases=parent_cases, second_draw_restores_background=True, row_cases=row_cases,
                  column_cases=column_cases, source_sha256=hashlib.sha256(source).hexdigest(),
                  original_visited=observed, bitmap_and_attributes_compared=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/XorOutlineVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
