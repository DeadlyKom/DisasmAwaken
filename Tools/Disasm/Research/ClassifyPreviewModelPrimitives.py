"""Публикация физических граней D3D в границах исходных потоков."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json
import re

from PreviewModelPrimitiveStreams import ROOT, check, render, tables
from PublishActionModelPhysical import publish_scoped, verify


def main():
    with redirect_stdout(StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name + '.json')).read_bytes())

    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    data = (ROOT / 'Tools/Disasm/Extracted/Active/06_D3D.C.bin').read_bytes()
    proof = check(data, read('D3DFrameProbe'))
    assert proof == read('PreviewModelPrimitiveStreamsVerification')
    source_map, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    include = ROOT / 'Source/Files/06_D3D.inc'
    text = include.read_text('utf-8')
    pending, removed, physical = {}, {}, {}
    for stream in tables(data):
        start, end = stream['start'], stream['end']
        old = next(row for row in source_map if row['slot'] == 6 and row['offset'] == start)
        path = ROOT / old['path']
        raw = data[start:end]
        assert old['kind'] == 'unclassified' and path.read_bytes() == raw and old['length'] == len(raw)
        removed[path] = raw
        output, labels = render(data, stream)
        target = ROOT / stream['path']
        assert not target.exists() and not symbols.keys() & labels.keys()
        pending[target] = output.encode('utf-8')
        symbols.update(labels)
        physical.update({address: name for name, address in labels.items()})
        replacement = dict(old, kind='typed_data', path=stream['path'], origin=0xC000 + start,
                           sha256=sha256(raw).hexdigest())
        source_map[source_map.index(old)] = replacement
        needle = '                incbin "../' + old['path'][7:] + '"'
        assert text.count(needle) == 1
        text = text.replace(needle, '\n'.join((
            f'                disp #{0xC000 + start:04X}',
            '                include "../' + stream['path'][7:] + '"',
            '                ent',
        )))
    pending[include] = text.encode('utf-8')
    p = ROOT / 'Includes/Variables/Include.inc'
    text = p.read_text('utf-8')
    start = text.index('                module PreviewFaceHeaders\n')
    end = text.index('                endmodule', start)
    block = text[start:end]
    bindings = re.findall(r'(?m)^(\w+)\s+equ #([0-9A-F]{4})\s+;', block)
    assert len(bindings) == 13
    bindings = ''.join(f'                assert {name} == @{physical[int(address, 16)]}\n'
                       for name, address in bindings)
    pending[p] = (text[:end] + bindings + text[end:]).encode('utf-8')

    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in source_map))
    sizes = Counter()
    for row in source_map:
        sizes[row['kind']] += row['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for stem, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (stem + '.json')] = encode(value)

    p = ROOT / 'Tools/Disasm/VerifySources.py'
    text = p.read_text('utf-8')
    needle = '    # Проверка исходных DB свёрнутых квадратов'
    assert text.count(needle) == 1
    hook = '''    from PreviewModelPrimitiveStreams import tables as preview_streams, parse as parse_preview_stream
    for stream in preview_streams(sources[6]):
        start,end=stream['start'],stream['end']
        rows=[row for row in source_map if row['path']==stream['path']]
        assert len(rows)==1 and (rows[0]['slot'],rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(6,start,end-start,0xC000+start)
        raw,labels=parse_preview_stream((ROOT/stream['path']).read_text('utf-8'),stream)
        assert raw==sources[6][start:end] and all(symbols.get(name.upper())==address for name,address in labels.items())

'''
    pending[p] = text.replace(needle, hook + needle).encode('utf-8')
    p = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = p.read_text('utf-8')
    needle = '    # Исходный рабочий буфер проекции, экспорт на этапе исследования не запускается.'
    assert text.count(needle) == 1
    hook = '''    from PreviewModelPrimitiveStreams import tables as preview_streams, render as render_preview_stream
    for stream in preview_streams(data_by_slot[6]):
        start,end=stream['start'],stream['end']
        stream_text,stream_labels=render_preview_stream(data_by_slot[6],stream)
        write(stream['path'],stream_text);symbols.update(stream_labels)
        special[6,start]=(end,stream['path'],0xC000+start)

'''
    pending[p] = text.replace(needle, hook + needle).encode('utf-8')
    publish_scoped(pending, removed, 'PreviewModelPrimitiveStreams')
    report = dict(proof, classified=True, preserved_write_targets=len(physical) >= 13)
    (reports / 'PreviewModelPrimitiveStreamsClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
