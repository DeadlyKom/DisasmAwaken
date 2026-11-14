"""Авторские подписи CNKR/CNSK, все физические записи и границы именованных потребителей."""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckStationFlightCycle import ROOT, DISK, payload
from ArchivedSourceInventory import load_sources


def parse_rows(lines):
    result = []
    pattern = re.compile(rb'\s*(?:\x06[\x80-\x8c])?\x05g(\d+):\x05h(\d+):\x05g(\d+),(\d+)')
    for line in lines:
        match = pattern.fullmatch(line)
        if match:
            capacity, price, speed, last = map(int, match.groups())
            result.append(dict(capacity=capacity, price=price, speed=speed, last=last))
    return result


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        _, source, _ = read_entry(archive.read('awk6.trd'), b'DATA_M  a')
        lines = source.split(b'\r')
        ship, skimmer = lines.index(b'CNKR'), lines.index(b'CNSK')
        # Проверка авторских подписей отдельно от интерпретации числовых строк.
        assert lines[ship + 1].decode('cp866') == 'ТОНАЖ, ЦЕНА, СКОРОСТЬ'
        assert lines[ship + 2].decode('cp866') == 'СТАТУС КОРАБЛЕЙ 1-ЛЕГАЛЬНЫЙ,0-НЕТ'
        assert lines[skimmer + 1].decode('cp866') == 'ТОНАЖ, ЦЕНА, СКОРОСТЬ, ВЕС СКИММЕРОВ'
        assert 'НЕЛЕГАЛЬНЫЙ КОРАБЛЬ, НЕ ПРОДАВАЕМЫЙ'.encode('cp866') in lines[ship:skimmer]
        ships, skimmers = parse_rows(lines[ship:skimmer]), parse_rows(lines[skimmer:skimmer + 6])
        assert len(ships) == 7 and len(skimmers) == 4
        references = []
        sources, _, _ = load_sources()
        checked = len(sources)
        for text in sources:
            for number, line in enumerate(text['content'].split(b'\r'), 1):
                if re.search(rb'(?<![A-Z0-9_])(CNKR|CNSK)(?![A-Z0-9_])', line, re.I):
                    references.append(dict(member=text['member'], slot=text['slot'], line=number, raw_hex=line.hex()))
    # Сверка всех исходных байтов, а не только совпадений первых записей.
    station = payload(4)
    for address, records in ((0x9802, ships), (0x9825, skimmers)):
        raw = b''.join(bytes([row['capacity']]) + row['price'].to_bytes(2, 'little')
                       + bytes([row['speed'], row['last']]) for row in records)
        assert raw == station[address - 0x6000:address - 0x6000 + len(raw)]
    assert checked == 129 and len(references) == 8
    assert [(row['slot'], row['line']) for row in references] == [
        (48, 1034), (48, 1048), (48, 1061), (48, 1065), (48, 1069), (48, 1580), (56, 689), (56, 700)]
    assert {row['member'] for row in references} == {'awk6.trd'}
    uses = []
    for row in references:
        if row['slot'] != 48:
            continue
        match = re.search(rb'(CNKR|CNSK)(?:\+(\d+))?$', bytes.fromhex(row['raw_hex']))
        assert match
        uses.append((match[1].decode('ascii'), int(match[2] or b'0')))
    assert uses == [('CNKR', 1), ('CNKR', 0), ('CNKR', 4), ('CNSK', 1), ('CNSK', 4), ('CNSK', 4)]
    report = dict(passed=True, archive_sha256=digest, original_disk_sha256=sha256(DISK).hexdigest(),
        archived_source='awk6.trd:DATA_M.a', current_ship_start=0x9802, current_skimmer_start=0x9825,
        matched_bytes=55, ship_records=ships, skimmer_records=skimmers,
        declared_fields=['tonnage', 'price_word', 'speed', 'ship_legality_or_skimmer_weight'],
        active_archived_source_entries_checked=checked, identifier_references=references,
        named_archived_accessors_use_only_offsets=[0, 1, 4],
        numeric_or_aliased_references_excluded=False,
        current_ship_speed_consumer_proved=False, current_skimmer_speed_consumer_proved=False,
        current_skimmer_tonnage_consumer_proved=False, current_speed_units_proved=False,
        current_ship_sale_zero_branch_previously_proved=True,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchivedTransportTradeFieldsVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Подписи и все 55 байтов CNKR/CNSK совпали, просмотрены 129 распознанных текстов.')


if __name__ == '__main__':
    main()
