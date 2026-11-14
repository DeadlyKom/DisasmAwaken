"""Сдвиг физического хвоста для совмещённых окон и всех 46 записей станции."""

import json
import re

from CheckStationExpandedDrawTail import DrawMemory, draw_list, word
from CheckStationFlightCycle import payload, put, run_to
from CheckInitialZeroTailAccesses import WatchedCPU
from CheckScreenUpdate import PortTrace
from TraceFlight import A, D, E, H, L, PC, ROOT, SP, main as trace
from skoolkit.simutils import IXh, IXl


FIRST = 0xF488
OPENERS = ('OpenMapPanelGroup', 'OpenHelpPanels', 'OpenEquipmentPanels', 'OpenShipPanels',
           'OpenContractPanels', 'OpenGameOptions', 'OpenEnvOptions', 'OpenRestoreDialog')
LAST_INDICES = (20, 22, 38, 26, 32, 42, 41, 44)
LENGTHS = (21, 23, 27, 33, 36, 37, 38, 39)
DRAW_LIST = 0xF3DE
PHYSICAL_LIST_READ_END = 0xF4BA


def check_literal_openers(handlers, symbols, flow):
    assert len(set(handlers)) == len(handlers) == 46
    indices = {handler: index for index, handler in enumerate(handlers)}
    entry = symbols['Station.RestoreItemBounds.Entry']
    target = re.compile(rf'(?:CALL|JP|JR) (?:[A-Z]+,)?#{entry:04X}')
    candidates = []
    for region in flow:
        for i, item in enumerate(region['instructions']):
            if not target.fullmatch(item['operation']):
                continue
            assert region['name'] == 'Station' and i
            previous = region['instructions'][i - 1]
            match = re.fullmatch(r'LD HL,#([0-9A-F]{4})', previous['operation'])
            assert match and previous['address'] + 3 == item['address']
            handler = int(match[1], 16)
            candidates.append(dict(call_site=item['address'], wrapper=handler, bound_index=indices[handler]))
    assert len(candidates) == 35 and len({row['wrapper'] for row in candidates}) == 35
    return candidates


def check_list_entry_references(flow, functions):
    calls = []
    writes = []
    for region in flow:
        name = region['name']
        for item in region['instructions']:
            op = item['operation']
            store = re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|HL|BC|DE|SP|IX|IY)', op)
            if store:
                address = int(store[1], 16)
                width = 1 if store[2] == 'A' else 2
                if address < 0x9CA8 and 0x9CA6 < address + width:
                    writes.append((name, item['address'], op))
            if not re.fullmatch(r'(?:JP|JR|CALL) (?:[A-Z]+,)?#BE38', op):
                continue
            owner, = (row for row in functions if row['region'] == name and row['slot'] == item['slot']
                      and row['offset'] <= item['offset'] < row['end_offset'])
            calls.append(dict(region=name, pc=item['address'], path=owner['path']))
    assert writes == [('StationBoot', 0x41B4, 'LD (#9CA6),HL')]
    boot = next(region['instructions'] for region in flow if region['name'] == 'StationBoot')
    assert next(item['operation'] for item in boot if item['address'] == 0x41B1) == 'LD HL,#F3DE'
    station = next(region['instructions'] for region in flow if region['name'] == 'Station')
    assert next(item['hex'] for item in station if item['address'] == 0xBE37) == 'c0'
    assert [(call['region'], call['pc']) for call in calls] == [
        ('Station', address) for address in (0x68E1, 0x78CA, 0x7F22, 0x9E80, 0xCBB3, 0xCBFE, 0xCC36, 0xCC81)]
    return dict(direct_calls=calls, conditional_fallthrough=0xBE37,
                direct_head_writer=0x41B4, initialized_head=0xF3DE,
                registered_regions_checked=len(flow), indirect_head_writes_proved=False)


def check_periodic_list_references(flow, memory):
    station = next(region['instructions'] for region in flow if region['name'] == 'Station')
    ops = {item['address']: item['operation'] for item in station}
    expected = {
        0x78C6: 'LD DE,(#788D)', 0x78CA: 'CALL #BE38', 0x78D9: 'JR NZ,#78BD',
        0x68DD: 'LD DE,(#6878)', 0x68E1: 'CALL #BE38', 0x68ED: 'JR NZ,#68CC',
        0x6D35: 'LD DE,(#788D)', 0x6D39: 'CALL #BE27',
        0x7885: 'LD DE,#788C', 0x7888: 'CALL #CB64', 0x788B: 'RET NZ',
        0x6870: 'LD DE,#6877', 0x6873: 'CALL #CB64', 0x6876: 'RET NZ',
        0x78A1: 'JR NC,#78A6', 0x78A3: 'LD HL,#78D6', 0x78A6: 'LD (#9A89),HL',
        0x688C: 'JR NC,#6891', 0x688E: 'LD HL,#68EA', 0x6891: 'LD (#9A89),HL',
        0x7843: 'CALL #C85E', 0x7846: 'JR NZ,#784E', 0x7848: 'LD HL,#9A58', 0x784B: 'LD (#9A89),HL',
        0x6841: 'CALL #C85E', 0x6844: 'JR NZ,#684D', 0x6846: 'LD HL,#9A58', 0x6849: 'LD (#9A89),HL',
        0x6780: 'LD HL,#9A58', 0x6783: 'LD (#9A89),HL',
        0x6C67: 'LD HL,#9A58', 0x6C6A: 'LD (#9A89),HL',
        0xA781: 'LD HL,#9A58', 0xA784: 'LD (#9A89),HL',
    }
    assert all(ops[pc] == operation for pc, operation in expected.items())
    assert [(item['address'], item['operation']) for item in station if item['operation'] == 'LD (#9A89),HL'] == [
        (pc, 'LD (#9A89),HL') for pc in (0x6783, 0x6849, 0x6891, 0x6C6A, 0x784B, 0x78A6, 0xA773, 0xA784, 0xAA69)
    ]
    assert [(word(memory, pointer + 1), word(memory, 0xF109 + index * 16)) for index, pointer in
            ((20, 0x788C), (26, 0x6877))] == [(20, 0x788C), (26, 0x6877)]
    assert all(memory[0xF101 + index * 16] & 0xE0 == 0 for index in (20, 26))
    events = {word(memory, 0xF103 + index * 16) + 3: index for index in range(46)}
    assert (events[0x783B], events[0x683A]) == (20, 26)
    assert (events[0x6E82], events[0x741E + 3], events[0x74A7 + 3], events[0x7539 + 3]) == (10, 43, 44, 40)

    removal_sites = []
    for region in flow:
        for index, item in enumerate(region['instructions']):
            if not re.fullmatch(r'(?:CALL|JP|JR) (?:[A-Z]+,)?#C873', item['operation']):
                continue
            assert region['name'] == 'Station'
            previous = region['instructions'][index - 1]
            assert previous['address'] + len(bytes.fromhex(previous['hex'])) == item['address']
            if load := re.fullmatch(r'LD DE,\(#([0-9A-F]{4})\)', previous['operation']):
                operand = int(load[1], 16)
                removal_sites.append(dict(pc=item['address'], operand=operand, key=word(memory, operand)))
            else:
                removal_sites.append(dict(pc=item['address'], operand=None, key=None))
    assert [(row['pc'], row['key']) for row in removal_sites if row['key'] in (20, 26)] == [
        (0x6791, 26), (0x6C64, 20)
    ]
    assert [row['pc'] for row in removal_sites if row['key'] is None] == [
        0x6E86, 0x747B, 0x7504, 0x7549, 0x9E48, 0xA7AD
    ]
    return dict(periodic_keys=[20, 26], direct_removal_sites=removal_sites,
                event_close_entries=[0x783B, 0x683A], closes_use_row_guard=0xC85E,
                group_removals_reset_periodic=True, popup_filter_excludes_periodic_keys=True,
                indirect_mutations_outside_registered_paths_proved=False)


def check_periodic_removal_paths(memory, cpu, symbols, invoke):
    initial = tuple(bank.copy() for bank in memory.banks), cpu.registers[:]
    registers = cpu.registers
    rows = []
    for name, key, periodic, selected, removed in (
        ('HandleSystemMapAction', 20, 0x78D6, 20, (20,)),
        ('HandleModelPreviewClick', 26, 0x68EA, 26, (26,)),
        ('HandleMapPanelEvent', 20, 0x78D6, 11, (11, 20)),
        ('DropShipDetailPanels', 26, 0x68EA, None, (26,)),
        ('CloseAllItems', 20, 0x78D6, None, (20, 26)),
        ('CloseAllItems', 26, 0x68EA, None, (20, 26)),
        ('RemoveOtherPopups', 20, 0x78D6, None, (40,)),
        ('RemoveOtherPopups', 26, 0x68EA, None, (40,)),
    ):
        for bank, saved in zip(memory.banks, initial[0]):
            bank[:] = saved
        memory.out7ffd(0x10)
        registers[:] = initial[1]
        invoke('OpenMapPanelGroup')
        invoke('OpenShipPanels')
        put(memory, 0x9A89, periodic.to_bytes(2, 'little'))
        memory[0x9E78], memory[0x9839] = 0, 0
        if selected is not None:
            item = 0xF0FD + 16 * selected
            invoke('RestoreItemBounds', hl=word(memory, item + 12))
            registers[A] = 0
            registers[IXh], registers[IXl] = divmod(item, 256)
            memory[0x6308] = memory[0xAEC7]
        if name == 'RemoveOtherPopups':
            invoke('RestoreItemBounds', hl=word(memory, 0xF109 + 16 * 40))
            put(memory, 0x9E31, b'\xF0\xFF')
        before = {index for _, _, index in draw_list(memory)}
        assert {20, 26, *removed} <= before
        memory.reads.clear()
        memory.writes.clear()
        invoke(name, hl=0x5F00, de=selected)
        after = {index for _, _, index in draw_list(memory)}
        target = word(memory, 0x9A89)
        assert after <= before and set(removed).isdisjoint(after)
        assert all(address < 0xF4DE for _, address, _ in memory.reads + memory.writes)
        if name == 'RemoveOtherPopups':
            assert {20, 26} <= after and target == periodic
        else:
            assert key not in after and target == symbols['Station.EmptyCallback.Entry']
        rows.append(dict(entry=name, periodic_key=key, selected=selected, removed=sorted(before - after),
                         periodic_before=periodic, periodic_after=target))
    for bank, saved in zip(memory.banks, initial[0]):
        bank[:] = saved
    memory.out7ffd(0x10)
    registers[:] = initial[1]
    memory.reads.clear()
    memory.writes.clear()
    return dict(cases=rows, periodic_and_selected_event_context_prepared=True,
                original_panel_openers_and_close_handlers_executed=True)


def check_popup_tail(memory, cpu, handlers, symbols, station):
    snapshot = [bank.copy() for bank in memory.banks]
    cases = []
    for count in (63, 64):
        for bank, saved in zip(memory.banks, snapshot):
            bank[:] = saved
        memory.out7ffd(0x10)
        ordinary, popup = 0, 40
        assert memory[0xF101 + 16 * ordinary] & 0xE0 != 0x20
        assert memory[0xF101 + 16 * popup] & 0xE0 == 0x20
        pointers = [handlers[ordinary]] * (count - 1) + [handlers[popup], 0x0101]
        put(memory, DRAW_LIST, b''.join(value.to_bytes(2, 'little') for value in pointers))
        assert memory[0x9E30] == 0x21
        put(memory, 0x9E31, b'\xF0\xFF')
        put(memory, 0x5FFD, b'\xFF\x3F')
        cpu.registers[PC], cpu.registers[SP] = symbols['Station.RemoveOtherPopups.Entry'], 0x5FFD
        cpu.set_tracer(PortTrace(cpu))
        memory.reads.clear()
        memory.writes.clear()

        last = DRAW_LIST + 2 * (count - 1)
        source, end = last + 2, last + 2 + 128
        original = bytes(memory[source:end])
        assert original[:2] == b'\x01\x01'
        assert original[2:] == station[source + 2 - 0x6000:end - 0x6000]
        run_to(cpu, 0x3FFF)
        assert cpu.registers[SP] == 0x5FFF and memory.o7ffd == 0x10
        assert word(memory, last) == 0x0101 and bytes(memory[last:last + 128]) == original
        assert [word(memory, DRAW_LIST + 2 * i) for i in range(count - 1)] == pointers[:-2]
        assert memory.reads == [(0xCB48, address, original[address - source])
                                for address in range(0xF472, end)]
        assert memory.writes == [(0xCB48, address, original[address - last])
                                 for address in range(0xF472, end - 2)]
        cases.append(dict(entries=count, popup_index=popup, end_marker_preserved=True,
                          read_end_exclusive=end, write_end_exclusive=end - 2))
    assert cases[-1]['read_end_exclusive'] == 0xF4DE and cases[-1]['write_end_exclusive'] == 0xF4DC
    return dict(cases=cases, original_popup_filter_and_removal_executed=True,
                repeated_original_pointers_supplied=True, normal_game_list_proved=False)


def check_unique_list_positions(memory, cpu, handlers, symbols):
    memory.out7ffd(0x10)
    end = PHYSICAL_LIST_READ_END + 2
    original = bytes(memory[DRAW_LIST:end])
    initial = cpu.registers[:]
    profiles = 0
    for count in range(1, len(handlers) + 1):
        items = handlers[:count]
        encoded = b''.join(handler.to_bytes(2, 'little') for handler in (*items, 0x0101))
        raw = encoded + bytes((index * 37 + 11) & 255 for index in range(len(original) - len(encoded)))
        for position in range(count):
            first = position * 2
            next_item = first + 2
            remaining = items[:position] + items[position + 1:]
            for operation in ('RemoveItemDraw', 'MoveItemToTail'):
                put(memory, DRAW_LIST, raw)
                put(memory, 0x5FFD, b'\xFF\x3F')
                cpu.registers[:] = initial
                cpu.registers[PC], cpu.registers[SP] = symbols[f'Station.{operation}.Entry'], 0x5FFD
                cpu.registers[D], cpu.registers[E] = 0, position
                cpu.registers[H], cpu.registers[L] = divmod(items[position], 256)
                memory.reads.clear()
                memory.writes.clear()
                expected = bytearray(raw)
                expected[first:first + 128] = raw[next_item:next_item + 128]
                ordered = remaining
                if operation == 'MoveItemToTail':
                    marker = (count - 1) * 2
                    expected[marker:marker + 4] = items[position].to_bytes(2, 'little') + b'\x01\x01'
                    ordered = remaining + [items[position]]
                run_to(cpu, 0x3FFF)
                assert cpu.registers[SP] == 0x5FFF
                assert bytes(memory[DRAW_LIST:end]) == expected
                assert [handler for _, handler, _ in draw_list(memory)] == ordered
                assert all(address < PHYSICAL_LIST_READ_END for _, address, _ in memory.reads + memory.writes)
                profiles += 1
    put(memory, DRAW_LIST, original)
    assert profiles == 2162
    return dict(profiles=profiles, max_original_handlers=len(handlers), every_position_checked=True,
                read_end_exclusive=PHYSICAL_LIST_READ_END, all_normal_game_callers_proved=False)


def check_rebuild_limit(memory, cpu, handlers, symbols, station):
    registers = cpu.registers
    snapshot = [bank.copy() for bank in memory.banks]
    group = [memory[0xF101 + 16 * index] & 0xE0 for index in range(len(handlers))]
    front = group.index(0x40)
    last = next(index for index in range(len(group)) if index != front and group[index] == 0x40)
    available = [index for index in range(len(group)) if index not in (front, last)]
    cases = []
    for count in range(46, 64):
        for bank, saved in zip(memory.banks, snapshot):
            bank[:] = saved
        memory.out7ffd(0x10)
        keys = [available[index % len(available)] for index in range(count - 2)] + [front, last]
        pointers = [handlers[index] for index in keys]
        put(memory, DRAW_LIST, b''.join(value.to_bytes(2, 'little') for value in (*pointers, 0x0101)))
        memory[0x9E78] = 0
        memory[0x9CAA] = 0
        put(memory, 0x5FFD, b'\xFF\x3F')
        registers[PC], registers[SP] = symbols['Station.RebuildInterface.Entry'], 0x5FFD
        cpu.set_tracer(PortTrace(cpu))
        memory.reads.clear()
        memory.writes.clear()

        # Эталон физического сдвига отдельно от порядка обработки исходных ключей.
        end = DRAW_LIST + 2 * count + 128
        expected = bytearray(memory[DRAW_LIST:end])
        assert expected[PHYSICAL_LIST_READ_END - DRAW_LIST:] == station[PHYSICAL_LIST_READ_END - 0x6000:end - 0x6000]
        expected_reads, expected_writes = [], []
        for position, key in enumerate(keys[:-1]):
            if group[key] != 0x40:
                continue
            expected[2:130] = expected[:128]
            item = 2 * (position + 1)
            pointer = expected[item:item + 2]
            source = item + 2
            block = expected[source:source + 128]
            for index, value in enumerate(block):
                read = DRAW_LIST + source + index
                if read >= PHYSICAL_LIST_READ_END:
                    expected_reads.append((0x9D02, read, value))
                if read - 2 >= PHYSICAL_LIST_READ_END:
                    expected_writes.append((0x9D02, read - 2, value))
            expected[item:item + 128] = block
            expected[:2] = pointer

        run_to(cpu, symbols['Station.RebuildInterface.StartDrawing'])
        assert memory.o7ffd == 0x18 and bytes(memory[DRAW_LIST:end]) == expected
        assert [(pc, pos, value) for pc, pos, value in memory.reads if pos >= PHYSICAL_LIST_READ_END] == expected_reads
        assert [(pc, pos, value) for pc, pos, value in memory.writes if pos >= PHYSICAL_LIST_READ_END] == expected_writes
        wanted_keys = [key for key in reversed(keys[:-1]) if group[key] == 0x40]
        wanted_keys += [key for key in keys[:-1] if group[key] != 0x40] + [last]
        actual = [word(memory, DRAW_LIST + 2 * index) for index in range(count + 1)]
        assert actual == [handlers[index] for index in wanted_keys] + [0x0101]
        assert max(pos for _, pos, _ in memory.reads) == end - 1
        assert max(pos for _, pos, _ in memory.writes) == end - 3
        cases.append(dict(entries=count, read_end_exclusive=end, write_end_exclusive=end - 2))
    assert cases[-1]['read_end_exclusive'] == 0xF4DC
    return dict(cases=cases, maximum_tested_entries=63, actual_wrappers_and_flags=True,
                repeated_original_pointers_supplied=True, original_bytes_from_0xF4BA_read=34,
                original_bytes_from_0xF4BA_written=32, draw_callbacks_executed=False,
                actual_game_path_with_repeated_pointers_proved=False)


def main():
    memory = DrawMemory()
    station = payload(4)
    put(memory, 0x6000, station)
    cpu = WatchedCPU(memory, {'PC': 0x6300, 'SP': 0x5FFF, 'IY': 0x5C3A},
                     config={'fast_ldir': False, 'fast_djnz': False})
    registers = cpu.registers
    memory.registers = registers
    boot = trace(['--region', 'station', '--frames', '8'], boot_simulator=cpu, save_reports=False)
    assert boot['reason'] == 'requested_frame_entries' and len(draw_list(memory)) == 10
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    flow = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    functions = json.loads((ROOT / 'Tools/Disasm/Reports/Functions.json').read_bytes())

    def invoke(name, hl=None, de=None):
        registers[PC], registers[SP] = symbols[f'Station.{name}.Entry'], 0x5FFD
        if hl is not None:
            registers[H], registers[L] = divmod(hl, 256)
        if de is not None:
            registers[D], registers[E] = divmod(de, 256)
        put(memory, 0x5FFD, b'\xFF\x3F')
        cpu.set_tracer(PortTrace(cpu))
        run_to(cpu, 0x3FFF)
        assert registers[SP] == 0x5FFF and memory.o7ffd == 0x10

    def remove_last(kind, expected_count):
        current = draw_list(memory)
        assert len(current) == expected_count
        address, _, index = current[-1]
        begin, end = address + 2, address + 130
        original = bytes(memory[begin:end])
        assert original[FIRST - begin:] == station[FIRST - 0x6000:end - 0x6000] == bytes(end - FIRST)
        memory.reads.clear()
        memory.writes.clear()
        invoke('RemoveItemDraw', de=index)
        assert draw_list(memory) == current[:-1]
        assert bytes(memory[address:address + 128]) == original
        assert [(pc, pos, byte) for pc, pos, byte in memory.reads if pos >= FIRST] == [
            (0xCB48, pos, original[pos - begin]) for pos in range(FIRST, end)]
        assert [(pc, pos, byte) for pc, pos, byte in memory.writes if pos >= FIRST] == [
            (0xCB48, pos, original[pos - address]) for pos in range(FIRST, end - 2)]
        return dict(kind=kind, entries=expected_count, removed_index=index, read_end_exclusive=end,
                    write_end_exclusive=end - 2)

    periodic_references = check_periodic_list_references(flow, memory)
    periodic_removals = check_periodic_removal_paths(memory, cpu, symbols, invoke)
    for name, length, item in zip(OPENERS, LENGTHS, LAST_INDICES):
        invoke(name)
        active = draw_list(memory)
        assert len(active) == length and active[-1][2] == item
    assert not [pos for _, pos, _ in memory.reads + memory.writes if pos >= FIRST]
    combined = remove_last('combined_original_openers', 39)

    # Добавление отсутствующих записей через их реальные обёртки с индексами загрузчика.
    active = {index for _, _, index in draw_list(memory)}
    appended = []
    handlers = []
    for index in range(46):
        handler = word(memory, 0xF0FD + 16 * index + 12)
        assert 0x4000 <= handler < 0xF000 and word(memory, handler + 1) == index
        handlers.append(handler)
        if index in active:
            continue
        invoke('RestoreItemBounds', hl=handler)
        appended.append(index)
    assert {index for _, _, index in draw_list(memory)} == set(range(46))
    # Проверка повторных вызовов, каждый индекс переносится в конец без добавления дубля.
    for index, handler in enumerate(handlers):
        before = [(target, key) for _, target, key in draw_list(memory)]
        position = next(i for i, (_, key) in enumerate(before) if key == index)
        before.append(before.pop(position))
        memory.reads.clear()
        memory.writes.clear()
        invoke('RestoreItemBounds', hl=handler)
        assert [(target, key) for _, target, key in draw_list(memory)] == before
        assert all(address < 0xF4BA for _, address, _ in memory.reads + memory.writes)
    full = remove_last('all_46_physical_handlers', 46)
    assert (combined['read_end_exclusive'], full['read_end_exclusive']) == (0xF4AC, 0xF4BA)
    rebuild = check_rebuild_limit(memory, cpu, handlers, symbols, station)
    report = dict(passed=True, combined=combined, all_handlers=full,
                  rebuild_at_structural_limit=rebuild,
                  popup_removal_at_structural_limit=check_popup_tail(memory, cpu, handlers, symbols, station),
                  literal_bounds_restore_sources=check_literal_openers(handlers, symbols, flow),
                  list_entry_references=check_list_entry_references(flow, functions),
                  periodic_list_references=periodic_references, periodic_panel_removals=periodic_removals,
                  unique_list_move_and_remove=check_unique_list_positions(memory, cpu, handlers, symbols),
                  openers=list(OPENERS), observed_lengths=list(LENGTHS), appended_indices=appended,
                  original_wrappers_requeued_without_duplicate=len(handlers),
                  original_bytes_beyond_previous_boundary=full['read_end_exclusive'] - FIRST,
                  all_46_handlers_simultaneously_reachable_in_game_proved=False,
                  disk_calls_substituted=True, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/StationCombinedDrawTailVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
