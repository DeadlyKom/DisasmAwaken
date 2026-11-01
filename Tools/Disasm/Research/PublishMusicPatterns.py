"""Точечное разделение проверенных декодеров с кандидатом и историей ручных исходников."""
from pathlib import Path
import collections, contextlib, hashlib, io, json, re, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function, continuity
from ValidateNotes import validate_notes
from MusicNotes import COMMENTS as OLD_COMMENTS
import MusicPatternFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert all(read(stem)['passed'] for stem in ('MusicPatternRowsVerification', 'MusicPatternPhasesVerification'))
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/MusicPatterns'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeMusicPatterns'
    assert not candidate.exists() and not history.exists()
    pending = {}
    functions = read('Functions')
    old = [f for f in functions if f['region'] == 'Music' and 0xE37C <= f['address'] < 0xE60C]
    assert [f['address'] for f in old] == [0xE37C, 0xE439, 0xE4E6, 0xE583]
    assert all(f['semantic_status'] != 'described' for f in old)
    old_bytes = {ROOT / f['path']: (ROOT / f['path']).read_bytes() for f in old}
    new = [dict(region='Music', name=name, address=a, slot=10, offset=a - 0xDB00,
                end_offset=facts.ENDS[a] - 0xDB00, path='Source/Music/' + name + '.asm',
                description=description, semantic_status='described',
                fragment_scope='original_pattern_decoder_with_documented_internal_entries')
           for a, (name, description) in facts.FUNCTIONS.items()]
    at = functions.index(old[0])
    assert functions[at:at + 4] == old
    functions[at:at + 4] = new
    def owner(address):
        return next((f for f in new if f['address'] <= address < 0xDB00 + f['end_offset']), None)
    symbols, renames, labels = read('Symbols'), {}, {}
    for key, address in list(symbols.items()):
        if not any(key.startswith('Music.' + f['name'] + '.') for f in old):
            continue
        f = owner(address)
        assert f is not None
        label = 'Entry' if address == f['address'] else facts.LABELS.get(address, key.rsplit('.', 1)[1])
        replacement = 'Music.' + f['name'] + '.' + label
        renames[key] = replacement
        del symbols[key]
        symbols[replacement] = address
        labels[address] = label
    for f in new:
        symbols['Music.' + f['name'] + '.Entry'] = f['address']
        labels[f['address']] = 'Entry'
    for address, label in facts.LABELS.items():
        symbols['Music.' + owner(address)['name'] + '.' + label] = address
        labels[address] = label
    paths = {f['path']: owner(f['address'])['path'] for f in old}
    def rename(text):
        for old_symbol, new_symbol in sorted(renames.items(), key=lambda pair: -len(pair[0])):
            text = re.sub(r'\b' + re.escape(old_symbol) + r'\b', new_symbol, text)
        for before, after in paths.items():
            text = text.replace(before, after).replace('../Music/' + Path(before).name, '../Music/' + Path(after).name)
        return text
    # Создание отдельного кандидата, существующие ручные тексты сохраняются до проверки байтов.
    for folder, glob in (('Source', '*.asm'), ('Source', '*.inc'), ('Includes', '*.inc'), ('Docs', '*.md')):
        for p in (ROOT / folder).rglob(glob):
            if p in old_bytes:
                continue
            before = p.read_text('utf-8')
            after = rename(before)
            if before == after:
                continue
            lines = after.splitlines()
            for index, line in enumerate(lines):
                code, sep, comment = line.partition(';')
                if sep and code.strip() and '@Music.' in code:
                    assert len(code.rstrip()) < 80
                    lines[index] = code.rstrip().ljust(80) + ';' + comment
            pending[p] = ('\n'.join(lines) + '\n').encode('utf-8')
    flow = read('ControlFlow')
    music = next(x for x in flow if x['name'] == 'Music')
    music['roots'] = sorted(set(music['roots']) | set(facts.FUNCTIONS))
    validate_notes([music], {'Music': facts.COMMENTS})
    comments = {**OLD_COMMENTS, **facts.COMMENTS}
    target_symbols = {a: key for key, a in symbols.items() if key.startswith('Music.')}
    for f in new:
        address = f['address']
        lines = ['                module Music', '                module ' + f['name'],
                 '                ; Документация [декодирование паттернов](../../Docs/MusicPattern.md)',
                 '                ; -----------------------------------------', '                ; ' + f['description'],
                 '                ; исходная запись 10, файловые смещения #' + format(f['offset'], '04X') + '..#' + format(f['end_offset'] - 1, '04X')]
        for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), facts.CONTRACTS['Music', address]):
            lines += ['                ; ' + heading + ':'] + ['                ;   ' + v for v in values]
        lines += ['                ; -----------------------------------------']
        for instruction in music['instructions']:
            if not f['offset'] <= instruction['offset'] < f['end_offset']:
                continue
            a = instruction['address']
            before, right = comments.get(a, ([], None))
            lines += ['                ; ' + v for v in before]
            operation = instruction['operation'].replace(',', ', ')
            if operation.startswith(('JP ', 'JR ', 'CALL ', 'DJNZ ')):
                operation = re.sub(r'#([0-9A-F]{4})', lambda match: '@' + target_symbols[int(match[1], 16)]
                                   if int(match[1], 16) in target_symbols else match[0], operation)
            operation = facts.name_operands('Music', address, operation)
            label = labels.get(a, '')
            line = ((label + ':').ljust(16) if label else ' ' * 16) + operation
            if right:
                assert len(line) < 80
                line = line.ljust(80) + '; ' + right
            lines.append(line)
        lines += ['                endmodule', '                endmodule']
        next_part = owner(facts.ENDS[address]) if address in (0xE3DC, 0xE489, 0xE53D) else None
        pending[ROOT / f['path']] = format_function('\n'.join(lines) + '\n', next_part).encode('utf-8')
    source_map = read('SourceMap')
    old_ranges = [x for x in source_map if x['path'] in paths]
    assert len(old_ranges) == 4
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    source_map = [x for x in source_map if x not in old_ranges]
    source_map += [dict(slot=10, offset=f['offset'], length=f['end_offset'] - f['offset'],
                        kind='code', path=f['path'], origin=f['address'],
                        sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in new]
    source_map.sort(key=lambda x: (x['slot'], x['offset']))
    modified = read('ModifiedCode')
    for item in modified:
        if item['region'] == 'Music' and owner(item['writer']) is not None:
            item['path'] = owner(item['writer'])['path']
    for stem, value in (('Functions', functions), ('ControlFlow', flow), ('SourceMap', source_map), ('Symbols', symbols), ('ModifiedCode', modified)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encoded(value)
    inventory = read('Inventory')
    inventory.update(fragments=len(functions), described=sum(f['semantic_status'] == 'described' for f in functions),
                     unknown=sum(f['semantic_status'] != 'described' for f in functions),
                     ranges_by_kind=dict(collections.Counter(x['kind'] for x in source_map)))
    pending[ROOT / 'Tools/Disasm/Reports/Inventory.json'] = encoded(inventory)
    p = ROOT / 'Source/Files/10_MUZ1.inc'
    text = p.read_text('utf-8')
    start = text.index('                assert $ == #087C')
    end = text.index('                assert $ == #0B0C', start)
    block = ''
    for f in new:
        block += ('                assert $ == #' + format(f['offset'], '04X') + '\n                disp #' + format(f['address'], '04X') +
                  '\n                include "../Music/' + f['name'] + '.asm"\n                ent\n')
    text = text[:start] + block + text[end:]
    _, order = continuity(functions, flow)
    for f in functions:
        if f['region'] != 'Music':
            continue
        needle = '                include "../Music/' + Path(f['path']).name + '"'
        if f['path'] in order:
            line = next(line for line in text.splitlines() if line.startswith(needle))
            text = text.replace(line, needle.ljust(80) + '; (' + str(order[f['path']]) + ') жёсткий порядок, последовательное исполнение')
    pending[p] = text.encode('utf-8')
    p = ROOT / 'Includes/Variables/Include.inc'
    text = p.read_text('utf-8')
    assert 'module MusicPatternState' not in text
    block = '\n                ; Существующие счётчики и операнды паттернов, память не выделяется\n                module MusicPatternState\n'
    for name, (a, note) in facts.FIELDS.items():
        assert len(name) < 16
        block += name.ljust(16) + ('equ #' + format(a, '04X')).ljust(64) + '; ' + note + '\n'
    block += '                endmodule\n'
    pending[p] = text.replace('                endif', block + '\n                endif').encode('utf-8')
    for filename, extra in (
        ('Knowledge.py', "\nfrom MusicPatternFacts import FUNCTIONS as MUSIC_PATTERN_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_PATTERN_FUNCTIONS)\n"),
        ('Contracts.py', '\nfrom MusicPatternFacts import CONTRACTS as MUSIC_PATTERN_CONTRACTS\nCONTRACTS.update(MUSIC_PATTERN_CONTRACTS)\n'),
        ('MusicNotes.py', '\nfrom MusicPatternFacts import COMMENTS as MUSIC_PATTERN_COMMENTS\nCOMMENTS.update(MUSIC_PATTERN_COMMENTS)\n'),
        ('SemanticNames.py', '\nfrom MusicPatternFacts import name_operands as music_pattern_name_operands\nDOCUMENTS.update({("Music", a): ("MusicPattern", "декодирование паттернов") for a in ' + repr(tuple(facts.FUNCTIONS)) + '})\nLABELS.update(' + repr({('Music', a): name for a, name in facts.LABELS.items()}) + ')\n')):
        p = ROOT / 'Tools/Disasm/Research' / filename
        text = p.read_text('utf-8')
        assert 'from MusicPatternFacts import' not in text
        if filename == 'SemanticNames.py':
            needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
            assert text.count(needle) == 1
            text = text.replace(needle, needle + '\n    operation = music_pattern_name_operands(region, function_address, operation)')
        pending[p] = (text + extra).encode('utf-8')
    p = ROOT / 'Docs/Functions.md'
    text = p.read_text('utf-8')
    assert '| Music | 46 | 42 |' in text
    text = text.replace('| Music | 46 | 42 |', '| Music | 49 | 49 |')
    lines = [line for line in text.splitlines() if not any('](../' + f['path'] + ')' in line for f in old)]
    for f in new:
        lines.append('| #' + format(f['address'], '04X') + ' | [Music.' + f['name'] + '](../' + f['path'] + ') | ' + f['description'] + ' |')
    pending[p] = ('\n'.join(lines) + '\n').encode('utf-8')
    p = ROOT / 'Docs/FunctionDetails/Music.md'
    text = p.read_text('utf-8')
    for f in old:
        start = text.index('## ' + f['name'] + '\n')
        end = text.find('\n## ', start + 4)
        end = len(text) if end < 0 else end
        text = text[:start] + text[end:]
    for f in new:
        text += ('\n## ' + f['name'] + '\n\n[Music.' + f['name'] + '](../../' + f['path'] + ') — ' + f['description'] +
                 '.\n\nНачало физического блока #' + format(f['address'], '04X') + ', смещения #' + format(f['offset'], '04X') + '..#' +
                 format(f['end_offset'] - 1, '04X') + '. [Внутренние входы, алгоритм и границы проверки](../MusicPattern.md).\n')
    pending[p] = text.encode('utf-8')
    plan = [(p, p.read_bytes() if p.exists() else None, data) for p, data in pending.items()]
    for p, before, data in plan:
        c = candidate / p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(data)
    for p, before, data in plan:
        assert (p.read_bytes() == before) if before is not None else not p.exists()
    for p, before in {**{p: before for p, before, _ in plan if before is not None}, **old_bytes}.items():
        h = history / p.relative_to(ROOT)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_bytes(before)
    for p, before, data in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for p, before in old_bytes.items():
        assert p.resolve().is_relative_to((ROOT / 'Source/Music').resolve())
        assert p.read_bytes() == before == (history / p.relative_to(ROOT)).read_bytes()
        p.unlink()
    result = dict(passed=True, described_fragments=7, net_new_fragments=3,
                  instructions_changed=0, physical_bytes_preserved=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MusicPatternsClassification.json').write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
