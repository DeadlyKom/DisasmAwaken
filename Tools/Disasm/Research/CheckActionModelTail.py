"""Формат семи последовательных пакетов после последней цели таблицы OBJECT3D."""
from collections import Counter
import json

from ActionModelPhysicalData import parse, render
from ActionObjectPointersData import tail_targets
from CheckIntro import ROOT


def read_packets(data, start, end):
    packets = []
    while start < end:
        assert start + 2 < end
        cursor = start + 2
        groups = []
        while data[cursor]:
            assert cursor + 4 < end
            groups.append(dict(offset=cursor, mask=data[cursor]))
            cursor += 4
        vertex_count = sum(group['mask'].bit_count() for group in groups)
        assert 0 < vertex_count <= 40
        cursor += 1
        records = []
        while cursor < end and data[cursor]:
            header = data[cursor]
            line = bool(header & 128)
            count = header & 15
            assert count >= (2 if line else 3)
            assert line or (header >> 4) <= 4
            following = cursor + 1 + count
            assert following < end
            indices = data[cursor + 1:following]
            assert all(index % 5 == 0 and index // 5 < vertex_count for index in indices)
            records.append(dict(offset=cursor, kind='line' if line else 'face', count=count))
            cursor = following
        assert records and cursor < end
        packet = dict(offset=start, end=cursor + 1, fixed_groups=groups, records=records,
                      generated_vertices=vertex_count)
        text, labels = render(data, packet)
        assert parse(text) == (data[start:cursor + 1], labels)
        packets.append(packet)
        start = cursor + 1
    assert start == end
    return packets


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    original = json.loads((reports / 'ActionModelPacketsVerification.json').read_bytes())
    assert original['passed'] and original['distinct_packets'] == 95
    data = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    start = max(packet['end'] for packet in original['packets'])
    end = len(data)
    assert (start, end) == (0x2469, 0x2954)
    packets = read_packets(data, start, end)
    assert [(p['offset'], p['end']) for p in packets] == [
        (0x2469, 0x251F), (0x251F, 0x25C1), (0x25C1, 0x266B), (0x266B, 0x2707),
        (0x2707, 0x27AB), (0x27AB, 0x2859), (0x2859, 0x2954),
    ]
    assert not {p['offset'] for p in packets} & {p['offset'] for p in original['packets']}
    originals = {data[p['offset']:p['end']] for p in original['packets']}
    assert all(data[p['offset']:p['end']] not in originals for p in packets)
    action = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    tail_words = [int.from_bytes(action[offset:offset + 2], 'little') for offset in range(0x3F00, 0x3F1C, 2)]
    assert tail_words == [address for address in tail_targets().values() for _ in range(2)]
    assert set(tail_words) == {0xC000 + packet['offset'] for packet in packets}
    count = Counter(record['kind'] for p in packets for record in p['records'])
    report = dict(passed=True, covered_bytes=end - start, packets=packets,
                  primitives=dict(count), packet_count=len(packets),
                  each_vertex_index_within_generated_count=True,
                  exact_known_model_format_round_trip=True,
                  page_9e_has_no_tail_packet_pointer=True, page_9f_pointer_count=len(tail_words),
                  actual_game_callers_proved=False,
                  assembly_executed=False, native_execution=False)
    (reports / 'ActionModelTailVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'packets'}, indent=2))


if __name__ == '__main__':
    main()
