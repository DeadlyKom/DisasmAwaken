"""Условная старая цепочка 5E1F на секторах PANEL и CONTROL0."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsLegacySectorRead import SectorPorts, run_with_rom
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckScreenUpdate import put
from PackedResourceCodec import decode
from TraceFlight import A, B, C, D, E, H, IFF, L, PC, SP, Simulator


class LegacyPorts(SectorPorts):
    def __init__(self, disk, retry, memory):
        super().__init__(disk, retry)
        self.memory = memory
        self.paging = []
        self.ay = []

    def write_port(self, registers, port, value, offset):
        if port == 0x7FFD:
            self.memory.out7ffd(value)
            self.paging.append(value)
        elif port in (0xFFFD, 0xBFFD):
            self.ay.append((port, value))
        else:
            super().write_port(registers, port, value, offset)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    parser.add_argument('--basic-rom', type=Path,
                        default=ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom')
    args = parser.parse_args()
    basic, dos = args.basic_rom.read_bytes(), args.dos_rom.read_bytes()
    assert len(basic) == len(dos) == 16384
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    panel = next(row for row in manifest['entries'] if row['slot'] == 25)
    control0 = next(row for row in manifest['entries'] if row['slot'] == 22)
    control = next(row for row in manifest['entries'] if row['slot'] == 23)
    data = disk[panel['offset']:panel['offset'] + panel['length']]
    raw = disk[control['offset'] + 0x7F:control['offset'] + 0x13B]
    pixels = decode(data)['data']
    assert len(pixels) == 0x1B00
    flat = flat_action()
    banks = [bytearray([160 + page] * 16384) for page in range(8)]
    for page, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[page][:] = flat[address:address + 16384]
    banks[1][:] = base_memory()[0xC000:]
    profiles = []
    original_source_profiles = []

    for entry, equipment in ((panel, 0xFE), (panel, 0xFF), (control0, 0xFF)):
        for retry in (False, True):
            memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=0x16)
            memory.roms = (basic, basic)
            memory.out7ffd(0x16)
            put(memory, 0x5E1F, raw)
            # Подстановка каталожных координат и рамки условного входа.
            assert bytes(memory[0x5E20:0x5E24]) == bytes.fromhex('00 00 06 00')
            put(memory, 0x5E20, (entry['first_sector'] + 1, entry['first_track']))
            memory[0x5E23] = entry['sector_count']
            put(memory, 0x5E33, (0xF8, 0xBF))
            put(memory, 0xBFF0, (0xFD, 0x7F))
            put(memory, 0xBFF8, (0x34, 0x12, 0xFF, 0x3F))
            memory[0x5CC2], memory[0x5D16], memory[0x9C30] = 0xC9, 0xC7, equipment
            simulator = Simulator(memory, {'PC': 0x5E1F, 'SP': 0xBFF0, 'IX': 0x5678})
            ports = LegacyPorts(disk, retry, memory)
            simulator.set_tracer(ports)

            def set_rom(image):
                memory.memory[0] = image
            stop = 0x3FFF if entry is panel else 0xAB23
            _, keyboard_checks = run_with_rom(simulator, basic, dos, set_rom, stop)
            assert len(ports.attempts) == keyboard_checks == entry['sector_count'] + int(retry)
            if entry is control0:
                # Проверка первого переноса при чтении несжатого файла как HR.
                sectors = disk[entry['offset']:entry['offset'] + entry['allocated_length']]
                assert bytes(memory.banks[6][:len(sectors)]) == sectors
                assert sectors[:6] == bytes.fromhex('FF EF E9 E4 DF DC')
                r = simulator.registers
                assert r[H:L + 1] == r[D:E + 1] == [0xC0, 0]
                run_with_rom(simulator, basic, dos, set_rom, 0xAB3C)
                assert r[H:L + 1] == [0x9C, 0xDD] and r[D:E + 1] == [0xA4, 0xE8], r[:8]
                assert r[B:C + 1] == [0xDC, 0xDE] and bytes(memory[0xAB3C:0xAB3E]) == b'\xED\xB8'
                source_byte = memory[0x9CDD]
                memory.writes = []
                memory.recording = True
                simulator.run()
                memory.recording = False
                assert memory.writes == [(2, 0xA4E8 - 0x8000, source_byte)]
                assert r[PC] == 0xAB3C and not ports.paging and not ports.ay
                original_source_profiles.append(dict(retry_first=retry, sectors_read=len(sectors) // 256,
                    disk_attempts=len(ports.attempts), raw_prefix=sectors[:6].hex(),
                    first_copy_source=0x9CDD, first_copy_destination=0xA4E8, first_copy_value=source_byte,
                    first_copy_bank=2, initial_copy_count=0xDCDE))
                continue
            assert bytes(memory.banks[6][:len(pixels)]) == pixels
            assert ports.paging == [0x11, 0x10] and memory.o7ffd == 0x10
            assert ports.ay == [(0xFFFD, 7), (0xBFFD, 0xDB)]
            r = simulator.registers
            assert r[A] == 0xDB and r[B:C + 1] == [0xBF, 0xFD]
            assert r[8:10] == [0x12, 0x34] and r[SP] == 0xBFFC and not r[IFF]
            template = 0xDF91 if equipment == 0xFF else 0xDFD9
            assert bytes(memory[0x9B27:0x9B6F]) == bytes(banks[1][template - 0xC000:template - 0xC000 + 72])
            assert bytes(memory[0x9BC1:0x9BC6]) == bytes(memory[0x9BC6:0x9BCB])
            profiles.append(dict(equipment=equipment, retry_first=retry, sectors=len(ports.attempts),
                                 patch_opcode=memory[0x7B60], output_bytes=len(pixels)))

    report = dict(passed=True, total_cases=len(profiles), profiles=profiles,
                  original_control0_profiles=original_source_profiles,
                  control0_stops_after_first_out_of_window_copy=True,
                  dos_rom=args.dos_rom.name, dos_rom_sha256=sha256(dos).hexdigest(),
                  basic_rom=args.basic_rom.name, basic_rom_sha256=sha256(basic).hexdigest(),
                  original_sector_read_unpack_and_reset_executed=True,
                  original_AY_restore_and_external_return_executed=True,
                  panel_CHS_and_sector_count_are_explicit_legacy_input_fixtures=True,
                  actual_game_legacy_source_resource_and_entry_proved=False,
                  modelled_FDC_and_ROM_paging=True, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsLegacyLoadChainVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
