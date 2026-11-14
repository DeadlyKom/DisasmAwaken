"""Длины условного переноса из #C600 и слова, оставленные буфером TR-DOS."""
from hashlib import sha256
import json

from CheckTemporaryModuleLiveSource import (
    B, COPY_LOOP, D, H, PC, ROOT, Simulator, SliceableMemory, payload, put,
    restore_cpu, run_to, trace, word,
)
from CheckStationFlightCycle import DISK
from skoolkit.simutils import F, IXh, SP


SOURCE, STAGING, DESTINATION = 0xC600, 0x8000, 0x6400
UNPACK = 0xAB23
MOVE_PACKED, COPY_MATCH = 0xAB3C, 0xABC0
SOURCE_LIMIT = 0x10000 - SOURCE
FIRST_OVERWRITE = UNPACK - STAGING + 1
COMPLETE_BAD_PREFIX = 20
THIRD_COPY_LOOP = 0x5DDD
FIRST_SELF_WRITE = ((COPY_LOOP - STAGING) & 0xFFFF) + 1
THIRD_SELF_WRITE = ((THIRD_COPY_LOOP - DESTINATION) & 0xFFFF) + 1
THIRD_UNPACK_WRITE = UNPACK - DESTINATION + 1


def sector_buffer_lengths():
    report = json.loads((ROOT / 'Tools/Disasm/Reports/BootBankFileReadsVerification.json').read_bytes())
    assert report['passed'] and report['disk_sha256'] == sha256(DISK).hexdigest()
    sources = []
    for stage, expected in (('hyper_load', 0xC4BC), ('hyper_initialization', 0x5103)):
        sectors = set()
        for profile in report['intro_transitions']:
            result = profile['flight_transition']['legacy_workspace'][stage]
            track, sector = result['fixed_buffer_sector_reads'][-1]
            offset = (track * 16 + sector - 1) * 256 + 0x5DC3 - 0x5D25
            assert result['fixed_operand_addresses'][:2] == [0x5DC3, 0x5DC4]
            assert all(result['last_fixed_operand_writers'][str(address)] == 0x3FEC
                       for address in (0x5DC3, 0x5DC4))
            length = int.from_bytes(DISK[offset:offset + 2], 'little')
            assert length == int.from_bytes(bytes.fromhex(result['fixed_operands_after'][:4]), 'little')
            assert length == expected
            sectors.add((track, sector))
        assert len(report['intro_transitions']) == 2 and len(sectors) == 1
        sources.append(dict(stage=stage, length=expected, sector=list(sectors.pop())))
    return sources


def check_wrapped_copy(cpu, start, source, target, length):
    memory, registers = cpu.memory, cpu.registers
    run_to(cpu, start)
    assert (word(registers, H), word(registers, D), word(registers, B)) == (source, target, length)
    assert memory.o7ffd == 0x11 and bytes(memory[start:start + 2]) == b'\xED\xB0'
    expected = bytearray(memory[0:0x10000])
    rom_reads = ignored_rom_writes = 0
    for index in range(length):
        read_address, write_address = (source + index) & 0xFFFF, (target + index) & 0xFFFF
        rom_reads += read_address < 0x4000
        if write_address >= 0x4000:
            expected[write_address] = expected[read_address]
        else:
            ignored_rom_writes += 1
    run_to(cpu, start + 2)
    assert bytes(memory[0:0x10000]) == expected
    next_source, next_target = (source + length) & 0xFFFF, (target + length) & 0xFFFF
    assert (word(registers, H), word(registers, D), word(registers, B)) == (next_source, next_target, 0)
    return dict(pc=start, source_after=next_source, target_after=next_target,
                reads_from_rom=rom_reads, writes_ignored_in_rom=ignored_rom_writes)


def check_sector_buffer_length(memory, banks, registers, length):
    cpu, ports = restore_cpu(memory, banks, registers, length)
    first = check_wrapped_copy(cpu, COPY_LOOP, SOURCE, STAGING, length)
    assert memory[UNPACK] == 0xC0
    backup = check_wrapped_copy(cpu, 0x5DD5, 0x6000, 0xE000, 0x2000)
    third = check_wrapped_copy(cpu, 0x5DDD, STAGING, DESTINATION, length)
    overwritten = bytes.fromhex('77 21 89 5C BE 38 03 34 06 18 CD 00 0E')
    assert bytes(memory[UNPACK:UNPACK + len(overwritten)]) == overwritten
    run_to(cpu, UNPACK)
    assert cpu.registers[SP] == 0x5FEC
    run_to(cpu, 0x0E00)
    assert cpu.registers[SP] == 0x5FEA and bytes(memory[0x5FEA:0x5FEE]) == b'\x30\xAB\xE5\x5D'

    rom_calls = []
    for step in range(800000):
        pc = cpu.registers[PC]
        assert pc not in (0x0008, 0x5DE5, 0x5DE8, 0x6500)
        if pc == 0x0E00:
            rom_calls.append(step)
        if pc == 0xAB4C and bytes(memory[cpu.registers[SP]:cpu.registers[SP] + 2]) == b'\0\0':
            assert memory[pc] == 0xC9 and cpu.registers[SP] == 0x5FF4
            cpu.run()
            assert (cpu.registers[PC], cpu.registers[SP]) == (0, 0x5FF6)
            break
        cpu.run()
    else:
        raise AssertionError('Подменённый распаковщик не дошёл до возврата в #0000')
    assert rom_calls == list(range(0, 93 * 8115, 8115)) and step == 754706
    assert ports.writes == [(0x7FFD, 0x16), (0x7FFD, 0x11)]
    return dict(length=length, transfers=[first, backup, third], unpack_entry_hex=overwritten.hex(),
                rom_subroutine=0x0E00, rom_calls=len(rom_calls), rom_call_interval_steps=8115,
                return_pc=0xAB4C, return_target=0, sp_after_return=0x5FF6,
                reached_temporary_entry=False)


def check_staged_copy(memory, banks, registers, source, length):
    cpu, ports = restore_cpu(memory, banks, registers, length)
    run_to(cpu, COPY_LOOP)
    r = cpu.registers
    assert (word(r, H), word(r, D), word(r, B)) == (SOURCE, STAGING, length)
    run_to(cpu, COPY_LOOP + 2)
    assert bytes(memory[STAGING:STAGING + length]) == source[:length]
    run_to(cpu, UNPACK)
    assert bytes(memory[DESTINATION:DESTINATION + length]) == source[:length]
    assert (word(r, H), word(r, D)) == (DESTINATION, DESTINATION)
    assert ports.writes == [(0x7FFD, 0x16), (0x7FFD, 0x11)]
    return cpu


def check_first_invalid_match(cpu, length):
    r = cpu.registers
    run_to(cpu, MOVE_PACKED)
    assert (word(r, H), word(r, D), word(r, B)) == (0x67FF, 0x6803, 0x03FF)
    first_invalid = None
    for _ in range(8):
        run_to(cpu, COPY_MATCH)
        match = word(r, H), word(r, D), word(r, B), word(r, IXh)
        if match[0] < DESTINATION:
            first_invalid = match
            break
        assert match[0] < match[1] and match[2] == 1
        cpu.run()

    if length < 14:
        expected = (0x63C3, 0x6403, 2, 0x6416)
    elif length < COMPLETE_BAD_PREFIX:
        expected = (0x62D7, 0x6406, 2, 0x6418)
    else:
        expected = (0x624F, 0x6406, 2, 0x6418)
    assert first_invalid == expected, (length, first_invalid)
    # После переноса на +4 поток прочитан только до байта перед IX.
    return dict(source=expected[0], destination=expected[1], count=expected[2],
                packed_bytes_through_last_read=expected[3] - (DESTINATION + 4))


def check_copy_boundary(cpu, pc, source, target, requested, limit, replacement):
    memory, registers = cpu.memory, cpu.registers
    assert registers[PC] == pc and memory[pc:pc + 2] == [0xED, 0xB0]
    assert (word(registers, H), word(registers, D), word(registers, B)) == (source, target, requested & 0xFFFF)
    copied = min(requested, limit)
    for _ in range(copied):
        assert registers[PC] == pc and memory[pc] == 0xED
        cpu.run()
    remaining = requested - copied
    assert (word(registers, H), word(registers, D), word(registers, B)) == (
        (source + copied) & 0xFFFF, (target + copied) & 0xFFFF, remaining)
    assert registers[PC] == (pc if remaining else pc + 2)
    assert memory[pc:pc + 2] == [replacement if copied == limit else 0xED, 0xB0]
    return dict(copied=copied, remaining=remaining, next_pc=registers[PC], opcode_at_copy_site=memory[pc])


def check_full_length_boundaries(memory, banks, registers):
    lengths = (SOURCE_LIMIT + 1, THIRD_UNPACK_WRITE - 1, THIRD_UNPACK_WRITE, THIRD_UNPACK_WRITE + 1,
               0x8000, 0x9C00, 0xC000, 0xDC00, FIRST_SELF_WRITE - 1, FIRST_SELF_WRITE, FIRST_SELF_WRITE + 1,
               THIRD_SELF_WRITE - 1, THIRD_SELF_WRITE, THIRD_SELF_WRITE + 1, 0xFFFF, 0)
    assert (FIRST_SELF_WRITE, THIRD_SELF_WRITE, THIRD_UNPACK_WRITE) == (0xDDCB, 0xF9DE, 0x4724)
    cases = []
    for length in lengths:
        cpu, ports = restore_cpu(memory, banks, registers, length)
        run_to(cpu, COPY_LOOP)
        # Значения в трёх точках определяют перезапись обоих LDIR и входа распаковщика.
        assert memory[0xE9CA] == 0x3E and memory[0xDBDD] == 0xDD and memory[0x0D23] == 0x77
        requested = length or 65536
        first = check_copy_boundary(cpu, COPY_LOOP, SOURCE, STAGING, requested, FIRST_SELF_WRITE, 0x3E)
        assert memory[UNPACK] == 0xC0
        run_to(cpu, THIRD_COPY_LOOP)
        third = check_copy_boundary(cpu, THIRD_COPY_LOOP, STAGING, DESTINATION, requested, THIRD_SELF_WRITE, 0xDD)
        run_to(cpu, UNPACK)
        opcode = 0x77 if requested >= THIRD_UNPACK_WRITE else 0xC0
        assert memory[UNPACK] == opcode and ports.writes == [(0x7FFD, 0x16), (0x7FFD, 0x11)]
        assert cpu.registers[SP] == 0x5FEC
        cases.append(dict(length_word=length, requested_bytes=requested, first=first, third=third,
                          unpack_entry_opcode=opcode))
    return cases


def check_mixed_prefix_returns(memory, banks, registers):
    cases = []
    for length, stop, expected_steps in ((0x2B35, 0x0038, 28328), (0x472F, 0x0020, 275)):
        cpu, ports = restore_cpu(memory, banks, registers, length)
        run_to(cpu, UNPACK)
        registers_at_call = cpu.registers
        if length == 0x2B35:
            assert bytes(memory[0xAB23:0xAB35]) == bytes(banks[1][0x3123:0x3135])
            assert bytes(memory[0xAB34:0xAB36]) == b'\x30\xED'
        else:
            assert bytes(memory[0xAB23:0xAB2F]) == bytes(memory[0x0D23:0x0D2F])
            assert bytes(memory[0xAB2D:0xAB30]) == b'\xCD\x00\xC8'
            assert memory[0x803E] == banks[1][0x223E] == 0xC0

        observed = []
        sites = {0xAB23, 0xAB2D, 0xAB34, 0x803E, 0xC800, 0x5DE5, 0x5DE8, 0x6500,
                 0x652B, 0x5DEB, 0x6000, 0xEC56, 0xAEB0, 0x0038, 0x0020}
        reached_stop = False
        for step in range(expected_steps + 1):
            pc, sp = registers_at_call[PC], registers_at_call[SP]
            if pc in sites:
                observed.append(dict(step=step, pc=pc, sp=sp, page=memory.o7ffd,
                                     opcode=memory[pc], stack_word=bytes(memory[sp:sp + 2]).hex()))
            if pc == 0x6500:
                assert sp == 0x5FFE and memory[sp:sp + 2] == [0xEB, 0x5D]
                assert bytes(memory[0x6500:0x6530]) == bytes(banks[1][0x700:0x730])
            if pc == 0x6000:
                assert bytes(memory[0x6000:0x8000]) == bytes(banks[5][0x2000:0x4000])
            if pc == stop and (length == 0x472F or sp == 0x1814):
                assert step == expected_steps
                reached_stop = True
                break
            cpu.run()
        assert reached_stop

        if length == 0x2B35:
            assert [(row['step'], row['pc']) for row in observed if row['pc'] in
                    (0xAB23, 0xAB34, 0x5DE5, 0x6500, 0x652B, 0x5DEB, 0x6000, 0xEC56, 0x0038)] == [
                        (0, 0xAB23), (11, 0xAB34), (12, 0xAB23), (13, 0x5DE5),
                        (15, 0x6500), (51, 0x652B), (52, 0x5DEB), (28187, 0x6000),
                        (28197, 0xEC56), (28219, 0x0038), (28328, 0x0038)]
        else:
            assert [(row['step'], row['pc']) for row in observed if row['pc'] in
                    (0xAB2D, 0xC800, 0x0038, 0x803E, 0x5DE5, 0x6500, 0xAEB0, 0x0020)] == [
                        (6, 0xAB2D), (7, 0xC800), (25, 0x0038), (210, 0x803E),
                        (211, 0x5DE5), (213, 0x6500), (274, 0xAEB0), (275, 0x0020)]
            assert registers_at_call[SP] == 0x5FFC and memory[0x5FFC:0x6000] == [0xB1, 0xAE, 0xEB, 0x5D]
        cases.append(dict(length_word=length, partial_unpacker_returned=True,
                          bytes_at_temporary_entry_from_original_font=48, reached_stop=stop,
                          stack_at_stop=registers_at_call[SP], observed=observed, ports=ports.writes))
    return cases


def check_snapshot(frames, sector_lengths):
    memory = SliceableMemory(out7ffd=0x10)
    put(memory, 0x6000, payload(17))
    cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A})
    state = trace(['--frames', str(frames)], boot_simulator=cpu, save_reports=False)
    assert state['reason'] == 'requested_frame_entries'
    banks, registers = [bank.copy() for bank in memory.banks], cpu.registers[:]
    source = bytes(banks[1][SOURCE - 0xC000:])
    assert len(source) == SOURCE_LIMIT
    assert source[:6] == bytes.fromhex('04 04 04 04 00 04')
    assert source[FIRST_OVERWRITE - 1] == 0xC0
    assert DESTINATION + SOURCE_LIMIT == 0x9E00 < UNPACK
    # Стадия по #8000 и источник в выбранном банке не пересекаются.
    assert STAGING + SOURCE_LIMIT == 0xBA00 < SOURCE

    cases = []
    representatives = (*range(1, COMPLETE_BAD_PREFIX + 1), 0x400, 0x1C00, 0x1C01,
                       FIRST_OVERWRITE - 1, FIRST_OVERWRITE, SOURCE_LIMIT)
    for length in representatives:
        cpu = check_staged_copy(memory, banks, registers, source, length)
        first_opcode = memory[UNPACK]
        if length >= FIRST_OVERWRITE:
            assert first_opcode == 0xC0
            r = cpu.registers
            entry_sp = r[SP]
            takes_return = not (r[F] & 0x40)
            cpu.run()
            assert (r[PC], r[SP]) == ((0x5DE5, entry_sp + 2) if takes_return else (UNPACK + 1, entry_sp))
            result = dict(overwritten_unpack_entry=True, opcode=first_opcode, next_pc=r[PC])
        else:
            assert first_opcode == 0xD5
            packed = int.from_bytes(memory[DESTINATION + 4:DESTINATION + 6], 'little')
            if length < 6:
                assert packed == (0xC69B if length < 5 else 0xC600)
                run_to(cpu, MOVE_PACKED)
                assert word(cpu.registers, B) == packed - 1
                result = dict(packed_size=packed, reverse_copy_length=packed - 1)
            else:
                assert packed == 0x400
                result = dict(packed_size=packed, invalid_match=check_first_invalid_match(cpu, length))
        cases.append(dict(length=length, **result))

    complete = cases[COMPLETE_BAD_PREFIX - 1]['invalid_match']
    assert complete['packed_bytes_through_last_read'] == COMPLETE_BAD_PREFIX
    sector_cases = [check_sector_buffer_length(memory, banks, registers, entry['length'])
                    for entry in sector_lengths]
    full_length_cases = check_full_length_boundaries(memory, banks, registers)
    mixed_prefix_cases = check_mixed_prefix_returns(memory, banks, registers)
    return dict(frame_entries=frames, cases=cases, sector_cases=sector_cases,
                full_length_cases=full_length_cases, mixed_prefix_cases=mixed_prefix_cases)


def main():
    sector_lengths = sector_buffer_lengths()
    snapshots = [check_snapshot(frames, sector_lengths) for frames in (2, 9, 65)]
    cases = snapshots[0]['cases']
    sector_cases = snapshots[0]['sector_cases']
    full_length_cases = snapshots[0]['full_length_cases']
    mixed_prefix_cases = snapshots[0]['mixed_prefix_cases']
    assert all(snapshot['cases'] == cases and snapshot['sector_cases'] == sector_cases
               and snapshot['full_length_cases'] == full_length_cases
               and snapshot['mixed_prefix_cases'] == mixed_prefix_cases for snapshot in snapshots)
    report = dict(passed=True, frame_entries=[snapshot['frame_entries'] for snapshot in snapshots],
                  identical_cases_in_all_snapshots=cases, source_bank=1,
                  lengths_with_header_outside_staged_block=[1, 5],
                  lengths_with_invalid_history=[6, FIRST_OVERWRITE - 1],
                  lengths_with_overwritten_entry=[FIRST_OVERWRITE, SOURCE_LIMIT],
                  first_complete_invalid_prefix_bytes=COMPLETE_BAD_PREFIX,
                  observed_buffer_words=sector_lengths, conditional_buffer_word_cases=sector_cases,
                  full_length_boundary_cases=full_length_cases,
                  mixed_prefix_return_cases=mixed_prefix_cases,
                  unpack_opcode_by_effective_length=[
                      dict(first=1, last=FIRST_OVERWRITE - 1, opcode=0xD5),
                      dict(first=FIRST_OVERWRITE, last=THIRD_UNPACK_WRITE - 1, opcode=0xC0),
                      dict(first=THIRD_UNPACK_WRITE, last=65536, opcode=0x77)],
                  conditional_copy_base=0x5DA0, original_caller_proved=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/TemporaryModuleLiveLengthsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены границы длин источника C600 в трёх исходных снимках ACTION.')


if __name__ == '__main__':
    main()
