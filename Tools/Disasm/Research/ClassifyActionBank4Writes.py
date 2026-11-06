"""Корректировка ложных связей банка 0 только для 80 доказанных записей выбранного банка 4."""
import json
import re
from ClassifyControlsTextDisplay import ROOT
from ActionBank4Writes import records, qualify_mutations


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    proof = read('ActionBank4WritesVerification')
    assert proof['passed'] and proof['total_cases'] == 3076
    flow, modified = read('ControlFlow'), read('ModifiedCode')
    data = records(flow)
    removed = qualify_mutations(modified, flow)
    assert len(removed) > 5
    pending = {ROOT / 'Tools/Disasm/Reports/ModifiedCode.json': encode(modified),
               ROOT / 'Tools/Disasm/Reports/ActionBank4DataWrites.json': encode(data)}
    path = ROOT / 'Docs/ModifiedCode.md'
    text = path.read_text('utf-8')
    wrong = {(m['writer'], m['target']) for m in removed}
    lines, count = [], 0
    for line in text.splitlines():
        match = re.match(r'\| Action \| #([0-9A-F]{4}) \| #([0-9A-F]{4}) \|', line)
        if match and (int(match[1], 16), int(match[2], 16)) in wrong:
            count += 1
        else:
            lines.append(line)
    assert count == len(removed)
    lines += ['', '## Уточнение банковых записей кадра', '',
        '[Блок A981..AA89](ActionBank4Writes.md) пишет OBJECT3D в банке 4, код ACTION банка 0 по совпадающим адресам не изменяется. '
        + str(len(removed)) + ' ошибочных связей исключены из таблицы инструкций, все 80 фактических записей сохранены в [отдельном банковом реестре](../Tools/Disasm/Reports/ActionBank4DataWrites.json).']
    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    path = ROOT / 'Source/Action/UpdateFrame.asm'
    text = path.read_text('utf-8')
    marker = '                ; Документация [банковые записи кадра](../../Docs/ActionBank4Writes.md)\n'
    assert marker not in text
    text = text.replace('                module UpdateFrame\n', '                module UpdateFrame\n' + marker)
    needle = '                LD A, #14\n'
    assert text.count(needle) == 1
    text = text.replace(needle, '                ; Выбор банка 4 для трёх групп XOR 60 в OBJECT3D, совпадающие адреса ACTION банка 0 не меняются.\n' + needle)
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/GenerateDocs.py'
    text = path.read_text('utf-8')
    needle = '    # Сохранение адресов записей в инструкции без объявления каждой записи ошибкой.'
    assert text.count(needle) == 1
    hook = '''    # Доказанный блок UpdateFrame пишет выбранный банк 4, а не инструкции ACTION по тем же адресам.
    from ActionBank4Writes import qualify_mutations as qualify_bank4_writes, records as bank4_write_records
    qualify_bank4_writes(mutations,flow)
    write("Tools/Disasm/Reports/ActionBank4DataWrites.json",json.dumps(bank4_write_records(flow),ensure_ascii=False,indent=2))

'''
    pending[path] = text.replace(needle, hook + needle).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionBank4Writes'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionBank4Writes'
    assert not candidate.exists() and not history.exists()
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    # Сохранение отдельного кандидата и точной истории перед обновлением только доказанных банковых связей.
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
    report = dict(passed=True, data_writes=80, removed_false_bank0_instruction_links=len(removed),
                  target_bank=4, target_slot=24, source_instructions_changed=False, original_bytes_preserved=True,
                  model_cases=3076, whole_update_frame_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionBank4WritesClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
