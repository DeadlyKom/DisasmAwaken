"""Сверка исходников ENGINE и физической разметки без ассемблирования."""
from hashlib import sha256
import json
import re

from InspectZ80 import ROOT, decoder
from VerifySources import structure_symbols


ORIGIN = 0x4000
DISK_OFFSET = 0x8B100
PHYSICAL_SIZE = 0x1100
LOGICAL_SIZE = 0x105B
DRIVER = ROOT / 'Source/Files/46_ENGINE.inc'
ARCHIVE = ROOT / 'Tools/Disasm/Extracted/Archived'
INCBIN = r'incbin "([^"]+)"(?:, #([0-9A-F]+), #([0-9A-F]+))?'


def source_lines(path):
    return [line.partition(';')[0].strip() for line in path.read_text('utf-8').splitlines()]


def constants():
    result = structure_symbols()
    for relative in ('Includes/Const/ArchiveEngine.inc', 'Includes/Variables/ArchiveEngine.inc',
                     'Includes/Const/ArchiveRun.inc', 'Includes/Const/ArchiveStart.inc',
                     'Includes/Const/Include.inc', 'Includes/Variables/Include.inc'):
        module = ''
        for line in source_lines(ROOT / relative):
            if match := re.fullmatch(r'module\s+(\w+)', line):
                module = match[1]
            elif line == 'endmodule':
                module = ''
            elif module and (match := re.fullmatch(r'(\w+)\s+equ\s+#([0-9a-fA-F]+)', line)):
                result[f'{module}.{match[1]}'.upper()] = int(match[2], 16)
    return result


def read_structure(lines, kind, key, address, symbols, memory, deferred):
    fields = sorted((offset, name[len(kind) + 1:]) for name, offset in symbols.items()
                    if name.startswith(kind + '.'))
    parents = {field.rsplit('.', 1)[0] for _, field in fields if '.' in field}
    leaves = [(offset, field) for offset, field in fields if field not in parents]
    ends = [offset for offset, _ in leaves[1:]] + [symbols[kind]]
    values = []
    depth = 1
    while depth:
        line = next(lines)
        if line == '{':
            depth += 1
        elif line in ('}', '},'):
            depth -= 1
        else:
            value = re.fullmatch(r'(#[0-9A-F]+|@[A-Za-z0-9_.]+|(?:HIGH|LOW)\(@[A-Za-z0-9_.]+\)),?', line)
            assert value, line
            values.append(value[1])
    assert len(values) == len(leaves), (key, len(values), len(leaves))
    for offset, field in fields:
        symbols[f'{key}.{field}'] = address + offset
    result = bytearray()
    for initializer, (offset, _), end in zip(values, leaves, ends):
        width = end - offset
        if initializer.startswith('#'):
            value = int(initializer[1:], 16)
        elif part := re.fullmatch(r'(HIGH|LOW)\(@([A-Za-z0-9_.]+)\)', initializer):
            shift = 8 if part[1] == 'HIGH' else 0
            value = (symbols[part[2].upper()] >> shift) & 255
        else:
            name = initializer[1:].upper()
            if name in symbols:
                value = symbols[name]
            else:
                value = int.from_bytes(memory[address + offset:address + end], 'little')
                deferred.append((name, value))
        result.extend(value.to_bytes(width, 'little'))
    return result


def read_module(path, address, end, symbols, instruction_decoder, memory, deferred, macros):
    module = []
    instructions = []
    physical_keys = bytearray()
    structured_bytes = 0
    lines = iter(filter(None, source_lines(path)))
    for line in lines:
        if line.startswith('module '):
            module.append(line.split()[1])
            continue
        if line == 'endmodule':
            module.pop()
            continue
        label = re.match(r'(\w+):\s*', line)
        if label:
            key = '.'.join([*module, label[1]]).upper()
            assert key not in symbols
            symbols[key] = address
            line = line[label.end():]
        if record := re.fullmatch(r'FTrDosFileKey\s+\{\s*\{ "(.{8})" \},\s*#([0-9A-F]{2}) \}', line):
            physical_keys.extend(record[1].encode('ascii'))
            physical_keys.append(int(record[2], 16))
            address += symbols['FTRDOSFILEKEY']
            structured_bytes += symbols['FTRDOSFILEKEY']
        elif record := re.fullmatch(r'(FArchive\w+|FBasicLineHeader|FBasicSmallInteger|FTrDosBasicAutostart)\s+\{', line):
            assert label
            kind = record[1].upper()
            physical_keys.extend(read_structure(lines, kind, key, address, symbols, memory, deferred))
            address += symbols[kind]
            structured_bytes += symbols[kind]
        elif span := re.fullmatch(INCBIN, line):
            data = read_slice(path, span)
            physical_keys.extend(data)
            address += len(data)
        elif line.startswith('db '):
            atom = r'"[^"\r\n]*"|#[0-9A-F]{2}'
            values = line[3:]
            assert re.fullmatch(rf'(?:{atom})(?:,\s*(?:{atom}))*', values), line
            data = b''.join(value[1:-1].encode('ascii') if value.startswith('"') else bytes.fromhex(value[1:])
                            for value in re.findall(atom, values))
            physical_keys.extend(data)
            address += len(data)
        elif word := re.fullmatch(r'dw\s+(#[0-9A-F]{4}|@[A-Za-z0-9_.]+)', line):
            if word[1].startswith('#'):
                value = int(word[1][1:], 16)
            else:
                name = word[1][1:].upper()
                value = int.from_bytes(memory[address:address + 2], 'little')
                deferred.append((name, value))
            physical_keys.extend(value.to_bytes(2, 'little'))
            address += 2
        elif fill := re.fullmatch(r'ds\s+#([0-9A-F]{4}),\s*#([0-9A-F]{2})', line):
            length, byte = (int(value, 16) for value in fill.groups())
            physical_keys.extend(bytes((byte,)) * length)
            address += length
        else:
            name, _, arguments = line.partition(' ')
            operations = [line]
            if name.upper() in macros:
                parameters, body = macros[name.upper()]
                replacements = dict(zip(parameters, map(str.strip, arguments.split(',')), strict=True))
                operations = [re.sub(r'\b\w+\b', lambda m: replacements.get(m[0], m[0]), op) for op in body]
            for operation in operations:
                expected, *_ = instruction_decoder.disassemble(address, address + 1, 'h')
                instructions.append((address, operation, expected.operation))
                address += len(expected.bytes)
    assert not module and address == end, (path.name, address, end)
    return instructions, bytes(physical_keys), structured_bytes


def read_slice(path, span):
    data = (path.parent / span[1]).read_bytes()
    if span[2] is None:
        return data
    start, size = int(span[2], 16), int(span[3], 16)
    assert start + size <= len(data)
    return data[start:start + size]


def compare_source(raw, driver=DRIVER, origin=ORIGIN, *, macros=None, instructions_out=None):
    memory = bytearray(0x10000)
    memory[origin:origin + len(raw)] = raw
    instruction_decoder = decoder(memory)
    symbols = constants()
    lines = [line for line in source_lines(driver) if line]
    instructions = []
    deferred = []
    covered = 0
    structured_bytes = 0
    for index, line in enumerate(lines):
        if span := re.fullmatch(INCBIN, line):
            data = read_slice(driver, span)
            assert data == raw[covered:covered + len(data)]
            covered += len(data)
        elif span := re.fullmatch(r'disp #([0-9A-F]+)', line):
            start = int(span[1], 16)
            include = re.fullmatch(r'include "([^"]+)"', lines[index + 1])
            assert start == origin + covered and include and lines[index + 2] == 'ent'
            end = origin + int(lines[index + 3].split('#')[1], 16)
            rows, records, typed = read_module(driver.parent / include[1], start, end, symbols,
                                              instruction_decoder, memory, deferred, macros or {})
            instructions.extend(rows)
            if records:
                assert records == raw[covered:end - origin] and not rows
                structured_bytes += typed
            covered = end - origin
        elif line.startswith('assert $ == #'):
            assert int(line.split('#')[1], 16) == covered
        else:
            assert line == 'ent' or line.startswith('include '), line
    assert covered == len(raw)
    for name, value in deferred:
        assert symbols[name] == value, (name, symbols[name], value)

    def normalize(line):
        line = re.sub(r'@[A-Z_][A-Z0-9_.]*', lambda m: f'#{symbols[m[0][1:]]:X}', line.upper())
        line = re.sub(r'(HIGH|LOW)\(#([0-9A-F]+)\)',
                      lambda m: f'#{(int(m[2], 16) >> (8 if m[1] == "HIGH" else 0)) & 255:X}', line)
        line = re.sub(r'#([0-9A-F]+)\s*\+\s*(#[0-9A-F]+|[0-9]+)',
                      lambda m: f'#{int(m[1], 16) + (int(m[2][1:], 16) if m[2].startswith("#") else int(m[2])):X}', line)
        line = re.sub(r'#([0-9A-F]+)', lambda m: f'#{int(m[1], 16):X}', line)
        line = re.sub(r'(?<![#A-Z0-9_])\b[0-9]+\b', lambda m: f'#{int(m[0]):X}', line)
        return re.sub(r'\s+', '', line)

    for address, actual, expected in instructions:
        assert normalize(actual) == normalize(expected), (f'{address:04X}', actual, expected)
    if instructions_out is not None:
        instructions_out.extend((address, normalize(actual)) for address, actual, _ in instructions)
    return len(instructions), structured_bytes


def compare_layout(disk):
    layout = (ROOT / 'Tools/Disasm/Disk/Layout.lua').read_text('utf-8')
    unit_text = (ROOT / 'Tools/Disasm/Disk/BuildUnits.lua').read_text('utf-8')
    builder = (ROOT / 'Builder/Main.asm').read_text('utf-8')
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    names = re.findall(r'SAVETRD "Awakenv02\.trd", "S(\d{2})\.C", 0, (\d+)', builder)
    entries = re.findall(r'\{slot=(\d+), offset=(\d+), size=(\d+)(, archived=true)?\}', unit_text)
    assert [(int(n), int(size)) for n, size in names] == [(int(s), int(size)) for s, _, size, _ in entries]
    archive_files = {44: ('BASIC', '_K-II.d2.B'), 45: ('RUN', 'RUN.C'),
                     46: ('ENGINE', 'ENGINE.C'), 47: ('START', 'START.C')}
    assert {int(slot) for slot, _, _, archived in entries if archived} == set(archive_files)
    assert sum(not archived for _, _, _, archived in entries) == 41
    files = {row['slot']: row for row in manifest['entries']}
    chunks = []
    for slot, offset, size, archived in entries:
        slot, offset, size = int(slot), int(offset), int(size)
        if archived:
            name, archive_key = archive_files[slot]
            assert f'include "../Source/Files/{slot}_{name}.inc"' in builder
            header = disk[16 * slot:16 * (slot + 1)]
            assert header[0] == 0 and header[13] * 256 == size
            assert (header[15] * 16 + header[14]) * 256 == offset
            data = (ARCHIVE / f'{slot}_{archive_key}.sectors.bin').read_bytes()
        else:
            original = files[slot]
            assert not original['deleted'] and original['offset'] == offset
            data = (ROOT / (original['path'] + '.sectors.bin')).read_bytes()
        assert len(data) == size
        chunks.append((offset, data))
    for offset, size, path, start, source_size in re.findall(
            r'\{offset=(\d+), size=(\d+), path="([^"]+)"(?:, source_offset=(\d+), source_size=(\d+))?\}', layout):
        offset, size = int(offset), int(size)
        data = (ROOT / path).read_bytes()
        if start:
            assert len(data) == int(source_size)
            start = int(start)
            data = data[start:start + size]
        assert len(data) == size
        chunks.append((offset, data))
    cursor = 0
    for offset, data in sorted(chunks):
        assert offset == cursor and disk[offset:offset + len(data)] == data
        cursor += len(data)
    assert cursor == len(disk) == 655360


def main():
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    raw = (ARCHIVE / '46_ENGINE.C.sectors.bin').read_bytes()
    tail = (ARCHIVE / '46_ENGINE.C.tail.bin').read_bytes()
    assert raw == disk[DISK_OFFSET:DISK_OFFSET + PHYSICAL_SIZE]
    assert tail == raw[LOGICAL_SIZE:] and disk[46 * 16] == 0
    instructions, structured = compare_source(raw)
    compare_layout(disk)
    result = dict(passed=True, slot=46, original_disk_offset=DISK_OFFSET, origin=ORIGIN,
                  instructions=instructions, structured_bytes=structured, verified_disk_layout_bytes=len(disk),
                  engine_physical_sha256=sha256(raw).hexdigest(), assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveEngineSourceVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
