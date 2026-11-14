"""Сверяет выравнивания 3DPART и начало рабочего блока объектов с исходниками."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


OVERLAY = (
    (0x0EE3, 0x0F00, 'ClipDispatchAlignment', 'Выравнивание ADRXX00 перед младшей страницей L95'),
    (0x1194, 0x11C0, 'PolygonRowsAlignment', 'Переход к смещению C0 внутри страницы перед записью пролёта'),
    (0x2009, 0x2010, 'LineMasksAlignment', 'Заполнение до 16-байтовой границы масок MASKS'),
)
ALIGNMENT = 'ACTION_AUTHORED_ALIGNMENT'
BUFFER_TAIL = 'ACTION_AUTHORED_OBJECT_BUFFER_TAIL'
ACTION_ARCHIVED_LAYOUT = (
    (0x4017, 0x401C, 'Source/Action/Resources/ObjectStreamBufferTail.bin', BUFFER_TAIL,
     'Последние пять исходных байтов резерва OBJBUF'),
    (0x4027, 0x4100, 'Source/Action/Resources/ObjectRecordsAlignment.bin', ALIGNMENT,
     'Заполнение ADRXX00 после CARGS перед массивом CARSB'),
    *((a + 0x6000, b + 0x6000, f'Source/Action/Resources/{name}.bin', ALIGNMENT, note)
      for a, b, name, note in OVERLAY),
)
THREED_ARCHIVED_LAYOUT = tuple((a, b, f'Source/ThreeD/Resources/{name}.bin', ALIGNMENT, note)
                               for a, b, name, note in OVERLAY)


def check_overlay(disk, original, action):
    origin, previous, _ = read_entry(disk, b'3DPART  C')
    current_origin, current, _ = read_entry(original, b'3DPART  C')
    assert origin == current_origin == 0xC000 and current == action[0x6000:0x8020]
    assert current[:0x15CE] == previous[:0x15CE]
    assert current[0x1FB6:] == previous[0x1FB6:]
    _, clip, _ = read_entry(disk, b'CLIPMATRa')
    _, render, _ = read_entry(disk, b'3D-II   a')
    _, macros, _ = read_entry(disk, b'MACRO   a')
    _, space, _ = read_entry(disk, b'SPACE   a')
    assert b'ADRXX00\x06\x85\x03\xa2\r\x06\x8c\x05i\x06\x83(($-1).h).e-$+256\r' in macros
    assert b'\x05n"CLIPMATR"\r' in space and b'\x05n"3D-II"\r' in space
    assert b'\x06\x8cADRXX00\rL95:\r' in clip
    assert current[0x0EE2] == 0xC9
    assert b'\x05e\x06\x82(($.h).e)+#C0\r' in render
    assert bytes.fromhex('DD E9') == current[0x1192:0x1194]
    assert current[0x11C0:0x11FE] == b'\x02\x0C' * 31
    lines = render.split(b'\r')
    masks = lines.index(b'MASKS:')
    assert lines[masks - 1] == b'\x06\x8c\x05i\x06\x83$-1/16*16-$+16'
    words = [re.fullmatch(rb'\x06\x8c\x05h\x06\x83#([A-F0-9]{4})', line)
             for line in lines[masks + 1:masks + 9]]
    assert all(words)
    assert current[0x2010:0x2020] == b''.join(int(word[1], 16).to_bytes(2, 'little') for word in words)
    assert current[0x2008] == 0xC9
    for first, last, *_ in OVERLAY:
        assert current[first:last] == previous[first:last] == bytes(last - first)
    assert [((start - 1) // size + 1) * size for start, size in ((0x0EE3, 256), (0x2009, 16))] == [0x0F00, 0x2010]
    assert (0x1194 & 0xFF00) + 0xC0 == 0x11C0
    return [list(row[:2]) for row in OVERLAY]


def check_clip_table_alias(disk, sp_disk, original, action):
    _, source, _ = read_entry(disk, b'CLIPMATRa')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    old_origin, old, _ = read_entry(disk, b'3DPART  C')
    current_origin, current, _ = read_entry(original, b'3DPART  C')
    sp_origin, sp, _ = read_entry(sp_disk, b'SP      C')
    assert old_origin == current_origin == 0xC000 and sp_origin == 0x6000
    assert b'L95\x06\x8c\x04f52992' in labels.split(b'\r')
    lines = source.split(b'\r')
    align = b'\x06\x8cADRXX00'
    low = lines.index(b'L95:') + 1
    high = lines.index(align, low) + 1
    assert lines[low - 2] == align
    byte = rb'(?:\x06\x8c|[A-Z_0-9]+\x06[\x83\x84])\x05g\x06\x83'
    for start in (low, high):
        assert all(re.fullmatch(byte + rb'(?:[A-Za-z_0-9]+\.[bh]|0)', line)
                   for line in lines[start:start + 11])
    assert [line for line in lines if b'L95' in line] == [
        b'\x06\x8c\x05 \x06\x83\x03{,L95.h',
        b'\x06\x8c\x05 \x06\x83\x03{,L95.h',
        b'L95:',
    ]

    def span(data, origin, start, end):
        return data[start - origin:end - origin]

    pages = span(current, current_origin, 0xCF00, 0xD100)
    assert pages == span(old, old_origin, 0xCF00, 0xD100)
    assert pages == span(sp, sp_origin, 0xCF00, 0xD100)
    assert pages == span(action, 0x6000, 0xCF00, 0xD100)
    entries = []
    for index, name, target in (
        (8, 'C_XY_DXiY', 0xC4F3), (9, 'X937', 0xC0AF), (10, 'X951', 0xC0C9),
    ):
        symbol = name.encode('ascii')
        assert lines[low + index] == b'\x06\x8c\x05g\x06\x83' + symbol + b'.b'
        assert lines[high + index] == b'\x06\x8c\x05g\x06\x83' + symbol + b'.h'
        assert sum(line.startswith(symbol + b'\x06') for line in lines) == 1
        assert target == (pages[index] | (pages[0x100 + index] << 8))
        entries.append(dict(index=index, author_label=name, target=target,
                            low_address=0xCF00 + index, high_address=0xD000 + index))

    dispatchers = []
    for start, jump, window_start, point_page_offsets, opcodes in (
        (0xC066, 0xC070, 0xC058, (2, 9), '26 CF 5E 24 56 EB 11 71 C0 D5 E9'),
        (0xC986, 0xC992, 0xC97F, (2,), '26 CF 5E 24 56 EB 11 93 C9 D5 D5 D5 E9'),
    ):
        window = span(current, current_origin, window_start, jump + 1)
        assert window == span(old, old_origin, window_start, jump + 1)
        assert window == span(action, 0x6000, window_start, jump + 1)
        assert window[start - window_start:] == bytes.fromhex(opcodes)
        sp_window = bytearray(window)
        for offset in point_page_offsets:
            assert sp_window[offset] == 0xCF
            sp_window[offset] = 0x8D
        assert sp_window == span(sp, sp_origin, window_start, jump + 1)
        dispatchers.append(dict(address=start, jump=jump,
                                sp_point_page_changes=[window_start + offset for offset in point_page_offsets]))
    return dict(source='CLIPMATR.a', low_label='L95', entries=entries,
                compared_table_bytes=len(pages), dispatchers=dispatchers,
                runtime_entry_ruled_out=False)


def check_object_storage(disk, original, action):
    archive_origin, previous, _ = read_entry(disk, b'DATAS   C')
    origin, current, _ = read_entry(original, b'DATAS   C')
    assert archive_origin == origin == 0x8C00 and current == action[0x2C00:0x482D]
    assert current[0x1200:] == previous[0x1300:] and len(current[0x1200:]) == 0xA2D
    _, tables, _ = read_entry(disk, b'3DTABS  a')
    _, labels, _ = read_entry(disk, b'LABELS  a')
    assert b'OBJBUF\x06\x89\x04f40988\r' in labels
    assert b'CARGS\x06\x8a\x04f41244\r' in labels
    assert b'CARSB\x06\x8a\x04f41472\r' in labels
    assert b'OBJBUF:\x06\x85\x05i\x06\x83#100\r' in tables
    assert b'\rCARGS:\r' in tables
    assert b'\x05i\x06\x83#0A,#FFFF\r\x06\x8c\x05g\x06\x83#FE\r' in tables
    assert b'\rCARSB:\r' in tables and b'\x06\x8cADRXX00\r' in tables
    assert current[0x131C:0x141C] == bytes(0x100)
    assert current[0x141C:0x1427] == bytes.fromhex('FF ' * 10 + 'FE')
    assert current[0x1427:0x1500] == bytes(0xD9)
    assert current[0x1500:0x1502] == b'\x00\x80'
    return dict(archive_address_delta=0x100, exact_tail_bytes=0xA2D, object_stream=[0x9F1C, 0xA01C],
                candidate_codes=[0xA01C, 0xA027], alignment=[0xA027, 0xA100], first_record=0xA100)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
        sp_disk = archive.read('awk5.trd')
    original = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    _, action, _ = read_entry(original, b'ACTION  C')
    result = dict(passed=True, archive_sha256=digest, source_disk='awk1.trd',
                  overlay_alignments=check_overlay(disk, original, action),
                  clip_table_alias=check_clip_table_alias(disk, sp_disk, original, action),
                  object_storage=check_object_storage(disk, original, action),
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionArchivedLayoutVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        for slot, origin, resources, tag, name in (
            (17, 0x6000, ACTION_ARCHIVED_LAYOUT, 'ActionArchivedLayout', 'ACTION_ARCHIVED_LAYOUT'),
            (19, 0xC000, THREED_ARCHIVED_LAYOUT, 'ThreeDArchivedLayout', 'THREED_ARCHIVED_LAYOUT'),
        ):
            publish(slot=slot, origin=origin, ranges=tuple(row[:2] for row in resources),
                    resources=resources, tag=tag, resource_module='CheckActionArchivedLayout',
                    resource_name=name, proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()
