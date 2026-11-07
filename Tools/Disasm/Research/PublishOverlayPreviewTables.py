"""Выделение двух исходных таблиц, сохранение соседних байтов и существующей адресации."""
from collections import Counter
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

from OverlayPreviewTables import ROOT, TABLES, render, verify_originals
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    data_tables = verify_originals()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    sm, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    pending, removed = {}, []
    for table, data in zip(TABLES, data_tables):
        slot, offset, origin, size, module, relative, kind = table
        old = next(item for item in sm if item['slot'] == slot and item['offset'] == offset)
        old_path = ROOT / old['path']
        raw = old_path.read_bytes()
        assert old['kind'] == 'unclassified' and raw[:size] == data
        text, labels = render(table, data)
        pending[ROOT / relative] = text.encode('utf-8')
        spans = [dict(old, length=size, path=relative, kind='typed_data', origin=origin,
                      sha256=hashlib.sha256(data).hexdigest())]
        for label, address in labels.items():
            key = module + '.' + label
            assert key not in symbols
            symbols[key] = address
        include = f'                disp #{origin:04X}\n                include "../' + relative.removeprefix('Source/') + '"\n                ent'
        if len(raw) > size:
            suffix = 'Source/Resources/06_D3D/UnknownAfterSine.bin'
            pending[ROOT / suffix] = raw[size:]
            spans.append(dict(old, offset=offset + size, length=len(raw) - size, path=suffix,
                              sha256=hashlib.sha256(raw[size:]).hexdigest()))
            include += f'\n                assert $ == #{offset+size:04X}\n' + (
                '                ; Следующая страница сохраняет неизвестное назначение.\n'
                '                incbin "../Resources/06_D3D/UnknownAfterSine.bin"')
        sm[sm.index(old):sm.index(old) + 1] = spans
        path = ROOT / ('Source/Files/06_D3D.inc' if slot == 6 else 'Source/Files/23_CONTROL.inc')
        text = path.read_text(encoding='utf-8')
        needle = '                incbin "../' + old['path'].removeprefix('Source/') + '"'
        assert text.count(needle) == 1
        warning = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
        if warning + needle in text:
            text = text.replace(warning + needle, needle)
        pending[path] = text.replace(needle, include).encode('utf-8')
        removed.append(old_path)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in sm))
    sizes = Counter()
    for item in sm:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', sm), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FOverlayGlyphPhase' not in text and text.count('                endif') == 1
    block = '                struct FOverlayGlyphPhase\n'
    for row in range(8):
        for side in ('Left', 'Right'):
            block += (f'Row{row}{side}'.ljust(16) + 'db #00').ljust(80) + f'; пиксели {"левой" if side=="Left" else "правой"} колонки строки {row}, объединяются с буфером через XOR\n'
    block += '                ends\n                assert FOverlayGlyphPhase == #10\n\n'
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка синусоиды D3D и двух восьмифазных форм прицельного значка.
    from OverlayPreviewTables import TABLES as OVERLAY_PREVIEW_TABLES, parse as parse_overlay_preview, verify_originals as verify_overlay_preview
    verify_overlay_preview()
    for slot,offset,origin,size,module,path,kind in OVERLAY_PREVIEW_TABLES:
        raw,labels=parse_overlay_preview((ROOT/path).read_text('utf-8'))
        assert raw==sources[slot][offset:offset+size]
        assert all(symbols[(module+'.'+label).upper()]==origin+position for label,position in labels.items())
    assert symbols['FOVERLAYGLYPHPHASE']==16

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/OverlayPreviewTables'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeOverlayPreviewTables'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, *removed)}
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
        if path.suffix == '.json':
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='overlay-preview-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary, path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        else:
            path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('256 значений синусоиды D3D и 16 физических фаз прицельных значков, 512 байтов')


if __name__ == '__main__':
    main()
