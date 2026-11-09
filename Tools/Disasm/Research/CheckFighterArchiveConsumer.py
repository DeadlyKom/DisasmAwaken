"""Исходный архивный потребитель заголовков, кадров BAR и масок BD."""
import hashlib
import json

from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckScene1ArchiveConsumer import FIXED_OFFSET, RETURN_SENTINEL, start_call
from CheckStationFlightCycle import DISK, payload, put, run_to
from FighterAssetData import decode
from TraceFlight import A, C, H, IFF, L, PC, SP, T, ROOT, Simulator
from skoolkit.simutils import I, IM


STATE = 0x4842
SCENE = 0x7700
ROW_BYTES = 92


def word(memory, address):
    return int.from_bytes(memory[address:address + 2], 'little')


def service_requests(cpu, requests):
    memory, registers = cpu.memory, cpu.registers
    results = []
    for slot, page, address in requests:
        run_to(cpu, 0x3D13)
        assert (registers[A], registers[C], registers[H] * 256 + registers[L]) == (255, 0x0E, address)
        assert memory.o7ffd == page
        key = bytes(memory[0x5CDD:0x5CE6])
        assert key == DISK[16 * slot:16 * slot + 9]
        data = payload(slot)
        put(memory, address, data)
        assert bytes(memory[address:address + len(data)]) == data
        stack = registers[SP]
        registers[PC] = word(memory, stack)
        registers[SP] += 2
        results.append(dict(slot=slot, key=key.decode('ascii'), address=address, port_value=page))
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
        for mirror in (0, 1):
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
            memory[STATE] = mirror
            put(memory, STATE + 1, (0xC000 + offset).to_bytes(2, 'little'))
            put(memory, STATE + 3, (SCENE + (width - 1 if mirror else 0)).to_bytes(2, 'little'))
            memory[STATE + 0x17] = bank
            memory[STATE + 0x11], memory[STATE + 0x12] = width, height
            start_call(cpu, 0x4753, IX=STATE)
            run_to(cpu, RETURN_SENTINEL)
            assert bytes(memory[SCENE:SCENE + len(wanted)]) == wanted, (bank, offset, mirror)
            assert memory.o7ffd == 0x58 + bank
            cases += 1
    return cases


def check_archive_boot(requests):
    memory = ExtendedMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    cpu = Simulator(memory, {'PC': 0x4000})
    cpu.set_tracer(ArchivePorts(memory))
    registers = cpu.registers
    loads = service_requests(cpu, requests)
    run_to(cpu, 0x4030)
    assert (registers[I], registers[IM], registers[IFF], registers[SP]) == (0x5E, 2, 1, 0x6000)
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
    return dict(loads=loads, frame_entry=0x4030, complete_cycles=len(frames),
                screen_bitmap_sha256=frames, distinct_bitmap_count=len(set(frames)),
                interrupts_scheduled_at_loop_boundaries=True, no_keys_pressed=True)


def main():
    memory = ExtendedMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    put(memory, 0x4FB6, memory[0x5018:0x501A])
    cpu = Simulator(memory)
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
    masks = check_masks(cpu, banks, sprites)
    result = dict(passed=True, original_sha256=hashlib.sha256(DISK).hexdigest(), loads=loads,
                  headers_executed=len(groups), indexed_group_loads=len(pointers),
                  step_cases=steps, mask_cases=masks, archived_fighter_code=True,
                  archive_boot=check_archive_boot(bd_requests + [(30, 0x5B, 0x7700)] + bar_requests),
                  active_game_entry_proved=False, trdos_substituted=True,
                  assembly_executed=False, native_execution=False)
    report = ROOT / 'Tools/Disasm/Reports/FighterArchiveConsumerVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'{len(loads)} загрузок, {len(groups)} заголовков, {steps} шагов, {masks} отрисовок')


if __name__ == '__main__':
    main()
