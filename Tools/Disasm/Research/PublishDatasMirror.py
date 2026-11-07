"""Выделение точной дисковой копии блока ACTION и сохранение секторного хвоста."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    root = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((root / (name + '.json')).read_text(encoding='utf-8'))
    proof = read('DatasMirrorVerification')
    assert proof['passed'] and proof['exact_bytes'] == 7213
    data = (ROOT / 'Tools/Disasm/Extracted/Active/18_DATAS.C.sectors.bin').read_bytes()
    source_map = read('SourceMap')
    old = next(item for item in source_map if item['slot'] == 18)
    old_path = ROOT / old['path']
    assert old_path.read_bytes() == data and old['kind'] == 'unclassified' and len(data) == 7424
    logical_path = 'Source/Resources/18_DATAS/ActionInitialBlock.bin'
    tail_path = 'Source/Resources/18_DATAS/SectorTail.bin'
    pending = {ROOT / logical_path: data[:7213], ROOT / tail_path: data[7213:]}
    spans = [dict(slot=18, offset=start, length=end - start, kind=kind, path=path, origin=None,
                  sha256=hashlib.sha256(data[start:end]).hexdigest())
             for start, end, kind, path in ((0, 7213, 'binary_resource', logical_path),
                                           (7213, 7424, 'unclassified', tail_path))]
    index = source_map.index(old)
    source_map[index:index + 1] = spans
    inventory = read('Inventory')
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Inventory', inventory)):
        pending[root / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/18_DATAS.inc'
    text = path.read_text(encoding='utf-8')
    needle = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n' + (
        '                incbin "../Resources/18_DATAS/Unclassified000.bin"')
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, '''                ; Документация [точная копия блока ACTION](../../Docs/DatasMirror.md)
                ; Исходная копия 8C00..A82C, путь загрузки DATAS пока не установлен.
                incbin "../Resources/18_DATAS/ActionInitialBlock.bin"
                assert $ == #1C2D
                ; 211 байтов после логического конца, сохранены без классификации.
                incbin "../Resources/18_DATAS/SectorTail.bin"''').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка отдельной дисковой копии начального блока полётного состояния.
    mirror=(ROOT/'Source/Resources/18_DATAS/ActionInitialBlock.bin').read_bytes()
    assert mirror==sources[18][:0x1C2D]==sources[17][0x2C00:0x482D]
    assert (ROOT/'Source/Resources/18_DATAS/SectorTail.bin').read_bytes()==sources[18][0x1C2D:]

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    docs = [
        '# Дисковая копия блока полётного состояния', '',
        'Все 7 213 байтов DATAS.C побайтно совпадают с ACTION.C по',
        'файловым смещениям #2C00..#482C, которым в полёте соответствуют',
        'адреса #8C00..#A82C. Последние 211 байтов выделенных секторов',
        'сохранены отдельно. Исходные копии в двух файлах не объединяются.',
        '', 'Совпадение проверяет [модель](../Tools/Disasm/Research/CheckDatasMirror.py).',
        'Путь загрузки отдельного DATAS пока не установлен. Известные',
        'потребители и писатели областей ACTION описаны в связанных исходниках.',
        'Неизвестные поля и промежутки исходного ACTION остаются неизвестными',
        'и для этой дисковой копии. Назначение DATAS как механизма сброса',
        'состояния этой проверкой не устанавливается.', '',
        '| Смещение DATAS | Длина | Вид ACTION | Соответствующий исходник |',
        '| --- | --- | --- | --- |',
    ]
    for span in proof['source_spans']:
        relative = span['action_path']
        docs.append(f'| #{span["datas_offset"]:04X} | {span["length"]} | {span["action_kind"]} | [{relative}](../{relative}) |')
    pending[ROOT / 'Docs/DatasMirror.md'] = ('\n'.join(docs) + '\n').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/DatasMirror'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeDatasMirror'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, old_path)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, original in before.items():
        assert path.read_bytes() == original if original is not None else not path.exists()
        if original is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert old_path.read_bytes() == data
    old_path.unlink()
    print('DATAS: 7213 байтов копии ACTION и 211 байтов секторного хвоста')


if __name__ == '__main__':
    main()
