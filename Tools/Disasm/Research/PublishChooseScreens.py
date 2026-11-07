"""Публикация двух подтверждённых экранных файлов без назначения игровой RAM."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import re
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def parse_attributes(text):
    rows = re.findall(r'Row\d{2}:\s+FChooseScreenAttributes\s*\{([^}]+)\}', '\n'.join(
        line.partition(';')[0] for line in text.splitlines()))
    assert len(rows) == 24
    raw = bytearray()
    for row in rows:
        fields = row.split(',')
        assert len(fields) == 32
        raw.extend(int(field.strip().removeprefix('#'), 16) for field in fields)
    return bytes(raw)


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    load = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    pending = {}
    source_map, symbols, inventory = (load(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    removed = []
    for slot, name in ((31, 'choose1'), (32, 'choose2')):
        entry = next(item for item in source_map if item['slot'] == slot)
        assert entry['kind'] == 'unclassified' and entry['length'] == 6912
        old = ROOT / entry['path']
        data = old.read_bytes()
        assert data == (ROOT / f'Tools/Disasm/Extracted/Active/{slot}_{name}.C.bin').read_bytes()
        root = f'Source/Resources/{slot}_{name}/'
        bitmap_path, attributes_path = root + 'Bitmap.bin', root + 'Attributes.asm'
        pending[ROOT / bitmap_path] = data[:6144]
        module = 'ChooseFighter' + str(slot - 30)
        lines = ['                module ' + module,
                 '                ; Документация [экран выбора](../../../Docs/ChooseFighterScreens.md)',
                 '                ; Метки задают смещения файла, адрес загрузки игре здесь не назначается.',
                 '                assert $ == #1800']
        for row in range(24):
            label = f'Row{row:02}'
            symbols[module + '.' + label] = 6144 + row * 32
            lines.append((label + ':').ljust(16) + 'FChooseScreenAttributes {')
            for col in range(32):
                value = data[6144 + 32 * row + col]
                line = f'                    #{value:02X}' + (',' if col < 31 else '')
                note = f'Column{col:02}, ink={value & 7}, paper={(value >> 3) & 7}, bright={(value >> 6) & 1}, flash={value >> 7}'
                lines.append(line.ljust(80) + '; ' + note)
            lines.append('                }')
        lines.extend(('                assert $ == #1B00', '                endmodule', ''))
        text = '\n'.join(lines)
        assert parse_attributes(text) == data[6144:]
        pending[ROOT / attributes_path] = text.encode('utf-8')
        spans = [dict(slot=slot, offset=start, length=end - start, path=path, kind=kind,
                      origin=None, sha256=hashlib.sha256(data[start:end]).hexdigest())
                 for start, end, path, kind in ((0, 6144, bitmap_path, 'binary_resource'),
                                                (6144, 6912, attributes_path, 'typed_data'))]
        pos = source_map.index(entry)
        source_map[pos:pos + 1] = spans
        path = ROOT / f'Source/Files/{slot}_{name}.inc'
        before = path.read_text(encoding='utf-8')
        needle = f'                incbin "../Resources/{slot}_{name}/Unclassified000.bin"'
        assert before.count(needle) == 1
        before = before.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления',
                                '                ; Экран выбора, bitmap и атрибуты, исходные файловые смещения.')
        pending[path] = before.replace(needle, f'                incbin "../Resources/{slot}_{name}/Bitmap.bin"\n'
            '                assert $ == #1800\n'
            f'                include "../Resources/{slot}_{name}/Attributes.asm"').encode('utf-8')
        removed.append(old)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FChooseScreenAttributes' not in text and text.count('                endif') == 1
    lines = ['                struct FChooseScreenAttributes']
    lines += [(f'Column{col:02}'.ljust(16) + 'db #00').ljust(80) + '; flash, bright, paper и ink одного знакоместа'
              for col in range(32)]
    lines += ['                ends', '                assert FChooseScreenAttributes == #20', '']
    pending[path] = text.replace('                endif', '\n'.join(lines) + '\n                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка двух физических экранов выбора, без предположения об их загрузке.
    from PublishChooseScreens import parse_attributes as parse_choose_attributes
    for slot,name in ((31,'choose1'),(32,'choose2')):
        prefix=f'Source/Resources/{slot}_{name}/'
        assert (ROOT/(prefix+'Bitmap.bin')).read_bytes()==sources[slot][:6144]
        assert parse_choose_attributes((ROOT/(prefix+'Attributes.asm')).read_text('utf-8'))==sources[slot][6144:6912]
    assert symbols['FCHOOSESCREENATTRIBUTES']==32

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ChooseScreens'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeChooseScreens'
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
        verify()
    for old in removed:
        assert old.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert old.read_bytes() == (history / old.relative_to(ROOT)).read_bytes()
        old.unlink()
    print('choose1/choose2: 13824 байта, 12288 байтов bitmap и 1536 байтов атрибутов')


if __name__ == '__main__':
    main()
