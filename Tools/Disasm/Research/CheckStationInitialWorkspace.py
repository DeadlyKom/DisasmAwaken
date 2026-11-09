"""Первые обращения к физическим байтам рабочих областей станции в модели загрузки."""
from collections import Counter
import json

from CheckScreenUpdate import put
from TraceFlight import Memory, PC, ROOT, Simulator, main as trace


class WatchedMemory(Memory):
    active = False

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.first = {}
        self.execution = set()

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.active and 0x8238 <= address < 0x8900:
            self.first.setdefault(address, ('read', self.registers[PC], value))
        return value

    def __setitem__(self, address, value):
        if self.active and 0x8238 <= address < 0x8900:
            self.first.setdefault(address, ('write', self.registers[PC], value))
        super().__setitem__(address, value)


class WatchedCPU(Simulator):
    def run(self, *args, **kwargs):
        pc = self.registers[PC]
        if 0x8238 <= pc < 0x8900:
            self.memory.execution.add(pc)
        self.memory.active = True
        try:
            return super().run(*args, **kwargs)
        finally:
            self.memory.active = False


def bitmap_row(index):
    return 0x4000 | (index & 0xC0) << 5 | (index & 7) << 8 | (index & 0x38) << 2


def main():
    memory = WatchedMemory()
    source = (ROOT / 'Tools/Disasm/Extracted/Active/04_STATIONF.C.bin').read_bytes()
    put(memory, 0x6000, source)
    simulator = WatchedCPU(memory, {'PC': 0x6300, 'SP': 0x5FFF, 'IY': 0x5C3A},
                           config={'fast_ldir': False, 'fast_djnz': False})
    memory.registers = simulator.registers
    report = trace(['--region', 'station', '--frames', '3'], boot_simulator=simulator, save_reports=False)
    assert report['reason'] == 'requested_frame_entries' and report['frame_entries'] == 3
    assert [item['slot'] for item in report['loads'][:-1]] == [7, 10, 8, 6, 5]
    assert 'offset' in report['loads'][-1] and not memory.execution

    # Начальные значения проверяются до первого изменения, поздние записи интерфейса не смешиваются с ними.
    groups = (
        (0x8238, 0x8300, 'row_high_tail', lambda address: bitmap_row(address & 255) >> 8),
        (0x8300, 0x8400, 'row_low', lambda address: bitmap_row(address & 255) & 255),
        (0x8400, 0x8500, 'column', lambda address: (address & 255) >> 3),
        (0x8500, 0x8580, 'index_first_half', lambda _: 255),
        (0x8600, 0x8900, 'cell_owners', lambda _: 0),
    )
    writers = {}
    for start, end, name, expected in groups:
        pcs = Counter()
        for address in range(start, end):
            mode, pc, value = memory.first[address]
            assert mode == 'write' and value == expected(address), (hex(address), mode, value)
            pcs[f'{pc:04X}'] += 1
        writers[name] = dict(bytes=end - start, writers=dict(pcs))

    retained = {}
    for address in range(0x8580, 0x8600):
        first = memory.first.get(address)
        if first is None:
            continue
        mode, pc, value = first
        assert mode == 'read' and value == source[address - 0x6000]
        retained[f'{address:04X}'] = dict(reader=f'{pc:04X}', original_value=value)
    assert len(retained) == 70
    result = dict(passed=True, total_cases=1, original_station_entry_and_main_loop_executed=True,
                  frame_entries=report['frame_entries'], first_write_groups=writers,
                  initial_index_tail_read_bytes=retained, original_index_tail_not_zeroed_by_reset=True,
                  workspace_instructions_executed=False, TR_DOS_read_substituted=True,
                  other_game_paths_first_access_proved=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/StationInitialWorkspaceVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'initial_index_tail_read_bytes'}, indent=2))


if __name__ == '__main__':
    main()
