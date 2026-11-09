"""Исходный хвост, затронутый 128-байтовыми сдвигами списка станции."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x93F4, 0x9472, 'Source/Station/Resources/InitialDrawListShiftTail.bin',
     'INITIAL_STATION_DRAW_LIST_SHIFT_TAIL',
     '126 исходных байтов хвоста, затронутых сдвигами списка рисователей'),
    (0x9472, 0xA000, 'Source/Resources/04_STATIONF/Unclassified9472_A000.bin', None,
     'Unknown, более дальние обращения хвоста этой трассой не установлены'),
)


if __name__ == '__main__':
    report = ROOT / 'Tools/Disasm/Reports/InitialZeroTailAccesses.json'
    proof = json.loads(report.read_bytes())
    station = proof['regions']['station']
    assert proof['passed'] and station['frame_entries'] == 8
    assert [int(address, 16) for address in station['first_accesses']] == list(range(0xF3F4, 0xF472))
    assert {row['pc'] for row in station['accesses']} == {'9CEF', '9D02'}
    assert all(row['value'] == 0 for row in station['first_accesses'].values())
    publish(slot=4, origin=0x6000, ranges=((0x93F4, 0xA000),), resources=RESOURCES,
            tag='StationDrawListTail', resource_module='ClassifyStationDrawListTail',
            resource_name='STATION_DRAW_LIST_SHIFT_TAIL',
            proof=dict(original_zero_bytes=126, original_shift_instructions=['9CEF', '9D02'],
                       maximum_possible_shift_extent_proved=False))
