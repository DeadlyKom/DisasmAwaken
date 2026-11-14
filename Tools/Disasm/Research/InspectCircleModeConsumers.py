"""Статический разбор прямых чтений D18C, отдельно от Direction по D18B."""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckStationFlightCycle import ROOT, payload


def returned_flag_paths(code, original):
    """Проверка продолжений трёх чтений, не теряющих флаги внутри помощника."""
    def sequence(start, operations):
        address = start
        for operation in operations:
            row = code[address]
            assert row['slot'] == 22 and row['operation'] == operation
            raw = bytes.fromhex(row['hex'])
            assert original[row['offset']:row['offset'] + len(raw)] == raw
            address += len(raw)
        return address

    # После каждой полноширинной заливки вызывается один и тот же загрузчик.
    fills = [(0xD35C, 0xD208), (0xD377, 0xD211),
             (0xD3AE, 0xD211), (0xD3C5, 0xD208)]
    for site, target in fills:
        sequence(site, [f'CALL #{target:04X}', 'CALL #D56C'])
    # LD сохраняет флаги, но SUB B заменяет их до любого выбора ветви.
    sequence(0xD56C, ['LD BC,(#D181)', 'LD A,#88', 'SUB B', 'EXX',
                       'LD C,A', 'LD A,(#D185)', 'LD E,A', 'EXX', 'RET'])
    sequence(0xD605, ['POP BC', 'POP AF', 'POP DE', 'RET'])

    # Два вызова левого подготовителя передают его AF в рамку половины.
    sequence(0xD3F8, ['CALL #D4E4', 'CALL #D1B6', 'CALL #D4E4', 'JP #D1CB'])
    sequence(0xD4F9, ['LD A,(#D18C)', 'AND A', 'LD A,B', 'LD B,#00', 'RET'])
    for start, direction, read in ((0xD1B6, ['LD A,#01'], 0xD1C4),
                                   (0xD1CB, ['XOR A'], 0xD1D8)):
        sequence(start, ['PUSH AF', 'EXX', 'LD HL,#0000', 'LD D,H',
                         'LD B,#FF', 'EXX'] + direction +
                        ['LD (#D18B),A', 'LD A,(#D18C)', 'AND A', 'JP #D73B'])
        assert read in code
    sequence(0xD73B, ['LD A,L', 'AND #1F', 'CP #20'])
    return dict(
        method='contiguous_instruction_sequences_checked_against_original_CONTROL0',
        full_width_calls=[dict(call=site, target=target, following_call=site + 3)
                          for site, target in fills],
        full_width_flags_replaced_at=0xD572,
        full_width_return_frame_restore=0xD605,
        left_setup_call_sites=[0xD3F8, 0xD3FE],
        left_half_saved_af_sites=[0xD1B6, 0xD1CB],
        left_half_internal_flags_replaced_at=0xD73C,
        left_half_saved_flags_remain_part_of_return_contract=True,
        callers_beyond_circle_dispatch_proved=False,
        whole_raster_mode_independence_proved=False)


def archived_provenance(instructions, current):
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        disk = archive.read('awk1.trd')
        _, old, _ = read_entry(disk, b'CONTROL0C')
        _, effect, _ = read_entry(disk, b'EFF     c')
        _, source, _ = read_entry(disk, b'STARHSUNa')
    assert len(effect) == 0x535 and old[0x600:0xB35] == effect
    assert source.count(b'SEDETECT\x06\x84\x05g\x06\x830\r') == 1
    assert source.count(b'\x03~,(SEDETECT)') == 15
    assert source.count(b'(SEDETECT),\x05~') == 2
    start, end, delta = 0xD18D, 0xD9DE, 0x535
    candidate = bytearray(old[start - 0xC000 + delta:end - 0xC000 + delta])
    expected = current[start - 0xC000:end - 0xC000]
    equal = shifted = instruction_bytes = 0
    for row in instructions:
        if row['slot'] != 22 or not start <= row['address'] < end:
            continue
        offset = row['address'] - start
        raw = bytes.fromhex(row['hex'])
        prior = bytes(candidate[offset:offset + len(raw)])
        instruction_bytes += len(raw)
        if prior == raw:
            equal += 1
        else:
            # Разрешена только разность последнего 16-битного операнда, опкод и остальные байты неизменны.
            assert len(raw) >= 3 and prior[:-2] == raw[:-2]
            assert int.from_bytes(prior[-2:], 'little') == int.from_bytes(raw[-2:], 'little') + delta
            candidate[offset + len(raw) - 2:offset + len(raw)] = raw[-2:]
            shifted += 1
    assert (equal, shifted, instruction_bytes) == (1025, 222, 2075)
    # Проверка всего блока включает и 54 байта вне декодированных инструкций.
    assert len(candidate) == 2129 and candidate == expected
    assert old[0xD6C1 - 0xC000] == current[0xD18C - 0xC000] == 0
    return dict(archive_sha256=digest, source='awk1.trd:STARHSUN.a',
        compiled='awk1.trd:CONTROL0.C', archived_identifier='SEDETECT',
        archived_mode_address=0xD6C1, current_mode_address=0xD18C,
        archived_code_start=start + delta, current_code_start=start,
        code_bytes=2129, decoded_instruction_bytes=2075, other_compared_bytes=54,
        identical_instructions=equal, changed_terminal_word_operands=shifted,
        operand_delta=delta, delta_equals_removed_effect_bytes=True,
        normalized_block_sha256=sha256(candidate).hexdigest(),
        archived_named_reads=15, archived_named_writes=2,
        identifier_expansion_or_graphical_intent_proved=False)


def known_action_return_paths(flow):
    """Проверка двух зарегистрированных продолжений после банкового рисования."""
    instructions = next(region['instructions'] for region in flow if region['name'] == 'Action')
    code = {row['address']: row for row in instructions}
    original = payload(17)

    def sequence(start, operations):
        address = start
        for operation in operations:
            row = code[address]
            assert row['slot'] == 17 and row['operation'] == operation
            raw = bytes.fromhex(row['hex'])
            assert original[row['offset']:row['offset'] + len(raw)] == raw
            address += len(raw)

    # Восстановление BC/IY/DE не трогает F, DEC C заменяет всё кроме Carry.
    sequence(0x6B48, ['CALL #6C7E', 'POP BC', 'POP IY', 'POP DE',
                       'DEC C', 'JR NZ,#6B64'])
    # Следующий обход начинается с OR, до него нет проверки входных флагов.
    sequence(0xE0C5, ['CALL NZ,#6A6E', 'CALL #6B16'])
    sequence(0x6B16, ['LD A,#80', 'LD (#9B87),A', 'LD (#9B88),A',
                       'LD (#9B89),A', 'LD A,(#688B)', 'OR A', 'RET Z'])
    return dict(
        method='known_current_ACTION_continuations_checked_against_original_bytes',
        banked_body_return=0x6B4B, flags_replaced_except_carry_at=0x6B4F,
        mode_AND_carry_is_zero_for_all_256_values=True,
        transformed_body_return=0xE0C8, following_entry=0x6B16,
        all_incoming_flags_replaced_at=0x6B24,
        arbitrary_indirect_callers_excluded=False,
        primary_mask_real_caller_proved=False)


def main():
    flow = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    instructions = next(region['instructions'] for region in flow if region['name'] == 'Controls')
    code = {row['address']: row for row in instructions}
    original = payload(22)
    reads = [row['address'] for row in instructions if row['operation'] == 'LD A,(#D18C)']
    writes = [row['address'] for row in instructions if row['operation'] == 'LD (#D18C),A']
    expected_reads = [0xD19B, 0xD1AF, 0xD1C4, 0xD1D8, 0xD1ED, 0xD201, 0xD209,
                      0xD212, 0xD43D, 0xD473, 0xD4D9, 0xD4F9, 0xD52A, 0xD55B, 0xD57B]
    assert reads == expected_reads and writes == [0xD221, 0xD22F]
    # Привязка всех найденных команд к физическим байтам исходного CONTROL0.
    for address in reads + writes:
        row = code[address]
        assert row['slot'] == 22
        raw = bytes.fromhex(row['hex'])
        assert original[row['offset']:row['offset'] + len(raw)] == raw
    assert code[0xD220]['operation'] == 'XOR A'
    assert code[0xD22D]['operation'] == 'LD A,#01'
    # Ручные точки замены зависимости сверяются с исходными командами графа.
    normalized = {
        0xD19B: (0xD833, 'LD A,E', 0xD834, 'AND #1F'),
        0xD1AF: (0xD833, 'LD A,E', 0xD834, 'AND #1F'),
        0xD1C4: (0xD73B, 'LD A,L', 0xD73C, 'AND #1F'),
        0xD1D8: (0xD73B, 'LD A,L', 0xD73C, 'AND #1F'),
        0xD1ED: (0xD633, 'LD A,E', 0xD634, 'SUB L'),
        0xD201: (0xD633, 'LD A,E', 0xD634, 'SUB L'),
        0xD43D: (0xD441, 'LD A,E', 0xD442, 'AND #1F'),
        0xD473: (0xD479, 'LD A,(#D17F)', 0xD47C, 'BIT 1,A'),
        0xD4D9: (0xD4DD, 'LD A,E', 0xD4DE, 'OR #1F'),
        0xD52A: (0xD52E, 'LD A,B', 0xD531, 'INC A'),
        0xD55B: (0xD55F, 'LD A,C', 0xD562, 'SLL C'),
        0xD57B: (0xD57F, 'LD A,L', 0xD580, 'AND #E0'),
    }
    rows = []
    for address, (a_site, a_op, f_site, f_op) in normalized.items():
        assert code[a_site]['operation'] == a_op and code[f_site]['operation'] == f_op
        rows.append(dict(read=address, category='dependency_replaced_in_known_path',
                         a_replaced_at=a_site, flags_normalized_at=f_site,
                         flags_operation=f_op,
                         note='INC сохраняет Carry, но AND A перед ним уже делает Carry=0' if address == 0xD52A else ''))
    assert [code[a]['operation'] for a in (0xD4FC, 0xD4FD, 0xD4FE, 0xD500)] == [
        'AND A', 'LD A,B', 'LD B,#00', 'RET']
    rows.append(dict(read=0xD4F9, category='logical_flags_returned', return_at=0xD500))
    for address, branch in ((0xD209, 0xD58A), (0xD212, 0xD595)):
        assert code[address + 3]['operation'] == 'AND A'
        assert code[address + 4]['operation'] == 'LD A,C'
        assert code[address + 5]['operation'] == f'JP #{branch:04X}'
        assert code[0xD5A2]['operation'] == 'PUSH AF'
        rows.append(dict(read=address, category='logical_flags_saved_in_row_frame',
                         row_entry=branch, save_af_at=0xD5A2))
    assert len(rows) == 15
    report = dict(passed=True, method='static_instruction_and_manual_dependency_classification',
        source_control0_sha256=sha256(original).hexdigest(), mode_address=0xD18C,
        separate_direction_address=0xD18B, direct_reads=sorted(rows, key=lambda row: row['read']),
        direct_writers=[dict(address=0xD221, value=0), dict(address=0xD22F, value=1)],
        archived_provenance=archived_provenance(instructions, original),
        returned_flag_paths=returned_flag_paths(code, original),
        known_action_return_paths=known_action_return_paths(flow),
        full_interprocedural_dataflow_proved=False, indirect_accesses_excluded=False,
        unusedness_proved=False, original_graphics_intent_proved=False,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/CircleModeConsumers.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены 15 прямых чтений и два писателя D18C, три пути сохраняют зависимые флаги.')


if __name__ == '__main__':
    main()
