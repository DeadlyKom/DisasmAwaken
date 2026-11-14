"""Исходные байты после списка в пределах проверенного договора RebuildInterface."""

import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x94BA, 0x94DC, 'Source/Station/Resources/InitialConditionalRebuildShiftTail.bin',
     'INITIAL_STATION_CONDITIONAL_REBUILD_SHIFT_TAIL',
     'Исходный хвост LDIR при 47..63 указателях, штатное достижение не установлено'),
    (0x94DC, 0xA000, 'Source/Resources/04_STATIONF/Unclassified94DC_A000.bin',
     None, 'Unknown, дальнейшие обращения не установлены'),
)


if __name__ == '__main__':
    report = json.loads((ROOT / 'Tools/Disasm/Reports/StationCombinedDrawTailVerification.json').read_bytes())
    proof = report['rebuild_at_structural_limit']
    assert report['passed'] and proof['original_bytes_from_0xF4BA_read'] == 34
    assert proof['cases'][-1]['read_end_exclusive'] == 0xF4DC
    publish(slot=4, origin=0x6000, ranges=((0x94BA, 0xA000),), resources=RESOURCES,
            tag='StationRebuildShiftTail', resource_module='ClassifyStationRebuildShiftTail',
            resource_name='STATION_CONDITIONAL_REBUILD_SHIFT_TAIL',
            proof=dict(maximum_tested_entries=63, original_rebuild_executed=True,
                       original_pointers_repeated_in_model=True, natural_game_path_proved=False))
