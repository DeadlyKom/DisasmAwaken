"""Физическая двухбайтовая запись экранной точки, X перед Y."""
PATH = 'Source/Action/Data/AimPoint.asm'


def structure_text():
    return '\n'.join(('', '                ; Физическая экранная точка, X перед Y', '                struct FActionAimPoint',
        'X               db #00'.ljust(80) + '; горизонтальный экранный байт',
        'Y               db #00'.ljust(80) + '; вертикальный экранный байт',
        '                ends', '                assert FActionAimPoint == #02',
        '                assert FActionAimPoint.X == #00', '                assert FActionAimPoint.Y == #01', ''))


def render(source):
    values = source[0x3B19:0x3B1B]
    assert len(values) == 2
    lines = ['                module ActionAimPoint',
             '                ; Документация [сопровождение экранной точки](../../../Docs/ActionAimFollow.md)',
             '                assert $ == #9B19', 'Value:          FActionAimPoint {']
    for index, (field, note) in enumerate((('X', 'начальный экранный центр X'), ('Y', 'начальный экранный центр Y'))):
        lines.append(('                    #' + format(values[index], '02X') + (',' if index == 0 else '')).ljust(80) + '; ' + field + ', ' + note)
    lines += ['                }', '                assert $ == #9B1B', '                endmodule']
    return '\n'.join(lines) + '\n', {'ActionAimPoint.Value': 0x9B19, 'ActionAimPoint.Value.X': 0x9B19, 'ActionAimPoint.Value.Y': 0x9B1A}


def parse(text):
    import re
    clean = [line.partition(';')[0].rstrip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert clean[:3] == ['                module ActionAimPoint', '                assert $ == #9B19', 'Value:          FActionAimPoint {']
    assert len(clean) == 8 and clean[5:] == ['                }', '                assert $ == #9B1B', '                endmodule']
    assert re.fullmatch(r'\s+#[0-9A-F]{2},', clean[3]) and re.fullmatch(r'\s+#[0-9A-F]{2}', clean[4])
    raw = bytes(int(clean[i].strip().removesuffix(',')[1:], 16) for i in (3, 4))
    return raw, {'ActionAimPoint.Value': 0x9B19, 'ActionAimPoint.Value.X': 0x9B19, 'ActionAimPoint.Value.Y': 0x9B1A}
