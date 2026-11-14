"""Девять токенизированных XAS 9.07 из авторского awk5.trd.

Документация: ../../../Docs/AuthorSourceInventory.md#токенизированные-xas-907
"""
from collections import Counter
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256
from CheckIntro import ROOT


SIGNATURE = b'XAS 9.07 ReCompiled by Mythos'
SLOTS = (8, 9, 10, 11, 22, 23, 24, 27, 29)
QUERY_NAMES = ('RDS', 'SEDETECT', 'STPA', 'STPB', 'STPG', 'EYE_A', 'EYE_B',
               'EYE_G', 'SETS', 'JL1', 'JL2', 'NEWS', 'ORDER', 'ABONS',
               'PLAYER', 'SHILD', 'CNKR', 'CNSK', 'LZS', 'RCO', 'EXAS', 'EFF')


def allocated_file(image, slot):
    header = image[slot * 16:(slot + 1) * 16]
    start = (header[15] * 16 + header[14]) * 256
    return header, start, image[start:start + header[13] * 256]


def converter_table(image):
    header, offset, allocated = allocated_file(image, 31)
    assert header[:9] == b'AX3     C' and int.from_bytes(header[9:11], 'little') == 0x6000
    compiled = allocated[:int.from_bytes(header[11:13], 'little')]
    # Сверка чтения текста от C024 и выхода по нулевому байту, это код преобразователя AX3.
    assert compiled[0x4FE:0x504] == bytes.fromhex('2124C07EB7C8')
    # Сверка выбора токена, таблицы 6D50, пропуска слов и снятия старшего бита последнего символа.
    expected = bytes.fromhex('7ECB7FC8E521506DCBBF47B7280B7ECB7F2328FA10F8010900CB7EEDA028FAD5E12BCBBEE123C9')
    assert compiled[0x584:0x584 + len(expected)] == expected
    position = 0xD50
    tokens = {}
    for code in range(0x80, 0xF3):
        word = bytearray()
        while compiled[position] < 128:
            word.append(compiled[position])
            position += 1
        word.append(compiled[position] & 127)
        position += 1
        tokens[code] = word.decode('ascii')
    assert compiled[position] == 0x80 and position == 0xEA0
    assert tokens[0xAC] == 'LD' and tokens[0xC4] == 'ORG' and tokens[0xCF] == 'LOADCODE'
    return tokens, dict(member='awk5.trd', slot=31, name='AX3     C',
        compiled_origin=0x6000, compiled_sha256=sha256(compiled).hexdigest(),
        compiled_disk_offset=offset, source_start_load_instruction=0x64FE,
        source_end_check_addresses=[0x6501, 0x6502, 0x6503],
        token_expansion_addresses=[0x6584, 0x6589, 0x658C, 0x6592, 0x659D, 0x65A6],
        token_table_address=0x6D50, token_table_end_exclusive=0x6EA1,
        token_table_sha256=sha256(compiled[0xD50:0xEA1]).hexdigest(),
        token_count=len(tokens), converter_executed=False, assembly_executed=False)


def expanded_line(line, tokens):
    quoted, comment = False, False
    result, counts = [], Counter()
    for byte in line:
        if byte == ord(';') and not quoted:
            comment = True
        if byte == ord('"') and not comment:
            quoted = not quoted
        if byte >= 128 and not quoted and not comment:
            assert byte in tokens, (byte, line)
            result.append(' ' + tokens[byte] + ' ')
            counts[byte] += 1
        else:
            result.append(bytes((byte,)).decode('cp866'))
    assert not quoted, line
    return ''.join(result), counts


def xas_sources_from_disk(image):
    tokens, evidence = converter_table(image)
    result = []
    for slot in SLOTS:
        header, offset, allocated = allocated_file(image, slot)
        assert header[8:11] == b'XAS' and allocated.startswith(SIGNATURE)
        # Поиск нулевого конца внутри выделенных секторов, слово длины каталога не задаёт границу.
        end = allocated.index(0, 36)
        content = allocated[36:end]
        assert content.endswith(b'\r')
        rows, all_counts = [], Counter()
        for number, raw in enumerate(content.split(b'\r'), 1):
            expanded, counts = expanded_line(raw, tokens)
            all_counts.update(counts)
            rows.append(dict(line=number, original_hex=raw.hex(), expanded_tokens=expanded))
        result.append(dict(member='awk5.trd', slot=slot, name=header[:9].decode('cp866'),
            disk_offset=offset + 36, file_disk_offset=offset, bytes=len(content),
            sha256=sha256(content).hexdigest(), recognition='XAS_9_07_tokenized',
            plain_instruction_lines=0, content=content, lines=rows,
            allocated_bytes=len(allocated), allocated_sha256=sha256(allocated).hexdigest(),
            catalog_length_word=int.from_bytes(header[11:13], 'little'),
            catalog_length_word_semantics_proved=False,
            source_start_file_offset=36, zero_terminator_file_offset=end,
            trailing_allocated_bytes=len(allocated)-end-1,
            source_header_metadata_hex=allocated[29:36].hex(),
            source_header_metadata_semantics_proved=False,
            token_counts={f'{code:02X}': count for code, count in sorted(all_counts.items())}))
    return result, evidence, tokens


def load_xas_sources(archive_path=ARCHIVE):
    assert sha256(archive_path.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with ZipFile(archive_path) as archive:
        return xas_sources_from_disk(archive.read('awk5.trd'))


def loadcode_references(sources, archive_path=ARCHIVE):
    catalog = []
    with ZipFile(archive_path) as archive:
        for member in sorted(name for name in archive.namelist() if name.endswith('.trd')):
            image = archive.read(member)
            for slot in range(128):
                header = image[slot * 16:(slot + 1) * 16]
                if header[0] == 0:
                    break
                catalog.append(dict(member=member, slot=slot,
                    name=header[:8].decode('cp866').rstrip(' '),
                    extension=chr(header[8])))
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    current = [dict(slot=row['slot'], name=row['name'].rstrip(' '), extension=row['extension'])
               for row in manifest['entries'] if not row['deleted']]
    references = []
    # Поиск имён в директивах, совпадение каталога не заменяет выполнение загрузчика XAS.
    for source in sources:
        for row in source['lines']:
            if ' LOADCODE ' not in row['expanded_tokens']:
                continue
            match = re.fullmatch(rb'\xCF"([^\"]+)"', bytes.fromhex(row['original_hex']))
            assert match, row
            name = match[1].decode('ascii')
            references.append(dict(source=source['name'], slot=source['slot'], line=row['line'],
                requested_name=name,
                exact_archive_name_matches=[entry for entry in catalog if entry['name'] == name],
                case_insensitive_archive_name_candidates=[entry for entry in catalog if entry['name'].upper() == name.upper()],
                case_insensitive_current_image_name_candidates=[entry for entry in current if entry['name'].upper() == name.upper()],
                actual_directive_file_resolution_proved=False,
                current_game_resource_consumer_proved=False))
    assert len(references) == 11
    return references


def main():
    sources, evidence, tokens = load_xas_sources()
    hits = []
    for source in sources:
        for row in source['lines']:
            raw = bytes.fromhex(row['original_hex'])
            for name in QUERY_NAMES:
                if re.search(rb'(?<![A-Z0-9_])' + name.encode() + rb'(?![A-Z0-9_])', raw, re.I):
                    hits.append(dict(name=name, member=source['member'], slot=source['slot'],
                                     source=source['name'], line=row['line']))
    report = dict(passed=True, archive_sha256=ARCHIVE_SHA256, sources=len(sources),
        tokenized_source_bytes=sum(source['bytes'] for source in sources),
        converter_evidence=evidence,
        token_table={f'{code:02X}': word for code, word in tokens.items()},
        entries=[{key: value for key, value in source.items() if key != 'content'} for source in sources],
        queried_names=list(QUERY_NAMES), named_reference_hits=hits,
        loadcode_references=loadcode_references(sources),
        expanded_tokens_are_not_assembler_ready_source=True,
        source_versions_match_current_game_proved=False,
        arbitrary_other_source_formats_excluded=False, native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ArchivedXasSourceInventory.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'sources', 'tokenized_source_bytes', 'named_reference_hits')}))


if __name__ == '__main__':
    main()
