"""Архивный хвост WMISS2 и два сохранённых RET перед наведением контракта."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckMissionPanelActions import prepare
from CheckPassivePanelHovers import check_adjacent_ret_bytes
from ClassifyStationWorkspaceResources import ROOT, publish
from ProbeShipPreviewCallbacks import Fixture, make_context, put
from skoolkit.simutils import SP


RESOURCES = (
    (0x4A82, 0x4A84, 'Source/Station/Resources/LegacyMissionReturnPair.bin',
     'STATION_LEGACY_MISSION_RETURN_PAIR', 'Два RET перед пустым наведением, раскладка архивного WMISS2'),
)


def check_archived_layout(archive_path):
    with ZipFile(archive_path) as archive:
        source = archive.read('awk6.trd')
        _, handlers, _ = read_entry(source, b'OBR     a')
        _, descriptors, _ = read_entry(source, b'OBJECT  a')
    lines = handlers.split(b'\r')
    start, draw = lines.index(b'WMISS2'), lines.index(b'WMISS2_')
    action = [line for line in lines[start + 1:draw] if line]
    assert action == [b'\x06\x8c\x053\x06\x83WMISS2C',
                      b'\x06\x8c\x054 WINOBR1:\x05$\x05x',
                      b'\x06\x8c\x050\x06\x82\x03~:\x053\x03\x94,F_S5',
                      b'\x06\x8c\x054 ERSOBJ', b'\x06\x8c\x05$\x06\x82\x05\x94',
                      b'\x06\x8c\x05$', b'F_S5', b'\x06\x8c\x05$', b'WMISS2C', b'\x06\x8c\x05$']
    assert lines[draw + 1:draw + 3] == [b'\x06\x8c\x05 \x06\x83\x03\x8c,0', b'\x06\x8c\x054 Outwin']
    rows = descriptors.split(b'\r')
    handler = rows.index(b'\x06\x8c\x05h\x06\x83WMISS2')
    assert rows[handler - 3:handler + 3] == [b'\x06\x8c\x05h\x06\x830,0',
        b'\x06\x8c\x05g\x06\x83%00000001', b'\x06\x8c\x05g\x06\x834',
        b'\x06\x8c\x05h\x06\x83WMISS2', b'\x06\x8c\x05h\x06\x83#1006,#070E',
        b'\x06\x8c\x05h\x06\x83WMISS2_,0']
    return dict(archive_sha256=sha256(archive_path.read_bytes()).hexdigest(), archive_disk='awk6.trd',
                archive_event='WMISS2', archive_hover='WMISS2C', archive_draw='WMISS2_',
                archive_two_returns_before_hover=True, archive_second_return_label='F_S5')


def check_current_paths():
    _, _, base = make_context()
    fixture = Fixture(base)
    memory = fixture.memory
    descriptor_audit = check_adjacent_ret_bytes(memory)
    row = bytes(memory[0xF2FD:0xF30D])
    assert row[4:6] == bytes((1, 4)) and row[6:8] == b'\x55\xAA' and row[12:14] == b'\x85\xAA'
    assert bytes(memory[0xAA55:0xAA60]) == bytes.fromhex('C3 84 AA CD E2 CB D8 3D CA 81 AA')
    assert bytes(memory[0xAA60:0xAA66]) == bytes.fromhex('CD 5E C8 C2 81 AA')
    assert bytes(memory[0xAA7E:0xAA8B]) == bytes.fromhex('C3 73 C8 C9 C9 C9 C9 21 00 00 CD 87 C2')

    exits = Counter()
    for selector in range(256):
        for same_row in (False, True):
            profile = prepare(base, selector)
            put(profile.memory, 0x6307, (50, 3 if same_row else 80))
            profile.memory[0xAEC7] = 3
            reached = []

            def observe(_, pc):
                if pc in (0xAA5B, 0xAA81, 0xAA82, 0xAA83, 0xAA84, 0xAA7E):
                    reached.append(pc)

            profile.run(0xAA58, observe)
            assert not {0xAA82, 0xAA83, 0xAA84}.intersection(reached)
            assert reached[0] == 0xAA5B and profile.sim.registers[SP] == 0x8000
            exits[f'{reached[-1]:04X}'] += 1

    before = [bytes(bank) for bank in memory.banks]
    for address in (0xAA82, 0xAA83):
        for af in range(65536):
            registers = fixture.sim.registers
            registers[:] = fixture.initial
            registers[:2] = [af >> 8, af & 255]
            fixture.sim.run(address, 0x3FFF)
            assert registers[:2] == [af >> 8, af & 255] and registers[SP] == 0x8000
            assert registers[2:12] == fixture.initial[2:12] and registers[16:24] == fixture.initial[16:24]
    assert [bytes(bank) for bank in memory.banks] == before and not fixture.trace.writes
    return dict(current_descriptor_audit=descriptor_audit, original_action_exit_profiles=dict(exits),
                separately_forced_ret_profiles=131072, current_normal_entry_to_either_ret_proved=False,
                native_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    proof = check_archived_layout(args.source_archive) | check_current_paths()
    if args.publish:
        publish(slot=4, origin=0x6000, ranges=((0x4A82, 0x4A84),), resources=RESOURCES,
                tag='StationLegacyMissionReturns', resource_module='ClassifyStationLegacyMissionReturns',
                resource_name='STATION_LEGACY_MISSION_RETURNS', proof=proof)
    else:
        print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
