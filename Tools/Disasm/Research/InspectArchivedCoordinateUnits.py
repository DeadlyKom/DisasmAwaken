"""Поиск обозначений единиц и авторский порядок координат XW/YW/ZW."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ArchivedSourceInventory import load_sources
from ArchivedStormSources import load_storm_sources, SymbolWalker, format_evidence


def main():
    path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    pattern = re.compile(r'\b(?:КИЛОМЕТР\w*|КМ|KM|МЕТРОВ|МЕТРАХ|МЕТРЫ|СЕКУНД\w*|ЕДИНИЦ\w*)\b', re.I)
    hits = []
    sources, _, _ = load_sources()
    checked = len(sources)
    for source in sources:
        for number, row in enumerate(source['content'].split(b'\r'), 1):
            if pattern.search(row.decode('cp866')):
                hits.append(dict(member=source['member'], name=source['name'], line=number,
                                 raw_line_cp866_hex=row.hex()))
    with ZipFile(path) as archive:
        _, equs, _ = read_entry(archive.read('awk1.trd'), b'EQUS    a')
    axes = {}
    for row in equs.split(b'\r'):
        match = re.fullmatch(rb'(XW|YW|ZW)\x06.\x05f\x06\x82(\d+)', row)
        if match:
            axes[match[1].decode()] = int(match[2])
    assert checked == 129 and len(hits) == 1 and axes == dict(XW=0, YW=2, ZW=4)
    assert hits[0]['name'] == 'BRAINPROa' and hits[0]['line'] == 636
    format_evidence()
    storm = load_storm_sources()
    counts = dict(comments=0, string_literals=0, symbols=0)
    additional = []
    # Поиск в расшифрованных текстовых частях STORM, а не в его двоичных кодах операндов.
    for source in storm:
        for row in source['records']:
            walker = SymbolWalker(row['data'])
            symbols = walker.walk()
            for kind, items in (('comments', walker.comments), ('string_literals', walker.literals),
                                ('symbols', [dict(text=value['name']) for value in symbols])):
                counts[kind] += len(items)
                for item in items:
                    if pattern.search(item['text']):
                        additional.append(dict(member=source['member'], name=source['name'],
                            line=row['line'], part=kind, text=item['text'], raw_record_hex=row['data'].hex()))
    assert counts == dict(comments=1512, string_literals=39, symbols=5027)
    assert not additional
    report = dict(passed=True, method='archived_source_text_and_coordinate_definition_inspection',
                  archive_sha256=digest, active_sources_checked=checked + len(storm),
                  ordinary_text_source_entries_checked=checked, structured_storm_source_entries_checked=len(storm),
                  structured_text_parts_checked=counts, structured_unit_word_occurrences=additional,
                  whole_word_units_pattern=pattern.pattern, unit_word_occurrences=hits,
                  archived_coordinate_word_offsets=axes, spatial_or_speed_SI_unit_proved=False,
                  text_search_does_not_exclude_other_notations_or_packed_manuals=True,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchivedCoordinateUnitsInspection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены 160 исходников и смещения XW/YW/ZW, физические единицы не установлены.')


if __name__ == '__main__':
    main()
