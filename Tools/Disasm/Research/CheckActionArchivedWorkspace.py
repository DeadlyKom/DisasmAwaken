"""Сверяет исходные резервы страниц L9C, L9D и поля 3DTABS перед TIME."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ArchivedSourceInventory import load_sources


FORMAT = 'ACTION_AUTHORED_RENDER_PAGE_TAIL'
RESOURCES = (
    (0x2EC8, 0x2F00, 'Source/Action/Resources/ProjectedPointsPageTail.bin', FORMAT,
     'Последние 56 байтов авторской страницы L9C после ста пар проекции'),
    (0x2FFC, 0x3000, 'Source/Action/Resources/RenderQueuePageTail.bin', FORMAT,
     'Последние четыре байта авторской страницы L9D за полными узлами очереди'),
)


def inspect_step_references(archive):
    names = (b'STPA', b'STPB', b'STPG')
    references = []
    sources, _, _ = load_sources(archive.filename)
    checked = len(sources)
    for source in sources:
        for number, line in enumerate(source['content'].split(b'\r'), 1):
            for name in names:
                if not re.search(rb'(?<![A-Z0-9_])' + name + rb'(?![A-Z0-9_])', line, re.I):
                    continue
                # Проверка назначения найденной строки, употребление имени не равно обращению к памяти.
                if re.fullmatch(name + rb':\x06[\x80-\x8f]\x05g\x06\x830', line):
                    kind = 'zero_byte_declaration'
                else:
                    assert re.fullmatch(name + rb'\x06.\x04f\d+', line)
                    kind = 'symbol_listing'
                references.append(dict(member=source['member'], slot=source['slot'], line=number,
                                       name=name.decode('ascii'), kind=kind, raw_hex=line.hex()))
    assert checked == 129 and len(references) == 12
    assert {(r['member'], r['slot']) for r in references} == {
        ('awk1.trd', 49), ('awk1.trd', 63), ('awk3.trd', 18), ('awk4.trd', 18)}
    assert sum(r['kind'] == 'zero_byte_declaration' for r in references) == 9
    # Поиск буквальных адресов также включает начало слова на байт раньше первого STP.
    flow = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    current = []
    for region in flow:
        for item in region['instructions']:
            literals = {int(value, 16) for value in re.findall(r'#([0-9A-F]{4})\b', item['operation'])}
            if literals.intersection(range(0x9B9D, 0x9BA1)):
                current.append(dict(region=region['name'], address=item['address'], operation=item['operation']))
    assert not current
    return dict(active_archived_source_entries_checked=checked, identifier_occurrences=references,
                named_archived_consumers_found=False, current_decoded_literal_references=current,
                watched_literal_addresses=list(range(0x9B9D, 0x9BA1)),
                indirect_or_block_accesses_excluded=False, current_global_unusedness_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
        step_references = inspect_step_references(archive)
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    _, action, _ = read_entry(original, b'ACTION  C')
    origin, data, _ = read_entry(original, b'DATAS   C')
    archive_origin, old_data, _ = read_entry(disk, b'DATAS   C')
    _, source, _ = read_entry(disk, b'3DTABS  a')
    _, masks, _ = read_entry(disk, b'D9000   d')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    assert origin == archive_origin == 0x8C00
    assert data == action[0x2C00:0x482D] and data[:0xFCC] == old_data[:0xFCC]
    assert len(masks) == 0x200 and masks == data[:0x200]
    assert b'\x05m"D9000.dat"\r' in source
    for name in (b'L9C', b'L9D', b'L9E'):
        assert name + b':\x06\x88\x05f\x06\x82$.h\r\x06\x8c\x05i\x06\x83#100\r' in source
    assert data[0x200:0x500] == bytes(0x300)
    assert all(action[first:last] == bytes(last - first) for first, last, *_ in RESOURCES)
    fields = {}
    for name, address, width in ((b'EYE_X', 0x9B98, 2), (b'EYE_Y', 0x9B9A, 2),
                                 (b'EYE_Z', 0x9B9C, 2), (b'STPA', 0x9B9E, 1),
                                 (b'STPB', 0x9B9F, 1), (b'STPG', 0x9BA0, 1)):
        assert any(line.startswith(name + b'\x06') and line.endswith(b'\x04f' + str(address).encode())
                   for line in labels.split(b'\r'))
        directive = b'h' if width == 2 else b'g'
        assert re.search(name + rb':\x06[\x80-\x8F]\x05' + directive + rb'\x06\x830\r', source)
        assert action[address - 0x6000:address - 0x6000 + width] == bytes(width)
        fields[name.decode()] = [address, width]
    assert b'PLANDICTAT: \x05i\x06\x8316\r' in source
    assert b'WERPO:\x06\x86\x05i\x06\x839\r' in source
    assert b'WERPO\x06\x8a\x04f39860\r' in labels
    assert action[0x3BB3:0x3BBD] == bytes(10)
    result = dict(passed=True, archive_sha256=digest, source='awk1.trd:3DTABS.a',
                  common_prefix=0xFCC, archived_camera_fields=fields,
                  archived_parameter_extent=[0x9BA4, 0x9BB4], archived_spawn_chances=[0x9BB4, 0x9BBD],
                  initial_page_ranges=[[0x8E00, 0x8F00], [0x8F00, 0x9000]],
                  tail_file_ranges=[list(row[:2]) for row in RESOURCES],
                  camera_and_chances_current_game_users_proved=False,
                  archived_step_references=step_references,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionArchivedWorkspaceVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        publish(slot=17, origin=0x6000, ranges=tuple(row[:2] for row in RESOURCES), resources=RESOURCES,
                tag='ActionArchivedWorkspace', resource_module='CheckActionArchivedWorkspace',
                resource_name='ACTION_ARCHIVED_WORKSPACE', proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()
