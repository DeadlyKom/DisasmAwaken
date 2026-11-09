"""Проверка обращений после реальных переносов ядер ACTION и STATIONF."""
from collections import Counter
import hashlib
import json

from CheckInitialZeroTailAccesses import WatchedCPU
from TraceFlight import Memory, PC, ROOT, main as trace


class RelocatedMemory(Memory):
    active = False

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.lookup = {}
        self.first = {}
        self.accesses = Counter()

    def observe(self, mode, address, value):
        if not self.active or (address >= 0xC000 and self.o7ffd & 7 != 0):
            return
        binding = self.lookup.get(address)
        if binding is None:
            return
        path, file_offset, original = binding
        pc = self.registers[PC]
        code_bank = self.o7ffd & 7 if pc >= 0xC000 else -1
        self.first.setdefault((path, file_offset), (address, mode, pc, code_bank, value, original))
        self.accesses[path, address, mode, pc, code_bank] += 1

    def __getitem__(self, address):
        value = super().__getitem__(address)
        self.observe('read', address, value)
        return value

    def __setitem__(self, address, value):
        self.observe('write', address, value)
        super().__setitem__(address, value)


def run_profile(region, slot, filename, entry, completed, source_start, target_start, length, frames, source_map):
    raw = (ROOT / 'Tools/Disasm/Extracted/Active' / filename).read_bytes()
    memory = RelocatedMemory()
    for index, value in enumerate(raw, 0x6000):
        memory[index] = value
    cpu = WatchedCPU(memory, {'PC': entry, 'SP': 0x5FFF, 'IY': 0x5C3A},
                     config={'fast_ldir': False, 'fast_djnz': False})
    memory.registers = cpu.registers
    rows = [row for row in source_map if row['slot'] == slot and row['kind'] == 'unclassified']
    installed = False

    def observe(frame, memory, registers):
        nonlocal installed
        if registers[PC] != completed or installed:
            return
        assert bytes(memory[target_start + i] for i in range(length)) == raw[source_start:source_start + length]
        installed = True
        for row in rows:
            for offset in range(row['offset'], row['offset'] + row['length']):
                if source_start <= offset < source_start + length:
                    address = target_start + offset - source_start
                else:
                    address = 0x6000 + offset
                    if target_start <= address < target_start + length:
                        continue
                memory.lookup[address] = (row['path'], offset, raw[offset])

    result = trace(['--region', region, '--frames', str(frames)], boot_simulator=cpu,
                   save_reports=False, instruction_observer=observe)
    assert installed and result['reason'] == 'requested_frame_entries' and result['frame_entries'] == frames
    return dict(frame_entries=frames, watched_addresses=len(memory.lookup),
                first=[dict(path=path, offset=offset, address=address, mode=mode, pc=pc, code_bank=bank,
                            value=value, disk_value=original)
                       for (path, offset), (address, mode, pc, bank, value, original) in sorted(memory.first.items())],
                accesses=[dict(path=path, address=address, mode=mode, pc=pc, code_bank=bank, count=count)
                          for (path, address, mode, pc, bank), count in sorted(memory.accesses.items())])


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    source_map = (reports / 'SourceMap.json').read_bytes()
    decoded = json.loads(source_map)
    profiles = dict(
        station=run_profile('station', 4, '04_STATIONF.C.bin', 0x6300, 0x400B, 0x05CE, 0x6322, 0x1C6A, 8, decoded),
        flight=run_profile('flight', 17, '17_ACTION.C.bin', 0x6000, 0x420C, 0x023D, 0x6000, 0x1F8F, 65, decoded),
    )
    report = dict(passed=True, source_map_sha256=hashlib.sha256(source_map).hexdigest(), profiles=profiles,
                  real_core_relocations_verified=True, trdos_stub=True, no_keys=True,
                  complete_runtime_provenance=False, assembly_executed=False, native_execution=False)
    (reports / 'RelocatedUnclassifiedAccesses.json').write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps({name: dict(watched=profile['watched_addresses'], accessed=len(profile['first']),
                                 instruction_sites=sorted({(row['mode'], row['pc'], row['code_bank'])
                                                           for row in profile['accesses']}))
                      for name, profile in profiles.items()}, indent=2))


if __name__ == '__main__':
    main()
