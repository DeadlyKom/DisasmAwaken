"""Проверка удаления по индексу с исходным физическим LDIR 128 байтов."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1")]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, PC, SP


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    dis = decoder(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    memory[0x9CA6:0x9CA8] = [0, 0xE0]
    observed = {}
    counts = {}
    beyond = 0

    def execute(start, length, key, flags, low=0xA5, duplicate=False, trace=False):
        nonlocal beyond
        pointers = [0x5000+8*i for i in range(length)]
        keys = [((i*149) ^ 0xA15C) & 65535 for i in range(length)]
        if duplicate and length > 1:
            keys[1] = keys[0]
        for pointer, item_key in zip(pointers, keys):
            memory[pointer:pointer+6] = [0xC9 if flags & 1 else 0x21, item_key & 255, item_key >> 8, 0xC3, 0x58, 0x9A]
        original = [(i*73+19) & 255 for i in range(1024)]
        data = [b for pointer in pointers for b in pointer.to_bytes(2, "little")]+[low, 1]
        original[:len(data)] = data
        expected = original.copy()
        found = keys.index(key) if key in keys else -1
        if found >= 0:
            offset = 2*found
            expected[offset:offset+128] = original[offset+2:offset+130]
            if length-found-1 >= 64:
                beyond += 1
            expected_a, expected_f = (0, 0x44) if start == 0xC873 else (1, 0)
        else:
            carry = int(keys[-1] < key) if length else flags & 1
            expected_a, expected_f = 0, 0x42|carry
        memory[0xE000:0xE400] = original
        memory[0x9A82] = 0x5A
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
        simulator.registers[A], simulator.registers[F] = low, flags
        if trace:
            simulator.registers[PC] = start
            while simulator.registers[PC] != 0x3FFF:
                pc = simulator.registers[PC]
                if 0xC873 <= pc < 0xC87C or 0xCB1C <= pc < 0xCB52:
                    instruction = dis.disassemble(pc, pc+1, "h")[0]
                    raw = bytes(memory[pc:pc+len(instruction.bytes)])
                    if raw != source[pc-0x6000:pc-0x6000+len(raw)]:
                        raise ValueError("Изменены исходные инструкции удаления")
                    observed[f"{pc:04X}"] = raw.hex()
                simulator.run()
        else:
            simulator.run(start=start, stop=0x3FFF)
        if memory[0xE000:0xE400] != expected:
            raise ValueError("Удаление отличается от физического сдвига 128 байтов")
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP], memory[0x9A82]) != (
                expected_a, expected_f, 0x8000, 0 if start == 0xC873 and found >= 0 else 0x5A):
            raise ValueError("Не совпал статус удаления либо запрос перестроения")
        for reg in (*range(2, 12), *range(16, 24)):
            expected_reg = key >> 8 if reg == D else key & 255 if reg == E else initial[reg]
            if simulator.registers[reg] != expected_reg:
                raise ValueError("Удаление изменило сохраняемый регистр")
        counts[f"{start:04X}"] = counts.get(f"{start:04X}", 0)+1

    for start in (0xCB1C, 0xC873):
        for length in (0, 3):
            for key in (0xA15C, 0xFFF0):
                execute(start, length, key, 1, trace=True)
        # Проверка всех слов искомого индекса, в том числе сравнения старшего и младшего байтов.
        for key in range(65536):
            execute(start, 2, key, key & 255)
        # Проверка ограничителя и исходных флагов на коротких и превышающих длину LDIR списках.
        for length in (0, 1, 3, 63, 64, 65, 128, 256):
            for position in {-1, 0, length//2, length-1}:
                if position >= length:
                    continue
                key = ((position*149)^0xA15C)&65535 if position >= 0 else 0xFFF0
                for flags in range(256):
                    execute(start, length, key, flags, flags)
        for flags in range(256):
            execute(start, 3, 0xA15C, flags, duplicate=True)
    if sum(len(bytes.fromhex(v)) for v in observed.values()) != 63:
        raise ValueError("Не покрыты все исходные байты удаления и обёртки")
    report = dict(passed=True, method="original_remove_first_index_against_exact_128_byte_shift",
                  by_entry=counts, cases=sum(counts.values()), beyond_copy_cases=beyond,
                  source_sha256=hashlib.sha256(source).hexdigest(), original_visited=observed,
                  first_duplicate_only=True, full_tail_compared=True, irq_enabled=False,
                  native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/RemoveDrawVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
