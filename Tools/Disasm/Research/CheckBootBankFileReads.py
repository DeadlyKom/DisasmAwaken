"""Исходные банковые загрузки станции и полёта с ROM TR-DOS и моделью контроллера."""
import argparse
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path

from CheckAwakenBasicRun import load_basic
from CheckBasicIntroDiskRead import FileReadPorts, prepare_memory
from CheckControlsLegacySectorRead import run_with_rom
from CheckFlightKeyPaths import KeyProbe
from CheckIntroStationTransition import IntroInput
from CheckScreenUpdate import put
from CheckStationFlightCycle import DISK, ENTRIES, ROOT, payload, prepare_hyperjump, purchase_equipment, purchase_return_system, run_to
from CheckMusic import PC, SP, IFF, Simulator
from CheckWeightedLoad import reference as weighted_load
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import F, IM


STATION_CALLS = (
    (7, 0x407A, 0x408F, 0xC000, 1, 0),
    (10, 0x4094, 0x40A9, 0xDB00, 3, 0),
    (8, 0x40B1, 0x40C6, 0xDB00, 7, 0),
    (6, 0x40CB, 0x40E0, 0xC000, 4, 0),
    (5, 0x410C, 0x4121, 0xC000, 6, 0),
)
ACTION_CALLS = (
    (25, 0x4216, 0x422C, 0xC000, 6, 2),
    (20, 0x4237, 0x4245, 0xC000, 3, 0),
    (21, 0x4245, 0x425B, 0xEC00, 3, 2),
    (22, 0x4261, 0x4270, 0xC000, 1, 0),
    (23, 0x4270, 0x427C, 0xDADE, 1, 0),
    (24, 0x4281, 0x428F, 0xC000, 4, 0),
)
STATION_CATALOGUE = [(0, 1), (0, 1)]
ACTION_CATALOGUE = [(0, 1), (0, 2), (0, 2)]
TRANSFER_PROBE_OFFSETS = (*range(0x85, 0x8B), 0xC9, 0xCA, 0xCC, 0xCE)
ACTION_TAIL, STATION_TAIL = 0xF866, 0xF4DC
STATION_UNCLASSIFIED_TAIL = 0xF4DE


class LegacyStackReturns:
    """Наблюдает исполняемые RET, условные RET и возвраты ED без подмены стека."""

    def __init__(self, cpu):
        self.cpu = cpu
        self.phase = 'intro'
        self.counts = Counter()
        self.candidates = Counter()
        self.control = payload(23)[:0x13B]
        for opcode in (0xC9, *range(0xC0, 0x100, 8)):
            self.wrap(cpu.opcodes, opcode, opcode)
        for opcode in range(0x45, 0x80, 8):
            self.wrap(cpu.after_ED, opcode, 0xED00 | opcode)

    def wrap(self, table, opcode, encoding):
        operation = table[opcode]
        memory, registers = self.cpu.memory, self.cpu.registers

        def watched_return():
            pc, sp, page = registers[PC], registers[SP], memory.o7ffd & 7
            operation()
            if registers[SP] != ((sp + 2) & 0xFFFF):
                assert registers[SP] == sp
                return
            self.counts[self.phase, encoding] += 1
            target = registers[PC]
            if 0x5DA0 <= target < 0x5F5D:
                target_bank, base = 5, 0x1DA0
            elif 0xDADE <= target < 0xDC9B:
                target_bank, base = page, 0x1ADE
            else:
                return
            # Сравниваются физические банки без дополнительных чтений через наблюдатель шины.
            window = bytes(memory.banks[target_bank][base:base + len(self.control)])
            prefix = window[:0x23] == self.control[:0x23]
            source_bank = page if pc >= 0xC000 else 2 if pc >= 0x8000 else 5 if pc >= 0x4000 else -1
            self.candidates[self.phase, encoding, source_bank, pc, target_bank, target, prefix] += 1

        table[opcode] = watched_return

    def result(self):
        candidates = [dict(phase=phase, opcode=opcode, source_bank=source_bank, pc=pc,
                           target_bank=target_bank, target=target, control_prefix_present=prefix,
                           count=count)
                      for (phase, opcode, source_bank, pc, target_bank, target, prefix), count
                      in sorted(self.candidates.items())]
        return dict(taken_returns=sum(self.counts.values()),
                    counts=[dict(phase=phase, opcode=opcode, count=count)
                            for (phase, opcode), count in sorted(self.counts.items())],
                    matching_numeric_targets=candidates,
                    returns_with_control_prefix=sum(row['count'] for row in candidates if row['control_prefix_present']),
                    starts_after_basic=True,
                    all_possible_paths_proved=False)


@contextmanager
def watch_addresses(cpu, addresses, upper_bank):
    """Наблюдение адресов с одним банком либо отображением адреса в банк."""
    memory = cpu.memory
    assert not memory.watched_addresses and memory.watched_upper_bank is None
    saved_registers, saved_accesses = memory.registers, memory.watched_accesses
    memory.registers = cpu.registers
    memory.watched_addresses = frozenset(addresses)
    memory.watched_upper_bank = upper_bank
    memory.watched_accesses = []
    try:
        yield memory.watched_accesses
    finally:
        memory.watched_addresses = frozenset()
        memory.watched_upper_bank = None
        memory.registers, memory.watched_accesses = saved_registers, saved_accesses


@contextmanager
def watch_station_tail(cpu):
    with watch_addresses(cpu, range(STATION_UNCLASSIFIED_TAIL, 0x10000), 0) as accesses:
        result = dict(bank=0, start=STATION_UNCLASSIFIED_TAIL, end_exclusive=0x10000, accesses=accesses)
        yield result
    assert not result['accesses'], result['accesses'][:20]
    assert bytes(cpu.memory.banks[0][STATION_UNCLASSIFIED_TAIL - 0xC000:]) == bytes(0x10000 - STATION_UNCLASSIFIED_TAIL)


@contextmanager
def watch_flight_legacy(cpu, ports):
    memory = cpu.memory
    fixed, template = range(0x5DA0, 0x5EDB), range(0xDADE, 0xDB5D)
    font, viewport_code = range(0xC600, 0xC870), range(0xC870, 0xCA00)
    operands = (0x5DC3, 0x5DC4, 0x5E20, 0x5E21, 0x5E23, 0x5E33, 0x5E34)
    result = dict(fixed_operands_before=bytes(memory[address] for address in operands).hex())
    cursor = len(ports.read_destinations)
    with watch_addresses(cpu, (*fixed, *font, *viewport_code, *template), 1) as accesses:
        yield result
    result['fixed_operands_after'] = bytes(memory[address] for address in operands).hex()
    result['fixed_operand_addresses'] = list(operands)
    result['fixed_buffer_sector_reads'] = [sector for sector, address in ports.read_destinations[cursor:]
                                           if address == 0x5D25]
    result['fixed_operand_writers'] = [dict(address=address, pc=pc, count=count)
                                       for (address, pc), count in sorted(Counter(
                                           (address, pc) for mode, address, pc in accesses
                                           if mode == 'write' and address in operands).items())]
    result['last_fixed_operand_writers'] = {address: pc for mode, address, pc in accesses
                                            if mode == 'write' and address in operands}
    for label, span in (('fixed', fixed), ('bank1_font', font), ('bank1_viewport_code', viewport_code),
                        ('bank1_template', template)):
        touched = [(mode, address, pc) for mode, address, pc in accesses if address in span]
        opcode_sites = {pc for mode, address, pc in touched if mode == 'read' and address == pc}
        if label == 'bank1_viewport_code':
            result['viewport_code_opcode_sites'] = len(opcode_sites)
            result['viewport_code_first_pc'] = min(opcode_sites) if opcode_sites else None
            touched = [access for access in touched if access[2] not in span]
        else:
            assert not opcode_sites, (label, sorted(opcode_sites))
        result[label] = [dict(mode=mode, pc=pc, accesses=count,
                              first=min(addresses), last=max(addresses), distinct_bytes=len(addresses))
                         for (mode, pc), (count, addresses) in sorted(summarize_accesses(touched).items())]


def summarize_accesses(accesses):
    counts = Counter((mode, pc) for mode, _, pc in accesses)
    addresses = {key: set() for key in counts}
    for mode, address, pc in accesses:
        addresses[mode, pc].add(address)
    return {key: (count, addresses[key]) for key, count in counts.items()}


def check_legacy_loads(departure, initialization, hyper_command, hyper_load, hyper_initialization, memory):
    assert departure['fixed_operands_after'] == initialization['fixed_operands_after'] == '00000000000000'
    assert hyper_command['fixed_operands_before'] == hyper_command['fixed_operands_after'] == '00000000000000'
    assert not hyper_command['fixed'] and not hyper_command['bank1_template']
    assert hyper_command['bank1_font'] and all(row['mode'] == 'read' for row in hyper_command['bank1_font'])
    for stage in (initialization, hyper_initialization):
        writes = {(row['pc'], row['address'], row['count']) for row in stage['fixed_operand_writers']}
        assert {(0x4267, 0x5E20, 1), (0x4267, 0x5E21, 1), (0x426A, 0x5E23, 1)} <= writes
        assert stage['bank1_template'] == [dict(mode='write', pc=0x3FEC, accesses=161,
                                               first=0xDADE, last=0xDB5C, distinct_bytes=127)]
    for stage, length in ((hyper_load, b'\xBC\xC4'), (hyper_initialization, b'\x03\x51')):
        final = bytes.fromhex(stage['fixed_operands_after'])
        track, sector = stage['fixed_buffer_sector_reads'][-1]
        start = (16 * track + sector - 1) * 256
        assert final[:2] == length
        assert int.from_bytes(length, 'little') > 0x10000 - 0xC600
        for index, address in enumerate(stage['fixed_operand_addresses'][:5]):
            assert final[index] == DISK[start + address - 0x5D25]
            assert stage['last_fixed_operand_writers'][address] == 0x3FEC
    assert bytes(memory.banks[1][0x1ADE:0x1B5D]) == payload(23)[:0x7F]
    assert bytes(memory.banks[1][0x0600:0x0A00]) == payload(22)[0x0600:0x0A00]


def seed_loaded_tail(memory, start, value):
    memory.banks[0][start - 0xC000:] = bytes((value,)) * (0x10000 - start)


def check_loaded_tail(memory, slot, start):
    expected = payload(slot)[start - 0x6000:]
    assert expected == bytes(0x10000 - start)
    assert memory.o7ffd & 7 == 0 and bytes(memory[start:0x10000]) == expected
    return dict(slot=slot, start=start, end_exclusive=0x10000, bytes_overwritten=len(expected))


def boot_memory(basic, boot_slot):
    memory = prepare_memory(basic)
    memory[0x5D06] = 9
    if boot_slot == 4:
        memory[0x4000:0x42B5] = payload(4)[0x319:0x5CE]
    else:
        memory[0x4200:0x43FA] = payload(17)[0x43:0x23D]
        # Исходный каталог доступен в уже подготовленном буфере TR-DOS.
        memory[0x5D0C] = 0xFF
    return memory


def check_profile(basic, dos, boot_slot, file_call, cylinder, fill):
    slot, start, stop, destination, bank, pushed = file_call
    entry = ENTRIES[slot]
    offset = entry['offset']
    physical = DISK[offset:offset + entry['allocated_length']]
    length = entry['length']
    # Фикстура начинает на выборке ключа после выбора соответствующей страницы.
    memory = boot_memory(basic, boot_slot)
    stack = 0x5FFF if boot_slot == 4 else 0xBFFE
    end = destination + len(physical)
    assert end < 0x10000
    memory[destination:end + 1] = bytes((fill,)) * (len(physical) + 1)
    ports = FileReadPorts(cylinder)
    cpu = Simulator(memory, {'SP': stack, 'PC': start, 'IY': 0x5C3A})
    cpu.set_tracer(ports)

    def set_rom(image):
        memory[:16384] = image

    run_with_rom(cpu, basic, dos, set_rom, stop)
    first = offset // 256
    sectors = [(index // 16, index % 16 + 1) for index in range(first, first + entry['sector_count'])]
    catalogue = STATION_CATALOGUE if boot_slot == 4 else ACTION_CATALOGUE
    if slot in (22, 23):
        catalogue = catalogue * 2
    assert ports.attempts == catalogue + sectors
    assert memory[destination:end] == physical and memory[end] == fill
    assert (cpu.registers[PC], cpu.registers[SP]) == (stop, stack - pushed)
    return dict(file=entry['name'], slot=slot, boot_slot=boot_slot,
                start=start, stop=stop, destination=destination,
                window_bank_fixture=bank, initial_cylinder=cylinder,
                catalogue_reads=catalogue, data_reads=sectors,
                logical_bytes=length, sector_bytes_loaded=len(physical),
                suffix_bytes_loaded=len(physical) - length)


def check_controls_overlap(basic, dos):
    memory = boot_memory(basic, 17)
    ports = FileReadPorts(0)
    cpu = Simulator(memory, {'SP': 0xBFFE, 'PC': 0x4261, 'IY': 0x5C3A})
    cpu.set_tracer(ports)

    def set_rom(image):
        memory[:16384] = image

    run_with_rom(cpu, basic, dos, set_rom, 0x4270)
    control0 = ENTRIES[22]
    previous_end = 0xC000 + control0['allocated_length']
    overlap = previous_end - 0xDADE
    before = bytes(memory[0xDADE:previous_end])
    assert overlap == 34 and before == DISK[control0['offset'] + control0['length']:
                                            control0['offset'] + control0['allocated_length']]
    run_with_rom(cpu, basic, dos, set_rom, 0x427C)
    control = ENTRIES[23]
    after = bytes(memory[0xDADE:previous_end])
    assert after == DISK[control['offset']:control['offset'] + overlap] and before != after
    assert memory[0xC000:0xDADE] == payload(22)
    return dict(address=0xDADE, length=overlap, control0_suffix=before.hex(), control_prefix=after.hex())


def check_station_sector_read(basic, dos):
    memory = SliceableMemory(out7ffd=0x18)
    memory.roms = (basic, basic)
    memory.out7ffd(0x18)
    flat = prepare_memory(basic)
    put(memory, 0x5C00, flat[0x5C00:0x5D3E])
    awaken_offset = ENTRIES[3]['offset']
    put(memory, 0x5D3B, DISK[awaken_offset + 0x2B7:awaken_offset + 0x315])
    memory[0x5D06], memory[0x5D0C], memory[0x5CB6] = 9, 0xFF, 0xF4
    # Каталожная запись уже прочитана, выполняется только исходный хвост с функцией 05.
    put(memory, 0x5CDD, DISK[4 * 16:5 * 16])
    ports = FileReadPorts(0)
    cpu = Simulator(memory, {'SP': 0x5FFF, 'PC': 0x5D87, 'IY': 0x5C3A}, state={'im': 1})
    cpu.set_tracer(ports)

    def set_rom(image):
        memory.memory[0] = image

    run_with_rom(cpu, basic, dos, set_rom, 0x6300)
    first = ENTRIES[4]['offset'] // 256
    sectors = [(index // 16, index % 16 + 1) for index in range(first, first + 192)]
    assert ports.attempts == sectors
    assert bytes(memory[0x6000:0x10000]) == payload(4)
    assert bytes(memory[0:16384]) == dos and memory.o7ffd == 0x18
    assert (cpu.registers[PC], cpu.registers[SP]) == (0x6300, 0x5FFF)
    assert (first + 160) * 256 == ENTRIES[5]['offset']
    assert (first + 176) * 256 == ENTRIES[6]['offset']
    return dict(data_reads=sectors, station_sectors_written_to_ram=160, sectors_addressed_to_rom=32,
                catalogue_header_supplied=True, rom_preserved=True,
                extra_sector_ranges=[dict(slot=5, count=16), dict(slot=6, count=16)])


def check_flight_transition(cpu, ports, basic, dos, set_rom, *, mark_context):
    memory, registers = cpu.memory, cpu.registers

    def file_sectors(slot):
        entry = ENTRIES[slot]
        first = entry['offset'] // 256
        return [(index // 16, index % 16 + 1) for index in range(first, first + entry['sector_count'])]

    def transfer_sectors(slots, next_slot):
        # Функция 0E с A=0 читает следующий сектор и при нулевом остатке длины.
        return (file_sectors(slots[0]) + file_sectors(next_slot)[:1]
                + [sector for slot in slots[1:] for sector in file_sectors(slot)])

    purchase = purchase_return_system(cpu, True)
    assert memory[0x98A8] == 0xFF
    assert memory[0x98AA] == 0xFF
    if mark_context:
        # В полётном профиле задан символ от редактора, исходный парсер сам меняет пару.
        memory[0x973E] = ord('4')
        assert bytes(memory[0x99D8:0x99DA]) == b'\x7F\x01'
        stack = registers[SP]
        registers[SP] -= 2
        put(memory, registers[SP], b'\xFF\x3F')
        registers[2:6] = [0x97, 0x36, 0x99, 0xC8]
        registers[PC] = 0xA191
        run_to(cpu, 0x3FFF)
        assert registers[SP] == stack and bytes(memory[0x99D8:0x99DA]) == b'\xF7\x08'
        # Покупка присадки за 1800, после сделки остаётся контрольная сумма.
        price = int.from_bytes(memory[0x95C6:0x95C8], 'little')
        assert price == 1800
        put(memory, 0x984E, (0x1234 + price).to_bytes(2, 'little'))
        assert purchase_equipment(cpu, 26) == ([], 0x1234) and memory[0x98A8] == 0xFE
        # Тип 6 входит в запретный набор строки 28. После отказа возвращаем тип профиля.
        ship = memory[0x9849]
        memory[0x9849] = 6
        price = int.from_bytes(memory[0x95CA:0x95CC], 'little')
        assert price == 2000
        put(memory, 0x984E, (0x1234 + price).to_bytes(2, 'little'))
        assert purchase_equipment(cpu, 28) == ([6], 0x1234 + price) and memory[0x98AA] == 0xFF
        memory[0x9849] = ship
        system_purchase = purchase_equipment(cpu, 28)
        assert (system_purchase, memory[0x98AA]) == (([], 0x1234), 0xFE), (system_purchase, memory[0x98AA])
        memory[0x9906] = 0xF3
        memory[0x98A0] = 0xFE
        # Различимые пары времени и два ненулевых байта очков ранга.
        memory[0x983D], memory[0x983E] = 0x37, 0x42
        memory[0x984C], memory[0x984D] = 0x02, 0x01
    player_indices = bytes(memory[0x9849:0x984B])
    rank_score = bytes(memory[0x984C:0x984E])
    money = bytes(memory[0x984E:0x9850])
    tonnage = bytes(memory[0x9850:0x9852])
    fuel_additive = memory[0x98A8]
    transition_counter_before = memory[0x9906]
    transition_counter = (transition_counter_before + (30 if mark_context else 0)) & 255
    station_prefix = bytes(memory[0x983B:0x9852])
    action_prefix = station_prefix[:2] + station_prefix[2:4][::-1] + station_prefix[4:]
    artifact = memory[0x98A0]
    assert artifact == (0xFE if mark_context else 0xFF)
    station_equipment = bytes(memory[0x988E:0x98B0])
    assert len(station_equipment) == 34 and station_equipment[-1] == 0x80
    # Отличимые значения для проверки переноса байтов с неизвестным игровым назначением.
    marker = bytes(memory[0x983B + offset] for offset in TRANSFER_PROBE_OFFSETS)
    if mark_context:
        marker = bytes(0x31 + index * 17 for index in range(len(TRANSFER_PROBE_OFFSETS)))
        for offset, value in zip(TRANSFER_PROBE_OFFSETS, marker):
            memory[0x983B + offset] = value
    station_news_orders = bytes(memory[0x98BF:0x9906])
    assert len(station_news_orders) == 71

    def check_marker(base):
        assert bytes(memory[base + offset] for offset in TRANSFER_PROBE_OFFSETS) == marker

    cpu.set_tracer(ports)
    registers[PC] = 0x7E5A
    start = len(ports.attempts)
    seed_loaded_tail(memory, ACTION_TAIL, 0xA5)
    with watch_flight_legacy(cpu, ports) as departure_legacy:
        run_with_rom(cpu, basic, dos, set_rom, 0x6000, step_limit=5000000)
    outbound_tail = check_loaded_tail(memory, 17, ACTION_TAIL)
    with watch_flight_legacy(cpu, ports) as start_flight_legacy:
        run_with_rom(cpu, basic, dos, set_rom, 0xA82D, step_limit=5000000)
    action_files = [17, *(file_call[0] for file_call in ACTION_CALLS)]
    outbound = [(track, sector) for track, sector in ports.attempts[start:] if track]
    assert outbound == transfer_sectors(action_files, 18)
    after_action = file_sectors(18)[0]
    assert [address for sector, address in ports.read_destinations[start:] if sector == after_action] == [0x5D25]
    assert (registers[SP], memory.o7ffd) == (0xBFFE, 0x19)
    check_marker(0x9BBD)
    assert bytes(memory[0x9BBD:0x9BD4]) == action_prefix
    assert bytes(memory[0x9BCB:0x9BCD]) == player_indices
    assert bytes(memory[0x9BCE:0x9BD0]) == rank_score
    assert bytes(memory[0x9BD0:0x9BD2]) == money
    assert bytes(memory[0x9BD2:0x9BD4]) == tonnage
    assert memory[0x9C22] == artifact
    assert memory[0x9C2A] == fuel_additive
    assert memory[0x9C88] == transition_counter
    assert bytes(memory[0x9C10:0x9C32]) == station_equipment
    assert bytes(memory[0x9C41:0x9C88]) == station_news_orders
    set_rom(basic)
    cpu.run(0xA82D, 0xA85E, interrupts=True)
    memory.registers = registers
    unknown_addresses = frozenset(0x9BBD + offset for offset in TRANSFER_PROBE_OFFSETS)
    news_order_addresses = frozenset(range(0x9C41, 0x9C88))
    memory.watched_addresses = unknown_addresses | news_order_addresses | {0x9C22, 0x9C88}
    for _ in range(64):
        cpu.run(0xA85E, 0xA85E, interrupts=True)
        assert (registers[SP], memory.o7ffd) == (0xBFFC, 0x10)
    memory.watched_addresses = frozenset()
    memory.registers = None
    unknown_accesses = [access for access in memory.watched_accesses if access[1] in unknown_addresses]
    artifact_accesses = [access for access in memory.watched_accesses if access[1] == 0x9C22]
    news_order_accesses = [access for access in memory.watched_accesses if access[1] in news_order_addresses]
    transition_counter_accesses = [access for access in memory.watched_accesses if access[1] == 0x9C88]
    assert not unknown_accesses, unknown_accesses
    assert not news_order_accesses, news_order_accesses
    assert not transition_counter_accesses, transition_counter_accesses
    assert bytes(memory[0x9C41:0x9C88]) == station_news_orders
    check_marker(0x9BBD)
    assert bytes(memory[0x9BCB:0x9BCD]) == player_indices
    assert bytes(memory[0x9BCE:0x9BD0]) == rank_score
    assert bytes(memory[0x9BD0:0x9BD2]) == money
    assert bytes(memory[0x9BD2:0x9BD4]) == tonnage
    assert memory[0x9C22] == artifact
    assert memory[0x9C27] == 0xFE

    remapped_speed = None
    if mark_context:
        assert bytes(memory[0x9D5A:0x9D5C]) == b'\xF7\x08'
        speed_key = KeyProbe(memory, (0xF7, 8))
        cpu.set_tracer(speed_key)
        run_to(cpu, 0x6F1D)
        speed_key.observe(1, memory, registers)
        run_to(cpu, 0x7680, lambda _: speed_key.observe(1, memory, registers))
        assert speed_key.handlers == [(7, 0, 0x7680)]
        old_speed = int.from_bytes(memory[0xA78F:0xA791], 'little')
        run_to(cpu, 0x6F55, lambda _: speed_key.observe(1, memory, registers))
        speed_key.observe(1, memory, registers)
        new_speed = int.from_bytes(memory[0xA78F:0xA791], 'little')
        assert speed_key.finished and speed_key.returns == 1 and new_speed == (old_speed + 8) & 65535
        remapped_speed = dict(matrix=list(speed_key.key), handler=0x7680, before=old_speed, after=new_speed,
                              station_caption_prepared=True, original_parser_and_scan_executed=True)

    wait_cycles = 0

    def watch_hyperjump(frame, memory, registers):
        nonlocal wait_cycles
        if registers[PC] == 0x719A:
            assert memory[0x9C2A] == fuel_additive
            wait_cycles += 1

    with watch_flight_legacy(cpu, ports) as hyper_command_legacy:
        hyper_key, saved = prepare_hyperjump(cpu, watch_hyperjump, fuel_additive=None)
    assert wait_cycles == (64 if mark_context else 128)
    assert registers[SP] == 0x4FFE
    cpu.set_tracer(ports)
    start = len(ports.attempts)
    seed_loaded_tail(memory, ACTION_TAIL, 0x5A)
    with watch_flight_legacy(cpu, ports) as hyper_load_legacy:
        run_with_rom(cpu, basic, dos, set_rom, 0x6000, step_limit=5000000)
    hyper_tail = check_loaded_tail(memory, 17, ACTION_TAIL)
    assert bytes(memory[0x9BBD:0x9D9E]) == saved and registers[SP] == 0x5FFF
    set_rom(basic)
    with watch_flight_legacy(cpu, ports) as hyper_init_legacy:
        run_with_rom(cpu, basic, dos, set_rom, 0xA82D, step_limit=5000000)
    check_legacy_loads(departure_legacy, start_flight_legacy, hyper_command_legacy,
                       hyper_load_legacy, hyper_init_legacy, memory)
    hyper_sectors = [(track, sector) for track, sector in ports.attempts[start:] if track]
    assert hyper_sectors == transfer_sectors(action_files, 18)
    assert [address for sector, address in ports.read_destinations[start:] if sector == after_action] == [0x5D25]
    set_rom(basic)
    cpu.run(0xA82D, 0xA85E, interrupts=True)
    for _ in range(2):
        cpu.run(0xA85E, 0xA85E, interrupts=True)
        assert (registers[SP], memory.o7ffd) == (0xBFFC, 0x10)
    check_marker(0x9BBD)
    assert bytes(memory[0x9C41:0x9C88]) == station_news_orders
    assert memory[0x9C88] == transition_counter
    assert bytes(memory[0x9BD2:0x9BD4]) == tonnage

    key = KeyProbe(memory, (0xFB, 8))
    cpu.set_tracer(key)
    run_to(cpu, 0x6F1D)
    key.observe(1, memory, registers)
    run_to(cpu, 0x7606, lambda _: key.observe(1, memory, registers))
    assert key.handlers == [(0x12, 0, 0x7606)]
    key.observe(1, memory, registers)

    launches = []
    return_tonnage = tonnage
    cleared_indices = (2, 3, 5, 6, 7, 8, 9, 31)
    if mark_context:
        # У входа возврата проверяем два настоящих пуска с подготовленными захватами.
        saved_registers = list(registers)
        template_mode = memory[0x9B83]
        memory[0x9B83] = 0
        assert memory[0x9BCD] == 0
        for item in cleared_indices:
            memory[0x9C10 + item] = 0xFE if item & 1 else 2
        for record in (0xA100, 0xA140):
            put(memory, record, b'\x00\x80')
            memory[record + 24] = 0
        for handler, target_slot, class_code, expected_status in ((0x704C, 4, 3, 50), (0x7075, 5, 2, 65)):
            target = 0xA100 + target_slot * 64
            put(memory, target, b'\x23\x00')
            memory[target + 18] = class_code
            capture = 0x9B1B + len(launches)
            memory[capture] = target_slot
            registers[SP] -= 2
            put(memory, registers[SP], b'\xFF\x3F')
            registers[F] |= 0x40
            registers[PC] = handler
            run_to(cpu, 0x3FFF)
            assert registers[SP] == saved_registers[SP] and memory[0x9BCD] == expected_status
            assert memory[capture] == 0xFF and memory[target + 11] == len(launches)
            launches.append(dict(handler=handler, target_slot=target_slot, target_class=class_code, status=expected_status))
        assert memory[0xA85F] == 5
        # Префикс кадра уменьшает задержку, остальные стадии кадра здесь не исполняются.
        for delay in (4, 3, 2, 1, 0):
            cpu.run(0xA85E, 0xA867)
            assert memory[0xA85F] == delay
        registers[:] = saved_registers
        memory[0x9B83] = template_mode
        assert memory[0x9C12] == 2 and memory[0x9C13] == 0xFC
        return_tonnage = bytes(((tonnage[0] - len(launches)) & 255, tonnage[1]))
        assert bytes(memory[0x9BD2:0x9BD4]) == return_tonnage

    cpu.set_tracer(ports)
    start = len(ports.attempts)
    context = bytearray(memory[0x9BBD:0x9DBD])
    context[2], context[3] = context[3], context[2]
    context[0x6A] = 0xFF
    run_with_rom(cpu, basic, dos, set_rom, 0x6300, step_limit=5500000)
    inbound_tail = check_loaded_tail(memory, 4, STATION_TAIL)
    assert bytes(memory[0x983B:0x9A1C]) == context[:481]
    assert bytes(memory[0x9A1C:0x9A3B]) == payload(4)[0x3A1C:0x3A3B]
    check_marker(0x983B)
    assert bytes(memory[0x9849:0x984B]) == player_indices
    assert bytes(memory[0x984C:0x984E]) == rank_score
    assert bytes(memory[0x984E:0x9850]) == money
    assert bytes(memory[0x9850:0x9852]) == return_tonnage
    assert memory[0x98A0] == artifact
    assert memory[0x98A8] == fuel_additive
    assert memory[0x9906] == transition_counter
    assert bytes(memory[0x98BF:0x9906]) == station_news_orders
    if mark_context:
        assert bytes(memory[0x99D8:0x99DA]) == b'\xF7\x08'
    set_rom(basic)
    with watch_station_tail(cpu) as arrival_station_tail:
        run_with_rom(cpu, basic, dos, set_rom, 0x9A59, step_limit=5500000)
    station_files = [4, *(file_call[0] for file_call in STATION_CALLS)]
    inbound = [(track, sector) for track, sector in ports.attempts[start:] if track]
    main_files = transfer_sectors(station_files, 5)
    assert inbound[:len(main_files)] == main_files
    after_station = file_sectors(5)[0]
    assert [address for sector, address in ports.read_destinations[start:] if sector == after_station] == [0x5D25, 0xC000]
    backdrop = inbound[len(main_files):]
    backdrop_file = file_sectors(9)
    assert backdrop and backdrop[0] in backdrop_file
    first_backdrop = backdrop_file.index(backdrop[0])
    assert backdrop == backdrop_file[first_backdrop:first_backdrop + len(backdrop)]
    assert (registers[SP], memory.o7ffd, memory[0x98A5]) == (0x5FFF, 0x10, 0xFF)
    status_at_arrival = memory[0x984B]
    assert status_at_arrival == (65 if mark_context else 0)
    docking_script = None
    if mark_context:
        before_equipment = bytes(memory[0x988E:0x98AE])
        expected_equipment = bytearray(before_equipment)
        for item in cleared_indices:
            expected_equipment[item] = 0xFF if before_equipment[item] & 128 else 0
        with watch_station_tail(cpu) as docking_station_tail:
            cpu.run(0x9A59, 0x9A81, interrupts=True)
        final_credits = int.from_bytes(memory[0x984E:0x9850], 'little')
        assert (memory[0x984B], final_credits) == (17, 0x1234 - 1000)
        assert bytes(memory[0x988E:0x98AE]) == expected_equipment
        assert memory[0x9850] == weighted_load(bytearray(memory[0:65536]), 0xC0DB)[0]
        docking_script = dict(launches=launches, status_from_flight=[row['status'] for row in launches],
                              station_tail=docking_station_tail,
                              status_at_arrival=status_at_arrival, tonnage_at_arrival=return_tonnage[0],
                              command_delay_prefix_steps=5,
                              status_after_script=17, credits_after_script=final_credits,
                              cleared_equipment_indices=cleared_indices, recomputed_tonnage=memory[0x9850])
    return dict(purchase=purchase, departure_entry=0x7E5A, flight_frames=64, outbound_initial_tail=outbound_tail,
                legacy_workspace=dict(departure_load=departure_legacy, action_initialization=start_flight_legacy,
                                      hyper_command=hyper_command_legacy, hyper_load=hyper_load_legacy,
                                      hyper_initialization=hyper_init_legacy),
                remapped_speed=remapped_speed,
                hyperjump=dict(key=list(hyper_key.key), handler=0x70F6, preferred_spent=14,
                               context_bytes_restored=len(saved), flight_frames_after_reload=2,
                               fuel_additive_code=fuel_additive, fuel_additive_bought=mark_context,
                               warmup_outer_iterations=wait_cycles,
                               gate_fixture_applied_at_handler=True, data_sectors=len(hyper_sectors), initial_tail=hyper_tail),
                return_key=list(key.key), return_handler=0x7606, station_entry=0x9A59,
                inbound_initial_tail=inbound_tail, arrival_station_tail=arrival_station_tail,
                docking_script=docking_script,
                outbound_slots=action_files, inbound_slots=station_files,
                next_file_sector_after_action=after_action, next_file_sector_after_station=after_station,
                next_file_sector_scratch_address=0x5D25,
                station_context_restored=481, station_context_suffix_from_disk=31,
                station_player_indices_transferred=list(player_indices),
                station_rank_score_transferred=int.from_bytes(rank_score, 'little'),
                station_money_transferred=int.from_bytes(money, 'little'),
                station_tonnage_transferred=dict(used=tonnage[0], capacity=tonnage[1]),
                outbound_player_prefix=action_prefix.hex(),
                source_station_player_prefix=station_prefix.hex(),
                station_artifact_code_transferred=artifact,
                artifact_accesses_in_first_64_flight_frames=artifact_accesses,
                outbound_primary_equipment=station_equipment.hex(),
                inbound_primary_equipment=context[0x53:0x75].hex(),
                transferred_news_and_orders=station_news_orders.hex(),
                news_order_accesses_in_first_64_flight_frames=len(news_order_accesses),
                transition_counter=dict(before=transition_counter_before, transferred=transition_counter,
                                        equipment_row=28, bought=mark_context,
                                        accesses_in_first_64_flight_frames=len(transition_counter_accesses)),
                transferred_unknown_probe_offsets=TRANSFER_PROBE_OFFSETS,
                transferred_unknown_probe_bytes=marker.hex(),
                transferred_unknown_markers_injected=mark_context,
                probe_accesses_in_first_64_flight_frames=len(unknown_accesses),
                outbound_data_sectors=len(outbound), inbound_data_sectors=len(inbound),
                inbound_backdrop_sectors=len(backdrop), trdos_calls_substituted=False)


def check_intro_transition(basic, dos, frames, *, mark_context, flight_check=check_flight_transition):
    cpu, ports, basic_run = load_basic(basic, dos)
    stack_returns = LegacyStackReturns(cpu)
    memory = cpu.memory
    first_intro = ENTRIES[3]['offset'] // 256 + 1
    basic_sectors = ports.attempts.copy()

    def set_rom(image):
        memory.memory[0] = image

    put(memory, 0x65B3, b'\xA5\x5A\x96\x69')
    run_with_rom(cpu, basic, dos, set_rom, 0x6500)
    intro_stack_range = bytes(memory[0x65B3:0x65B7])
    assert intro_stack_range == bytes(4)
    intro_sectors = [(index // 16, index % 16 + 1) for index in range(first_intro, first_intro + 44)]
    assert ports.attempts == basic_sectors + intro_sectors
    tail_displacement = memory[0x9000]
    assert tail_displacement == 0
    set_rom(basic)
    inputs = IntroInput(cpu, frames)
    cpu.set_tracer(inputs)
    memory[0x5C00] = memory[0x5C04] = 0xFF
    cpu.run(0x6500, 0x5D3B, interrupts=True)
    assert inputs.polls == frames + 1
    intro_stack_saved = bytes(memory[0x65B3:0x65B7])
    assert intro_stack_saved == bytes.fromhex('00 FF 5F 00')
    assert bytes(memory[0x74FF:0x7501]) == bytes((0x28, tail_displacement))
    cpu.set_tracer(ports)
    seed_loaded_tail(memory, STATION_TAIL, 0x5A)
    run_with_rom(cpu, basic, dos, set_rom, 0x6300, step_limit=2000000)
    initial_station_tail = check_loaded_tail(memory, 4, STATION_TAIL)
    first_station = ENTRIES[4]['offset'] // 256
    station_sectors = [(index // 16, index % 16 + 1) for index in range(first_station, first_station + 192)]
    assert ports.attempts == basic_sectors + intro_sectors + STATION_CATALOGUE + station_sectors, (
        len(ports.attempts), ports.attempts[len(basic_sectors) + len(intro_sectors):][:8])
    assert bytes(memory[0x6000:0x10000]) == payload(4)
    station_stack_range = bytes(memory[0x65B3:0x65B7])
    assert station_stack_range == bytes.fromhex('98 CD 33 C3')
    assert bytes(memory[0:16384]) == dos and memory.o7ffd == 0x18
    assert (cpu.registers[PC], cpu.registers[SP]) == (0x6300, 0x5FFF)
    stack_returns.phase = 'station_startup'
    set_rom(basic)
    attempts = len(ports.attempts)
    with watch_station_tail(cpu) as startup_station_tail:
        run_with_rom(cpu, basic, dos, set_rom, 0x9A59, step_limit=2500000)
    assert (cpu.registers[PC], cpu.registers[SP], cpu.registers[IM], cpu.registers[IFF]) == (0x9A59, 0x5FFF, 2, 1)
    assert memory.o7ffd == 0x10
    for slot, _, _, _, _, _ in STATION_CALLS:
        entry_file = ENTRIES[slot]
        first = entry_file['offset'] // 256
        count = entry_file['sector_count']
        sequence = [(index // 16, index % 16 + 1) for index in range(first, first + count)]
        assert ports.attempts[attempts:attempts + len(STATION_CATALOGUE)] == STATION_CATALOGUE
        attempts += len(STATION_CATALOGUE)
        assert ports.attempts[attempts:attempts + count] == sequence
        attempts += count
    assert len(ports.attempts) > attempts
    attempts_before_frames = len(ports.attempts)
    stack_returns.phase = 'station_frames'
    with watch_station_tail(cpu) as idle_station_tail:
        cpu.run(0x9A59, 0x9A81, interrupts=True)
        for _ in range(7):
            cpu.run(0x9A81, 0x9A81, interrupts=True)
            assert (cpu.registers[SP], cpu.registers[IM], memory.o7ffd) == (0x5FFF, 2, 0x10)
    assert len(ports.attempts) == attempts_before_frames
    result = dict(basic_run=basic_run, usr_entry=basic_run['actual_basic_usr_entry'],
                  intro_keyboard_polls=inputs.polls, intro_sectors=len(intro_sectors),
                  intro_tail_displacement=dict(source=0x9000, destination=0x7500,
                                               value=tail_displacement, both_jr_targets=0x7501),
                  intro_stack_storage=dict(address=0x65B3, after_load=intro_stack_range.hex(),
                                           after_intro=intro_stack_saved.hex(), after_station_load=station_stack_range.hex()),
                  station_catalogue_reads=STATION_CATALOGUE, station_sectors=len(station_sectors),
                  station_boot_reached=0x6300, initial_station_tail=initial_station_tail,
                  startup_station_tail=startup_station_tail, idle_station_tail=idle_station_tail,
                  main_loop_entry=0x9A59, frame_entry=cpu.registers[PC],
                  completed_station_frames=7, final_page=memory.o7ffd,
                  station_bank_file_sequences_checked=len(STATION_CALLS), trdos_calls_substituted=False)
    stack_returns.phase = 'flight_transition'
    result['flight_transition'] = flight_check(cpu, ports, basic, dos, set_rom, mark_context=mark_context)
    result['legacy_stack_returns'] = stack_returns.result()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    assert len(basic) == len(dos) == 16384
    profiles = []
    for boot_slot, calls in ((4, STATION_CALLS), (17, ACTION_CALLS)):
        for file_call in calls:
            file_cylinder = ENTRIES[file_call[0]]['first_track'] // 2
            profiles.extend(check_profile(basic, dos, boot_slot, file_call, cylinder, fill)
                            for cylinder, fill in ((0, 0xA5), (file_cylinder, 0x5A)))
    report = dict(passed=True, disk_sha256=sha256(DISK).hexdigest(),
                  dos_rom=args.dos_rom.name, dos_rom_sha256=sha256(dos).hexdigest(),
                  basic_rom_sha256=sha256(basic).hexdigest(), profiles=profiles,
                  control_load_overlap=check_controls_overlap(basic, dos),
                  intro_station_sector_read=check_station_sector_read(basic, dos),
                  intro_transitions=[check_intro_transition(basic, dos, 0, mark_context=False),
                                     check_intro_transition(basic, dos, 2, mark_context=True)],
                  basic_interpreter_executed=True,
                  fixed_bank_window_fixture=True, original_file_key_setup_executed=True,
                  modelled_fdc_and_rom_paging=True, suffix_game_consumers_proved=False,
                  assembly_executed=False, native_execution=False)
    output = ROOT / 'Tools/Disasm/Reports/BootBankFileReadsVerification.json'
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Одиннадцать банковых загрузок станции и полёта сверены в 22 профилях')


if __name__ == '__main__':
    main()
