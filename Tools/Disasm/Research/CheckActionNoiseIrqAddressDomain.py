"""Границы обращений ROM IM 1 при штатной рамке шумового HALT."""
from hashlib import sha256
from copy import deepcopy
import json
from pathlib import Path
import re

from Analyze import decoder
from CheckActionNoiseExit import ACTION_TAIL, NOISE_DI, NOISE_HALT, ROM48, ROM128, ROOT, flat_action


NOISE_ENTRY_SP = 0xBFFC
HALT_SP = NOISE_ENTRY_SP - 2
TAIL_START = 0xFFE0
INDEXED_IY = {0x0045: 0x40, 0x02FC: 7, 0x02FF: 1, 0x030B: 1, 0x035A: 0x30, 0x3870: 1}
IY_WRITERS = {0x0045, 0x030B}

# Диапазоны включают обе границы. Порты с (C) не обращаются к памяти.
OTHER_INDIRECT = (
    ('HL', (0x5C00, 0x5C07), (0x02C6, 0x02CB, 0x02CF, 0x02DF, 0x02E6, 0x02E9,
                              0x02EE, 0x02F2, 0x02F4, 0x02FA, 0x0307, 0x0311,
                              0x0314, 0x0319, 0x031B, 0x3A52, 0x3A56, 0x3A5C,
                              0x3A60, 0x3A71, 0x3A78, 0x3A7B, 0x3A80, 0x3A84,
                              0x3A86, 0x3A8E, 0x3A93, 0x3A9F, 0x3AA2, 0x3AA9, 0x3AAB)),
    ('HL', (0x0205, 0x022B), (0x0330,)),
    ('HL', (0x01EB, 0x0328), (0x034D,)),
    ('IX', (0x5B88, 0x5B8A), (0x39C3, 0x39D9, 0x39F0)),
    ('HL', (0x3A3F, 0x3A41), (0x39F3,)),
    ('HL', (0x5C3B, 0x5C3B), (0x3A9B,)),
    ('HL', (0x5B66, 0x5B66), (0x3AB2, 0x3AE1)),
    ('HL', (0x3B13, 0x3C24), (0x3B10,)),
)
INDIRECT_REGISTER = re.compile(r'\((HL|DE|BC|SP|IX|IY)(?:[+-]#[0-9A-F]+)?\)')
DIRECT_BRANCH = re.compile(r'(JP|JR|CALL|DJNZ) (?:(\w+),)?#([0-9A-F]+)')
BLOCK_MEMORY = {
    'LDI', 'LDIR', 'LDD', 'LDDR', 'CPI', 'CPIR', 'CPD', 'CPDR', 'INI', 'INIR',
    'IND', 'INDR', 'OUTI', 'OTIR', 'OUTD', 'OTDR', 'RLD', 'RRD',
}


def walk_irq(rom):
    dis = decoder(rom + bytes(0x10000 - len(rom)))
    pending = [(0x0038, (NOISE_DI,))]
    seen, instructions, exits = set(), {}, set()
    max_words = 0
    while pending:
        pc, stack = state = pending.pop()
        if state in seen:
            continue
        seen.add(state)
        max_words = max(max_words, len(stack))
        if pc == NOISE_DI:
            exits.add(stack)
            continue
        assert pc < len(rom)
        instruction = instructions.get(pc)
        if instruction is None:
            instruction = instructions[pc] = dis.disassemble(pc, pc + 1, 'h')[0]
        operation = instruction.operation
        next_pc = pc + len(instruction.bytes)
        if branch := DIRECT_BRANCH.fullmatch(operation):
            mnemonic, condition, address = branch.groups()
            pending.append((int(address, 16), stack + (next_pc,) if mnemonic == 'CALL' else stack))
            if condition or mnemonic == 'DJNZ':
                pending.append((next_pc, stack))
        elif operation == 'RET' or operation.startswith('RET '):
            assert stack and isinstance(stack[-1], int), (pc, stack)
            pending.append((stack[-1], stack[:-1]))
            if operation != 'RET':
                pending.append((next_pc, stack))
        elif operation.startswith('PUSH '):
            pending.append((next_pc, stack + (operation[5:],)))
        elif operation.startswith('POP '):
            assert stack and stack[-1] == operation[4:], (pc, stack)
            pending.append((next_pc, stack[:-1]))
        else:
            assert not operation.startswith(('RST', 'JP', 'JR', 'CALL', 'DJNZ', 'DB', 'HALT', 'RET'))
            assert 'SP' not in operation
            pending.append((next_pc, stack))
    assert exits == {()}
    return instructions, len(seen), max_words


def check_rom(path, action, *, extended):
    rom = Path(path).read_bytes()
    digest = sha256(rom).hexdigest()
    # Границы OTHER_INDIRECT сверены по этим версиям ROM.
    assert digest == ('8d93c3342321e9d1e51d60afcd7d15f6a7afd978c231b43435a7c0757c60b9a3' if extended else
                      'd55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42')
    instructions, states, max_words = walk_irq(rom)
    assert (len(instructions), states, max_words) == ((564, 975, 16) if extended else (193, 194, 8))
    operations = {pc: item.operation for pc, item in instructions.items()}
    assert {pc for pc, op in operations.items() if op == 'EI'} == {0x0051}
    assert operations[0x0052] == 'RET'
    assert not BLOCK_MEMORY.intersection(operations.values())
    assert {pc for pc, op in operations.items() if op.startswith('OUT ')} == (
        {0x3888, 0x388E, 0x3899, 0x389C, 0x38A2} if extended else set()
    )
    assert {pc for pc, op in operations.items() if 'IY' in op} == (
        INDEXED_IY.keys() if extended else INDEXED_IY.keys() - {0x3870}
    )

    words = [int.from_bytes(rom[0x10FE + seed:0x1100 + seed], 'little') for seed in range(256)]
    words.append(0x5C3A)
    stack_bottom = HALT_SP - max_words * 2
    iy_rows, other_rows, absolute_rows = [], [], []
    covered = set()
    for pc, offset in INDEXED_IY.items():
        if pc not in operations:
            continue
        assert f'(IY+#{offset:02X})' in operations[pc]
        effective = {(iy + offset) & 0xFFFF for iy in words}
        if pc in IY_WRITERS:
            assert effective.isdisjoint(range(stack_bottom, 0xC000))
        iy_rows.append(dict(pc=pc, offset=offset, distinct_addresses=len(effective),
                            effective_addresses=sorted(effective),
                            max_address=max(effective), writes=pc in IY_WRITERS))
        covered.add(pc)
    for register, bounds, sites in OTHER_INDIRECT:
        if not extended:
            sites = tuple(pc for pc in sites if pc < 0x3800)
        if not sites:
            continue
        for pc in sites:
            assert INDIRECT_REGISTER.search(operations[pc])[1] == register
        assert bounds[1] < stack_bottom
        other_rows.append(dict(register=register, addresses_inclusive=bounds, pcs=sites))
        covered.update(sites)
    indirect = {pc for pc, op in operations.items() if INDIRECT_REGISTER.search(op)}
    assert covered == indirect
    for pc, op in operations.items():
        if address := re.search(r'\(#([0-9A-F]{4})\)', op):
            absolute_rows.append(dict(pc=pc, address=int(address[1], 16)))
    assert max(row['address'] + 1 for row in absolute_rows) < stack_bottom
    assert max(row['max_address'] for row in iy_rows) == 0xFF7E < TAIL_START
    letter_rows = sorted({(iy + 1, iy + 0x30) for iy in words if ACTION_TAIL <= iy + 0x30 < 0x10000})
    assert len(letter_rows) == 14 and all(action[flag] == 0 for flag, _ in letter_rows)
    increment_addresses = {(iy + INDEXED_IY[0x0045]) & 0xFFFF for iy in words}
    enabled_by_rom_increment = [(flag, target) for flag, target in letter_rows if flag in increment_addresses]
    assert enabled_by_rom_increment == [(0xFD7C, 0xFDAB)]
    # Проверка трёх соседних байтов, байтовый INC не переносит запись на следующую ячейку.
    adjacent = []
    for address in (0xFE63, 0xFE64, 0xFE65):
        readers = [row['pc'] for row in iy_rows if address in row['effective_addresses']]
        writers = [row['pc'] for row in iy_rows if row['writes'] and address in row['effective_addresses']]
        assert all(not first <= address <= last for _, (first, last), _ in OTHER_INDIRECT)
        assert address < stack_bottom or address >= HALT_SP
        assert all(address not in (row['address'], row['address'] + 1) for row in absolute_rows)
        adjacent.append(dict(address=address, original_byte=action[address],
                             possible_indexed_readers=readers, possible_indexed_writers=writers,
                             other_irq_addressing_excluded=True))
    assert [row['possible_indexed_readers'] for row in adjacent] == [[0x0045], [], [0x02FC]]
    assert [row['possible_indexed_writers'] for row in adjacent] == [[0x0045], [], []]
    return dict(rom=Path(path).name, sha256=digest, instructions=len(instructions),
                control_states=states, stack_bytes_including_irq_pc=2 * max_words, stack_bottom=stack_bottom,
                iy_accesses=iy_rows, other_indirect_accesses=other_rows, absolute_accesses=absolute_rows,
                letter_flag_and_target_candidates=letter_rows, letter_pair_enabled_by_rom_increment=enabled_by_rom_increment,
                adjacent_fe63_fe64_fe65=adjacent,
                returns_to_noise_di_with_restored_sp=True)


def target_accesses(profile, address):
    """Консервативные обращения к одному байту, включая чтения и второй байт слова."""
    indexed = [row['pc'] for row in profile['iy_accesses']
               if address in row['effective_addresses']]
    indirect = [pc for row in profile['other_indirect_accesses']
                if row['addresses_inclusive'][0] <= address <= row['addresses_inclusive'][1]
                for pc in row['pcs']]
    absolute = [row['pc'] for row in profile['absolute_accesses']
                if address in (row['address'], (row['address'] + 1) & 0xFFFF)]
    # Проверка включает всю консервативную рамку, а не только адреса отдельных PUSH.
    stack = profile['stack_bottom'] <= address < HALT_SP
    return dict(address=address, indexed_pcs=indexed, other_indirect_pcs=indirect,
                absolute_pcs=absolute, stack_access_possible=stack,
                access_possible=bool(indexed or indirect or absolute or stack))


def main():
    action = flat_action()
    assert bytes(action[0x606C:NOISE_DI + 1]) == bytes.fromhex(
        'C5 11 00 80 ED 5F 6F 26 05 01 00 0C ED B0 FB 76 F3'
    )
    assert action[NOISE_HALT] == 0x76
    profiles = [check_rom(ROM48, action, extended=False), check_rom(ROM128[1], action, extended=True)]
    # Проверка обоих байтов длины, отсутствие числового адреса исключает любой банк.
    for profile in profiles:
        profile['temporary_module_length_accesses'] = [target_accesses(profile, address)
                                                       for address in (0xDB01, 0xDB02)]
        assert not any(row['access_possible'] for row in profile['temporary_module_length_accesses'])
        # Контроль обнаружения индексной записи, абсолютного слова и рамки стека.
        assert target_accesses(profile, profile['iy_accesses'][0]['effective_addresses'][0])['access_possible']
        assert target_accesses(profile, profile['absolute_accesses'][0]['address'] + 1)['access_possible']
        assert target_accesses(profile, profile['stack_bottom'])['stack_access_possible']
        # Контроль ложного отрицания, каждая разновидность адреса отдельно достигает DB01.
        for addressing in ('indexed', 'indirect', 'absolute_word'):
            candidate = deepcopy(profile)
            if addressing == 'indexed':
                candidate['iy_accesses'][0]['effective_addresses'].append(0xDB01)
            elif addressing == 'indirect':
                candidate['other_indirect_accesses'][0]['addresses_inclusive'] = (0xDB01, 0xDB02)
            else:
                candidate['absolute_accesses'][0]['address'] = 0xDB00
            assert target_accesses(candidate, 0xDB01)['access_possible'], addressing
    report = dict(passed=True, profiles=profiles, noise_entry_sp=NOISE_ENTRY_SP, noise_halt_sp=HALT_SP,
                  tail_start=TAIL_START,
                  all_conditional_control_outcomes_followed=True, all_noise_iy_words_enumerated=True,
                  rom_irq_tail_access_possible_with_verified_frame=False,
                  rom_irq_temporary_module_length_access_possible_with_verified_frame=False,
                  all_game_irq_handlers_and_stack_frames_proved=False,
                  whole_game_tail_role_proved=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseIrqAddressDomainVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Сверены графы, стеки и адреса доступа ROM 48K и ROM 128K при шумовом IRQ.')


if __name__ == '__main__':
    main()
