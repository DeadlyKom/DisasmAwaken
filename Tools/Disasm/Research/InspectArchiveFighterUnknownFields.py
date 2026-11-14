"""Прямые и индексированные обращения к двум исходным байтам записей бойцов."""
from hashlib import sha256
import json
import re

from CheckArchiveEngineSource import ARCHIVE, DISK_OFFSET, ORIGIN, PHYSICAL_SIZE, ROOT, compare_source


def inspect_scene_fields():
    """Проверка прямых обращений к SourceRows и Unknown0B записи сцены."""
    raw = (ARCHIVE / '46_ENGINE.C.sectors.bin').read_bytes()
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert raw == disk[DISK_OFFSET:DISK_OFFSET + PHYSICAL_SIZE]
    instructions = []
    count, structured = compare_source(raw, instructions_out=instructions)
    watched = {0x4A51, 0x4A52, 0x4A56}
    matches = []
    for pc, operation in instructions:
        if re.match(r'(?:IN(?:[A-Z],)?|OUT)\(', operation):
            continue
        for match in re.finditer(r'\(#([0-9A-F]+)\)', operation):
            target = int(match[1], 16)
            pair = re.fullmatch(r'LD(?:(?:HL|DE|BC|SP|IX|IY),\(#[0-9A-F]+\)|\(#[0-9A-F]+\),(?:HL|DE|BC|SP|IX|IY))', operation)
            width = 2 if pair else 1
            if watched.intersection(range(target, target + width)):
                matches.append(dict(pc=pc, operation=operation, width=width, target=target))
    assert count == 1325 and not matches
    report = dict(passed=True, original_engine_sha256=sha256(raw).hexdigest(), original_disk_offset=DISK_OFFSET,
        original_physical_bytes_matched=True, registered_instructions=count, structured_source_bytes=structured,
        source_rows_address=0x4A51,
        source_rows_original=int.from_bytes(raw[0x4A51 - ORIGIN:0x4A53 - ORIGIN], 'little'),
        unknown_byte_address=0x4A56, unknown_byte_original=raw[0x4A56 - ORIGIN],
        direct_byte_and_word_accesses=matches, indirect_indexed_mutable_or_generated_accesses_excluded=False,
        global_unusedness_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveSceneUnknownFieldsInspection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    raw = (ARCHIVE / '46_ENGINE.C.sectors.bin').read_bytes()
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert raw == disk[DISK_OFFSET:DISK_OFFSET + PHYSICAL_SIZE]
    instructions = []
    count, structured = compare_source(raw, instructions_out=instructions)
    assert count == len(instructions) == 1325
    watched = {base + offset for base in (0x4842, 0x4895) for offset in (8, 10)}
    assert all(raw[address - ORIGIN] == 0 for address in watched)
    direct, indexed, unresolved_indirect, block = [], [], [], []
    for address, operation in instructions:
        row = dict(pc=address, operation=operation)
        is_port_io = bool(re.match(r'(?:IN(?:[A-Z],)?|OUT)\(', operation))
        if operation in ('LDI', 'LDIR', 'LDD', 'LDDR', 'CPI', 'CPIR', 'CPD', 'CPDR',
                         'RLD', 'RRD', 'INI', 'INIR', 'IND', 'INDR', 'OUTI', 'OTIR', 'OUTD', 'OTDR'):
            block.append(row)
        if re.search(r'\((?:HL|DE|BC|SP)\)', operation) and not is_port_io:
            unresolved_indirect.append(row)
        for match in re.finditer(r'\((IX|IY)\+#([0-9A-F]+)\)', operation):
            if int(match[2], 16) in (8, 10):
                indexed.append(row | dict(index_register=match[1], displacement=int(match[2], 16)))
        if is_port_io:
            continue
        for match in re.finditer(r'\(#([0-9A-F]+)\)', operation):
            target = int(match[1], 16)
            pair_load = re.fullmatch(r'LD(HL|DE|BC|SP|IX|IY),\(#[0-9A-F]+\)', operation)
            pair_store = re.fullmatch(r'LD\(#[0-9A-F]+\),(HL|DE|BC|SP|IX|IY)', operation)
            width = 2 if pair_load or pair_store else 1
            touched = watched.intersection(range(target, target + width))
            if touched:
                direct.append(row | dict(target=target, width=width, watched_bytes=sorted(touched)))
    assert not direct and not indexed
    report = dict(passed=True, original_engine_sha256=sha256(raw).hexdigest(),
                  inspected_registered_instructions=count, structured_source_bytes=structured,
                  fighter_bases=[0x4842, 0x4895], field_offsets=[8, 10],
                  original_zero_byte_addresses=sorted(watched),
                  direct_byte_and_word_accesses=direct, indexed_displacement_accesses=indexed,
                  indexed_exclusion_requires_index_at_record_base=True,
                  unresolved_other_indirect_operations=unresolved_indirect, block_operations=block,
                  mutable_displacements_and_other_index_bases_excluded=False,
                  global_unusedness_proved=False, padding_or_word_high_part_proved=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveFighterUnknownFieldsInspection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('1325 инструкций ENGINE, прямых или исходных индексных обращений к +08/+0A нет.')


if __name__ == '__main__':
    main()
