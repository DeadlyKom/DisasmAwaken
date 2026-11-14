"""Адреса записей BuildParameterTables вместе с исходными дочерними процедурами.

Документация: ../../../Docs/ControlsParameterTables.md
Документация: ../../../Docs/ControlsTemporaryModule.md
"""
from copy import deepcopy
from hashlib import sha256
import json
import re

from CheckIntro import ROOT
from CheckControlsParameterStoreBounds import derive_domains


def inspect_function(rows, children):
    code = {row['address']: row for row in rows}
    assert len(code) == len(rows)
    first = rows[0]['address']
    # Проверка непрерывного покрытия команд, переходы не могут попасть в пробел разметки.
    for left, right in zip(rows, rows[1:]):
        assert left['address'] + len(bytes.fromhex(left['hex'])) == right['address']
    todo = [(first, 0)]
    seen = set()
    stack_depths = set()
    stores = {}
    call_sites = {}
    returns = set()
    # Проверка всех ветвей без предположений о значениях Carry, Zero и Sign.
    while todo:
        pc, depth = todo.pop()
        if (pc, depth) in seen:
            continue
        assert pc in code and 0 <= depth <= 8, (pc, depth)
        seen.add((pc, depth))
        row = code[pc]
        raw = bytes.fromhex(row['hex'])
        op = row['operation']
        following = pc + len(raw)
        if op.startswith('CALL '):
            target = int(op.removeprefix('CALL #'), 16)
            assert raw == b'\xcd' + target.to_bytes(2, 'little')
            assert target in children
            # Расчёт записей возврата CALL и всех вложенных стековых записей.
            stack_depths.update((depth + 1, depth + 2))
            stack_depths.update(depth + 2 + d for d in children[target]['stack_depths'])
            call_sites[pc] = target
        elif op.startswith('PUSH '):
            assert (op, raw) in [('PUSH BC', b'\xc5'), ('PUSH DE', b'\xd5')]
            stack_depths.update((depth + 1, depth + 2))
            depth += 2
        elif op.startswith('POP '):
            assert (op, raw) in [('POP BC', b'\xc1'), ('POP DE', b'\xd1')]
            depth -= 2
            assert depth >= 0
        elif op.startswith('RET'):
            assert (op, raw) in [('RET', b'\xc9'), ('RET C', b'\xd8'), ('RET NC', b'\xd0')]
            assert depth == 0, (pc, depth)
            returns.add(pc)
            if op == 'RET':
                continue
        elif op.startswith(('JP ', 'JR ', 'DJNZ ')):
            match = re.fullmatch(r'(JP|JR|DJNZ) (?:(NZ|Z|NC|C|P),)?#([0-9A-F]+)', op)
            assert match, op
            mnemonic, condition, target = match.groups()
            target = int(target, 16)
            assert target in code
            # Проверка цели по фактическому операнду команды, а не одному тексту реестра.
            if mnemonic == 'JP':
                assert raw[0] in (0xC2, 0xF2) and int.from_bytes(raw[1:], 'little') == target
            else:
                assert raw[0] in (0x10, 0x18, 0x20, 0x28, 0x30, 0x38)
                assert (following + int.from_bytes(raw[1:], 'little', signed=True)) & 65535 == target
            todo.append((target, depth))
            if condition is None and mnemonic != 'DJNZ':
                continue
        elif raw[0] in (0x22, 0x32) or raw[:2] == b'\xed\x53':
            # Расчёт адресов абсолютных LD по байтам исходной команды.
            prefix = 2 if raw[0] == 0xED else 1
            address = int.from_bytes(raw[prefix:], 'little')
            size = 1 if raw[0] == 0x32 else 2
            assert re.fullmatch(r'LD \(#[0-9A-F]+\),(HL|DE|A)', op)
            stores[pc] = dict(kind='absolute', addresses=[(address + i) & 65535 for i in range(size)])
        elif raw == b'\xdd\x77\x00' and op == 'LD (IX+#00),A':
            stores[pc] = dict(kind='indexed', addresses=[])
        elif raw == b'\x77' and op == 'LD (HL),A':
            stores[pc] = dict(kind='HL', addresses=[])
        else:
            # Проверка закрытого набора остальных операций, ни одна не записывает RAM или SP.
            safe = (
                re.fullmatch(r'LD (A|B|C|D|E|H|L|BC|DE|HL|IX),(A|B|C|D|E|H|L|BC|DE|HL|#[0-9A-F]+|\(#[0-9A-F]+\)|\(HL\)|\(DE\))', op)
                or re.fullmatch(r'(INC|DEC) (A|B|C|D|E|H|L|HL|DE|IX)', op)
                or re.fullmatch(r'(XOR|AND|OR|SUB|CP) (A|B|C|D|E|H|L|#[0-9A-F]+)', op)
                or re.fullmatch(r'(ADD|ADC) (A|HL),(A|B|C|D|E|H|L|BC|DE|HL|\(HL\))', op)
                or op in ("EX AF,AF'", 'EX DE,HL', 'EXX', 'CPL', 'RLCA', 'RRCA', 'NEG', 'RR B', 'SRA A')
            )
            assert safe, (hex(pc), op, raw.hex())
            # Проверка кодов команд отдельно от текстового назначения операндов реестра.
            register_only = (
                raw[0] in (0x01, 0x11, 0x21, 0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x3E,
                           0x03, 0x13, 0x23, 0x0B, 0x1B, 0x2B, 0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x3C,
                           0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x3D,
                           0x08, 0xEB, 0xD9, 0x07, 0x0F, 0x2F, 0x09, 0x19, 0x1A, 0x2A,
                           0x3A, 0xE6, 0xEE, 0xFE)
                or 0x40 <= raw[0] <= 0x6F or 0x78 <= raw[0] <= 0xBF
                or raw in (b'\xed\x44', b'\xcb\x18', b'\xcb\x2f', b'\xdd\x23')
                or raw[:2] in (b'\xed\x5b', b'\xdd\x21'))
            assert register_only, (hex(pc), op, raw.hex())
        todo.append((following, depth))
    assert {pc for pc, _ in seen} == set(code), 'Не вся функция включена в доказательство'
    assert returns
    return dict(stack_depths=sorted(stack_depths), own_stores=stores,
                calls=call_sites, return_sites=sorted(returns))


def derive_report():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entries = {row['slot']: row for row in manifest['entries']}
    payloads = {}
    for slot in (17, 23):
        entry = entries[slot]
        data = (ROOT/(entry['path'] + '.bin')).read_bytes()
        assert data == disk[entry['offset']:entry['offset'] + entry['length']]
        payloads[slot] = data
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    specifications = [
        ('Action', 0x6E2B, 0x6E6C, 'ClassifyCoordinateRegion'),
        ('Controls', 0xDD5D, 0xDD87, 'StepWordRandom'),
        ('Controls', 0xDE9A, 0xDEDC, 'BuildSeededIndices'),
        ('Controls', 0xDE10, 0xDE9A, 'BuildParameterTables')]
    functions = {}
    summaries = {}
    blocks = {}
    # Проверка исходных байтов каждой команды по физическому TRD в двух разных контекстах загрузки.
    for region, first, end, name in specifications:
        rows = [row for block in flow if block['name'] == region
                for row in block['instructions'] if first <= row['address'] < end]
        assert rows and rows[0]['address'] == first
        assert rows[-1]['address'] + len(bytes.fromhex(rows[-1]['hex'])) == end
        for row in rows:
            raw = bytes.fromhex(row['hex'])
            assert row['slot'] == (17 if region == 'Action' else 23)
            assert payloads[row['slot']][row['offset']:row['offset'] + len(raw)] == raw
            assert row['offset'] == (row['address'] - 0x6000 + 0x23D if region == 'Action' else row['address'] - 0xDADE)
        raw = b''.join(bytes.fromhex(row['hex']) for row in rows)
        summary = inspect_function(rows, summaries)
        summaries[first] = summary
        blocks[first] = rows
        functions[region + '.' + name] = dict(entry=first, end_exclusive=end,
            original_code_sha256=sha256(raw).hexdigest(), original_bytes=len(raw), **summary)
    assert summaries[0x6E2B]['own_stores'] == {} and summaries[0x6E2B]['stack_depths'] == []
    expected_random = {0xDD7A: [0x9B15, 0x9B16], 0xDD7D: [0x9B17, 0x9B18]}
    expected_seed = {0xDEA8: [0x9B15, 0x9B16], 0xDEAB: [0x9B17, 0x9B18]}
    for first, expected in ((0xDD5D, expected_random), (0xDE9A, expected_seed)):
        assert {pc: row['addresses'] for pc, row in summaries[first]['own_stores'].items()} == expected
    assert summaries[0xDE10]['stack_depths'] == list(range(1, 9))
    assert summaries[0xDE10]['calls'] == {0xDE1A: 0xDE9A}
    assert summaries[0xDE9A]['calls'] == {0xDEB1: 0x6E2B, 0xDEBD: 0xDD5D}
    # Расчёт полного нестекового множества с уже доказанными циклами родительской функции.
    domains = derive_domains(blocks[0xDE10])
    own = summaries[0xDE10]['own_stores']
    assert set(own) == {0xDE1D, 0xDE69, 0xDE88, 0xDE93}
    assert own[0xDE1D] == dict(kind='absolute', addresses=[0x688B])
    assert own[0xDE69]['kind'] == 'indexed'
    assert own[0xDE88]['kind'] == own[0xDE93]['kind'] == 'HL'
    destinations = sorted(set([0x688B, 0x9B15, 0x9B16, 0x9B17, 0x9B18]
        + domains['parameter_addresses'] + [domains['first_row_address']] + domains['other_row_addresses']))
    assert len(destinations) == 29 and not set(destinations) & {0xDB01, 0xDB02}
    bounds = json.loads((ROOT/'Tools/Disasm/Reports/ControlsParameterStoreBoundsVerification.json').read_bytes())
    assert bounds['passed'] and bounds['domains'] == domains
    assert bounds['original_code_sha256'] == functions['Controls.BuildParameterTables']['original_code_sha256']
    masks = [payloads[23][address - 0xDADE] for address in domains['coefficient_shift_mask_addresses']]
    assert masks == bounds['original_shift_masks'] and all(v and v & (v - 1) == 0 for v in masks)
    # Расчёт всех SP, при которых восемь байтов рамки могут попасть в длину модуля.
    overlap_sp = [sp for sp in range(65536)
        if {(sp - depth) & 65535 for depth in range(1, 9)} & {0xDB01, 0xDB02}]
    assert overlap_sp == list(range(0xDB02, 0xDB0B))
    # Проверка отказа на неизвестном косвенном писателе и внешнем дочернем вызове.
    rejected = []
    for first, pc, operation, raw in [(0xDD5D, 0xDD65, 'LD (DE),A', '12'),
                                    (0xDD5D, 0xDD65, 'LD SP,HL', 'f9'),
                                    (0xDE9A, 0xDEB1, 'CALL #DB01', 'cd01db')]:
        rows = deepcopy(blocks[first])
        row = next(row for row in rows if row['address'] == pc)
        row.update(operation=operation, hex=raw)
        try:
            inspect_function(rows, summaries)
        except AssertionError:
            rejected.append(operation)
        else:
            raise AssertionError(operation)
    result = dict(passed=True, method='original_four_function_control_flow_stack_and_store_invariants',
        original_disk_sha256=manifest['sha256'], functions=functions,
        nonstack_destinations=destinations, nonstack_destination_count=29,
        nonstack_destinations_disjoint_from_DB01_DB02=True,
        maximum_additional_stack_bytes=8, stack_byte_depths=list(range(1, 9)),
        stack_overlap_input_SP=overlap_sp, unsupported_mutations_rejected=rejected,
        all_seeds_and_step_counts_covered_by_static_write_domains=True,
        required_preconditions=['вход через исходный BuildParameterTables.Entry',
            'банк 1 выбран и общее ядро ACTION перенесено в 6000',
            'исходные код и таблицы не меняются извне, исходные ненулевые маски коэффициентов',
            'восемь байтов рамки и внешний возврат доступны, стек не перекрывает код, таблицы и рабочие данные',
            'IRQ, NMI, DMA и иные внешние писатели не вмешиваются'],
        instruction_execution_or_bus_timing_simulated=False,
        all_callers_stack_and_banking_preconditions_proved=False,
        entire_program_length_writers_excluded=False, legitimate_temporary_module_entry_proved=False,
        nonzero_temporary_module_length_writer_proved=False, assembly_executed=False, native_execution=False)
    return result


def main():
    result = derive_report()
    path = ROOT/'Tools/Disasm/Reports/ControlsParameterCallWritesVerification.json'
    serialized = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if path.exists():
        assert path.read_bytes().replace(b'\r\n', b'\n') == serialized, 'Существующий отчёт отличается, автоматическая замена запрещена'
    else:
        path.write_bytes(serialized)
    print('Четыре функции, 29 нестековых адресов, до 8 байтов стека, 9 опасных SP, три отрицательных контроля.')


if __name__ == '__main__':
    main()
