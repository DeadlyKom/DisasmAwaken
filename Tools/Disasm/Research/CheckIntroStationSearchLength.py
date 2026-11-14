"""Происхождение длины поиска STATIONF от RUN через BASIC и вступление.

Документация: ../../../Docs/IntroStationTransition.md#наследуемая-длина-поиска-tr-dos
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckAwakenBasicRun import BasicLoadMemory, load_basic
from CheckBootBankFileReads import IntroInput, run_with_rom, DISK, ENTRIES, ROOT
from skoolkit.simutils import PC, C, SP


class SearchLengthMemory(BasicLoadMemory):
    def __init__(self):
        self.length_writes = []
        self.phase = 'RUN'
        super().__init__()

    def __setitem__(self, address, value):
        if isinstance(address, int) and address == 0x5D06:
            registers = getattr(self, 'registers', None)
            pc = registers[PC] if registers is not None else None
            self.length_writes.append(dict(phase=self.phase if pc is not None else 'fixture', pc=pc, value=value,
                pc_bytes=bytes(self[pc:pc + 4]).hex() if pc is not None else None,
                selected_rom_sha256=sha256(bytes(self.memory[0])).hexdigest() if pc is not None else None))
        super().__setitem__(address, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    dos = args.dos_rom.read_bytes()
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    assert sha256(dos).hexdigest() == 'e21d37271d087eab5ef8f88d8f3a58c8c19da1fa857b9790eaa974b231db9e13'
    assert dos[0x0332:0x0337] == bytes.fromhex('3e0932065d')
    cpu, ports, basic_run = load_basic(basic, dos, memory_factory=SearchLengthMemory)
    memory = cpu.memory
    memory.registers = cpu.registers
    checkpoints = [dict(phase='BASIC_USR', pc=cpu.registers[PC], length=memory[0x5D06])]

    def set_rom(image):
        memory.memory[0] = image

    memory.phase = 'intro_sector_read'
    run_with_rom(cpu, basic, dos, set_rom, 0x6500)
    checkpoints.append(dict(phase='intro_entry', pc=0x6500, length=memory[0x5D06]))
    set_rom(basic)
    memory.phase = 'intro_effects'
    inputs = IntroInput(cpu, 0)
    cpu.set_tracer(inputs)
    memory[0x5C00] = memory[0x5C04] = 255
    cpu.run(0x6500, 0x5D3B, interrupts=True)
    assert inputs.polls == 1
    checkpoints.append(dict(phase='relocated_loader', pc=0x5D3B, length=memory[0x5D06]))
    memory.phase = 'station_search'
    cpu.set_tracer(ports)
    # Исполнение исходного распаковщика и копирования экрана до первой функции каталога.
    run_with_rom(cpu, basic, dos, set_rom, 0x3D13)
    assert cpu.registers[C] == 0x0A
    assert bytes(memory[0x5CDD:0x5CE6]) == b'STATIONFC'
    checkpoints.append(dict(phase='before_search', pc=0x3D13, length=memory[0x5D06]))
    catalogue_start = len(ports.attempts)
    run_with_rom(cpu, basic, dos, set_rom, 0x5D81)
    assert cpu.registers[C] == 4
    run_with_rom(cpu, basic, dos, set_rom, 0x5D87, initial_dos=True)
    assert bytes(memory[0x5CDD:0x5CED]) == DISK[4 * 16:5 * 16]
    assert ports.attempts[catalogue_start:] == [(0, 1), (0, 1)]
    checkpoints.append(dict(phase='after_catalogue', pc=0x5D87, length=memory[0x5D06]))
    memory.phase = 'station_sector_read'
    run_with_rom(cpu, basic, dos, set_rom, 0x6300, initial_dos=True)
    assert bytes(memory[0x6000:0x10000]) == DISK[ENTRIES[4]['offset']:ENTRIES[4]['offset'] + 40960]
    assert cpu.registers[SP] == 0x5FFF
    checkpoints.append(dict(phase='station_entry', pc=0x6300, length=memory[0x5D06]))
    assert all(row['length'] == 9 for row in checkpoints)
    assert [(row['phase'], row['pc'], row['value']) for row in memory.length_writes] == [
        ('fixture', None, 0), ('RUN', 0x0334, 9)]
    assert memory.length_writes[1]['selected_rom_sha256'] == sha256(dos).hexdigest()
    report = dict(passed=True, dos_rom_sha256=sha256(dos).hexdigest(),
                  basic_rom_sha256=sha256(basic).hexdigest(),
                  length_writes=memory.length_writes, checkpoints=checkpoints,
                  editor_RUN_fixture=True, station_catalogue_header_supplied=False,
                  trdos_calls_substituted=False, controller_and_ROM_paging_modelled=True,
                  intro_does_not_write_search_length=True, search_length_inherited_from_RUN=True,
                  cold_boot_proved=False,
                  final_effect_keyboard_polls=inputs.polls,
                  all_DOS_versions_proved=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroStationSearchLengthVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(length_writes=memory.length_writes, checkpoints=checkpoints), indent=2))


if __name__ == '__main__':
    main()
