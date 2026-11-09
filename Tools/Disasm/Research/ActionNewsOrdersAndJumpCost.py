"""Проверка исходных блоков NEWS/ORDER и отдельного байта стоимости гиперперехода."""
from PreviewSceneTables import parse as parse_records, render as render_records


NEWS_FIELDS = (
    ('State', 1, 'исходное состояние NEWS по авторской заметке, игровые коды не проверены'),
    ('Byte01', 1, 'второй исходный байт строки 1, 0, назначение неизвестно'),
    ('Word02', 2, 'первое слово нулевой пары, назначение неизвестно'),
    ('Word04', 2, 'второе слово нулевой пары, назначение неизвестно'),
    ('Byte06', 1, 'последний исходный ноль NEWS, назначение неизвестно'),
)
ORDER_FIELDS = (('Marker', 1, 'исходное значение FF из записи ORDER, проверка маркера не найдена'),) + tuple(
    (f'Byte{offset:02d}', 1, f'байт тела по смещению {offset}, игровое назначение не доказано')
    for offset in range(1, 16)
)
COST_FIELDS = (('Cost', 1, 'базовая стоимость гиперперехода, маршрут Preferred удваивает её в слове'),)
TABLES = (
    (17, 0x6000, ('ActionNewsState', 'Source/Action/Data/NewsState.asm',
                  0x3C41, 0x3C48, 'FActionNewsState', NEWS_FIELDS, ('Initial',))),
    (17, 0x6000, ('ActionDeliveryOrders', 'Source/Action/Data/DeliveryOrders.asm',
                  0x3C48, 0x3C88, 'FActionOrderRecord', ORDER_FIELDS, ('Order0', 'Order1', 'Order2', 'Order3'))),
    (17, 0x6000, ('ActionHyperJumpCost', 'Source/Action/Data/HyperJumpCost.asm',
                  0x3C8A, 0x3C8B, 'FHyperJumpCost', COST_FIELDS, ('Value',))),
)
BINDINGS = ()
REQUIRED_REPORTS = ('ActionEquipmentNotesMapping', 'ActionHyperJumpVerification', 'ActionHyperReloadVerification')
DOCUMENT = 'ActionNewsOrdersAndJumpCost'
TAG = DOCUMENT


def validate_sources(sources):
    action = sources[17]
    notes = action[0x516F:0x6000]
    news_offset = notes.index(b'NEWS:')
    order_offset = notes.index(b'ORDER:', news_offset)
    news_tokens = notes[news_offset:order_offset].rstrip(b'\r').split(b'\r')
    assert news_tokens == [b'NEWS:\x06\x87\x05g\x06\x831,0', b'\x06\x8c\x05h\x06\x830,0', b'\x06\x8c\x05g\x06\x830']
    order_tokens = notes[order_offset:].split(b'\r')[1:9]
    assert order_tokens == [b'\x06\x8c\x05g\x06\x83#FF', b'\x06\x8c\x05i\x06\x8315'] * 4
    assert action[0x3C41:0x3C48] == bytes((1, 0, 0, 0, 0, 0, 0))
    assert action[0x3C48:0x3C88] == (bytes((255,)) + bytes(15)) * 4
    assert action[0x3C88:0x3C8C] == bytes.fromhex('64 64 00 00')
    # Два чтения в перенесённом ядре имеют одинаковый абсолютный операнд.
    for address in (0x7108, 0x7127):
        offset = address - 0x6000 + 0x23D
        assert action[offset:offset + 3] == bytes.fromhex('3a 8a 9c')
    return dict(note_backed_bytes=71, news_record_bytes=7, order_records=4, order_record_bytes=16,
                hyper_jump_cost_read_sites=[0x7108, 0x7127], initial_hyper_jump_cost=0,
                covered_by_hyper_reload_9BBD_9D9D=True, known_direct_cost_writer=False,
                all_game_consumers_and_writers_proved=False)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[исходные записи и стоимость гиперперехода](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = []
    for name, fields in (('FActionNewsState', NEWS_FIELDS), ('FActionOrderRecord', ORDER_FIELDS), ('FHyperJumpCost', COST_FIELDS)):
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
