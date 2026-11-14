"""Исполнение машинного загрузчика AWAKEN через TR-DOS 5.04T до входа во вступление."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckControlsLegacySectorRead import SectorPorts, run_with_rom
from CheckStationFlightCycle import DISK, ENTRIES, ROOT
from CheckMusic import PC, SP, Simulator
from skoolkit.tap2sna import SYSVARS


class FileReadPorts(SectorPorts):
    def __init__(self, cylinder):
        super().__init__(DISK, retry=False)
        self.track = cylinder
        self.data_register = 0
        self.step_direction = -1

    def write_port(self, registers, port, value, offset):
        low = port & 255
        super().write_port(registers, port, value, offset)
        if low == 0x7F:
            self.data_register = value
        elif low == 0x1F:
            if value == 0xC0:
                # Команда Read Address возвращает C/H/R/N и два байта CRC.
                self.current = bytes((self.track, self.side, 1, 1, 0, 0))
                self.cursor = 0
            elif value in (0x18, 0x1B):
                self.step_direction = 1 if self.data_register > self.track else -1
                self.track = self.data_register
            elif value == 0x3C:
                self.track = max(0, self.track + self.step_direction)
            elif value == 0x08:
                self.track = 0

    def read_port(self, registers, port, offset=0):
        low = port & 255
        if low == 0x3F:
            return self.track
        if low == 0x1F and self.commands[-1:] != [0x80]:
            return 4 if self.track == 0 else 0
        return super().read_port(registers, port, offset)


def prepare_memory(basic):
    memory = bytearray(65536)
    memory[:16384] = basic
    memory[0x5C00:0x5C00 + len(SYSVARS)] = bytes(SYSVARS)
    # Модель системных переменных с областью TR-DOS перед началом BASIC.
    for address in (0x5C4B, 0x5C53, 0x5C57, 0x5C59, 0x5C61, 0x5C63, 0x5C65):
        value = int.from_bytes(memory[address:address + 2], 'little') + 0x70
        memory[address:address + 2] = value.to_bytes(2, 'little')
    memory[0x5CB2:0x5CB4] = b'\x57\xff'
    memory[0x5D3B:0x5D3E] = b'\x80\r\x80'
    memory[0x5C3A] = 0xFF
    memory[0x5CC2] = 0xC9
    memory[0x5CC8] = 2
    memory[0x5CF8] = 0xFF
    return memory


def check_profile(basic, dos, cylinder):
    entry = ENTRIES[3]
    first = entry['offset'] // 256 + 1
    track, sector = divmod(first, 16)
    count = entry['sector_count'] - 1
    program = DISK[entry['offset']:entry['offset'] + entry['length']]
    assert (len(program), count, track, sector) == (119, 44, 18, 2)

    memory = prepare_memory(basic)
    memory[0x5D3B:0x5DB2] = program
    memory[0x5CF4:0x5CF6] = bytes((sector, track))
    address = int.from_bytes(program[115:117], 'little')
    assert address == 0x5D41

    cpu = Simulator(memory, {'SP': 0xFEFE, 'PC': address, 'IY': 0x5C3A})
    ports = FileReadPorts(cylinder)
    cpu.set_tracer(ports)

    def set_rom(image):
        memory[:16384] = image

    run_with_rom(cpu, basic, dos, set_rom, 0x6500)
    expected_sectors = [(index // 16, index % 16 + 1) for index in range(first, first + count)]
    assert ports.attempts == expected_sectors
    assert memory[0x6400:0x9000] == DISK[first * 256:(first + count) * 256]
    assert memory[0x63FF] == memory[0x9000] == 0
    assert (cpu.registers[PC], cpu.registers[SP]) == (0x6500, 0x5FFF)
    assert int.from_bytes(memory[0x5CF4:0x5CF6], 'little') == 0x140E
    return dict(initial_cylinder=cylinder, sectors_read=ports.attempts,
                first_file_offset=256, bytes_in_intro_window=44 * 256,
                pc=cpu.registers[PC], sp=cpu.registers[SP])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    assert len(dos) == len(basic) == 16384
    profiles = [check_profile(basic, dos, cylinder) for cylinder in (0, 9)]
    report = dict(passed=True, dos_rom=args.dos_rom.name, dos_rom_sha256=sha256(dos).hexdigest(),
                  basic_rom_sha256=sha256(basic).hexdigest(), profiles=profiles,
                  first_catalogue_sector_read_by_usr=False, basic_interpreter_executed=False,
                  modelled_fdc_and_rom_paging=True, assembly_executed=False, native_execution=False)
    destination = ROOT / 'Tools/Disasm/Reports/BasicIntroDiskReadVerification.json'
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('44 исходных сектора вступления и возврат TR-DOS на #6500 проверены в двух профилях')


if __name__ == '__main__':
    main()
