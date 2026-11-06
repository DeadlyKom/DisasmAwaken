"""Регистрация двух подтверждённых писателей операнда без изменения кода и исходного образа."""
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action


def main():
    reports = ROOT/'Tools/Disasm/Reports'
    proof = json.loads((reports/'ActionLineModesVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases'] == 7168
    memory = flat_action()
    records = json.loads((reports/'ModifiedCode.json').read_text('utf-8'))
    source_map = json.loads((reports/'SourceMap.json').read_text('utf-8'))
    functions = json.loads((reports/'Functions.json').read_text('utf-8'))
    # Проверка писателей, цели и двух слов состояния непосредственно по исходным байтам.
    assert bytes(memory[0xDE0E:0xDE10]) == bytes((0xC6, 0))
    for writer in (0xDC52, 0xDDA0):
        assert bytes(memory[writer:writer+3]) == bytes((0x32, 0x0F, 0xDE))
        owner=next(item for item in source_map if item['slot']==17 and item['offset']<=writer-0x6000<item['offset']+item['length'])
        row = dict(region='Action', writer=writer, target=0xDE0F, target_instruction=0xDE0E,
                   size=1, target_operation='ADD A,#00',
                   path=owner['path'],
                   writer_bank=0, target_bank=0, target_region='Action', target_slot=17,
                   target_offset=0xDE0F-0x6000, writer_source_classified=owner['kind']=='code',
                   target_source_classified=True, target_path='Source/Action/DrawLinearLine.asm',
                   target_runtime_values=[0x10, 0x18])
        existing = [r for r in records if r['region']=='Action' and r['writer']==writer and r['target']==0xDE0F]
        if existing:
            assert existing == [row]
        else:
            records.append(row)
    for writer in (0xDC4E, 0xDD9C):
        assert bytes(memory[writer:writer+4]) == bytes((0xED, 0x53, 0x4E, 0x8D))
    records.sort(key=lambda r: (r['region'], r['writer'], r['target']))
    (reports/'ModifiedCode.json').write_bytes((json.dumps(records, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    result = dict(passed=True, operand_writers=[0xDC52, 0xDDA0], target=0xDE0F,
                  state_word_writers=[0xDC4E, 0xDD9C], state_word_address=0x8D4E,
                  model_cases=7168, parent_procedures_classified=all(any(f['region']=='Action' and f['address']==address and f['semantic_status']=='described' for f in functions) for address in (0xDBBD,0xDD23)),
                  original_bytes_changed=False, assembly_executed=False)
    (reports/'ActionLineModesRegistration.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
