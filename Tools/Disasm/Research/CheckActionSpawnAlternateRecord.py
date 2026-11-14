"""Создание альтернативной записи с настоящим эффектом страницы 3.

Документация: ../../../Docs/ActionSpawnSchedule.md
Документация: ../../../Docs/ActionSpawnRecordFinish.md
Документация: ../../../Docs/ActionObjectRecords.md
Документация: ../../../Docs/ActionClass6Link.md
"""
from itertools import product
from collections import Counter
from hashlib import sha256
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionSpawnTemplateLoop import signed, word
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import refresh, cp_flags
from ReferenceActionClassHandlers import ClassMachine


class TailMemory(RecordedBanks):
    """Чтения хвоста единственной создаваемой записи, только во время исполнения CPU."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.watching = False
        self.tail_reads = []

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.watching and isinstance(address, int) and 0xA127 <= address < 0xA140:
            self.tail_reads.append((address, value))
        return value


def complete_dispatch(memory, sim, trace, objects, record, counts):
    """Настоящие заголовок и диспетчер, затем независимый договор выбранного класса."""
    assert sim.registers[PC] == 0x7E89
    memory.watching = True
    for _ in range(100):
        if sim.registers[PC] == 0x64DF:
            break
        sim.run()
    else:
        raise AssertionError('Не достигнут диспетчер класса после ReadHeader')
    memory.watching = False
    pointer = word(memory, 0x9E00 + record[6])
    record[37] = 1 if objects[pointer - 0xC000 + 1] == 4 else 2
    assert bytes(memory[0xA100:0xA140]) == record
    assert trace.writes == [(0x7FFD, page) for page in (20, 16, 19, 16, 20, 16)]
    kind = record[18]
    target = 0x660E if kind == 0 else 0x657F
    assert kind in (0, 6)
    memory.watching = True
    for _ in range(12):
        if sim.registers[PC] == target:
            break
        sim.run()
    else:
        raise AssertionError('Диспетчер не передал управление классу')
    memory.watching = False
    model = ClassMachine(memory.banks, sim.registers)
    if kind == 0:
        model.class0()
    else:
        model.handle(6)
    memory.writes = []
    memory.recording = memory.watching = True
    for _ in range(3000):
        if sim.registers[PC] == 0x3FFF:
            break
        sim.run()
    else:
        raise AssertionError(('Обработчик класса не вернулся создателю', kind,
            hex(sim.registers[PC]), hex(sim.registers[SP]), model.path, model.m1_count,
            hex(model.r[PC]), hex(model.r[SP])))
    memory.recording = memory.watching = False
    assert all(model.r[i] == sim.registers[i] for i in (*range(25), 26, 27))
    assert memory.banks == model.banks and Counter(memory.writes) == Counter(model.writes)
    assert sim.registers[SP] == 0xC000 and memory.o7ffd == 16
    assert bytes(memory[0xA127:0xA140]) == record[39:64]
    assert memory.tail_reads == []
    assert trace.writes == [(0x7FFD, page) for page in (20, 16, 19, 16, 20, 16)]
    counts['class_' + str(kind)] += 1
    counts.update(model.path)
    if 'class6_zero_secondary' in model.path:
        counts['secondary_link_index_' + str(memory[0xA10B])] += 1
        counts['secondary_state_' + str(memory[0xA10A])] += 1


def saved_entry_rejections(banks):
    """Полные ранние возвраты Entry, точные регистры и отсутствие записей RAM."""
    cases = 0
    for saved in (0, 0x22F2, 0x2300, 0x23F1, 0x2400, 0xFFFF):
        for seed in range(256):
            memory = TailMemory(banks=[bank.copy() for bank in banks], out7ffd=16)
            memory[0x9B83], memory[0x9B82] = 1, 0xA5
            put(memory, 0x799C, saved.to_bytes(2, 'little'))
            memory[0x7B61], memory[0x79DE], memory[0x7A6A] = 0xAA, 0xBB, 0xCC
            put(memory, 0xBFFE, bytes((255, 63)))
            cpu = Simulator(memory)
            trace = PortTrace(cpu)
            cpu.set_tracer(trace)
            initial = get_registers(dict(PC=0x7859, SP=0xBFFE, HL=0x1357, DE=0x2468,
                BC=0x369C, AF=0x5A5D, IX=0xABCD, IY=0x5C3A,
                **{'^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC, '^AF':0xDEF0}), None, False)
            initial[14], initial[15], initial[26], initial[27] = seed ^ 0xA5, seed, seed & 1, seed % 3
            expected = list(initial)
            high, low = saved >> 8, saved & 255
            value, limit, m1 = (high, 0x23, 7) if high != 0x23 else (low, 0xF2, 10)
            expected[0:2] = [value, cp_flags(value, limit)]
            expected[4:6] = [high, low]
            expected[12], expected[24] = 0xC000, 0x3FFF
            expected[15] = refresh(seed, m1)
            before = [bytes(bank) for bank in memory.banks]
            cpu.registers[:] = initial
            memory.writes = []
            memory.recording = memory.watching = True
            for _ in range(16):
                if cpu.registers[PC] == 0x3FFF:
                    break
                cpu.run()
            else:
                raise AssertionError(('Отказ Entry не вернулся', saved, seed))
            memory.recording = memory.watching = False
            assert all(cpu.registers[i] == expected[i] for i in (*range(25), 26, 27))
            assert [bytes(bank) for bank in memory.banks] == before
            assert memory.writes == [] and memory.tail_reads == [] and trace.writes == []
            cases += 1
    assert cases == 1536
    return cases


def main(finish_dispatch=False, zero_predicate=False, saved_entry=False, distance_entry=False):
    assert not zero_predicate or finish_dispatch
    assert not saved_entry or finish_dispatch
    assert not distance_entry or finish_dispatch
    assert sum((zero_predicate, saved_entry, distance_entry)) <= 1
    gated_entry = saved_entry or distance_entry
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[3][:] = bytes(memory_image()[0xC000:])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    streams = (0xEBFC, 0xEBFF, 0xEBE4, 0xEBE7, 0xEBF0, 0xEBEA, 0xEBF3, 0xEBDB)
    cases = 0
    dispatch_counts = Counter()
    if finish_dispatch:
        # Проверка файлов, исходного переноса ядра и подготовленного банка эффектов по физическим байтам TRD.
        manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
        disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
        assert sha256(disk).hexdigest() == manifest['sha256']
        sources = {}
        for slot in (17, 20, 21, 24):
            entry = next(row for row in manifest['entries'] if row['slot'] == slot)
            raw = (ROOT / (entry['path'] + '.bin')).read_bytes()
            assert raw == disk[entry['offset']:entry['offset'] + len(raw)]
            sources[slot] = raw
        assert bytes(flat[0x6000:0x7F8F]) == sources[17][0x23D:0x21CC]
        assert bytes(flat[0x7F8F:0x10000]) == sources[17][0x1F8F:]
        expected_voxel = bytearray(0x4000)
        expected_voxel[:len(sources[20])] = sources[20]
        expected_voxel[0x2C00:0x2C00 + len(sources[21])] = sources[21]
        assert banks[3] == expected_voxel and objects == sources[24]
        # Проверка наблюдателя чтения реальными CPU-инструкциями для всех 25 адресов хвоста.
        probe = TailMemory(banks=[bank.copy() for bank in banks], out7ffd=16)
        for address in range(0xA127, 0xA140):
            probe.watching = False
            probe.tail_reads.clear()
            put(probe, 0x4000, bytes((0x3A, address & 255, address >> 8)))
            probe[address] = 0x6B
            cpu = Simulator(probe)
            cpu.registers[PC] = 0x4000
            probe.watching = True
            cpu.run()
            assert probe.tail_reads == [(address, 0x6B)]
    rejection_cases = saved_entry_rejections(banks) if saved_entry else 0
    distance_profiles = (((0, 0, 112), 110), ((0, 0, 0), 50), ((0, 0, 0xFF90), 117))
    distance_seed = next(seed for seed in range(65536)
                         if (value := step(seed, 0)['word']) >> 8 == value & 255) if distance_entry else None
    distance_counts = Counter()
    for fixture, mode, free, ttl, distance in product(range(32), (1,) if zero_predicate else (0, 1),
                                          range(9), (0, 26, 255), range(3) if distance_entry else (0,)):
        memory_type = TailMemory if finish_dispatch else RecordedBanks
        memory = memory_type(banks=[bank.copy() for bank in banks], out7ffd=16)
        record = bytearray((offset * 37 + fixture) & 255 for offset in range(64))
        record[:2] = bytes((0, 128))
        record[24] = 0
        put(memory, 0xA100, record)
        put(memory, 0xA140, (128, 128))
        memory[0x79DE], memory[0x7A6A] = mode * 32, mode * 6
        if gated_entry:
            # Данные сохранённого слова подготавливаются до общего входа, префикс сам задаёт модель и класс.
            saved = 0x23F2 + fixture % 14
            put(memory, 0x799C, saved.to_bytes(2, 'little'))
            memory[0x9B83], memory[0x9B82] = 1, 0xA5
            memory[0x7B61], memory[0x79DE], memory[0x7A6A] = 0xAA, 0xBB, 0xCC
        if distance_entry:
            # Сам писатель заменит прежний операнд словом HL, расстояния и Stream1 заданы до вызова.
            put(memory, 0x799C, bytes((0x5A, 0xA5)))
            coordinates, gate_m1 = distance_profiles[distance]
            for axis, value in enumerate(coordinates):
                put(memory, 0x9B79 + axis * 3, value.to_bytes(2, 'little'))
            put(memory, 0xEC02, distance_seed.to_bytes(2, 'little') + bytes((0,)))
        for slot in range(8):
            memory[0xA795 + slot * 18 + 7] = int(slot != free)
        memory[0x6D39], memory[0x6D3D] = 0, ttl
        states = {}
        for stream in streams:
            seed = (fixture * 719 + mode * 2953 + stream * 173) & 65535
            fold = (fixture + ttl + stream) & 255
            put(memory, stream, seed.to_bytes(2, 'little') + bytes((fold,)))
            states[stream] = (seed, fold)
        if zero_predicate:
            # Подготовка Stream0 до создания, его следующее слово равно нулю независимо от R.
            assert step(5254, 0)['word'] == 0
            put(memory, 0xEBDE, bytes((0x86, 0x14, 0)))

        def advance(stream):
            result = step(*states[stream])
            states[stream] = result['word'], result['fold']
            return result['word']

        random = advance(0xEBFC)
        model = ((random ^ (random >> 8)) & 28) + 64 + mode * 32
        coords = [signed(advance(0xEBFF)) // 2 for _ in range(3)][::-1]
        record[:6] = b''.join((coord & 65535).to_bytes(2, 'little') for coord in coords)
        record[6:8] = bytes((model, 0))
        delta = advance(0xEBE4)
        record[8] = ((delta >> 8) + (-1 if delta & 128 else 1) * (delta & 3)) & 255
        record[9] = advance(0xEBE7) & 31
        record[11:13] = bytes((255, 0))
        record[13:15] = states[0xEBDB][0].to_bytes(2, 'little')
        record[15:19] = bytes((100, 32, flat[0x7DE4], mode * 6))
        advance(0xEBF0)
        advance(0xEBEA)
        record[19:24] = bytes((min((advance(0xEBF3) & 255) | flat[0x7E07], flat[0x7E09] - 1),
                               0, 255, record[10], 0))
        states[0xEBDB] = states[0xEBDB][0], 0
        advance(0xEBDB)
        record[32:34] = b'\xff\xff'
        record[36] = 0
        effect = bytearray(memory[0xA795:0xA82D])
        pointer = word(flat, 0x9E00 + model)
        if free < 8:
            effect[free * 18:(free + 1) * 18] = record[:6] + bytes(
                (objects[pointer - 0xC000 + 1], 26, 0, 216, 0, 216, 1, 13, 192, 0, 12, 12))

        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        if finish_dispatch:
            # Новый полный путь требует обычного внешнего возврата, прежний режим останавливался до RET.
            put(memory, 0xBFFE, [255, 63])
        sim.registers[:] = get_registers({'PC': 0x794B if distance_entry else 0x7859 if saved_entry else 0x79CC,
                                         'SP': 0xBFFE, 'HL': saved if distance_entry else 0}, None, False)
        initial_r = ((fixture * 7) & 254) | mode if gated_entry else fixture * 7
        if distance_entry:
            initial_r ^= gate_m1 & 1
        sim.registers[15] = initial_r
        sample = None
        gate_sample = None
        if finish_dispatch:
            memory.watching = True
        if gated_entry:
            memory.writes = []
            memory.recording = True
        for _ in range(1800):
            pc = sim.registers[PC]
            if pc == 0x7E89:
                break
            if 0x7A96 <= pc < 0x7E89 and memory[pc:pc + 2] == [0xED, 0x5F]:
                sample = refresh(sim.registers[15], 2)
            if gated_entry and 0x79A8 <= pc < 0x79CC and memory[pc:pc + 2] == [0xED, 0x5F]:
                gate_sample = refresh(sim.registers[15], 2)
            sim.run()
        if finish_dispatch:
            memory.watching = False
        if gated_entry:
            memory.recording = False
            assert gate_sample is not None and gate_sample & 1 == mode
            assert gate_sample == refresh(initial_r, gate_m1 if distance_entry else 20), (distance, gate_sample, initial_r)
            assert (memory[0x79DE], memory[0x7A6A], memory[0x7B61]) == (mode * 32, mode * 6, 5 + (saved & 3))
            assert (memory[0x9B83], memory[0x9B82]) == (1, 0xA5)
            assert [value for bank, offset, value in memory.writes if (bank, offset) == (5, 0x3B61)] == [255, 5 + (saved & 3)]
        if distance_entry:
            assert bytes(memory[0x799C:0x799E]) == saved.to_bytes(2, 'little')
            assert [(offset, value) for bank, offset, value in memory.writes
                    if bank == 5 and offset in (0x399C, 0x399D)] == [(0x399C, saved & 255), (0x399D, saved >> 8)]
            expected_stream = step(distance_seed, 0) if distance != 1 else dict(word=distance_seed, fold=0)
            assert bytes(memory[0xEC02:0xEC05]) == expected_stream['word'].to_bytes(2, 'little') + bytes((expected_stream['fold'],))
            distance_counts[('far_positive', 'near_without_Stream1', 'far_negative')[distance]] += 1
        context = (fixture, mode, free, ttl)
        assert sim.registers[PC] == 0x7E89 and sim.registers[SP] == 0xBFFE, context
        record[24] = (sample + 1) & 15
        actual = bytes(memory[0xA100:0xA140])
        assert actual == record, (context, [(n, a, b) for n, (a, b) in enumerate(zip(actual, record)) if a != b])
        assert bytes(memory[0xA795:0xA82D]) == effect, context
        for address, (value, fold) in states.items():
            assert bytes(memory[address:address + 3]) == value.to_bytes(2, 'little') + bytes((fold,)), context
        assert (memory[0x6D39], memory[0x6D3D]) == (1, max(26, ttl)), context
        assert trace.writes == [(0x7FFD, page) for page in (20, 16, 19, 16)] and memory.o7ffd == 16, context
        if finish_dispatch:
            if zero_predicate:
                assert bytes(memory[0xEBDE:0xEBE1]) == bytes((0x86, 0x14, 0))
            complete_dispatch(memory, sim, trace, objects, record, dispatch_counts)
            if zero_predicate:
                assert bytes(memory[0xEBDE:0xEBE1]) == bytes((0, 0, 3))
        cases += 1

    report = dict(passed=True, total_cases=cases, whole_object_and_effect_pool_compared=True,
                  all_eight_stream_states_compared=True, stops_before_final_header=True, assembly_executed=False)
    target = ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateRecordVerification.json'
    if finish_dispatch:
        per_class = 2592 if distance_entry else 864
        assert dispatch_counts['class_0'] == (0 if zero_predicate else per_class)
        assert dispatch_counts['class_6'] == per_class
        report.update(stops_before_final_header=False, dispatch_counts=dict(dispatch_counts),
            original_header_class_dispatch_and_class_handlers_executed=True,
            header_scale_full_record_and_page_writes_checked=True,
            class_phase_exact_registers_except_T_all_RAM_and_write_multiplicity_checked=True,
            created_record_tail_27_3F_no_CPU_reads_observed=True,
            created_record_tail_27_3F_preserved=True, tail_read_CPU_probe_passed=True,
            external_return_3FFF_prepared_at_BFFE=True,
            prefix_all_registers_and_full_RAM_not_independently_compared=True,
            original_physical_files_revalidated=[17, 20, 21, 24],
            original_disk_sha256=manifest['sha256'], original_common_code_relocation_checked=True,
            original_voxel_bank_composition_checked=True, tail_read_CPU_probes=25,
            Entry_gate_and_native_game_loop_executed=False, IRQ_executed=False, native_execution=False)
        target = ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateDispatchVerification.json'
        if saved_entry:
            report.pop('Entry_gate_and_native_game_loop_executed')
            report.update(whole_Entry_saved_word_branch_executed=True,
                saved_words_prepared_before_Entry=list(range(0x23F2, 0x2400)),
                template_flags_unchanged_by_saved_branch=True,
                gate_R_parity_selects_model_and_class=True, gate_R_read_after_20_M1_checked=True,
                countdown_two_writes_FF_then_5_plus_saved_low_and_3_checked=True,
                CPU_state_not_reset_between_gate_and_creation=True,
                rejection_cases=rejection_cases,
                rejection_exact_registers_R_all_RAM_and_no_writes_checked=True,
                saved_word_original_writer_CheckDistance_executed=False,
                Entry_gate_executed=True, native_game_loop_executed=False)
            target = ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateSavedEntryVerification.json'
        if distance_entry:
            assert cases == 5184 and all(value == 1728 for value in distance_counts.values())
            report.pop('Entry_gate_and_native_game_loop_executed')
            report.update(CheckDistance_entry_to_external_RET_executed=True,
                saved_word_original_writer_CheckDistance_executed=True,
                initial_saved_operand_replaced_by_HL=True,
                exact_two_byte_saved_word_write_checked=True,
                distance_profiles=[dict(words=list(words), M1_until_gate_R=m1)
                                   for words, m1 in distance_profiles],
                distance_counts=dict(distance_counts), Stream1_initial_word=distance_seed,
                Stream1_initial_fold=0, Stream1_equal_bytes_required_for_far_profiles=True,
                Stream1_unchanged_for_near_profiles=True,
                gate_R_values_and_counter_two_writes_checked=True,
                CPU_state_not_reset_between_writer_gate_and_creation=True,
                common_Entry_executed_in_near_profiles_only=True,
                all_distance_and_stream_and_word_input_combinations_proved=False,
                native_game_loop_executed=False)
            target = ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateDistanceEntryVerification.json'
        if zero_predicate:
            assert dispatch_counts['class6_zero_secondary'] == cases == 864
            assert dispatch_counts['predicate_nonzero'] == 0
            assert dispatch_counts['secondary_link_index_0'] == cases
            assert dispatch_counts['secondary_state_1'] == cases
            report.update(Stream0_seed_5254_fold_0_prepared_before_creation=True,
                          Stream0_next_word_zero_independent_of_R=True,
                          class6_zero_predicate_and_real_secondary_filter_executed=True,
                          Stream0_state_before_header_and_after_class_checked=True,
                          secondary_filter_selects_created_record_itself_in_this_fixture=True,
                          created_record_slot_index=0, final_LinkedIndex=0, final_StateCode=1)
            target = ROOT / 'Tools/Disasm/Reports/ActionSpawnAlternateZeroPredicateVerification.json'
    payload = json.dumps(report, indent=2) + '\n'
    target.write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finish-dispatch', action='store_true')
    parser.add_argument('--zero-class6-predicate', action='store_true')
    parser.add_argument('--saved-entry', action='store_true')
    parser.add_argument('--distance-entry', action='store_true')
    args = parser.parse_args()
    main(args.finish_dispatch or args.zero_class6_predicate or args.saved_entry or args.distance_entry,
         args.zero_class6_predicate, args.saved_entry, args.distance_entry)
