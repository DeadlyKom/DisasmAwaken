"""Отделение доказанного C99B..CB22 от двух неизвестных частей, все ручные строки вне него сохраняются."""
import contextlib
import hashlib
import io
import json
import re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function, operation
from ValidateNotes import validate_notes
import ActionRenderCoefficientsFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read('ActionRenderCoefficientsVerification')
    assert proof['passed'] and proof['total_cases'] == 353280
    assert read('ActionBank4WritesClassification')['passed']
    functions, source_map, symbols, inventory, flow, modified = [read(n) for n in ('Functions', 'SourceMap', 'Symbols', 'Inventory', 'ControlFlow', 'ModifiedCode')]
    old = next(f for f in functions if f['region'] == 'Action' and f['address'] == 0xC88C)
    assert (old['offset'], old['end_offset'], old['semantic_status']) == (0x688C, 0x6EE3, 'unknown')
    old_path = ROOT / old['path']
    old_text = old_path.read_text('utf-8')
    old_range = next(i for i in source_map if i['path'] == old['path'])
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    name, description = facts.FUNCTIONS[0xC99B]
    prefix = dict(old, end_offset=0x699B)
    middle = dict(old, name=name, description=description, address=0xC99B, offset=0x699B, end_offset=0x6B23,
                  semantic_status='described', path='Source/Action/' + name + '.asm')
    suffix = dict(old, name='UnknownCB23', address=0xCB23, offset=0x6B23, path='Source/Action/UnknownCB23.asm')
    region = next(r for r in flow if r['name'] == 'Action')
    instructions = {i['offset']: i for i in region['instructions'] if i['slot'] == 17}
    records = [i for i in region['instructions'] if i['slot'] == 17 and 0x699B <= i['offset'] < 0x6B23]
    assert b''.join(bytes.fromhex(i['hex']) for i in records) == source[0x699B:0x6B23]
    validate_notes([region], {'Action': facts.COMMENTS})
    renames, pending = {}, {}
    for key, value in symbols.items():
        if not key.startswith('Action.UnknownC88C.') or value < 0xC99B:
            continue
        if value < 0xCB23:
            renames[key] = 'Action.' + name + '.' + facts.LOCAL[value]
        else:
            renames[key] = key.replace('Action.UnknownC88C.', 'Action.UnknownCB23.')
    def rename(text):
        for before, after in renames.items():
            text = re.sub(r'\b' + re.escape(before) + r'\b', after, text)
        return text
    # Поиск только ссылок на перемещённые метки, чужие банковые области и остальной код не переоформляются.
    for directory, patterns in (('Source', ('*.asm', '*.inc')), ('Docs', ('*.md',))):
        for pattern in patterns:
            for path in (ROOT / directory).rglob(pattern):
                if path == old_path:
                    continue
                text = path.read_text('utf-8')
                after = rename(text)
                if path.is_relative_to(ROOT / 'Source/Action'):
                    after = after.replace('CALL #C99B', 'CALL @Action.BuildRenderCoefficients.Entry')
                    after = after.replace('CALL #CB23', 'CALL @Action.UnknownCB23.Entry')
                if after != text:
                    lines = []
                    for line in after.splitlines():
                        code, sep, note = line.partition(';')
                        if sep and code.strip() and '@Action.' in code:
                            assert len(code.rstrip()) < 80
                            line = code.rstrip().ljust(80) + ';' + note
                        lines.append(line)
                    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    # Поиск границ по фактической длине каждой инструкции рабочей копии, без механического экспорта соседних функций.
    lines = old_text.splitlines(True)
    position, cuts = old['offset'], {}
    for index, line in enumerate(lines):
        op = operation(line)
        if not op or op.lower().startswith(('module ', 'endmodule')):
            continue
        if position in (0x699B, 0x6B23):
            cuts[position] = index
        position += len(bytes.fromhex(instructions[position]['hex']))
    assert position == old['end_offset'] and set(cuts) == {0x699B, 0x6B23}
    first = rename(''.join(lines[:cuts[0x699B]])).replace('#688C..#6EE2', '#688C..#699A')
    pending[old_path] = (first.rstrip() + '\n\n                endmodule\n                endmodule\n').encode('utf-8')
    header = old_text[:old_text.index('Entry:')].replace('module UnknownC88C', 'module UnknownCB23').replace('#688C..#6EE2', '#6B23..#6EE2')
    tail = rename(''.join(lines[cuts[0x6B23]:]))
    assert tail.startswith('                LD H, #98\n')
    pending[ROOT / suffix['path']] = (header + tail.replace('                LD H, #98\n', 'Entry:          LD H, #98\n', 1)).encode('utf-8')
    text = ['                module Action', '                module ' + name,
            '                ; Документация [точные формулы коэффициентов](../../Docs/ActionRenderCoefficients.md)',
            '                ; -----------------------------------------', '                ; ' + description,
            '                ; исходная запись 17, код ACTION банка 0, адреса C99B..CB22']
    for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), facts.CONTRACTS['Action', 0xC99B]):
        text += ['                ; ' + heading + ':'] + ['                ;   ' + v for v in values]
    text.append('                ; -----------------------------------------')
    for record in records:
        pc = record['address']
        before, right = facts.COMMENTS.get(pc, ([], None))
        text += ['                ; ' + v for v in before]
        op = record['operation'].replace(',', ', ')
        if op.startswith(('JP ', 'JR ')):
            for address, label in facts.LOCAL.items():
                op = op.replace('#' + format(address, '04X'), '@Action.' + name + '.' + label)
        op = facts.name_operands('Action', 0xC99B, op)
        label = 'Entry' if pc == 0xC99B else facts.LOCAL.get(pc, '')
        assert len(label) <= 15
        line = ((label + ':').ljust(16) if label else ' ' * 16) + op
        if right:
            assert len(line) < 80
            line = line.ljust(80) + '; ' + right
        text.append(line)
    text += ['                endmodule', '                endmodule']
    pending[ROOT / middle['path']] = format_function('\n'.join(text) + '\n').encode('utf-8')
    index = functions.index(old)
    functions[index:index + 1] = [prefix, middle, suffix]
    index = source_map.index(old_range)
    source_map[index:index + 1] = [dict(old_range, offset=f['offset'], length=f['end_offset'] - f['offset'], path=f['path'], origin=f['address'],
        sha256=hashlib.sha256(source[f['offset']:f['end_offset']]).hexdigest()) for f in (prefix, middle, suffix)]
    symbols = {renames.get(key, key): value for key, value in symbols.items()}
    for key, value in (('Action.' + name + '.Entry', 0xC99B), ('Action.UnknownCB23.Entry', 0xCB23)):
        assert key not in symbols
        symbols[key] = value
    region['roots'] = sorted(set(region['roots']) | {0xC99B, 0xCB23})
    for item in modified:
        if item['path'] == old['path']:
            item['path'] = prefix['path'] if item['writer'] < 0xC99B else middle['path'] if item['writer'] < 0xCB23 else suffix['path']
    writers = [m for m in modified if m['region'] == 'Action' and 0xC99B <= m['writer'] < 0xCB23]
    assert len(writers) == 18 and {m['target'] for m in writers} == {a for a, _ in facts.OUTPUTS}
    for item in writers:
        item.update(writer_bank=0, target_bank=0, target_region='Action', target_slot=17)
    inventory.update(fragments=len(functions), described=sum(f['semantic_status'] == 'described' for f in functions), unknown=sum(f['semantic_status'] != 'described' for f in functions))
    inventory['ranges_by_kind']['code'] += 2
    for stem, value in (('Functions', functions), ('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory), ('ControlFlow', flow), ('ModifiedCode', modified)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    path = ROOT / 'Source/Files/17_ACTION.inc'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    line = next(l for l in text.splitlines() if 'include "../Action/UnknownC88C.asm"' in l)
    replacement = line
    for f in (middle, suffix):
        replacement += '\n                ent\n                assert $ == #' + format(f['offset'], '04X')
        replacement += '\n                disp #' + format(f['address'], '04X') + '\n                include "../Action/' + f['name'] + '.asm"'
    pending[path] = text.replace(line, replacement).encode('utf-8')
    path = ROOT / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    assert 'module ActionRenderCoefficientsState' not in text
    block = '\n                ; Раздельные существующие операнды коэффициентов и три исходные фазы\n                module ActionRenderCoefficientsState\n'
    for address, label in (*facts.OUTPUTS, *((0x9B12 + i, 'Phase' + str(i)) for i in range(3))):
        note = 'непосредственный байт коэффициента следующего вычислителя' if label.startswith('Coeff') else 'байтовая фаза исходной синусоиды'
        block += (label.ljust(16) + 'equ #' + format(address, '04X')).ljust(80) + '; ' + note + '\n'
    pending[path] = text.replace('                endif', block + '                endmodule\n\n                endif').encode('utf-8')
    path = ROOT / 'Includes/Const/Include.inc'
    text = path.read_text('utf-8')
    assert 'module ActionRenderCoefficientsConst' not in text
    block = '\n                ; Исходные параметры выбора и единичного коэффициента\n                module ActionRenderCoefficientsConst\n'
    block += 'OneAxisBit      equ #00'.ljust(80) + '; номер бита режима одной фазы\n'
    block += 'Unit            equ #7F'.ljust(80) + '; исходный единичный байтовый коэффициент\n                endmodule\n\n'
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    for filename, extra in (
        ('Knowledge.py', "\nfrom ActionRenderCoefficientsFacts import FUNCTIONS as ACTION_RENDER_COEFFICIENTS_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_RENDER_COEFFICIENTS_FUNCTIONS)\n"),
        ('Contracts.py', "\nfrom ActionRenderCoefficientsFacts import CONTRACTS as ACTION_RENDER_COEFFICIENTS_CONTRACTS\nCONTRACTS.update(ACTION_RENDER_COEFFICIENTS_CONTRACTS)\n")):
        path = ROOT / 'Tools/Disasm/Research' / filename
        text = path.read_text('utf-8')
        assert extra.splitlines()[1] not in text
        pending[path] = (text + extra).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/SemanticNames.py'
    text = path.read_text('utf-8')
    needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
    assert text.count(needle) == 1
    text = text.replace(needle, needle + '\n    operation = action_render_coefficients_name_operands(region, function_address, operation)')
    text += "\nfrom ActionRenderCoefficientsFacts import name_operands as action_render_coefficients_name_operands\nDOCUMENTS['Action',0xC99B]=('ActionRenderCoefficients','точные формулы коэффициентов')\n"
    text += 'LABELS.update(' + repr({('Action', a): n for a, n in facts.LOCAL.items()}) + ')\n'
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '\n\nif __name__ == "__main__":'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, "\nfrom ActionRenderCoefficientsFacts import COMMENTS as ACTION_RENDER_COEFFICIENTS_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_RENDER_COEFFICIENTS_COMMENTS)\n" + needle).encode('utf-8')
    path = ROOT / 'Docs/Functions.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    text = re.sub(r'\| Action \| \d+ \| \d+ \|', '| Action | ' + str(sum(f['region'] == 'Action' for f in functions)) + ' | ' + str(sum(f['region'] == 'Action' and f['semantic_status'] == 'described' for f in functions)) + ' |', text)
    line = next(l for l in text.splitlines() if '[Action.UnknownC88C]' in l)
    rows = '\n'.join('| #' + format(f['address'], '04X') + ' | [Action.' + f['name'] + '](../' + f['path'] + ') | ' + f['description'] + ' |' for f in (prefix, middle, suffix))
    pending[path] = text.replace(line, rows).encode('utf-8')
    path = ROOT / 'Docs/FunctionDetails/Action.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    start = text.index('## UnknownC88C\n')
    end = text.find('\n## ', start + 4)
    assert end > start
    sections = ''.join('## ' + f['name'] + '\n\n[Action.' + f['name'] + '](../../' + f['path'] + ')\n\n' + f['description'] + '.\n\n' for f in (prefix, middle, suffix))
    sections += '[Построитель и границы локального доказательства](../ActionRenderCoefficients.md).\n\n'
    pending[path] = (text[:start] + sections + text[end:]).encode('utf-8')
    path = ROOT / 'Docs/ModifiedCode.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    changed = []
    for line in text.splitlines():
        match = re.match(r'\| Action \| #([0-9A-F]{4}) \|', line)
        if match and 0xC99B <= int(match[1], 16) < 0xCB23:
            line = line.replace('UnknownC88C.asm', name + '.asm')
        elif match and int(match[1], 16) >= 0xCB23 and 'Source/Action/UnknownC88C.asm' in line:
            line = line.replace('UnknownC88C.asm', 'UnknownCB23.asm')
        changed.append(line)
    changed += ['', '## Девять коэффициентов ACTION', '',
        '[BuildRenderCoefficients](ActionRenderCoefficients.md) имеет 18 прямых писателей девяти раздельных байтов Coeff11..Coeff33. '
        'Писатель и цель находятся в банке 0, записи OBJECT3D банка 4 по совпадающим адресам выделены в отдельный реестр. '
        'Новая непрерывная область матрицы не создаётся.']
    pending[path] = ('\n'.join(changed) + '\n').encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionRenderCoefficients'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionRenderCoefficients'
    assert not candidate.exists() and not history.exists()
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    # Создание кандидата, сверка рабочей копии и сохранение точной истории, индекс Git не затрагивается.
    for path, before, after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, before, after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path, before, after in plan:
        if before is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True, described_functions=1, confirmed_code_bytes=392, confirmed_instructions=len(records),
        remaining_unknown_prefix_bytes=271, remaining_unknown_suffix_bytes=960, model_cases=353280,
        self_modifying_writers_registered=18, original_bytes_preserved=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderCoefficientsClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
