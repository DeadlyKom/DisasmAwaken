"""Переменная часть десяти моделей предпросмотра после групп вершин."""
from collections import Counter
import json

from ActionModelPhysicalData import parse as parse_records
from CheckIntro import ROOT
from PreviewModelGroupTables import tables as model_groups


def tables(data):
    groups = model_groups(data)
    streams = []
    for index, model in enumerate(groups):
        start = model['end']
        end = groups[index + 1]['start'] if index + 1 < len(groups) else 0x3581
        count = sum(values[0].bit_count() for _, values in model['groups'])
        cursor = start
        records = []
        while cursor < end and data[cursor]:
            header = data[cursor]
            line = bool(header & 128)
            size = header & 15
            assert size >= (2 if line else 3) and (line or (header >> 4) <= 4)
            following = cursor + size + 1
            assert following < end
            assert all(value % 5 == 0 and value // 5 < count for value in data[cursor + 1:following])
            records.append(dict(offset=cursor, size=size, header=header, line=line))
            cursor = following
        assert records and cursor + 1 == end and data[cursor] == 0
        name = model['name']
        streams.append(dict(name=name, start=start, end=end, records=records, vertices=count,
                            module='PreviewPrimitives' + name,
                            path='Source/D3D/Data/ModelPrimitives/' + name + '.asm'))
    return streams


def parse(text, stream):
    raw, labels = parse_records(text.replace('module ' + stream['module'], 'module ActionModels'))
    return raw, {name.replace('ActionModels.', stream['module'] + '.', 1): address
                 for name, address in labels.items()}


def render(data, stream):
    start = stream['start']
    end = stream['end']
    lines = ['                module ' + stream['module'],
             '                ; Документация [грани и линии моделей](../../../../Docs/PreviewModelPrimitiveStreams.md)',
             f'                assert $ == #{0xC000 + start:04X}']
    labels = {}
    for index, record in enumerate(stream['records']):
        name = f'Primitive{index:02X}'
        offset, size = record['offset'], record['size']
        labels[stream['module'] + '.' + name] = 0xC000 + offset
        lines.append((name + ':').ljust(16) + f'FActionModelPrimitive{size} {{')
        header = 'Header, код линии и число точек' if record['line'] else 'Header, режим заполнения и число точек'
        fields = (header, *(f'Vertex{i}, байтовое смещение точки на странице C6' for i in range(size)))
        for number, (value, field) in enumerate(zip(data[offset:offset + size + 1], fields)):
            code = f'                    #{value:02X}' + (',' if number < size else '')
            lines.append(code.ljust(80) + '; ' + field)
        lines.append('                }')
    lines.extend(('                db #00'.ljust(80) + '; нулевой заголовок завершает поток',
                  f'                assert $ == #{0xC000 + end:04X}', '                endmodule', ''))
    text = '\n'.join(lines)
    assert parse(text, stream) == (data[start:end], labels)
    return text, labels


def check(data, frame_report):
    streams = tables(data)
    assert len(streams) == 10
    assert frame_report['all_13_headers_consumed_by_face_parsers'] and frame_report['all_cases_returned']
    sizes = Counter()
    headers = {}
    for stream in streams:
        render(data, stream)
        for record in stream['records']:
            headers[record['offset'] + 0xC000] = record
            sizes['lines' if record['line'] else 'faces'] += 1
    for address in (0xF0F0, 0xF382, 0xF434, 0xF4C4, 0xF144, 0xF266, 0xF31A):
        assert headers[address]['size'] == 4 and not headers[address]['line']
    for address in (0xF2B7, 0xF544, 0xF548, 0xF2BB, 0xF1BE, 0xF1DB):
        assert headers[address]['size'] == 3 and not headers[address]['line']
    assert sizes == {'faces': 219, 'lines': 4}
    return dict(passed=True, stream_count=len(streams), **sizes,
                physical_bytes=sum(s['end'] - s['start'] for s in streams),
                verified_mutated_headers=13, vertex_bounds_checked=True,
                original_bytes_round_trip=True, assembly_executed=False, native_execution=False)


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    report = check((ROOT / 'Tools/Disasm/Extracted/Active/06_D3D.C.bin').read_bytes(),
                   json.loads((reports / 'D3DFrameProbe.json').read_bytes()))
    output = json.dumps(report, indent=2) + '\n'
    (reports / 'PreviewModelPrimitiveStreamsVerification.json').write_text(output, 'utf-8')
    print(output, end='')
