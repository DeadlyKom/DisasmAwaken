"""Физическая таблица указателей, два неизвестных соседних диапазона сохраняются побайтово."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckActionObjectCopy import packet
import ActionObjectPointersData as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ActionObjectCopyVerification')['passed'] and read('ActionObjectCopyClassification')['passed']
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    source_map, symbols, inventory = [read(n) for n in ('SourceMap', 'Symbols', 'Inventory')]
    old = next(i for i in source_map if i['slot'] == 17 and i['offset'] == 0x3D82)
    assert (old['kind'], old['length']) == ('unclassified', 894)
    old_path = ROOT / old['path']
    before_raw = old_path.read_bytes()
    assert before_raw == source[0x3D82:0x4100]
    text, labels = facts.render(source)
    raw, bindings = facts.parse(text)
    assert (raw, bindings) == (source[0x3E00:0x3F00], labels)
    pointers = [int.from_bytes(raw[i:i + 2], 'little') for i in range(0, 256, 2)]
    assert len(set(pointers)) == 95 and all(0xC000 <= p < 0xC000 + len(objects) for p in pointers)
    assert max(len(packet(objects, p - 0xC000)[0]) for p in pointers) == 238
    assert not set(labels) & set(symbols)
    symbols.update(labels)
    path = facts.TABLE[1]
    pending = {ROOT / path: text.encode('utf-8')}
    pieces = ((0x3D82, 0x3E00, 'Source/Resources/17_ACTION/Unclassified020_BeforeObjectPointers.bin', False),
              (0x3E00, 0x3F00, path, True),
              (0x3F00, 0x4100, 'Source/Resources/17_ACTION/Unclassified020_AfterObjectPointers.bin', False))
    ranges = []
    for start, end, relative, typed in pieces:
        if not typed:
            pending[ROOT / relative] = source[start:end]
        ranges.append(dict(slot=17, offset=start, length=end - start, kind='typed_data' if typed else 'unclassified', path=relative,
            origin=start + 0x6000 if typed else None, sha256=hashlib.sha256(source[start:end]).hexdigest()))
    index = source_map.index(old)
    source_map[index:index + 1] = ranges
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind'] == kind) for kind in inventory['ranges_by_kind']}
    for stem, value in (('SourceMap', source_map), ('Symbols', symbols), ('Inventory', inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    current = ROOT / 'Includes/Structs/Include.inc'
    text = current.read_text('utf-8')
    assert 'struct FObjectDataPointer' not in text
    pending[current] = text.replace('                endif', facts.structure_text() + '\n                endif').encode('utf-8')
    current = ROOT / 'Source/Files/17_ACTION.inc'
    text = current.read_text('utf-8')
    needle = '                incbin "../Resources/17_ACTION/' + old_path.name + '"'
    assert text.count(needle) == 1
    lines = []
    for start, end, relative, typed in pieces:
        lines.append('                assert $ == #' + format(start, '04X'))
        if typed:
            lines += ['                disp #9E00', '                include "../Action/Data/ObjectPointers.asm"', '                ent']
        else:
            lines += ['                ; Unknown, соседние байты вне доказанной таблицы OBJECT3D', '                incbin "../Resources/17_ACTION/' + relative.rsplit('/', 1)[-1] + '"']
    pending[current] = text.replace(needle, '\n'.join(lines)).encode('utf-8')
    current = ROOT / 'Tools/Disasm/VerifySources.py'
    text = current.read_text('utf-8')
    needle = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(needle) == 1
    hook = '''    # Проверка всех исходных little-endian указателей OBJECT3D и полей реальных STRUCT.
    from ActionObjectPointersData import TABLE as OBJECT_POINTER_TABLE, parse as parse_object_pointers
    pointer_path=OBJECT_POINTER_TABLE[1]
    pointer_records=[i for i in source_map if i['path']==pointer_path]
    assert len(pointer_records)==1
    pointer_item=pointer_records[0]
    assert (pointer_item['slot'],pointer_item['offset'],pointer_item['length'],pointer_item['origin'])==(17,0x3E00,256,0x9E00)
    pointer_raw,pointer_labels=parse_object_pointers((ROOT/pointer_path).read_text('utf-8'))
    assert pointer_raw==sources[17][0x3E00:0x3F00]
    assert all(symbols.get(k.upper())==v for k,v in pointer_labels.items())
    assert symbols['FOBJECTDATAPOINTER']==2 and symbols['FOBJECTDATAPOINTER.TARGET']==0

'''
    pending[current] = text.replace(needle, hook + needle).encode('utf-8')
    current = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = current.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle) == 1
    hook = '''    # Физическая таблица OBJECT3D, сохраняются все 128 записей, включая одинаковые указатели.
    if "struct FObjectDataPointer" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionObjectPointersData import TABLE as OBJECT_POINTER_TABLE, render as render_object_pointers
        text,bindings=render_object_pointers(data_by_slot[17])
        write(OBJECT_POINTER_TABLE[1],text)
        symbols.update(bindings)
        special[17,0x3E00]=(0x3F00,OBJECT_POINTER_TABLE[1],0x9E00)
'''
    pending[current] = text.replace(needle, hook + needle).encode('utf-8')
    for relative in ('Docs/DataFormats.md', 'Tools/Disasm/Research/GenerateDocs.py'):
        current = ROOT / relative
        text = current.read_text('utf-8')
        row = '| FObjectDataPointer | #02 | 128 физических указателей банка 4, см. [OBJECT3D](ActionObjectPointers.md) |'
        line = next(l for l in text.splitlines(True) if '| FRenderPhases |' in l)
        addition = '               "' + row + '",\n' if relative.endswith('.py') else row + '\n'
        assert '| FObjectDataPointer |' not in text
        pending[current] = text.replace(line, line + addition).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ActionObjectPointers'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeActionObjectPointers'
    assert not candidate.exists() and not history.exists()
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    # Подготовка кандидата и точной истории, старый ресурс удаляется лишь после проверки всех байтов.
    for current, before, after in plan:
        target = candidate / current.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for current, before, after in plan:
        assert current.read_bytes() == before if before is not None else not current.exists()
    for current, before in {**{p: b for p, b, _ in plan if b is not None}, old_path: before_raw}.items():
        target = history / current.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for current, before, after in plan:
        current.parent.mkdir(parents=True, exist_ok=True)
        current.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes() == before_raw == (history / old['path']).read_bytes()
    old_path.unlink()
    report = dict(passed=True, physical_records=128, physical_bytes=256, unique_targets=95, maximum_packet_bytes=238,
        neighboring_unknown_bytes=638, all_target_fields_and_instance_addresses_checked=True,
        original_bytes_preserved=True, native_index_reachability_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectPointersClassification.json').write_bytes(encode(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
