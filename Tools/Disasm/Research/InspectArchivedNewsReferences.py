"""Именованные обращения к NEWS и TNEWS, без переноса архивной логики в текущую игру."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from ArchivedSourceInventory import load_sources
from InspectUnresolvedAuthorSymbols import inspect as inspect_storm_symbols


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    hits = {'NEWS': [], 'TNEWS': []}
    sources, _, _ = load_sources()
    checked = len(sources)
    for source in sources:
        for line_number, line in enumerate(source['content'].split(b'\r'), 1):
            for identifier in hits:
                pattern = rb'(?<![A-Z0-9_])' + identifier.encode('ascii') + rb'(?![A-Z0-9_])'
                if re.search(pattern, line, re.I):
                    hits[identifier].append(dict(member=source['member'], slot=source['slot'],
                        name=source['name'], line=line_number, raw_line_hex=line.hex()))
    with ZipFile(archive_path) as archive:
        _, panel, _ = read_entry(archive.read('awk6.trd'), b'OBR     a')
        _, texts, _ = read_entry(archive.read('awk6.trd'), b'DATAT   a')

    # Проверяем все именованные употребления, включая объявления и листинг символов.
    assert checked == 129
    assert [(x['member'], x['slot']) for x in hits['NEWS']] == [
        ('awk1.trd', 49), ('awk1.trd', 63), ('awk4.trd', 33), ('awk4.trd', 60),
        ('awk6.trd', 52), ('awk6.trd', 56)]
    assert [(x['member'], x['slot']) for x in hits['TNEWS']] == [
        ('awk6.trd', 52), ('awk6.trd', 57)]
    lines = panel.split(b'\r')
    entry = lines.index(b'WNEWS_')
    sequence = lines[entry:entry + 8]
    # Проверяем исходный хвост LD A,(NEWS), LD HL,TNEWS, JP LIST в токенизированном тексте.
    assert sequence[5:] == [b'\x06\x8c\x05 \x06\x83\x03~,(NEWS)',
                            b'\x06\x8c\x05 \x06\x83\x03\x8c,TNEWS',
                            b'\x06\x8c\x053\x06\x83LIST']
    text_lines = texts.split(b'\r')
    table = text_lines.index(b'TNEWS')
    assert text_lines[table + 1] == b' \x05gET'
    assert text_lines[table + 2] == b' \x05g"' + 'Новостей нет.'.encode('cp866') + b'",ET'
    assert 'Федерацию напала враждебная расса '.encode('cp866') in text_lines[table + 4]
    # Проверка остальных структурированных исходников, отдельно от обычных текстов.
    storm = inspect_storm_symbols({"NEWS", "TNEWS"})
    assert len(storm["mentions"]) == 1
    occurrence = storm["mentions"][0]
    assert (occurrence["member"], occurrence["slot"], occurrence["kind"], occurrence["name"]) == (
        "awk2.trd", 48, "definition", "NEWS")
    report = dict(passed=True, method='recognized_tokenized_plain_and_structured_STORM_source_inspection',
                  archive_sha256=digest, active_source_entries_checked=checked,
                  total_text_and_storm_sources_checked=checked+storm["source_entries"],
                  structured_storm_inspection=storm,
                  identifier_occurrences=hits, historical_first_byte_consumer='awk6.trd:OBR.a:WNEWS_',
                  consumer_source_hex=[line.hex() for line in sequence],
                  consumer_first_line=entry + 1, text_table='awk6.trd:DATAT.a:TNEWS',
                  text_table_first_line=table + 1,
                  text_table_prefix_hex=[line.hex() for line in text_lines[table:table + 8]],
                  named_body_field_consumers_found=False,
                  numeric_or_aliased_references_excluded=False,
                  current_game_consumer_proved=False,
                  compiled_historical_consumer_proved=False,
                  assembly_executed=False, native_execution=False)
    output = ROOT / 'Tools/Disasm/Reports/ArchivedNewsReferences.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены 129 текстов и 31 STORM. Найдено пятое объявление NEWS, новых читателей тела нет, прежний архивный читатель первого байта сохранён.')


if __name__ == '__main__':
    main()
