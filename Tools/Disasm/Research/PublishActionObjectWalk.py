"""Публикация подтверждённого продолжения F775 в пределах UpdateObjects."""
from collections import Counter
from pathlib import Path
import contextlib
import hashlib
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from InspectZ80 import decoder
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    pending = {}

    def read(name):
        return json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))

    def save(name, data):
        pending[reports / (name + '.json')] = json.dumps(data, ensure_ascii=False, indent=2) + '\n'

    assert read('ActionObjectWalkVerification')['passed']
    raw_path = ROOT / 'Source/Resources/17_ACTION/Unclassified052.bin'
    raw = bytes.fromhex('d243f8dd360a0bed5fe601c602dd7716dd7e0dfe1a0e08cc8c63c343f8')
    original = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    assert original[0x9775:0x9792] == raw_path.read_bytes() == raw
    flow = read('ControlFlow')
    action = next(region for region in flow if region['name'] == 'Action')
    addresses = {item['address'] for item in action['instructions']}
    assert not addresses.intersection(range(0xF775, 0xF792))
    memory = [0] * 65536
    memory[0xF775:0xF792] = raw
    decoded = decoder(memory).disassemble(0xF775, 0xF792, 'h')
    assert bytes(byte for item in decoded for byte in item.bytes) == raw
    assert all(not item.operation.startswith('DEFB') for item in decoded)
    action['instructions'].extend(dict(address=item.address, operation=item.operation, hex=item.bytes.hex(),
                                       slot=17, offset=item.address - 0x6000) for item in decoded)
    action['instructions'].sort(key=lambda item: (item['address'], item['slot'], item['offset']))
    action['instruction_count'] += len(decoded)
    action['code_bytes'] += len(raw)
    action['classified_fraction'] = action['code_bytes'] / action['total_bytes']
    action['calls'] = sorted(set(action['calls']) | {0x638C})
    action['branches'] = sorted(set(action['branches']) | {0xF843})
    save('ControlFlow', flow)
    functions = read('Functions')
    function = next(item for item in functions if item['region'] == 'Action' and item['address'] == 0xF729)
    assert function['end_offset'] == 0x9775
    function['end_offset'] = 0x9792
    save('Functions', functions)
    ranges = read('SourceMap')
    span = next(item for item in ranges if item['path'] == function['path'])
    orphan = next(item for item in ranges if ROOT / item['path'] == raw_path)
    assert span['offset'] + span['length'] == orphan['offset'] == 0x9775
    span['length'] += len(raw)
    span['sha256'] = hashlib.sha256(original[span['offset']:0x9792]).hexdigest()
    ranges.remove(orphan)
    save('SourceMap', ranges)
    inventory = read('Inventory')
    inventory['instructions'] += len(decoded)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in ranges))
    sizes = Counter()
    for item in ranges:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    save('Inventory', inventory)
    symbols = read('Symbols')
    symbol = 'Action.ApplyIndexedDelta.AdjustMode'
    assert symbol not in symbols
    symbols[symbol] = 0x638C
    save('Symbols', symbols)

    def replace(relative, old, new):
        path = ROOT / relative
        text = pending.get(path, path.read_text(encoding='utf-8'))
        assert text.count(old) == 1, (relative, old)
        pending[path] = text.replace(old, new)

    replace('Source/Action/ApplyIndexedDelta.asm', '                LD A, (#9B83)',
            'AdjustMode:     LD A, (#9B83)')
    path = function['path']
    replace(path, '; Документация [Action]', '                ; Документация [обход записей](../../Docs/ActionObjectWalk.md)\n; Документация [Action]')
    replace(path, '#9729..#9774', '#9729..#9791')
    tail = '''
                ; Проверка числа совпадающих связей класса 3 после возврата из счётчика.
                JP NC, @Action.DispatchObjectState.CallHandler                 ; переход, если найдены две связи, сохранить текущее состояние

                ; Установка состояния и начальной фазы при числе связей меньше двух.
                LD (IX + @FActionRecord.StateCode), #0B
                LD A, R
                AND #01
                ADD A, #02
                LD (IX + @FActionRecord.Unknown16), A
                ; Применение прямой поправки 8 при сохранённом индексе #1A.
                LD A, (IX + @FActionRecord.Unknown0D)
                CP #1A
                LD C, #08
                CALL Z, @Action.ApplyIndexedDelta.AdjustMode                    ; вызов, если сохранённый индекс равен #1A, применить поправку

                JP @Action.DispatchObjectState.CallHandler

'''
    lines = []
    for line in tail.split('\n'):
        code, sep, comment = line.partition(';')
        lines.append(code.rstrip().ljust(80) + sep + comment if sep and code.strip() else line)
    tail = '\n'.join(lines)
    replace(path, '                endmodule\n                endmodule', tail + '                endmodule\n                endmodule')
    replace('Source/Files/17_ACTION.inc', '                assert $ == #9775\n'
            '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/17_ACTION/Unclassified052.bin"\n', '')
    replace('Tools/Disasm/Research/Analyze.py', 'CONFIRMED_CONTINUATIONS = {"Station": {0xC0C8: "af"}}',
            'CONFIRMED_CONTINUATIONS = {"Station": {0xC0C8: "af"},\n'
            '                           "Action": {0xF775: "' + raw.hex() + '"}}')
    replace('Docs/FunctionDetails/Action.md', 'Вход `#F729`, запись 17, смещения `#9729..#9774`.',
            'Вход `#F729`, запись 17, смещения `#9729..#9791`.\n\n'
            '[Обход записей и продолжение F775](../ActionObjectWalk.md).')

    tag = 'ActionObjectWalk'
    candidate = ROOT / ('Tools/Disasm/Research/Candidates/' + tag)
    history = ROOT / ('Tools/Disasm/Research/History/Before' + tag)
    assert not candidate.exists() and not history.exists()
    originals = {path: path.read_bytes() for path in (*pending, raw_path)}
    for path, text in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    for path, raw_before in originals.items():
        assert path.read_bytes() == raw_before
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw_before)
    for path, text in pending.items():
        path.write_text(text, encoding='utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert raw_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert raw_path.read_bytes() == (history / raw_path.relative_to(ROOT)).read_bytes() == raw
    raw_path.unlink()
    print(f'F775: {len(raw)} байт, {len(decoded)} инструкций, исходное размещение сохранено')


if __name__ == '__main__':
    main()
