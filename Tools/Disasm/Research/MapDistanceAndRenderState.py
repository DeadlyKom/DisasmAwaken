"""Физические поля переноса станция–полёт и подтверждённые рабочие значения рендера."""
from PreviewSceneTables import parse as parse_records, render as render_records
from SavedStateLayout import SLOTS as SAVE_SLOTS


DISTANCE_FIELDS = (('Value', 1, 'результат MeasureCoordinateDistance, FF при переполнении'),)
COUNTER_FIELDS = (('Count', 1, 'байтовый счётчик, станционный переход условно прибавляет 30'),)
RENDER_FIELDS = (
    ('InputX', 2, 'первое исходное слово текущего объекта до допуска по старшему байту'),
    ('InputY', 2, 'второе исходное слово после допуска X, до допуска Y'),
    ('InputDepth', 2, 'третье исходное слово после допуска Y, до допуска глубины'),
)
BODY_FIELDS = (('Mode', 1, 'режим малого рисователя, поддерживаются полные коды 0..3'),)
SAVE_FIELDS = (
    (0xCB, 'TransitionCounter', 'FTransitionCounter', COUNTER_FIELDS, 'Value'),
    (0xCD, 'MeasuredDistance', 'FMeasuredDistance', DISTANCE_FIELDS, 'State'),
)
TABLES = (
    (4, 0x6000, ('StationTransitionCounter', 'Source/Station/Data/TransitionCounter.asm',
                 0x3906, 0x3907, 'FTransitionCounter', COUNTER_FIELDS, ('Value',))),
    (4, 0x6000, ('StationMeasuredDistance', 'Source/Station/Data/MeasuredDistance.asm',
                 0x3908, 0x3909, 'FMeasuredDistance', DISTANCE_FIELDS, ('State',))),
    (17, 0x6000, ('ActionTransitionCounter', 'Source/Action/Data/TransitionCounter.asm',
                  0x3C88, 0x3C89, 'FTransitionCounter', COUNTER_FIELDS, ('Value',))),
    (17, 0x6000, ('ActionRenderInputSnapshot', 'Source/Action/Data/RenderInputSnapshot.asm',
                  0x3B8F, 0x3B95, 'FRenderInputSnapshot', RENDER_FIELDS, ('Value',))),
    (22, 0xC000, ('ControlsBodyDrawMode', 'Source/Controls/Data/BodyDrawMode.asm',
                  0x0EF9, 0x0EFA, 'FBodyDrawMode', BODY_FIELDS, ('Value',))),
) + tuple(
    (slot, 0, (name.title() + stem, f'Source/Resources/{slot:02d}_{name}/{stem}.asm',
               offset, offset + 1, structure, fields, (label,)))
    for slot, name in SAVE_SLOTS for offset, stem, structure, fields, label in SAVE_FIELDS
)
BINDINGS = (
    ('MapState', 'LastDistance', 0x9908, 'StationMeasuredDistance.State.Value'),
    ('ControlsSmallBodiesState', 'Mode', 0xCEF9, 'ControlsBodyDrawMode.Value.Mode'),
)
REQUIRED_REPORTS = ('StationHyperJumpCostTransferVerification', 'ActionObjectProjectionScanVerification',
                    'ProjectedBodyEntryVerification', 'ControlsSmallBodiesVerification')
DOCUMENT = 'MapDistanceAndRenderState'
TAG = DOCUMENT


def name_operands(region, address, operation):
    if (region, address) == ('Station', 0x7E53):
        return operation.replace('(#9906)', '(@StationTransitionCounter.Value.Count)')
    if (region, address) == ('Action', 0xE020):
        for pointer, field in (('9B8F', 'InputX'), ('9B91', 'InputY'), ('9B93', 'InputDepth')):
            operation = operation.replace('(#' + pointer + ')', '(@ActionRenderInputSnapshot.Value.' + field + ')')
    return operation


def validate_sources(sources):
    assert sources[4][0x3906:0x390A] == bytes.fromhex('64 00 00 00')
    assert sources[17][0x3C88:0x3C8C] == bytes.fromhex('64 64 00 00')
    assert sources[17][0x3B8F:0x3B95] == bytes(6)
    assert sources[22][0x0EF9:0x0EFA] == bytes(1)
    for slot, name in SAVE_SLOTS:
        assert sources[slot][0xCB:0xCF] == (bytes(4) if name == 'SAVE5' else bytes.fromhex('64 00 00 00'))
    assert 0x9906 - 0x983B == 0x9C88 - 0x9BBD == 0xCB
    assert 0x9908 - 0x983B == 0x9C8A - 0x9BBD == 0xCD
    for slot, offset, hex_bytes in ((4, 0x1E7E + 0x2AC, '3a 06 99'),
                                    (4, 0x1E83 + 0x2AC, '32 06 99'),
                                    (7, 0x2830, '32 08 99'),
                                    (17, 0x80F3, '22 8f 9b'),
                                    (17, 0x8105, '22 91 9b'),
                                    (17, 0x8117, '22 93 9b'),
                                    (22, 0x0EFF, '32 f9 ce'),
                                    (22, 0x0F10, '3a f9 ce'),
                                    (22, 0x19E1, '3a f9 ce')):
        raw = bytes.fromhex(hex_bytes)
        assert sources[slot][offset:offset + len(raw)] == raw, (slot, hex(offset))
    return dict(typed_context_bytes=3, typed_save_context_bytes=12, raw_render_input_bytes=6, body_draw_mode_bytes=1,
                distance_transfer_offset=0xCD, transition_counter_transfer_offset=0xCB,
                all_render_snapshot_consumers_proved=False, action_counter_reader_proved=False)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[состояние переноса и рендера](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = []
    for name, fields in (('FMeasuredDistance', DISTANCE_FIELDS), ('FTransitionCounter', COUNTER_FIELDS),
                         ('FRenderInputSnapshot', RENDER_FIELDS), ('FBodyDrawMode', BODY_FIELDS)):
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
