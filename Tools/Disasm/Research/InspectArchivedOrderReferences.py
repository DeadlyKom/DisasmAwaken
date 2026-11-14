"""Полные текстовые идентификаторы ORDER в действующих авторских исходниках шести TRD."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from CheckIntro import ROOT
from ArchivedSourceInventory import ARCHIVE, load_sources
from InspectUnresolvedAuthorSymbols import inspect as inspect_storm_symbols


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path, nargs='?', default=ARCHIVE)
    args = parser.parse_args()
    digest = sha256(args.source_archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    hits = []
    sources, disks, _ = load_sources(args.source_archive)
    checked = len(sources)
    members = [row['member'] for row in disks]
    for source in sources:
        for line_number, line in enumerate(source['content'].split(b'\r'), 1):
            if not re.search(rb'(?<![A-Z0-9_])ORDER(?![A-Z0-9_])', line, re.I):
                continue
            if line in (b'ORDER', b'ORDER:'):
                kind = 'data_declaration'
            elif line == b'ORDER\x06\x8a\x04f40006':
                kind = 'symbol_listing'
            elif line == b';NUMBERS IN ORDER PRINT':
                kind = 'unrelated_English_comment'
            else:
                kind = 'unreviewed_text_occurrence'
            hits.append(dict(member=source['member'], slot=source['slot'], name=source['name'],
                             line=line_number, raw_line_hex=line.hex(), kind=kind))
    assert checked == 129
    assert {(x['member'], x['slot'], x['kind']) for x in hits} == {
        ('awk1.trd', 49, 'data_declaration'), ('awk1.trd', 63, 'symbol_listing'),
        ('awk4.trd', 33, 'data_declaration'), ('awk4.trd', 47, 'unrelated_English_comment'),
        ('awk4.trd', 60, 'data_declaration'), ('awk6.trd', 56, 'data_declaration')}
    assert len(hits) == 6
    # Проверка оставшихся 31 структурированных STORM, имена не ищутся как обычный CR-текст.
    storm = inspect_storm_symbols({"ORDER"})
    assert {(x["member"], x["slot"], x["kind"]) for x in storm["mentions"]} == {
        ("awk2.trd", 48, "definition"), ("awk2.trd", 64, "comment")}
    assert len(storm["mentions"]) == 2
    assert storm["mentions"][1]["text"] == ";NUMBERS IN ORDER PRINT"
    report = dict(passed=True, archive_sha256=digest, disk_members=members,
                  active_source_entries_checked=checked, total_text_and_storm_sources_checked=checked+storm['source_entries'],
                  structured_storm_inspection=storm, identifier='ORDER',
                  identifier_occurrences=hits, named_consumer_text_found=False,
                  numeric_or_aliased_references_excluded=False,
                  current_game_consumer_proved=False, assembly_executed=False,
                  native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchivedOrderReferences.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены 129 текстов и 31 STORM, пять объявлений ORDER, листинг и два английских комментария. Именованный потребитель не найден.')


if __name__ == '__main__':
    main()
