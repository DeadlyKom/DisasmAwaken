"""Записи загрузчика ACTION в адреса операндов старой копии CONTROL."""
import json

from CheckScreenUpdate import put
from TraceFlight import Memory, ROOT, Simulator, main as trace_flight


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    intro = json.loads((reports / 'IntroStationTransitionVerification.json').read_bytes())
    assert intro['passed']
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    entries = {entry['slot']: entry for entry in manifest['entries']}

    def read(slot, start, length):
        offset = entries[slot]['offset'] + start
        return disk[offset:offset + length]

    intro_copy = read(3, 0x2B7, 0x100)
    control0 = read(22, 0, entries[22]['length'])
    legacy = read(23, 0x7F, 188)
    assert legacy[:5] == bytes.fromhex('11 00 00 06 00')
    assert control0[:2] != b'HR' and control0[0x600:0x602] != b'HR'
    expected = (entries[22]['first_sector'] + 1, entries[22]['first_track'], entries[22]['sector_count'])
    assert expected == (5, 75, 27)
    profiles = []
    for name, initial_copy in (('empty_low_ram', bytes(256)), ('original_intro_copy', intro_copy)):
        memory = Memory(out7ffd=0x10)
        put(memory, 0x5D3B, initial_copy)
        put(memory, 0x6000, read(17, 0, entries[17]['length']))
        simulator = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A})
        observations = []

        def observe(frame, ram, registers):
            assert frame == 1
            # Результат реальных записей в общей RAM сравнивается отдельно от загруженных байтов банка 1.
            actual = bytes(ram[address] for address in range(0x5E1F, 0x5E24))
            assert actual[1:3] + actual[4:] == bytes(expected)
            assert actual[0] == initial_copy[0xE4] and actual[3] == initial_copy[0xE7]
            assert actual[0] != legacy[0]
            assert bytes(ram.banks[1][0x1B5D:0x1B5D + len(legacy)]) == legacy
            observations.append(actual.hex())

        result = trace_flight(['--verify-flight-cycle', '--frames', '2'], observe, boot_simulator=simulator)
        assert len(observations) == 1 and result['legacy_runtime_execution_visits'] == 0
        profiles.append(dict(name=name, after_5E1F_5E23=observations[0],
                             file_location=result['legacy_control0_parameters']))
    report = dict(passed=True, total_cases=len(profiles), profiles=profiles,
                  active_InitializeFlight_written_bytes=list(expected), writer_addresses=[0x4267, 0x426A],
                  source_disk_slot=22, legacy_bytes_remain_in_bank1_at=0xDB5D,
                  actual_CONTROL0_C000_prefix=control0[:6].hex(), actual_CONTROL0_C600_prefix=control0[0x600:0x606].hex(),
                  actual_CONTROL0_matches_HR_signature=False, native_execution=False, assembly_executed=False,
                  whole_station_session_before_boot_executed=False, trdos_io_substituted=True,
                  all_possible_legacy_callers_excluded=False)
    (reports / 'ActionLegacyBootOperandsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
