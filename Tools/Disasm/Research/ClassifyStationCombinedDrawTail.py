"""Физические нулевые байты, до которых доходит сдвиг длинных списков станции."""

import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x9488, 0x94AC, 'Source/Station/Resources/InitialCombinedPanelShiftTail.bin',
     'INITIAL_STATION_COMBINED_PANEL_SHIFT_TAIL',
     'Исходный хвост LDIR в композиции восьми открывателей, 39 обработчиков'),
    (0x94AC, 0x94BA, 'Source/Station/Resources/InitialFullDrawListShiftTail.bin',
     'INITIAL_STATION_FULL_DRAW_LIST_SHIFT_TAIL',
     'Исходный хвост LDIR при включении всех 46 физических обработчиков в модели'),
    (0x94BA, 0xA000, 'Source/Resources/04_STATIONF/Unclassified94BA_A000.bin',
     None, 'Unknown, дальнейшие обращения не установлены'),
)


if __name__ == '__main__':
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/StationCombinedDrawTailVerification.json').read_bytes())
    assert proof['passed'] and proof['original_bytes_beyond_previous_boundary'] == 50
    assert proof['combined']['read_end_exclusive'] == 0xF4AC and proof['all_handlers']['read_end_exclusive'] == 0xF4BA
    publish(slot=4, origin=0x6000, ranges=((0x9488, 0xA000),), resources=RESOURCES,
            tag='StationCombinedDrawTail', resource_module='ClassifyStationCombinedDrawTail',
            resource_name='STATION_COMBINED_DRAW_TAIL',
            proof=dict(combined_openers=8, full_physical_handlers=46, maximum_possible_extent_proved=False))
