"""Физические байты режима и разделители ресурса LANG в общей памяти станции."""
import re


START = 0x3A3B
END = 0x3A58
ORIGIN = 0x9A3B
PATH = 'Source/Station/Data/ScriptFields.asm'
MODULE = 'StationScriptFields'

OPERANDS = {
    0xC189: ('#9A32', '@StationScriptFields.ModeM08 - 9'),
    0xC191: ('#9A41', '@StationScriptFields.ModeE00 - 1'),
    0xC342: ('#9A42', '@StationScriptFields.ModeE00'),
    0xC34D: ('#9A33', '@StationScriptFields.ModeM08 - 8'),
    0xC849: ('#9A49', '@StationScriptFields.Group01'),
}


def name_operands(region, address, operation):
    if region == 'Text' and address in OPERANDS:
        return operation.replace(*OPERANDS[address])
    if region == 'Text' and address in (0xC10E, 0xC355):
        selection = '@ControlOptions.ResourceSelect'
        group = selection if operation.startswith('LD BC,') else selection + '.GroupCount'
        return operation.replace('#9A1C', group).replace('#9A1D', selection + '.RecordCount')
    return operation

LAYOUT = (
    *((f'ModeM{index:02d}', 'FScriptModeByte', (0,), 'исходный байт режима m')
      for index in range(8, 15)),
    *((f'ModeE{index:02d}', 'FScriptModeByte', (0,), 'исходный байт режима e')
      for index in range(7)),
    ('Group01', 'FScriptGroupStart', (0xFF,), 'первый разделитель групп'),
    ('Record01', 'FScriptRecordStart', (0xFE,), 'первый разделитель записей'),
    ('Payload01', 'db', (0, 0, 0), 'байты до следующего разделителя записей'),
    ('Record02', 'FScriptRecordStart', (0xFE,), 'второй разделитель записей'),
    ('Payload02', 'db', (0, 0), 'байты до следующего разделителя групп'),
    ('Group02', 'FScriptGroupStart', (0xFF,), 'второй разделитель групп'),
    ('Record03', 'FScriptRecordStart', (0xFE,), 'разделитель записи после второй группы'),
    ('Payload03', 'db', (0, 0, 0, 0, 0), 'исходные байты до EmptyCallback'),
)


def render(source):
    lines = [f'                module {MODULE}',
             '                ; Документация [режимы и ресурс LANG](../../../Docs/StationScriptFields.md)',
             f'                assert $ == #{ORIGIN:04X}']
    address = ORIGIN
    symbols = {}
    for label, kind, values, comment in LAYOUT:
        symbols[f'{MODULE}.{label}'] = address
        assert source[address - 0x6000:address - 0x6000 + len(values)] == bytes(values)
        literals = ', '.join(f'#{value:02X}' for value in values)
        if kind == 'db':
            lines.append(f'{label + ":":16}db {literals}'.ljust(80) + '; ' + comment)
        else:
            lines.extend((f'{label + ":":16}{kind} {{',
                          f'                    {literals}'.ljust(80) + '; ' + comment,
                          '                }'))
            field = 'Value' if kind == 'FScriptModeByte' else 'Marker'
            symbols[f'{MODULE}.{label}.{field}'] = address
        address += len(values)
    assert address == END + 0x6000
    lines.extend((f'                assert $ == #{address:04X}', '                endmodule'))
    return '\n'.join(lines) + '\n', symbols


def parse(text):
    lines = [line.split(';', 1)[0].strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    assert lines[:2] == [f'module {MODULE}', f'assert $ == #{ORIGIN:04X}']
    assert lines[-2:] == [f'assert $ == #{END + 0x6000:04X}', 'endmodule']
    code = '\n'.join(lines[2:-2])
    pattern = r'^(\w+):\s*(?:(db)\s+([^\n]+)|(FScript\w+)\s*\{\s*([^}]+)\})'
    records = list(re.finditer(pattern, code, re.MULTILINE))
    assert len(records) == len(LAYOUT)
    result = bytearray()
    end = 0
    for record, (expected, kind, values, _) in zip(records, LAYOUT):
        assert not code[end:record.start()].strip()
        end = record.end()
        label, directive, data, structure, fields = record.groups()
        assert (label, directive or structure) == (expected, kind)
        tokens = (data or fields).strip().split(', ')
        assert len(tokens) == len(values) and all(re.fullmatch(r'#[0-9A-F]{2}', token) for token in tokens)
        result.extend(int(token[1:], 16) for token in tokens)
    assert not code[end:].strip()
    return bytes(result)


def check_runtime(station, lang):
    from CheckMusic import Simulator, get_registers, SP

    initial = bytearray(65536)
    initial[0x6000:0xC000] = station[:0x6000]
    initial[0xC000:0xC000 + len(lang)] = lang
    initial[0x7FFE:0x8000] = b'\xff\x3f'
    memory = initial.copy()
    cpu = Simulator(memory)

    def run(entry, argument, *, mode=0):
        encoded = argument.encode('ascii') + b'!'
        memory[0xB000:0xB000 + len(encoded)] = encoded
        cpu.registers[:] = get_registers({'IX': 0xB000, 'SP': 0x7FFE, '^HL': 0xB800,
                                         '^AF': mode << 8}, None, False)
        cpu.run(start=entry, stop=0x3FFF)
        assert cpu.registers[SP] == 0x8000
        return cpu.registers[6] * 256 + cpu.registers[7]

    mode_cases = 0
    for base, first_index, reader, writer in ((0x9A33, 8, 0xC34D, 0xC189), (0x9A42, 0, 0xC342, 0xC191)):
        for index in range(first_index, first_index + 7):
            address = base + index
            memory[:] = initial
            assert run(reader, str(index)) == address
            assert memory[0xB800:0xB802] == bytes((initial[address], 0))
            for mode in (0, 1, 0x80, 0xFF):
                before = memory[ORIGIN:END + 0x6000]
                before[address - ORIGIN] = mode
                assert run(writer, str(index + 1), mode=mode) == address
                assert memory[ORIGIN:END + 0x6000] == before
                assert run(reader, str(index)) == address and memory[0xB800:0xB802] == bytes((mode, 0))
                mode_cases += 1

    resource_cases = 0
    markers = ((1, 1, 0x9A4A, 4), (1, 2, 0x9A4E, 3), (1, 3, 0x9A52, 6), (2, 1, 0x9A52, 6))
    for group, record, marker, length in markers:
        for offset in range(length):
            memory[:] = initial
            address = marker + offset
            assert run(0xC362, f'{group},{record},{offset}') == address
            assert memory[0xB800:0xB802] == bytes((initial[address], 0))
            memory[0x9A1C:0x9A1E] = bytes((group, record))
            assert run(0xC355, str(offset)) == address
            assert memory[0xB800:0xB802] == bytes((initial[address], 0))
            resource_cases += 1
    return dict(mode_write_read_profiles=mode_cases, resource_read_profiles=resource_cases,
                resource_read_profiles_via_stored_selection=resource_cases,
                marker_routes=[list(profile[:3]) for profile in markers])


if __name__ == '__main__':
    import json
    from CheckStationFlightCycle import ROOT, payload

    report = dict(passed=True, **check_runtime(payload(4), payload(5)),
                  physical_bytes=END - START, mode_and_record_game_meanings_proved=False,
                  assembly_executed=False, native_execution=False)
    output = ROOT / 'Tools/Disasm/Reports/StationScriptFieldsVerification.json'
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
