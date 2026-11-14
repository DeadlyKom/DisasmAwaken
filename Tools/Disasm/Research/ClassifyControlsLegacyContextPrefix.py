"""Точные копии начальных байтов станционного состояния внутри CONTROL."""

START = 0x013B
END = 0x0148
LIMIT = 0x01BD
STATION_START = 0x383B
FORMAT = 'CONTROL_LEGACY_CONTEXT_PREFIX'

RESOURCES = (
    (START, END, 'Source/Controls/Resources/LegacyContextPrefix.bin', FORMAT,
     'Совпадающие байты счётчика и двух ключей STATIONF, потребитель CONTROL неизвестен'),
    (END, LIMIT, 'Source/Resources/23_CONTROL/Unclassified0148_01BD.bin', None,
     'Unknown, остальная часть соседнего диапазона сохраняется без классификации'),
)


def verify_prefix(control, station):
    state = station[STATION_START:STATION_START + 14]
    prefix = control[START:END]
    # Проверка двух точных частей, без байта варианта первого ключа станции.
    assert state == bytes.fromhex('22 01 10 10 38 4B F3 4A 00 38 4B F3 4A 00')
    assert prefix == state[:8] + state[9:14]
    assert state[4:8] == state[9:13] and control[START + 8] != state[8]
    return prefix


def compare_adjacent_header(control, station):
    # Сопоставление физических байтов, без вывода о формате старого счётчика ранга.
    header = control[END:END + 8]
    station_header = station[STATION_START + 14:STATION_START + 23]
    assert header == bytes.fromhex('06 FF 00 00 D0 07 00 32')
    assert station_header == bytes.fromhex('06 FF 00 05 00 D0 07 0D 32')
    pairs = ((0, 0), (1, 1), (2, 2), (4, 5), (5, 6), (7, 8))
    assert all(header[left] == station_header[right] for left, right in pairs)
    continuation = 34
    assert control[END + 8:END + 8 + continuation] == bytes(continuation)
    assert station[STATION_START + 23:STATION_START + 23 + continuation] == bytes(continuation)
    assert control[END + 8 + continuation] == 0xFF
    assert station[STATION_START + 23 + continuation] == 0
    return dict(control_header_offset=END, station_header_offset=STATION_START + 14,
                equal_byte_pairs=pairs, equal_zero_bytes_after_header=continuation,
                legacy_header_layout_proved=False, runtime_consumer_proved=False)


if __name__ == '__main__':
    from CheckStationFlightCycle import payload
    from ClassifyStationWorkspaceResources import publish

    verify_prefix(payload(23), payload(4))
    publish(slot=23, origin=0xDADE, ranges=((START, LIMIT),), resources=RESOURCES,
            tag='ControlsLegacyContextPrefix', resource_module='ClassifyControlsLegacyContextPrefix',
            resource_name='CONTROLS_LEGACY_CONTEXT_PREFIX',
            proof=dict(station_prefix_offsets=[[0, 8], [9, 14]], missing_station_variant_offset=8,
                       actual_runtime_consumer_proved=False, adjacent_record_layout_proved=False))
