"""Исходные открыватели панелей, порядок ключей и физический хвост списка."""
import json

from CheckInitialZeroTailAccesses import WatchedCPU
from CheckScreenUpdate import PortTrace
from CheckStationCombinedDrawTail import DRAW_LIST, OPENERS
from CheckStationExpandedDrawTail import DrawMemory, draw_list, word
from CheckStationFlightCycle import ROOT, payload, put, run_to
from TraceFlight import A, PC, SP, main as trace
from skoolkit.simutils import F


END = 0xF4DE
MARKER = b'\x01\x01'
PERIODIC = 0x9A89


def reference_move(raw, keys, handler, key):
    if key in keys:
        reference_remove(raw, keys, key)
    index = 2 * len(keys)
    raw[index:index + 4] = handler.to_bytes(2, 'little') + MARKER
    keys.append(key)


def reference_remove(raw, keys, key):
    index = keys.index(key) * 2
    raw[index:index + 128] = raw[index + 2:index + 130]
    keys.remove(key)


def check_popup_sequence(memory, invoke, symbols, handlers):
    def keys():
        return [index for _, _, index in draw_list(memory)]

    initial = keys()
    assert len(initial) == 39 and 44 in initial
    rows = []

    def step(name, after, *, accumulator=0, flags=0):
        before = keys()
        visited = invoke(name, accumulator=accumulator, flags=flags)
        assert keys() == after
        assert 1 not in after and len(after) == len(set(after))
        rows.append(dict(entry=name, entries=len(after), added=[key for key in after if key not in before],
                         removed=[key for key in before if key not in after],
                         last_read=max((address for _, address, _ in memory.reads), default=0),
                         last_write=max((address for _, address, _ in memory.writes), default=0)))
        return visited

    raw = bytes(memory[DRAW_LIST:END])
    counter = step('DrawItem01', initial)
    assert symbols['Station.DrawGlyph.Entry'] in counter
    assert bytes(memory[DRAW_LIST:END]) == raw
    step('OpenGalaxyNewsPanel', initial + [24])
    current = initial + [24, 35, 34]
    step('OpenTradePanels', current)

    # Указатель в знакоместе без владельца, событие 1 открывает меню.
    put(memory, 0x6307, (16, 16))
    memory[0x8642] = 0
    step('DispatchInterfaceEvent', current + [40], accumulator=1)
    step('QueueTextRow', current + [40, 10], accumulator=11)

    # Подготовленный результат определения владельца, A=2 даёт селектор действия 1.
    put(memory, 0x6307, (32, 75))
    memory[0x8724] = 1
    put(memory, 0x8500, (40, 0))
    memory[0x9A82] = 1
    current = [key for key in current if key != 44]
    suppressed = step('DispatchInterfaceEvent', current + [40], accumulator=2)
    menu_action = symbols['Station.ActivateContextMenu.Entry']
    assert menu_action not in suppressed and memory[0x9A82] == 0
    assert word(memory, 0x9E31) == 40

    # После перестроения снова доступно событие, наведение уже выбрало строку сохранения.
    memory[0x9A82], memory[0x757A] = 1, 7
    clicked = step('DispatchInterfaceEvent', current + [43], accumulator=2)
    assert menu_action in clicked and handlers[40] not in clicked
    assert memory[0x9A82] == 0

    put(memory, 0x6307, (16, 16))
    memory[0x8642] = 0
    step('DispatchInterfaceEvent', current + [43, 40], accumulator=1)
    step('QueueTextRow', current + [43, 40, 10], accumulator=11)
    assert set(keys()) == set(range(46)) - {1, 44}
    step('DispatchInterfaceEvent', current, accumulator=2)
    assert word(memory, 0x9E31) == 0xFFF0

    maximum_entries = max(row['entries'] for row in rows)
    last_read = max(row['last_read'] for row in rows)
    last_write = max(row['last_write'] for row in rows)
    assert (maximum_entries, last_read, last_write) == (44, 0xF4B3, 0xF4B1)
    return dict(steps=rows, maximum_entries=maximum_entries,
                maximum_read_address=last_read, maximum_write_address=last_write,
                first_selected_event_suppressed=True, prepared_owner_cells=True,
                prepared_event_enabled_after_cleanup=True, prepared_save_hover_row=True)


def check_openers():
    memory = DrawMemory()
    put(memory, 0x6000, payload(4))
    cpu = WatchedCPU(memory, {'PC': 0x6300, 'SP': 0x5FFF, 'IY': 0x5C3A},
                     config={'fast_ldir': False, 'fast_djnz': False})
    registers = cpu.registers
    memory.registers = registers
    boot = trace(['--region', 'station', '--frames', '8'], boot_simulator=cpu, save_reports=False)
    assert boot['reason'] == 'requested_frame_entries' and memory.o7ffd == 0x10
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    handlers = [word(memory, 0xF109 + 16 * key) for key in range(46)]
    assert all(word(memory, handler + 1) == key for key, handler in enumerate(handlers))
    assert len(set(handlers)) == 46
    start = [key for _, _, key in draw_list(memory)]
    assert len(start) == 10 and len(set(start)) == 10

    def snapshot():
        return tuple(bytes(bank) for bank in memory.banks), registers[:]

    def restore(state):
        banks, values = state
        for bank, saved in zip(memory.banks, banks):
            bank[:] = saved
        memory.out7ffd(0x10)
        registers[:] = values

    def invoke(name, *, accumulator=None, flags=0):
        registers[PC], registers[SP] = symbols[f'Station.{name}.Entry'], 0x5FFD
        if accumulator is not None:
            registers[A], registers[F] = accumulator, flags
        put(memory, 0x5FFD, b'\xFF\x3F')
        cpu.set_tracer(PortTrace(cpu))
        memory.reads.clear()
        memory.writes.clear()
        visited = set()
        run_to(cpu, 0x3FFF, visited.add if accumulator is not None else None)
        assert registers[SP] == 0x5FFF and memory.o7ffd == 0x10
        assert word(memory, 0x9CA6) == DRAW_LIST
        assert [word(memory, 0xF109 + 16 * key) for key in range(46)] == handlers
        assert all(word(memory, handler + 1) == key for key, handler in enumerate(handlers))
        return visited

    initial = snapshot()
    groups = []
    for name in OPENERS:
        restore(initial)
        invoke(name)
        after = [key for _, _, key in draw_list(memory)]
        # Каждый открыватель переносит свою группу в конец, исходные десять ключей остаются на месте.
        assert after[:len(start)] == start
        groups.append(after[len(start):])
    assert sum(map(len, groups)) == 29 and len({key for group in groups for key in group}) == 29

    memory.active = True
    states = {0: initial}
    opens = repeats = closes = maximum_length = 0
    last_read = last_write = 0
    for mask in range(1 << len(OPENERS)):
        state = states.pop(mask)
        wanted_before = set(start)
        for bit, members in enumerate(groups):
            if mask & (1 << bit):
                wanted_before.update(members)
        for index, (name, group) in enumerate(zip(OPENERS, groups, strict=True)):
            restore(state)
            expected = bytearray(memory[DRAW_LIST:END])
            keys = [key for _, _, key in draw_list(memory)]
            assert set(keys) == wanted_before and len(keys) == len(wanted_before)
            for key in group:
                reference_move(expected, keys, handlers[key], key)
            invoke(name)
            assert bytes(memory[DRAW_LIST:END]) == expected
            assert [key for _, _, key in draw_list(memory)] == keys
            maximum_length = max(maximum_length, len(keys))
            last_read = max(last_read, max((address for _, address, _ in memory.reads), default=0))
            last_write = max(last_write, max((address for _, address, _ in memory.writes), default=0))
            next_mask = mask | (1 << index)
            if next_mask == mask:
                repeats += 1
            else:
                opens += 1
                if next_mask not in states:
                    states[next_mask] = snapshot()

        restore(state)
        keys = [key for _, _, key in draw_list(memory)]
        expected = bytearray(memory[DRAW_LIST:END])
        for key in keys.copy():
            flags = memory[0xF101 + 16 * key]
            if not (flags & 0xC0) or flags & 0x60 == 0x60:
                reference_remove(expected, keys, key)
        invoke('CloseAllItems')
        assert [key for _, _, key in draw_list(memory)] == keys
        assert bytes(memory[DRAW_LIST:END]) == expected
        assert word(memory, PERIODIC) == symbols['Station.EmptyCallback.Entry']
        last_read = max(last_read, max((address for _, address, _ in memory.reads), default=0))
        last_write = max(last_write, max((address for _, address, _ in memory.writes), default=0))
        closes += 1

    assert not states and (opens, repeats, closes) == (1024, 1024, 256)
    assert maximum_length == 39 and (last_read, last_write) == (0xF4AB, 0xF4A9)
    restore(state)
    popup_sequence = check_popup_sequence(memory, invoke, symbols, handlers)
    return dict(initial_indices=start, groups=dict(zip(OPENERS, groups, strict=True)),
                tested_group_sets=closes, first_opens=opens, repeated_opens=repeats,
                close_all_cases=closes, maximum_list_length=maximum_length,
                maximum_read_address=last_read, maximum_write_address=last_write,
                popup_sequence=popup_sequence)


def main():
    result = dict(passed=True, **check_openers(), original_entry_points=True,
                  one_concrete_order_per_group_set=True, group_openers_execute_draw_callbacks=False,
                  counter_renderer_executed=True,
                  disk_reads_substituted_during_boot=True, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/StationDrawOpenerCompositionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
