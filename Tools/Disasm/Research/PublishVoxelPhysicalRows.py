"""Публикация доказанных таблиц и кадров VOXAL с сохранением соседнего диапазона."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import sys

from CheckIntro import ROOT
from VoxelPhysicalData import TABLES, render, parse, structures
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'

    def read(name):
        return json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))

    data = (ROOT / 'Tools/Disasm/Extracted/Active/20_VOXAL0.C.sectors.bin').read_bytes()
    assert read('VoxelSpriteSampleRasterVerification')['passed']
    assert read('ActionVisualEffectListVerification')['passed']
    for page in range(4):
        block = data[page * 256:(page + 1) * 256]
        assert all(block[16 * high + low] == (block[16 * high] & 240) | (block[low] & 15)
                   for high in range(16) for low in range(16))
    pending = {}
    source_map = read('SourceMap')
    old = next(item for item in source_map if item['slot'] == 20 and item['offset'] == 0)
    old_path = ROOT / old['path']
    assert old['kind'] == 'unclassified' and old['length'] == 9472 and old_path.read_bytes() == data[:9472]
    symbols = read('Symbols')
    spans, lines = [], []
    for table in TABLES:
        module, path, start, end, width, count = table
        text, labels = render(data, table)
        raw, decoded_labels = parse(text)
        assert raw == data[start:end] and decoded_labels == labels
        assert not symbols.keys() & labels.keys()
        symbols.update(labels)
        pending[ROOT / path] = text.encode('utf-8')
        spans.append(dict(slot=20, offset=start, length=end - start, kind='typed_data', path=path,
                          origin=0xC000 + start, sha256=hashlib.sha256(raw).hexdigest()))
        lines.extend((f'                assert $ == #{start:04X}', f'                disp #{0xC000 + start:04X}',
                      '                include "../Voxel/Data/' + path.rsplit('/', 1)[1] + '"', '                ent'))
    tail_path = 'Source/Resources/20_VOXAL0/AfterSmallFrames.bin'
    pending[ROOT / tail_path] = data[8640:9472]
    spans.append(dict(slot=20, offset=8640, length=832, kind='unclassified', path=tail_path,
                      origin=None, sha256=hashlib.sha256(data[8640:9472]).hexdigest()))
    lines.extend(('                assert $ == #21C0', '                ; Назначение следующих 832 байтов ещё не установлено.',
                  '                incbin "../Resources/20_VOXAL0/AfterSmallFrames.bin"'))
    source_map[source_map.index(old):source_map.index(old) + 1] = spans
    inventory = read('Inventory')
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/20_VOXAL0.inc'
    text = path.read_text(encoding='utf-8')
    old_text = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n' + (
        '                incbin "../Resources/20_VOXAL0/Unclassified000.bin"')
    assert text.count(old_text) == 1
    pending[path] = text.replace(old_text, '\n'.join(lines)).encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert text.count('                endif') == 1 and 'struct FEffectByteRow' not in text
    pending[path] = text.replace('                endif', structures() + '\n                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка физических строк палитры и двух анимаций VOXAL.
    from VoxelPhysicalData import TABLES as VOXEL_ROWS, parse as parse_voxel_rows
    for module,path,start,end,width,count in VOXEL_ROWS:
        rows=[item for item in source_map if item['path']==path]
        assert len(rows)==1 and rows[0]['slot']==20 and rows[0]['offset']==start
        raw,labels=parse_voxel_rows((ROOT/path).read_text('utf-8'))
        assert len(raw)==width*count and raw==sources[20][start:end]
        assert all(symbols.get(name.upper())==address for name,address in labels.items())
    assert symbols['FEFFECTBYTEROW16']==16 and symbols['FEFFECTBYTEROW32']==32
    assert symbols['FEFFECTBYTEROW16.PAIR15']==15 and symbols['FEFFECTBYTEROW32.PAIR31']==31

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/VoxelPhysicalRows'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeVoxelPhysicalRows'
    assert not candidate.exists() and not history.exists()
    originals = {p: p.read_bytes() if p.exists() else None for p in (*pending, old_path)}
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
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert old_path.read_bytes() == data[:9472]
    old_path.unlink()
    print('VOXAL0: 8640 байтов физических строк, соседние 832 байта сохранены')


if __name__ == '__main__':
    main()
