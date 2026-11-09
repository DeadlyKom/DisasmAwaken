"""Копии 50-байтовых маршрутов кадров в промежутках исходных BANK."""
from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = TAG = 'BankArchiveRouteCopies'
REQUIRED_REPORTS = ('BankStripArchiveConsumerVerification',)
BINDINGS = ()
RECORD = 'FArchiveBankStripRoute'
SIZE = 50
START = 0x1E12
SOURCE_OFFSET = 0x9406F
COUNTS = {34: 2, 35: 4, 37: 8, 38: 10}
FIELDS = (
    ('BankIndex', 1, 'индекс файла BANK, которому принадлежит маршрут'),
    ('FrameCount', 1, 'число используемых кадров в каждом списке'),
    *((f'Staged{i:02}', 2, 'указатель полосы через буфер для страницы 7') for i in range(12)),
    *((f'Direct{i:02}', 2, 'указатель полосы прямого вывода в экран 4000') for i in range(12)),
)


def table(slot, count):
    name = f'Bank{slot - 33}'
    path = f'Source/Resources/{slot}_BANK{slot - 33}/ArchiveRouteCopies.asm'
    labels = tuple(f'Route{i:02}' for i in range(count))
    return slot, 0, (name + 'RouteCopies', path, START, START + count * SIZE, RECORD, FIELDS, labels)


TABLES = tuple(table(slot, count) for slot, count in COUNTS.items())


def validate_sources(sources):
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    for slot, _, row in TABLES:
        start, end = row[2:4]
        raw = sources[slot][start:end]
        assert raw == disk[SOURCE_OFFSET:SOURCE_OFFSET + end - start]
        next_route = disk[SOURCE_OFFSET + end - start:SOURCE_OFFSET + end - start + SIZE]
        assert next_route[0] == slot - 33 and sources[slot][end] == 0
        for index in range(COUNTS[slot]):
            record = raw[index * SIZE:(index + 1) * SIZE]
            bank, count = record[:2]
            assert bank == index // 2 and 0 < count <= 12
            for begin in (2, 26):
                words = [int.from_bytes(record[i:i + 2], 'little') for i in range(begin, begin + 24, 2)]
                assert all(0xC000 <= value <= 0xFFFF for value in words[:count])
                assert not any(words[count:])
    return dict(original_routes_copied=sum(COUNTS.values()), route_copy_source_disk_offset=SOURCE_OFFSET,
                runtime_read_of_bank_copies_proved=False)


def render(source, origin, entry):
    text, labels = render_records(source, entry, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[копии маршрутов кадров BANK](../../../Docs/BankArchiveRouteCopies.md)'), labels


def parse(text, origin, entry):
    return parse_records(text, entry, origin)


def structures():
    lines = ['                struct ' + RECORD]
    offset = 0
    assertions = []
    for field, width, meaning in FIELDS:
        directive = 'db #00' if width == 1 else 'dw #0000'
        lines.append(f'{field:<16}{directive:<64}; {meaning}')
        assertions.append(f'                assert {RECORD}.{field} == {offset}')
        offset += width
    assert offset == SIZE
    return '\n'.join(lines + ['                ends', f'                assert {RECORD} == {SIZE}', *assertions, ''])
