"""Зависимость A/F от свежего чтения Mode до нормализатора, без исполнения игры.

Документация: ../../../Docs/ControlsCircleWork.md#зависимость-свежего-чтения-mode-в-префиксах
Сохранённый ранее AF и возвращающие Mode-флаги пути не объявляются независимыми.
"""
from hashlib import sha256
import json
import re

from CheckStationFlightCycle import ROOT, payload


ENCODINGS = {
    'LD A,(#D18C)': '3a8cd1', 'AND A': 'a7',
    'LD A,E': '7b', 'LD A,L': '7d', 'LD A,B': '78', 'LD A,C': '79',
    'LD A,(#D17F)': '3a7fd1', 'LD B,#00': '0600', 'LD B,#FF': '06ff',
    'LD C,#00': '0e00', 'AND #1F': 'e61f', 'AND #E0': 'e6e0',
    'OR #1F': 'f61f', 'SUB L': '95', 'BIT 1,A': 'cb4f',
    'INC A': '3c', 'SLL C': 'cb31',
    'LD C,A': '4f', 'LD HL,#FFE0': '21e0ff', 'LD HL,#3880': '218038',
    'LD HL,#0020': '212000', 'LD HL,#308C': '218c30',
    'LD (#D5B5),HL': '22b5d5', 'LD (#D600),HL': '2200d6',
    'PUSH DE': 'd5', 'PUSH AF': 'f5', 'LD L,A': '6f', 'LD H,#04': '2604',
    'ADD HL,HL': '29', 'LD DE,#001F': '111f00', 'ADD HL,DE': '19',
    'PUSH BC': 'c5', 'DEC B': '05', 'INC B': '04', 'LD DE,#0020': '112000',
    'LD C,L': '4d', 'LD A,IXL': 'dd7d', 'DEC L': '2d', 'LD (HL),A': '77',
    'LD L,C': '69', 'XOR IXH': 'ddac', 'LD IXL,A': 'dd6f', 'LD A,H': '7c',
    'CP #00': 'fe00', 'POP BC': 'c1', 'POP AF': 'f1', 'POP DE': 'd1', 'RET': 'c9',
    'PUSH HL': 'e5', 'LD H,#C3': '26c3', 'LD E,(HL)': '5e',
    'INC H': '24', 'LD D,(HL)': '56', 'POP HL': 'e1',
    'LD L,D': '6a', 'ADD A,A': '87', 'SUB #3E': 'd63e', 'NEG': 'ed44',
    'LD (#CEB4),A': '32b4ce',
    'LD BC,(#D181)': 'ed4b81d1', 'LD A,#88': '3e88', 'SUB B': '90', 'EXX': 'd9',
    'LD A,(#D185)': '3a85d1', 'LD E,A': '5f', 'OR #01': 'f601',
    'LD C,#FF': '0eff', 'BIT 0,A': 'cb47',
}


def checked_sequence(code, source, start, operations):
    """Проверка соседних инструкций, включая независимое кодирование переходов."""
    pc = start
    trace = []
    for op in operations:
        row = code[pc]
        assert row['operation'] == op and row['slot'] == 22
        raw = bytes.fromhex(row['hex'])
        absolute = re.fullmatch(r'(JP|CALL) (?:(NZ|Z),)?#([0-9A-F]{4})', op)
        relative = re.fullmatch(r'(JR(?: Z,| NC,| )|DJNZ )#([0-9A-F]{4})', op)
        if absolute:
            opcode = {('JP', None): 0xC3, ('CALL', None): 0xCD,
                      ('CALL', 'NZ'): 0xC4, ('CALL', 'Z'): 0xCC}[absolute[1], absolute[2]]
            expected = bytes((opcode,)) + int(absolute[3], 16).to_bytes(2, 'little')
        elif relative:
            opcode = {'JR ': 0x18, 'JR Z,': 0x28, 'JR NC,': 0x30, 'DJNZ ': 0x10}[relative[1]]
            expected = bytes((opcode, (int(relative[2], 16) - pc - 2) & 255))
        else:
            expected = bytes.fromhex(ENCODINGS[op])
        assert raw == expected
        assert source[row['offset']:row['offset'] + len(raw)] == raw
        trace.append(pc)
        pc += len(raw)
    return trace


def returned_mode_flags(code, source):
    """Два сохранения F заливки и прямой возврат F левого подготовителя."""
    up = checked_sequence(code, source, 0xD208,
        ['LD C,A', 'LD A,(#D18C)', 'AND A', 'LD A,C', 'JP #D58A'])
    down = checked_sequence(code, source, 0xD211,
        ['LD C,A', 'LD A,(#D18C)', 'AND A', 'LD A,C', 'JP #D595'])
    checked_sequence(code, source, 0xD58A,
        ['LD HL,#FFE0', 'LD (#D5B5),HL', 'LD HL,#3880', 'JR #D59E'])
    checked_sequence(code, source, 0xD595,
        ['LD HL,#0020', 'LD (#D5B5),HL', 'LD HL,#308C'])
    # A уже содержит чистый номер строки, только S/Z/PV/X/Y текущего F зависят от Mode.
    setup = checked_sequence(code, source, 0xD59E,
        ['LD (#D600),HL', 'PUSH DE', 'PUSH AF', 'LD L,A', 'LD H,#04']
        + ['ADD HL,HL'] * 5
        + ['LD DE,#001F', 'ADD HL,DE', 'PUSH BC', 'DEC B', 'INC B', 'JR Z,#D605'])
    assert setup[2] == 0xD5A2 and setup[-3:] == [0xD5B0, 0xD5B1, 0xD5B2]
    # ADD HL заменяет H/N/C/X/Y, сохраняя Mode-зависимость только S/Z/PV.
    dependencies_after_add = 0xEC & 0xC4
    # DEC B заменяет всё кроме уже независимого Carry, затем INC B восстанавливает B.
    assert dependencies_after_add & 1 == 0
    body = checked_sequence(code, source, 0xD5B4,
        ['LD DE,#0020', 'LD C,L', 'LD A,IXL']
        + ['DEC L', 'LD (HL),A'] * 30
        + ['LD L,C', 'ADD HL,DE', 'LD A,IXL', 'XOR IXH', 'LD IXL,A', 'LD A,H',
           'CP #00', 'JR NC,#D605', 'DJNZ #D5B7', 'POP BC', 'POP AF', 'POP DE', 'RET'])
    assert body[-4:] == [0xD605, 0xD606, 0xD607, 0xD608]
    # До завершающих POP в петле нет ни чтений памяти, ни потребления рамки CPU-стека.
    # При неперекрывающемся стеке зависимое слово F не может стать пиксельным источником.
    left = checked_sequence(code, source, 0xD4F9,
        ['LD A,(#D18C)', 'AND A', 'LD A,B', 'LD B,#00', 'RET'])
    # Статическое описание реальной рамки должно совпадать с обратным порядком PUSH.
    structures = (ROOT / 'Includes/Structs/Include.inc').read_text(encoding='utf-8')
    frame = re.search(r'^\s*struct FInteriorRowsFrame\s*$\n(.*?)^\s*ends\s*$',
                      structures, re.M | re.S)
    assert frame is not None
    fields = re.findall(r'^(\w+)\s+dw #0000\s*;', frame[1], re.M)
    assert fields == ['SavedBC', 'SavedAF', 'SavedDE', 'CallerReturn']
    for offset, field in enumerate(fields):
        assert f'assert FInteriorRowsFrame.{field} == #{offset * 2:02X}' in structures
    assert 'assert FInteriorRowsFrame == #08' in structures
    return dict(row_wrappers=[up, down], row_setup=setup, row_body_and_restore=body,
        saved_AF_at=0xD5A2, computation_F_dependency_killed_at=0xD5B0,
        first_row_conditional_at=0xD5B2, final_AF_restored_at=0xD606,
        final_flags_are_AND_Mode=True,
        nonoverlapping_stack_and_raster_required=True, valid_rows_0_to_95_required=True,
        stack_frame_disjoint_from_code_required=True,
        physical_frame=dict(name='FInteriorRowsFrame', bytes=8, base_relative_to_entry_SP=-6,
            fields=[dict(name=field, offset=offset * 2, bytes=2) for offset, field in enumerate(fields)]),
        row_pixels_and_control_independent_of_Mode_under_preconditions=True,
        left_setup_return_sequence=left, left_setup_A_independent_but_F_dependent=True,
        whole_circle_independence_proved=False)


def memory_read_domains(code, source):
    """Полный перечень явных чтений в обозначенных диапазонах кода, отдельно от стека."""
    ranges = ((0xD18D, 0xD21A), (0xD236, 0xD95B), (0xCEA4, 0xCEF9))
    inside = lambda address: any(lo <= address < hi for lo, hi in ranges)
    rows = [row for pc, row in code.items() if inside(pc)]
    covered = set()
    fixed = []
    raster = []
    square = []
    for row in rows:
        pc, op = row['address'], row['operation']
        raw = bytes.fromhex(row['hex'])
        assert row['slot'] == 22 and source[row['offset']:row['offset'] + len(raw)] == raw
        covered.update(range(pc, pc + len(raw)))
        # У перечисленных блоковых команд есть неявные чтения HL, их нельзя потерять поиском скобок.
        assert op.split()[0] not in {'LDI', 'LDIR', 'LDD', 'LDDR', 'CPI', 'CPIR', 'CPD', 'CPDR',
                                    'RLD', 'RRD', 'INI', 'INIR', 'IND', 'INDR', 'OUTI', 'OTIR', 'OUTD', 'OTDR'}
        assert not op.startswith('RST ')
        target = re.fullmatch(r'(?:CALL|JP|JR) (?:(?:NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]{4})', op)
        if target:
            assert inside(int(target[1], 16)), (pc, op)
        if '(' not in op:
            continue
        absolute = re.fullmatch(r'LD (A|BC|DE|HL|SP),\(#([0-9A-F]{4})\)', op)
        if absolute:
            address = int(absolute[2], 16)
            width = 1 if absolute[1] == 'A' else 2
            addresses = list(range(address, address + width))
            if 0xD18C in addresses:
                assert op == 'LD A,(#D18C)'
            fixed.append(dict(pc=pc, address=address, bytes=width, operation=op))
        elif op in ('LD E,(HL)', 'LD D,(HL)'):
            square.append(pc)
        elif op in ('AND (HL)', 'OR (HL)'):
            raster.append(pc)
        else:
            # Другие инструкции со скобками обязаны быть чистыми писателями, не EX (SP),HL или ALU (HL).
            assert re.fullmatch(r'LD \((?:#[0-9A-F]{4}|HL)\),(?:A|BC|DE|HL|SP)', op), (pc, op)
            destination = re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|BC|DE|HL|SP)', op)
            if destination:
                start = int(destination[1], 16)
                size = 1 if destination[2] == 'A' else 2
                assert not start <= 0xD18C < start + size
    assert covered == {address for lo, hi in ranges for address in range(lo, hi)}
    assert square == [0xD30F, 0xD311] and len(raster) == 12
    checked_sequence(code, source, 0xD30B,
        ['PUSH HL', 'LD H,#C3', 'LD L,A', 'LD E,(HL)', 'INC H', 'LD D,(HL)', 'POP HL', 'RET'])
    checked_sequence(code, source, 0xCEA4,
        ['LD L,D', 'ADD A,A', 'JR Z,#CEF4', 'PUSH HL', 'ADD A,A', 'SUB #3E', 'NEG',
         'LD (#CEB4),A', 'LD A,IXL', 'JR #CEB3'])
    tail_targets = []
    for count in range(1, 16):
        target = 0xCEB5 + 62 - 4 * count
        assert code[target]['operation'] == 'DEC L' and code[target + 1]['operation'] == 'LD (HL),A'
        tail_targets.append(dict(input_A=count, target=target))
    return dict(physical_code_ranges=[dict(start=lo, end_exclusive=hi) for lo, hi in ranges],
        all_bytes_covered_by_original_instructions=True, instruction_count=len(rows),
        fixed_reads=fixed, indirect_square_reads=square, square_domains=[[0xC300, 0xC400], [0xC400, 0xC500]],
        fixed_Mode_read_sites=[row['pc'] for row in fixed if row['address'] == 0xD18C],
        no_fixed_address_write_overlaps_Mode=True,
        indirect_raster_reads=raster, raster_domain_required=[0x8000, 0x8C00],
        raster_domain_is_child_contract_precondition=True,
        FillEvenSpan_tail_targets=tail_targets,
        FillEvenSpan_zero_length_inputs=[0, 128], FillEvenSpan_zero_length_target=0xCEF4,
        stack_reads_require_separate_frame_analysis=True,
        code_fetch_and_runtime_modifications_not_a_global_reachability_proof=True,
        whole_raster_independence_proved=False)


def direct_flag_consumers(code, source):
    """Все зарегистрированные прямые передачи к трём производителям F и двум левым половинам."""
    expected = {
        0xD35C: 'CALL #D208', 0xD377: 'CALL #D211', 0xD3AE: 'CALL #D211', 0xD3C5: 'CALL #D208',
        0xD36A: 'CALL Z,#D1CB', 0xD385: 'CALL Z,#D1B6', 0xD3BC: 'CALL Z,#D1B6', 0xD3D3: 'CALL Z,#D1CB',
        0xD47E: 'CALL NZ,#D1B6', 0xD481: 'CALL Z,#D1CB',
        0xD3F8: 'CALL #D4E4', 0xD3FE: 'CALL #D4E4', 0xD3FB: 'CALL #D1B6', 0xD401: 'JP #D1CB',
    }
    targets = {0xD208, 0xD211, 0xD4E4, 0xD1B6, 0xD1CB}
    actual = {}
    for pc, row in code.items():
        match = re.fullmatch(r'(?:CALL|JP) (?:(?:NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]{4})', row['operation'])
        if match and int(match[1], 16) in targets:
            actual[pc] = row['operation']
    assert actual == expected
    for pc, op in expected.items():
        checked_sequence(code, source, pc, [op])
    # Ни одно из четырёх продолжений после заливки не проверяет полученные флаги.
    fill_calls = []
    for site, entry in ((0xD35C, 0xD208), (0xD377, 0xD211), (0xD3AE, 0xD211), (0xD3C5, 0xD208)):
        fill_calls.append(checked_sequence(code, source, site,
            [f'CALL #{entry:04X}', 'CALL #D56C', 'CALL #D57B']))
    load_state = checked_sequence(code, source, 0xD56C,
        ['LD BC,(#D181)', 'LD A,#88', 'SUB B', 'EXX', 'LD C,A', 'LD A,(#D185)', 'LD E,A', 'EXX', 'RET'])
    mask_state = checked_sequence(code, source, 0xD57B,
        ['LD A,(#D18C)', 'AND A', 'LD A,L', 'AND #E0', 'OR #01', 'LD E,A', 'LD C,#FF', 'LD B,#00', 'RET'])
    # В этих парах исходный F получен из геометрического Flags, а не из возвращённого AND Mode.
    half_calls = []
    for site, left, right in ((0xD365, 0xD1CB, 0xD1A2), (0xD380, 0xD1B6, 0xD18D),
                              (0xD3B7, 0xD1B6, 0xD18D), (0xD3CE, 0xD1CB, 0xD1A2)):
        half_calls.append(checked_sequence(code, source, site,
            ['LD A,(#D17F)', 'BIT 0,A', f'CALL Z,#{left:04X}', f'CALL NZ,#{right:04X}']))
    corner = checked_sequence(code, source, 0xD473,
        ['LD A,(#D18C)', 'AND A', 'LD B,#00', 'LD A,(#D17F)', 'BIT 1,A',
         'CALL NZ,#D1B6', 'CALL Z,#D1CB', 'RET'])
    # Единственная прямая цепочка с Mode-зависимым входным SavedAF не имеет условий между вызовами.
    left_path = checked_sequence(code, source, 0xD3F8,
        ['CALL #D4E4', 'CALL #D1B6', 'CALL #D4E4', 'JP #D1CB'])
    return dict(registered_direct_transfers_checked=len(expected),
        transfer_sites=[dict(pc=pc, operation=op) for pc, op in sorted(expected.items())],
        four_fill_continuations=fill_calls, load_state_sequence=load_state,
        load_state_replaces_all_F_at=0xD572, mask_state_sequence=mask_state,
        four_geometry_bit0_pairs=half_calls, geometry_bit1_pair=corner,
        left_Mode_AF_chain=left_path,
        clipped_halves_restore_saved_input_AF_required=True,
        other_inputs_independent_of_Mode_and_valid_child_contracts_required=True,
        all_registered_direct_transfers_to_selected_targets_classified=True,
        indirect_transfers_and_external_return_consumers_excluded=False,
        global_Mode_unusedness_proved=False)


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    prior = json.loads((reports / 'CircleModeConsumers.json').read_bytes())
    source = payload(22)
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(row for row in manifest['entries'] if row['slot'] == 22)
    assert sha256(disk).hexdigest() == manifest['sha256']
    assert source == disk[entry['offset']:entry['offset'] + entry['length']]
    assert prior['source_control0_sha256'] == sha256(source).hexdigest()
    flow = json.loads((reports / 'ControlFlow.json').read_bytes())
    code = {row['address']: row for region in flow if region['name'] == 'Controls'
            for row in region['instructions']}
    reads = {pc for pc, row in code.items() if row['operation'] == 'LD A,(#D18C)'}
    assert reads == {row['read'] for row in prior['direct_reads']}
    profiles = []
    for row in prior['direct_reads']:
        if row['category'] != 'dependency_replaced_in_known_path':
            continue
        pc = row['read']
        # Остальные входные регистры и D17F независимы от меняемого Mode.
        a_dependent = False
        flag_dependencies = 0
        carry_known_zero = False
        c_known_zero = False
        trace = []
        for _ in range(8):
            instruction = code[pc]
            op = instruction['operation']
            raw = bytes.fromhex(instruction['hex'])
            jump = re.fullmatch(r'JP #([0-9A-F]{4})', op)
            expected = (b'\xC3' + int(jump[1], 16).to_bytes(2, 'little')) if jump else bytes.fromhex(ENCODINGS[op])
            # Проверка самого кодирования, а не только текстового имени операции в старом отчёте.
            assert instruction['slot'] == 22 and raw == expected
            assert source[instruction['offset']:instruction['offset'] + len(raw)] == raw
            if op == 'LD A,(#D18C)':
                assert pc == row['read']
                a_dependent = True
            elif op == 'AND A':
                # S/Z/PV/X/Y зависят от Mode, H=1, N=0, C=0 от его значения не зависят.
                flag_dependencies = 0xEC if a_dependent else 0
                carry_known_zero = True
            elif op.startswith('LD A,'):
                a_dependent = False
            elif op in ('LD B,#00', 'LD B,#FF', 'LD C,#00'):
                if op == 'LD C,#00':
                    c_known_zero = True
            elif jump:
                pass
            elif op in ('AND #1F', 'AND #E0', 'OR #1F', 'SUB L'):
                assert not a_dependent
                flag_dependencies = 0
                carry_known_zero = op != 'SUB L'
            elif op in ('BIT 1,A', 'INC A'):
                assert not a_dependent and carry_known_zero
                # BIT и INC сохраняют Carry, но он уже равен нулю после AND A.
                flag_dependencies &= 1
            elif op == 'SLL C':
                assert c_known_zero
                flag_dependencies = 0
                carry_known_zero = True  # C непосредственно перед этим обнулён.
            else:
                raise AssertionError(('неподдержанная операция', pc, op))
            trace.append(dict(address=pc, operation=op, A_depends_on_Mode=a_dependent,
                              F_dependency_mask=flag_dependencies))
            if pc == row['flags_normalized_at']:
                assert not a_dependent and flag_dependencies == 0
                break
            pc = int(jump[1], 16) if jump else pc + len(raw)
        else:
            raise AssertionError(('нормализатор не достигнут', row))
        profiles.append(dict(read=row['read'], normalized_at=pc, instructions=trace))
    assert len(profiles) == 12
    escaped = [row['read'] for row in prior['direct_reads']
               if row['category'] != 'dependency_replaced_in_known_path']
    assert sorted(escaped) == [0xD209, 0xD212, 0xD4F9]
    result = dict(passed=True, method='restricted_symbolic_fresh_A_and_F_dependency_check',
        original_disk_sha256=manifest['sha256'],
        source_control0_sha256=sha256(source).hexdigest(), prefixes_checked=len(profiles),
        profiles=profiles, other_registered_reads=escaped,
        returned_or_saved_flag_routes=returned_mode_flags(code, source),
        explicit_memory_read_domains=memory_read_domains(code, source),
        direct_flag_consumer_routes=direct_flag_consumers(code, source),
        no_conditional_branch_or_memory_write_before_dependency_kill=True,
        all_prefix_opcodes_checked_against_original=True,
        independent_other_inputs_required=True, irq_interference_excluded_by_precondition=True,
        prior_saved_AF_dependency_excluded=False, indirect_Mode_reads_excluded=False,
        whole_raster_independence_proved=False, original_graphics_intent_proved=False,
        assembly_executed=False, native_execution=False)
    (reports / 'CircleModePrefixDataflowVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены 12 нормализующих префиксов, три маршрута сохранения F, '
          '1269 инструкций областей чтения и 14 прямых передач вызывающих процедур.')


if __name__ == '__main__':
    main()
