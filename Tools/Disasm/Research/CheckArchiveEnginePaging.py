"""Переключение страниц ENGINE с исполнением исходной ROM TR-DOS."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckArchiveEngineStartup import RETURN, STACK, enter_call, init_prefix
from CheckAwakenBasicRun import model_rom_context
from CheckControlsLegacySectorRead import run_with_rom
from CheckStartArchiveMenu import PagingPorts
from TraceFlight import A, F, IFF, PC, ROOT, SP
from skoolkit.simutils import B, C, D, E, H, I, IM, L


def expected_select(mode, code, flags):
    common = 0x18 | (code & 7)
    if mode == 2:
        inverted = code ^ 255
        value = inverted | 0xC0
        result_flags = (flags & 0xC5) | (inverted & 0x28) | 0x12
        return [(0x7FFD, common), (0xFFF7, value)], value, result_flags
    if mode == 1:
        writes, value = [(0x1FFD, (code & 8) << 1), (0x7FFD, common)], common
    else:
        value = common | ((code & 8) << 3)
        writes = [(0x7FFD, value)]
    result_flags = (value & 0x28) | (4 if value.bit_count() % 2 == 0 else 0)
    return writes, value, result_flags


def check_mode(mode, rom):
    basic, dos, _ = rom
    cpu = init_prefix(mode)
    memory, registers = cpu.memory, cpu.registers
    ports = PagingPorts(memory)
    cpu.set_tracer(ports)
    registers[IFF], registers[I], registers[IM] = 1, 0x5E, 2

    def set_rom(image):
        memory.memory[0] = image

    def select(address, argument, flags):
        enter_call(cpu, address)
        registers[A], registers[F] = argument, flags
        for index in (*range(2, 12), *range(16, 24)):
            registers[index] = (index * 73 + argument * 17 + flags * 5) & 255
        ports.writes.clear()
        set_rom(basic)
        visited, _ = run_with_rom(cpu, basic, dos, set_rom, RETURN)
        assert registers[PC] == RETURN and registers[SP] == STACK
        assert registers[IFF] and registers[I] == 0x5E and registers[IM] == 2
        assert (visited[0x3D2F], visited[0x2A53]) == ((1, 1) if mode == 2 else (0, 0))

    inputs = (0, 1, 0xC4, 0xFF)
    for code in range(256):
        for flags in inputs:
            select(0x4FB1, code, flags)
            writes, value, result_flags = expected_select(mode, code, flags)
            assert (registers[A], registers[F], ports.writes) == (value, result_flags, writes), (
                mode, code, flags, registers[A], registers[F], ports.writes)
            assert memory[0x5012] == code
            for index in (*range(2, 12), *range(16, 24)):
                assert registers[index] == (index * 73 + code * 17 + flags * 5) & 255

    for index in range(4):
        for flags in inputs:
            select(0x5006, index, flags)
            writes, value, result_flags = expected_select(mode, index + 8, flags & ~1)
            assert memory[0x5012] == index + 8
            assert (registers[A], registers[F], ports.writes) == (value, result_flags, writes)
            assert tuple(registers[r] for r in (H, L, D, E)) == (0x50, 0x14 + index, 0x50, 0x14)
            for reg in (B, C, *range(8, 12), *range(16, 24)):
                assert registers[reg] == (reg * 73 + index * 17 + flags * 5) & 255

    return dict(mode=mode, selector_cases=256 * len(inputs), sprite_index_cases=4 * len(inputs),
                atm_rom_path=mode == 2, checked_flags=list(inputs))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    rom = model_rom_context(parser.parse_args().dos_rom)
    profiles = [check_mode(mode, rom) for mode in range(3)]
    result = dict(passed=True, profiles=profiles, dos_rom_sha256=sha256(rom[1]).hexdigest(),
                  scorpion_and_atm_physical_paging_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveEnginePagingVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
