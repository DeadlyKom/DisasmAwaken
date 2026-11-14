"""Сверка строки архивного BASIC, секторного хвоста и разметки TRD."""
from hashlib import sha256
import json

from CheckArchiveEngineSource import ARCHIVE, ROOT, compare_layout, compare_source


def main():
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    prefix = '44__K-II.d2.B'
    raw = (ARCHIVE / f'{prefix}.sectors.bin').read_bytes()
    header = (ARCHIVE / f'{prefix}.header.bin').read_bytes()
    logical = (ARCHIVE / f'{prefix}.bin').read_bytes()
    tail = (ARCHIVE / f'{prefix}.tail.bin').read_bytes()
    assert raw == disk[0x87300:0x87400] == logical + tail
    assert header == disk[0x2C0:0x2D0] and header[:9] == b'\x00K-II.d2B'
    assert int.from_bytes(header[9:11], 'little') == int.from_bytes(header[11:13], 'little') == len(logical) == 28
    assert int.from_bytes(logical[:2], 'big') == 1
    assert int.from_bytes(logical[2:4], 'little') == len(logical[4:]) == 24
    assert logical[4:17] == b'\xF9\xC015619\x0E\x00\x00\x03\x3D\x00'
    assert logical[17:] == b'\x3A\xEA\x3A\xF7"RUN"\xAF\x0D'
    assert tail[:4] == b'\x80\xAA\x00\x00'
    instructions, structured = compare_source(raw, ROOT / 'Source/Files/44_BASIC.inc', 0)
    assert instructions == 0 and structured == 13
    compare_layout(disk)
    result = dict(passed=True, slot=44, original_disk_offset=0x87300, logical_bytes=len(logical),
                  structured_bytes=structured, sector_tail_bytes=len(tail), autostart_line=0,
                  physical_sha256=sha256(raw).hexdigest(), verified_disk_layout_bytes=len(disk),
                  assembly_executed=False)
    encoded = json.dumps(result, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ArchiveBasicSourceVerification.json').write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()
