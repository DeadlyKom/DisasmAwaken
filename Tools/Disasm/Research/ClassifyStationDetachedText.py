"""Физические границы двух потоков CP866, штатные потребители пока не установлены."""
from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x80E4, 0x8262, 'Source/Station/Resources/SubscriberSystemRows.bin', 'CP866_SUBSCRIBER_SYSTEM_ROWS',
     'заголовок и 16 строк абонентов с разделителем второй колонки 02'),
    (0x9066, 0x90B2, 'Source/Station/Resources/FuelAndDeliveryLabels.bin', 'CP866_FUEL_AND_DELIVERY_LABELS',
     'подпись топлива и заголовок доставки с кодами колонок 02..05'),
)


def validate(source):
    subscribers = source[0x80E4:0x8262].decode('cp866')
    header, body = subscribers.split('\r\r\n', 1)
    assert header == 'Имя абонента:\x02Система:'
    assert body.endswith('\r') and not body.endswith('\n')
    rows = tuple(row.split('\x02') for row in body[:-1].split('\r\n'))
    assert len(rows) == 16 and all(len(row) == 2 and all(row) for row in rows)
    assert all(ord(c) >= 32 for row in rows for column in row for c in column)
    assert rows[0] == ['Петр Грек', 'Миир'] and rows[-1] == ['Иван Ефремов', 'Ипраби']
    rebuilt = header + '\r\r\n' + '\r\n'.join('\x02'.join(row) for row in rows) + '\r'
    assert rebuilt.encode('cp866') == source[0x80E4:0x8262]

    labels = source[0x9066:0x90B2].decode('cp866')
    assert labels == ('\rТопливо СМРП\nДоставка грузов ко времени\r'
                      'Звезда:\x02Планета:\x03Вес:\x04Время:\x05Цена:\n')
    assert labels.encode('cp866') == source[0x9066:0x90B2]
    return dict(subscriber_rows=len(rows), delivery_columns=5, control_bytes_round_trip=True,
                active_consumers_proved=False)


if __name__ == '__main__':
    source = (ROOT / 'Tools/Disasm/Extracted/Active/04_STATIONF.C.bin').read_bytes()
    publish(slot=4, origin=0x6000, ranges=tuple(row[:2] for row in RESOURCES),
            resources=RESOURCES, tag='StationDetachedText', resource_module='ClassifyStationDetachedText',
            resource_name='STATION_DETACHED_TEXT', proof=validate(source))
