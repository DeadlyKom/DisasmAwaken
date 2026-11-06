"""Три физические фазы по 9B12..9B14, те же поля вложены в runtime-снимок."""
PATH = 'Source/Action/Data/RenderPhases.asm'
FIELDS = ('Phase0', 'Phase1', 'Phase2')


def structure_text():
    lines = ['', '                ; Три физических байтовых фазы исходной синусоиды, оборот равен 256', '                struct FRenderPhases']
    for index, field in enumerate(FIELDS):
        lines.append((field.ljust(16) + 'db #00').ljust(80) + '; фаза ' + str(index) + ', индекс страницы синусоиды')
    return '\n'.join(lines + ['                ends', '                assert FRenderPhases == #03',
        '                assert FRenderPhases.Phase0 == #00', '                assert FRenderPhases.Phase1 == #01',
        '                assert FRenderPhases.Phase2 == #02', ''])


def render(source):
    values = source[0x3B12:0x3B15]
    assert len(values) == 3
    lines = ['                module ActionRenderPhases',
             '                ; Документация [фазы коэффициентов](../../../Docs/ActionRenderCoefficients.md)',
             '                assert $ == #9B12', 'Value:          FRenderPhases {']
    for index, field in enumerate(FIELDS):
        lines.append(('                    #' + format(values[index], '02X') + (',' if index < 2 else '')).ljust(80) + '; ' + field + ', исходная байтовая фаза')
    lines += ['                }', '                assert $ == #9B15', '                endmodule']
    labels = {'ActionRenderPhases.Value': 0x9B12}
    labels.update({'ActionRenderPhases.Value.' + field: 0x9B12 + index for index, field in enumerate(FIELDS)})
    return '\n'.join(lines) + '\n', labels


def parse(text):
    import re
    clean = [line.partition(';')[0].rstrip() for line in text.splitlines() if line.partition(';')[0].strip()]
    assert clean[:3] == ['                module ActionRenderPhases', '                assert $ == #9B12', 'Value:          FRenderPhases {']
    assert len(clean) == 9 and clean[6:] == ['                }', '                assert $ == #9B15', '                endmodule']
    for index in range(3):
        assert re.fullmatch(r'\s+#[0-9A-F]{2}' + (',' if index < 2 else ''), clean[3 + index])
    raw = bytes(int(clean[i].strip().removesuffix(',')[1:], 16) for i in (3, 4, 5))
    labels = {'ActionRenderPhases.Value': 0x9B12}
    labels.update({'ActionRenderPhases.Value.' + field: 0x9B12 + index for index, field in enumerate(FIELDS)})
    return raw, labels
