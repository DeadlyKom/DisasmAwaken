"""Проверка границ доступа к начальным 64-байтовым записям ACTION."""
from collections import Counter
import json
import re

from CheckScreenUpdate import put
from CheckStationFlightCycle import payload
from TraceFlight import Memory, PC, ROOT, Simulator, main as trace_flight


RECORDS_START = 0xA100
RECORD_SIZE = 0x40
RECORD_COUNT = 26
TAIL_OFFSET = 0x27


class RecordMemory(Memory):
    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.pc = None
        self.accesses = Counter()

    def observe(self, address, operation):
        # Подстановка дисковых загрузок производится исследовательской моделью.
        if self.pc is None or self.pc == 0x3D13 or not isinstance(address, int):
            return
        if RECORDS_START <= address < RECORDS_START + RECORD_SIZE * RECORD_COUNT:
            offset = (address - RECORDS_START) % RECORD_SIZE
            self.accesses[operation, self.pc, offset] += 1

    def __getitem__(self, address):
        self.observe(address, 'read')
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        self.observe(address, 'write')
        super().__setitem__(address, value)


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    regions = {'ActionBoot', 'Action', 'Controls', 'ThreeD', 'Voxel'}
    indexed_operand = re.compile(r'\(I[XY]\s*\+\s*#(?:2[7-9A-F]|3[0-9A-F])\)', re.IGNORECASE)
    flow = json.loads((reports / 'ControlFlow.json').read_bytes())
    checked = {region['name']: len(region['instructions']) for region in flow if region['name'] in regions}
    assert checked.keys() == regions
    assert all(not indexed_operand.search(instruction['operation'])
               for region in flow if region['name'] in regions for instruction in region['instructions'])

    action = payload(17)
    for index in range(RECORD_COUNT):
        start = RECORDS_START - 0x6000 + index * RECORD_SIZE
        assert action[start + TAIL_OFFSET:start + RECORD_SIZE] == bytes(RECORD_SIZE - TAIL_OFFSET)

    memory = RecordMemory()
    put(memory, 0x6000, action)
    cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A},
                    config={'fast_ldir': False, 'fast_djnz': False})

    def observe_instruction(_, memory, registers):
        memory.pc = registers[PC]

    flight = trace_flight(['--verify-flight-cycle', '--frames', '65'], boot_simulator=cpu,
                         save_reports=False, instruction_observer=observe_instruction)
    assert flight['complete_frame_returns'] == 64
    assert not any(offset >= TAIL_OFFSET for _, _, offset in memory.accesses)
    assert memory.accesses['read', 0xE6D3, 1] and memory.accesses['write', 0xE0EC, 0x1B]
    totals = Counter()
    for (operation, _, _), count in memory.accesses.items():
        totals[operation] += count

    report = dict(passed=True, complete_flight_frames=flight['complete_frame_returns'],
                  instruction_counts_by_region=checked, physical_records=RECORD_COUNT,
                  bytes_per_record=RECORD_SIZE, first_tail_field_offset=TAIL_OFFSET,
                  disk_tails_all_zero=True, observed_record_accesses=dict(totals),
                  tail_accesses_in_profile=0, indirect_accesses_in_other_paths_excluded=False,
                  trdos_substituted=True, assembly_executed=False, native_execution=False)
    (reports / 'ActionRecordTailVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
