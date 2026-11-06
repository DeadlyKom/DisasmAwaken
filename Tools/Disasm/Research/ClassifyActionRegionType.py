"""Точечная публикация классификатора ACTION, кандидат и защита ручных изменений."""
from pathlib import Path
import contextlib
import io
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionRegionTypeFacts as facts


def main(facts=facts, tag='ActionTextDisplay', document='ActionTextDisplay', state_fields=None, allow_named=False, include_blocks=()):
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read(tag + 'Verification')
    assert proof['passed']
    if tag == 'ActionTextDisplay':
        assert proof['cases_by_kind']['shared_rows'] == 4096
    functions = read('Functions')
    selected = [f for f in functions if f['region'] == 'Action' and f['address'] in facts.FUNCTIONS]
    assert len(selected) == len(facts.FUNCTIONS)
    if allow_named:
        # Проверка отсутствия доказанного договора у уже именованной процедуры перед его заменой.
        assert all('Unknown, регистровый контракт ещё не доказан' in (ROOT/f['path']).read_text('utf-8') for f in selected)
    else:
        assert all(f['semantic_status'] == 'unknown' for f in selected)
    old = {f['address']: dict(f) for f in selected}
    candidate = ROOT / ('Tools/Disasm/Research/Candidates/' + tag)
    history = ROOT / ('Tools/Disasm/Research/History/Before' + tag)
    assert not candidate.exists() and not history.exists()
    pending, removed = {}, {}

    def rename(text):
        for before, after in facts.RENAMES.items():
            text = re.sub(r'\b' + re.escape(before) + r'\b', after, text)
        for address, f in old.items():
            name = facts.FUNCTIONS[address][0]
            text = text.replace('/Action/' + f['name'] + '.asm', '/Action/' + name + '.asm')
            text = text.replace('[' + f['name'] + '.asm]', '[' + name + '.asm]')
            text = text.replace('продолжение в ' + f['name'] + '.asm', 'продолжение в ' + name + '.asm')
            text = text.replace('Action.' + f['name'], 'Action.' + name)
            text = text.replace('## ' + f['name'] + '\n', '## ' + name + '\n')
        return text

    # Поиск только ссылок на переименовываемые функции, без переоформления остальных строк.
    for folder, pattern in (('Source', '*.asm'), ('Source', '*.inc'), ('Docs', '*.md')):
        for path in (ROOT / folder).rglob(pattern):
            before = path.read_text('utf-8')
            after = rename(before)
            if before != after:
                lines = after.splitlines()
                for index, line in enumerate(lines):
                    code, sep, note = line.partition(';')
                    if sep and code.strip() and ('@Action.' in code or code.lstrip().startswith('include ')):
                        assert len(code.rstrip()) < 80
                        lines[index] = code.rstrip().ljust(80) + ';' + note
                pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    symbols = read('Symbols')
    for before, after in facts.RENAMES.items():
        assert before in symbols and after not in symbols, (before, after)
        symbols[after] = symbols.pop(before)
    controls = next(item for item in read('ControlFlow') if item['name'] == 'Action')
    # Проверка новых внутренних входов только на границах уже декодированных инструкций выбранных функций.
    for key,value in getattr(facts,'ADDITIONAL_SYMBOLS',{}).items():
        assert key.startswith('Action.') and key not in symbols
        assert any(f['address']<=value<f['address']+f['end_offset']-f['offset'] for f in selected)
        assert any(i['address']==value for i in controls['instructions'])
        symbols[key]=value
    validate_notes([controls], {'Action': facts.COMMENTS})
    labels = {address: name for name, address in symbols.items() if name.startswith('Action.')}
    for f in selected:
        address = f['address']
        if f['name'] != facts.FUNCTIONS[address][0]:
            removed[ROOT / f['path']] = (ROOT / f['path']).read_bytes()
        pending.pop(ROOT / f['path'], None)
        name, description = facts.FUNCTIONS[address]
        f.update(name=name, description=description, semantic_status='described', path='Source/Action/' + name + '.asm')
        lines = ['                module Action', '                module ' + name,
                 '                ; Документация [алгоритм и проверка](../../Docs/' + document + '.md)',
                 '                ; -----------------------------------------', '                ; ' + description,
                 '                ; исходная запись ' + str(f['slot']) + ', ' + getattr(facts, 'LOCATION', {}).get(address, 'перенесённое ядро 6000..7F8E') + ', смещения #' + format(f['offset'], '04X') + '..#' + format(f['end_offset'] - 1, '04X')]
        for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), facts.CONTRACTS['Action', address]):
            lines += ['                ; ' + heading + ':'] + ['                ;   ' + value for value in values]
        lines += ['                ; -----------------------------------------']
        for instruction in controls['instructions']:
            if instruction['slot'] != f['slot'] or not f['offset'] <= instruction['offset'] < f['end_offset']:
                continue
            pc = instruction['address']
            before, right = facts.COMMENTS.get(pc, ([], None))
            lines += ['                ; ' + text for text in before]
            operation = instruction['operation'].replace(',', ', ')
            if operation.startswith(('JP ', 'JR ', 'CALL ', 'DJNZ ')):
                operation = re.sub(r'#([0-9A-F]{4})', lambda m: '@' + labels[int(m[1], 16)] if int(m[1], 16) in labels else m[0], operation)
            operation = facts.name_operands('Action', address, operation)
            if hasattr(facts, 'name_instruction'):
                operation = facts.name_instruction('Action', address, pc, operation)
            label = 'Entry' if pc == address else facts.LOCAL.get(pc, '')
            assert len(label) <= 15, ('метка выходит за начало кода', label)
            line = ((label + ':').ljust(16) if label else ' ' * 16) + operation
            if right:
                assert len(line) < 80
                line = line.ljust(80) + '; ' + right
            lines.append(line)
        lines += ['                endmodule', '                endmodule']
        following = getattr(facts, 'CONTINUATIONS', {0xEFC4: 0xEFF1}).get(address)
        target = None if following is None else next(f for f in functions if f['region']=='Action' and f['address']==following)
        continuation = None if target is None else dict(region='Action', name=target['name'],path=target['path'])
        # Выбор окончательного имени продолжения, даже если соседний участник этого пакета ещё не обработан циклом.
        if target is not None and target['address'] in facts.FUNCTIONS:
            target_name=facts.FUNCTIONS[target['address']][0]
            continuation=dict(region='Action',name=target_name,path='Source/Action/'+target_name+'.asm')
        pending[ROOT / f['path']] = format_function('\n'.join(lines) + '\n', continuation).encode('utf-8')
    source_map = read('SourceMap')
    for item in source_map:
        for f in selected:
            if item['path'] == old[f['address']]['path']:
                item['path'] = f['path']
    modified = read('ModifiedCode')
    for item in modified:
        item['path'] = rename(item['path'])
    if hasattr(facts, 'qualify_mutations'):
        facts.qualify_mutations(modified, read('ControlFlow'), functions)
    inventory = read('Inventory')
    inventory.update(described=sum(f['semantic_status'] == 'described' for f in functions),
                     unknown=sum(f['semantic_status'] != 'described' for f in functions))
    for stem, value in (('Functions', functions), ('Symbols', symbols), ('SourceMap', source_map), ('ModifiedCode', modified), ('Inventory', inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    # Именование существующих изменяемых операндов, дополнительной RAM нет.
    path = ROOT / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    assert 'module ' + tag + 'State' not in text
    block = '\n                ; Существующее состояние, память не выделяется\n                module ' + tag + 'State\n'
    default_fields = (('ActiveString', 0xECA3, 'указатель следующего байта активной строки'),
                              ('ReadCursor', 0xECAA, 'последний прочитанный элемент очереди'),
                              ('TextColumn', 0xEFD6, 'байтовая колонка следующего знака'),
                              ('SavedScrollSP', 0xEFC1, 'входной SP на время экранных POP и PUSH'))
    for name, value, note in (default_fields if state_fields is None else state_fields):
        assert len(name) <= 15, ('имя константы выходит за начало equ', name)
        block += name.ljust(16) + ('equ #' + format(value, '04X')).ljust(64) + '; ' + note + '\n'
    block += '                endmodule\n'
    if state_fields != ():
        pending[path] = text.replace('                endif', block + '\n                endif').encode('utf-8')
    prefix = re.sub(r'(?<!^)(?=[A-Z][a-z])', '_', tag).upper()
    operand_handler = prefix.lower() + '_name_operands'
    for filename, extra in (
        ('Knowledge.py', f"\nfrom {tag}Facts import FUNCTIONS as {prefix}_FUNCTIONS\nFUNCTIONS['Action'].update({prefix}_FUNCTIONS)\n"),
        ('Contracts.py', f'\nfrom {tag}Facts import CONTRACTS as {prefix}_CONTRACTS\nCONTRACTS.update({prefix}_CONTRACTS)\n'),
        ('SemanticNames.py', f'\nfrom {tag}Facts import LABELS as {prefix}_LABELS, name_operands as {operand_handler}\nLABELS.update({prefix}_LABELS)\nDOCUMENTS.update({{("Action", a): ("{document}", "алгоритм и проверка") for a in {tuple(facts.FUNCTIONS)}}})\n'),
        ('ExportSources.py', f'\nfrom {tag}Facts import COMMENTS as {prefix}_COMMENTS\nREGION_COMMENTS.setdefault("Action", {{}}).update({prefix}_COMMENTS)\n')):
        path = ROOT / 'Tools/Disasm/Research' / filename
        text = path.read_text('utf-8')
        assert extra.splitlines()[1] not in text
        if filename == 'SemanticNames.py':
            needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
            assert text.count(needle) == 1
            text = text.replace(needle, needle + '\n    operation = ' + operand_handler + '(region, function_address, operation)')
            if hasattr(facts, 'name_instruction'):
                instruction_handler = operand_handler + '_instruction'
                needle = '    return point_motion_instruction(region, function_address, address, operation)'
                assert text.count(needle) == 1
                text = text.replace(needle, '    operation = ' + instruction_handler + '(region, function_address, address, operation)\n' + needle)
                extra += f'\nfrom {tag}Facts import name_instruction as {instruction_handler}\n'
        if filename == 'ExportSources.py':
            needle = '\n\nif __name__ == "__main__":'
            assert text.count(needle) == 1
            text = text.replace(needle, '\n' + extra + needle)
        else:
            text += extra
        pending[path] = text.encode('utf-8')
    for name in ('Docs/Functions.md', 'Docs/FunctionDetails/Action.md'):
        path = ROOT / name
        text = pending.get(path, path.read_bytes()).decode('utf-8')
        if name == 'Docs/Functions.md':
            count = sum(f['region'] == 'Action' and f['semantic_status'] == 'described' for f in functions)
            total = sum(f['region'] == 'Action' for f in functions)
            text = re.sub(r'\| Action \| \d+ \| \d+ \|', f'| Action | {total} | {count} |', text)
            for f in selected:
                previous_description = old[f['address']]['description']
                needle = '| #' + format(f['address'], '04X') + ' | [Action.' + f['name'] + '](../' + f['path'] + ') | ' + previous_description + ' |'
                assert text.count(needle) == 1
                text = text.replace(needle, needle.replace(previous_description, f['description']))
        else:
            for f in selected:
                start = text.index('## ' + f['name'] + '\n')
                end = text.find('\n## ', start + 4)
                end = len(text) if end < 0 else end
                previous_description = old[f['address']]['description']
                block = text[start:end].replace(previous_description + '.', f['description'] + '.')
                text = text[:start] + block.rstrip() + '\n\n[Алгоритм, контракты и проверка](../' + document + '.md).\n' + text[end:]
        pending[path] = text.encode('utf-8')
    # Подключение только явно переданных структур и констант в тот же проверяемый кандидат.
    for relative, unique_marker, block in include_blocks:
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT.resolve())
        text = pending.get(path, path.read_bytes()).decode('utf-8')
        assert unique_marker not in text and text.count('                endif') == 1
        pending[path] = text.replace('                endif', block + '\n                endif').encode('utf-8')
    # Создание отдельного кандидата до замены активных файлов.
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for path, before, after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    # Проверка отсутствия новых ручных изменений после чтения рабочей копии.
    for path, before, after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path, before in {**{p: b for p, b, _ in plan if b is not None}, **removed}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    # Удаление только прежних имён после проверки точного совпадения инструкций и сохранённой копии.
    for path, before in removed.items():
        assert path.resolve().is_relative_to((ROOT / 'Source/Action').resolve())
        assert path.read_bytes() == before == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    result = dict(passed=True, described_functions=len(selected), instructions_changed=0,
        physical_bytes_preserved=True, model_cases=proof.get('total_cases', proof.get('original_position_cases', proof.get('original_calls'))),
        original_function_boundaries_preserved=True, assembly_executed=False)
    (ROOT / ('Tools/Disasm/Reports/' + tag + 'Classification.json')).write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(facts, 'ActionRegionType', 'ActionRegionType', ())
