"""Сверка исходников и размещения архивного RUN без ассемблирования."""
from hashlib import sha256
import json

from CheckArchiveEngineSource import ARCHIVE, ROOT, compare_layout, compare_source


def main():
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    raw = (ARCHIVE / '45_RUN.C.sectors.bin').read_bytes()
    tail = (ARCHIVE / '45_RUN.C.tail.bin').read_bytes()
    assert raw == disk[0x87400:0x8B100] and tail == raw[0x3CDD:]
    instructions, structured = compare_source(raw, ROOT / 'Source/Files/45_RUN.inc', 0x6000)
    compare_layout(disk)
    result = dict(passed=True, slot=45, original_disk_offset=0x87400, origin=0x6000,
                  instructions=instructions, structured_bytes=structured, verified_disk_layout_bytes=len(disk),
                  run_physical_sha256=sha256(raw).hexdigest(), assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveRunSourceVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
