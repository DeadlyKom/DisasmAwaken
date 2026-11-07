"""Публикация 322 физических байтов планировщика и именование обращений к строке шаблона."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import re
import sys

from SpawnPhysicalRows import ROOT, TABLES, TYPES, render, parse
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    assert read('ActionSpawnTemplateLoopVerification')['passed']
    assert read('ActionSpawnModelSelectionVerification')['passed']
    sm, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    pending, removed = {}, []
    path = ROOT / 'Source/Files/17_ACTION.inc'
    includes = path.read_text(encoding='utf-8')
    for table in TABLES:
        start, end, module, relative = table
        offset = start - 0x6000 + 0x23D
        old = next(item for item in sm if item['slot'] == 17 and item['offset'] == offset)
        old_path = ROOT / old['path']
        before = old_path.read_bytes()
        size = end - start
        assert old['kind'] == 'unclassified' and old['length'] in (192, 146)
        text, labels = render(table)
        raw, relative_labels = parse(text)
        assert raw == before[:size]
        assert all(labels[name] == start + value for name, value in relative_labels.items())
        pending[ROOT / relative] = text.encode('utf-8')
        for label, address in labels.items():
            name = module + '.' + label
            assert name not in symbols
            symbols[name] = address
        spans = [dict(old, length=size, kind='typed_data', path=relative, origin=start,
                      sha256=hashlib.sha256(raw).hexdigest())]
        new_include = f'                disp #{start:04X}\n                include "../Action/Data/' + relative.rsplit('/', 1)[1] + '"\n                ent'
        if size < len(before):
            tail_path = 'Source/Resources/17_ACTION/UnknownAfterSpawnModelChoices.bin'
            pending[ROOT / tail_path] = before[size:]
            spans.append(dict(old, offset=offset + size, length=len(before) - size, path=tail_path,
                              sha256=hashlib.sha256(before[size:]).hexdigest()))
            new_include += f'\n                assert $ == #{offset+size:04X}\n' + (
                '                ; Соседние 16 байтов не имеют подтверждённого потребителя.\n'
                '                incbin "../Resources/17_ACTION/UnknownAfterSpawnModelChoices.bin"')
        sm[sm.index(old):sm.index(old) + 1] = spans
        needle = '                incbin "../Resources/17_ACTION/' + old_path.name + '"'
        assert includes.count(needle) == 1
        includes = includes.replace(needle, new_include)
        removed.append(old_path)
    pending[path] = includes.encode('utf-8')
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in sm))
    sizes = Counter()
    for item in sm:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', sm), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FSpawnTemplateRow' not in text and text.count('                endif') == 1
    descriptions = {'Address': 'доказанный адрес исходной строки в перенесённом ядре',
                    'Delta0': 'знаковая поправка к первой компоненте', 'Delta1': 'знаковая поправка ко второй компоненте',
                    'Delta2': 'знаковая поправка к третьей компоненте',
                    'ModelOffset': 'байт, записываемый в FActionRecord.ModelOffset',
                    'OffsetPhase1': 'байт, записываемый в FActionRecord.OffsetPhase1',
                    'RecordByte0F': 'байт, записываемый в FActionRecord.TargetIndex, смысл зависит от класса',
                    'Unknown00': 'Unknown, младший байт ограничителя, исходно FF',
                    'EndCode': 'код 80 завершает обход, проверяется отдельно от предыдущих восьми байтов'}
    block = ''
    for kind, fields in TYPES.items():
        block += '                struct ' + kind + '\n'
        for field, size in fields:
            block += (field.ljust(16) + ('db #00' if size == 1 else 'dw #0000')).ljust(80) + '; ' + descriptions[field] + '\n'
        block += '                ends\n                assert ' + kind + ' == #' + format(sum(size for _, size in fields), '02X') + '\n\n'
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    for relative, old, new in (
        ('Source/Action/SpawnAlternate.asm', 'LD DE, #7799', 'LD DE, @ActionSpawnTemplates.Seed00'),
        ('Source/Action/ScheduleSpawn.asm', 'LD HL, #7AC6', 'LD HL, @ActionSpawnModels.Class00')):
        path = ROOT / relative
        text = path.read_text(encoding='utf-8')
        assert text.count(old) == 1
        pending[path] = text.replace(old, new).encode('utf-8')
    path = ROOT / 'Source/Action/SpawnAlternate.asm'
    text = pending[path].decode('utf-8')
    start, end = text.index('NextTemplate:'), text.index('BuildRandom:')
    section = text[start:end]
    for offset in range(8):
        field = 'FSpawnTemplateRow.Delta' + str(offset // 2) + (' + 1' if offset & 1 else '') if offset < 6 else (
            'FSpawnTemplateRow.ModelOffset' if offset == 6 else 'FSpawnTemplateRow.OffsetPhase1')
        needle = f'(IX+#{offset:02X})'
        assert needle in section
        # Последнее чтение +1 после ADD IX относится к отдельному ограничителю.
        if offset == 1:
            assert section.count(needle) == 2
            section = section.replace(needle, '(IX + @' + field + ')', 1)
            section = section.replace(needle, '(IX + @FSpawnTemplateEnd.EndCode)')
        else:
            section = section.replace(needle, '(IX + @' + field + ')')
    text = text[:start] + section + text[end:]
    text = text.replace('LD BC, #0008', 'LD BC, FSpawnTemplateRow')
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка всех физических шаблонов, ограничителей и пар параметров создания.
    from SpawnPhysicalRows import TABLES as SPAWN_TABLES, TYPES as SPAWN_TYPES, parse as parse_spawn
    for start,end,module,path in SPAWN_TABLES:
        raw,labels=parse_spawn((ROOT/path).read_text('utf-8'))
        offset=start-0x6000+0x23D
        assert raw==sources[17][offset:offset+end-start]
        assert all(symbols[(module+'.'+label).upper()]==start+relative for label,relative in labels.items())
    for kind,fields in SPAWN_TYPES.items():
        offset=0
        for field,size in fields:
            assert symbols[(kind+'.'+field).upper()]==offset
            offset+=size
        assert symbols[kind.upper()]==offset

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/SpawnPhysicalRows'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeSpawnPhysicalRows'
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
            import os, tempfile
            from pathlib import Path
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='spawn-rows-', suffix='.tmp', delete=False) as output:
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
    print('16 шаблонов, 16 ограничителей, 9 указателей моделей и 56 пар оформлены, 322 байта сохранены')


if __name__ == '__main__':
    main()
