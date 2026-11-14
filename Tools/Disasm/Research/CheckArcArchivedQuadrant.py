"""Происхождение снимка RDS, без вывода о назначении его старших битов."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from ArcWorkspaceTable import ORIGINAL
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ArchivedSourceInventory import load_sources


def main():
    path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    hits = []
    sources, _, _ = load_sources()
    checked = len(sources)
    for text in sources:
        for number, line in enumerate(text['content'].split(b'\r'), 1):
            if re.search(rb'(?<![A-Z0-9_])RDS(?![A-Z0-9_])', line, re.I):
                hits.append(dict(member=text['member'], slot=text['slot'], name=text['name'],
                                 line=number, raw_line_hex=line.hex()))
    with ZipFile(path) as archive:
        _, source, _ = read_entry(archive.read('awk6.trd'), b'CIRCMATHa')
        origin, old, _ = read_entry(archive.read('awk6.trd'), b'KARTA   C')
    assert len(hits) == 15
    assert sum(x['name'] == 'CIRCMATHa' for x in hits) == 14
    assert [(x['name'], x['line']) for x in hits if x['name'] != 'CIRCMATHa'] == [('KARTA   a', 101)]
    rows = source.split(b'\r')
    index = rows.index(b'RDS\x06\x89\x05g\x06\x83#0F')
    notes = rows[index - 2:index]
    assert notes == [' ЗНАКИ b0-X,b1-Y ,1-PLUS'.encode('cp866'),
                     ' ТАК ЖЕ b2,b3=1,1'.encode('cp866')]
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    current_origin, current, _ = read_entry(disk, b'KARTA   C')
    assert origin == current_origin == 0xC000 and checked == 129
    assert old[0x1FAB:0x1FC3] == current[0x1FAB:0x1FC3] == ORIGINAL
    report = dict(passed=True, archive_sha256=digest, original_disk_sha256=sha256(disk).hexdigest(),
                  source='awk6.trd:CIRCMATH.a', source_name='RDS', current_address=0xDFAD,
                  matched_workspace_bytes=len(ORIGINAL), initial_code=ORIGINAL[2],
                  source_notes_cp866_hex=[row.hex() for row in notes],
                  source_prescribes_bits_2_and_3_set=True, active_sources_checked=checked,
                  named_references=hits, high_bit_algorithmic_purpose_proved=False,
                  numeric_alias_and_generated_references_excluded=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArcArchivedQuadrantVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('RDS: совпали 24 байта снимка, найдено именованных ссылок:', len(hits))


if __name__ == '__main__':
    main()
