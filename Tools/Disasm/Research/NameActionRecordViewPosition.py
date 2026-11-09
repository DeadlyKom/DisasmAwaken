"""Публикация физической позиции в системе отрисовки без изменения шести байтов."""

from contextlib import redirect_stdout
from io import StringIO
import importlib
import json
import re
import sys

from ActionObjectRecords import PATH, parse
from CheckIntro import ROOT


FIELD_NAMES = dict(zip(('Unknown1A', 'Unknown1B', 'Unknown1C', 'Unknown1D', 'Unknown1E', 'Unknown1F'),
                       ('X.Low', 'X.High', 'Y.Low', 'Y.High', 'Depth.Low', 'Depth.High')))
NOTE = 'X, Y и глубина после ComputePatchedVector, старший байт X равен 80 до успешного преобразования'
WRITER = ROOT / 'Source/Action/RenderSceneFrame.asm'


def rename_fields(text):
    for old, name in FIELD_NAMES.items():
        text = text.replace(old, 'ViewPosition.' + name)
    return text


def main():
    sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
    import VerifySources

    def verify():
        with redirect_stdout(StringIO()):
            VerifySources.main()

    verify()
    research = ROOT / 'Tools/Disasm/Research'
    reports = ROOT / 'Tools/Disasm/Reports'
    proof = json.loads((reports / 'ActionRecordViewPositionVerification.json').read_bytes())
    assert proof['passed'] and proof['frame_entries'] == 32
    pending = {}
    records = ROOT / PATH
    previous_bytes, old_symbols = parse(records.read_text('utf-8'))
    text = records.read_text('utf-8')
    old_block = ''.join(r'(?m:^ {20}(#[0-9A-F]{2}),[ ]*; ' + name +
                        r', игровой смысл ещё неизвестен\n)' for name in FIELD_NAMES)

    def record(match):
        values = iter(match.groups())
        lines = ['                    {'.ljust(80) + '; ViewPosition, ' + NOTE]
        for index, name in enumerate(('X', 'Y', 'Depth')):
            lines.append('                        {'.ljust(80) + f'; {name}, знаковое слово')
            lines.append(('                            ' + next(values) + ',').ljust(80) + '; Low, младший байт')
            lines.append(('                            ' + next(values)).ljust(80) + '; High, старший знаковый байт')
            lines.append('                        }' + (',' if index < 2 else ''))
        return '\n'.join((*lines, '                    },', ''))

    text, count = re.subn(old_block, record, text)
    assert count == 26
    pending[records] = text

    structs = ROOT / 'Includes/Structs/Include.inc'
    text = structs.read_text('utf-8')
    anchor = '                struct FActionRecord\n'
    assert text.count(anchor) == 1
    declaration = ('                struct FActionViewPosition\n' +
                   ''.join((name.ljust(16) + 'FActionWord').ljust(80) + '; знаковая координата после преобразования\n'
                           for name in ('X', 'Y', 'Depth')) +
                   '                ends\n                assert FActionViewPosition == #06\n\n')
    text = text.replace(anchor, declaration + anchor)
    old_block = ''.join((name.ljust(16) + 'db #00').ljust(80) + '; игровой смысл ещё неизвестен\n'
                        for name in FIELD_NAMES)
    assert text.count(old_block) == 1
    text = text.replace(old_block, ('ViewPosition'.ljust(16) + 'FActionViewPosition').ljust(80) + '; ' + NOTE + '\n')
    anchor = '                assert FActionRecord == #40'
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + '\n                assert FActionRecord.ViewPosition == #1A\n'
                        '                assert FActionRecord.ViewPosition.Depth.High == #1F')
    pending[structs] = text

    schema = research / 'ActionObjectRecords.py'
    text = schema.read_text('utf-8')
    anchor = " 'FActionRecord':(('Components'"
    assert text.count(anchor) == 1
    text = text.replace(anchor, " 'FActionViewPosition':tuple((name,'FActionWord','знаковое слово') for name in ('X','Y','Depth')),\n" + anchor)
    old = " for i in range(6,64))}"
    assert text.count(old) == 1
    text = text.replace(old, " for i in range(6,64) if not 0x1A <= i <= 0x1F)}\n"
                        "fields = SCHEMA['FActionRecord']\n"
                        "SCHEMA['FActionRecord'] = (fields[:21] +\n"
                        "    (('ViewPosition', 'FActionViewPosition', " + repr(NOTE) + "),) + fields[21:])")
    scope = {'__name__': 'candidate_action_object_records'}
    exec(compile(text, str(schema), 'exec'), scope)
    _, new_offsets = scope['layout']('FActionRecord')
    assert [new_offsets['ViewPosition.' + name] for name in FIELD_NAMES.values()] == list(range(0x1A, 0x20))
    raw, new_symbols = scope['parse'](pending[records])
    assert raw == previous_bytes
    pending[schema] = text

    for folder in ('Action', 'Controls'):
        for path in (ROOT / 'Source' / folder).glob('*.asm'):
            text = path.read_text('utf-8')
            changed = rename_fields(text)
            if changed == text:
                continue
            lines = changed.splitlines(keepends=True)
            for index, line in enumerate(lines):
                op, separator, note = line.partition(';')
                if separator and '@FActionRecord.ViewPosition' in op:
                    assert len(op.rstrip()) < 80
                    lines[index] = op.rstrip().ljust(80) + ';' + note
            pending[path] = ''.join(lines)
    for name in ('ActionAntimissileCommandFacts', 'ActionLinkedOverlayFacts', 'ActionLinkedVectorsFacts',
                 'ActionPhaseTransitionFacts', 'ConfirmedIndexedFields'):
        path = research / (name + '.py')
        text = path.read_text('utf-8')
        pending[path] = rename_fields(text)
        assert pending[path] != text

    replacements = (('LD HL, #001B', 'LD HL, @FActionRecord.ViewPosition.X.High'),
                    ('LD DE, #0020', 'LD DE, @FActionRecord.ViewPosition.Depth + @FActionWord'))
    text = WRITER.read_text('utf-8')
    for old, new in replacements:
        assert text.count(old) == 1
        text = text.replace(old, new)
    pending[WRITER] = text
    semantic = research / 'SemanticNames.py'
    text = semantic.read_text('utf-8')
    anchor = 'def name_operands(region, function_address, operation):\n'
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + '    if (region, function_address) == ("Action", 0xE020):\n' +
                        ''.join(f'        operation = operation.replace({old!r}, {new!r})\n' for old, new in replacements))
    pending[semantic] = text

    symbols_path = reports / 'Symbols.json'
    symbols = json.loads(symbols_path.read_bytes())
    assert all(symbols[key] == value for key, value in old_symbols.items())
    for key in old_symbols.keys() - new_symbols.keys():
        del symbols[key]
    symbols.update(new_symbols)
    pending[symbols_path] = json.dumps(symbols, ensure_ascii=False, indent=2) + '\n'
    candidate = research / 'Candidates/ActionRecordViewPosition'
    history = research / 'History/BeforeActionRecordViewPosition'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() for path in pending}
    for path, text in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, 'utf-8', newline='\n')
    for path, original in before.items():
        assert path.read_bytes() == original
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original)
    for path, text in pending.items():
        path.write_text(text, 'utf-8', newline='\n')
    importlib.reload(sys.modules['ActionObjectRecords'])
    verify()
    result = dict(passed=True, physical_records=26, record_size=64, new_structure='FActionViewPosition',
                  fields=dict(zip(FIELD_NAMES.values(), range(0x1A, 0x20))),
                  physical_bytes_preserved=True, assembly_executed=False)
    (reports / 'ActionRecordViewPositionClassification.json').write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
