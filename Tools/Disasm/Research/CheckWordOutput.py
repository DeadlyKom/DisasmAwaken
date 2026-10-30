"""Проверка двух исходных печатателей слова, их разного статуса переноса и сохранения регистров."""

from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP


def reference(entry, text, widths, x, y, width, height, origin, bc=0x36C9, e=0x7A, positions=None):
    pointer, calls = 0, []
    for _ in range(1000):
        code = text[pointer]
        pointer += 1
        if code == 13:
            return pointer, x, y, 1, 0, bc, 1, calls
        if code == 10:
            return pointer, x, y, 10, (0x49 if entry == 0xADA7 else 0x4A), bc, e, calls
        if code == 32:
            return pointer, x, y, 33, 0x20, bc, e, calls
        calls.append(code)
        if positions is not None:
            positions.append((code, x, y))
        # Проверка причин отказа в порядке исходного DrawGlyph.
        if y >= height:
            status = 2
        elif x+widths[code] > 255 or x+widths[code] >= width:
            status = 3
        else:
            px, py = (origin[0]+x) & 65535, (origin[1]+y) & 65535
            x = (x+widths[code]) & 255
            if px & 0x8000:
                status = None
            elif px >> 8:
                status = 0
            elif py & 0x8000:
                status = None
            elif py >> 8 or py >= 185:
                status = 1
            else:
                status = None
        if status is None or status == 0:
            continue
        if status in (1, 2):
            return pointer, x, y, 0, 0x44, bc, e, calls
        # Расчёт байтового перехода строки, указатель остаётся на отказавшем символе.
        pointer -= 1
        next_y = (y+8) & 255
        bc = height*256+next_y
        accepted = next_y < height
        if accepted:
            x, y = 0, next_y
        if entry == 0xADA7:
            return pointer, x, y, 0, 0x44, bc, e, calls
        return pointer, x, y, int(accepted), (0 if accepted else 0x43), bc, e, calls
    raise ValueError("Эталон не нашёл ограничитель слова")


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5]
    simulator = Simulator(memory)
    widths = source[0x2900:0x2A00]
    initial = get_registers({"SP": 0x7FFE, "HL": 0x8000, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases, kinds = 0, {}

    def execute(start, text, x=0, y=0, width=200, height=192, origin=(0, 0), kind="word"):
        nonlocal cases
        expected = reference(start, text, widths, x, y, width, height, origin)
        memory[0x8000:0x8000+len(text)] = text
        for address, byte in ((0x6320, x), (0x6321, y), (0xAEAB, height), (0xAEB3, width),
                              (0xAEBB, origin[0] & 255), (0xAEBF, origin[0] >> 8),
                              (0xAEC7, origin[1] & 255), (0xAECB, origin[1] >> 8)):
            memory[address] = byte
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[PC] = start
        calls = []
        for _ in range(10000):
            if simulator.registers[PC] == 0x3FFF:
                break
            if simulator.registers[PC] == 0xAE8D:
                calls.append(simulator.registers[A])
                sp = simulator.registers[SP]
                simulator.run(stop=memory[sp]+256*memory[sp+1])
            else:
                simulator.run()
        else:
            raise ValueError("Исходный печататель слова не завершился")
        actual = (simulator.registers[H]*256+simulator.registers[L]-0x8000,
                  memory[0x6320], memory[0x6321], simulator.registers[A], simulator.registers[F],
                  simulator.registers[B]*256+simulator.registers[C], simulator.registers[E], calls)
        if actual != expected:
            raise ValueError(f"Не совпало слово start={start:04X}, text={text}, x={x}, y={y}, size={width}/{height}: {actual} != {expected}")
        for reg in (D, *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Изменился сохраняемый регистр печатателя слова")
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Нарушен стек печатателя слова")
        cases += 1
        kinds[kind] = kinds.get(kind, 0)+1

    for start in (0xADA7, 0xAE2A):
        # Проверка всех сочетаний X и ширины на первом обычном символе.
        for x in range(256):
            for width in range(256):
                execute(start, [65, 10], x=x, width=width, kind="width")
        # Проверка всех сочетаний Y и высоты при неизбежном отказе ширины.
        for y in range(256):
            for height in range(256):
                execute(start, [65, 10], y=y, width=0, height=height, kind="height_and_wrap")
        for code in range(256):
            for origin in ((0, 0), (256, 0), (65535, 0), (0, 185), (0, 256), (0, 65535)):
                execute(start, [code, 66, 10], origin=origin, kind="code_and_origin")
        generator = random.Random(start)
        for _ in range(2500):
            text = [generator.randrange(256) for _ in range(generator.randrange(1, 50))]+[10]
            execute(start, text, x=generator.randrange(256), y=generator.randrange(256),
                    width=generator.randrange(256), height=generator.randrange(256), kind="mixed_word")
    report = dict(method="two_original_word_printers_against_cursor_and_status_model", passed=True,
                  cases=cases, by_kind=kinds, source_sha256=hashlib.sha256(source).hexdigest(),
                  original_glyph_executed=True, glyph_pixels_disabled=True, irq_enabled=False,
                  native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/WordOutputVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
