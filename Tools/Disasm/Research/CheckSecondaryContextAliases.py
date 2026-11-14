"""Чтения после станционной таблицы количеств исходными обработчиками LANG."""
import json
import re

from CheckRowHighlight import ROOT, Simulator, SliceableMemory, make_context, put
from CheckScreenUpdate import PortTrace
from CheckWeightedLoad import reference as weighted_reference
from ProbeShipPreviewCallbacks import payload
from skoolkit.simutils import A, B, D, E, F, H, L, PC, SP, get_registers


QUANTITIES = 0x98F6
TAIL = (0x9904, 0x9905, 0x9907, 0x9909)
SCRIPT_EVENTS_WITHOUT_BLOCK = (3, 4, 7, 8)


class ContextMemory(SliceableMemory):
    def __getitem__(self, address):
        value = super().__getitem__(address)
        if isinstance(address, int) and 0x9904 <= address <= 0x9910:
            self.reads.append((address, self.registers[PC], value))
        if address in (0xC1A7, 0xC86F, 0xAA1D) and self.registers[PC] == address:
            self.script_entries.append(address)
        return value


def main():
    _, _, banks = make_context()
    original = [bytearray(bank) for bank in banks]
    lang = payload(5)
    d3d = payload(6)
    original[6][:len(lang)] = lang
    original[4][:len(d3d)] = d3d
    memory = ContextMemory(banks=[bank.copy() for bank in original], out7ffd=0x16)
    sim = Simulator(memory)
    sim.set_tracer(PortTrace(sim))
    memory.registers = sim.registers

    def prepare(stack_index=None):
        memory.banks = [bank.copy() for bank in original]
        memory.memory = [None, memory.banks[5], memory.banks[2], None]
        memory.out7ffd(0x16)
        stack = 0x7FFE if stack_index is None else 0x7FFC
        sim.registers[:] = get_registers({'SP': stack, 'IX': 0xB000}, None, False)
        put(memory, stack, (255, 63) if stack_index is None else (stack_index, 0xA7, 255, 63))
        memory[0x6306] = 0x16
        memory.reads = []
        memory.script_entries = []

    def run(entry):
        sim.run(start=entry, stop=0x3FFF)
        r = sim.registers
        assert r[SP] == 0x8000 and memory.o7ffd == 0x16
        return r[H] * 256 + r[L], r[A], r[F]

    direct = []
    for address in TAIL:
        index = address - QUANTITIES
        prepare()
        put(memory, 0xB000, str(index + 1).encode() + b'!\r')
        raw = memory[address]
        memory.reads.clear()
        decoded = raw if raw < 128 else raw ^ 255
        assert run(0xC1EC)[:2] == (address, decoded)
        assert memory.reads == [(address, 0xC1DC, raw)]
        quantity_read = memory.reads[0]
        prepare(index)
        maximum = 1 if raw & 0x80 else 127
        assert run(0xC5BB)[:2] == (address, maximum)
        assert memory.reads == [(address, 0xC580, raw)]
        direct.append(dict(address=address, decimal_quantity_index=index + 1, stack_index=index,
                           quantity=decoded, limit=maximum, quantity_read=quantity_read, limit_read=memory.reads[0]))

    # Второй поиск использует исходные границы и имеет 14 допустимых индексов.
    neighbors = []
    for index in range(256):
        prepare(index)
        run(0xC5A9)
        reads = [item for item in memory.reads if item[0] in TAIL]
        if reads:
            assert index >= 14
            neighbors.append(dict(index=index, reads=reads))

    # Значения признака получены реальным банковым запросом, без подмены результата.
    sizes = set()
    for variant in range(256):
        prepare(0)
        put(memory, 0x983F, (0x38, 0x4B, 0x57, 0x13, variant))
        assert run(0xC596)[:2] == (QUANTITIES, 0)
        assert sim.registers[B] == 14 and not memory.reads
        sizes.add(memory[0xC509])
    assert sizes == set(range(1, 17))

    prepare(0)
    put(memory, 0x983F, (0x38, 0x4B, 0x57, 0x13, 0))
    for index in range(7):
        memory[QUANTITIES + 2 * index] = 0
    assert run(0xC596)[:2] == (0x9904, 0)
    assert memory.reads == [(0x9904, 0xC50A, 0x50)]
    forced_threshold = memory.reads[0]

    weighted = []
    for option in range(256):
        prepare()
        memory[0x984A] = option
        expected = weighted_reference(memory, 0)
        memory.reads.clear()
        assert run(0xC86F) == (expected[3], expected[0], expected[1])
        reads = [item for item in memory.reads if item[0] in TAIL]
        if reads:
            assert len(reads) == 1 and reads[0][:2] == (expected[3], 0xC8FD)
            weighted.append(dict(skimmer_index=option, read=reads[0]))
    assert [(item['skimmer_index'], item['read'][0]) for item in weighted] == [
        (0x2C, 0x9905), (0x5F, 0x9905), (0x92, 0x9905), (0xC5, 0x9905), (0xF8, 0x9904), (0xF9, 0x9909),
    ]

    active_script = lang[0xA8F:].split(b'\x00', 1)[0]
    assert set(map(int, re.findall(rb'^\?X=(\d+):\{', active_script.replace(b'\r', b'\n'), re.M))) == {
        1, 2, 5, 6, 9, 10, 11, 15, 16, 17
    }
    price_list = d3d[0x0E99:0x0ECE]
    assert price_list.count(b'\x0D') == 4 and price_list.endswith(b'\x0A')
    market_rows = range(price_list.count(b'\x0D'))
    alias_reads_by_index = {item['skimmer_index']: item['read'] for item in weighted}
    script_profiles = []
    for event in SCRIPT_EVENTS_WITHOUT_BLOCK:
        for skimmer in (*market_rows, 0xFF, *alias_reads_by_index):
            prepare()
            memory[0x983A] = event
            memory[0x984A] = skimmer
            before = bytes(memory[0x9849:0x9850])
            run(0xC000)
            assert bytes(memory[0x9849:0x9850]) == before
            assert memory.script_entries == [0xC86F], (event, skimmer, memory.script_entries)
            aliases = [read for read in memory.reads if read[0] in TAIL]
            expected = [alias_reads_by_index[skimmer]] if skimmer in alias_reads_by_index else []
            assert aliases == expected, (event, skimmer, aliases)
            script_profiles.append(dict(event=event, initial_skimmer=skimmer, alias_reads=aliases))

    report = dict(passed=True, explicit_quantity_and_limit=direct,
                  neighbor_valid_indices_without_tail_reads=14, neighbor_out_of_range_reads=neighbors,
                  threshold_original_key_variants=256, threshold_sizes=sorted(sizes),
                  threshold_forced_first_seven_zero=forced_threshold, weighted_options_checked=256,
                  weighted_tail_reads=weighted, original_market_script_profiles=script_profiles,
                  physical_skimmer_rows=len(market_rows), secondary_selection_entered=False,
                  normal_game_use_of_aliases_proved=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/SecondaryContextAliasesVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', 'utf-8')
    print(f'Проверены 256 признаков ключа, 256 индексов скимера, 256 границ поиска, '
          f'{len(direct)} пары прямых чтений и {len(script_profiles)} профилей исходного сценария.')


if __name__ == '__main__':
    main()
