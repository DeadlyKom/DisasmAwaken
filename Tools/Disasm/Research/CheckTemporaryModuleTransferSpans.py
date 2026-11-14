"""Проверка прямых блоковых переносов, пересекающих окна старого загрузчика."""
from collections import Counter
import json
import re

from CheckIntro import ROOT, execute, original_memory


PAIRS = ('HL', 'DE', 'BC')
BLOCK_COPY = ('LDI', 'LDD', 'LDIR', 'LDDR')
WINDOWS = {'fixed_wrapper': (0x5DA0, 0x5EDB), 'fixed_saved_context': (0x5EDB, 0x5F5D),
           'banked_wrapper': (0xDADE, 0xDB5D), 'banked_saved_context': (0xDC19, 0xDC9B),
           'current_font': (0xC600, 0xC870), 'viewport_code_prefix': (0xC870, 0xCA00)}
OPERANDS = {'copy_length': (0x5DC3, 0x5DC5), 'banked_length': (0xDB01, 0xDB03),
            'saved_sp': (0x5E33, 0x5E35), 'legacy_disk_position_and_count': (0x5E20, 0x5E24)}


def interval(start, size, direction):
    begin = (start - size + 1) & 0xFFFF if direction < 0 else start
    end = begin + size
    return [(begin, end)] if end <= 65536 else [(begin, 65536), (0, end - 65536)]


def intersections(start, size, direction):
    result = {}
    for label, (left, right) in WINDOWS.items():
        overlaps = [(max(left, begin), min(right, end)) for begin, end in interval(start, size, direction)
                    if begin < right and end > left]
        if overlaps:
            result[label] = overlaps
    return result


def transfer(row, state, region):
    opcode = row['operation']
    source, target, count = (state[pair] for pair in PAIRS)
    direction = -1 if opcode in ('LDD', 'LDDR') else 1
    repeats = opcode in ('LDIR', 'LDDR')
    size = (None if count is None else count or 65536) if repeats else 1
    result = dict(region=region, slot=row['slot'], pc=row['address'], disk_file_offset=row['offset'],
                  operation=opcode, source=source, target=target, size=size, direction=direction)
    if size is not None:
        result['source_windows'] = intersections(source, size, direction) if source is not None else {}
        result['target_windows'] = intersections(target, size, direction) if target is not None else {}
    state['HL'] = (source + size * direction) & 65535 if source is not None and size is not None else None
    state['DE'] = (target + size * direction) & 65535 if target is not None and size is not None else None
    state['BC'] = 0 if repeats else (count - 1) & 65535 if count is not None else None
    return result


def update(operation, state):
    if literal := re.fullmatch(r'LD (HL|DE|BC),#([0-9A-F]{4})', operation):
        state[literal[1]] = int(literal[2], 16)
    elif operation == 'EX DE,HL':
        state['DE'], state['HL'] = state['HL'], state['DE']
    elif shift := re.fullmatch(r'(INC|DEC) (HL|DE|BC)', operation):
        pair = shift[2]
        if state[pair] is not None:
            state[pair] = (state[pair] + (1 if shift[1] == 'INC' else -1)) & 65535
    elif re.fullmatch(r'(?:LD (?:\([^)]*\)|A|SP|IX|IY),.+|PUSH \w+|OUT .+|DI|EI|NOP|XOR A|OR A|AND #..)', operation):
        pass
    else:
        # Не переносим факты через вызовы, развилки и неподдерживаемые изменения регистров.
        state.update(dict.fromkeys(PAIRS))


def scan(flow):
    for region in flow:
        targets = set(region['roots']) | set(region['calls']) | set(region['branches'])
        targets.update(block['origin'] for block in region['blocks'])
        previous = None
        state = dict.fromkeys(PAIRS)
        for row in region['instructions']:
            pc = row['address']
            if pc in targets or previous != (row['slot'], row['offset'], pc):
                state.update(dict.fromkeys(PAIRS))
            length = len(bytes.fromhex(row['hex']))
            previous = row['slot'], row['offset'] + length, (pc + length) & 65535
            if row['operation'] in BLOCK_COPY:
                yield transfer(row, state, region['name'])
            else:
                update(row['operation'], state)


def direct_stores(flow):
    for region in flow:
        for row in region['instructions']:
            match = re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|HL|DE|BC|IX|IY|SP)', row['operation'])
            if match is None:
                continue
            address = int(match[1], 16)
            size = 1 if match[2] == 'A' else 2
            hits = [name for name, (start, end) in OPERANDS.items()
                    if any(start <= ((address + offset) & 65535) < end for offset in range(size))]
            if hits:
                yield dict(region=region['name'], slot=row['slot'], pc=row['address'],
                           instruction=row['operation'], operand_names=hits)


def check_intro_overlap(transfers):
    copy = next(row for row in transfers if (row['region'], row['pc']) == ('Intro', 0x650A))
    source, target, count = (copy[name] for name in ('source', 'target', 'size'))
    assert (source, target, count) == (0x65B7, 0x5D3B, 256)
    memory = original_memory()
    expected = bytes(memory[source:source + count])
    execute(memory, {'PC': 0x6500}, stop=0x650C)
    assert bytes(memory[target:target + count]) == expected
    assert bytes(memory[0x5DA0:0x5DA6]) == bytes.fromhex('46 43 3E 16 11 FF')
    assert bytes(memory[0x5DC3:0x5DC5]) == b'\x67\x11'
    assert bytes(memory[0x5E33:0x5E35]) == b'\x3F\x32'
    return dict(pc=0x650A, source=source, target=target, bytes_copied=count,
                wrapper_prefix_hex=bytes(memory[0x5DA0:0x5DA6]).hex(),
                length_position_hex=bytes(memory[0x5DC3:0x5DC5]).hex(),
                saved_sp_position_hex=bytes(memory[0x5E33:0x5E35]).hex())


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    flow = json.loads((reports / 'ControlFlow.json').read_bytes())
    transfers = list(scan(flow))
    matches = [row for row in transfers if row.get('source_windows') or row.get('target_windows')]
    stores = list(direct_stores(flow))
    assert {(row['region'], row['pc'], row['instruction']) for row in stores} == {
        ('Help', 0xDB57, 'LD (#DB01),A'), ('ActionBoot', 0x4267, 'LD (#5E20),HL'),
        ('ActionBoot', 0x426A, 'LD (#5E23),A'), ('Controls', 0xDAE0, 'LD (#5E33),SP'),
    }
    wrapper_copies = {(row['region'], row['pc']) for row in matches if 'fixed_wrapper' in row['target_windows']}
    assert wrapper_copies == {('Intro', 0x650A), ('Controls', 0xDB08)}
    report = dict(passed=True, decoded_block_copies=len(transfers),
                  by_opcode=dict(Counter(row['operation'] for row in transfers)),
                  known_size_and_target=sum(row['size'] is not None and row['target'] is not None for row in transfers),
                  known_all_operands=sum(None not in (row['source'], row['target'], row['size']) for row in transfers),
                  matching_transfers=matches, overlapping_direct_stores=stores,
                  intro_overlap=check_intro_overlap(transfers), assumed_straight_line_only=True,
                  mutable_operands_and_selected_banks_inferred=False,
                  ordinary_game_caller_proved=False, assembly_executed=False)
    (reports / 'TemporaryModuleTransferSpansVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for row in matches:
        print(f"{row['region']} #{row['pc']:04X} {row['operation']} "
              f"{row['source']!r} -> {row['target']!r}, {row['size']}: "
              f"{list(row['source_windows'])} -> {list(row['target_windows'])}")


if __name__ == '__main__':
    main()
