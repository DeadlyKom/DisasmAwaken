"""Физические поля исходного переноса в тело NEWS."""
import json

from CheckIntro import ROOT
from PreviewSceneTables import parse as parse_records, render as render_records
from SavedStateLayout import SLOTS, START


DOCUMENT = 'StationNewsTransfer'
TAG = DOCUMENT
REQUIRED_REPORTS = ('BootBankFileReadsVerification',)
BINDINGS = ()
STRUCTURE = 'FStationNewsTransfer'
FIELDS = (
    ('EndHour', 1, 'при переносе занимает байт часа окончания из авторского NEWS'),
    ('SystemWord0', 2, 'при переносе занимает первое слово системы в NEWS'),
    ('SystemWord1', 2, 'при переносе занимает второе слово системы в NEWS'),
    ('PlanetIndex', 1, 'при переносе занимает номер планеты в NEWS'),
)
TABLES = (
    (4, 0x6000, ('StationNewsTransfer', 'Source/Station/Data/NewsTransfer.asm',
                 0x38C0, 0x38C6, STRUCTURE, FIELDS, ('Initial',))),
    *((slot, 0, (name.title() + 'NewsTransfer', f'Source/Resources/{slot:02d}_{name}/NewsTransfer.asm',
                 0x85, 0x8B, STRUCTURE, FIELDS, ('Initial',)))
      for slot, name in SLOTS),
)


def validate_sources(sources):
    save_offset = 0x85
    source_offset = START - 0x6000 + save_offset
    assert (source_offset, 0x9BBD + save_offset) == (0x38C0, 0x9C42)
    initial = sources[4][source_offset:source_offset + 6]
    assert initial == bytes.fromhex('00 00 00 00 00 01')
    assert sources[17][0x3C41:0x3C48] == bytes([1]) + bytes(6)
    for slot, name in SLOTS:
        assert sources[slot][save_offset:save_offset + 6] == (bytes(6) if name == 'SAVE5' else initial)

    proof = json.loads((ROOT / 'Tools/Disasm/Reports/BootBankFileReadsVerification.json').read_bytes())
    profiles = [entry['flight_transition'] for entry in proof['intro_transitions']]
    assert proof['passed'] and len(profiles) == 2
    assert {profile['transferred_unknown_markers_injected'] for profile in profiles} == {False, True}
    for profile in profiles:
        assert profile['transferred_unknown_probe_offsets'][:6] == list(range(0x85, 0x8B))
        body = bytes.fromhex(profile['transferred_news_and_orders'])[1:7]
        assert body == bytes.fromhex(profile['transferred_unknown_probe_bytes'])[:6]
        expected = bytes.fromhex('31 42 53 64 75 86') if profile['transferred_unknown_markers_injected'] else initial
        assert body == expected and profile['news_order_accesses_in_first_64_flight_frames'] == 0
    return dict(station_address=0x98C0, action_address=0x9C42, save_offset=save_offset,
                marked_and_original_flight_profiles=len(profiles), observed_game_reads_in_first_64_frames=0,
                normal_game_field_semantics_proved=False)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[перенос тела NEWS](../../../Docs/StationNewsTransfer.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    lines = ['                struct ' + STRUCTURE]
    offset = 0
    assertions = []
    for field, width, note in FIELDS:
        declaration = 'db #00' if width == 1 else 'dw #0000'
        lines.append((field.ljust(16) + declaration).ljust(80) + '; ' + note)
        assertions.append(f'                assert {STRUCTURE}.{field} == {offset}')
        offset += width
    return '\n'.join((*lines, '                ends', f'                assert {STRUCTURE} == {offset}',
                      *assertions, ''))
