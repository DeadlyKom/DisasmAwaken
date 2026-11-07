"""Фазовые значки прицела и исходная синусоида предпросмотра, точные физические байты."""
import re
from CheckIntro import ROOT
from SavedStateLayout import parse as parse_records, structures

TABLES = (
    (6, 0x400, 0xC400, 256, 'PreviewSineTable', 'Source/D3D/Data/SineTable.asm', 'FFixedSineValue'),
    (23, 0x1030, 0xEB0E, 256, 'ControlsOverlayGlyphs', 'Source/Controls/Data/OverlayGlyphs.asm', 'FOverlayGlyphPhase'),
)


def render(table, data):
    slot, offset, origin, size, module, path, kind = table
    fields = ('Value',) if slot == 6 else tuple(f'Row{row}{side}' for row in range(8) for side in ('Left', 'Right'))
    labels = {}
    lines = ['                module ' + module,
             '                ; Документация [таблицы проекции](../../../Docs/OverlayPreviewTables.md)',
             f'                assert $ == #{origin:04X}']
    step = len(fields)
    for position in range(0, size, step):
        label = f'Angle{position:02X}' if slot == 6 else ('Normal' if position < 128 else 'Selected') + str((position % 128) // 16)
        labels[label] = origin + position
        lines.append((label + ':').ljust(16) + kind + ' {')
        for index, field in enumerate(fields):
            text = f'                    #{data[position + index]:02X}' + (',' if index + 1 < step else '')
            lines.append(text.ljust(80) + '; ' + kind + '.' + field + ', исходный байт')
        lines.append('                }')
    lines.extend((f'                assert $ == #{origin + size:04X}', '                endmodule', ''))
    return '\n'.join(lines), labels


def parse(text):
    return parse_records(text, structures())


def verify_originals():
    sine = (ROOT / 'Tools/Disasm/Extracted/Active/06_D3D.C.bin').read_bytes()[0x400:0x500]
    action = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()[0x3900:0x3A00]
    assert sine == action
    glyphs = (ROOT / 'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()[0x1030:0x1130]
    # Проверка восьми подбайтовых фаз каждой формы с точным переносом между левой и правой колонками.
    for base in (0, 128):
        for phase in range(8):
            for row in range(8):
                original = int.from_bytes(glyphs[base + row * 2:base + row * 2 + 2], 'big')
                shifted = int.from_bytes(glyphs[base + phase * 16 + row * 2:base + phase * 16 + row * 2 + 2], 'big')
                assert shifted == original >> phase
    assert glyphs[:16] == bytes.fromhex('ff00810081008100810081008100ff00')
    assert glyphs[128:144] == bytes.fromhex('10002800440082004400280010000000')
    return sine, glyphs


def name_operands(region, address, operation):
    if (region, address) == ('Controls', 0xE97A):
        return operation.replace('LD DE, #EB0E', 'LD DE, @ControlsOverlayGlyphs.Normal0')
    return operation
