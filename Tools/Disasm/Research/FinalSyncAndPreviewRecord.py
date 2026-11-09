"""Физические указатели синхронизации финала и начало исходной записи просмотра."""
from PreviewSceneTables import parse as parse_records, render as render_records


SYNC_FIELDS = (
    ('AfterRow18', 2, 'указатель вставки после восемнадцатого знакоместного ряда, установлен построителем'),
    ('AfterRow10', 2, 'указатель вставки после десятого знакоместного ряда, установлен построителем'),
)
PREVIEW_FIELDS = (
    ('First', 2, 'первая координата исходной записи, прочитана первым POP'),
    ('Second', 2, 'вторая координата исходной записи, прочитана вторым POP'),
    ('Third', 2, 'третья координата исходной записи, управление принимает значения 512..4095'),
    ('ModelOffset', 1, 'байтовое смещение пары указателей модели, устанавливается SetupPreviewModel'),
)
TABLES = (
    (29, 0x6000, ('FinalSyncPointers', 'Source/Final/Data/SyncPointers.asm',
                  0x02A5, 0x02A9, 'FFinalSyncPointers', SYNC_FIELDS, ('Value',))),
    (6, 0xC000, ('PreviewObjectHeader', 'Source/D3D/Data/PreviewObjectHeader.asm',
                 0x0DC0, 0x0DC7, 'FPreviewObjectHeader', PREVIEW_FIELDS, ('Value',))),
)
BINDINGS = (
    ('D3DPreviewState', 'ThirdCoordinate', 0xCDC4, 'PreviewObjectHeader.Value.Third'),
    ('D3DPreviewState', 'ModelOffset', 0xCDC6, 'PreviewObjectHeader.Value.ModelOffset'),
)
REQUIRED_REPORTS = ('FinalVerification', 'FinalCycleVerification', 'PreviewQueueBuildVerification',
                    'PreviewThirdVerification', 'PreviewSetupVerification')
DOCUMENT = 'FinalSyncAndPreviewRecord'
TAG = DOCUMENT


def name_operands(region, address, operation):
    if region != 'Final':
        return operation
    if address in (0x6000, 0x61DF):
        operation = operation.replace('(#62A5)', '(@FinalSyncPointers.Value.AfterRow18)')
        operation = operation.replace('(#62A7)', '(@FinalSyncPointers.Value.AfterRow10)')
    if address == 0x6000 and operation == 'CALL #8000':
        return 'CALL @FinalDisplayChainConst.GeneratedEntry'
    if address == 0x6196 and operation == 'LD HL, #8000':
        return 'LD HL, @FinalDisplayChainConst.GeneratedEntry'
    return operation


def validate_sources(sources):
    final = sources[29]
    preview = sources[6]
    assert final[0x02A5:0x02A9] == bytes(4)
    assert preview[0x0DC0:0x0DC7] == bytes.fromhex('00 00 00 00 dc 05 00')
    for address, raw in ((0x607D, '2a a7 62'), (0x608B, '2a a5 62'),
                         (0x60B6, '2a a5 62'), (0x60C4, '2a a7 62'),
                         (0x61F6, 'ed 53 a5 62'), (0x6203, 'ed 53 a7 62')):
        data = bytes.fromhex(raw)
        offset = address - 0x6000
        assert final[offset:offset + len(data)] == data
    for address, raw in ((0xECA0, '21 c0 cd'), (0xE0B5, 'ed 5b c4 cd'),
                         (0xE0C1, '22 c4 cd'), (0xE150, '32 c6 cd')):
        data = bytes.fromhex(raw)
        offset = address - 0xC000
        assert preview[offset:offset + len(data)] == data
    return dict(final_pointer_bytes=4, final_sync_read_sites=4, final_sync_write_sites=2,
                preview_header_bytes=7, preview_next_record_field_starts_at=0xCDC7,
                runtime_chain_start=0x8000, code_emitted_at_chain_start_by_assembly=False)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические поля и потребители](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = []
    for name, fields in (('FFinalSyncPointers', SYNC_FIELDS), ('FPreviewObjectHeader', PREVIEW_FIELDS)):
        lines.append('                struct ' + name)
        offset = 0
        assertions = []
        for field, width, note in fields:
            declaration = 'db #00' if width == 1 else 'dw #0000'
            lines.append((field.ljust(16) + declaration).ljust(80) + '; ' + note)
            assertions.append(f'                assert {name}.{field} == {offset}')
            offset += width
        lines.extend(('                ends', f'                assert {name} == {offset}', *assertions, ''))
    return '\n'.join(lines) + '\n'
