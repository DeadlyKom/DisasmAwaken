"""Проверка подсчёта выровненных строк и пропуска строк перед печатью."""

from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP
from CheckJustifiedText import reference as layout


def reference(start, text, widths, coords, width, height, skip, initial_d=0x24, positions=None, origin=(0, 0)):
    x, y, bc, d, e, pointer, calls = 0, coords >> 8, coords, initial_d, skip, 0, []
    if start == 0xA82D:
        count = 0
        for _ in range(1000):
            result = layout(0xAD35, text[pointer:], widths, x, 8, width, height, bc, count >> 8, count & 255, origin=origin)
            consumed, x, y, a, f, bc, _, _, attempted = result
            pointer += consumed
            calls.extend(attempted)
            count = (count+1) & 65535
            if f & 1:
                return pointer, x, y, a, f, bc, count >> 8, count & 255, calls
        raise ValueError("Подсчёт строк не достиг завершения")
    x, y = coords & 255, coords >> 8
    for _ in range(skip):
        result = layout(0xAD35, text[pointer:], widths, x, y, width, height, coords, d, e, origin=origin)
        consumed, _, _, a, f, _, _, _, attempted = result
        pointer += consumed
        calls.extend(attempted)
        if f & 1:
            return pointer, x, y, a, f, coords, d, e, calls
        e = (e-1) & 255
    result = layout(0xADCD, text[pointer:], widths, x, y, width, height, coords, d, e, positions=positions, origin=origin)
    consumed, x, y, a, f, bc, d, e, attempted = result
    calls.extend(attempted)
    return pointer+consumed, x, y, a, f, bc, d, e, calls


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

    def execute(start, raw, coords=0x0803, width=100, height=192, skip=0, kind="pagination"):
        nonlocal cases
        text = list(raw)+[10]*1024
        expected = reference(start, text, widths, coords, width, height, skip)
        memory[0x8000:0x8000+len(text)] = text
        memory[0x6320:0x6322] = [127, 250]
        for address, value in ((0xAEAB, height), (0xAEB3, width), (0xAEBB, 0), (0xAEBF, 0), (0xAEC7, 0), (0xAECB, 0)):
            memory[address] = value
        memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[B], simulator.registers[C] = coords >> 8, coords & 255
        simulator.registers[E] = skip
        simulator.registers[PC] = start
        calls = []
        for _ in range(300000):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if pc == 0xAD35:
                # Вход сухого прохода требует исходного префикса, затем сам восстанавливает его.
                memory[0xAED5:0xAED8] = list(source[0x4ED5:0x4ED8])
            if pc == 0xADCD:
                # Пиксели проверены отдельно, в этой модели измеряется поток и курсор.
                memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5]
            if pc == 0xAE8D:
                calls.append(simulator.registers[A])
                sp = simulator.registers[SP]
                simulator.run(stop=memory[sp]+256*memory[sp+1])
            else:
                simulator.run()
        else:
            raise ValueError("Исходная пагинация не завершилась")
        actual = (simulator.registers[H]*256+simulator.registers[L]-0x8000,
                  *memory[0x6320:0x6322], simulator.registers[A], simulator.registers[F],
                  simulator.registers[B]*256+simulator.registers[C], simulator.registers[D], simulator.registers[E], calls)
        if actual != expected:
            raise ValueError(f"Не совпала пагинация #{start:04X}, size={width}/{height}, coords={coords:04X}, skip={skip}: {actual} != {expected}")
        for reg in (*range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Пагинация изменила сохраняемый регистр")
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Нарушен стек пагинации")
        cases += 1
        kinds[kind] = kinds.get(kind, 0)+1

    for width in (9, 17, 32, 64, 128, 255):
        for height in (0, 13, 17, 24, 192, 255):
            for text in (b"A\n", b"ONE TWO THREE FOUR FIVE\n", b"ONE\rTWO\rTHREE\n", b" ", b"A"*100+b"\n"):
                execute(0xA82D, text, width=width, height=height, kind="count")
    for skip in range(256):
        for coords in (0, 0x0803, 0xB8FE, 0xFF00):
            execute(0xA843, b"ONE TWO THREE FOUR FIVE SIX SEVEN\n", coords=coords, skip=skip, kind="skip_byte")
    generator = random.Random(0xA843)
    for _ in range(1000):
        text = bytes(generator.choice([32, 32, 13, 10, 65, 66, 128, 255])
                     for _ in range(generator.randrange(1, 70)))+b"\n"
        execute(0xA843, text, coords=generator.randrange(65536), width=generator.randrange(256),
                height=generator.randrange(193), skip=generator.randrange(16), kind="mixed_skip")
    # Проверка отсутствия продвижения при нулевой ширине либо отказавшем переносе высоты 14.
    stalled = 0
    for width, height in ((0, 192), (9, 14)):
        memory[0x6000:] = source
        memory[0x8000:0x8000+1125] = [65]*100+[10]*1025
        for address, value in ((0xAEAB, height), (0xAEB3, width), (0xAEBB, 0), (0xAEBF, 0), (0xAEC7, 0), (0xAECB, 0)):
            memory[address] = value
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[PC] = 0xA82D
        states, counts = [], []
        for _ in range(100000):
            pc = simulator.registers[PC]
            if pc == 0xAD35:
                states.append((simulator.registers[H]*256+simulator.registers[L],
                               tuple(memory[0x6320:0x6322]), simulator.registers[B]*256+simulator.registers[C]))
                counts.append(simulator.registers[D]*256+simulator.registers[E])
                if len(states) == 34:
                    break
            if pc == 0xAE8D:
                sp = simulator.registers[SP]
                simulator.run(stop=memory[sp]+256*memory[sp+1])
            else:
                simulator.run()
        else:
            raise ValueError("Не воспроизведён ожидаемый повтор подсчёта без продвижения")
        if any(state != states[2] for state in states[2:]) or counts != list(range(34)):
            raise ValueError("Повтор подсчёта изменил положение текста либо счётчик")
        stalled += 1
    report = dict(method="original_text_pagination_against_composed_row_contracts", passed=True,
                  cases=cases, by_kind=kinds, source_sha256=hashlib.sha256(source).hexdigest(),
                  full_renderer_pixels_disabled_in_fixture=True, original_glyph_executed=True,
                  glyph_prefix_adjusted_at_layout_entries=True, demonstrated_nonprogress_cases=stalled,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/TextPaginationVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
