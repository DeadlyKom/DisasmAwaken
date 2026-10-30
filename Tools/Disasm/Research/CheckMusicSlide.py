"""Проверка установщика скольжения тона C на исходных байтах, без сборки."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, PC, SP, IFF


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/10_MUZ1.C.bin").read_bytes()
    memory = [0] * 65536
    memory[0xDB00:0xDB00 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    cases = 0
    for delay in range(256):
        for step in (0, 1, 0x7FFF, 0x8000, 0xA55A, 0xFFFF):
            # Проверка всех байтов задержки с граничными знаковыми и обычными шагами.
            memory[0x7000:0x7003] = [delay, step & 255, step >> 8]
            simulator.registers[:] = get_registers(
                {"HL": 0xABCD, "DE": 0x7000, "BC": 0x1357,
                 "IX": 0x2468, "IY": 0x5C3A, "SP": 0xBFFE, "PC": 0xE6AE}, None, False)
            simulator.registers[16:24] = [19, 37, 61, 83, 107, 131, 157, 181]
            preserved = [simulator.registers[i] for i in (2, 3, 8, 9, 10, 11, *range(16, 24), IFF)]
            for _ in range(32):
                if simulator.registers[PC] == 0x3FFF:
                    break
                simulator.run()
            else:
                raise ValueError("Установщик скольжения не вернулся")
            actual = [memory[p] for p in (0xE29D, 0xE2CC, 0xE2A6, 0xE2A7, 0xE2AD, 0xE2D5)]
            expected = [delay, delay, step & 255, step >> 8, 0x1D, 0]
            if actual != expected:
                raise ValueError("Изменяемые операнды не соответствуют трём байтам команды")
            if (simulator.registers[H] * 256 + simulator.registers[L] != step
                    or simulator.registers[D] * 256 + simulator.registers[E] != 0x7003
                    or simulator.registers[A] != 0 or simulator.registers[F] != 0x44
                    or simulator.registers[SP] != 0xC000):
                raise ValueError("Не совпал регистровый контракт SetToneSlideC")
            if preserved != [simulator.registers[i] for i in (2, 3, 8, 9, 10, 11, *range(16, 24), IFF)]:
                raise ValueError("Изменились сохраняемые регистры")
            cases += 1
    report = {"method": "original_z80_bytes_without_assembly", "entry": 0xE6AE,
              "cases": cases, "all_delay_bytes_checked": True,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "whole_slide_playback_proved": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/MusicSlideVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
