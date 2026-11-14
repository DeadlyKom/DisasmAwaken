"""Физические состояния игрока в станции и шести SAVE, без изменения размещения."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

from PlayerSavedFields import ROOT, SLOTS, TABLES, FIELDS, render
from SavedStateLayout import parse
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    source_map, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    pending, removed = {}, []
    for slot, name, origin in ((4, 'STATIONF', 0x6000), *((slot, name, 0x983B) for slot, name in SLOTS)):
        extension = 'C' if slot == 4 else 's'
        data = (ROOT / f'Tools/Disasm/Extracted/Active/{slot:02}_{name}.{extension}.sectors.bin').read_bytes()
        start = 0x9844 - origin
        old = next(item for item in source_map if item['slot'] == slot and item['offset'] == start)
        old_path = ROOT / old['path']
        assert old['kind'] == 'unclassified' and old['length'] == 108
        assert old_path.read_bytes() == data[start:start + 108]
        prefix = 'Source/Station/Data/' if slot == 4 else f'Source/Resources/{slot}_{name}/'
        pieces = []
        include = []
        for table in TABLES:
            address, module, kind, labels = table
            size = sum(size for _, size in FIELDS[kind]) * len(labels)
            path = prefix + module + '.asm'
            module_prefix = '' if slot == 4 else name.title()
            text = render(data, table, module_prefix, 0x6000 if slot == 4 else 0, origin)
            raw, bindings = parse(text, {key: list(value) for key, value in FIELDS.items()})
            offset = address - origin
            assert raw == data[offset:offset + size]
            pending[ROOT / path] = text.encode('utf-8')
            physical_origin = address if slot == 4 else None
            pieces.append(dict(slot=slot, offset=offset, length=size, kind='typed_data', path=path,
                               origin=physical_origin, sha256=hashlib.sha256(raw).hexdigest()))
            for label, relative in bindings.items():
                symbol = module_prefix + module + '.' + label
                assert symbol not in symbols
                symbols[symbol] = (address if slot == 4 else offset) + relative
            include.append(f'                assert $ == #{offset:04X}')
            if slot == 4:
                include.extend((f'                disp #{address:04X}', f'                include "../Station/Data/{module}.asm"', '                ent'))
            else:
                include.append(f'                include "../Resources/{slot}_{name}/{module}.asm"')
        offset = 0x98AC - origin
        path = ('Source/Resources/04_STATIONF/' if slot == 4 else prefix) + 'Unknown98AC.bin'
        raw = data[offset:offset + 4]
        pending[ROOT / path] = raw
        pieces.append(dict(slot=slot, offset=offset, length=4, kind='unclassified', path=path,
                           origin=None, sha256=hashlib.sha256(raw).hexdigest()))
        include.extend((f'                assert $ == #{offset:04X}',
                        '                ; Четыре соседних байта сохраняют неизвестный смысл.',
                        '                incbin "../' + path.removeprefix('Source/') + '"'))
        assert sum(item['length'] for item in pieces) == 108
        index = source_map.index(old)
        source_map[index:index + 1] = pieces
        path = ROOT / f'Source/Files/{slot:02}_{name}.inc'
        text = path.read_text(encoding='utf-8')
        needle = '                incbin "../' + old['path'].removeprefix('Source/') + '"'
        assert text.count(needle) == 1
        pending[path] = text.replace(needle, '\n'.join(include)).encode('utf-8')
        removed.append(old_path)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FPlayerSaveHeader' not in text and text.count('                endif') == 1
    notes = {
        'ShipIndex': 'индекс текущей модели корабля, его игровые значения здесь не перечисляются',
        'SkimmerIndex': 'индекс скимера, FF пропускает дополнительное слагаемое взвешенной загрузки',
        'StatusCode': 'числовой полицейский статус, все 8 бит участвуют в расчётах, подпись по старшим трём',
        'RankScore': 'беззнаковое слово выбора ранга',
        'Money': 'денежное слово, печатается и изменяется торговлей и наградой',
        'UsedTonnage': 'байт используемого тоннажа статусной панели',
        'Capacity': 'байт вместимости статусной панели',
        'QuantityAndMark': 'рисователь читает 6..0 как количество и 7 как FE, сборщик и LANG читают весь байт, смысл пометки неизвестен',
        'Price': 'полный байт цены колонки Наличие',
        'Code': 'код количества оборудования, 81..FF инвертируются, 80 останавливает печать',
    }
    block = ''
    for kind in ('FPlayerSaveHeader', 'FOwnedCargoRow', 'FEquipmentQuantityCode'):
        block += '                struct ' + kind + '\n'
        for field, size in FIELDS[kind]:
            block += (field.ljust(16) + ('db #00' if size == 1 else 'dw #0000')).ljust(80) + '; ' + notes[field] + '\n'
        block += '                ends\n                assert ' + kind + ' == #' + format(sum(size for _, size in FIELDS[kind]), '02X') + '\n\n'
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка 728 байтов физического состояния игрока и его дисковых копий.
    from PlayerSavedFields import verify_all as verify_player_saved_fields, TABLES as PLAYER_SAVED_TABLES
    assert verify_player_saved_fields() == 728
    for slot,name in ((4,'STATIONF'),*SAVE_SLOTS):
        for _,module,_,_ in PLAYER_SAVED_TABLES:
            path=('Source/Station/Data/' if slot==4 else f'Source/Resources/{slot}_{name}/')+module+'.asm'
            item=next(item for item in source_map if item['path']==path)
            raw,labels=parse_save((ROOT/path).read_text('utf-8'),save_types)
            prefix=module if slot==4 else name.title()+module
            base=item['origin'] if item['origin'] is not None else item['offset']
            assert all(symbols[(prefix+'.'+label).upper()]==base+offset for label,offset in labels.items())

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    path = ROOT / 'Docs/SavedStateLayout.md'
    text = path.read_text(encoding='utf-8').replace('301 байт', '405 байтов').replace('211 байтов', '107 байтов')
    start = text.index('| Смещение SAVE |')
    end = text.index('\nФизические подключения:', start)
    rows = ['| Смещение SAVE | Длина | Поля станции |', '| --- | --- | --- |']
    for item in source_map:
        if item['slot'] == 4 and 0x383B <= item['offset'] < 0x3A3B:
            length = min(item['length'], 0x3A3B - item['offset'])
            rows.append(f'| #{item["offset"] - 0x383B:03X} | {length} | [{item["path"].rsplit("/",1)[1]}](../{item["path"]}) |')
    pending[path] = (text[:start] + '\n'.join(rows) + '\n' + text[end:]).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/PlayerSavedFields'
    history = ROOT / 'Tools/Disasm/Research/History/BeforePlayerSavedFields'
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
        if path.suffix != '.json':
            path.write_bytes(raw)
            continue
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='player-state-', suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            output.write(raw)
        try:
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('104 байта состояния станции и 624 байта шести SAVE оформлены физическими структурами')


if __name__ == '__main__':
    main()
