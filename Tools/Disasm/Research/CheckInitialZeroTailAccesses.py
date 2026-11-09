"""Ограниченная трасса обращений к исходным нулевым хвостам банка 0."""
from collections import Counter
import json

from TraceFlight import Memory, PC, ROOT, Simulator, main as trace


class WatchedMemory(Memory):
    active = False

    def __init__(self, start):
        super().__init__(out7ffd=0x10)
        self.start = start
        self.first = {}
        self.accesses = Counter()

    def observe(self, address, mode, value):
        if self.active and self.o7ffd & 7 == 0 and self.start <= address <= 65535:
            pc = self.registers[PC]
            self.first.setdefault(address, (mode, pc, value))
            self.accesses[mode, pc] += 1

    def __getitem__(self, address):
        value = super().__getitem__(address)
        self.observe(address, 'read', value)
        return value

    def __setitem__(self, address, value):
        self.observe(address, 'write', value)
        super().__setitem__(address, value)


class WatchedCPU(Simulator):
    def run(self, *args, **kwargs):
        self.memory.active = True
        try:
            return super().run(*args, **kwargs)
        finally:
            self.memory.active = False

    def accept_interrupt(self, *args, **kwargs):
        self.memory.active = True
        try:
            return super().accept_interrupt(*args, **kwargs)
        finally:
            self.memory.active = False


def main():
    results = {}
    for region, filename, entry, first, frames in (
        ('station', '04_STATIONF.C.bin', 0x6300, 0xF3F4, 8),
        ('flight', '17_ACTION.C.bin', 0x6000, 0xF866, 65),
    ):
        source = (ROOT / 'Tools/Disasm/Extracted/Active' / filename).read_bytes()
        assert source[first - 0x6000:] == bytes(65536 - first)
        memory = WatchedMemory(first)
        for offset, value in enumerate(source, 0x6000):
            memory[offset] = value
        simulator = WatchedCPU(memory, {'PC': entry, 'SP': 0x5FFF, 'IY': 0x5C3A},
                               config={'fast_ldir': False, 'fast_djnz': False})
        memory.registers = simulator.registers
        report = trace(['--region', region, '--frames', str(frames)], boot_simulator=simulator,
                       save_reports=False)
        assert report['reason'] == 'requested_frame_entries' and report['frame_entries'] == frames
        results[region] = dict(first_address=f'{first:04X}', frame_entries=frames,
                               accesses=[dict(mode=mode, pc=f'{pc:04X}', count=count)
                                         for (mode, pc), count in sorted(memory.accesses.items())],
                               first_accesses={f'{address:04X}': dict(mode=mode, pc=f'{pc:04X}', value=value)
                                               for address, (mode, pc, value) in sorted(memory.first.items())})
    report = dict(passed=True, regions=results, real_software_instructions=True,
                  TR_DOS_read_substituted=True, inactive_regions_proved=False,
                  other_inputs_or_frames_proved=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/InitialZeroTailAccesses.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({region: {k: v for k, v in row.items() if k != 'first_accesses'} |
                      {'distinct_addresses': len(row['first_accesses'])}
                      for region, row in results.items()}, indent=2))


if __name__ == '__main__':
    main()
