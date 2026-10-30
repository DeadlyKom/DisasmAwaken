"""Проверка исходного текстового потока, управляющих кодов, переносов и отказов глифа."""

from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, H, L, PC, SP, R
from CheckGlyphRenderer import compare_flags


def reference(text, widths, x, y, width, height, mode, columns, origin, delimiter, recover=False, stop_on_cr=False, positions=None):
    pointer, calls = 0, []

    def skip_line():
        nonlocal pointer
        while text[pointer] not in (10, 13):
            pointer += 1
        if text[pointer] == 10:
            pointer += 1
            return True
        return False

    if recover:
        if mode:
            pointer += 1
        elif skip_line():
            return pointer, x, y, 10, 0x4A, calls
    for _ in range(2000):
        code = text[pointer]
        pointer += 1
        if code == 10:
            return pointer, x, y, 10, 0x4A, calls
        if code == 1:
            return pointer, x, y, 0, 0x44, calls
        if 2 <= code <= 6:
            x = columns[code-2]
            continue
        if code == 0:
            total = 0
            while True:
                char = text[pointer]
                if char in (13, 10, delimiter):
                    return pointer, x, y, total, 0x42 | (char & 0x28), calls
                summed = total + widths[char]
                result = summed & 255
                flags = ((result & 0xA8) | (0x40 if result == 0 else 0)
                         | ((total ^ widths[char] ^ result) & 16)
                         | (4 if (~(total ^ widths[char]) & (total ^ result) & 128) else 0)
                         | int(summed > 255))
                if summed > 255 or result == 0:
                    return pointer, x, y, 255, flags, calls
                pointer += 1
                total = result
        next_line = code == 13
        if not next_line:
            calls.append(code)
            if positions is not None:
                positions.append((code, x, y))
            # Проверка глифа в том же порядке, что и доказанный контракт DrawGlyph.
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
            if status is None:
                continue
            pointer -= 1
            if status in (1, 2):
                return pointer, x, y, 0, 0x41, calls
            if status == 0:
                if mode:
                    pointer += 1
                elif skip_line():
                    return pointer, x, y, 10, 0x4A, calls
                continue
            if mode:
                next_line = True
            elif skip_line():
                return pointer, x, y, 10, 0x4A, calls
            else:
                continue
        if next_line:
            next_y = (y+8) & 255
            if next_y >= height:
                flags = (compare_flags(next_y, height) & 0xC4) | (next_y & 0x28) | 1
                return pointer, x, y, next_y, flags, calls
            x, y = 0, next_y
            if code == 13 and stop_on_cr:
                return pointer, x, y, 0, 0x44, calls
    raise ValueError("Эталон вошёл в повторяющийся поток, требуется отдельная проверка цикла")


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x8000, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    widths = source[0x2900:0x2A00]
    cases, kinds = 0, {}

    def execute(text, x=0, y=0, width=200, height=192, mode=0,
                columns=(0, 17, 42, 100, 255), origin=(0, 0), delimiter=54, recover=False, kind="stream", stop_on_cr=False):
        nonlocal cases
        expected = reference(text, widths, x, y, width, height, mode, columns, origin, delimiter, recover, stop_on_cr)
        memory[0x8000:0x8000+len(text)] = text
        # Настройка исходных изменяемых операндов, как это делают игровые обработчики.
        for address, byte in ((0x6320, x), (0x6321, y), (0xAEAB, height), (0xAEB3, width),
                              (0xAEBB, origin[0] & 255), (0xAEBF, origin[0] >> 8),
                              (0xAEC7, origin[1] & 255), (0xAECB, origin[1] >> 8), (0xBD26, mode)):
            memory[address] = byte
        for address, value in zip((0xBD73, 0xBD7E, 0xBD89, 0xBD94, 0xBD9F), columns):
            memory[address] = value
        memory[0xBD4F] = 0xC9 if stop_on_cr else 0xC3
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[B] = delimiter
        simulator.registers[PC] = 0xBD01 if recover else 0xBD08
        calls = []
        for _ in range(30000):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if pc == 0xAE8D:
                calls.append(simulator.registers[A])
                sp = simulator.registers[SP]
                return_pc = memory[sp]+256*memory[sp+1]
                simulator.run(stop=return_pc)
            else:
                simulator.run()
        else:
            raise ValueError("Исходный поток не завершился")
        actual = (simulator.registers[H]*256+simulator.registers[L]-0x8000,
                  memory[0x6320], memory[0x6321], simulator.registers[A], simulator.registers[F], calls)
        if actual != expected:
            raise ValueError(f"Не совпал поток {text}, mode={mode}, x={x}, y={y}, size={width}/{height}, origin={origin}: {actual} != {expected}")
        for reg in (B, C, *range(4, 6), *range(8, 12), *range(16, 24)):
            expected_reg = delimiter if reg == B else initial[reg]
            if simulator.registers[reg] != expected_reg:
                raise ValueError("Поток изменил сохраняемый регистр")
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Поток нарушил баланс стека")
        cases += 1
        kinds[kind] = kinds.get(kind, 0)+1

    # Проверка всех сочетаний относительной строки и высоты на единственном CR перед LF.
    for y in range(256):
        for height in range(256):
            execute([13, 10], x=123, y=y, height=height, kind="carriage_return")
    # Проверка каждого байта потока и всех значений режима, включая нулевой хвост измерителя.
    for code in range(256):
        for mode in range(256):
            execute([code, 65, 66, 13, 67, 10], width=17, mode=mode, kind="code_and_mode")
    # Проверка штатной подмены JP на RET после явного CR в центрирующем выводе.
    for y in range(256):
        for height in range(256):
            execute([13, 10], x=123, y=y, height=height, kind="return_after_cr", stop_on_cr=True)
    for code in range(256):
        for mode in range(256):
            execute([code, 65, 66, 13, 67, 10], width=17, mode=mode,
                    kind="patched_code_and_mode", stop_on_cr=True)
    for recover in (False, True):
        for mode in (0, 1, 2, 128, 255):
            for origin in ((0, 0), (65535, 0), (256, 0), (0, 185), (0, 256), (0, 65535)):
                for width in (0, 1, 5, 10, 255):
                    for y in (0, 184, 185, 191, 248, 255):
                        execute([65, 66, 13, 67, 10], x=3, y=y, width=width, mode=mode,
                                origin=origin, recover=recover, kind="geometry_and_recovery")
    generator = random.Random(0xBD08)
    for _ in range(5000):
        text = [generator.choice([*range(0, 14), 32, 48, 65, 128, 255])
                for _ in range(generator.randrange(1, 40))]+[10]
        execute(text, x=generator.randrange(256), y=generator.randrange(256),
                width=generator.randrange(256), height=generator.randrange(193),
                mode=generator.randrange(256), columns=tuple(generator.randrange(256) for _ in range(5)),
                delimiter=generator.randrange(256), kind="mixed_stream")
    # Проверка повторения исходного состояния при ширине ноль и высоте выше 248.
    cyclic_cases = 0
    for height in range(249, 256):
        for residue in range(height-248):
            memory[0x8000:0x8002] = [65, 10]
            memory[0x6320:0x6322] = [0, residue]
            for address, value in ((0xAEAB, height), (0xAEB3, 0), (0xBD26, 1),
                                   (0xAEBB, 0), (0xAEBF, 0), (0xAEC7, 0), (0xAECB, 0)):
                memory[address] = value
            memory[0x7FFE:0x8000] = [0xFF, 0x3F]
            simulator.registers[:] = initial
            simulator.registers[PC] = 0xBD08
            states = []
            for _ in range(15000):
                if simulator.registers[PC] == 0xAE8D:
                    # R меняется при выборке инструкций, текущий исходный поток его не читает.
                    states.append((tuple(v for i, v in enumerate(simulator.registers[:24]) if i != R), tuple(memory[0x6320:0x6322]),
                                   tuple(memory[0x7FF0:0x8000])))
                    if len(states) == 65:
                        break
                    sp = simulator.registers[SP]
                    simulator.run(stop=memory[sp]+256*memory[sp+1])
                else:
                    simulator.run()
            else:
                raise ValueError("Не достигнуты три оборота ожидаемого цикла переноса")
            # Первый оборот заполняет рабочие слова стека, сравниваются два последующих состояния.
            if states[32] != states[64]:
                raise ValueError(f"Повторение переноса не сохранило состояние двух оборотов: {states[32]} != {states[64]}")
            cyclic_cases += 1
    report = dict(method="original_text_stream_against_control_and_cursor_model", passed=True,
                  cases=cases, by_kind=kinds, source_sha256=hashlib.sha256(source).hexdigest(),
                  original_glyph_executed=True, glyph_pixels_disabled=True,
                  demonstrated_wrap_cycles=cyclic_cases,
                  line_return_patch_cases=kinds["return_after_cr"]+kinds["patched_code_and_mode"],
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/TextStreamVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
