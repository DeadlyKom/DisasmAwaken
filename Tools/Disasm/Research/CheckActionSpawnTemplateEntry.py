"""Выбор исходного шаблона на 7859 с настоящим банковым вызовом DE9A.

Документация: ../../../Docs/ActionSpawnSchedule.md
Документация: ../../../Docs/ActionSpawnPhysicalRows.md
"""
import json
from collections import Counter
from hashlib import sha256
from itertools import product

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckControlsWordRandom import reference as random_step
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from CheckActionSpawnTemplateLoop import word
from skoolkit.simutils import IXh, IXl


def finish_template(memory, sim, pointer, coordinates, allocation, counts):
    """Продолжение выбранного оригинального шаблона, независимые ожидаемые поля и пул."""
    pool = bytearray(memory[0xA100:0xA780])
    assert bytes(memory[pointer:pointer + 6]) == bytes(6)
    assert bytes(memory[pointer + 8:pointer + 10]) == bytes((255, 128))
    if allocation:
        slot = 0 if allocation == 1 else 1
        offset = slot * 64
        record = pool[offset:offset + 64]
        record[:6] = b''.join(value.to_bytes(2, 'little') for value in coordinates)
        record[6:14] = bytes((memory[pointer + 6], 0, memory[pointer + 7], 0, 9, 0, 0, 0))
        record[15:25] = bytes((0, 0, 0, 0x12, 255, 255, 255, 0, 0, 16))
        record[36] = 0
        pool[offset:offset + 64] = record
        if allocation == 2:
            pool[24] = 0
    # Исполнение без подстановки состояния CPU между выбором указателя и телом шаблона.
    for _ in range(1000):
        if sim.registers[PC] == 0x3FFF:
            break
        sim.run()
    else:
        raise AssertionError(('Шаблонный вход не вернулся', allocation))
    assert sim.registers[SP] == 0xC000
    assert bytes(memory[0xA100:0xA780]) == pool
    assert (memory[0x9B82], memory[0x9B83], memory[0x792E]) == (1, 1, 0 if allocation else 16)
    assert sim.registers[IXh] * 256 + sim.registers[IXl] == pointer + (8 if allocation else 0)
    assert sim.registers[0:2] == [128, 0x42]
    if allocation:
        assert sim.registers[6] * 256 + sim.registers[7] == coordinates[0]
        assert sim.registers[4] * 256 + sim.registers[5] == coordinates[1]
        assert sim.registers[2] * 256 + sim.registers[3] == coordinates[2]
    counts['no_slot' if allocation == 0 else 'created_first' if allocation == 1 else 'skipped_FF_created_second'] += 1


def main(finish_entry=False):
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[1][:] = bytes(base_memory()[0xC000:])
    if finish_entry:
        # Проверка физических файлов и перенесённого ядра до исполнения составного входа.
        manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
        disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
        assert sha256(disk).hexdigest() == manifest['sha256']
        sources = {}
        for slot in (17, 22, 23):
            entry = next(row for row in manifest['entries'] if row['slot'] == slot)
            raw = (ROOT / (entry['path'] + '.bin')).read_bytes()
            assert raw == disk[entry['offset']:entry['offset'] + len(raw)]
            sources[slot] = raw
        assert bytes(flat[0x6000:0x7F8F]) == sources[17][0x23D:0x21CC]
        assert bytes(flat[0x7F8F:0x10000]) == sources[17][0x1F8F:]
        expected_control = bytearray([0xA5] * 0x4000)
        expected_control[:len(sources[22])] = sources[22]
        expected_control[0x1ADE:0x1ADE + len(sources[23])] = sources[23]
        assert banks[1] == expected_control
    memory = RecordedBanks(banks=banks, out7ffd=16)
    sim = Simulator(memory)
    indices = set()
    cases = 0
    outcomes = Counter()
    for first in (0, 0x4A36, 0x4734, 0x4738):
        for control, allocation in product(range(256), (0, 1, 2) if finish_entry else (0,)):
            second = (control * 25173 + first) & 65535
            coordinates = (0xAAAA, 0xBBBB, 0xCCCC)
            put(memory, 0x9BC1, first.to_bytes(2, 'little') + second.to_bytes(2, 'little') + bytes((control,)))
            for axis, coordinate in enumerate(coordinates):
                put(memory, 0x9B78 + axis * 3, coordinate.to_bytes(2, 'little'))
            memory[0x9B82] = memory[0x9B83] = memory[0x792E] = 0
            if finish_entry:
                # Подготовка трёх состояний списка до общего Entry, исходные шаблоны не меняются.
                put(memory, 0xA100, flat[0xA100:0xA780])
                for slot in range(allocation):
                    record = bytearray((offset * 43 + slot * 17 + 7) & 255 for offset in range(64))
                    record[:2] = bytes((0, 128))
                    record[24] = 255 if allocation == 2 and slot == 0 else 0
                    put(memory, 0xA100 + slot * 64, record)
                put(memory, 0xA100 + allocation * 64, bytes((128, 128)))
                put(memory, 0xBFFE, bytes((255, 63)))
            x, y = first, second
            for _ in range(control + 1):
                x, y, output, _ = random_step(x, y)
            index = ((output ^ 255) >> 2) & 15
            pointer = word(flat, 0x7799 + index * 2)
            sim.registers[:] = get_registers({'PC': 0x7859, 'SP': 0xBFFE}, None, False)
            trace = PortTrace(sim)
            sim.set_tracer(trace)
            sim.run(0x7859, 0x78A1)
            context = (first, second, control, index)
            assert sim.registers[PC] == 0x78A1 and sim.registers[SP] == 0xBFFE, context
            assert sim.registers[IXh] * 256 + sim.registers[IXl] == pointer, context
            assert sim.registers[18:24] == [0xCC, 0xCC, 0xBB, 0xBB, 0xAA, 0xAA], context
            assert (memory[0x9B82], memory[0x9B83], memory[0x792E]) == (1, 1, 16), context
            assert (word(memory, 0x9B15), word(memory, 0x9B17)) == (x, y), context
            assert trace.writes == [(0x7FFD, 17), (0x7FFD, 16)] and memory.o7ffd == 16, context
            if finish_entry:
                finish_template(memory, sim, pointer, coordinates, allocation, outcomes)
                assert (word(memory, 0x9B15), word(memory, 0x9B17)) == (x, y)
                assert trace.writes == [(0x7FFD, 17), (0x7FFD, 16)] and memory.o7ffd == 16
            indices.add(index)
            cases += 1
    assert indices == set(range(16))
    report = dict(passed=True, total_cases=cases, original_banked_seeded_indices=True,
                  all_original_template_pointers=True, assembly_executed=False)
    target = ROOT / 'Tools/Disasm/Reports/ActionSpawnTemplateEntryVerification.json'
    if finish_entry:
        assert cases == 3072 and all(outcomes[name] == 1024 for name in
            ('no_slot', 'created_first', 'skipped_FF_created_second'))
        report.update(outcomes=dict(outcomes), original_disk_sha256=manifest['sha256'],
            original_physical_files_checked=[17, 22, 23], original_common_code_relocation_checked=True,
            original_font_and_control_bank_composition_checked=True,
            actual_Entry_to_external_RET_executed=True, CPU_state_not_reset_at_template_loop=True,
            all_1664_pool_bytes_compared=True, original_single_row_templates_unmodified=True,
            no_slot_preserves_both_flags_and_pending_16=True,
            successful_creation_writes_class_12_state_09=True,
            FF_skip_clears_first_reuse_and_creates_second_record=True,
            SP_IX_AF_and_success_HL_DE_BC_checked=True,
            all_registers_full_RAM_R_T_and_write_order_not_independently_compared=True,
            saved_word_branch_executed=False, IRQ_executed=False,
            native_game_loop_executed=False, native_execution=False)
        target = ROOT / 'Tools/Disasm/Reports/ActionSpawnTemplateWholeEntryVerification.json'
    payload = json.dumps(report, indent=2) + '\n'
    target.write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finish-template', action='store_true')
    main(parser.parse_args().finish_template)
