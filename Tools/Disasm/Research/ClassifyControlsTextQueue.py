"""Производитель очереди и 34 физических байта, с кандидатом и сохранением прежних исходников."""
from pathlib import Path
import collections, contextlib, io, json, re, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm'), str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ControlsTextQueueFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsTextQueueVerification')['passed']
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ControlsTextQueue'
    history = ROOT/'Tools/Disasm/Research/History/BeforeControlsTextQueue'
    assert not candidate.exists() and not history.exists()
    pending, removed = {}, {}
    functions = read('Functions')
    selected = [f for f in functions if f['region'] == 'Controls' and f['address'] in facts.FUNCTIONS]
    assert len(selected) == 2 and all(f['semantic_status'] == 'unknown' for f in selected)
    previous = {f['address']: dict(f) for f in selected}
    symbols = read('Symbols')
    for old, new in facts.RENAMES.items():
        assert old in symbols and new not in symbols
        symbols[new] = symbols.pop(old)
    def rename(text):
        for old, new in facts.RENAMES.items():
            text = re.sub(r'\b'+re.escape(old)+r'\b', new, text)
        for old in previous.values():
            name = facts.FUNCTIONS[old['address']][0]
            text = text.replace('/Controls/'+old['name']+'.asm', '/Controls/'+name+'.asm')
            text = text.replace('Controls.'+old['name'], 'Controls.'+name)
            text = text.replace('## '+old['name']+'\n', '## '+name+'\n')
        return text
    for folder, pattern in (('Source', '*.asm'), ('Source', '*.inc'), ('Docs', '*.md')):
        for p in (ROOT/folder).rglob(pattern):
            before = p.read_text('utf-8')
            after = rename(before)
            if before != after:
                lines = after.splitlines()
                for index, line in enumerate(lines):
                    code, sep, note = line.partition(';')
                    if sep and code.strip() and (code.lstrip().startswith('include ') or '@Controls.' in code):
                        assert len(code.rstrip()) < 80
                        lines[index] = code.rstrip().ljust(80)+';'+note
                pending[p] = ('\n'.join(lines)+'\n').encode('utf-8')
    flow = read('ControlFlow')
    controls = next(item for item in flow if item['name'] == 'Controls')
    validate_notes([controls], {'Controls': facts.COMMENTS})
    labels = {address: key for key, address in symbols.items() if key.startswith('Controls.')}
    for f in selected:
        a = f['address']
        old_path = ROOT/f['path']
        removed[old_path] = old_path.read_bytes()
        pending.pop(old_path, None)
        f.update(name=facts.FUNCTIONS[a][0], description=facts.FUNCTIONS[a][1], semantic_status='described',
                 path='Source/Controls/'+facts.FUNCTIONS[a][0]+'.asm')
        lines = ['                module Controls', '                module '+f['name'],
                 '                ; Документация [производитель текстовой очереди](../../Docs/TextQueueProducer.md)',
                 '                ; -----------------------------------------', '                ; '+f['description'],
                 '                ; исходная запись 23, банк 1, файловые смещения #'+format(f['offset'], '04X')+'..#'+format(f['end_offset']-1, '04X')]
        for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), facts.CONTRACTS['Controls', a]):
            lines += ['                ; '+heading+':']+['                ;   '+value for value in values]
        lines += ['                ; -----------------------------------------']
        for instruction in controls['instructions']:
            if instruction['slot'] != 23 or not f['offset'] <= instruction['offset'] < f['end_offset']:
                continue
            address = instruction['address']
            before, right = facts.COMMENTS.get(address, ([], None))
            lines += ['                ; '+value for value in before]
            operation = instruction['operation'].replace(',', ', ')
            if operation.startswith(('JP ', 'JR ', 'CALL ', 'DJNZ ')):
                operation = re.sub(r'#([0-9A-F]{4})', lambda match: '@'+labels[int(match[1], 16)] if int(match[1], 16) in labels else match[0], operation)
            operation = facts.name_operands('Controls', a, operation)
            label = 'Entry' if address == a else facts.LABELS.get(('Controls', address), '')
            line = ((label+':').ljust(16) if label else ' '*16)+operation
            if right:
                assert len(line) < 80
                line = line.ljust(80)+'; '+right
            lines.append(line)
        lines += ['                endmodule', '                endmodule']
        continuation = dict(region='Controls', name='QueueTextItem', path='Source/Controls/QueueTextItem.asm') if a == 0xEC56 else None
        pending[ROOT/f['path']] = format_function('\n'.join(lines)+'\n', continuation).encode('utf-8')
    source_map = read('SourceMap')
    for item in source_map:
        for a, old in previous.items():
            if item['path'] == old['path']:
                item['path'] = 'Source/Controls/'+facts.FUNCTIONS[a][0]+'.asm'
    entry = next(item for item in source_map if item['slot'] == 23 and item['offset'] == 0x11A2)
    assert entry['length'] == 34 and entry['kind'] == 'unclassified'
    raw_source = (ROOT/'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    old_binary = ROOT/entry['path']
    assert old_binary.read_bytes() == raw_source[0x11A2:0x11C4]
    removed[old_binary] = old_binary.read_bytes()
    table_text, table_symbols = facts.render(raw_source)
    assert facts.parse(table_text) == (raw_source[0x11A2:0x11C4], table_symbols)
    assert not any(key in symbols for key in table_symbols)
    symbols.update(table_symbols)
    pending[ROOT/facts.TABLE[1]] = table_text.encode('utf-8')
    entry.update(kind='typed_data', path=facts.TABLE[1], origin=0xEC80)
    modified = read('ModifiedCode')
    for item in modified:
        if item['region'] == 'Controls':
            item['path'] = rename(item['path'])
            if item['target'] == 0xEC5D:
                item.update(writer_bank=1, target_bank=1, target_region='Controls', target_slot=23)
    inventory = read('Inventory')
    inventory.update(described=sum(f['semantic_status'] == 'described' for f in functions),
                     unknown=sum(f['semantic_status'] != 'described' for f in functions),
                     ranges_by_kind=dict(collections.Counter(item['kind'] for item in source_map)))
    inventory['physical_bytes_by_kind'] = {kind: sum(item['length'] for item in source_map if item['kind'] == kind) for kind in inventory['physical_bytes_by_kind']}
    for stem, value in (('Functions', functions), ('Symbols', symbols), ('SourceMap', source_map), ('ModifiedCode', modified), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')] = encoded(value)
    p = ROOT/'Source/Files/23_CONTROL.inc'
    text = pending.get(p, p.read_bytes()).decode('utf-8')
    needle = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/23_CONTROL/Unclassified008.bin"'
    assert text.count(needle) == 1
    pending[p] = text.replace(needle, '                disp #EC80\n                include "../Controls/Data/TextQueue.asm"\n                ent').encode('utf-8')
    p = ROOT/'Includes/Structs/Include.inc'
    text = p.read_text('utf-8')
    assert 'struct FTextQueueItem' not in text
    block = '\n                ; Числовая запись либо указатель строки, старший байт хранится первым\n                struct FTextQueueItem\n'
    for name, width, note in facts.FIELDS:
        block += name.ljust(16)+'db #01'.ljust(64)+'; '+note+'\n'
    block += '                ends\n                assert FTextQueueItem == 2\n\n                ; Динамический кадр производителя очереди, статической памяти нет\n                struct FTextQueueInsertFrame\n'
    for name, note in (('SavedAF', 'входной AF, младший байт F'), ('SavedBC', 'сохранённый BC'), ('SavedHL', 'сохранённый HL'), ('CallerReturn', 'внешний адрес возврата')):
        block += name.ljust(16)+'dw #0000'.ljust(64)+'; '+note+'\n'
    block += '                ends\n                assert FTextQueueInsertFrame == 8\n'
    pending[p] = text.replace('                endif', block+'\n                endif').encode('utf-8')
    p = ROOT/'Includes/Variables/Include.inc'
    text = p.read_text('utf-8')
    block = ('\n                ; Существующий изменяемый операнд в банке 1, память не выделяется\n                module ControlsTextQueueState\n'+
             'WriteCursor'.ljust(16)+'equ #EC5D'.ljust(64)+'; адрес следующего проверяемого элемента в LD HL, nn\n                endmodule\n')
    assert 'module ControlsTextQueueState' not in text
    pending[p] = text.replace('                endif', block+'\n                endif').encode('utf-8')
    p = ROOT/'Includes/Const/Include.inc'
    text = p.read_text('utf-8')
    block = '\n                ; Числовые коды и лимит очереди, не набор битовых флагов\n                module TextQueueConst\n'
    for name, value, note in (('End', 0, 'конечный маркер кольца'), ('Free', 1, 'свободная запись'), ('Number', 2, 'числовое значение в LowValue'), ('Capacity', 16, 'максимум чтений, маркер входит в лимит')):
        block += name.ljust(16)+('equ #'+format(value, '02X')).ljust(64)+'; '+note+'\n'
    block += '                endmodule\n'
    assert 'module TextQueueConst' not in text
    pending[p] = text.replace('                endif', block+'\n                endif').encode('utf-8')
    for filename, extra in (
        ('Knowledge.py', "\nfrom ControlsTextQueueFacts import FUNCTIONS as CONTROLS_TEXT_QUEUE_FUNCTIONS\nFUNCTIONS['Controls'].update(CONTROLS_TEXT_QUEUE_FUNCTIONS)\n"),
        ('Contracts.py', '\nfrom ControlsTextQueueFacts import CONTRACTS as CONTROLS_TEXT_QUEUE_CONTRACTS\nCONTRACTS.update(CONTROLS_TEXT_QUEUE_CONTRACTS)\n'),
        ('SemanticNames.py', '\nfrom ControlsTextQueueFacts import LABELS as CONTROLS_TEXT_QUEUE_LABELS, name_operands as controls_text_queue_name_operands\nLABELS.update(CONTROLS_TEXT_QUEUE_LABELS)\nDOCUMENTS.update({("Controls", a): ("TextQueueProducer", "производитель текстовой очереди") for a in (0xEC56, 0xEC59)})\n'),
        ('ExportSources.py', '\nfrom ControlsTextQueueFacts import COMMENTS as CONTROLS_TEXT_QUEUE_COMMENTS\nREGION_COMMENTS.setdefault("Controls", {}).update(CONTROLS_TEXT_QUEUE_COMMENTS)\n')):
        p = ROOT/'Tools/Disasm/Research'/filename
        text = p.read_text('utf-8')
        if filename == 'SemanticNames.py':
            needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
            assert text.count(needle) == 1
            text = text.replace(needle, needle+'\n    operation = controls_text_queue_name_operands(region, function_address, operation)')
        if filename == 'ExportSources.py':
            needle = '\n\nif __name__ == "__main__":'
            assert text.count(needle) == 1
            text = text.replace(needle, '\n'+extra+needle)
        else:
            text += extra
        pending[p] = text.encode('utf-8')
    p = ROOT/'Docs/Functions.md'
    text = pending.get(p, p.read_bytes()).decode('utf-8').replace('| Controls | 67 | 1 |', '| Controls | 67 | 3 |')
    for f in selected:
        needle = '| #'+format(f['address'], '04X')+' | [Controls.'+f['name']+'](../'+f['path']+') | Unknown, назначение этого фрагмента ещё не установлено |'
        assert text.count(needle) == 1
        text = text.replace(needle, needle.replace('Unknown, назначение этого фрагмента ещё не установлено', f['description']))
    pending[p] = text.encode('utf-8')
    p = ROOT/'Docs/FunctionDetails/Controls.md'
    text = pending.get(p, p.read_bytes()).decode('utf-8')
    for f in selected:
        start = text.index('## '+f['name']+'\n')
        end = text.find('\n## ', start+4)
        end = len(text) if end < 0 else end
        block = text[start:end].replace('Unknown, назначение этого фрагмента ещё не установлено.', f['description']+'.')
        text = text[:start]+block.rstrip()+'\n\n[Алгоритм, рамка стека и условия отказа](../TextQueueProducer.md).\n'+text[end:]
    pending[p] = text.encode('utf-8')
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for p, before, after in plan:
        c = candidate/p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(after)
    for p, before, after in plan:
        assert (p.read_bytes() == before) if before is not None else not p.exists()
    for p, before in {**{p: before for p, before, _ in plan if before is not None}, **removed}.items():
        h = history/p.relative_to(ROOT)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_bytes(before)
    for p, before, after in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for p, before in removed.items():
        assert p.resolve().is_relative_to((ROOT/'Source').resolve()) and p.read_bytes() == before == (history/p.relative_to(ROOT)).read_bytes()
        p.unlink()
    result = dict(passed=True, described_functions=2, typed_bytes=34, physical_records=17,
                  physical_bytes_preserved=True, instructions_changed=0, bounded_wrap_quirk_preserved=True,
                  full_consumer_contract_proved=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsTextQueueClassification.json').write_bytes(encoded(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
