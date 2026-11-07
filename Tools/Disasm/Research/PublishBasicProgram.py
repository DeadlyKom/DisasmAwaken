"""Исправление доказанного BASIC-входа и публикация исходных строк, без изменения байтов TRD."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from BasicProgramData import ROOT, ENTRY, PROGRAM_BASE, PARTS, parse, original_program
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    original_program()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    sm, functions, symbols, flow, inventory = (read(name) for name in ('SourceMap', 'Functions', 'Symbols', 'ControlFlow', 'Inventory'))
    data = (ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()
    old_ranges = [item for item in sm if item['slot'] == 3 and item['offset'] in (0, 30)]
    assert len(old_ranges) == 2 and all(item['kind'] == 'unclassified' for item in old_ranges)
    pending, removed = {}, []
    new_ranges = []
    for start, end, origin, name, source in PARTS:
        path = f'Source/Basic/Data/{name}.asm'
        lines = []
        for line in source.splitlines():
            code, sep, note = line.partition(';')
            lines.append(code.rstrip().ljust(80) + ';' + note if sep and code.strip() else line)
        text = '\n'.join(lines) + '\n'
        raw, labels = parse(text, origin)
        assert raw == data[start:end]
        module = re.search(r'module (\w+)', text)[1]
        pending[ROOT / path] = text.encode('utf-8')
        new_ranges.append(dict(slot=3, offset=start, length=end - start, path=path, kind='typed_data', origin=origin,
                               sha256=hashlib.sha256(raw).hexdigest()))
        for label, address in labels.items():
            key = module + '.' + label
            assert key not in symbols
            symbols[key] = address
    for start, end, name in ((119, 256, 'BasicSectorTail'), (256, 512, 'IntroCoordinateSeed')):
        path = f'Source/Resources/03_AWAKEN/Unclassified{name}.bin'
        pending[ROOT / path] = data[start:end]
        new_ranges.append(dict(slot=3, offset=start, length=end - start, path=path, kind='unclassified', origin=None,
                               sha256=hashlib.sha256(data[start:end]).hexdigest()))
    for old in old_ranges:
        old_path = ROOT / old['path']
        assert old_path.read_bytes() == data[old['offset']:old['offset'] + old['length']]
        removed.append(old_path)
    sm = [item for item in sm if item not in old_ranges] + new_ranges
    sm.sort(key=lambda item: (item['slot'], item['offset']))
    source = next(item for item in sm if item['path'] == 'Source/Basic/ReadIntroSectors.asm')
    assert source['origin'] == 0x5CD1
    source['origin'] = ENTRY
    function = next(item for item in functions if item['region'] == 'Basic')
    assert function['address'] == 0x5CD1
    function['address'] = ENTRY
    assert symbols['Basic.ReadIntroSectors.Entry'] == 0x5CD1
    symbols['Basic.ReadIntroSectors.Entry'] = ENTRY
    basic = next(region for region in flow if region['name'] == 'Basic')
    basic['blocks'][0].update(origin=PROGRAM_BASE, length=119, roots=[ENTRY])
    basic['roots'] = [ENTRY]
    basic['total_bytes'], basic['classified_fraction'] = 119, 24 / 119
    for instruction in basic['instructions']:
        assert 0x5CD1 <= instruction['address'] < 0x5CE9
        instruction['address'] += 0x70
    for unresolved in basic['unresolved']:
        unresolved['address'] += 0x70
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in sm))
    sizes = Counter()
    for item in sm:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', sm), ('Functions', functions), ('Symbols', symbols), ('ControlFlow', flow), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/03_AWAKEN.inc'
    text = path.read_text(encoding='utf-8')
    prefix = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
    needle = prefix + '                incbin "../Resources/03_AWAKEN/Unclassified000.bin"'
    assert text.count(needle) == 1
    text = text.replace(needle, '                disp #5D3B\n                include "../Basic/Data/Prefix.asm"\n                ent')
    assert text.count('disp #5CD1') == 1
    text = text.replace('disp #5CD1', 'disp #5D41')
    needle = prefix + '                incbin "../Resources/03_AWAKEN/Unclassified001.bin"'
    assert text.count(needle) == 1
    text = text.replace(needle, '''                disp #5D59
                include "../Basic/Data/Line10Tail.asm"
                ent
                assert $ == #0065
                disp #5DA0
                include "../Basic/Data/EntryLine.asm"
                ent
                assert $ == #0077
                ; Секторные байты после логического BASIC не относятся к загружаемой программе.
                incbin "../Resources/03_AWAKEN/UnclassifiedBasicSectorTail.bin"
                assert $ == #0100
                ; Эта страница читается вместе со вступлением по адресу 6400 отдельным дисковым вызовом.
                incbin "../Resources/03_AWAKEN/UnclassifiedIntroCoordinateSeed.bin"''')
    pending[path] = text.encode('utf-8')
    for relative in ('Tools/Disasm/Research/Knowledge.py', 'Tools/Disasm/Research/Contracts.py',
                     'Tools/Disasm/Research/SemanticNames.py', 'Docs/Functions.md', 'Docs/FunctionDetails/Basic.md', 'Docs/Loader.md'):
        path = ROOT / relative
        text = path.read_text(encoding='utf-8')
        assert '5CD1' in text
        pending[path] = text.replace('5CD1', '5D41').encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/BasicNotes.py'
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'0x5C(?:D[0-9A-F]|E[0-8])', lambda m: '0x' + format(int(m[0], 16) + 0x70, '04X'), text)
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/Analyze.py'
    text = path.read_text(encoding='utf-8')
    needle = 'block(3, 0, 0x100, 0x5CCB, "Basic", (0x5CD1,))'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, 'block(3, 0, 119, 0x5D3B, "Basic", (0x5D41,))').encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/CheckBasicLoader.py'
    text = path.read_text(encoding='utf-8')
    assert 'memory[0x5CD1:0x5CE9] = source[6:30]' in text
    text = text.replace('memory[0x5CD1:0x5CE9] = source[6:30]', 'memory[0x5D3B:0x5DB2] = source[:119]\n    assert int(source[107:112]) == int.from_bytes(source[115:117], "little") == 0x5D41')
    pending[path] = text.replace('"PC": 0x5CD1', '"PC": 0x5D41').encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FBasicLineHeader' not in text
    block = '''                struct FBasicLineHeader
LineHigh        db #00                                                          ; старший байт номера строки, номер хранится big-endian
LineLow         db #00                                                          ; младший байт номера строки
BodyLength      dw #0000                                                        ; длина тела little-endian, включает завершающий CR
                ends
                assert FBasicLineHeader == #04

                struct FBasicSmallInteger
Exponent        db #00                                                          ; нулевой байт выбирает компактное целое вместо плавающей точки
Sign            db #00                                                          ; ноль для исходного положительного целого
Low             db #00                                                          ; младший байт абсолютного значения
High            db #00                                                          ; старший байт абсолютного значения
Unused          db #00                                                          ; пятый байт исходного компактного целого, сохранён как ноль
                ends
                assert FBasicSmallInteger == #05

'''
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка исходного BASIC и адреса, указанного обеими формами числа USR.
    from BasicProgramData import PARTS as BASIC_PROGRAM_PARTS, parse as parse_basic_program, original_program
    original_program()
    for start,end,origin,name,_ in BASIC_PROGRAM_PARTS:
        text=(ROOT/f'Source/Basic/Data/{name}.asm').read_text('utf-8')
        raw,labels=parse_basic_program(text,origin)
        assert raw==sources[3][start:end]
        module=re.search(r'module (\\w+)',text)[1]
        assert all(symbols[(module+'.'+label).upper()]==address for label,address in labels.items())
    assert symbols['FBASICLINEHEADER']==4 and symbols['FBASICSMALLINTEGER']==5

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/BasicProgram'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeBasicProgram'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, *removed)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, original in before.items():
        assert path.read_bytes() == original if original is not None else not path.exists()
        if original is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.json':
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='basic-program-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary, path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        else:
            path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
        assert path.read_bytes() == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('119 байтов BASIC полностью разобраны, исходный USR задаёт 5D41, все дисковые байты сохранены')


if __name__ == '__main__':
    main()
