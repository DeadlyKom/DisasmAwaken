"""Публикация 165 доказанных байтов, неизвестный хвост сохраняется из рабочей копии."""
import contextlib
import hashlib
import io
import json
import re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionAimFollowFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read('ActionAimFollowVerification')
    assert proof['passed'] and proof['total_cases'] == 214564
    functions, source_map, symbols, inventory, flow, modified = [read(n) for n in ('Functions', 'SourceMap', 'Symbols', 'Inventory', 'ControlFlow', 'ModifiedCode')]
    old = next(f for f in functions if f['region'] == 'Action' and f['address'] == 0xE36A)
    assert (old['name'], old['offset'], old['end_offset']) == ('UnknownE36A', 0x836A, 0x84A6)
    old_path = ROOT / old['path']
    old_text = old_path.read_text('utf-8')
    old_range = next(i for i in source_map if i['path'] == old['path'])
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    name, description = facts.FUNCTIONS[0xE36A]
    first = dict(old, name=name, description=description, semantic_status='described', end_offset=0x840F, path='Source/Action/' + name + '.asm')
    second = dict(old, name='UnknownE40F', address=0xE40F, offset=0x840F, path='Source/Action/UnknownE40F.asm',
                  description='Unknown, полный договор очереди отрисовки и её окружающего обхода ещё не доказан')
    pending, renames = {}, {}
    for key, value in symbols.items():
        if not key.startswith('Action.UnknownE36A.'):
            continue
        if value < 0xE40F:
            label = 'Entry' if value == 0xE36A else facts.LOCAL[value]
            renames[key] = 'Action.' + name + '.' + label
        else:
            label = 'Entry' if value == 0xE40F else key.rsplit('.', 1)[1]
            renames[key] = 'Action.UnknownE40F.' + label

    def rename(text):
        for before, after in renames.items():
            text = re.sub(r'\b' + re.escape(before) + r'\b', after, text)
        return text

    # Поиск точных ссылок на переносимые метки, посторонние строки не переоформляются.
    for directory, patterns in (('Source', ('*.asm', '*.inc')), ('Docs', ('*.md',))):
        for pattern in patterns:
            for path in (ROOT / directory).rglob(pattern):
                if path == old_path:
                    continue
                before = path.read_text('utf-8')
                after = rename(before)
                if before != after:
                    lines = []
                    for line in after.splitlines():
                        code, sep, comment = line.partition(';')
                        if sep and code.strip() and '@Action.' in code:
                            assert len(code.rstrip()) < 80
                            line = code.rstrip().ljust(80) + ';' + comment
                        lines.append(line)
                    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    region = next(r for r in flow if r['name'] == 'Action')
    records = [i for i in region['instructions'] if 0xE36A <= i['address'] < 0xE40F]
    assert b''.join(bytes.fromhex(i['hex']) for i in records) == source[0x836A:0x840F]
    validate_notes([region], {'Action': facts.COMMENTS})
    lines = ['                module Action', '                module ' + name,
             '                ; Документация [сопровождение и цель](../../Docs/ActionAimFollow.md)',
             '                ; -----------------------------------------', '                ; ' + description,
             '                ; исходная запись 17, код ACTION банка 0, адреса E36A..E40E']
    for heading, values in zip(('In', 'Out', 'Corrupt', 'Note'), facts.CONTRACTS['Action', 0xE36A]):
        lines += ['                ; ' + heading + ':'] + ['                ;   ' + v for v in values]
    lines += ['                ; -----------------------------------------']
    for record in records:
        pc = record['address']
        before, right = facts.COMMENTS.get(pc, ([], None))
        lines += ['                ; ' + v for v in before]
        operation = record['operation'].replace(',', ', ')
        if operation.startswith(('JP ', 'JR ')):
            for address, label in facts.LOCAL.items():
                operation = operation.replace('#' + format(address, '04X'), '@Action.' + name + '.' + label)
            operation = operation.replace('#E40F', '@Action.UnknownE40F.Entry')
        operation = facts.name_operands('Action', 0xE36A, operation)
        label = 'Entry' if pc == 0xE36A else facts.LOCAL.get(pc, '')
        assert len(label) <= 15
        line = ((label + ':').ljust(16) if label else ' ' * 16) + operation
        if right:
            assert len(line) < 80
            line = line.ljust(80) + '; ' + right
        lines.append(line)
    lines += ['                endmodule', '                endmodule']
    pending[ROOT / first['path']] = format_function('\n'.join(lines) + '\n', second).encode('utf-8')
    # Сохранение неизвестных 151 байта текстом рабочей копии, заменяются только заголовок и ссылки.
    cut = old_text.index('PointE40F:')
    header = old_text[:old_text.index('Entry:')].replace('module UnknownE36A', 'module UnknownE40F')
    header = header.replace('E36A..E4A5', 'E40F..E4A5').replace(old['description'], second['description'])
    tail = rename(old_text[cut:]).replace('PointE40F:', 'Entry:', 1)
    tail = tail.replace('Entry:      LD', 'Entry:          LD', 1)
    pending[ROOT / second['path']] = (header + tail).encode('utf-8')
    index = functions.index(old)
    functions[index:index + 1] = [first, second]
    index = source_map.index(old_range)
    source_map[index:index + 1] = [dict(old_range, offset=f['offset'], length=f['end_offset'] - f['offset'], path=f['path'], origin=f['address'],
        sha256=hashlib.sha256(source[f['offset']:f['end_offset']]).hexdigest()) for f in (first, second)]
    symbols = {renames.get(key, key): value for key, value in symbols.items()}
    region['roots'] = sorted(set(region['roots']) | {0xE40F})
    for item in modified:
        if item['path'] == old['path']:
            item['path'] = first['path'] if item['writer'] < 0xE40F else second['path']
    inventory.update(fragments=len(functions), described=sum(f['semantic_status'] == 'described' for f in functions), unknown=sum(f['semantic_status'] != 'described' for f in functions))
    inventory['ranges_by_kind']['code'] += 1
    for stem, value in (('Functions', functions), ('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory), ('ControlFlow', flow), ('ModifiedCode', modified)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    path = ROOT / 'Source/Files/17_ACTION.inc'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    line = next(line for line in text.splitlines() if 'include "../Action/UnknownE36A.asm"' in line)
    replacement = line.replace('UnknownE36A.asm', name + '.asm')
    replacement = replacement.partition(';')[0].rstrip().ljust(80) + '; (6) жёсткий порядок продолжения E020'
    replacement += '\n                ent\n                assert $ == #840F\n                disp #E40F\n'
    replacement += '                include "../Action/UnknownE40F.asm"'.ljust(80) + '; (7) жёсткий порядок продолжения E020'
    pending[path] = text.replace(line, replacement).encode('utf-8')
    path = ROOT / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    assert 'module ActionAimFollowState' not in text
    block = '\n                ; Исходные состояние точки и изменяемый запрос, память не выделяется\n                module ActionAimFollowState\n'
    for label, address, note in (('Position', 0x9B19, 'два байта X и Y сопровождающей точки'),
                                 ('Request', 0xAA8E, 'операнд LD A,n по AA8D, ненулевой запрос назначения цели')):
        block += (label.ljust(16) + 'equ #' + format(address, '04X')).ljust(80) + '; ' + note + '\n'
    pending[path] = text.replace('                endif', block + '                endmodule\n\n                endif').encode('utf-8')
    path = ROOT / 'Includes/Const/Include.inc'
    text = path.read_text('utf-8')
    assert 'module ActionAimFollowConst' not in text
    block = '\n                ; Исходные параметры сопровождения и назначения цели\n                module ActionAimFollowConst\n'
    for label, value, note in (('DistanceLimit', 16, 'оба модуля должны быть строго меньше 16'), ('CenterX', 119, 'экранный центр X'),
        ('CenterY', 43, 'экранный центр Y'), ('CaptureSound', 0xEE02, 'шесть строк потока назначения цели'),
        ('FullSound', 0xEE1B, 'шесть строк потока трёх занятых целей'), ('FullText', 0xF258, 'указатель сообщения Controls банка 1'),
        ('RecordBias', 0x5F00, 'прибавление эквивалентно вычитанию A100 по модулю 65536')):
        block += (label.ljust(16) + 'equ #' + format(value, '04X')).ljust(80) + '; ' + note + '\n'
    pending[path] = text.replace('                endif', block + '                endmodule\n\n                endif').encode('utf-8')
    # Подключение точечных фактов к реестрам, массовый экспорт не запускается.
    for filename, extra in (
        ('Knowledge.py', "\nfrom ActionAimFollowFacts import FUNCTIONS as ACTION_AIM_FOLLOW_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_AIM_FOLLOW_FUNCTIONS)\n"),
        ('Contracts.py', "\nfrom ActionAimFollowFacts import CONTRACTS as ACTION_AIM_FOLLOW_CONTRACTS\nCONTRACTS.update(ACTION_AIM_FOLLOW_CONTRACTS)\n")):
        path = ROOT / 'Tools/Disasm/Research' / filename
        text = path.read_text('utf-8')
        assert extra.splitlines()[1] not in text
        pending[path] = (text + extra).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/SemanticNames.py'
    text = path.read_text('utf-8')
    needle = '    operation = ship_preview_callback_name_operands(region, function_address, operation)'
    assert text.count(needle) == 1
    text = text.replace(needle, needle + '\n    operation = action_aim_follow_name_operands(region, function_address, operation)')
    text += "\nfrom ActionAimFollowFacts import name_operands as action_aim_follow_name_operands\nDOCUMENTS['Action',0xE36A]=('ActionAimFollow','сопровождение и цель')\n"
    text += 'LABELS.update(' + repr({('Action', a): n for a, n in facts.LOCAL.items()}) + ')\n'
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '\n\nif __name__ == "__main__":'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, "\nfrom ActionAimFollowFacts import COMMENTS as ACTION_AIM_FOLLOW_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_AIM_FOLLOW_COMMENTS)\n" + needle).encode('utf-8')
    path = ROOT / 'Docs/Functions.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    text = re.sub(r'\| Action \| \d+ \| \d+ \|', '| Action | ' + str(sum(f['region'] == 'Action' for f in functions)) + ' | ' + str(sum(f['region'] == 'Action' and f['semantic_status'] == 'described' for f in functions)) + ' |', text)
    line = next(line for line in text.splitlines() if '[Action.UnknownE36A]' in line)
    rows = '\n'.join('| #' + format(f['address'], '04X') + ' | [Action.' + f['name'] + '](../' + f['path'] + ') | ' + f['description'] + ' |' for f in (first, second))
    pending[path] = text.replace(line, rows).encode('utf-8')
    path = ROOT / 'Docs/FunctionDetails/Action.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    start = text.index('## UnknownE36A\n')
    end = text.find('\n## ', start + 4)
    assert end > start
    sections = ''.join('## ' + f['name'] + '\n\n[Action.' + f['name'] + '](../../' + f['path'] + ')\n\n' + f['description'] + '.\n\n[Сопровождение и границы проверки](../ActionAimFollow.md).\n\n' for f in (first, second))
    pending[path] = (text[:start] + sections + text[end:]).encode('utf-8')
    path = ROOT / 'Docs/ModifiedCode.md'
    text = pending.get(path, path.read_bytes()).decode('utf-8')
    text += '\n## Писатели сопровождения и назначения цели\n\n[FollowProjectedTarget](ActionAimFollow.md) записывает CompanionMask по E3C2, снимает Request по E3CC и дважды выбирает CursorA по E3D2 и E3ED. Все четыре писателя зарегистрированы с исходными размерами операндов, новые области RAM не выделяются. AbsoluteX и AbsoluteY остаются изменяемыми операндами LD BC,nn и LD DE,nn, которые заполняет PrepareProjectedBounds.\n'
    pending[path] = text.encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionAimFollow'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionAimFollow'
    assert not candidate.exists() and not history.exists()
    plan = [(path, path.read_bytes() if path.exists() else None, after) for path, after in pending.items()]
    # Создание отдельного кандидата, проверка ручных изменений и сохранение точной истории до публикации.
    for path, before, after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, before, after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path, before in {**{p: b for p, b, _ in plan if b is not None}, old_path: old_path.read_bytes()}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    # Удаление только заменённого исходника после проверки и сверки сохранённой истории.
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Action').resolve())
    assert old_path.read_bytes() == (history / old['path']).read_bytes()
    old_path.unlink()
    result = dict(passed=True, described_functions=1, proved_local_code_bytes=165, confirmed_instructions=len(records),
        remaining_unknown_code_bytes=151, original_bytes_preserved=True, model_cases=214564, whole_projection_scan_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionAimFollowClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
