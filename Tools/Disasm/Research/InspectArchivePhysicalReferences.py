"""Обозначения открытых полей вне распознанных текстов авторского архива.

Документация: ../../../Docs/AuthorSourceInventory.md#совпадения-вне-129-распознанных-текстов
"""
from collections import Counter
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256, load_sources
from ArchivedXasSources import QUERY_NAMES
from CheckIntro import ROOT
from PackedResourceCodec import decode


def storm_reference_blocks(archive_path=ARCHIVE):
    assert sha256(archive_path.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with ZipFile(archive_path) as archive:
        disk = archive.read('awk2.trd')
    header = disk[:16]
    assert header[:9] == b'STORM   B'
    start = (header[15] * 16 + header[14]) * 256
    allocated = disk[start:start + header[13] * 256]
    result = []
    # Восстановление HR-блоков только как данных, программа STORM не исполняется.
    for offset, packed_size, restored_size in ((0x11A, 368, 646), (0x400, 16094, 20455)):
        packed = allocated[offset:offset + packed_size]
        assert packed[:2] == b'HR' and int.from_bytes(packed[4:6], 'little') == packed_size
        decoded = decode(packed)
        assert len(decoded['data']) == restored_size
        result.append(dict(member='awk2.trd', slot=0, name='STORM   B', file_offset=offset,
            packed_bytes=packed_size, restored_bytes=restored_size,
            packed_sha256=sha256(packed).hexdigest(), restored_sha256=sha256(decoded['data']).hexdigest(),
            lookahead_bytes_read=decoded['lookahead_bytes_read'], data=decoded['data'],
            decoder_is_independent_research_tool=True, restored_program_executed=False))
    return result


def main():
    sources, _, _ = load_sources()
    known = {}
    for source in sources:
        known.setdefault(source['member'], []).append((source['disk_offset'],
            source['disk_offset'] + source['bytes']))
    hits, candidate_headers = [], []
    counts = Counter()
    with ZipFile(ARCHIVE) as archive:
        members = sorted(name for name in archive.namelist() if name.endswith('.trd'))
        for member in members:
            disk = archive.read(member)
            owners = []
            for slot in range(128):
                header = disk[slot * 16:(slot + 1) * 16]
                if header[0] == 0:
                    break
                start = (header[15] * 16 + header[14]) * 256
                owner = dict(slot=slot, name=header[:9].decode('cp866'),
                    disk_offset=start, allocated_bytes=header[13] * 256,
                    declared_length_word=int.from_bytes(header[11:13], 'little'))
                owners.append(owner)
                if header[8] == ord('C') and int.from_bytes(header[9:11], 'little') == 0xC00B:
                    candidate_headers.append(dict(member=member, **owner,
                        whole_file_source_format_proved=False))
            # Поиск по всему образу, включая каталог, служебные области и хвосты секторов.
            for name in QUERY_NAMES:
                pattern = rb'(?<![A-Z0-9_])' + name.encode() + rb'(?![A-Z0-9_])'
                for match in re.finditer(pattern, disk, re.I):
                    counts[name] += 1
                    if any(low <= match.start() and match.end() <= high for low, high in known.get(member, [])):
                        continue
                    owner = next((row for row in owners if row['disk_offset'] <= match.start()
                                  < row['disk_offset'] + row['allocated_bytes']), None)
                    context_start = max(0, match.start() - 35)
                    context_end = min(len(disk), match.end() + 50)
                    if owner:
                        owner = dict(owner, file_offset=match.start() - owner['disk_offset'])
                        region = ('allocated_file_payload' if owner['file_offset'] < owner['declared_length_word']
                                  else 'allocated_file_sector_tail')
                    else:
                        region = 'catalog' if match.start() < 0x800 else 'outside_file_allocations'
                    hits.append(dict(member=member, identifier=name, disk_offset=match.start(),
                        physical_region=region, owner=owner,
                        context_disk_offset=context_start, context_hex=disk[context_start:context_end].hex(),
                        occurrence_is_not_instruction_or_memory_access_proof=True))
    assert len(hits) == 13
    blocks = storm_reference_blocks()
    report = dict(passed=True, archive_sha256=ARCHIVE_SHA256, physical_images_scanned=6,
        physical_bytes_scanned=6 * 655360, recognized_sources_excluded=len(sources),
        queried_names=list(QUERY_NAMES), all_raw_occurrence_counts=dict(counts),
        occurrences_outside_recognized_sources=hits,
        C00B_C_header_candidates=candidate_headers,
        storm_reference_blocks=[{key: value for key, value in block.items() if key != 'data'} for block in blocks],
        additional_full_source_decoding_required=True, current_field_semantics_established=False,
        numeric_compressed_or_encoded_identifiers_excluded=False,
        native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ArchivePhysicalReferencesInspection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'6 physical TRDs, {len(hits)} occurrences outside {len(sources)} recognized sources, '
          f'{len(candidate_headers)} C00B/C header candidates')


if __name__ == '__main__':
    main()
