"""Сверяет объявление NDATA и изменённый заголовок нынешнего CONTROL."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import compare_reset_context, read_entry
from CheckControlsTemporaryModule import RecordedBanks
from CheckIntro import ROOT
from CheckMusic import PC, Simulator, get_registers
from CheckScreenUpdate import put


RESOURCES = (
    (0x148, 0x150, 'Source/Controls/Resources/LegacyResetRevisedHeader.bin',
     'CONTROL_LEGACY_RESET_REVISED_HEADER',
     'Изменённая часть заголовка исходного NDATA, потребители полей не установлены'),
)


def authored_reset_bytes(source):
    lines = source.split(b'\r')
    start, end = lines.index(b'NDATA'), lines.index(b'RETSTT')
    raw = bytearray()
    for line in filter(None, lines[start + 1:end]):
        declaration = re.fullmatch(rb'\x06\x8c\x05([ghi])\x06\x83([#\dA-F,]+)(?:;.*)?', line)
        assert declaration, line
        kind, values = declaration.groups()
        numbers = [int(v[1:], 16) if v.startswith(b'#') else int(v) for v in values.split(b',')]
        if kind == b'i':
            assert len(numbers) == 1
            raw.extend(bytes(numbers[0]))
        else:
            width = 1 if kind == b'g' else 2
            for number in numbers:
                raw.extend(number.to_bytes(width, 'little'))
    return bytes(raw)


def check_archived_copy(old_control, origin, authored_size):
    start = origin + 0x20F
    target = 0x9BBD
    data = old_control[0x138:0x338]
    assert len(data) == 512
    assert old_control[0x20F:0x21C] == bytes.fromhex('D9 21 4B E1 11 BD 9B 01 00 02 ED B0 D9')
    memory = RecordedBanks(banks=[bytearray(0x4000) for _ in range(8)], out7ffd=0x11)
    put(memory, origin, old_control)
    put(memory, target - 1, b'\xA5' * 514)
    cpu = Simulator(memory)
    cpu.registers[:] = get_registers({'PC': start, 'SP': 0x5FF0}, None, False)
    cpu.run(start, start + 13)
    assert cpu.registers[PC] == start + 13
    assert bytes(memory[target:target + 512]) == data
    assert memory[target - 1] == memory[target + 512] == 0xA5
    assert bytes(memory[target + authored_size:target + authored_size + 13]) == old_control[0x20F:0x21C]
    return dict(archived_copy_entry=start, archived_copy_destination=target, archived_copy_bytes=512,
                authored_data_bytes=authored_size, bytes_copied_after_authored_data=512 - authored_size,
                copy_instructions_in_destination=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        old_disk = archive.read('awk1.trd')
    old_origin, old, _ = read_entry(old_disk, b'CONTROL C')
    _, source, _ = read_entry(old_disk, b'SETHJRETa')
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    origin, control, _ = read_entry(disk, b'CONTROL C')
    assert old_origin == 0xE013 and origin == 0xDADE
    raw = authored_reset_bytes(source)
    assert len(raw) == 215 and raw == old[0x138:0x20F]
    context = compare_reset_context(old, control)
    assert context['target_template_bytes'] == 130
    assert control[0x147:0x150] == bytes.fromhex('00 06 FF 00 00 D0 07 00 32')
    assert control[0x1BD:0x1CB] == bytes.fromhex('21 A9 DC 11 00 40 01 00 01 ED B0 C3 00 40')
    assert (origin + 0x13B).to_bytes(2, 'little') not in disk
    copy = check_archived_copy(old, old_origin, len(raw))
    report = dict(passed=True, archive_sha256=digest, archived_declaration='awk1.trd:SETHJRET.a:NDATA',
                  revised_header_file_offsets=[0x148, 0x150], revised_header_hex=control[0x148:0x150].hex(),
                  current_template_location=[origin + 0x13B, origin + 0x1BD],
                  current_game_field_semantics_proved=False, assembly_executed=False, native_execution=False,
                  **copy)
    path = ROOT / 'Tools/Disasm/Reports/ControlsArchivedResetHeaderVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        publish(slot=23, origin=origin, ranges=((0x148, 0x150),), resources=RESOURCES,
                tag='ControlsArchivedResetHeader', resource_module='CheckControlsArchivedResetHeader',
                resource_name='CONTROLS_ARCHIVED_RESET_HEADER', proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()
