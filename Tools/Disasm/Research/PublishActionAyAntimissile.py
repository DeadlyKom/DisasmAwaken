"""Включение 16 строк противоракетного звука в существующий формат FActionAyFrame."""
from collections import Counter
import json

from ActionAyStreams import GROUPS, bounds, parse, render
from PublishActionModelPhysical import ROOT, publish_scoped


def main():
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name + '.json')).read_bytes())

    def encode(data):
        return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    playback = read('ActionAyStreamPlaybackVerification')
    assert playback['passed'] and playback['streams'] == 9 and playback['physical_frames'] == 110
    command = read('ActionAntimissileCommandVerification')
    assert command['passed']
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    name, streams = GROUPS[-1]
    first, last = bounds(streams)
    assert (first, last) == (0x8DC1, 0x8E02)
    sm, symbols, inventory = (read(stem) for stem in ('SourceMap', 'Symbols', 'Inventory'))
    old = next(row for row in sm if row['slot'] == 17 and row['offset'] == first)
    old_path = ROOT / old['path']
    assert old['kind'] == 'unclassified' and old['length'] == last - first
    raw = source[first:last]
    text, labels = render(source, streams)
    assert parse(text, streams) == (raw, labels) and not labels.keys() & symbols.keys()
    path = ROOT / name
    assert not path.exists()
    pending = {path: text.encode('utf-8')}
    sm[sm.index(old)] = dict(old, kind='typed_data', path=name, origin=0xEDC1)
    symbols.update(labels)
    inventory['ranges_by_kind'] = dict(Counter(row['kind'] for row in sm))
    inventory['physical_bytes_by_kind'] = {
        kind: sum(row['length'] for row in sm if row['kind'] == kind) for kind in inventory['ranges_by_kind']
    }
    for stem, data in (('SourceMap', sm), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (stem + '.json')] = encode(data)
    p = ROOT / 'Source/Files/17_ACTION.inc'
    text = p.read_text('utf-8')
    needle = '                incbin "../' + old['path'][7:] + '"'
    assert text.count(needle) == 1
    pending[p] = text.replace(needle, '                disp #EDC1\n'
                              '                include "../Action/Data/AyAntimissileStream.asm"\n'
                              '                ent').encode('utf-8')
    p = ROOT / 'Source/Action/ActivateAntimissileSystem.asm'
    text = p.read_text('utf-8')
    assert text.count('LD HL, #EDC1') == 1
    pending[p] = text.replace('LD HL, #EDC1', 'LD HL, @ActionAyStreams.AntimissRow00').encode('utf-8')
    publish_scoped(pending, {old_path: raw}, 'ActionAyAntimissileStream')
    result = dict(passed=True, physical_bytes=len(raw), frames=16, terminators=1,
                  original_ay_consumer_proved=True, assembly_executed=False)
    (reports / 'ActionAyAntimissileStreamClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
