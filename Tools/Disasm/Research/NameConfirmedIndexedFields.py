"""Именованные поля доказанных записей с привязкой к исходной инструкции."""
import contextlib
import io
import json
import re
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify, structure_symbols


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    source_map = json.loads((reports / 'SourceMap.json').read_text(encoding='utf-8'))
    flow = json.loads((reports / 'ControlFlow.json').read_text(encoding='utf-8'))
    functions = json.loads((reports / 'Functions.json').read_text(encoding='utf-8'))
    instructions = {(item['slot'], item['offset']): item for region in flow for item in region['instructions']}
    types = structure_symbols()
    record = {index: f'FActionRecord.Components.Component{index // 2}.' + ('High' if index & 1 else 'Low')
              for index in range(6)}
    structs = (ROOT / 'Includes/Structs/Include.inc').read_text(encoding='utf-8')
    body = re.search(r'struct FActionRecord\n(.*?)\s+ends', structs, re.S)[1]
    for line in body.splitlines():
        field = re.match(r'(\w+)\s+db\s+', line)
        if field:
            name = 'FActionRecord.' + field[1]
            record[types[name.upper()]] = name
    assert len(record) == 64
    sources = {
        'Action/ScheduleSpawn': {'IX': record, 'IY': record},
        'Action/SpawnAlternate': {'IX': record, 'IY': record},
        'Action/UpdateObjects': {'IX': record},
        'Action/SetClass18ObjectState': {'IX': record},
        'Controls/DrawRadar': {'IX': record},
        'Controls/ToggleTargetOverlay': {'IX': record},
        'StationBoot/StartStation': {'IX': {0: 'FInterfaceItem.X', 12: 'FInterfaceItem.DrawHandler',
                                           13: 'FInterfaceItem.DrawHandler + 1'}},
        'Station/CloseAllItems': {'IX': {0: 'FDrawListEntry.Handler', 1: 'FDrawListEntry.Handler + 1'}},
        'Station/RemoveItemDraw': {'IX': {0: 'FDrawListEntry.Handler', 1: 'FDrawListEntry.Handler + 1'}},
        'Controls/CompareComponents': {'IX': {1: 'FComponent24.Middle', 2: 'FComponent24.High'},
                                       'IY': {1: 'FComponent24.Middle', 2: 'FComponent24.High'}},
    }
    pending, substitutions = {}, {}
    count = 0
    for relative, bindings in sources.items():
        path = ROOT / ('Source/' + relative + '.asm')
        fragment = next(item for item in source_map if item['path'] == path.relative_to(ROOT).as_posix())
        owner = next(item for item in functions if item['path'] == fragment['path'])
        offset = fragment['offset']
        lines = []
        for line in path.read_text(encoding='utf-8').splitlines():
            code, sep, note = line.partition(';')
            operation = code[16:].strip()
            if operation and not operation.lower().startswith(('module ', 'endmodule')):
                instruction = instructions[fragment['slot'], offset]
                address = instruction['address']
                replacements = []
                for match in re.finditer(r'\((IX|IY)\s*\+\s*#([0-9A-F]{2})\)', code):
                    register, displacement = match[1], int(match[2], 16)
                    # До BuildRandom IX указывает строку шаблона, а не FActionRecord.
                    if relative == 'Action/SpawnAlternate' and register == 'IX' and address < 0x79CC:
                        continue
                    if register not in bindings:
                        continue
                    assert displacement in bindings[register]
                    field = bindings[register][displacement]
                    new = f'({register} + @{field})'
                    replacements.append((match[0], new))
                    count += 1
                for before, after in replacements:
                    code = code.replace(before, after)
                if replacements:
                    substitutions[owner['region'], address] = replacements
                    line = code.rstrip()
                    if sep:
                        assert len(line) < 80
                        line = line.ljust(80) + ';' + note
                offset += len(bytes.fromhex(instruction['hex']))
            lines.append(line)
        assert offset == fragment['offset'] + fragment['length']
        pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/ConfirmedIndexedFields.py'
    helper = '''"""Поля IX/IY по доказанному контексту конкретной исходной инструкции."""
REPLACEMENTS = ''' + repr(substitutions) + '''


def name_instruction(region, function_address, address, operation):
    for before, after in REPLACEMENTS.get((region, address), ()):
        operation = operation.replace(before, after)
        # Экспортёр предварительно нормализует пробелы у индексных операндов.
        operation = operation.replace(before.replace('IX+', 'IX + ').replace('IY+', 'IY + '), after)
    return operation
'''
    pending[path] = helper.encode('utf-8')
    path = ROOT / 'Tools/Disasm/Research/SemanticNames.py'
    text = path.read_text(encoding='utf-8')
    needle = '    operation = action_class3_link_count_name_operands_instruction(region, function_address, address, operation)'
    assert text.count(needle) == 1
    text = text.replace(needle, '    operation = confirmed_indexed_field_name_instruction(region, function_address, address, operation)\n' + needle)
    text += '\nfrom ConfirmedIndexedFields import name_instruction as confirmed_indexed_field_name_instruction\n'
    pending[path] = text.encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ConfirmedIndexedFields'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeConfirmedIndexedFields'
    assert not candidate.exists() and not history.exists()
    originals = {path: path.read_bytes() if path.exists() else None for path in pending}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, original in originals.items():
        assert path.read_bytes() == original if original is not None else not path.exists()
        if original is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
    for path, raw in pending.items():
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True, indexed_operands_named=count, instructions_changed=0,
                  template_IX_context_preserved=True, assembly_executed=False)
    (reports / 'ConfirmedIndexedFieldsVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
