"""Сравнение исходных проходов выравнивания с выбором слов и расчётом межсловного промежутка."""

from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP
from CheckWordOutput import reference as word
from CheckGlyphRenderer import and_flags, compare_flags


def choose_row(text, pointer, widths, width):
    previous, count = 0, 0
    for _ in range(512):
        measured = 0
        while text[pointer] not in (10, 13, 32):
            total = measured+widths[text[pointer]]
            if total > 255 or (total & 255) == 0:
                measured = 255
                break
            measured = total
            pointer += 1
        pointer += 1
        count = (count+1) & 255
        total = previous+((measured+2) & 255)
        wrapped = total & 255
        if total > 255 or wrapped >= width:
            selected = (count-1) & 255
            if total <= 255 and ((wrapped-2) & 255) < width and count == 1:
                selected = 1
            return selected, previous
        previous = wrapped
    raise ValueError("Не завершается выбор набора слов строки")


def reference(start, text, widths, x, y, width, height, bc=0x36C9, d=0x24, e=0x7A, positions=None, origin=(0, 0)):
    pointer, calls = 0, []
    if height < 14:
        return pointer, x, y, height, compare_flags(height, 14), bc, d, e, calls
    dry = start == 0xAD35
    for _ in range(1000):
        count, d = choose_row(text, pointer, widths, width)
        e, bc = count, 0x2000+width

        def print_word():
            nonlocal pointer, x, y, bc, e
            result = word(0xADA7 if dry else 0xAE2A, text[pointer:], widths,
                          x, y, width, height, origin, bc, e, positions)
            consumed, x, y, a, f, bc, e, attempted = result
            pointer += consumed
            calls.extend(attempted)
            return a, f

        if count == 0:
            a, f = print_word()
            if dry or f & 0x40:
                return pointer, x, y, (0x68 if dry else a), f, bc, (0x26 if dry else d), (0x48 if dry else e), calls
            continue
        remaining = (width-d) & 255
        d = remaining if count == 1 else remaining//(count-1)
        for _ in range(256):
            a, f = print_word()
            if f & 0x40:
                return pointer, x, y, (0x68 if dry else a), f, bc, (0x26 if dry else d), (0x48 if dry else e), calls
            x = (x+2+d) & 255
            e = (e-1) & 255
            if e == 0:
                break
        else:
            raise ValueError("Не завершилась группа слов")
        next_y = (y+8) & 255
        bc = height*256+next_y
        accepted = next_y < height
        if accepted:
            x, y, a, f = 0, next_y, 0, 0x44
        else:
            a = next_y
            f = (compare_flags(next_y, height) & 0xC4) | (next_y & 0x28) | 1
        if dry:
            return pointer, x, y, 0x68, and_flags(a), bc, 0x26, 0x48, calls
        if not accepted:
            return pointer, x, y, a, f, bc, d, e, calls
    raise ValueError("Выравнивание не достигло выхода")


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    widths = source[0x2900:0x2A00]
    initial = get_registers({"SP": 0x7FFE, "HL": 0x8000, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases, kinds = 0, {}

    def execute(start, text, x=0, y=0, width=100, height=192, kind="layout"):
        nonlocal cases
        # Запас читаемых байтов нужен для исходного просмотра вперёд за LF, он не останавливает выбор слов.
        text = list(text)+[10]*1024
        expected = reference(start, text, widths, x, y, width, height)
        memory[0x8000:0x8000+len(text)] = text
        memory[0x6320:0x6322] = [x, y]
        for address, value in ((0xAEAB, height), (0xAEB3, width), (0xAEBB, 0), (0xAEBF, 0), (0xAEC7, 0), (0xAECB, 0)):
            memory[address] = value
        # Сухой проход сам устанавливает и снимает этот JP, полный проход проверяется без записи пикселей.
        prefix = list(source[0x4ED5:0x4ED8]) if start == 0xAD35 else [0xC3, 0x14, 0xB5]
        memory[0xAED5:0xAED8] = prefix
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[PC] = start
        calls = []
        for _ in range(150000):
            if simulator.registers[PC] == 0x3FFF:
                break
            if simulator.registers[PC] == 0xAE8D:
                calls.append(simulator.registers[A])
                sp = simulator.registers[SP]
                simulator.run(stop=memory[sp]+256*memory[sp+1])
            else:
                simulator.run()
        else:
            raise ValueError("Исходный выравниватель не завершился")
        actual = (simulator.registers[H]*256+simulator.registers[L]-0x8000,
                  memory[0x6320], memory[0x6321], simulator.registers[A], simulator.registers[F],
                  simulator.registers[B]*256+simulator.registers[C], simulator.registers[D], simulator.registers[E], calls)
        if actual != expected:
            raise ValueError(f"Не совпало выравнивание #{start:04X}, size={width}/{height}, x={x}, y={y}, text={text[:80]}: {actual} != {expected}")
        if memory[0xAED5:0xAED8] != prefix:
            raise ValueError("Сухой проход не восстановил исходный префикс глифа")
        for reg in (*range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Изменён сохраняемый регистр выравнивателя")
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Нарушен стек выравнивателя")
        cases += 1
        kinds[kind] = kinds.get(kind, 0)+1

    fixtures = (b"A B C D E\n", b"ONE TWO THREE FOUR FIVE\n", b"A\rB C D\n",
                b"A  B   C\n", b"\n", b" ", b"A"*60+b" B C\n")
    for start in (0xAD35, 0xADCD):
        for text in fixtures:
            for width in range(256):
                execute(start, text, width=width, kind="width_and_words")
        for height in range(256):
            for y in (0, 8, 184, 192, 248, 255):
                execute(start, b"ONE TWO THREE FOUR\n", y=y, height=height, kind="height")
        generator = random.Random(start)
        for _ in range(2500):
            text = bytes(generator.choice([32, 32, 13, 10, 65, 66, 67, 128, 255])
                         for _ in range(generator.randrange(1, 70)))+b"\n"
            execute(start, text, x=generator.randrange(256), y=generator.randrange(256),
                    width=generator.randrange(1, 256), height=generator.randrange(256), kind="mixed_layout")
    report = dict(method="original_justification_against_word_selection_and_gap_model", passed=True,
                  cases=cases, by_kind=kinds, source_sha256=hashlib.sha256(source).hexdigest(),
                  full_renderer_pixels_disabled_in_fixture=True, dry_pass_restores_glyph_prefix=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/JustifiedTextVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
