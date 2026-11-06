"""Доказанная табличная роль CF08 не доказывает невозможность исполнения этих байтов."""
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action


def main():
    memory = flat_action()
    rows = json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_text('utf-8'))['rows']
    # Проверка исходных байтов и действительных обращений диспетчера к младшей странице таблицы.
    assert bytes(memory[0xCF08:0xCF0B]) == bytes((0xF3, 0xAF, 0xC9))
    selected = []
    for index in (8, 9, 10):
        row = next(row for row in rows if row['index'] == index)
        assert row['target'] == memory[0xCF00+index]+256*memory[0xD000+index]
        selected.append(dict(index=index, low_address=0xCF00+index, low_byte=memory[0xCF00+index],
                             target=row['target'], target_path=row['path']))
    # Ищем все явно заданные адреса внутри трёх байтов во всех разобранных областях.
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    targets = ('#CF08', '#CF09', '#CF0A')
    references = [dict(region=region['name'], address=item['address'], operation=item['operation'])
                  for region in flow for item in region['instructions']
                  if any(target in item['operation'] for target in targets)]
    assert not references, references
    report = dict(passed=True, region='Action', bank=0, address=0xCF08, bytes=[0xF3, 0xAF, 0xC9],
                  valid_lookup_entries=selected, table_role_proved=True,
                  decoded_regions=len(flow), decoded_instructions=sum(len(r['instructions']) for r in flow),
                  explicit_references_to_cf08_cf0a=references,
                  possible_instructions=['DI', 'XOR A', 'RET'], execution_entry_proved=False,
                  nonexecution_proved=False, unknown_status_preserved=True,
                  source_bytes_changed=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipTableAliasVerification.json').write_bytes(
        (json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
