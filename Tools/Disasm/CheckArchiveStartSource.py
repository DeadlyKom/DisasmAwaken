"""Статическая сверка двух окон и 129 секторов архивного START."""
from hashlib import sha256
import json

from CheckArchiveEngineSource import ARCHIVE, ROOT, compare_layout, compare_source, source_lines


def layer_macro():
    path = ROOT / 'Source/ArchiveStart/LayerRow.inc'
    builder = (ROOT / 'Builder/Main.asm').read_text('utf-8')
    assert 'include "../Source/ArchiveStart/LayerRow.inc"' in builder
    header, *body, end = filter(None, source_lines(path))
    directive, name, parameters = header.split(maxsplit=2)
    assert directive == 'MACRO' and name == 'ArchiveLayerRow' and end == 'ENDM'
    return {name.upper(): (tuple(map(str.strip, parameters.split(','))), body)}


def main():
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    raw = (ARCHIVE / '47_START.C.sectors.bin').read_bytes()
    tail = (ARCHIVE / '47_START.C.tail.bin').read_bytes()
    assert raw == disk[0x8C200:0x94300] and tail == raw[0x80C7:]
    instructions, structured = compare_source(raw, ROOT / 'Source/Files/47_START.inc', 0x6000, macros=layer_macro())
    compare_layout(disk)
    result = dict(passed=True, slot=47, original_disk_offset=0x8C200, fixed_origin=0x6000,
                  banked_origin=0xC000, instructions=instructions, structured_bytes=structured,
                  verified_disk_layout_bytes=len(disk), start_physical_sha256=sha256(raw).hexdigest(),
                  assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveStartSourceVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
