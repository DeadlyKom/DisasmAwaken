"""Исходный архивный потребитель заголовков, кадров BAR и масок BD."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckControlsLegacySectorRead import run_with_rom
from CheckScene1ArchiveConsumer import FIXED_OFFSET, RETURN_SENTINEL, start_call
from CheckStationFlightCycle import DISK, ENTRIES, payload, put, run_to
from FighterAssetData import decode
from TraceFlight import A, B, C, H, IFF, L, PC, SP, T, ROOT, Simulator
from skoolkit.simutils import I, IM


STATE = 0x4842
SECOND_STATE = 0x4895
SCENE = 0x7700
ROW_BYTES = 92


class FighterBootMemory(ExtendedMemory):
    def __init__(self):
        super().__init__()
        self.scene_copy_reads = Counter()

    def __getitem__(self, address):
        if isinstance(address, int) and address >= 0xC000 and self.o7ffd & 0x47 in (0x45, 0x46):
            page = (self.o7ffd & 7) + 8
            self.scene_copy_reads[page, self.cpu.registers[PC], address] += 1
        return super().__getitem__(address)


def word(memory, address):
    return int.from_bytes(memory[address:address + 2], 'little')


def check_scene_restore(sprites):
    memory = FighterBootMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    put(memory, 0x4FB6, memory[0x5018:0x501A])
    scene = payload(30)
    put(memory, SCENE, scene)
    cpu = Simulator(memory)
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    start_call(cpu, 0x492D)
    run_to(cpu, RETURN_SENTINEL)
    initial = bytes(value ^ 255 for value in scene)
    original_copies = bytes(memory.banks[13]), bytes(memory.banks[14])
    cases = Counter()
    physical_sizes = {(sprite[2], sprite[3]) for sprite in sprites}
    for width, height in sorted(physical_sizes | {(1, 1)}):
        assert height <= 203 and 0 < width <= 90
        top_positions = {0, min(178 - height // 2, 203 - height), min(178, 203 - height)}
        for top, column, mirror, view_y in product(sorted(top_positions), (0, 29, 90 - width), (0, 1), (0, 11)):
            put(memory, SCENE, initial)
            memory[0x4A59] = view_y
            memory[STATE + 7] = width
            memory[STATE + 9] = height
            memory[STATE + 0x13] = mirror
            memory[STATE + 0x16] = (top - view_y) & 255
            destination = SCENE + top * ROW_BYTES + column
            put(memory, STATE + 0x0B, (destination + mirror * (width - 1)).to_bytes(2, 'little'))
            expected = bytearray(initial)
            expected_reads = Counter()
            for row in range(top, top + height):
                offset = row * ROW_BYTES + column
                expected[offset:offset + width] = scene[offset:offset + width]
                page, source = (13, 0xC000 + offset) if row < 178 else (
                    14, 0xC054 + (row - 178) * ROW_BYTES + column)
                expected_reads.update((page, 0x472C, address) for address in range(source, source + width))
            memory.scene_copy_reads.clear()
            ports.pages.clear()
            start_call(cpu, 0x46EE, IX=STATE)
            cpu.run(start=0x46EE, stop=RETURN_SENTINEL)
            assert memory.scene_copy_reads == expected_reads, (top, column, width, height, mirror)
            assert bytes(memory[SCENE:SCENE + len(scene)]) == expected
            assert tuple(bytes(memory.banks[page]) for page in (13, 14)) == original_copies
            switched = top + height > 178
            assert ports.pages == ([0x5D, 0x5E] if switched else [0x5D])
            assert cpu.registers[SP] == 0x5BFE
            cases['switches_to_page_14' if switched else 'page_13_only'] += 1
            cases['starts_at_row_178'] += top == 178
    assert cases['switches_to_page_14'] and cases['starts_at_row_178']
    return dict(cases=dict(cases), source_split_row=178, actual_restoration_entry=0x46EE,
                exact_read_bytes_and_fixed_destination=True, expanded_copies_unchanged=True,
                physical_sprite_sizes=len(physical_sizes), synthetic_one_byte_edge_profile=True,
                both_sprite_orientations=True)


def service_requests(cpu, requests, roms=None, *, advance=run_to):
    memory, registers = cpu.memory, cpu.registers
    archive_ports = cpu.tracer
    disk_ports = BasicReadPorts(memory) if roms is not None else None
    results = []

    def set_rom(image):
        memory.memory[0] = image

    for slot, page, address in requests:
        advance(cpu, 0x3D13)
        assert (registers[A], registers[C], registers[H] * 256 + registers[L]) == (255, 0x0E, address)
        assert memory.o7ffd == page
        key = bytes(memory[0x5CDD:0x5CE6])
        assert key == DISK[16 * slot:16 * slot + 9]
        data = payload(slot)
        stack = registers[SP]
        continuation = word(memory, stack)
        physical_reads = None
        if roms is None:
            put(memory, address, data)
            registers[PC] = continuation
            registers[SP] += 2
        else:
            basic, dos = roms
            full_sectors, final_bytes = divmod(len(data), 256)
            assert final_bytes and full_sectors + 1 == ENTRIES[slot]['sector_count']
            end = address + len(data)
            end_of_sector = end + 256 - final_bytes
            tail = bytes(memory[end:end_of_sector])
            cursor = len(disk_ports.read_destinations)
            cpu.set_tracer(disk_ports)
            set_rom(basic)
            run_with_rom(cpu, basic, dos, set_rom, continuation)
            cpu.set_tracer(archive_ports)
            assert bytes(memory[end:end_of_sector]) == tail
            targets = [address + 256 * i for i in range(full_sectors)] + [0x5D25]
            first = ENTRIES[slot]['offset'] // 256
            expected = [(divmod(index, 16), target) for index, target in enumerate(targets, first)]
            physical_reads = [(sector, addr) for sector, addr in disk_ports.read_destinations[cursor:] if sector[0]]
            assert physical_reads == [((track, sector + 1), target) for (track, sector), target in expected]
        assert bytes(memory[address:address + len(data)]) == data and memory.o7ffd == page
        results.append(dict(slot=slot, key=key.decode('ascii'), address=address, port_value=page,
                            physical_sectors=len(physical_reads) if physical_reads is not None else None,
                            final_sector_read=physical_reads[-1] if physical_reads is not None else None))
    return results


def check_headers(cpu, bar, pointers, groups):
    memory = cpu.memory
    memory.out7ffd(0x18)
    indexed = {offset: index for index, offset in enumerate(pointers)}
    for group in groups:
        start = group['offset']
        count, flags, repeat_index, next_action = bar[start:start + 4]
        action = indexed.get(start)
        if action is not None:
            memory[STATE + 5] = action
            memory[STATE + 6] = 255
            start_call(cpu, 0x427B, IX=STATE)
            run_to(cpu, 0x4309)
            assert tuple(memory[STATE + off] for off in (0x18, 0x1D, 0x48, 0x4F)) == (
                count, flags, repeat_index, next_action)
            assert word(memory, STATE + 0x19) == 0xC000 + start + 4
        memory[STATE + 5] = memory[STATE + 6] = 0
        memory[STATE + 0x10] = 1
        memory[STATE + 0x0F] = count - 1
        for offset, value in zip((0x18, 0x1D, 0x48, 0x4F), (count, flags, repeat_index, next_action)):
            memory[STATE + offset] = value
        start_call(cpu, 0x41F8, IX=STATE)
        run_to(cpu, RETURN_SENTINEL)
        assert memory[STATE + 0x4D] == 1 and memory[STATE + 0x10] == 0
        assert (memory[STATE + 0x0F], memory[STATE + 5]) == (
            (repeat_index, 0) if flags & 0x40 else (0, next_action))


def check_steps(cpu, bar, groups):
    memory = cpu.memory
    put(memory, 0x4A57, (0x7720).to_bytes(2, 'little'))
    memory[0x4A59] = 11
    cases = 0
    for group in groups:
        put(memory, STATE + 0x19, (0xC000 + group['offset'] + 4).to_bytes(2, 'little'))
        for index, record in enumerate(group['records']):
            offset = record['offset']
            row = bar[offset:offset + 14]
            step_x, step_y, offset_x, offset_y = (word(row, i) for i in (1, 3, 5, 7))
            for mirror in (0, 1):
                direction = -1 if mirror else 1
                memory[STATE] = mirror
                memory[STATE + 0x0F] = index
                memory[STATE + 0x14] = (45 - direction * step_x) & 255
                memory[STATE + 0x15] = 16
                start_call(cpu, 0x4309, IX=STATE)
                run_to(cpu, RETURN_SENTINEL)
                x, y = (45 + direction * offset_x) & 255, (16 + step_y + offset_y) & 255
                assert (memory[STATE + 0x14], memory[STATE + 0x15]) == (45, (16 + step_y) & 255)
                assert (memory[STATE + 0x1B], memory[STATE + 0x1C]) == (x, y)
                assert word(memory, STATE + 0x50) == step_x
                assert memory[STATE + 0x10] == row[0]
                assert (memory[STATE + 0x17], word(memory, STATE + 1),
                        memory[STATE + 0x11], memory[STATE + 0x12]) == (
                            record['bank'], record['address'], record['width'], record['height'])
                assert word(memory, STATE + 3) == (SCENE + ROW_BYTES * ((y + 11) & 255) + x) & 65535
                cases += 1
    return cases


def check_masks(cpu, banks, sprites):
    memory = cpu.memory
    start_call(cpu, 0x46C4)
    run_to(cpu, RETURN_SENTINEL)
    reverse = bytes(int(f'{value:08b}'[::-1], 2) for value in range(256))
    assert bytes(memory[0x7600:0x7700]) == reverse
    cases = 0
    for bank, offset, width, height in sprites:
        data = banks[bank][offset:offset + 2 * width * height]
        for state, side in product((STATE, SECOND_STATE), (0, 1, 0x80)):
            mirror = bool(side)
            initial = bytes((index * 23 + bank * 41) & 255 for index in range(height * ROW_BYTES))
            put(memory, SCENE, initial)
            wanted = bytearray(initial)
            for y in range(height):
                for x in range(width):
                    source = 2 * (y * width + x)
                    mask, pixels = data[source:source + 2]
                    column = x
                    if mirror:
                        mask, pixels, column = reverse[mask], reverse[pixels], width - 1 - x
                    dest = y * ROW_BYTES + column
                    wanted[dest] = (initial[dest] & mask) | pixels
            memory[state] = side
            destination = (SCENE + (width - 1 if mirror else 0)).to_bytes(2, 'little')
            put(memory, state + 1, (0xC000 + offset).to_bytes(2, 'little'))
            put(memory, state + 3, destination)
            memory[state + 0x17] = bank
            memory[state + 0x11], memory[state + 0x12] = width, height
            memory[state + 0x1C] = (offset + 19 * side) & 255
            other = SECOND_STATE if state == STATE else STATE
            other_before = bytes(memory[other:other + 0x53])
            record = bytearray(memory[state:state + 0x53])
            record[0x0B:0x0D] = destination
            record[0x07], record[0x09], record[0x13], record[0x16] = width, height, side, record[0x1C]
            start_call(cpu, 0x4753, IX=state)
            run_to(cpu, RETURN_SENTINEL)
            assert bytes(memory[SCENE:SCENE + len(wanted)]) == wanted, (bank, offset, mirror)
            assert bytes(memory[state:state + 0x53]) == record
            assert bytes(memory[other:other + 0x53]) == other_before
            assert memory.o7ffd == 0x58 + bank
            cases += 1
    return cases


def check_frame_counters(cpu):
    memory = cpu.memory
    cases = 0
    for state, new_request, flags, index in product(
            (STATE, SECOND_STATE), (False, True), (0, 0x40, 0xA5, 0xE5), (0, 3, 0xFF)):
        initial = bytearray(memory[state:state + 0x53])
        initial[5], initial[6] = (2 if new_request else 0), 0
        initial[0x0F], initial[0x18], initial[0x1D] = index, 4, flags
        initial[0x48], initial[0x4D], initial[0x4F] = 1, 0x80, 7
        for delay in range(256):
            initial[0x10] = delay
            put(memory, state, initial)
            expected = initial.copy()
            if new_request:
                expected[0x4D] = 1
            else:
                expected[0x10] = (delay - 1) & 255
                if delay == 1:
                    expected[0x4D] = 1
                    next_index = (index + 1) & 255
                    if next_index >= 4:
                        if flags & 0x40:
                            next_index = 1
                        else:
                            next_index, expected[5] = 0, 7
                    expected[0x0F] = next_index
            start_call(cpu, 0x41F8, IX=state)
            run_to(cpu, RETURN_SENTINEL)
            assert bytes(memory[state:state + 0x53]) == expected
            cases += 1
    return cases


def check_action_switches(cpu, bar, pointers):
    memory = cpu.memory
    memory.out7ffd(0x18)
    cases = inverse_cases = 0
    for state in (STATE, SECOND_STATE):
        base = 0xC000 if state == STATE else 0xD000
        initial = bytearray(memory[state:state + 0x53])
        initial[0x0D:0x0F] = base.to_bytes(2, 'little')
        for requested, index, pending, turn in product(range(36), (0, 1, 7, 8, 9, 10, 255), (0, 0x80), (0, 1)):
            for loaded in sorted({0, 1, 2, requested, 255}):
                initial[0], initial[5], initial[6] = int(state == SECOND_STATE), requested, loaded
                initial[0x0F], initial[0x4D], initial[0x52] = index, pending, turn
                put(memory, state, initial)
                expected = initial.copy()
                if requested != loaded:
                    offset = pointers[requested]
                    count, flags, repeat, next_action = bar[offset:offset + 4]
                    reflected = (requested, loaded) in ((1, 2), (2, 1))
                    new_index = min(8, (9 - index) & 255) if reflected else index if 28 <= requested <= 33 else 0
                    expected[0] ^= (requested == 35) ^ bool(turn)
                    expected[6], expected[0x0F], expected[0x18] = requested, new_index, count
                    expected[0x19:0x1B] = (base + offset + 4).to_bytes(2, 'little')
                    expected[0x1D], expected[0x48], expected[0x4F] = flags, repeat, next_action
                    expected[0x4D], expected[0x52] = 0, 0
                    target = 0x4309
                else:
                    expected[0x4D] = 0
                    target = 0x4309 if pending else RETURN_SENTINEL
                start_call(cpu, 0x427B, IX=state)
                run_to(cpu, target)
                assert bytes(memory[state:state + 0x53]) == expected, (state, requested, loaded, index, pending, turn)
                cases += 1

        for (entry, request, required_loaded), index, matches in product(
                ((0x424E, 2, 1), (0x4258, 1, 2)), range(256), (False, True)):
            memory[state + 6], memory[state + 0x0F] = (required_loaded if matches else 0xFF), index
            start_call(cpu, entry, IX=state, AF=request << 8, BC=0xA5FE)
            run_to(cpu, RETURN_SENTINEL)
            assert cpu.registers[B] == (min(8, (9 - index) & 255) if matches else 0xA5)
            assert cpu.registers[A] == cpu.registers[C] == request
            inverse_cases += 1
    return dict(group_switches=cases, index_reversal_cases=inverse_cases)


def check_horizontal_edges(cpu, bar, groups):
    memory = cpu.memory
    opponent_xor = STATE ^ SECOND_STATE
    put(memory, 0x503E, opponent_xor.to_bytes(2, 'little'))
    memory[0x4A4F] = 58
    paths = dict(interior=0, left_held=0, left_scrolled=0, left_at_limit=0,
                 right_held=0, right_scrolled=0, right_at_limit=0)
    for group in groups:
        for index, record in enumerate(group['records']):
            offset = record['offset']
            step_x, draw_x = (word(bar, offset + delta) for delta in (1, 5))
            for state, opponent, direction in ((STATE, SECOND_STATE, 1), (SECOND_STATE, STATE, -1)):
                memory[state] = int(direction < 0)
                memory[state + 0x0F] = index
                put(memory, state + 0x19, (0xC000 + group['offset'] + 4).to_bytes(2, 'little'))
                for viewport in (0, 32, 58, 245):
                    left = (viewport + 3) & 255
                    right = (left + 24) & 255
                    for candidate in (0, 255, left, (left + 1) & 255, right, (right + 1) & 255):
                        before = (candidate - direction * step_x) & 255
                        separation = (candidate + 23 if candidate <= left else candidate - 23) & 255
                        for other in {separation, max(0, separation - 1), min(255, separation + 1)}:
                            expected_view, expected_x = viewport, before
                            if candidate <= left:
                                if separation < other:
                                    path = 'left_held'
                                else:
                                    expected_view = max(0, viewport - 1)
                                    expected_x = (expected_view + 4) & 255
                                    path = 'left_scrolled' if viewport else 'left_at_limit'
                            elif candidate > right:
                                if separation >= other:
                                    path = 'right_held'
                                else:
                                    expected_view = viewport + int(viewport < 58)
                                    expected_x = (expected_view + 27) & 255
                                    path = 'right_scrolled' if viewport < 58 else 'right_at_limit'
                            else:
                                path, expected_x = 'interior', candidate
                            memory[0x4A57], memory[0x4A58] = viewport, 0x77
                            memory[state + 0x14], memory[state + 0x15] = before, 16
                            memory[opponent + 0x14] = other
                            start_call(cpu, 0x4309, IX=state)
                            run_to(cpu, RETURN_SENTINEL)
                            assert word(memory, 0x4A57) == 0x7700 + expected_view, (path, viewport, candidate, other)
                            assert memory[state + 0x14] == expected_x, (path, viewport, candidate, other)
                            assert memory[state + 0x1B] == (expected_x + direction * draw_x) & 255
                            assert memory[opponent + 0x14] == other
                            paths[path] += 1
    assert all(paths.values()), paths
    return paths


def check_view_adjustments(cpu):
    memory = cpu.memory
    cases = 0
    for entry, field, maximum, increasing in ((0x48E8, 0x4A57, 0x4A4F, True),
                                               (0x48F5, 0x4A55, 0x4A53, True),
                                               (0x4902, 0x4A55, 0x4A53, False),
                                               (0x490C, 0x4A57, 0x4A4F, False)):
        bounds = (0, memory[maximum], 0x80, 0xFF) if increasing else (memory[maximum],)
        for limit in bounds:
            memory[maximum], memory[maximum + 1] = limit, 0xD5
            for initial in range(256):
                memory[field], memory[field + 1] = initial, 0xA7
                start_call(cpu, entry)
                run_to(cpu, RETURN_SENTINEL)
                expected = initial + (initial < limit) if increasing else max(0, initial - 1)
                assert memory[field] == expected and memory[field + 1] == 0xA7
                cases += 1
    return cases


def check_keyboard_actions(cpu, action_count):
    memory, ports = cpu.memory, cpu.tracer
    key_profiles = (
        (STATE, ((0xFBFE, 2), (0xFDFE, 2), (0xFDFE, 4), (0xFDFE, 1), (0xFEFE, 16)),
         ((0xFEFE, 8), (0xFDFE, 8), (0x7FFE, 16), (0xFDFE, 16))),
        (SECOND_STATE, ((0xEFFE, 8), (0xDFFE, 8), (0xDFFE, 4), (0xDFFE, 16), (0xBFFE, 1)),
         ((0xBFFE, 4), (0xDFFE, 2), (0xBFFE, 2), (0xDFFE, 1))),
    )
    scan_cases = 0
    for state, primary_keys, secondary_keys in key_profiles:
        for mirrored in (0, 1):
            memory[state] = mirrored
            keys = list(primary_keys)
            if mirrored:
                keys[2], keys[3] = keys[3], keys[2]
            for key in (None, *keys, *secondary_keys):
                memory[state + 0x49], memory[state + 0x4A] = 0x80, 0x40
                ports.menu_key = key
                start_call(cpu, 0x4439, IX=state)
                run_to(cpu, RETURN_SENTINEL)
                primary = 1 << keys.index(key) if key in keys else 0
                secondary = 1 << secondary_keys.index(key) if key in secondary_keys else 0
                assert (memory[state + 0x49], memory[state + 0x4A]) == (0x80 | primary, 0x40 | secondary)
                scan_cases += 1
    ports.menu_key = None

    table = 0x44DE
    assert all(word(memory, state + 0x4B) == table for state, _, _ in key_profiles)
    blocks = {}
    action_rules = []
    for action in range(action_count):
        address = word(memory, table + 2 * action)
        count = memory[address]
        rules = tuple(tuple(memory[address + 1 + 5 * i:address + 6 + 5 * i]) for i in range(count))
        assert all(len(rule) == 5 and rule[-1] < action_count for rule in rules)
        blocks[address] = count
        action_rules.append(rules)

    cases = 0
    for state, _, _ in key_profiles:
        for action, rules in enumerate(action_rules):
            for primary in range(32):
                for secondary in range(16):
                    for previous in (secondary, secondary ^ 1):
                        fresh = secondary if secondary != previous else 0
                        expected = next((target for pm, pv, sm, sv, target in rules
                                         if primary & pm == pv and fresh & sm == sv), action)
                        memory[state + 5] = action
                        memory[state + 0x49], memory[state + 0x4A] = primary, secondary
                        memory[state + 0x4E] = previous
                        start_call(cpu, 0x448B, IX=state)
                        run_to(cpu, RETURN_SENTINEL)
                        assert memory[state + 5] == expected, (state, action, primary, secondary, previous)
                        assert (memory[state + 0x49], memory[state + 0x4A], memory[state + 0x4E]) == (0, 0, secondary)
                        cases += 1
    return dict(scan_cases=scan_cases, dispatch_cases=cases, action_table=table,
                indexed_actions=action_count, physical_rule_blocks=blocks,
                physical_rules=sum(blocks.values()),
                action_rules=[[list(rule) for rule in rules] for rules in action_rules])


def check_relative_positions(cpu, action_count):
    memory = cpu.memory
    state_pair = (STATE, SECOND_STATE)
    turn_now = {0, 1, 2, 4, 9, 11}
    positions = ((0, 0), (0, 1), (34, 38), (34, 39), (38, 34), (39, 34), (255, 255))
    crossing_cases = 0
    for (first, second), orientation, action in product(positions, product((0, 1), repeat=2), range(action_count)):
        for state, side, x, y in zip(state_pair, orientation, (first, second), (8, 9)):
            memory[state] = side
            memory[state + 5] = action
            memory[state + 0x14], memory[state + 0x15] = x, y
            memory[state + 0x52] = 0
        start_call(cpu, 0x4178)
        run_to(cpu, RETURN_SENTINEL)
        for state, side, own, other in zip(state_pair, orientation, (first, second), (second, first)):
            faces_away = bool(side) == (own < other)
            requested = 34 if faces_away and action in turn_now else action
            pending = int(faces_away and action not in turn_now | {34, 35})
            assert (memory[state + 5], memory[state + 0x52]) == (requested, pending)
            assert memory[state] == side and memory[state + 0x14] == own
        crossing_cases += 1

    proximity_cases = 0
    for (first, second), movement in product(positions, product((0, 1), repeat=2)):
        for state, x, moved in zip(state_pair, (first, second), movement):
            memory[state + 0x14], memory[state + 0x15] = x, 8
            memory[state + 0x50] = moved
        start_call(cpu, 0x4178)
        run_to(cpu, RETURN_SENTINEL)
        direction = 1 if first >= second else -1
        expected = (first, second)
        if abs(first - second) < 5:
            expected = ((first + direction * movement[0]) & 255, (second - direction * movement[1]) & 255)
        assert tuple(memory[state + 0x14] for state in state_pair) == expected
        proximity_cases += 1

    vertical_cases = 0
    extents = ((0, 0), (150, 15), (150, 16), (150, 17), (172, 5), (200, 20), (255, 20))
    assert memory[0x4A53] == 11
    for pair in product(extents, repeat=2):
        for state, (y, height) in zip(state_pair, pair):
            memory[state + 0x14], memory[state + 0x15] = 20, 8
            memory[state + 0x50] = 0
            memory[state + 0x1C], memory[state + 0x12] = y, height
        memory[0x4A55] = 0xA5
        start_call(cpu, 0x415D)
        run_to(cpu, RETURN_SENTINEL)
        expected = min(11, max(0, max((y + height) & 255 for y, height in pair) - 166))
        assert memory[0x4A55] == expected
        vertical_cases += 1

    def call(address, state):
        start_call(cpu, address, IX=state)
        run_to(cpu, RETURN_SENTINEL)

    turn_cases = 0
    put(memory, 0x4A57, b'\x20\x77')
    for state, side in product(state_pair, (0, 1)):
        memory[state] = side
        memory[state + 0x14], memory[state + 0x15] = 45, 16
        memory[state + 5], memory[state + 6] = 34, 0
        memory[state + 0x52] = 0
        for action, successor, expected_side in ((34, 35, side), (35, 0, side ^ 1)):
            call(0x427B, state)
            assert (memory[state + 6], memory[state]) == (action, expected_side)
            ticks = memory[state + 0x10]
            assert ticks and memory[state + 0x18] == 1
            for _ in range(ticks):
                call(0x41F8, state)
            assert memory[state + 5] == successor
        call(0x427B, state)
        assert (memory[state + 6], memory[state]) == (0, side ^ 1)

        memory[state + 5] = 0
        memory[state + 0x52] = 1
        call(0x427B, state)
        assert (memory[state + 0x52], memory[state]) == (1, side ^ 1)
        memory[state + 5] = 1
        call(0x427B, state)
        assert (memory[state + 0x52], memory[state]) == (0, side)
        turn_cases += 1
    return dict(crossing_cases=crossing_cases, proximity_cases=proximity_cases, vertical_cases=vertical_cases,
                turn_cases=turn_cases, direct_turn_requests=sorted(turn_now), turn_action_sequence=[34, 35, 0])


def check_archive_boot(requests, rom_profile=None):
    memory = FighterBootMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    if rom_profile is not None:
        put(memory, 0x5C00, rom_profile[2])
        memory[0x5D06] = 9
    cpu = Simulator(memory, {'PC': 0x4000})
    memory.cpu = cpu
    cpu.set_tracer(ArchivePorts(memory))
    registers = cpu.registers
    loads = service_requests(cpu, requests, rom_profile[:2] if rom_profile is not None else None)
    run_to(cpu, 0x4030)
    assert (registers[I], registers[IM], registers[IFF], registers[SP]) == (0x5E, 2, 1, 0x6000)
    assert word(memory, 0x503E) == STATE ^ SECOND_STATE
    split_reads = Counter({(14, 0x4971, address): 1 for address in range(0xC000, 0xC050)})
    assert memory.scene_copy_reads == split_reads
    visited = set()
    frames = []
    for _ in range(64):
        assert registers[IFF]
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        assert cpu.accept_interrupt(registers, memory, 0x4048)
        run_to(cpu, 0x4030, visited.add)
        cpu.run()
        run_to(cpu, 0x4030, visited.add)
        assert registers[SP] == 0x6000 and memory.o7ffd == 0x1F
        frames.append(hashlib.sha256(memory.banks[7][:0x1800]).hexdigest())
    assert len(set(frames)) > 1 and {0x41E9, 0x427B, 0x46EE, 0x4753, 0x4974} <= visited

    def frame_with_key(key):
        cpu.tracer.menu_key = key
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        assert cpu.accept_interrupt(registers, memory, 0x4048)
        run_to(cpu, 0x4030)
        input_bits = tuple(memory[state + 0x49] for state in (STATE, SECOND_STATE))
        cpu.run()
        run_to(cpu, 0x4030)
        assert registers[SP] == 0x6000
        return input_bits

    key_cycles = []
    for state, key, row in ((STATE, (0xFDFE, 4), 0), (SECOND_STATE, (0xDFFE, 4), 1)):
        assert tuple(memory[record + 5] for record in (STATE, SECOND_STATE)) == (0, 0)
        expected_action = 2 if memory[state] else 1
        expected_bits = 8 if expected_action == 2 else 4
        inputs = frame_with_key(key)
        assert inputs[row] == expected_bits and inputs[1 - row] == 0, (state, inputs)
        assert memory[state + 5] == memory[state + 6] == expected_action
        assert frame_with_key(None) == (0, 0)
        assert memory[state + 5] == memory[state + 6] == 0
        key_cycles.append(dict(state=state, port=key[0], mask=key[1], primary_bits=expected_bits,
                               entered_action=expected_action, released_action=0))
    extra_reads = memory.scene_copy_reads - split_reads
    assert {(page, pc) for page, pc, _ in extra_reads} == {(13, 0x472C)}
    return dict(loads=loads, frame_entry=0x4030, complete_cycles=len(frames),
                screen_bitmap_sha256=frames, distinct_bitmap_count=len(set(frames)),
                opponent_state_xor=word(memory, 0x503E),
                expanded_scene_copy_reads_during_frame_cycles=sum(extra_reads.values()),
                expanded_scene_copy_read_page=13, expanded_scene_copy_read_instruction=0x472C,
                scene_split_reads_beyond_fixed_ram=len(split_reads),
                interrupts_scheduled_at_loop_boundaries=True, baseline_cycles_without_keys=True,
                key_cycles=key_cycles)


def main(report_name='FighterArchiveConsumerVerification.json'):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dos-rom', type=Path)
    args = parser.parse_args()
    memory = ExtendedMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    put(memory, 0x4FB6, memory[0x5018:0x501A])
    cpu = Simulator(memory)
    memory.cpu = cpu
    cpu.set_tracer(ArchivePorts(memory))
    bd_requests = [(40 + i, 0x58 + i, 0xC000) for i in range(4)]
    bar_requests = [(39, 0x18, 0xC000), (39, 0x18, 0xD000)]
    start_call(cpu, 0x469C)
    loads = service_requests(cpu, bd_requests)
    run_to(cpu, RETURN_SENTINEL)
    start_call(cpu, 0x466C)
    loads += service_requests(cpu, bar_requests)
    run_to(cpu, RETURN_SENTINEL)
    bar, banks = payload(39), [payload(i) for i in range(40, 44)]
    pointers, groups, sprites, _ = decode(bar, banks)
    check_headers(cpu, bar, pointers, groups)
    steps = check_steps(cpu, bar, groups)
    frame_counters = check_frame_counters(cpu)
    action_switches = check_action_switches(cpu, bar, pointers)
    horizontal_edges = check_horizontal_edges(cpu, bar, groups)
    keyboard_actions = check_keyboard_actions(cpu, len(pointers))
    relative_positions = check_relative_positions(cpu, len(pointers))
    masks = check_masks(cpu, banks, sprites)
    view_adjustments = check_view_adjustments(cpu)
    scene_restore = check_scene_restore(sprites)
    requests = bd_requests + [(30, 0x5B, 0x7700)] + bar_requests
    archive_boot = check_archive_boot(requests)
    real_boot = None
    if args.dos_rom is not None:
        basic, dos, sysvars = model_rom_context(args.dos_rom)
        real_boot = check_archive_boot(requests, (basic, dos, sysvars))
        assert real_boot['screen_bitmap_sha256'] == archive_boot['screen_bitmap_sha256']
        real_boot.update(dos_rom_sha256=hashlib.sha256(dos).hexdigest(), trdos_substituted=False,
                         bitmaps_match_stub_profile=True)
    result = dict(passed=True, original_sha256=hashlib.sha256(DISK).hexdigest(), loads=loads,
                  headers_executed=len(groups), indexed_group_loads=len(pointers),
                  step_cases=steps, frame_counter_cases=frame_counters, action_switches=action_switches,
                  mask_cases=masks, mask_cases_cover_both_fighter_records=True,
                  view_adjustment_cases=view_adjustments, archived_fighter_code=True,
                  horizontal_edge_cases=sum(horizontal_edges.values()), horizontal_edge_paths=horizontal_edges,
                  keyboard_actions=keyboard_actions,
                  relative_positions=relative_positions,
                  scene_restore=scene_restore,
                  archive_boot=archive_boot, archive_boot_with_rom=real_boot,
                  active_game_entry_proved=False, trdos_substituted=True,
                  assembly_executed=False, native_execution=False)
    report = ROOT / 'Tools/Disasm/Reports' / report_name
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'{len(loads)} загрузок, {len(groups)} заголовков, {steps} шагов, {masks} отрисовок')


if __name__ == '__main__':
    main()
