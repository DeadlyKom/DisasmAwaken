"""Имена неустановленных полей в структурированных источниках STORM, без сборки.

Документация: ../../../Docs/ActionInputContextData.md
Документация: ../../../Docs/StationTransportTradeTables.md
Документация: ../../../Docs/ActionClipTableAlias.md
"""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
from ArchivedStormSources import load_storm_sources, SymbolWalker
from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256, load_sources
from CheckIntro import ROOT


def inspect(names=None):
    names = {'STPA', 'STPB', 'STPG', 'CNKR', 'CNSK'} if names is None else {name.upper() for name in names}
    assert names
    pattern = r'(?<![A-Z0-9_])(' + '|'.join(re.escape(name) for name in sorted(names)) + r')(?![A-Z0-9_])'
    sources = load_storm_sources()
    hits, identities, records, symbols, comments, literals = [], [], 0, 0, 0, 0
    for source in sources:
        identities.append({key: source[key] for key in ('member', 'slot', 'name', 'bytes', 'sha256')})
        # Проверка обратимого тела исходника подтверждает хеш вместе с маркерами строк.
        body = b''.join(row['data'] + bytes((row['footer'],)) for row in source['records'])
        assert len(body) == source['bytes'] and sha256(body).hexdigest() == source['sha256']
        for row in source['records']:
            records += 1
            walker = SymbolWalker(row['data'])
            found = []
            for item in walker.walk():
                symbols += 1
                if item['name'].upper() in names:
                    found.append(dict(kind='definition' if item['byte_offset'] == 0 and 'definition' in row
                                      else 'operand_symbol', byte_offset=item['byte_offset'], name=item['name']))
            # Поиск в комментариях и строках не смешивается с обращениями к символам.
            for kind, parts in (('comment', walker.comments), ('string_literal', walker.literals)):
                if kind == 'comment': comments += len(parts)
                else: literals += len(parts)
                for part in parts:
                    for match in re.finditer(pattern,
                                             part['text'], re.I):
                        found.append(dict(kind=kind, byte_offset=part['byte_offset'],
                                          name=match[1], text=part['text']))
            hits.extend(dict(member=source['member'], slot=source['slot'], source=source['name'],
                line=row['line'], file_offset=row['file_offset'], original_record_hex=row['data'].hex(), **item)
                for item in found)
    assert len(sources) == 31 and records == 18123
    assert sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256
    return dict(passed=True, method='structured_STORM_symbol_comment_and_literal_search',
        archive_sha256=ARCHIVE_SHA256, queried_names=sorted(names), source_entries=len(sources),
        records=records, decoded_symbol_occurrences=symbols, comment_fragments=comments,
        string_literal_fragments=literals, source_identities=identities, mentions=hits,
        binary_source_not_treated_as_CR_text=True, numeric_or_aliased_accesses_excluded=False,
        computed_or_indirect_accesses_excluded=False, current_consumers_proved=False,
        semantic_field_names_established=False, assembly_executed=False, native_execution=False)


def inspect_all(names):
    """Все распознанные исходники, без смешивания CR-текстов и записей STORM."""
    names = {name.upper() for name in names}
    assert names and all(re.fullmatch(r'[A-Z_][A-Z0-9_]*', name) for name in names)
    pattern = re.compile(rb'(?<![A-Z0-9_])(' + b'|'.join(name.encode('ascii') for name in sorted(names)) + rb')(?![A-Z0-9_])', re.I)
    sources, _, _ = load_sources(ARCHIVE)
    assert len(sources) == 129
    hits, identities = [], []
    for source in sources:
        content = source['content']
        identities.append(dict(member=source['member'], slot=source['slot'], name=source['name'],
                               bytes=len(content), sha256=sha256(content).hexdigest()))
        lines = content.split(b'\r')
        # Все текстовые совпадения сохраняются без назначения им семантики команды.
        for number, raw in enumerate(lines, 1):
            for match in pattern.finditer(raw):
                hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                    line=number, identifier=match[1].decode('ascii'), raw_line_hex=raw.hex(),
                    text_match_not_automatically_instruction=True,
                    context_hex=[row.hex() for row in lines[max(0, number-3):number+2]]))
    storm = inspect(names)
    return dict(passed=True, method='recognized_text_and_structured_STORM_symbol_search',
        queried_names=sorted(names), archive_sha256=ARCHIVE_SHA256,
        text_source_entries=129, structured_source_entries=storm['source_entries'],
        total_source_entries=129+storm['source_entries'], text_source_identities=identities,
        text_mentions=hits, structured_storm_inspection=storm,
        numeric_or_aliased_accesses_excluded=False, computed_or_indirect_accesses_excluded=False,
        same_identifier_does_not_prove_same_address_across_versions=True,
        current_consumers_proved=False, semantic_field_names_established=False,
        assembly_executed=False, native_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-sources', action='store_true')
    parser.add_argument('--names', nargs='+')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.all_sources and (not args.names or not args.output):
        parser.error('--all-sources требует явных --names и относительного --output')
    result = inspect_all(args.names) if args.all_sources else inspect(args.names)
    relative = args.output or Path('Tools/Disasm/Reports/UnresolvedAuthorSymbolsStormInspection.json')
    assert not relative.is_absolute()
    target = ROOT/relative
    assert target.resolve().is_relative_to(ROOT.resolve())
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.all_sources:
        print(json.dumps(dict(passed=result['passed'], sources=result['total_source_entries'],
            text_mentions=len(result['text_mentions']), structured_mentions=len(result['structured_storm_inspection']['mentions']))))
    else:
        print(json.dumps({key: result[key] for key in ('passed', 'source_entries', 'records', 'mentions')}))


if __name__ == '__main__':
    main()
