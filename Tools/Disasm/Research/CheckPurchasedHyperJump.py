"""Гиперпрыжок Awakenv02 после покупки и измерения расстояния исходным кодом."""
import argparse
from functools import partial
from hashlib import sha256
from math import isqrt
import json
from pathlib import Path

from CheckBootBankFileReads import check_intro_transition
from CheckControlsLegacySectorRead import run_with_rom
from CheckFlightKeyPaths import KeyProbe
from CheckIntro import ROOT
from CheckMapSectorTables import reference as sector_table
from CheckStationFlightCycle import DISK, ENTRIES, payload, purchase_equipment, put, run_to
from skoolkit.simutils import D, E, F, H, L, PC, SP


STOCK = 0x9C10
GATE = 0x9C26
COST = 0x9C8A
TARGET_CONTEXT = 0x9BC6
FIXED_START, FIXED_END = 0x5DA0, 0x5F5D
CONTROL_START, CONTROL_END = 0x1ADE, 0x1C9B


def file_sectors(slot):
    entry = ENTRIES[slot]
    first = entry['offset'] // 256
    return [(index // 16, index % 16 + 1) for index in range(first, first + entry['sector_count'])]


def call_station(cpu, address):
    memory, registers = cpu.memory, cpu.registers
    stack = registers[SP]
    registers[SP] -= 2
    put(memory, registers[SP], b'\xFF\x3F')
    cpu.run(address, 0x3FFF, interrupts=True)
    assert registers[SP] == stack and memory.o7ffd == 0x10


def purchase(cpu, stock):
    memory = cpu.memory
    assert memory[0x9849] == 6 and memory[0x98A4] == 0xFF
    assert bytes(memory[0x988E:0x9890]) == bytes(2)
    prices = [int.from_bytes(bytes(memory[0x9592 + 2 * row:0x9594 + 2 * row]), 'little')
              for row in (0, 1, 22)]
    assert prices[2] == 10000 and all(prices)
    # Подготовлены модель корабля и бюджет, покупки исполняет исходный LANG.
    memory[0x9849] = 0
    try_other_fuel = stock != (9, 0)
    other_row = 1 if stock[0] else 0
    credits = prices[2] + sum(count * price for count, price in zip(stock, prices[:2]))
    if try_other_fuel:
        credits += prices[other_row]
    put(memory, 0x984E, credits.to_bytes(2, 'little'))
    credits -= prices[2]
    assert purchase_equipment(cpu, 22) == ([], credits) and memory[0x98A4] == 0xFE
    for row, count in enumerate(stock):
        for amount in range(1, count + 1):
            credits -= prices[row]
            result = purchase_equipment(cpu, row)
            assert result == ([], credits), (row, amount, result, credits)
            assert memory[0x988E + row] == amount
    if try_other_fuel:
        assert purchase_equipment(cpu, other_row) == ([12], prices[other_row])
    assert bytes(memory[0x988E:0x9890]) == bytes(stock)
    assert credits == (prices[other_row] if try_other_fuel else 0)
    return prices, other_row if try_other_fuel else None


def select_map_key(cpu, ports, symbols, coordinates):
    memory, registers = cpu.memory, cpu.registers
    current = bytes(memory[0x983F:0x9844])
    assert current == bytes.fromhex('38 4B F3 4A 00')
    data = sector_table(current[0], current[1])[0]
    x, y = coordinates
    assert (x, y) in zip(data[::2], data[1::2])
    assert ((current[0] ^ current[1] ^ x ^ y) & 7) >= 2
    expected = isqrt(((x - current[2]) ** 2 + (y - current[3]) ** 2) // 9)
    cpu.set_tracer(ports)
    call_station(cpu, symbols['Station.OpenMapPanelGroup.Entry'])
    call_station(cpu, symbols['Station.RebuildInterface.Entry'])
    registers[D], registers[E] = current[1], current[0]
    registers[H], registers[L] = y, x
    call_station(cpu, symbols['Station.CenterKeyAndRefreshMap.Entry'])
    selected = bytes(memory[0x9844:0x9849])
    assert selected == current[:2] + bytes((x, y, 0))
    assert memory[0x9908] == expected
    return current, selected, expected


def check_flight(cpu, ports, basic, dos, set_rom, *, mark_context, stock, symbols,
                 coordinates=(234, 85), finish_first_frame=True):
    assert not mark_context
    memory, registers = cpu.memory, cpu.registers
    prices, incompatible_fuel_row = purchase(cpu, stock)
    current, destination, cost = select_map_key(cpu, ports, symbols, coordinates)
    registers[PC] = 0x7E5A
    run_with_rom(cpu, basic, dos, set_rom, 0xA82D, step_limit=5_000_000)
    set_rom(basic)
    cpu.run(0xA82D, 0xA85E, interrupts=True)
    assert bytes(memory[STOCK:STOCK + 2]) == bytes(stock)
    assert memory[GATE] == 0xFE and memory[COST] == cost and memory[0xA85F] == 0
    assert bytes(memory[0x9BC1:0x9BC6]) == current
    assert bytes(memory[TARGET_CONTEXT:TARGET_CONTEXT + 5]) == destination

    key = KeyProbe(memory, tuple(memory[0x9D7A:0x9D7C]))
    assert key.key == (0xFD, 0x10)
    cpu.set_tracer(key)
    run_to(cpu, 0x6F1D)
    key.observe(1, memory, registers)
    run_to(cpu, 0x70F6, lambda _: key.observe(1, memory, registers))
    key.observe(1, memory, registers)
    assert key.handlers == [(0x17, 0, 0x70F6)]
    before_fixed = bytes(memory[FIXED_START:FIXED_END])
    before_control = bytes(memory.banks[1][CONTROL_START:CONTROL_END])
    assert before_control == payload(23)[:CONTROL_END - CONTROL_START]
    assert before_fixed[:127] != before_control[:127]

    spending_index = 0 if stock[0] else 1
    spending = cost * (2 if spending_index == 0 else 1)
    accepted = stock[spending_index] >= spending
    sites = []
    wait_cycles = 0

    def observe(pc):
        nonlocal wait_cycles
        assert not FIXED_START <= pc < FIXED_END
        assert not (memory.o7ffd & 7 == 1 and 0xDADE <= pc < 0xDC9B)
        if pc in (0x7176, 0x4200):
            sites.append(pc)
        if pc == 0x719A:
            wait_cycles += 1

    memory.registers = registers
    memory.watched_accesses.clear()
    memory.watched_addresses = frozenset(range(FIXED_START, FIXED_END))
    try:
        run_to(cpu, 0x3D13 if accepted else 0x6F4E, observe)
        assert not memory.watched_accesses
    finally:
        memory.watched_addresses = frozenset()
        memory.registers = None
    assert bytes(memory[FIXED_START:FIXED_END]) == before_fixed
    assert bytes(memory.banks[1][CONTROL_START:CONTROL_END]) == before_control
    expected_stock = list(stock)
    reload_sectors = 0
    frames = 0
    if accepted:
        expected_stock[spending_index] -= spending
        assert sites == [0x7176, 0x4200] and wait_cycles == 128
        assert bytes(memory[STOCK:STOCK + 2]) == bytes(expected_stock)
        assert bytes(memory[0x9BC1:0x9BC6]) == destination
        saved = bytes(memory[0x9BBD:0x9D9E])
        assert bytes(memory[0x4000:0x41E1]) == saved
        assert bytes(memory[0x5CDD:0x5CE6]) == b'ACTION  C'
        cpu.set_tracer(ports)
        first = len(ports.attempts)
        run_with_rom(cpu, basic, dos, set_rom, 0x6000, step_limit=5_500_000)
        assert bytes(memory[0x9BBD:0x9D9E]) == saved
        set_rom(basic)
        run_with_rom(cpu, basic, dos, set_rom, 0xA82D, step_limit=5_500_000)
        expected_reads = file_sectors(17) + file_sectors(18)[:1]
        for slot in (25, 20, 21, 22, 23, 24):
            expected_reads += file_sectors(slot)
        assert [sector for sector in ports.attempts[first:] if sector[0]] == expected_reads
        reload_sectors = len(expected_reads)
        assert bytes(memory.banks[1][CONTROL_START:CONTROL_END]) == before_control
        set_rom(basic)
        cpu.run(0xA82D, 0xA85E, interrupts=True)
        if finish_first_frame:
            cpu.run(0xA85E, 0xA85E, interrupts=True)
            frames = 1
        assert memory.o7ffd == 0x10 and registers[SP] == 0xBFFC
    else:
        assert not sites and not wait_cycles and registers[F] & 1
        assert bytes(memory[0x9BC1:0x9BC6]) == current
        run_to(cpu, 0x6F55, lambda _: key.observe(1, memory, registers))
        key.observe(1, memory, registers)
        assert key.finished and key.returns == 1
    assert bytes(memory[STOCK:STOCK + 2]) == bytes(expected_stock)
    return dict(initial_stock=list(stock), purchased_trail=0xFE, fuel_prices=prices[:2],
                initial_context=current.hex(), selected_context=destination.hex(), measured_cost=cost,
                selected_fuel_index=spending_index, required_fuel=spending, accepted=accepted,
                rejected_other_fuel_row=incompatible_fuel_row,
                final_stock=expected_stock, warmup_iterations=wait_cycles, relay_entries=sites,
                reload_data_sectors=reload_sectors, complete_frames_after_reload=frames,
                fixed_legacy_accesses_before_dos=0, old_control_code_fetches_before_dos=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    assert len(basic) == len(dos) == 0x4000
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    profiles = []
    for stock in ((0, 5), (9, 0), (7, 0)):
        check = partial(check_flight, stock=stock, symbols=symbols)
        result = check_intro_transition(basic, dos, 0, mark_context=False, flight_check=check)
        profiles.append(result['flight_transition'])
    assert [profile['accepted'] for profile in profiles] == [True, True, False]
    report = dict(passed=True, disk_sha256=sha256(DISK).hexdigest(), dos_rom_sha256=sha256(dos).hexdigest(),
                  purchase_ship_type_and_credits_fixture=True, map_key_selected_via_center_command=True,
                  flight_request_state_patched=False, irq_executed_during_frames=True,
                  irq_executed_during_request_or_warmup=False, trdos_calls_substituted=False,
                  assembly_executed=False, native_execution=False, profiles=profiles)
    target = ROOT / 'Tools/Disasm/Reports/PurchasedHyperJumpVerification.json'
    target.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print('Проверены две оплаты и отказ через исходные покупки, карту, клавиатуру и TR-DOS')


if __name__ == '__main__':
    main()
