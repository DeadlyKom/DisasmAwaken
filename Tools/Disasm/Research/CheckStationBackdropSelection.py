"""Шестнадцать фонов станции, все байты R и исходная секторная адресация."""
from collections import Counter
import json

from CheckActionOverlappingKeyClipReturns import run_to
from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator
from CheckRowHighlight import make_context
from CheckScreenUpdate import put
from PackedResourceCodec import decode


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(row for row in manifest['entries'] if row['slot'] == 9)
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    screens = [row for row in json.loads((reports / 'Screens.json').read_bytes()) if row['slot'] == 9]
    assert len(screens) == 16
    station, _, banks = make_context()
    size_table = station[0x379:0x389]
    assert list(size_table) == [row['allocated_size'] // 256 for row in screens]
    assert sum(size_table) == entry['sector_count'] == 239
    counts = Counter()
    hashes = {}

    for refresh in range(256):
        memory = RecordedBanks(banks=[bytearray(bank) for bank in banks], out7ffd=0x13)
        put(memory, 0x4000, station[0x319:0x5CE])
        put(memory, 0x5CDD, disk[entry['slot'] * 16:(entry['slot'] + 1) * 16])
        simulator = Simulator(memory, {'PC': 0x413C, 'SP': 0x5FFE, 'R': refresh})
        run_to(simulator, 0x3D13, 1000)
        r = simulator.registers
        index = (refresh + 2) & 15
        screen = screens[index]
        start = entry['offset'] + screen['offset']
        track, sector = divmod(start // 256, 16)
        assert r[2:8] == [size_table[index], 5, track, sector, 0xC0, 0]
        assert r[SP] == 0x5FFC
        assert bytes(memory[r[SP]:r[SP] + 2]) == bytes.fromhex('7b 41')

        # Подмена только дискового чтения, дальнейший распаковщик выполняется оригинальными командами.
        sector_bytes = disk[start:start + screen['allocated_size']]
        put(memory, 0xC000, sector_bytes)
        r[PC], r[SP] = 0x417B, r[SP] + 2
        run_to(simulator, 0x4184, 600000)
        expected = decode(sector_bytes[:screen['packed_size']])['data']
        assert bytes(memory[0xC000:0xDB00]) == expected and r[SP] == 0x5FFE
        counts[index] += 1
        hashes[index] = dict(start_sector=sector, start_track=track, sectors=size_table[index])

    assert set(counts.values()) == {16} and len(counts) == 16
    result = dict(passed=True, total_cases=counts.total(), all_refresh_register_bytes=True,
                  screen_locations=hashes, total_allocated_sectors=sum(size_table),
                  original_code_and_decoder_executed=True, disk_read_substituted=True,
                  native_execution=False, assembly_executed=False)
    (reports / 'StationBackdropSelectionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'screen_locations'}, indent=2))


if __name__ == '__main__':
    main()
