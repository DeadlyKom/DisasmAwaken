"""Сохранение подтверждённого продолжения физического хвоста списка станции."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x9472, 0x9488, 'Source/Station/Resources/InitialDrawListExtendedTail.bin',
     'INITIAL_STATION_DRAW_LIST_EXTENDED_TAIL',
     '22 исходных байта, читаемых удалением последней панели после открытия исходных окон'),
    (0x9488, 0xA000, 'Source/Resources/04_STATIONF/Unclassified9488_A000.bin', None,
     'Unknown, более дальние обращения этой трассой не установлены'),
)


if __name__ == '__main__':
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/StationExpandedDrawTailVerification.json').read_bytes())
    assert proof['passed'] and proof['observed_original_tail_bytes'] == 22
    assert proof['maximum_observed_read_end'] == 0xF488 and proof['maximum_observed_write_end'] == 0xF486
    publish(slot=4, origin=0x6000, ranges=((0x9472, 0xA000),), resources=RESOURCES,
            tag='StationExpandedDrawTail', resource_module='ClassifyStationExpandedDrawTail',
            resource_name='STATION_EXPANDED_DRAW_TAIL',
            proof=dict(original_zero_bytes=22, original_shift_instruction='CB48',
                       maximum_possible_shift_extent_proved=False))
