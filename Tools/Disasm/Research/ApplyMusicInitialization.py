"""Четыре точных договора и именованные существующие поля, без изменения инструкций."""
from pathlib import Path
import contextlib, io, json, re, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm'), str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import MusicInitializationFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('MusicInitializeAndMuteVerification')['passed']
    candidate = ROOT/'Tools/Disasm/Research/Candidates/MusicInitialization'
    history = ROOT/'Tools/Disasm/Research/History/BeforeMusicInitialization'
    assert not candidate.exists() and not history.exists()
    pending = {}
    functions = read('Functions')
    selected = [f for f in functions if f['region'] == 'Music' and f['address'] in facts.FUNCTIONS]
    assert len(selected) == 4
    old_descriptions = {f['address']: f['description'] for f in selected}
    symbols = read('Symbols')
    for old, new in facts.RENAMES.items():
        assert old in symbols and new not in symbols
        symbols[new] = symbols.pop(old)
    def rename(text):
        for old, new in facts.RENAMES.items():
            text = re.sub(r'\b'+re.escape(old)+r'\b', new, text)
        return text
    for folder, pattern in (('Source', '*.asm'), ('Docs', '*.md')):
        for p in (ROOT/folder).rglob(pattern):
            before = p.read_text('utf-8')
            after = rename(before)
            if before != after:
                pending[p] = after.encode('utf-8')
    flow = read('ControlFlow')
    music = next(item for item in flow if item['name'] == 'Music')
    validate_notes([music], {'Music': facts.COMMENTS})
    labels = {address: key for key, address in symbols.items() if key.startswith('Music.')}
    for f in selected:
        a = f['address']
        f['description'] = facts.FUNCTIONS[a][1]
        lines = ['                module Music', '                module '+f['name'],
                 '                ; Документация [инициализация и глушение AY](../../Docs/MusicInitialization.md)',
                 '                ; -----------------------------------------', '                ; '+f['description'],
                 '                ; исходная запись 10, файловые смещения #'+format(f['offset'], '04X')+'..#'+format(f['end_offset']-1, '04X')]
        for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), facts.CONTRACTS['Music', a]):
            lines += ['                ; '+heading+':']+['                ;   '+value for value in values]
        lines += ['                ; -----------------------------------------']
        for instruction in music['instructions']:
            if not f['offset'] <= instruction['offset'] < f['end_offset']:
                continue
            address = instruction['address']
            before, right = facts.COMMENTS.get(address, ([], None))
            lines += ['                ; '+value for value in before]
            operation = instruction['operation'].replace(',', ', ')
            if operation.startswith(('JP ', 'JR ', 'CALL ', 'DJNZ ')):
                operation = re.sub(r'#([0-9A-F]{4})', lambda match: '@'+labels[int(match[1], 16)]
                                   if int(match[1], 16) in labels else match[0], operation)
            operation = facts.name_operands('Music', a, operation)
            label = 'Entry' if address == a else facts.LABELS.get(('Music', address), '')
            line = ((label+':').ljust(16) if label else ' '*16)+operation
            if right:
                assert len(line) < 80
                line = line.ljust(80)+'; '+right
            lines.append(line)
        lines += ['                endmodule', '                endmodule']
        continuation = next(f for f in selected if f['address'] == 0xDB7C) if a == 0xDB0A else None
        pending[ROOT/f['path']] = format_function('\n'.join(lines)+'\n', continuation).encode('utf-8')
    for stem, value in (('Symbols', symbols), ('Functions', functions)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')] = encoded(value)
    p = ROOT/'Includes/Variables/Include.inc'
    text = p.read_text('utf-8')
    assert 'module MusicInitializeState' not in text
    block = ('\n                ; Существующий изменяемый операнд восстановления SP, память не выделяется\n'
             '                module MusicInitializeState\n'+
             'SavedStack'.ljust(16)+'equ #DB4D'.ljust(64)+'; слово SP в исходной команде LD SP, nn\n'
             '                endmodule\n')
    pending[p] = text.replace('                endif', block+'\n                endif').encode('utf-8')
    for filename, extra in (
        ('Knowledge.py', "\nfrom MusicInitializationFacts import FUNCTIONS as MUSIC_INITIALIZATION_FUNCTIONS\nFUNCTIONS['Music'].update(MUSIC_INITIALIZATION_FUNCTIONS)\n"),
        ('Contracts.py', '\nfrom MusicInitializationFacts import CONTRACTS as MUSIC_INITIALIZATION_CONTRACTS\nCONTRACTS.update(MUSIC_INITIALIZATION_CONTRACTS)\n'),
        ('MusicNotes.py', '\nfrom MusicInitializationFacts import COMMENTS as MUSIC_INITIALIZATION_COMMENTS\nCOMMENTS.update(MUSIC_INITIALIZATION_COMMENTS)\n'),
        ('SemanticNames.py', '\nfrom MusicInitializationFacts import LABELS as MUSIC_INITIALIZATION_LABELS, name_operands as music_initialization_name_operands\nLABELS.update(MUSIC_INITIALIZATION_LABELS)\nDOCUMENTS.update({("Music", a): ("MusicInitialization", "инициализация и глушение AY") for a in (0xDB00, 0xDB08, 0xDB0A, 0xDB7C)})\n')):
        p = ROOT/'Tools/Disasm/Research'/filename
        text = p.read_text('utf-8')
        assert 'from MusicInitializationFacts import' not in text
        if filename == 'SemanticNames.py':
            needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
            assert text.count(needle) == 1
            text = text.replace(needle, needle+'\n    operation = music_initialization_name_operands(region, function_address, operation)')
        pending[p] = (text+extra).encode('utf-8')
    for name in ('Docs/Functions.md', 'Docs/FunctionDetails/Music.md'):
        p = ROOT/name
        text = pending.get(p, p.read_bytes()).decode('utf-8')
        for f in selected:
            assert old_descriptions[f['address']] in text
            text = text.replace(old_descriptions[f['address']], f['description'])
        if name.endswith('Music.md'):
            for f in selected:
                start = text.index('## '+f['name']+'\n')
                end = text.find('\n## ', start+4)
                end = len(text) if end < 0 else end
                block = text[start:end].rstrip()+'\n\n[Точный контракт и проверка памяти](../MusicInitialization.md).\n'
                text = text[:start]+block+text[end:]
        pending[p] = text.encode('utf-8')
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for p, before, after in plan:
        c = candidate/p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(after)
    for p, before, after in plan:
        assert (p.read_bytes() == before) if before is not None else not p.exists()
    for p, before, after in plan:
        if before is not None:
            h = history/p.relative_to(ROOT)
            h.parent.mkdir(parents=True, exist_ok=True)
            h.write_bytes(before)
    for p, before, after in plan:
        p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True, refined_contracts=4, instructions_changed=0, physical_bytes_preserved=True,
                  mute_af_exhaustive=True, initialization_partial_reset_explicit=True, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MusicInitializationClassification.json').write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
