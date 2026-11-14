"""Обращения торговли к цене приобретения, исходные события 9..11 без подмены LANG.

Документация: ../../../Docs/CargoField.md
Документация: ../../../Docs/OriginalTradeScript.md
"""
from collections import Counter
from itertools import product
from hashlib import sha256
import json

from CheckOriginalTradeScript import (
    ROOT, LangWorkspaceMemory, Simulator, get_registers, PC, SP, A,
    make_context, PortTrace, put, reference, weighted_load,
)

PRICE_ADDRESSES = tuple(0x9853 + 2 * index for index in range(30))
PROFILES = (
    (10, 3, 5, 1000, 255), (0, 0, 5, 1000, 255),
    (128, 3, 5, 1000, 255), (10, 3, 255, 0, 255),
    (10, 3, 5, 1000, 0), (10, 120, 5, 1000, 255),
    (10, 128, 5, 65000, 255), (10, 3, 255, 65535, 255),
)


class PriceMemory(LangWorkspaceMemory):
    """Наблюдение всех тридцати физических полей Price в фиксированном банке 2."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.price_recording = False
        self.price_reads = []
        self.price_writes = []

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.price_recording and isinstance(address, int) and address in PRICE_ADDRESSES:
            self.price_reads.append((self.registers[PC], address, value))
        return value

    def __setitem__(self, address, value):
        if self.price_recording and address in PRICE_ADDRESSES:
            self.price_writes.append((self.registers[PC], address, value))
        super().__setitem__(address, value)


def probe():
    memory = PriceMemory(banks=[[0] * 16384 for _ in range(8)], out7ffd=0x16)
    # Проверка чтения и записи реальными инструкциями CPU для каждого наблюдаемого адреса.
    for address in PRICE_ADDRESSES:
        memory.price_recording = False
        put(memory, 0x4000, bytes((0x3A, address & 255, address >> 8,
                                  0x32, address & 255, address >> 8)))
        memory[address] = 0x6B
        cpu = Simulator(memory)
        cpu.registers[PC] = 0x4000
        memory.registers = cpu.registers
        memory.price_reads.clear()
        memory.price_writes.clear()
        memory.price_recording = True
        cpu.run()
        cpu.run()
        memory.price_recording = False
        assert memory.price_reads == [(0x4000, address, 0x6B)]
        assert memory.price_writes == [(0x4003, address, 0x6B)]


def main(all_skimmers=False):
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    sources = {}
    # Проверка всех файлов фикстуры по исходным физическим секторам, включая хвост LANG.
    for slot in (4, 5, 7):
        entry = next(row for row in manifest['entries'] if row['slot'] == slot)
        source = (ROOT / (entry['path'] + '.sectors.bin')).read_bytes()
        assert source == disk[entry['offset']:entry['offset'] + entry['allocated_length']]
        sources[slot] = source
    _, _, banks = make_context()
    lang = sources[5]
    banks[6][:len(lang)] = lang
    probe()
    counts = Counter()
    for index in range(30):
        for event in (9, 10, 11):
            for skimmer, (profile, (stock, cargo, price, credits, capacity)) in product(
                    (255, 0, 1, 2, 3) if all_skimmers else (255,), enumerate(PROFILES)):
                outcomes = []
                for pattern in range(3):
                    memory = PriceMemory(banks=[bank.copy() for bank in banks], out7ffd=0x16)
                    cpu = Simulator(memory)
                    tracer = PortTrace(cpu)
                    cpu.set_tracer(tracer)
                    memory.registers = cpu.registers
                    memory[0x6306], memory[0x983A] = 0x16, event
                    memory[0x7026], memory[0x7068] = index // 2, index - index // 2
                    memory[0x984A], memory[0x9851] = skimmer, capacity
                    for address, size in ((0x9852, 60), (0x988E, 52), (0x98F6, 14)):
                        put(memory, address, bytes(size))
                    sentinels = tuple(0 if pattern == 0 else 255 if pattern == 1
                                      else (73 * row + 19) & 255 for row in range(30))
                    for address, value in zip(PRICE_ADDRESSES, sentinels):
                        memory[address] = value
                    memory[0x9555 + 2 * index] = stock
                    memory[0x9556 + 2 * index] = price
                    memory[0x9852 + 2 * index] = cargo
                    put(memory, 0x984E, credits.to_bytes(2, 'little'))
                    put(memory, 0x6E8B, [10, 0])
                    put(memory, 0x9CA6, [0xDE, 0xF3])
                    put(memory, 0xF3DE, [0x8A, 0x6E, 1, 1])
                    memory[0x9A82] = memory[0x6E91] = 0xA7
                    load = weighted_load(bytearray(memory[0:65536]), index)[0]
                    put(memory, 0x7FFE, [255, 63])
                    cpu.registers[:] = get_registers(dict(PC=0xC000, SP=0x7FFE,
                        IX=0x2468, IY=0x5C3A), None, False)
                    observed = []
                    memory.price_recording = True
                    for _ in range(220000):
                        if cpu.registers[PC] == 0x3FFF:
                            break
                        if cpu.registers[PC] == 0xA85F:
                            observed.append(cpu.registers[A])
                        cpu.run()
                    else:
                        raise AssertionError(('Торговля не вернулась', index, event, profile, pattern))
                    memory.price_recording = False
                    # Проверка отсутствия обращений, сохранности полей и независимых итогов сделки.
                    assert memory.price_reads == [] and memory.price_writes == []
                    assert tuple(memory[address] for address in PRICE_ADDRESSES) == sentinels
                    expected = reference(event, stock, cargo, price, credits, load, capacity)
                    actual = (memory[0x9555 + 2 * index], memory[0x9852 + 2 * index],
                              memory[0x984E] + 256 * memory[0x984F])
                    assert actual == expected[:3] and observed == expected[3]
                    assert cpu.registers[SP] == 0x8000 and memory.o7ffd == 0x16
                    assert memory.banks[6][0x28] == int(expected[4])
                    assert bytes(memory.banks[6][0xA8F:len(lang)]) == lang[0xA8F:]
                    outcomes.append((actual, observed, list(cpu.registers), tracer.writes))
                    if all_skimmers:
                        counts['skimmer_' + str(skimmer)] += 1
                    counts['cases'] += 1
                    counts['event_' + str(event)] += 1
                    counts['stopped' if expected[4] else 'continued'] += 1
                # Проверка одинаковых регистров, сообщений и OUT при трёх разных массивах Price.
                assert outcomes[0] == outcomes[1] == outcomes[2]
    assert counts['cases'] == (10800 if all_skimmers else 2160)
    result = dict(passed=True, counts=dict(counts), original_disk_sha256=manifest['sha256'],
        original_physical_files_checked=[4, 5, 7], CPU_read_write_probes=30,
        watched_price_addresses=list(PRICE_ADDRESSES), patterns=['zero', 'FF', '73*row+19 modulo 256'],
        events=[9, 10, 11], profiles=[list(row) for row in PROFILES],
        original_interpreter_and_trade_script_executed=True, price_CPU_reads=0, price_CPU_writes=0,
        all_30_prices_preserved=True, exact_registers_messages_and_OUT_equal_between_price_patterns=True,
        stock_quantity_credits_and_messages_match_arithmetic_reference=True,
        skimmer_index_prepared_FF=not all_skimmers, full_LANG_sector_tail_loaded_as_fixture=True,
        all_RAM_or_all_input_combinations_compared=False, native_reachability_proved=False,
        global_price_consumers_or_writers_excluded=False, station_display_executed=False,
        IRQ_executed=False, assembly_executed=False, native_execution=False)
    target = ROOT / 'Tools/Disasm/Reports/CargoPriceTradeAccessVerification.json'
    if all_skimmers:
        result.update(skimmer_indices=[255, 0, 1, 2, 3],
                      all_four_physical_skimmer_record_indices_tested=True)
        target = ROOT / 'Tools/Disasm/Reports/CargoPriceTradeAllSkimmersVerification.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, counts=dict(counts), price_reads=0, price_writes=0)))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-skimmers', action='store_true')
    main(parser.parse_args().all_skimmers)
