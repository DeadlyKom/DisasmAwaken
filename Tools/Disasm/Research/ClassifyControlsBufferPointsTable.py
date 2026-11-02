"""Выделение 70 исходных байтов Y,X из крупной области с сохранением обоих неизвестных хвостов."""
from pathlib import Path
import collections
import contextlib
import hashlib
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify
import ControlsBufferPointsFacts as facts


def main():
    def read(stem):
        return json.loads((ROOT / ('Tools/Disasm/Reports/' + stem + '.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsBufferPointsVerification')['passed']
    source_map, symbols, inventory = read('SourceMap'), read('Symbols'), read('Inventory')
    item = next(i for i in source_map if i['slot'] == 22 and i['offset'] == 0)
    assert item['kind'] == 'unclassified' and item['length'] == 0x870
    previous = ROOT / item['path']
    original = previous.read_bytes()
    source = (ROOT / 'Tools/Disasm/Extracted/Active/22_CONTROL0.C.bin').read_bytes()
    assert original == source[:0x870]
    text, labels = facts.render(source)
    assert facts.parse(text) == (source[0x500:0x546], labels)
    assert not any(key in symbols for key in labels)
    symbols.update(labels)
    prefix = 'Source/Resources/22_CONTROL0/Unclassified000_Prefix.bin'
    suffix = 'Source/Resources/22_CONTROL0/Unclassified000_Suffix.bin'
    replacements = []
    for start, end, kind, path, origin in ((0,0x500,'unclassified',prefix,None),
        (0x500,0x546,'typed_data',facts.TABLE[1],0xC500), (0x546,0x870,'unclassified',suffix,None)):
        replacements.append(dict(slot=22, offset=start, length=end-start, kind=kind, path=path,
            origin=origin, sha256=hashlib.sha256(source[start:end]).hexdigest()))
    index = source_map.index(item)
    source_map[index:index+1] = replacements
    inventory['ranges_by_kind'] = dict(collections.Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind: sum(i['length'] for i in source_map if i['kind'] == kind)
        for kind in inventory['ranges_by_kind']}
    assert sum(inventory['physical_bytes_by_kind'].values()) == 479744
    pending = {ROOT / facts.TABLE[1]: text.encode('utf-8'), ROOT / prefix: source[:0x500], ROOT / suffix: source[0x546:0x870]}
    for stem, value in (('Symbols',symbols),('SourceMap',source_map),('Inventory',inventory)):
        pending[ROOT / ('Tools/Disasm/Reports/'+stem+'.json')] = encode(value)
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FBufferPoint' not in text
    block = '\n                ; Физическая запись координат линейного буфера, Y перед X\n                struct FBufferPoint\n'
    for name,_,note in facts.FIELDS:
        block += name.ljust(16) + 'db #00'.ljust(64) + '; '+note+'\n'
    block += '                ends\n                assert FBufferPoint == 2\n'
    pending[path] = text.replace('                endif',block+'\n                endif').encode('utf-8')
    path = ROOT / 'Source/Files/22_CONTROL0.inc'
    text = path.read_text('utf-8')
    needle = '                incbin "../Resources/22_CONTROL0/Unclassified000.bin"'
    assert text.count(needle) == 1
    replacement = ('                incbin "../Resources/22_CONTROL0/Unclassified000_Prefix.bin"\n'
        '                assert $ == #0500\n                disp #C500\n'
        '                include "../Controls/Data/BufferPoints.asm"\n                ent\n'
        '                assert $ == #0546\n'
        '                ; Unknown, исходные байты после физических записей координат\n'
        '                incbin "../Resources/22_CONTROL0/Unclassified000_Suffix.bin"')
    pending[path] = text.replace(needle,replacement).encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle) == 1
    hook = ('    # Физические записи Y,X выделяются только в отдельном кандидате.\n'
        '    if "struct FBufferPoint" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsBufferPointsFacts import TABLE as BUFFER_POINTS_TABLE, render as render_buffer_points\n'
        '        text, bindings = render_buffer_points(data_by_slot[22])\n'
        '        write(BUFFER_POINTS_TABLE[1], text)\n        symbols.update(bindings)\n'
        '        special[22, 0x500] = (0x546, BUFFER_POINTS_TABLE[1], 0xC500)\n')
    pending[path] = text.replace(needle,hook+needle).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ControlsBufferPointsTable'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsBufferPointsTable'
    assert not candidate.exists() and not history.exists()
    plan = [(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes() == before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT / 'Source/Resources/22_CONTROL0').resolve())
    assert previous.read_bytes() == original == (history / previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    result = dict(passed=True,typed_bytes=70,physical_records=35,unknown_prefix_bytes=1280,
        unknown_suffix_bytes=810,original_zero_initializers_preserved=True,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBufferPointsTableClassification.json').write_bytes(encode(result))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
