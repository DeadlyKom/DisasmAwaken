"""Полная проверка двух байтовых сумм выбора, без сборки и без игрового интерфейса."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, H, L, D, E, PC, SP


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    memory = [0] * 65536
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    cases = 0
    for entry, row, base in ((0xC900, 0x7217, 0x71B9), (0xC918, 0x7068, 0x7026)):
        for selected in range(256):
            for scroll in range(256):
                # Проверка всех пар байтов, включая переполнение и выбранную строку #FF.
                memory[row], memory[base] = selected, scroll
                simulator.registers[:] = get_registers(
                    {"PC": entry, "SP": 0xBFFE, "HL": 0x1357, "DE": 0x2468,
                     "BC": 0xABCD, "IX": 0x789A, "IY": 0x5C3A}, None, False)
                before = simulator.registers[8:12] + simulator.registers[16:24]
                for _ in range(8):
                    if simulator.registers[PC] == 0x3FFF:
                        break
                    simulator.run()
                else:
                    raise ValueError("Расчёт индекса не вернулся")
                result = (selected + scroll) & 255
                expected_flags = (result & 0xA8) | (0x40 if result == 0 else 0)
                expected_flags |= 0x10 if (selected & 15) + (scroll & 15) > 15 else 0
                expected_flags |= 4 if (~(selected ^ scroll) & (selected ^ result) & 128) else 0
                expected_flags |= int(selected + scroll > 255)
                if (simulator.registers[B] != 0 or simulator.registers[C] != result
                        or simulator.registers[A] != result or simulator.registers[F] != expected_flags
                        or simulator.registers[H] * 256 + simulator.registers[L] != 0x1357
                        or simulator.registers[D] * 256 + simulator.registers[E] != 0x2468
                        or simulator.registers[SP] != 0xC000
                        or before != simulator.registers[8:12] + simulator.registers[16:24]):
                    raise ValueError("Не совпал полный контракт байтовой суммы выбора")
                cases += 1
    report = {"method": "original_z80_bytes_without_assembly", "cases": cases,
              "full_two_byte_input_domain": True, "flags_checked": True,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "ui_selection_correctness_proved": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/SelectionIndexVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
