"""Проверка исходного пропуска A+1 ограничителей LF либо временного CR."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, H, L, SP
from skoolkit.simutils import D, E, PC
from CheckTextStream import reference as stream_reference
from CheckJustifiedText import reference as justify_reference


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x2000, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases = 0

    def execute(start, index, flags, low):
        nonlocal cases
        delimiter = 13 if start == 0xA380 else 10
        text, positions = [], []
        for record in range(256):
            text.extend([65+record % 20]*(record % 7))
            text.append(delimiter)
            positions.append(0x2000+len(text))
        memory[0x2000:0x2000+len(text)] = text
        memory[0xA397] = 10
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F], simulator.registers[C] = index, flags, low
        simulator.run(start=start, stop=0x3FFF)
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[A],
                simulator.registers[F], simulator.registers[SP], memory[0xA397]) != (
                positions[index], 10, 0x42 | (flags & 1), 0x8000, 10):
            raise ValueError("Не совпал пропуск ограничителей либо полный AF")
        for reg in (*range(2, 6), *range(8, 12), *range(16, 24)):
            expected = low if reg == C else initial[reg]
            if simulator.registers[reg] != expected:
                raise ValueError("Выбор текста изменил сохраняемый регистр")
        cases += 1

    for start in (0xA390, 0xA380):
        # Проверка всех индексов, включая 255, при котором байтовый счётчик даёт 256 повторов.
        for index in range(256):
            for low in (0, 1, 127, 255):
                for carry in (0, 1):
                    execute(start, index, carry, low)
        for index in (0, 1, 127, 255):
            for flags in range(256):
                execute(start, index, flags, 0xC9)
        for index in (0, 255):
            for low in range(256):
                for carry in (0, 1):
                    execute(start, index, carry, low)
    # Проверка исчерпания CPIR без найденного ограничителя в отдельной памяти.
    exhausted = 0
    for start in (0xA390, 0xA380):
        for carry in (0, 1):
            memory[:] = [0]*65536
            memory[0xA380:0xA3A1] = source[0x4380:0x43A1]
            memory[0x7FFE:0x8000] = [0xFF, 0x3F]
            simulator.registers[:] = initial
            simulator.registers[A], simulator.registers[F], simulator.registers[C] = 0, carry, 0
            simulator.registers[H], simulator.registers[L] = 0xA3, 0x98
            simulator.run(start=start, stop=0x3FFF)
            if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[A], simulator.registers[F]) != (
                    0xA298, 10, 0x42 | carry):
                raise ValueError("Не подтверждено исходное отсутствие проверки успеха CPIR")
            exhausted += 1
    # Проверка трёх реальных обёрток выбора записи с последующим текстовым проходом.
    memory[0x6000:] = source
    memory[0xAED5:0xAED8] = [0xC3, 0x14, 0xB5]
    widths = source[0x2900:0x2A00]
    wrappers = 0
    for start in (0xA36E, 0xA37A, 0xA374):
        separator = 13 if start == 0xA36E else 10
        text = list(b"ONE TWO"+bytes([separator]))*10+[10]*1024
        positions = [i+1 for i, byte in enumerate(text) if byte == separator]
        for index in (0, 1, 3, 7):
            selected = positions[index]
            for width in (0, 5, 20, 100, 255):
                for height in (0, 13, 14, 24, 192):
                    memory[0x8000:0x8000+len(text)] = text
                    memory[0x6320:0x6322] = [3, 8]
                    for address, value in ((0xA397, 10), (0xAEAB, height), (0xAEB3, width),
                                           (0xAEBB, 0), (0xAEBF, 0), (0xAEC7, 0), (0xAECB, 0), (0xBD26, 0)):
                        memory[address] = value
                    if start == 0xA374:
                        result = justify_reference(0xADCD, text[selected:], widths, 3, 8, width, height)
                        count, x, y, a, f, bc, d, e, attempts = result
                    else:
                        count, x, y, a, f, attempts = stream_reference(
                            text[selected:], widths, 3, 8, width, height, 0, (0, 0, 0, 0, 0), (0, 0), 0x36)
                        bc, d, e = 0x36C9, 0x24, 0x7A
                    memory[0x7FFE:0x8000] = [0xFF, 0x3F]
                    simulator.registers[:] = initial
                    simulator.registers[H], simulator.registers[L] = 0x80, 0
                    simulator.registers[A] = index
                    simulator.registers[PC] = start
                    called = []
                    for _ in range(150000):
                        if simulator.registers[PC] == 0x3FFF:
                            break
                        if simulator.registers[PC] == 0xAE8D:
                            called.append(simulator.registers[A])
                            sp = simulator.registers[SP]
                            simulator.run(stop=memory[sp]+256*memory[sp+1])
                        else:
                            simulator.run()
                    else:
                        raise ValueError("Обёртка выбора текста не завершилась")
                    actual = (simulator.registers[H]*256+simulator.registers[L],
                              *memory[0x6320:0x6322], simulator.registers[A], simulator.registers[F],
                              simulator.registers[B]*256+simulator.registers[C], simulator.registers[D], simulator.registers[E], called)
                    if actual != (0x8000+selected+count, x, y, a, f, bc, d, e, attempts):
                        raise ValueError("Не совпала обёртка выбора и вывода текста")
                    if simulator.registers[SP] != 0x8000 or memory[0xA397] != 10:
                        raise ValueError("Обёртка нарушила стек либо восстановление ограничителя")
                    wrappers += 1
    # Реальный поиск подписей настроек при заданном индексе за всеми 43 подписями.
    memory[0x6000:] = source
    title_starts = [address + 1 for address in range(0xDF3C, 0xE262) if memory[address] == 13]
    assert len(title_starts) == 61 and title_starts[42:45] == [0xE0E2, 0xE0FB, 0xE0FC]
    subscriber_indices = []
    for index in range(43, len(title_starts)):
        memory[0xA397], memory[0xAEAB], memory[0xBD26], memory[0xBD4F] = 10, 192, 0, 0xC3
        bitmap = memory[0x4000:0x5B00]
        simulator.registers[:] = initial
        simulator.registers[H], simulator.registers[L] = 0, index
        simulator.run(start=0x78FC, stop=0x790B)
        registers = simulator.registers
        assert (registers[A], registers[F]) == (10, 0x4A)
        assert registers[H]*256+registers[L] == title_starts[index]+(2 if index == 43 else 1)
        assert memory[0x4000:0x5B00] == bitmap
        subscriber_indices.append(index)
    report = dict(method="original_text_separator_search_against_separator_positions", passed=True,
                  cases=cases, exhausted_search_cases=exhausted, source_sha256=hashlib.sha256(source).hexdigest(),
                  index_255_skips_256_separators=True, search_success_flag_not_propagated=True,
                  selection_and_print_wrapper_cases=wrappers,
                  prepared_settings_indices_into_subscriber_text=subscriber_indices,
                  subscriber_text_drawn_by_prepared_indices=False,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/TextSelectionVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
