"""Границы двух экранных ресурсов вступления, исходные данные не перекодируются."""
import re
from CheckIntro import ROOT

PREFIX = 'Source/Intro/Data/'
BITMAP = PREFIX + 'InitialScreenBitmap.bin'
ATTRIBUTES = PREFIX + 'InitialScreenAttributes.asm'
PACKED = PREFIX + 'StationScreenPacked.bin'
TAIL = 'Source/Resources/03_AWAKEN/UnknownAfterStationScreen.bin'


def render_attributes(raw):
    assert len(raw) == 768
    lines = ['                module IntroInitialScreen',
             '                ; Документация [экранные ресурсы](../../../Docs/IntroScreenResources.md)',
             '                assert $ == #8631']
    labels = {}
    for row in range(24):
        name = f'Row{row:02}'
        labels['IntroInitialScreen.' + name] = 0x8631 + 32 * row
        lines.append((name + ':').ljust(16) + 'FChooseScreenAttributes {')
        for column in range(32):
            value = raw[row*32+column]
            note = f'Column{column:02}, ink={value&7}, paper={(value>>3)&7}, bright={(value>>6)&1}, flash={value>>7}'
            code = f'                    #{value:02X}' + (',' if column < 31 else '')
            lines.append(code.ljust(80) + '; ' + note)
        lines.append('                }')
    lines += ['                assert $ == #8931', '                endmodule', '']
    return '\n'.join(lines), labels


def parse_attributes(text):
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    rows = re.findall(r'FChooseScreenAttributes\s*\{([^}]+)\}', code)
    assert len(rows) == 24
    result = b''
    for row in rows:
        values = re.findall(r'#([0-9A-F]{2})', row)
        assert len(values) == 32
        result += bytes(int(value, 16) for value in values)
    return result
