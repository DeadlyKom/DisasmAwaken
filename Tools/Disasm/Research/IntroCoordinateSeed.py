"""Физическая начальная страница индексов координат вступления."""
import re
from CheckIntro import ROOT

PATH = 'Source/Intro/Data/CoordinateSeed.asm'


def render(data):
    assert len(data) == 256
    lines = ['                module IntroCoordinateSeed',
             '                ; Документация [исходные отсчёты и отражение](../../../Docs/IntroCoordinateSeed.md)',
             '                assert $ == #6400']
    for index, value in enumerate(data):
        text = (f'Index{index:02X}:').ljust(16) + f'FIntroCoordinateSample {{ #{value:02X} }}'
        note = 'сохранённый отсчёт половины периода' if index < 128 else (
            'исходный ноль центрального индекса, построитель его не меняет' if index == 128 else
            'исходный ноль, построитель заменяет его отражённым отсчётом')
        lines.append(text.ljust(80) + '; ' + note)
    lines.extend(('                assert $ == #6500', '                endmodule', ''))
    return '\n'.join(lines)


def parse(text):
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    rows = re.findall(r'Index([0-9A-F]{2}):\s+FIntroCoordinateSample\s*\{\s*#([0-9A-F]{2})\s*\}', code)
    assert [int(index, 16) for index, _ in rows] == list(range(256))
    return bytes(int(value, 16) for _, value in rows)
