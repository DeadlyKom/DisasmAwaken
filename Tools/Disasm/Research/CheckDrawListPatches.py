"""Проверка включения и отключения обработчиков по списку с ограничителем старшего байта 1."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, H, L, SP
from CheckGlyphRenderer import ObservedMemory


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = ObservedMemory()
    memory[0x6000:] = source
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x80FF, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases, counts = 0, {}

    def execute(start, length, sentinel_low, flags, base=0x80FF):
        nonlocal cases
        memory.recording = False
        targets = [0x5000+3*i for i in range(length)]
        data = [byte for pointer in targets for byte in pointer.to_bytes(2, "little")]+[sentinel_low, 1]
        memory[base:base+len(data)] = data
        for target in targets:
            memory[target] = 0x55
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[H], simulator.registers[L] = base >> 8, base & 255
        simulator.registers[A], simulator.registers[F] = sentinel_low ^ flags, flags
        memory.written.clear()
        memory.recording = True
        simulator.run(start=start, stop=0x3FFF)
        memory.recording = False
        expected_d = targets[-1] >> 8 if length else 0x24
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[D], simulator.registers[E],
                simulator.registers[A], simulator.registers[F], simulator.registers[SP]) != (
                base+2*length+1, expected_d, sentinel_low, 0, 0x42 | (flags & 1), 0x8000):
            raise ValueError("Не совпал договор изменения списка обработчиков")
        opcode = 0xC9 if start == 0x9C59 else 0x21
        if memory.written != set(targets) or any(memory[target] != opcode for target in targets):
            raise ValueError("Изменён не тот набор первых байтов обработчиков")
        if memory[base:base+len(data)] != data:
            raise ValueError("Изменён исходный список указателей")
        for reg in (*range(2, 4), *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Изменён сохраняемый регистр обработчика списка")
        cases += 1
        counts[f"{start:04X}"] = counts.get(f"{start:04X}", 0)+1

    for start in (0x9C59, 0x9C68):
        # Проверка любого младшего байта ограничителя и всех входных флагов на пустом списке.
        for low in range(256):
            for flags in range(256):
                execute(start, 0, low, flags)
        # Проверка всех длин до 128 и списков за прежней предполагаемой границей.
        for length in (*range(1, 129), 256, 512):
            for low in (0, 1, 255):
                for flags in (0, 1, 0xFE, 0xFF):
                    execute(start, length, low, flags, 0x81FE if length & 1 else 0x80FF)
    report = dict(method="original_draw_list_opcode_patch_against_pointer_list", passed=True,
                  cases=cases, by_entry=counts, source_sha256=hashlib.sha256(source).hexdigest(),
                  sentinel_high_byte_only=True, list_length_not_limited_to_128=True,
                  exact_write_set_checked=True, irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/DrawListPatchVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
