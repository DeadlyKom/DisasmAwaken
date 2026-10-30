"""Проверка адреса поля интерфейсного элемента по оригинальным инструкциям #9EED."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, SP


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6000:0x6000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0xBFFE, "BC": 0x2468, "DE": 0x369C,
                             "IX": 0x47AD, "IY": 0x5C3A, "^HL": 0x58BE,
                             "^DE": 0x69CF, "^BC": 0x7AD0, "^AF": 0x8BE1}, None, False)
    cases = 0
    # Проверка всех восьмибитных индексов со всеми смещениями и полного HL с меняющимся смещением.
    for index in range(65536):
        fields = range(256) if index < 256 else ((index * 73 + 19) & 255,)
        for field in fields:
            simulator.registers[:] = initial
            simulator.registers[H], simulator.registers[L] = index >> 8, index & 255
            simulator.registers[A], simulator.registers[F] = field, (index ^ field) & 255
            simulator.run(start=0x9EED, stop=0x3FFF)
            expected = (0xF0FD + 16 * index + field) & 65535
            page = 0xF0 + int(field >= 3)
            flags = (page & 0xA8) | (4 if page.bit_count() % 2 == 0 else 0)
            if (simulator.registers[H] * 256 + simulator.registers[L], simulator.registers[A],
                    simulator.registers[F], simulator.registers[SP]) != (expected, page, flags, 0xC000):
                raise ValueError("Не совпал указатель поля или выходной AF")
            for reg in (*range(2, 6), *range(8, 12), *range(16, 24)):
                if simulator.registers[reg] != initial[reg]:
                    raise ValueError("Изменён сохраняемый регистр")
            cases += 1
    # Проверка отдельного последовательного входа со смещением Flags для всех 16-битных индексов.
    flags_cases = 0
    for index in range(65536):
        simulator.registers[:] = initial
        simulator.registers[H], simulator.registers[L] = index >> 8, index & 255
        simulator.registers[A], simulator.registers[F] = index & 255, index >> 8
        simulator.run(start=0x9EEB, stop=0x3FFF)
        if (simulator.registers[H]*256+simulator.registers[L], simulator.registers[A],
                simulator.registers[F], simulator.registers[SP]) != ((0xF101+16*index) & 65535, 0xF1, 0xA0, 0xC000):
            raise ValueError("Не совпал последовательный вход указателя Flags")
        for reg in (*range(2, 6), *range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Вход Flags изменил сохраняемый регистр")
        flags_cases += 1
    report = {"method": "original_z80_bytes_against_item_address_formula", "cases": cases,
              "flags_entry_cases": flags_cases,
              "passed": True, "source_sha256": hashlib.sha256(source).hexdigest(),
              "all_byte_indices_and_offsets_checked": True, "all_word_indices_sampled": True,
              "dereference_or_item_validity_checked": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/ItemFieldVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
