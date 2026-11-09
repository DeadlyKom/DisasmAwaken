"""Физический хвост состояния, прямой перенос в ACTION и предел обратного переноса."""
import json

from CheckStationFlightCycle import exercise, payload, ROOT
from SavedStateLayout import SLOTS


SIZE = 29
SAVE_OFFSET = 0x1E3
STATION_OFFSET = 0x3A1E
ACTION_OFFSET = 0x3DA0
FORMAT = 'INITIAL_STATION_SAVE_TRANSFER_TRAILER'
REPORT = 'StationSaveTransferTrailerVerification'


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    slot_protocol = json.loads((reports / 'SaveSlotProtocolVerification.json').read_bytes())
    assert slot_protocol['passed'] and slot_protocol['read_write_blocks_exactly_512_bytes']
    station = payload(4)[STATION_OFFSET:STATION_OFFSET + SIZE]
    assert station == bytes(SIZE)
    for slot, _ in SLOTS:
        assert payload(slot)[SAVE_OFFSET:] == station
    marker = bytes((37 * index + 19) & 255 for index in range(SIZE))
    result = exercise(True, transfer_trailer=marker)
    assert result['trailer_forward'] == result['trailer_after_64_frames'] == marker.hex()
    assert result['trailer_in_fresh_station'] == station.hex() and result['incoming_context_bytes'] == 481
    report = dict(passed=True, trailer_size=SIZE, save_offset=SAVE_OFFSET, station_offset=STATION_OFFSET,
                  action_offset=ACTION_OFFSET, original_station_and_save_trailers=station.hex(),
                  save_slots=[slot for slot, _ in SLOTS], cycle=result, fixture_trailer=True,
                  trdos_substituted=True, gameplay_fields_proved=False,
                  assembly_executed=False, native_execution=False)
    (reports / (REPORT + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('29 байтов в STATIONF и во всех шести SAVE, перенос в ACTION и отсечение при возврате')


if __name__ == '__main__':
    main()
