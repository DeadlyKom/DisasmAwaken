"""Сверка физической таблицы JLIST, имена взяты из DATA_M и BLOCK2."""
import re


START = 0x3762
END = 0x3802
ORIGIN = 0x9762
PATH = 'Source/Station/Data/ArchivedJobList.asm'
FIELDS = (
    ('DestKeyFirst', 2, 'первое слово ключа доставки'),
    ('DestKeySecond', 2, 'второе слово ключа доставки'),
    ('DeadlineDay', 2, 'день окончания срока'),
    ('DeadlineTime', 2, 'вторая пара байтов срока'),
    ('CreatedDay', 2, 'день создания'),
    ('CreatedTime', 2, 'вторая пара байтов времени создания'),
    ('Payment', 2, 'сумма оплаты'),
    ('WeightFlags', 1, 'биты 6..0, вес, бит 7, миссия принята'),
    ('Planet', 1, 'номер планеты назначения'),
)


def layout_symbols():
    result = {'FArchivedStationJob': 16}
    offset = 0
    for name, width, _ in FIELDS:
        result[f'FArchivedStationJob.{name}'] = offset
        offset += width
    assert offset == 16
    result.update({f'StationArchivedJobs.Job{i:02}': ORIGIN + 16 * i for i in range(10)})
    return result


def render(raw):
    assert len(raw) == 160
    lines = ['                module StationArchivedJobs',
             '                ; Документация [источник и физические поля](../../../Docs/StationArchivedJobs.md)',
             '                assert $ == #9762']
    for index in range(10):
        lines.append(f'Job{index:02}:'.ljust(16) + 'FArchivedStationJob {')
        cursor = 16 * index
        for field, width, note in FIELDS:
            value = int.from_bytes(raw[cursor:cursor + width], 'little')
            cursor += width
            comma = ',' if field != 'Planet' else ''
            line = f'                    #{value:0{2 * width}X}{comma}'
            lines.append(line.ljust(80) + f'; {field}, {note}')
        lines.append('                }')
    lines += ['                assert $ == #9802', '                endmodule', '']
    return '\n'.join(lines)


def parse(text):
    code = '\n'.join(line.split(';', 1)[0] for line in text.splitlines())
    records = re.findall(r'(?m)^(Job\d{2}):\s+FArchivedStationJob\s*\{([^}]+)\}', code)
    assert [name for name, _ in records] == [f'Job{index:02}' for index in range(10)]
    data = bytearray()
    for _, body in records:
        literals = re.findall(r'#([0-9A-F]+)', body)
        assert [len(value) for value in literals] == [width * 2 for _, width, _ in FIELDS]
        for value, (_, width, _) in zip(literals, FIELDS):
            data.extend(int(value, 16).to_bytes(width, 'little'))
    return bytes(data)
