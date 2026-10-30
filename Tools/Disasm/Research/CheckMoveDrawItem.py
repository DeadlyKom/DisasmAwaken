"""Проверка вставки и перемещения записи рисования, включая фиксированный LDIR 128 байтов."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, H, L, SP
from CheckGlyphRenderer import ObservedMemory


def decrement_flags(before):
    result = (before-1) & 255
    return (result & 0xA8) | (0x40 if result == 0 else 0) | (0x10 if before & 15 == 0 else 0) | (4 if before == 128 else 0) | 2


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = ObservedMemory()
    memory[0x6000:] = source
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x6000, "DE": 0, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases, beyond_copy, normal_move, appended = 0, 0, 0, 0

    def execute(length, found, low, flags):
        nonlocal cases, beyond_copy, normal_move, appended
        memory.recording = False
        pointers = [0x5000+8*i for i in range(length)]
        keys = [((i*149) ^ 0xA15C) & 65535 for i in range(length)]
        key = keys[found] if found >= 0 else 0xFFF0
        if found < 0 and key in keys:
            raise ValueError("Тестовый новый ключ уже присутствует")
        initial_buffer = [(i*73+19) & 255 for i in range(0x1000)]
        data = [byte for pointer in pointers for byte in pointer.to_bytes(2, "little")]+[low, 1]
        initial_buffer[:len(data)] = data
        expected = initial_buffer.copy()
        for i, pointer in enumerate(pointers):
            memory[pointer:pointer+6] = [0xC9 if flags & 1 else 0x21, keys[i] & 255, keys[i] >> 8, 0xC3, 0x58, 0x9A]
        memory[0x6000:0x6006] = [0x21, key & 255, key >> 8, 0xC3, 0x58, 0x9A]
        memory[0x8000:0x9000] = initial_buffer
        # Это изменяемое слово LD HL в RebuildInterface, а не новый указатель в раскладке игры.
        memory[0x9CA6:0x9CA8] = [0, 0x80]
        if found < 0:
            selected, expected_a, expected_f = 0x6000, 1, 0
            offset = 2*length
            appended += 1
        else:
            selected = pointers[found]
            offset = 2*found
            expected[offset:offset+128] = expected[offset+2:offset+130]
            cursor, count = offset, 0
            while expected[cursor+1] != 1:
                cursor += 2
                count += 1
                if cursor >= len(expected)-4:
                    raise ValueError("Не найден ограничитель после физического сдвига")
            count += 1
            expected_a = (count-1) & 255
            expected_f = decrement_flags(count & 255)
            offset = cursor
            if length-found-1 >= 64:
                beyond_copy += 1
            else:
                normal_move += 1
        expected[offset:offset+4] = list(selected.to_bytes(2, "little"))+[1, 1]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
        simulator.registers[A], simulator.registers[F] = low, flags
        memory.written.clear()
        memory.recording = True
        simulator.run(start=0xBE38, stop=0x3FFF)
        memory.recording = False
        if memory[0x8000:0x9000] != expected:
            raise ValueError(f"Не совпало физическое изменение списка length={length}, found={found}")
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[A], simulator.registers[F],
                simulator.registers[D]*256+simulator.registers[E], simulator.registers[SP]) != (
                selected, expected_a, expected_f, key, 0x8000):
            raise ValueError("Не совпали результат, частичный счётчик либо полный AF перемещения")
        if any(not (0x8000 <= address < 0x9000 or 0x7FF0 <= address < 0x7FFE) for address in memory.written):
            raise ValueError("Изменены данные вне списка и рабочего CPU-стека")
        for reg in (*range(2, 4), *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Перемещение изменило сохраняемый регистр")
        cases += 1

    for length in range(65):
        for found in range(-1, length):
            for low in (0, 1, 0xA5):
                for flags in (0, 1, 0xFE, 0xFF):
                    execute(length, found, low, flags)
    # Проверка поведения за длиной фиксированного сдвига, алгоритм не заменён логическим удалением.
    for length in (65, 128, 256):
        for found in (-1, 0, 1, 63, length-1):
            for flags in range(256):
                execute(length, found, 0xA5, flags)
    report = dict(method="original_draw_list_insert_move_against_physical_128_byte_shift", passed=True,
                  cases=cases, appended=appended, normal_move=normal_move, beyond_copy_cases=beyond_copy,
                  source_sha256=hashlib.sha256(source).hexdigest(), disabled_wrapper_indices_read=True,
                  entire_tail_buffer_compared=True, irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/MoveDrawItemVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
