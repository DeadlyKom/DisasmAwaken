"""Сдвиг хвоста после открытия исходных панелей в загруженной станции."""
import json

from CheckInitialZeroTailAccesses import WatchedCPU
from CheckStationFlightCycle import payload, put, run_to
from CheckScreenUpdate import PortTrace
from TraceFlight import D, E, PC, ROOT, SP, main as trace
from skoolkit.pagingtracer import SliceableMemory


FIRST = 0xF472
SHIFT = 128
RETURN_SENTINEL = 0x3FFF


class DrawMemory(SliceableMemory):
    active = False

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.reads = []
        self.writes = []

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.active and isinstance(address, int) and address >= FIRST and self.o7ffd & 7 == 0:
            self.reads.append((self.registers[PC], address, value))
        return value

    def __setitem__(self, address, value):
        if self.active and address >= FIRST and self.o7ffd & 7 == 0:
            self.writes.append((self.registers[PC], address, value))
        super().__setitem__(address, value)


def word(memory, address):
    return int.from_bytes(memory[address:address + 2], 'little')


def draw_list(memory):
    base = word(memory, 0x9CA6)
    assert base == 0xF3DE
    items = []
    for address in range(base, base + 2 * 47, 2):
        handler = word(memory, address)
        if handler >> 8 == 1:
            return items
        items.append((address, handler, word(memory, handler + 1)))
    raise AssertionError('Не найден ограничитель списка')


def main():
    memory = DrawMemory()
    put(memory, 0x6000, payload(4))
    cpu = WatchedCPU(memory, {'PC': 0x6300, 'SP': 0x5FFF, 'IY': 0x5C3A})
    memory.registers = cpu.registers
    model = trace(['--region', 'station', '--frames', '8'], boot_simulator=cpu, save_reports=False)
    assert model['reason'] == 'requested_frame_entries' and memory.o7ffd == 0x10
    assert len(draw_list(memory)) == 10
    assert not memory.reads and not memory.writes
    banks = [bank.copy() for bank in memory.banks]
    initial = cpu.registers[:]
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())

    def invoke(name, index=0):
        registers = cpu.registers
        registers[PC], registers[SP] = symbols['Station.' + name + '.Entry'], 0x5FFD
        registers[D], registers[E] = divmod(index, 256)
        put(memory, 0x5FFD, RETURN_SENTINEL.to_bytes(2, 'little'))
        cpu.set_tracer(PortTrace(cpu))
        run_to(cpu, RETURN_SENTINEL)
        assert registers[SP] == 0x5FFF and memory.o7ffd == 0x10

    cases = []
    for name, count, item in (
        ('OpenMapPanelGroup', 21, 20), ('OpenHelpPanels', 12, 22),
        ('OpenEquipmentPanels', 14, 38), ('OpenShipPanels', 16, 26),
        ('OpenContractPanels', 13, 32), ('OpenGameOptions', 11, 42),
    ):
        for bank, baseline in zip(memory.banks, banks):
            bank[:] = baseline
        memory.out7ffd(0x10)
        cpu.registers[:] = initial
        memory.reads.clear()
        memory.writes.clear()
        invoke(name)
        current = draw_list(memory)
        address, _, index = current[-1]
        assert (len(current), index) == (count, item)
        assert not memory.reads and not memory.writes
        source = address + 2
        expected = bytes(memory[source:source + SHIFT])
        invoke('RemoveItemDraw', index)
        assert draw_list(memory) == current[:-1]
        assert bytes(memory[address:address + SHIFT]) == expected
        assert memory.reads == [(0xCB48, pos, expected[pos - source])
                                for pos in range(FIRST, source + SHIFT)]
        assert memory.writes == [(0xCB48, pos, expected[pos - address])
                                 for pos in range(FIRST, address + SHIFT)]
        cases.append(dict(opener=name, entries=count, removed_index=item,
                          read_first=FIRST, read_end=source + SHIFT, write_end=address + SHIFT))
    end = max(row['read_end'] for row in cases)
    assert end == 0xF488 and payload(4)[FIRST - 0x6000:end - 0x6000] == bytes(end - FIRST)
    report = dict(passed=True, cases=cases, observed_original_tail_bytes=end - FIRST,
                  maximum_observed_read_end=end, maximum_observed_write_end=end - 2,
                  actual_initial_station_and_original_openers=True, selected_removal_is_fixture=True,
                  maximum_possible_extent_proved=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/StationExpandedDrawTailVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'{len(cases)} сценариев, ещё {end - FIRST} исходных байтов читаемого хвоста')


if __name__ == '__main__':
    main()
