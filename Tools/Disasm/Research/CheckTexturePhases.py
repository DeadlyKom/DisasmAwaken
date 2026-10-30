"""Проверка трёх связанных состояний фазы и байтового указателя на исходном Z80."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, B, C, PC, SP, IFF


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 3)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    memory = [0] * 65536
    memory[0x6300:0x6300 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    memory[0x6400:0x6500] = [(index * 73 + 19) & 255 for index in range(256)]
    simulator = Simulator(memory)

    def word(address, value=None):
        if value is None:
            return memory[address] + 256 * memory[address + 1]
        memory[address:address + 2] = [value & 255, value >> 8]

    profiles = [(phase, step, delta) for phase in (0, 0x7FFF, 0x8000, 0xFFFF)
                for step in (0, 0x5555, 0xFFFF) for delta in (0, 1, 0x8000, 0xFFFF)]
    cases = 0
    for cursor in range(256):
        for profile in range(len(profiles)):
            states = [profiles[(profile + shift) % len(profiles)] for shift in (0, 17, 31)]
            # Проверка исходных знаков фаз, переполнений приращений и всех младших байтов курсора.
            for address, state in zip((0x6C8A, 0x6C90, 0x6C96), states):
                for offset, value in zip((0, 2, 4), state):
                    word(address + offset, value)
            word(0x6C12, 0x6400 | cursor)
            simulator.registers[:] = get_registers(
                {"PC": 0x6BF6, "SP": 0xBFFE, "IX": 0x1357, "IY": 0x5C3A,
                 "^HL": 0x2468, "^DE": 0x369C, "^BC": 0x47AD, "^AF": 0x58BE}, None, False)
            preserved = simulator.registers[8:12] + simulator.registers[16:24]
            for _ in range(200):
                if simulator.registers[PC] == 0x3FFF:
                    break
                simulator.run()
            else:
                raise ValueError("Обновление трёх фаз не завершилось")
            expected_phases = []
            for address, (phase, step, delta) in zip((0x6C8A, 0x6C90, 0x6C96), states):
                effective_delta = (-delta if phase & 0x8000 else delta) & 0xFFFF
                new_step = (step + effective_delta) & 0xFFFF
                new_phase = (phase + new_step) & 0xFFFF
                if [word(address + offset) for offset in (0, 2, 4)] != [new_phase, new_step, delta]:
                    raise ValueError("Не совпали поля FTexturePhase")
                expected_phases.append(new_phase)
            next_cursor = (cursor + 3) & 255
            sampled = memory[0x6400 + next_cursor]
            result = sampled >> 1
            flags = (result & 0x28) | (0x40 if result == 0 else 0) | (4 if result.bit_count() % 2 == 0 else 0) | (sampled & 1)
            if ([memory[p] for p in (0x6BA2, 0x6BA6, 0x6BA9)] != [value >> 8 for value in expected_phases]
                    or memory[0x6BAC] != result or word(0x6C12) != 0x6400 + next_cursor
                    or simulator.registers[H] * 256 + simulator.registers[L] != 0x6400 + next_cursor
                    or simulator.registers[D] * 256 + simulator.registers[E] != effective_delta
                    or simulator.registers[B] * 256 + simulator.registers[C] != states[-1][0]
                    or simulator.registers[A] != result or simulator.registers[F] != flags
                    or simulator.registers[SP] != 0xC000 or simulator.registers[IFF] != 1
                    or preserved != simulator.registers[8:12] + simulator.registers[16:24]):
                raise ValueError("Не совпал контракт обновления текстурных фаз")
            cases += 1
    report = {"method": "original_z80_bytes_without_assembly", "cases": cases,
              "all_cursor_low_bytes_checked": True, "state_profiles": len(profiles),
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "irq_execution_included": False, "whole_intro_effect_verified": False, "assembly_executed": False}
    (ROOT / "Tools/Disasm/Reports/TexturePhaseVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
