"""Физическая рабочая запись, локальные назначения не заменяют разбор полного рисователя."""
import re
from PreviewSceneTables import render as render_records, parse as parse_records

FIELDS = (
    ('WorkY', 1, 'рабочее Y, исходно OffsetY, отсечённые ветви могут его менять'),
    ('WorkX', 1, 'рабочее X, исходно OffsetX, отсечённые ветви могут его менять'),
    ('CenterY', 1, 'байтовая строка центра сечения'),
    ('CenterX', 1, 'байтовая горизонтальная координата центра сечения'),
    ('SectionRadius', 1, 'результат SqrtSquareDiff для отсечённого сечения'),
    ('SavedSP', 2, 'сохранённый CPU-стек, указывает SavedAF перед внешним возвратом'),
    ('SquareDiff', 2, 'рабочее слово D*D-A*A-Carry по модулю 65536'),
    ('SavedB', 1, 'сохранённый B помощника правой маски'),
    ('Direction', 1, 'код направления строк, 0 вверх, 1 вниз, проверка различает ноль и ненулевое'),
    ('Mode', 1, 'авторский SEDETECT, прямые писатели задают 0/1, три чтения сохраняют или возвращают F от AND Mode, общий графический замысел не установлен'),
)
TABLE = ('ControlsCircleWork', 'Source/Controls/Data/CircleWork.asm', 0x1181, 0x118D,
         'FCircleRasterWork', FIELDS, ('Value',))


def render(source):
    text, symbols = render_records(source, TABLE, 0xC000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[рабочая запись большого контура](../../../Docs/ControlsCircleWork.md)'), symbols


def parse(text):
    clean = [line.partition(';')[0].strip() for line in text.splitlines()]
    clean = [line for line in clean if line]
    assert clean[:3] == ['module ControlsCircleWork', 'assert $ == #D181',
                         'Value:'.ljust(16)+'FCircleRasterWork {']
    for index, (_, width, _) in enumerate(FIELDS):
        assert re.fullmatch(r'#[0-9A-F]{'+str(2*width)+'}'+(',' if index+1<len(FIELDS) else ''), clean[index+3])
    assert clean[3+len(FIELDS):] == ['}', 'assert $ == #D18D', 'endmodule']
    return parse_records(text, TABLE, 0xC000)
