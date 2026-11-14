"""Проверка двух индексов и суммы, переносимых между станцией и полётом."""
from hashlib import sha256
import json
from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records


INDEX_FIELDS = (
    ('ShipIndex', 1, 'копия индекса корабля из состояния станции'),
    ('SkimmerIndex', 1, 'копия индекса глайдера из состояния станции'),
)
MONEY_FIELDS = (('Money', 2, 'копия суммы игрока из состояния станции'),)
TABLES = (
    (17, 0x6000, ('ActionPlayerIndices', 'Source/Action/Data/PlayerIndices.asm',
                  0x3BCB, 0x3BCD, 'FActionPlayerIndices', INDEX_FIELDS, ('Initial',))),
    (17, 0x6000, ('ActionPlayerMoney', 'Source/Action/Data/PlayerMoney.asm',
                  0x3BD0, 0x3BD2, 'FActionPlayerMoney', MONEY_FIELDS, ('Initial',))),
)
BINDINGS = ()
REQUIRED_REPORTS = ('BootBankFileReadsVerification',)
DOCUMENT = 'ActionTransferredPlayerFields'
TAG = DOCUMENT


def check_author_prefix(action):
    notes = action[0x516F:0x6000]
    lines = notes[notes.index(b'TIME:'):notes.index(b'TWRI:')].split(b'\r')
    widths = (2, 1, 1, 2, 2, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1)
    literals = []
    for line in lines:
        if line.startswith(b';') or b'\x06\x83' not in line:
            continue
        values = line.rsplit(b'\x06\x83', 1)[1].partition(b';')[0].split(b',')
        literals.extend(int(value[1:], 16) if value.startswith(b'#') else int(value) for value in values)
    assert len(literals) == len(widths)
    assert b''.join(value.to_bytes(width, 'little') for value, width in zip(literals, widths)) == action[0x3BBD:0x3BD4]
    return sum(widths)


def validate_sources(sources):
    action, station = sources[17], sources[4]
    author_prefix_bytes = check_author_prefix(action)
    assert action[0x3BCB:0x3BCD] == bytes(2)
    assert action[0x3BD0:0x3BD2] == bytes.fromhex('E8 FD')
    assert station[0x3849:0x384B] == bytes.fromhex('06 FF')
    assert station[0x384E:0x3850] == bytes.fromhex('D0 07')
    assert 0x9849 - 0x983B == 0x9BCB - 0x9BBD == 0x0E
    assert 0x984E - 0x983B == 0x9BD0 - 0x9BBD == 0x13
    report = json.loads((ROOT / 'Tools/Disasm/Reports/BootBankFileReadsVerification.json').read_bytes())
    assert report['passed']
    original = ROOT / 'Tools/Disasm/Disk/original.trd'
    assert report['disk_sha256'] == sha256(original.read_bytes()).hexdigest()
    flights = [row['flight_transition'] for row in report['intro_transitions']]
    assert len(flights) == 2 and all(row['trdos_calls_substituted'] is False for row in flights)
    assert sorted(row['station_money_transferred'] for row in flights) == [0, 0x1234]
    assert all(row['station_player_indices_transferred'] == [0, 0xFF] for row in flights)
    for row in flights:
        station_prefix = bytes.fromhex(row['source_station_player_prefix'])
        flight_prefix = bytes.fromhex(row['outbound_player_prefix'])
        assert len(station_prefix) == len(flight_prefix) == author_prefix_bytes
        assert flight_prefix == station_prefix[:2] + station_prefix[2:4][::-1] + station_prefix[4:]
        assert row['station_rank_score_transferred'] == int.from_bytes(station_prefix[0x11:0x13], 'little')
        assert row['station_tonnage_transferred'] == dict(used=station_prefix[0x15], capacity=station_prefix[0x16])
    marked = next(row for row in flights if row['transferred_unknown_markers_injected'])
    assert marked['station_rank_score_transferred'] == 0x0102
    assert bytes.fromhex(marked['outbound_player_prefix'])[2:4] == b'\x42\x37'
    assert all(row['station_context_restored'] == 481 for row in flights)
    return dict(original_action_indices=[0, 0], original_action_money=0xFDE8,
                model_flight_profiles=len(flights), author_prefix_bytes=author_prefix_bytes,
                flight_consumers_proved=False)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[перенос полей игрока](../../../Docs/' + DOCUMENT + '.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = []
    for name, fields in (('FActionPlayerIndices', INDEX_FIELDS), ('FActionPlayerMoney', MONEY_FIELDS)):
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
