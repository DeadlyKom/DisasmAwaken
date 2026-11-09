"""Фактические чтения обеих страниц диспетчера KARTA перед JP (HL)."""
from itertools import product
import json

from CheckClipSegment import record
from CheckInitialZeroTailAccesses import WatchedCPU
from CheckStationFlightCycle import payload
from TraceFlight import H, L, PC, ROOT, SP


class TableMemory(bytearray):
    active = False

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.active and isinstance(address, int) and self.registers[PC] in (0xD4D2, 0xD4D4):
            self.reads.append((self.registers[PC], address, value))
        return value


def main():
    data = payload(7)
    memory = TableMemory(65536)
    memory[0xC000:0xC000 + len(data)] = data
    memory[0x7FFE:0x8000] = bytes.fromhex('FF 3F')
    cpu = WatchedCPU(memory, {'SP': 0x7FFE})
    memory.registers = cpu.registers
    initial = cpu.registers[:]
    expected = json.loads((ROOT / 'Tools/Disasm/Reports/MapClipDispatch.json').read_bytes())
    targets = {row['index']: row['target'] for row in expected['pairs']}

    def dispatch(points, index, start):
        memory[0xDE2F:0xDE39] = points
        cpu.registers[:] = initial
        memory.reads = []
        cpu.run(start=start, stop=0xD4DC)
        reads = [(pc, address, value) for pc, address, value in memory.reads if address != pc]
        low, high = memory[0xDE00 + index], memory[0xDF00 + index]
        assert reads == [(0xD4D2, 0xDE00 + index, low), (0xD4D4, 0xDF00 + index, high)]
        assert cpu.registers[H] * 256 + cpu.registers[L] == low + 256 * high
        assert cpu.registers[SP] == 0x7FF8 and memory[0x7FF8:0x7FFE] == bytes.fromhex('DD D4') * 3
        return low + 256 * high

    def representative(code):
        return (-1 if code & 2 else 255 if code & 1 else 127,
                -1 if code & 8 else 255 if code & 4 else 127)

    normal_indices = set()
    for first, second in product(expected['valid_outcodes'], repeat=2):
        index = (first * 16 + second) if first else second * 16
        pair = record(representative(first)) + record(representative(second))
        assert dispatch(pair, index, 0xD48B) == targets[index]
        normal_indices.add(index)
    assert len(normal_indices) == 73

    # Неподдерживаемые коды используются только для проверки адреса чтения.
    # Начало PickCase позволяет задать все индексы без обмена первой точки.
    for index in range(256):
        pair = bytes((0x11, 0x22, 0x33, 0x44, (~index & 0xF0),
                      0x55, 0x66, 0x77, 0x88, index & 15))
        dispatch(pair, index, 0xD4BD)
    report = dict(passed=True, original_pairs=len(targets), valid_dispatch_cases=81,
                  effective_indices=sorted(normal_indices), all_index_reads=256,
                  bank='KARTA', low_page=0xDE00, high_page=0xDF00,
                  handler_jumps_executed=False, invalid_pairs_playable_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/MapClipTablePagesVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('81 обычная пара, 73 индекса после обмена, 256 пар чтений перед JP (HL)')


if __name__ == '__main__':
    main()
