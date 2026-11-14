"""Реальные создание класса 14, массовое освобождение и повторное заполнение.

Документация: ../../../Docs/ActionObjectRecords.md
Документация: ../../../Docs/ActionClass20Spawn.md
Документация: ../../../Docs/ActionClass14Reuse.md
"""
from hashlib import sha256
import json

from CheckActionMissileCreation import ROOT, flat_action, Simulator, get_registers, Memory, COEFFICIENTS
from ActionRandomStreamLayout import STREAMS


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    item = next(row for row in manifest['entries'] if row['slot'] == 17)
    action = (ROOT/(item['path']+'.bin')).read_bytes()
    assert action == disk[item['offset']:item['offset']+item['length']]
    baseline = flat_action()
    assert bytes(baseline[0xA100:0xA780]) == action[0x4100:0x4780]
    # Проверка наблюдателя одной реальной инструкцией CPU.
    probe = Memory([0]*65536)
    probe[0x4000:0x4003] = [0x32, 0, 0x70]
    probe_cpu = Simulator(probe)
    probe_cpu.registers[24] = 0x4000
    probe.writes = []
    probe.recording = True
    probe_cpu.run()
    assert probe.writes == [(0x7000, 0)]
    memory = Memory(baseline)
    cpu = Simulator(memory)
    stream = next(pointer for number, _, pointer in STREAMS if number == 8)
    profiles = []
    creates = failed = releases = cleared = 0
    for seed in (0, 1, 0x3456, 0xABCD, 0xFFFF):
        for mode in (0, 255):
            memory.recording = False
            memory[:] = baseline
            # Подготовка начального генератора и единичной геометрии, далее они не сбрасываются.
            memory[stream:stream+3] = [seed&255, seed>>8, (seed^0xA5)&255]
            memory[0x6E75] = mode
            for row in range(3):
                for column in range(3):
                    memory[COEFFICIENTS[row][column]] = 127 if row == column else 0
            marker = bytes(memory[0xA740:0xA780])
            rounds = []

            def invoke(entry):
                memory.recording = False
                memory[0xBFFE:0xC000] = [255, 63]
                cpu.registers[:] = get_registers({'SP':0xBFFE, 'AF':0xA55A, 'HL':0x1357,
                    'DE':0x2468, 'BC':0x369C, 'IX':0xA100, 'IY':0x5C3A,
                    '^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC, '^AF':0xDEF0}, None, False)
                memory.writes = []
                memory.recording = True
                cpu.run(start=entry, stop=0x3FFF)
                memory.recording = False
                r = cpu.registers
                # Проверка внешнего возврата и полного маркера, включая запись прежнего значения.
                assert r[12] == 0xC000 and bytes(memory[0xBFFE:0xC000]) == b'\xFF\x3F'
                assert bytes(memory[0xA740:0xA780]) == marker
                assert not any(0xA740 <= address < 0xA780 for address, _ in memory.writes)
                assert r[8:10] == [0xA1, 0]
                return r

            for cycle in range(3):
                allocation = []
                # Заполнение исходных 25 слотов настоящим создателем класса 14.
                for slot in range(25):
                    before = bytearray(memory[0xA100:0xA780])
                    r = invoke(0x617D)
                    address = 0xA100+64*slot
                    assert 256*r[10]+r[11] == address and r[0:2] == [0, 0x44]
                    assert memory[address+1] != 128
                    assert (memory[address+18], memory[address+19], memory[address+24]) == (20, 250, 0)
                    components = b''.join((256*r[i]+r[i+1]).to_bytes(2, 'little') for i in (6, 4, 2))
                    assert bytes(memory[address:address+6]) == components
                    # Другие слоты не инициализируются повторно вместе с выбранным.
                    before[64*slot:64*(slot+1)] = bytes(memory[address:address+64])
                    assert bytes(memory[0xA100:0xA780]) == bytes(before)
                    allocation.append(slot)
                    creates += 1
                before_pool = bytes(memory[0xA100:0xA780])
                before_stream = bytes(memory[stream:stream+3])
                r = invoke(0x617D)
                assert (r[0], r[1], 256*r[10]+r[11]) == (128, 0x42, 0xA740)
                assert bytes(memory[0xA100:0xA780]) == before_pool
                assert bytes(memory[stream:stream+3]) == before_stream
                assert not any(0xA100 <= a < 0xA780 for a, _ in memory.writes)
                failed += 1
                # Массовый поиск сам выбирает все активные записи класса 14 до исходного маркера.
                expected = bytearray(before_pool)
                changes = []
                for slot in range(25):
                    address = 0xA100+64*slot
                    for pointer, value in ((address+1, 128), (address, 0), (address+24, 255)):
                        expected[pointer-0xA100] = value
                        changes.append((pointer, value))
                r = invoke(0x6172)
                assert r[0:2] == [128, 0x42] and 256*r[10]+r[11] == 0xA740
                assert bytes(memory[0xA100:0xA780]) == bytes(expected)
                assert [(a,v) for a,v in memory.writes if 0xA100 <= a < 0xA780] == changes
                assert [(a,v) for a,v in memory.writes if not 0xBFFA <= a < 0xBFFE] == changes
                releases += 1
                # Первый следующий поиск пропускает все FF, только обнуляет их и отказывает.
                before_stream = bytes(memory[stream:stream+3])
                r = invoke(0x617D)
                for slot in range(25):
                    expected[64*slot+24] = 0
                assert (r[0], r[1], 256*r[10]+r[11]) == (128, 0x42, 0xA740)
                assert bytes(memory[0xA100:0xA780]) == bytes(expected)
                assert bytes(memory[stream:stream+3]) == before_stream
                assert [(a,v) for a,v in memory.writes if 0xA100 <= a < 0xA780] == [
                    (0xA100+64*slot+24, 0) for slot in range(25)]
                cleared += 25
                failed += 1
                rounds.append(dict(cycle=cycle, allocation_order=allocation,
                    released_by_original_scan=25, deferred_skip_clears=25))
            profiles.append(dict(seed=seed, mode=mode, cycles=rounds,
                final_stream_hex=bytes(memory[stream:stream+3]).hex(), marker_preserved=True))
    result = dict(passed=True, method='original_class14_create_release_scan_and_refill_without_pool_reset',
        profiles=len(profiles), cycles_per_profile=3, successful_creations=creates,
        creation_failures=failed, original_mass_release_calls=releases, deferred_skip_clears=cleared,
        details=profiles, physical_original_pool_checked=True, CPU_write_watch_positive_control=True,
        original_marker_all_64_bytes_preserved=True, marker_CPU_writes=False,
        records_class_not_changed_by_fixture=True, freeing_not_performed_by_fixture=True,
        generator_and_matrix_not_reset_between_cycles=True, failed_creation_does_not_advance_stream=True,
        calls_selected_by_scenario_not_main_loop=True, full_R_proved=False,
        all_runtime_writers_and_dynamic_pool_limit_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass14PoolCycleVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'details'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
