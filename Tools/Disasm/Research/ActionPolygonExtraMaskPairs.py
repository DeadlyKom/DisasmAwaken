"""Физические пары AND/OR индексов 5..7 вне перекрытых рабочих полей ACTION."""

from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'ActionPolygonExtraMaskPairs'
TAG = DOCUMENT
REQUIRED_REPORTS = ('ActionPolygonExtraMaskPairsVerification',)
BINDINGS = ()
FIELDS = (
    ('AndMask', 1, 'буквальный операнд AND краевого байта в исходном состоянии'),
    ('OrMask', 1, 'буквальный операнд OR краевого байта в исходном состоянии'),
)


def definitions():
    for parity, parity_name in enumerate(('Even', 'Odd')):
        for phase in range(8):
            for side, side_name in enumerate(('Left', 'Right')):
                start = 0x2C0A + parity * 256 + phase * 32 + side * 16
                first_mode = {0x2D2A: 7, 0x2D3A: 8, 0x2D4A: 8, 0x2D5A: 6}.get(start, 5)
                if first_mode == 8:
                    continue
                name = parity_name + side_name + str(phase)
                yield 17, 0x6000, (
                    'ActionExtraMask' + name,
                    'Source/Action/Data/PolygonExtraMasks/' + name + '.asm',
                    start + 2 * (first_mode - 5), start + 6,
                    'FPolygonLiteralEdgeMask', FIELDS,
                    tuple('Mode' + str(mode) for mode in range(first_mode, 8)),
                )


TABLES = tuple(definitions())


def validate_sources(sources):
    mask_pages = sources[17][0x2C00:0x2E00]
    assert len(mask_pages) == 512 and mask_pages == sources[6][:512] == sources[18][:512]
    overlay = sources[19][:0x2020]
    assert overlay == sources[17][0x6000:0x8020]
    assert overlay[0x110A:0x1110] == bytes.fromhex('ED 73 29 D1 31 00')
    offsets = {offset for _, _, table in TABLES for offset in range(table[2], table[3])}
    assert len(offsets) == 174
    return dict(shared_original_page_bytes=len(mask_pages), extra_mask_bytes=192,
                already_typed_overlap_bytes=17, incomplete_pair_byte_preserved=True)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[дополнительные пары AND/OR](../../../../Docs/ActionPolygonExtraMaskPairs.md)')
    return text, labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    lines = ['                struct FPolygonLiteralEdgeMask']
    lines.extend((name.ljust(16) + 'db #00').ljust(80) + '; ' + note for name, _, note in FIELDS)
    lines.extend(('                ends',
                  '                assert FPolygonLiteralEdgeMask == 2',
                  '                assert FPolygonLiteralEdgeMask.AndMask == 0',
                  '                assert FPolygonLiteralEdgeMask.OrMask == 1'))
    return '\n'.join(lines) + '\n'
