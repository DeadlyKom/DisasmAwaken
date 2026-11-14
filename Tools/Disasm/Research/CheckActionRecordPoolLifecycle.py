"""Последовательное заполнение исходных 25 слотов и однократный пропуск FF.

Документация: ../../../Docs/ActionObjectRecords.md
Документация: ../../../Docs/ActionMissileCreation.md
"""
from hashlib import sha256
import json
import sys

from CheckActionMissileCreation import ROOT, flat_action, Simulator, get_registers, Memory, COEFFICIENTS
from VerifySources import structure_symbols


def main(game_release=False):
    fields = structure_symbols()
    assert fields['FACTIONRECORD.EFFECTRESERVE'] == 19
    assert fields['FACTIONRECORD.CLASSCODE'] == 18
    assert fields['FACTIONRECORD.REUSEBYTE'] == 24
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    item = next(row for row in manifest['entries'] if row['slot'] == 17)
    action = (ROOT/(item['path']+'.bin')).read_bytes()
    assert action == disk[item['offset']:item['offset']+item['length']]
    baseline = flat_action()
    assert bytes(baseline[0xA100:0xA780]) == action[0x4100:0x4780]
    assert all(bytes(baseline[0xA100+64*i:0xA102+64*i]) == b'\x00\x80' for i in range(25))
    assert bytes(baseline[0xA740:0xA742]) == b'\x80\x80'
    # Проверка наблюдателя настоящей записью CPU в отдельной памяти.
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
    identity = ((127, 0, 0), (0, 127, 0), (0, 0, 127))
    profiles = []
    calls = created = failures = deferred = release_calls = 0
    for target in range(25):
        for preferred in (0, 1):
            memory.recording = False
            memory[:] = baseline
            # Создание одной активной цели и подготовка геометрической фикстуры.
            target_address = 0xA100+64*target
            memory[target_address:target_address+2] = [0, 0]
            for row, coefficients in zip(COEFFICIENTS, identity):
                for address, value in zip(row, coefficients):
                    memory[address] = value
            memory[0x9C12:0x9C14] = [7, preferred]
            marker = bytes(memory[0xA740:0xA780])
            trace = []
            releases = []

            def invoke(expected_slot, deferred_slot=None):
                nonlocal calls, created, failures, deferred
                memory.recording = False
                memory[0xBFFE:0xC000] = [255, 63]
                before_pool = bytearray(memory[0xA100:0xA780])
                cpu.registers[:] = get_registers({'SP':0xBFFE, 'BC':0x3600|target,
                    'HL':0x1357, 'DE':0x2468, 'AF':0xA55A, 'IX':0xABCD, 'IY':0x5C3A,
                    '^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC, '^AF':0xDEF0}, None, False)
                memory.writes = []
                memory.recording = True
                cpu.run(start=0x60AE, stop=0x3FFF)
                memory.recording = False
                r = cpu.registers
                # Проверка оригинального возврата и полей маркера после каждого реального вызова.
                assert r[12] == 0xC000 and r[8:10] == [0xAB, 0xCD]
                assert bytes(memory[0xBFFE:0xC000]) == b'\xFF\x3F'
                assert bytes(memory[0xA740:0xA780]) == marker
                assert not any(0xA740 <= address < 0xA780 for address, _ in memory.writes)
                assert bytes(memory[0x9C12:0x9C14]) == bytes((7, preferred))
                if expected_slot is None:
                    assert (r[0], r[1], 256*r[10]+r[11]) == (128, 0x42, 0xA740)
                    if deferred_slot is not None:
                        # Единственная разрешённая запись массива при отказе с однократным пропуском.
                        before_pool[64*deferred_slot+24] = 0
                        assert memory[0xA100+64*deferred_slot+1] == 128
                        assert [(a,v) for a,v in memory.writes if 0xA100 <= a < 0xA740] == [
                            (0xA100+64*deferred_slot+24, 0)]
                        deferred += 1
                    else:
                        assert not any(0xA100 <= address < 0xA740 for address, _ in memory.writes)
                    assert bytes(memory[0xA100:0xA780]) == bytes(before_pool)
                    failures += 1
                else:
                    address = 0xA100+64*expected_slot
                    assert (r[0], r[1], 256*r[10]+r[11]) == (
                        expected_slot, 0x45|(expected_slot&0x28), address)
                    assert memory[address+1] != 128
                    assert memory[address+18] == 17
                    assert memory[address+19] == (50 if preferred else 10)
                    created += 1
                trace.append(dict(slot=expected_slot, deferred_slot=deferred_slot,
                    pool_RAM_writes=sum(0xA100 <= a < 0xA780 for a,_ in memory.writes)))
                calls += 1

            # Заполнение всех остальных исходных слотов без сброса памяти между вызовами.
            allocation_order = [index for index in range(25) if index != target]
            for slot in allocation_order:
                invoke(slot)
            assert all(memory[0xA101+64*i] != 128 for i in range(25))
            invoke(None)
            invoke(None)
            # Выбор слотов остаётся сценарием модели, пометка может выполняться настоящими процедурами.
            for release_entry, slot in zip((0xF394, 0xF03D), (allocation_order[0], allocation_order[-1])):
                address = 0xA100+64*slot
                if game_release:
                    # Проверка точных текущих байтов двух пометчиков и их физического происхождения.
                    prefix = 0xDD if release_entry == 0xF394 else 0xFD
                    code = bytes((prefix,0x36,1,128,prefix,0x36,0,0,prefix,0x36,24,255,0xC9))
                    assert bytes(baseline[release_entry:release_entry+13]) == code
                    assert action[release_entry-0x6000:release_entry-0x6000+13] == code
                    memory[0xBFFE:0xC000] = [255,63]
                    initial_release = get_registers({'SP':0xBFFE, 'AF':0xA55A, 'HL':0x1357,
                        'DE':0x2468, 'BC':0x369C, '^HL':0x1234, '^DE':0x5678,
                        '^BC':0x9ABC, '^AF':0xDEF0, 'IX':address if prefix==0xDD else 0xABCD,
                        'IY':address if prefix==0xFD else 0x5C3A}, None, False)
                    initial_release[15] = (target*73+preferred)&255
                    wanted = list(initial_release)
                    wanted[12],wanted[24] = 0xC000,0x3FFF
                    wanted[15] = (initial_release[15]&128)|((initial_release[15]+7)&127)
                    expected_memory = list(memory)
                    changes = [(address+1,128),(address,0),(address+24,255)]
                    for destination,value in changes:expected_memory[destination] = value
                    cpu.registers[:] = initial_release
                    memory.writes = [];memory.recording = True
                    cpu.run(start=release_entry,stop=0x3FFF)
                    memory.recording = False
                    # Проверка всей RAM, порядка трёх записей и всех регистров кроме T.
                    assert memory.writes == changes and list(memory) == expected_memory
                    assert all(cpu.registers[i] == wanted[i] for i in range(len(wanted)) if i!=25)
                    releases.append(dict(entry=release_entry,slot=slot,exact_RAM_and_registers_checked=True))
                    release_calls += 1
                else:
                    memory[address:address+2] = [0, 128]
                    memory[address+24] = 255
                invoke(None, deferred_slot=slot)
                invoke(slot)
            profiles.append(dict(target=target, preferred=preferred,
                allocation_order=allocation_order, calls=trace, releases=releases, marker_preserved=True))
    result = dict(passed=True, method='stateful_original_missile_creator_pool_fill_and_deferred_reuse',
        original_release_routines_executed=game_release,original_release_calls=release_calls,
        profiles=len(profiles), calls=calls, successful_creations=created, no_slot_returns=failures,
        one_shot_skip_clears=deferred, details=profiles, original_pool_bytes_checked=True,
        original_disk_sha256=manifest['sha256'], all_25_initial_target_slots=True,
        calls_execute_without_child_stubs=True, memory_not_reset_between_calls=True,
        CPU_write_watch_positive_control=True, physical_structure_offsets_checked=True,
        marker_all_64_bytes_preserved=True, marker_written_by_CPU=False,
        stock_unchanged=True, pool_unchanged_on_ordinary_full_failure=True,
        freeing_is_fixture_action_not_game_freeing_proof=not game_release,
        release_selection_is_fixture_not_main_loop_reachability=True,
        original_release_exact_RAM_registers_and_R_checked=game_release,full_R_proved=False,
        full_game_dynamic_pool_limit_proved=False, arbitrary_writers_and_IRQ_excluded=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports'/('ActionRecordPoolRealReleaseVerification.json' if game_release else 'ActionRecordPoolLifecycleVerification.json')).write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'details'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main('--game-release' in sys.argv)
