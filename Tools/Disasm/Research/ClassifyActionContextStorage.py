"""Исходные байты назначения подтверждённого 512-байтового переноса состояния."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x3C8B, 0x3D4C, 'Source/Action/Resources/InitialTransferredContextMiddle.bin',
     'INITIAL_ACTION_CONTEXT_MIDDLE',
     'исходный диапазон внутри 512-байтового назначения переноса, до таблицы активных клавиш'),
    (0x3DA0, 0x3DBD, 'Source/Action/Resources/InitialTransferredContextTail.bin',
     'INITIAL_ACTION_CONTEXT_TAIL',
     'исходные 29 байтов назначения после последних станционных настроек'),
    (0x3DBD, 0x3E00, 'Source/Resources/17_ACTION/Unclassified3DBD_3E00.bin',
     None, 'Unknown, эти байты лежат после конца 512-байтового контекста'),
)


if __name__ == '__main__':
    path = ROOT / 'Tools/Disasm/Reports/StationHyperJumpCostTransferVerification.json'
    proof = json.loads(path.read_bytes())
    assert proof['passed'] and proof['whole_512_byte_copy_checked']
    assert proof['original_distance_arithmetic_and_both_state_copies_executed']
    base = 0x3BBD
    assert RESOURCES[1][1] == base + 512
    assert all(base <= start < end <= base + 512 for start, end, *_ in RESOURCES[:2])
    publish(slot=17, origin=0x6000, ranges=((0x3C8B, 0x3D4C), (0x3DA0, 0x3E00)),
            resources=RESOURCES, tag='ActionContextStorage', resource_module='ClassifyActionContextStorage',
            resource_name='ACTION_CONTEXT_INITIAL_STORAGE',
            proof=dict(transfer_bytes=512, station_source=0x983B, action_destination=0x9BBD,
                       unknown_neighbor_bytes=67, individual_game_fields_proved=False))
