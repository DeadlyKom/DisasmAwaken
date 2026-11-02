"""Два доказанных входа Action и отдельный неразобранный хвост 6054, без изменения байтов."""
from pathlib import Path
import collections, contextlib, hashlib, io, json, re, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm'), str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionTextQueueFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ActionTextQueueCallsVerification')['passed']
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ActionTextQueueCalls'
    history = ROOT/'Tools/Disasm/Research/History/BeforeActionTextQueueCalls'
    assert not candidate.exists() and not history.exists()
    pending = {}
    functions = read('Functions')
    old = [f for f in functions if f['region'] == 'Action' and f['address'] in (0x6000, 0x6040)]
    assert len(old) == 2 and all(f['semantic_status'] == 'unknown' for f in old)
    old_bytes = {ROOT/f['path']: (ROOT/f['path']).read_bytes() for f in old}
    new = []
    for address, (name, description) in facts.FUNCTIONS.items():
        new.append(dict(region='Action', name=name, description=description, address=address, slot=17,
                        offset=address-0x6000+0x23D, end_offset=facts.ENDS[address]-0x6000+0x23D,
                        path='Source/Action/'+name+'.asm', semantic_status='unknown' if address == 0x6054 else 'described',
                        fragment_scope='separate_banked_queue_entry' if address != 0x6054 else 'unproved_separate_control_chain'))
    for old_function in old:
        at = functions.index(old_function)
        pieces = [f for f in new if old_function['address'] <= f['address'] < 0x6000+old_function['end_offset']-0x23D]
        functions[at:at+1] = pieces
    def owner(address):
        return next((f for f in new if f['address'] <= address < 0x6000+f['end_offset']-0x23D), None)
    symbols = read('Symbols')
    renames, labels = {}, {}
    for key, address in list(symbols.items()):
        if not key.startswith(('Action.Unknown6000.', 'Action.Unknown6040.')):
            continue
        target = owner(address)
        assert target is not None
        label = 'Entry' if address == target['address'] else key.rsplit('.', 1)[1]
        replacement = 'Action.'+target['name']+'.'+label
        renames[key] = replacement
        del symbols[key]
        symbols[replacement] = address
        labels[address] = label
    for f in new:
        symbols['Action.'+f['name']+'.Entry'] = f['address']
        labels[f['address']] = 'Entry'
    def rename(text):
        for before, after in sorted(renames.items(), key=lambda pair: -len(pair[0])):
            text = re.sub(r'\b'+re.escape(before)+r'\b', after, text)
        for f in old:
            name = facts.FUNCTIONS[f['address']][0]
            text = text.replace('/Action/'+f['name']+'.asm', '/Action/'+name+'.asm')
            text = text.replace('Action.'+f['name'], 'Action.'+name)
        return text
    for folder, pattern in (('Source', '*.asm'), ('Source', '*.inc'), ('Includes', '*.inc'), ('Docs', '*.md')):
        for p in (ROOT/folder).rglob(pattern):
            if p in old_bytes:
                continue
            before = p.read_text('utf-8')
            after = rename(before)
            if before != after:
                lines = after.splitlines()
                for index, line in enumerate(lines):
                    code, sep, note = line.partition(';')
                    if sep and code.strip() and ('@Action.' in code or code.lstrip().startswith('include ')):
                        assert len(code.rstrip()) < 80
                        lines[index] = code.rstrip().ljust(80)+';'+note
                pending[p] = ('\n'.join(lines)+'\n').encode('utf-8')
    flow = read('ControlFlow')
    action = next(group for group in flow if group['name'] == 'Action')
    action['roots'] = sorted(set(action['roots']) | {0x6040, 0x6054})
    validate_notes([action], {'Action': facts.COMMENTS})
    for f in new:
        address = f['address']
        lines = ['                module Action', '                module '+f['name'],
                 '                ; Документация [межбанковые вызовы очереди](../../Docs/ActionTextQueueCalls.md)',
                 '                ; -----------------------------------------', '                ; '+f['description'],
                 '                ; исходная запись 17, файловые смещения #'+format(f['offset'], '04X')+'..#'+format(f['end_offset']-1, '04X')]
        contract = facts.CONTRACTS.get(('Action', address),
            (['Unknown, алгоритм и полный входной договор цепочки ещё не доказаны'],
             ['Unknown, эта цепочка не является продолжением завершившейся обёртки 6040'],
             ["Unknown, включая HL, DE, BC, AF, HL', DE', BC', AF', IX, IY и состояние отображения памяти"],
             ['выделение соседней проверенной обёртки не доказывает смысл оставшихся вызовов и аппаратных ожиданий']))
        for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), contract):
            lines += ['                ; '+heading+':']+['                ;   '+value for value in values]
        lines += ['                ; -----------------------------------------']
        if address == 0x6054:
            text = old_bytes[ROOT/old[1]['path']].decode('utf-8').replace('\r\n', '\n')
            start = text.index('Point6054:')
            body = rename(text[start:].split('                endmodule', 1)[0]).splitlines()
            body[0] = 'Entry:'.ljust(16)+body[0][16:]
            lines += body
        else:
            for instruction in action['instructions']:
                if not f['offset'] <= instruction['offset'] < f['end_offset']:
                    continue
                a = instruction['address']
                before, right = facts.COMMENTS.get(a, ([], None))
                lines += ['                ; '+note for note in before]
                operation = facts.name_operands('Action', address, instruction['operation'].replace(',', ', '))
                line = ('Entry:'.ljust(16) if a == address else ' '*16)+operation
                if right:
                    line = line.ljust(80)+'; '+right
                lines.append(line)
        lines += ['                endmodule', '                endmodule']
        pending[ROOT/f['path']] = format_function('\n'.join(lines)+'\n').encode('utf-8')
    raw = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map = read('SourceMap')
    old_paths = {f['path'] for f in old}
    source_map = [item for item in source_map if item['path'] not in old_paths]
    source_map += [dict(slot=17, offset=f['offset'], length=f['end_offset']-f['offset'], kind='code',
                        path=f['path'], origin=f['address'], sha256=hashlib.sha256(raw[f['offset']:f['end_offset']]).hexdigest()) for f in new]
    source_map.sort(key=lambda item: (item['slot'], item['offset']))
    modified = read('ModifiedCode')
    for item in modified:
        if item['region'] == 'Action' and owner(item['writer']) is not None:
            item['path'] = owner(item['writer'])['path']
    inventory = read('Inventory')
    inventory.update(fragments=len(functions), described=sum(f['semantic_status'] == 'described' for f in functions),
                     unknown=sum(f['semantic_status'] != 'described' for f in functions),
                     ranges_by_kind=dict(collections.Counter(item['kind'] for item in source_map)))
    for stem, value in (('Functions', functions), ('ControlFlow', flow), ('Symbols', symbols), ('SourceMap', source_map), ('ModifiedCode', modified), ('Inventory', inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')] = encoded(value)
    p = next((ROOT/'Source/Files').glob('17_*'))
    text = pending.get(p, p.read_bytes()).decode('utf-8')
    needle = next(line for line in text.splitlines() if line.startswith('                include "../Action/QueueTextItemBank1.asm"'))
    replacement = (needle+'\n                ent\n                assert $ == #0291\n                disp #6054\n'
                   '                include "../Action/Unknown6054.asm"')
    pending[p] = text.replace(needle, replacement).encode('utf-8')
    p = ROOT/'Includes/Const/Include.inc'
    text = p.read_text('utf-8')
    assert 'module ActionBankPage' not in text
    block = '\n                ; Полные управляющие байты 7FFD для межбанковых вызовов Action\n                module ActionBankPage\n'
    for name, value, note in (('Runtime', 0x10, 'ROM 1 и банк 0, фиксированное значение на выходе обёрток'), ('Controls', 0x11, 'ROM 1 и банк 1 с очередью Controls')):
        block += name.ljust(16)+('equ #'+format(value, '02X')).ljust(64)+'; '+note+'\n'
    block += '                endmodule\n'
    pending[p] = text.replace('                endif', block+'\n                endif').encode('utf-8')
    p = ROOT/'Includes/Structs/Include.inc'
    text = p.read_text('utf-8')
    assert 'struct FActionTextQueueFrame' not in text
    block = '\n                ; Собственная динамическая рамка QueueTextItemBank1, порядок отличается от рамки производителя\n                struct FActionTextQueueFrame\n'
    for name, note in (('SavedHL', 'сохранённый HL'), ('SavedBC', 'сохранённый BC'), ('SavedAF', 'сохранённый AF'), ('CallerReturn', 'внешний адрес возврата Action')):
        block += name.ljust(16)+'dw #0000'.ljust(64)+'; '+note+'\n'
    block += '                ends\n                assert FActionTextQueueFrame == 8\n'
    pending[p] = text.replace('                endif', block+'\n                endif').encode('utf-8')
    for filename, extra in (
        ('Knowledge.py', "\nfrom ActionTextQueueFacts import FUNCTIONS as ACTION_TEXT_QUEUE_FUNCTIONS\nFUNCTIONS['Action'].update({a: value for a, value in ACTION_TEXT_QUEUE_FUNCTIONS.items() if not value[0].startswith('Unknown')})\n"),
        ('Contracts.py', '\nfrom ActionTextQueueFacts import CONTRACTS as ACTION_TEXT_QUEUE_CONTRACTS\nCONTRACTS.update(ACTION_TEXT_QUEUE_CONTRACTS)\n'),
        ('SemanticNames.py', '\nfrom ActionTextQueueFacts import name_operands as action_text_queue_name_operands\nDOCUMENTS.update({("Action", a): ("ActionTextQueueCalls", "межбанковые вызовы очереди") for a in (0x6000, 0x6040, 0x6054)})\n'),
        ('ExportSources.py', '\nfrom ActionTextQueueFacts import COMMENTS as ACTION_TEXT_QUEUE_COMMENTS\nREGION_COMMENTS.setdefault("Action", {}).update(ACTION_TEXT_QUEUE_COMMENTS)\n')):
        p = ROOT/'Tools/Disasm/Research'/filename
        text = p.read_text('utf-8')
        if filename == 'SemanticNames.py':
            needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
            assert text.count(needle) == 1
            text = text.replace(needle, needle+'\n    operation = action_text_queue_name_operands(region, function_address, operation)')
        if filename == 'ExportSources.py':
            needle = '\n\nif __name__ == "__main__":'
            assert text.count(needle) == 1
            text = text.replace(needle, '\n'+extra+needle)
        else:
            text += extra
        pending[p] = text.encode('utf-8')
    p = ROOT/'Docs/Functions.md'
    text = p.read_text('utf-8')
    count = sum(f['region'] == 'Action' for f in functions)
    described = sum(f['region'] == 'Action' and f['semantic_status'] == 'described' for f in functions)
    text = re.sub(r'\| Action \| \d+ \| \d+ \|', '| Action | '+str(count)+' | '+str(described)+' |', text)
    lines = [line for line in text.splitlines() if not any('](../'+f['path']+')' in line for f in old)]
    for f in new:
        lines.append('| #'+format(f['address'], '04X')+' | [Action.'+f['name']+'](../'+f['path']+') | '+f['description']+' |')
    pending[p] = ('\n'.join(lines)+'\n').encode('utf-8')
    p = ROOT/'Docs/FunctionDetails/Action.md'
    text = p.read_text('utf-8')
    for f in old:
        start = text.index('## '+f['name']+'\n')
        end = text.find('\n## ', start+4)
        end = len(text) if end < 0 else end
        text = text[:start]+text[end:]
    for f in new:
        text += '\n## '+f['name']+'\n\n[Action.'+f['name']+'](../../'+f['path']+') — '+f['description']+'.\n\n'
        text += 'Начало #'+format(f['address'], '04X')+', смещения #'+format(f['offset'], '04X')+'..#'+format(f['end_offset']-1, '04X')+'. [Проверка и границы](../ActionTextQueueCalls.md).\n'
    pending[p] = text.encode('utf-8')
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for p, before, after in plan:
        c = candidate/p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(after)
    for p, before, after in plan:
        assert (p.read_bytes() == before) if before is not None else not p.exists()
    for p, before in {**{p: before for p, before, _ in plan if before is not None}, **old_bytes}.items():
        h = history/p.relative_to(ROOT)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_bytes(before)
    for p, before, after in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for p, before in old_bytes.items():
        assert p.resolve().is_relative_to((ROOT/'Source/Action').resolve()) and p.read_bytes() == before == (history/p.relative_to(ROOT)).read_bytes()
        p.unlink()
    report = dict(passed=True, described_wrappers=2, net_new_fragments=1, unknown_tail_preserved=True,
                  physical_bytes_preserved=True, instructions_changed=0, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionTextQueueCallsClassification.json').write_bytes(encoded(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
