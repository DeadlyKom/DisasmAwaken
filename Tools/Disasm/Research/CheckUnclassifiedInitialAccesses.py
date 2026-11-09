"""Обращения к неизвестным дисковым байтам при начальной загрузке станции и ACTION."""
from collections import Counter, defaultdict
import hashlib
import json

from CheckInitialZeroTailAccesses import WatchedCPU
from TraceFlight import Memory, PC, ROOT, main as trace


class RangeMemory(Memory):
    active = False

    def __init__(self, source, ranges):
        super().__init__(out7ffd=0x10)
        self.lookup = [None] * 65536
        self.first = defaultdict(dict)
        self.visits = defaultdict(Counter)
        self.source = source
        for index, row in enumerate(ranges):
            start = 0x6000 + row['offset']
            for address in range(start, start + row['length']):
                self.lookup[address] = index

    def observe(self, address, mode, value):
        if not self.active or (address >= 0xC000 and self.o7ffd & 7):
            return
        index = self.lookup[address]
        if index is None:
            return
        pc = self.registers[PC]
        code_bank = (self.o7ffd & 7) if pc >= 0xC000 else None
        self.visits[index][mode, pc, code_bank] += 1
        self.first[index].setdefault(address, (mode, pc, value, self.source[address - 0x6000]))

    def __getitem__(self, address):
        value = super().__getitem__(address)
        self.observe(address, 'read', value)
        return value

    def __setitem__(self, address, value):
        self.observe(address, 'write', value)
        super().__setitem__(address, value)


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    source_map = (reports / 'SourceMap.json').read_bytes()
    source_ranges = json.loads(source_map)
    profiles = {}
    for profile, slot, filename, entry, frames in (
        ('station', 4, '04_STATIONF.C.bin', 0x6300, 8),
        ('flight', 17, '17_ACTION.C.bin', 0x6000, 65),
    ):
        source = (ROOT / 'Tools/Disasm/Extracted/Active' / filename).read_bytes()
        assert len(source) == 0xA000
        ranges = [row for row in source_ranges if row['slot'] == slot and row['kind'] == 'unclassified']
        memory = RangeMemory(source, ranges)
        for address, value in enumerate(source, 0x6000):
            memory[address] = value
        cpu = WatchedCPU(memory, {'PC': entry, 'SP': 0x5FFF, 'IY': 0x5C3A},
                         config={'fast_ldir': False, 'fast_djnz': False})
        memory.registers = cpu.registers
        result = trace(['--region', profile, '--frames', str(frames)], boot_simulator=cpu,
                       save_reports=False)
        assert result['reason'] == 'requested_frame_entries' and result['frame_entries'] == frames
        touched = []
        for index, by_address in sorted(memory.first.items()):
            row = ranges[index]
            first = Counter((mode, pc, value == initial) for mode, pc, value, initial in by_address.values())
            touched.append(dict(path=row['path'], file_offset=row['offset'], total_bytes=row['length'],
                addresses_reached=len(by_address), addresses=sorted(by_address),
                first=[dict(mode=mode, pc=pc, value_matches_initial=matches, distinct_addresses=count)
                       for (mode, pc, matches), count in sorted(first.items())],
                accesses=[dict(mode=mode, pc=pc, instruction_bank=bank, count=count)
                          for (mode, pc, bank), count in sorted(memory.visits[index].items())]))
        profiles[profile] = dict(frame_entries=frames, checked_ranges=len(ranges),
                                 touched_ranges=touched)
    proof = dict(passed=True, method='actual_cpu_accesses_at_initial_physical_load_addresses',
                 source_map_sha256=hashlib.sha256(source_map).hexdigest(), profiles=profiles,
                 all_runtime_aliases_tracked=False, semantic_classification_performed=False,
                 trdos_stub=True, native_execution=False, assembly_executed=False)
    (reports / 'UnclassifiedInitialAccesses.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(profiles, indent=2))


if __name__ == '__main__':
    main()
