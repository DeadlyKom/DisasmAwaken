"""Типизация 32 исходных байтов масок без изменения размещения и ручных данных."""
from pathlib import Path
import collections
import contextlib
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
import ControlsMarkerFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsMarkerVerification')['passed']
    source_map, symbols, inventory = read('SourceMap'), read('Symbols'), read('Inventory')
    item = next(i for i in source_map if i['slot'] == 23 and i['offset'] == 0x160F)
    assert item['kind'] == 'unclassified' and item['length'] == 32
    previous = ROOT / item['path']
    original = previous.read_bytes()
    source = (ROOT / 'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    assert original == source[0x160F:0x162F]
    text, labels = facts.render(source)
    assert facts.parse(text) == (original, labels)
    assert not any(key in symbols for key in labels)
    symbols.update(labels)
    item.update(path=facts.TABLE[1], kind='typed_data', origin=0xF0ED)
    inventory['ranges_by_kind'] = dict(collections.Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind'] == kind)
        for kind in inventory['ranges_by_kind']}
    assert sum(inventory['physical_bytes_by_kind'].values()) == 479744
    pending = {ROOT / facts.TABLE[1]: text.encode('utf-8')}
    for stem, value in (('Symbols', symbols), ('SourceMap', source_map), ('Inventory', inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/' + stem + '.json')] = encode(value)
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FMarkerPhaseMasks' not in text
    block = '\n                ; Четыре исходные XOR-маски одной из восьми фаз маркера\n                struct FMarkerPhaseMasks\n'
    for name, _, note in facts.FIELDS:
        block += name.ljust(16) + 'db #00'.ljust(64) + '; ' + note + '\n'
    block += '                ends\n                assert FMarkerPhaseMasks == 4\n'
    pending[path] = text.replace('                endif', block + '\n                endif').encode('utf-8')
    path = ROOT / 'Source/Files/23_CONTROL.inc'
    text = path.read_text('utf-8')
    needle = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/23_CONTROL/Unclassified009.bin"'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, '                disp #F0ED\n                include "../Controls/Data/MarkerPhaseMasks.asm"\n                ent').encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle) == 1
    hook = ('    # Восстановление восьми физических фаз XOR-маркера только в отдельном кандидате.\n'
        '    if "struct FMarkerPhaseMasks" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsMarkerFacts import TABLE as MARKER_TABLE, render as render_marker\n'
        '        text, bindings = render_marker(data_by_slot[23])\n'
        '        write(MARKER_TABLE[1], text)\n'
        '        symbols.update(bindings)\n'
        '        special[23, 0x160F] = (0x162F, MARKER_TABLE[1], 0xF0ED)\n')
    pending[path] = text.replace(needle, hook + needle).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ControlsMarkerTable'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsMarkerTable'
    assert not candidate.exists() and not history.exists()
    plan = [(p, p.read_bytes() if p.exists() else None, after) for p, after in pending.items()]
    for path, before, after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(after)
    for path, before, after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path, before in {**{p: b for p, b, _ in plan if b is not None}, previous: original}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before)
    for path, before, after in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT / 'Source/Resources/23_CONTROL').resolve())
    assert previous.read_bytes() == original == (history / previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    result = dict(passed=True, typed_bytes=32, physical_records=8, fields_per_record=4,
        physical_bytes_preserved=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsMarkerTableClassification.json').write_bytes(encode(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
