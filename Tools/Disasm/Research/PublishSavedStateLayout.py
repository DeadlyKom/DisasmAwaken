"""Кандидат и публикация полей SAVE, без изменения адресов и дисковых байтов."""
from collections import Counter
from pathlib import Path
import contextlib
import hashlib
import io
import json
import sys

from SavedStateLayout import ROOT, START, SIZE, SLOTS, structures, render, parse
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    assert read('SavedStateLayoutVerification')['passed']
    source_map, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    layout = [dict(item) for item in source_map if item['slot'] == 4
              and START - 0x6000 <= item['offset'] < START - 0x6000 + SIZE]
    for item in layout:
        available = START - 0x6000 + SIZE - item['offset']
        if item['length'] > available:
            assert item['kind'] == 'unclassified'
            item['length'] = available
    assert sum(item['length'] for item in layout) == SIZE
    pending, removed = {}, []
    types = structures()
    for slot, name in SLOTS:
        old = next(item for item in source_map if item['slot'] == slot)
        old_path = ROOT / old['path']
        data = old_path.read_bytes()
        assert old['kind'] == 'unclassified' and len(data) == SIZE
        assert data == (ROOT / f'Tools/Disasm/Extracted/Active/{slot}_{name}.s.bin').read_bytes()
        prefix = f'Source/Resources/{slot}_{name}/'
        spans = []
        lines = ['; -----------------------------------------', f'; запись {slot}, {name}.s',
                 '; логическая длина 512, полный секторный размер 512',
                 '; -----------------------------------------',
                 '                ; Документация [состояние слота](../../Docs/SavedStateLayout.md)']
        for item in layout:
            offset = item['offset'] - (START - 0x6000)
            length = item['length']
            raw = data[offset:offset + length]
            assert len(raw) == length
            if item['kind'] == 'typed_data':
                path = prefix + Path(item['path']).name
                text, module = render(data, item, name, types)
                decoded, labels = parse(text, types)
                assert decoded == raw
                pending[ROOT / path] = text.encode('utf-8')
                for label, relative in labels.items():
                    symbol = module + '.' + label
                    assert symbol not in symbols
                    symbols[symbol] = offset + relative
                directive, kind = 'include', 'typed_data'
            else:
                assert item['kind'] == 'unclassified'
                path = prefix + f'Unknown{offset:03X}.bin'
                pending[ROOT / path] = raw
                directive, kind = 'incbin', 'unclassified'
                lines.append('                ; Неизвестные поля сохранены, нули не считаются свободным местом.')
            spans.append(dict(slot=slot, offset=offset, length=length, kind=kind, path=path,
                              origin=None, sha256=hashlib.sha256(raw).hexdigest()))
            lines.extend((f'                assert $ == #{offset:04X}',
                          f'                {directive} "../Resources/{slot}_{name}/' + path.rsplit('/', 1)[1] + '"'))
        lines.extend(('                assert $ == #0200', ''))
        pending[ROOT / f'Source/Files/{slot}_{name}.inc'] = '\n'.join(lines).encode('utf-8')
        index = source_map.index(old)
        source_map[index:index + 1] = spans
        removed.append(old_path)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in source_map))
    sizes = Counter()
    for item in source_map:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка каждого физического поля SAVE по общим структурам станции.
    from SavedStateLayout import SLOTS as SAVE_SLOTS, structures as save_structures, parse as parse_save
    save_types = save_structures()
    for slot, name in SAVE_SLOTS:
        for item in source_map:
            if item['slot'] != slot or item['kind'] != 'typed_data':
                continue
            text = (ROOT / item['path']).read_text('utf-8')
            raw, labels = parse_save(text, save_types)
            assert raw == sources[slot][item['offset']:item['offset'] + item['length']]
            module = re.search(r'module\\s+(\\w+)', text)[1]
            for label, relative in labels.items():
                assert symbols[(module + '.' + label).upper()] == item['offset'] + relative

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    path = ROOT / 'Docs/SaveSlots.md'
    text = path.read_text(encoding='utf-8')
    pending[path] = (text + '\nФизические поля всех шести файлов и точные различия описаны в\n'
                     '[SavedStateLayout](SavedStateLayout.md). Неизвестные поля остаются явными.\n').encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/RecordCircleProgress.py'
    text = path.read_text(encoding='utf-8')
    assert text.count("'DatasMirrorVerification')") == 1
    pending[path] = text.replace("'DatasMirrorVerification')",
                                "'DatasMirrorVerification', 'SavedStateLayoutVerification')").encode('utf-8')
    docs = ['# Физические состояния SAVE', '',
            'Файлы SAVE0..SAVE5 содержат по 512 байтов. Их адрес загрузки',
            'определяется инструкциями [загрузчика](../Source/Station/HandleLoadSlotAction.asm)',
            'и [записи](../Source/Station/HandleSaveSlotAction.asm), это #983B..#9A3A.',
            'Параметр каталога #6000 эти обработчики не используют.', '',
            'SAVE0..SAVE4 отличаются от исходного блока STATIONF только байтом +3,',
            'то есть FStationBcdCounter.Low. Значения SAVE0..SAVE4 равны #15, #17,',
            '#19, #22 и #25. В STATIONF этот байт равен #10. SAVE5 целиком нулевой.',
            'Нулевой SAVE5 сохраняется в исходном виде, пригодность такого состояния',
            'для игры не установлена. В том числе его границы списков равны нулю,',
            'а не исходному #80. Нормализация либо исправление не выполняются.', '',
            'В каждом файле 301 байт оформлен существующими структурами, 211 байтов',
            'сохранены в явно неизвестных диапазонах. Поля Unknown внутри известных',
            'структур сохраняют неизвестный смысл. Размер и порядок всех полей',
            'следуют из уже разобранных потребителей станции, новых адресов нет.', '',
            '| Смещение SAVE | Длина | Поля станции |', '| --- | --- | --- |']
    for item in layout:
        docs.append(f'| #{item["offset"] - (START - 0x6000):03X} | {item["length"]} | '
                    f'[{item["path"].rsplit("/", 1)[1]}](../{item["path"]}) |')
    docs += ['', 'Физические подключения:', '']
    for slot, name in SLOTS:
        docs.append(f'- [{name}](../Source/Files/{slot}_{name}.inc)')
    docs += ['', '[Проверка](../Tools/Disasm/Research/CheckSavedStateLayout.py) сравнивает все',
             'шесть оригинальных файлов и поля существующих структур, обычная статическая',
             'сверка исходников повторно проверяет каждый опубликованный байт.',
             'Это не проверка дисковой аппаратуры, запуска игры или сборки.', '']
    pending[ROOT / 'Docs/SavedStateLayout.md'] = '\n'.join(docs).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/SavedStateLayout'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeSavedStateLayout'
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
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('SAVE: 1806 физических байтов структур, 1266 неизвестных байтов, оригиналы сохранены')


if __name__ == '__main__':
    main()
