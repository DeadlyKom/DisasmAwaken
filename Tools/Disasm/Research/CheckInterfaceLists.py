"""Проверка чтения списка и полного восстановления текущих границ из сохранённых полей."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP, IXh, IXl
from InspectZ80 import decoder


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    dis = decoder([0]*0x6000+list(source))
    visited = {}
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1234, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    counts = {}

    def run(start, capture=False):
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        if capture:
            simulator.registers[PC] = start
            for _ in range(100000):
                pc = simulator.registers[PC]
                if pc == 0x3FFF:
                    break
                if 0xCB52 <= pc < 0xCBE0 and pc not in visited:
                    instruction = dis.disassemble(pc, pc+1, "h")[0]
                    raw = bytes(memory[pc:pc+len(instruction.bytes)])
                    if raw != source[pc-0x6000:pc-0x6000+len(raw)]:
                        raise ValueError("Исполнена изменённая инструкция восстановления границ")
                    visited[pc] = raw.hex()
                simulator.run()
            else:
                raise ValueError("Не завершился исследуемый интерфейсный вход")
        else:
            simulator.run(start=start, stop=0x3FFF)
        if simulator.registers[SP] != 0x8000:
            raise ValueError("Интерфейсный вход не восстановил стек")
        counts[f"{start:04X}"] = counts.get(f"{start:04X}", 0)+1

    def preserve(before, changed):
        for reg in (*range(12), *range(16, 24)):
            if reg not in changed and simulator.registers[reg] != before[reg]:
                raise ValueError("Изменён сохраняемый регистр интерфейсного входа")

    # Проверка последнего указателя для любого слова, включая слово с терминальным старшим байтом.
    memory[0x9CA6:0x9CA8] = [0, 0x81]
    memory[0x80FE:0x8100] = [0x34, 0x12]
    for pointer in range(65536):
        memory[0x8100:0x8104] = [pointer & 255, pointer >> 8, pointer & 255, 1]
        simulator.registers[:] = initial
        simulator.registers[F] = pointer & 255
        before = simulator.registers.copy()
        run(0xCB52, pointer in (0, 256, 65535))
        result = 0x1234 if pointer >> 8 == 1 else pointer
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[A], simulator.registers[F]) != (
                result, result >> 8, 0x42 | (pointer & 1)):
            raise ValueError("Не совпал последний указатель списка")
        preserve(before, {H, L, A, F})
    # Проверка всех слов искомого указателя на четырёх списках, в том числе пустом.
    pointers = [0, 255, 512, 65535]+[0x2000+257*i for i in range(42)]
    for length in (0, 1, 3, 46):
        selected = pointers[:length]
        memory[0x8100:0x8100+2*length+2] = [byte for p in selected for byte in p.to_bytes(2, "little")]+[0xA5, 1]
        for key in range(65536):
            simulator.registers[:] = initial
            simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
            simulator.registers[F] = key & 255
            before = simulator.registers.copy()
            run(0xCB64, key in (0, 255, 512, 65535))
            found = key in selected
            expected_f = 0x50 if found else int(selected[-1] < key) if selected else key & 1
            if (simulator.registers[A], simulator.registers[F]) != (0 if found else 1, expected_f):
                raise ValueError("Не совпал признак наличия указателя в списке")
            preserve(before, {A, F})
    # Проверка всех байтов сохраняемой геометрии на каждой длине до исходных 46 записей.
    for length in range(47):
        for pattern in range(256):
            table = [(i*19+pattern) & 255 for i in range(0x400)]
            expected = table.copy()
            for index in range(length):
                base = 16*index
                table[base] = 0x81 if pattern == 0x80 else pattern
                expected[base] = table[base]
                saved = [pattern, pattern ^ 0x5A, 255-pattern, (pattern*73) & 255]
                table[base+8:base+12] = saved
                expected[base+8:base+12] = saved
                expected[base:base+4] = saved
            table[16*length] = expected[16*length] = 0x80
            memory[0xF0FD:0xF4FD] = table
            simulator.registers[:] = initial
            before = simulator.registers.copy()
            run(0xCB7F, pattern == 0 and length in (0, 1, 46))
            if memory[0xF0FD:0xF4FD] != expected or (
                    simulator.registers[IXh]*256+simulator.registers[IXl], simulator.registers[D]*256+simulator.registers[E],
                    simulator.registers[A], simulator.registers[F]) != (0xF0FD+16*length, 16, 128, 0x42):
                raise ValueError("Не совпало восстановление всей таблицы границ")
            preserve(before, {IXh, IXl, D, E, A, F})
    # Проверка полного CBA9, включая ранее неразмеченный хвост после MoveItemToTail.
    for key in (0, 45):
        for length in (0, 1, 3, 46):
            positions = (-1,) if length == 0 else tuple(sorted({-1, 0, length-1}))
            for found in positions:
                for pattern in range(256):
                    pointers = [0x5000+8*i for i in range(length)]
                    for i, pointer in enumerate(pointers):
                        value = key if i == found else i+128
                        memory[pointer:pointer+3] = [0xC9, value & 255, value >> 8]
                    memory[0x6000:0x6003] = [0x21, key, 0]
                    buffer = [(i*73+pattern) & 255 for i in range(0x1000)]
                    buffer[:2*length+2] = [byte for p in pointers for byte in p.to_bytes(2, "little")]+[0xA5, 1]
                    expected_buffer = buffer.copy()
                    selected = 0x6000 if found < 0 else pointers[found]
                    if found >= 0:
                        begin = 2*found
                        expected_buffer[begin:begin+128] = buffer[begin+2:begin+130]
                    offset = 2*length if found < 0 else 2*(length-1)
                    expected_buffer[offset:offset+4] = list(selected.to_bytes(2, "little"))+[1, 1]
                    memory[0x8000:0x9000] = buffer
                    memory[0x9CA6:0x9CA8] = [0, 0x80]
                    base = 0xF0FD+16*key
                    record = [(pattern+17*i) & 255 for i in range(16)]
                    expected_record = record.copy()
                    expected_record[:4] = record[8:12]
                    memory[base:base+16] = record
                    memory[0x9A82] = 0x7F
                    simulator.registers[:] = initial
                    simulator.registers[H], simulator.registers[L] = 0x60, 0
                    simulator.registers[F] = pattern
                    before = simulator.registers.copy()
                    run(0xCBA9, pattern == 0 and length == 0 and key == 0)
                    if memory[0x8000:0x9000] != expected_buffer or memory[base:base+16] != expected_record or memory[0x9A82] != 0:
                        raise ValueError("Полное восстановление изменило не ту запись либо порядок списка")
                    if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[D]*256+simulator.registers[E],
                            simulator.registers[A], simulator.registers[F]) != (selected, key, record[11], 0xA4):
                        raise ValueError("Не совпали регистры полного восстановления записи")
                    preserve(before, {H, L, D, E, A, F})
    report = dict(method="original_draw_list_readers_and_saved_bounds_restore", passed=True,
                  cases=sum(counts.values()), by_entry=counts, source_sha256=hashlib.sha256(source).hexdigest(),
                  whole_table_and_list_tail_compared=True, irq_enabled=False, native_execution_verified=False,
                  assembly_executed=False, original_visited={f"{p:04X}": value for p, value in sorted(visited.items())})
    (ROOT / "Tools/Disasm/Reports/InterfaceListsVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
