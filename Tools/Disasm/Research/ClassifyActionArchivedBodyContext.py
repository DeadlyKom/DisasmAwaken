"""Архивное происхождение байта #697D и второго байта исходной пары SPEED."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckActionParameterActivation import flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckMusic import SP, Simulator, get_registers
from ClassifyStationWorkspaceResources import ROOT, publish
from ProbeShipPreviewCallbacks import payload
from skoolkit.simutils import A, E


RESOURCES = (
    (0x0BBA, 0x0BBB, 'Source/Action/Resources/LegacyBodyIndexLoad.bin',
     'ACTION_LEGACY_BODY_INDEX_LOAD', 'Байт #7B, остаток архивного LD A,E перед банковой обёрткой'),
    (0x3C89, 0x3C8A, 'Source/Action/Resources/InitialArchivedSkimmerSpeed.bin',
     'ACTION_ARCHIVED_SKIMMER_SPEED', 'Исходный второй байт архивной пары SPEED, роль после переноса неизвестна'),
)


def archive_inputs(path):
    with ZipFile(path) as archive:
        origin, sp, _ = read_entry(archive.read('awk5.trd'), b'SP      C')
        _, declarations, _ = read_entry(archive.read('awk6.trd'), b'DATA_M  a')
        _, old_jump, _ = read_entry(archive.read('awk1.trd'), b'SETCONTRa')
    assert origin == 0x6000 and len(sp) == 0x984B
    start = declarations.index(b'NEWS\x06\x88\x05g\x06\x831,0')
    order = declarations.index(b'\rORDER\r', start)
    speed = declarations.index(b'\rSPEED\r', order)
    distance = declarations.index(b'\rDALNO', speed)
    assert declarations[order:speed].count(b'\x05i\x06\x8315') == 4
    assert declarations[speed:distance].count(b'\x05g\x06\x830,0') == 1
    assert 'СКОРОСТЬ КУПЛЕННОГО КОРАБЛЯ,СКИМЕРА'.encode('cp866') in declarations[speed:distance]
    assert declarations[distance:].startswith(b'\rDALNO\x06\x87\x05h\x06\x830')
    assert b'(DALNO)' in old_jump
    return sp


def historical_memory(sp):
    memory = bytearray(65536)
    memory[0x6000:0x6000 + len(sp)] = sp
    memory[0x4200:0x43FA] = sp[0x43:0x23D]
    assert memory[0x4200:0x420C] == bytes.fromhex('31 00 C0 E5 11 00 60 01 95 1D ED B0')
    cpu = Simulator(memory, {'HL': 0x623D}, config={'fast_ldir': True})
    cpu.run(0x4200, 0x420C)
    assert memory[0x6000:0x7D95] == sp[0x23D:0x1FD2]
    return memory


def check_body_branch(historical, current):
    assert historical[0x6947:0x6958] == bytes.fromhex('3A C3 9B BB C8 7B 32 C3 9B 3E 11 CD FF AB C3 81 E5')
    assert current[0x6978:0x6986] == bytes.fromhex('3A C5 9B BB C9 7B 3E 11 CD 1B AB C3 0A DE')
    old, new = Simulator(historical), Simulator(current)
    initial = get_registers({'SP': 0xBFFE}, None, False)
    for memory in (historical, current):
        memory[0xBFFE:0xC000] = b'\xFF\x3F'
    for stored in range(256):
        for proposed in range(256):
            equal = stored == proposed
            historical[0x9BC3] = current[0x9BC5] = stored
            for cpu in (old, new):
                cpu.registers[:] = initial
                cpu.registers[E] = proposed
            old.run(0x6947, 0x3FFF if equal else 0x6950)
            new.run(0x6978, 0x3FFF)
            assert (old.registers[A], historical[0x9BC3]) == (proposed, proposed)
            assert old.registers[SP] == (0xC000 if equal else 0xBFFE)
            assert (new.registers[A], current[0x9BC5], new.registers[SP]) == (stored, stored, 0xC000)
    return dict(input_pairs=65536, old_conditional_return=0x694B, old_load_a_e=0x694C,
                old_field_writer=0x694D, old_banked_build_entry=0x6950,
                new_unconditional_return=0x697C, new_residual_byte=0x697D, new_banked_build_entry=0x697E)


def check_distance(historical, sp, action):
    assert sp[0x3C3D:0x3C88] == action[0x3C41:0x3C8C]
    assert sp[0x3C84:0x3C88] == action[0x3C88:0x3C8C] == b'\x64\x64\x00\x00'
    assert historical[0x703B:0x7041] == bytes.fromhex('2A 86 9C 7C A7 C0')
    cpu = Simulator(historical)
    initial = get_registers({'SP': 0xBFFE}, None, False)
    historical[0xBFFE:0xC000] = b'\xFF\x3F'
    for high in range(256):
        for low in (0, 1, 127, 255):
            historical[0x9C86:0x9C88] = bytes((low, high))
            cpu.registers[:] = initial
            cpu.run(0x703B, 0x3FFF if high else 0x7041)
            assert cpu.registers[A] == high and cpu.registers[SP] == (0xC000 if high else 0xBFFE)
    return dict(exact_layout_bytes=75, archived_speed_address=0x9C84, current_speed_pair_address=0x9C88,
                archived_distance_address=0x9C86, current_cost_address=0x9C8A,
                old_high_byte_return=0x7040, profiles=1024)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    sp = archive_inputs(args.source_archive)
    memory = historical_memory(sp)
    proof = dict(archive_sha256=sha256(args.source_archive.read_bytes()).hexdigest(),
                 body_branch=check_body_branch(memory, bytearray(flat_action())),
                 context=check_distance(memory, sp, payload(17)),
                 current_game_consumers_proved=False, native_execution=False)
    if args.publish:
        publish(slot=17, origin=0x6000, ranges=((0x0BBA, 0x0BBB), (0x3C89, 0x3C8A)),
                resources=RESOURCES, tag='ActionArchivedBodyContext',
                resource_module='ClassifyActionArchivedBodyContext', resource_name='ACTION_ARCHIVED_BODY_CONTEXT', proof=proof)
    else:
        print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
