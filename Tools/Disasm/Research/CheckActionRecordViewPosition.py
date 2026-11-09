"""Связь выходных слов преобразователя с физической записью объекта и радаром."""

from collections import Counter
import json

from CheckScreenUpdate import put
from CheckStationFlightCycle import payload
from TraceFlight import PC, ROOT, Simulator, main as trace
from skoolkit.pagingtracer import SliceableMemory


FIRST, LIMIT, STRIDE = 0xA100, 0xA780, 0x40
WRITERS = {0xE160: (0x1E, 0xD7A2), 0xE164: (0x1C, 0xD7C4), 0xE169: (0x1A, 0xD9B6)}
RADAR = {0xE4CE: 0x1B, 0xE4E0: 0x1D, 0xE4EE: 0x1F}


class RecordMemory(SliceableMemory):
    cpu = None

    def __init__(self):
        super().__init__(out7ffd=16)
        self.writers = Counter()
        self.readers = Counter()
        self.projected = {}

    def __setitem__(self, address, value):
        if self.cpu is not None and FIRST <= address < LIMIT and 0x1A <= address % STRIDE <= 0x1F:
            pc = self.cpu.registers[PC]
            if self.o7ffd & 7 == 0 and pc == 0xE0EC:
                assert address % STRIDE == 0x1B and value == 0x80
                self.projected.pop(address - 0x1B, None)
                self.writers['E0EC'] += 1
            elif self.o7ffd & 7 == 0 and pc in WRITERS:
                offset, source = WRITERS[pc]
                byte_index = address % STRIDE - offset
                assert byte_index in (0, 1)
                assert value == super().__getitem__(source + byte_index)
                record = address - offset - byte_index
                self.projected.setdefault(record, {})[offset + byte_index] = value
                self.writers[f'{pc:04X}'] += 1
        super().__setitem__(address, value)

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.cpu is not None and isinstance(address, int) and FIRST <= address < LIMIT:
            pc = self.cpu.registers[PC]
            if self.o7ffd & 7 == 1 and pc in RADAR:
                offset = RADAR[pc]
                assert address % STRIDE == offset
                record = address - offset
                expected = self.projected.get(record)
                if expected is not None:
                    assert len(expected) == 6 and value == expected[offset]
                    self.readers[f'{pc:04X}'] += 1
        return value


def main():
    memory = RecordMemory()
    put(memory, 0x6000, payload(17))
    cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A})
    memory.cpu = cpu
    result = trace(['--frames', '32'], boot_simulator=cpu, save_reports=False)
    assert result['reason'] == 'requested_frame_entries' and result['frame_entries'] == 32
    assert all(memory.writers[f'{pc:04X}'] > 0 and memory.writers[f'{pc:04X}'] % 2 == 0 for pc in WRITERS)
    assert all(memory.readers[f'{pc:04X}'] > 0 for pc in RADAR)
    report = dict(passed=True, frame_entries=result['frame_entries'], writers=dict(memory.writers),
                  radar_readers=dict(memory.readers), action_bank=0, radar_bank=1,
                  physical_bank=2, original_projection_and_radar_executed=True,
                  disk_calls_substituted=True, irq_executed=False, assembly_executed=False,
                  native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionRecordViewPositionVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
