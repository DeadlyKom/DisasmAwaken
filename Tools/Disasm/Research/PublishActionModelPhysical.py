"""Публикация реальных структур OBJECT3D с сохранением промежутков и хвоста."""
from collections import Counter
import argparse
import contextlib
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify
from ActionModelPhysicalData import render, parse, structures, model_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tail', action='store_true')
    args = parser.parse_args()
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))

    proof = read('ActionModelTailVerification' if args.tail else 'ActionModelPacketsVerification')
    assert proof['passed']
    if args.tail:
        assert proof['covered_bytes'] == 1259 and proof['packet_count'] == 7
    else:
        assert proof['covered_packet_bytes'] == 9317
    data = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.sectors.bin').read_bytes()
    source_map = read('SourceMap')
    first = 0x2469 if args.tail else 0
    old = next(item for item in source_map if item['slot'] == 24 and item['offset'] == first)
    last = first + old['length']
    old_bytes = data[first:last]
    old_path = ROOT / old['path']
    assert old['kind'] == 'unclassified' and old_path.read_bytes() == old_bytes
    pending = {}
    spans = []
    symbols = read('Symbols')
    includes = []
    cursor = first

    def gap(start, end):
        path = 'Source/Resources/24_OBJECT3D/Gap' + f'{start:04X}.bin'
        raw = data[start:end]
        pending[ROOT / path] = raw
        spans.append(dict(slot=24, offset=start, length=len(raw), kind='unclassified',
                          path=path, origin=None, sha256=hashlib.sha256(raw).hexdigest()))
        includes.extend((f'                assert $ == #{start:04X}',
                         '                ; Исходный промежуток, его назначение ещё не установлено.',
                         f'                incbin "../Resources/24_OBJECT3D/Gap{start:04X}.bin"'))

    for packet in proof['packets']:
        start, end = packet['offset'], packet['end']
        if cursor < start:
            gap(cursor, start)
        path = model_path(start)
        text, labels = render(data, packet)
        decoded, parsed_labels = parse(text)
        assert decoded == data[start:end] and labels == parsed_labels
        assert not labels.keys() & symbols.keys()
        symbols.update(labels)
        pending[ROOT / path] = text.encode('utf-8')
        spans.append(dict(slot=24, offset=start, length=end - start, kind='typed_data',
                          path=path, origin=0xC000 + start, sha256=hashlib.sha256(decoded).hexdigest()))
        includes.extend((f'                assert $ == #{start:04X}', f'                disp #{0xC000 + start:04X}',
                         f'                include "../Action/Data/{Path(path).name}"', '                ent'))
        cursor = end
    if cursor < last:
        gap(cursor, last)
    includes.append(f'                assert $ == #{last:04X}')
    source_map[source_map.index(old):source_map.index(old) + 1] = spans
    inventory = read('Inventory')
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/24_OBJECT3D.inc'
    original = path.read_text(encoding='utf-8')
    if args.tail:
        needle = ('                assert $ == #2469\n'
                  '                ; Исходный промежуток, его назначение ещё не установлено.\n'
                  '                incbin "../Resources/24_OBJECT3D/Gap2469.bin"\n'
                  '                assert $ == #2954')
    else:
        needle = '                incbin "../Resources/24_OBJECT3D/Unclassified000.bin"'
    assert original.count(needle) == 1
    pending[path] = original.replace(needle, '\n'.join(includes)).replace(
        '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n', ''
    ).encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    original = path.read_text(encoding='utf-8')
    needle = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert original.count(needle) == 1
    hook = '''    # Проверка физических заголовков, групп и примитивов всех потоков OBJECT3D.
    from ActionModelPhysicalData import parse as parse_action_model
    models=[item for item in source_map if item['slot']==24 and item['kind']=='typed_data']
    assert len(models)==95 and sum(item['length'] for item in models)==9317
    for item in models:
        raw,labels=parse_action_model((ROOT/item['path']).read_text('utf-8'))
        assert raw==sources[24][item['offset']:item['offset']+item['length']]
        assert all(symbols.get(name.upper())==address for name,address in labels.items())
    assert symbols['FACTIONMODELHEADER']==2 and symbols['FACTIONMODELGROUP']==4
    assert symbols['FACTIONMODELGROUP.MASK']==0 and symbols['FACTIONMODELGROUP.COMPONENT2']==3

'''
    if args.tail:
        baseline = "    assert len(models)==95 and sum(item['length'] for item in models)==9317"
        assert original.count(baseline) == 1
        pending[path] = original.replace(baseline,
            "    assert len(models)==102 and sum(item['length'] for item in models)==10576").encode('utf-8')
        path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
        original = path.read_text(encoding='utf-8')
        needle = '    # Исходные байты подтверждённого назначения копирования, модели OBJECT3D в TRD не подставляются.'
        assert original.count(needle) == 1
        export_hook = '''    from ActionModelPhysicalData import render as render_object_model, model_path as object_model_path
    from CheckActionModelTail import read_packets as object_tail_packets
    model_report = json.loads((ROOT/'Tools/Disasm/Reports/ActionModelPacketsVerification.json').read_bytes())
    object_data = data_by_slot[24]
    for packet in model_report['packets'] + object_tail_packets(object_data,0x2469,0x2954):
        start,end=packet['offset'],packet['end']
        path=object_model_path(start)
        model_text,model_labels=render_object_model(object_data,packet)
        write(path,model_text);symbols.update(model_labels)
        special[24,start]=(end,path,0xC000+start)

'''
        pending[path] = original.replace(needle, export_hook + needle).encode('utf-8')
    else:
        pending[path] = original.replace(needle, hook + needle).encode('utf-8')
        path = ROOT / 'Includes/Structs/Include.inc'
        original = path.read_text(encoding='utf-8')
        assert original.count('                endif') == 1 and 'struct FActionModelHeader' not in original
        pending[path] = original.replace('                endif',
                                        structures() + '\n                endif').encode('utf-8')
    tag = 'ActionModelPhysicalTail' if args.tail else 'ActionModelPhysical'
    publish_scoped(pending, {old_path: old_bytes}, tag)
    print(f"OBJECT3D: {len(proof['packets'])} потоков, {sum(p['end']-p['offset'] for p in proof['packets'])} байтов физических структур")


def publish_scoped(pending, removed, tag):
    for path, raw in removed.items():
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == raw
    candidate = ROOT / 'Tools/Disasm/Research/Candidates' / tag
    history = ROOT / 'Tools/Disasm/Research/History' / ('Before' + tag)
    assert not candidate.exists() and not history.exists()
    originals = {path: path.read_bytes() if path.exists() else None for path in (*pending, *removed)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, before in originals.items():
        assert path.read_bytes() == before if before is not None else not path.exists()
        if before is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        importlib.reload(sys.modules['VerifySources']).main()
    for path, raw in removed.items():
        assert path.read_bytes() == raw == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()


if __name__ == '__main__':
    main()
