"""Именованные обращения к MMASK и MPALKA во всех распознанных авторских текстах.

Документация: ../../../Docs/ControlsObjectProjection.md
"""
from hashlib import sha256
import json
import re

from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256, load_sources
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from InspectUnresolvedAuthorSymbols import inspect as inspect_storm


def main():
    sources, _, _ = load_sources(ARCHIVE)
    assert len(sources) == 129
    pattern = rb'(?<![A-Z0-9_])(MMASK|MPALKA)(?![A-Z0-9_])'
    hits = []
    identities = []
    panel = None
    for source in sources:
        content = source['content']
        identities.append(dict(member=source['member'], slot=source['slot'],
            name=source['name'], bytes=len(content), sha256=sha256(content).hexdigest()))
        if source['member'] == 'awk1.trd' and source['slot'] == 40:
            panel = content
        lines = content.split(b'\r')
        # Поиск полных имён, контекст сохраняется исходными байтами без исполнения текста.
        for number, line in enumerate(lines, 1):
            match = re.search(pattern, line, re.I)
            if match:
                hits.append(dict(member=source['member'], slot=source['slot'],
                    name=source['name'], line=number, identifier=match[1].decode('ascii'),
                    kind='definition' if line in (b'MMASK', b'MPALKA') else 'known_operand',
                    raw_line_hex=line.hex(),
                    context_hex=[row.hex() for row in lines[max(0, number-3):number+2]]))
    assert {(row['member'], row['slot'], row['line'], row['identifier']) for row in hits} == {
        ('awk1.trd', 40, 543, 'MPALKA'), ('awk1.trd', 40, 675, 'MMASK'),
        ('awk1.trd', 40, 756, 'MPALKA'), ('awk1.trd', 40, 765, 'MMASK')}
    assert len(hits) == 4 and panel is not None
    # Проверка всех восьми шестибайтовых объявлений против текущего CONTROL.
    lines = panel.split(b'\r')
    start = lines.index(b'MMASK')
    declared = bytearray()
    for line in lines[start+1:start+9]:
        match = re.fullmatch(rb'\x06[\x80-\x8f]\x05g\x06\x83([%#0-9A-F,]+)', line)
        assert match, line.hex()
        values = match[1].split(b',')
        assert len(values) == 6
        for value in values:
            declared.append(int(value[1:], 2) if value.startswith(b'%') else
                            int(value[1:], 16) if value.startswith(b'#') else int(value))
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(disk).hexdigest() == manifest['sha256']
    _, control, _ = read_entry(disk, b'CONTROL C')
    assert bytes(declared) == control[0xBAF:0xBDF]
    assert all(declared[phase*6+offset] == 0 for phase in range(8) for offset in range(2, 6))
    # Структурированные STORM разбираются отдельно от CR-текстов.
    storm = inspect_storm({'MMASK', 'MPALKA'})
    assert not storm['mentions']
    assert sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256
    result = dict(passed=True, method='all_recognized_archive_sources_named_mask_reference_search',
        archive_sha256=ARCHIVE_SHA256, original_disk_sha256=manifest['sha256'],
        text_sources_checked=129, structured_storm_sources_checked=31,
        total_sources_checked=160, source_identities=identities, text_mentions=hits,
        structured_storm_inspection=storm, matched_current_clear_mask_bytes=48,
        physical_clear_phase_bytes=6, zero_tail_bytes_per_phase=4,
        additional_named_consumer_found=False, current_full_game_access_graph_proved=False,
        numeric_aliased_and_indirect_accesses_excluded=False,
        zero_tail_global_unusedness_proved=False, semantic_field_names_established=False,
        assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ArchivedObjectMaskReferences.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('passed', 'total_sources_checked',
        'text_mentions', 'matched_current_clear_mask_bytes', 'additional_named_consumer_found')},
        ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
