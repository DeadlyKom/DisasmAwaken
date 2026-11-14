"""Распознанные тексты авторского архива, включая ASM с расширением C и XAS.

Документация: ../../../Docs/AuthorSourceInventory.md
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckIntro import ROOT


ARCHIVE = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
ARCHIVE_SHA256 = 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
PLAIN_SLOTS = set(range(32, 48)) | {64, 65}
ASM_LINE = re.compile(rb'^\s*(?:[A-Za-z_][A-Za-z_0-9]*:?\s+)?'
    rb'(?:LD|DB|DW|DS|ORG|EQU|JP|JR|CALL|RET|PUSH|POP|XOR|AND|OR|INC|DEC)\b', re.I)


def load_sources(archive_path=ARCHIVE):
    archive_path = Path(archive_path)
    assert sha256(archive_path.read_bytes()).hexdigest() == ARCHIVE_SHA256
    sources, disks, other_candidates = [], [], []
    with ZipFile(archive_path) as archive:
        for member in sorted(name for name in archive.namelist() if name.endswith('.trd')):
            image = archive.read(member)
            assert len(image) == 655360
            allocated = bytearray(len(image))
            allocated[:4096] = bytes([1]) * 4096
            deleted, active = 0, 0
            special_lengths = []
            for slot in range(128):
                header = image[slot * 16:(slot + 1) * 16]
                if header[0] == 0:
                    break
                if header[0] == 1:
                    deleted += 1
                    continue
                active += 1
                start = (16 * header[15] + header[14]) * 256
                size = int.from_bytes(header[11:13], 'little')
                extent = header[13] * 256
                assert start + extent <= len(image)
                allocated[start:start + extent] = bytes([1]) * extent
                # У пяти X-записей нестандартный заголовок, поле длины не задаёт доступный логический файл.
                if size > extent:
                    assert header[8] == ord('X')
                    special_lengths.append(dict(slot=slot, name=header[:9].decode('cp866'),
                        declared_length_word=size, allocated_bytes=extent,
                        length_word_semantics_proved=False))
                content = image[start:start + min(size, extent)]
                if header[8:11] == b'XAS':
                    # XAS разобран по собственной границе текста, слово длины каталога не используется.
                    assert member == 'awk5.trd' and slot in (8, 9, 10, 11, 22, 23, 24, 27, 29)
                    continue
                rows = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n').split(b'\n')
                plain_lines = sum(bool(ASM_LINE.match(row)) for row in rows)
                extension_source = header[8] in (ord('a'), ord('t'))
                plain_source = member == 'awk4.trd' and slot in PLAIN_SLOTS
                # Проверка вручную распознанной группы, эвристика не назначает тип любым бинарным данным.
                if plain_source:
                    assert header[8] == ord('C') and plain_lines >= 8
                elif not extension_source and plain_lines:
                    assert plain_lines < 8, (member, slot, plain_lines)
                    other_candidates.append(dict(member=member, slot=slot,
                        name=header[:9].decode('cp866'), matching_lines=plain_lines,
                        classification='isolated_text_or_accidental_binary_match_not_whole_ASM_file'))
                if extension_source or plain_source:
                    assert size <= extent
                    sources.append(dict(member=member, slot=slot,
                        name=header[:9].decode('cp866'), bytes=size,
                        disk_offset=start, sha256=sha256(content).hexdigest(),
                        recognition='plain_ASM_with_C_extension' if plain_source else 'declared_a_or_t_text',
                        plain_instruction_lines=plain_lines, content=content))
            if member == 'awk5.trd':
                from ArchivedXasSources import xas_sources_from_disk
                xas, _, _ = xas_sources_from_disk(image)
                keys = ('member', 'slot', 'name', 'bytes', 'disk_offset', 'sha256',
                        'recognition', 'plain_instruction_lines', 'content')
                sources.extend({key: row[key] for key in keys} for row in xas)
            unallocated_nonzero = sum(byte != 0 and not allocated[index]
                                     for index, byte in enumerate(image))
            assert deleted == 0 and unallocated_nonzero == 0
            disks.append(dict(member=member, active_entries=active,
                deleted_entries=deleted, nonzero_bytes_outside_allocated_sectors=unallocated_nonzero,
                nonstandard_length_entries=special_lengths))
    counts = Counter(row['recognition'] for row in sources)
    assert counts == {'declared_a_or_t_text': 102, 'plain_ASM_with_C_extension': 18,
                      'XAS_9_07_tokenized': 9}
    assert len(disks) == 6 and sum(row['active_entries'] for row in disks) == 358
    return sources, disks, other_candidates


def main():
    sources, disks, other = load_sources()
    report = dict(passed=True, archive_sha256=ARCHIVE_SHA256,
        recognized_text_files=len(sources), declared_a_or_t_texts=102,
        additional_plain_ASM_with_C_extension=18, disks=disks,
        tokenized_XAS_sources=9,
        sources=[{key: value for key, value in row.items() if key != 'content'} for row in sources],
        isolated_other_format_candidates=other,
        arbitrary_other_source_encodings_excluded=False,
        semantic_equivalence_of_converted_source_versions_proved=False,
        source_text_not_proof_of_current_binary_semantics=True,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/AuthorSourceInventory.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ('sources', 'disks', 'isolated_other_format_candidates')}))


if __name__ == '__main__':
    main()
