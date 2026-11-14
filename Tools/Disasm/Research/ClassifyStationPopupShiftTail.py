"""Два исходных байта, читаемые при удалении 64-го указателя списка."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x94DC, 0x94DE, 'Source/Station/Resources/InitialConditionalPopupShiftTail.bin',
     'INITIAL_STATION_CONDITIONAL_POPUP_SHIFT_TAIL', 'Хвост чтения удаления 64-го указателя, штатная длина не установлена'),
    (0x94DE, 0xA000, 'Source/Resources/04_STATIONF/Unclassified94DE_A000.bin',
     None, 'Unknown, назначение дальнейшего нулевого диапазона не установлено'),
)


if __name__ == '__main__':
    report = json.loads((ROOT / 'Tools/Disasm/Reports/StationCombinedDrawTailVerification.json').read_bytes())
    popup = report['popup_removal_at_structural_limit']
    assert report['passed'] and popup['original_popup_filter_and_removal_executed']
    assert popup['cases'][-1] == dict(entries=64, popup_index=40, end_marker_preserved=True,
                                     read_end_exclusive=0xF4DE, write_end_exclusive=0xF4DC)
    assert not popup['normal_game_list_proved']
    publish(slot=4, origin=0x6000, ranges=((0x94DC, 0xA000),), resources=RESOURCES,
            tag='StationPopupShiftTail', resource_module='ClassifyStationPopupShiftTail',
            resource_name='STATION_POPUP_SHIFT_TAIL',
            proof=dict(popup_index=40, entries=64, physical_read_start=0xF4DC,
                       physical_read_end_exclusive=0xF4DE, normal_game_reachability_proved=False))
