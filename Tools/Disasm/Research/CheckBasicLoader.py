"""Проверка первого загрузчика до входа TR-DOS, сам ROM и чтение диска не исполняются.

Документация: ../../../Docs/Loader.md#граница-загрузчика-перед-tr-dos
"""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, B, C, PC, SP, IYh, IYl, IFF, IM, I
from CheckMusicGateTicks import Memory
from collections import Counter


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 3)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert hashlib.sha256(disk).hexdigest() == manifest['sha256']
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    memory = Memory([0] * 65536)
    memory[0x5D3B:0x5DB2] = source[:119]
    assert int(source[107:112]) == int.from_bytes(source[115:117], "little") == 0x5D41
    simulator = Simulator(memory)
    cases = 0
    for flags in range(256):
        for accumulator in (0, 1, 127, 255):
            for location in (0, 1, 0x010F, 0x9F0F, 0xFFFF):
                # Проверка точного состояния интерфейса для всех входных флагов и нескольких слов положения.
                memory[0x5CF4:0x5CF6] = [location & 255, location >> 8]
                expected_memory = list(memory)
                expected_memory[0x5FFD:0x5FFF] = [0,0x65]
                initial_R = flags ^ accumulator
                simulator.registers[:] = get_registers(
                    {"PC": 0x5D41, "SP": 0xBFFE, "A": accumulator, "F": flags,
                     "IX": 0x1357, "IY": 0x2468, "I": 0x3F, "R":initial_R,
                     "^HL": 0x369C, "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF},
                    {"iff": 1, "im": 2}, False)
                alternate = simulator.registers[16:24].copy()
                memory.writes = []
                memory.recording = True
                for _ in range(16):
                    if simulator.registers[PC] == 0x3D13:
                        break
                    simulator.run()
                else:
                    raise ValueError("Загрузчик не передал управление TR-DOS")
                memory.recording = False
                # Проверка 12 M1, всей RAM и ровно двух записей подготовленного возврата.
                assert simulator.registers[15] == (initial_R & 128) | ((initial_R + 12) & 127)
                assert memory == expected_memory
                assert Counter(memory.writes) == Counter(((0x5FFD,0),(0x5FFE,0x65)))
                if (simulator.registers[H] * 256 + simulator.registers[L] != 0x6400
                        or simulator.registers[D] * 256 + simulator.registers[E] != location
                        or simulator.registers[B] * 256 + simulator.registers[C] != 0x2C05
                        or simulator.registers[IYh] * 256 + simulator.registers[IYl] != 0x5C3A
                        or simulator.registers[A] != accumulator or simulator.registers[F] != 0x22 + (flags & 1)
                        or simulator.registers[SP] != 0x5FFD or memory[0x5FFD:0x5FFF] != [0, 0x65]
                        or simulator.registers[IFF] != 0 or simulator.registers[IM] != 2
                        or simulator.registers[I] != 0x3F
                        or simulator.registers[8:10] != [0x13, 0x57]
                        or simulator.registers[16:24] != alternate):
                    raise ValueError("Не совпал контракт первого входа TR-DOS")
                cases += 1
    report = {"method": "original_loader_bytes_until_trdos_entry", "cases": cases,
              "all_input_flags_checked": True, "trdos_rom_executed": False,
              "disk_read_performed": False, "source_sha256": hashlib.sha256(source).hexdigest(),
              "passed": True, "assembly_executed": False,
              "exact_R_M1":12,"full_RAM_and_write_counts_compared":True,
              "physical_sectors_compared_with_original_TRD":True,
              "only_CPU_writes":[[0x5FFD,0],[0x5FFE,0x65]],
              "external_call_stack_abandoned":True,"native_execution":False}
    (ROOT / "Tools/Disasm/Reports/BasicLoaderVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
