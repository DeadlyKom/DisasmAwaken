"""Обращения к неизвестным физическим байтам D3D при подготовке и кадрах просмотра."""
from collections import Counter, defaultdict
import hashlib
import json

from CheckInitialZeroTailAccesses import WatchedCPU
from ProbeShipPreviewCallbacks import Fixture, ROOT, make_context, payload, put
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import PC


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    source_map = (reports / 'SourceMap.json').read_bytes()
    ranges = [row for row in json.loads(source_map) if row['slot'] == 6 and row['kind'] == 'unclassified']
    watched = {0xC000 + offset: row['path'] for row in ranges
               for offset in range(row['offset'], row['offset'] + row['length'])}
    accesses = defaultdict(Counter)
    first_access = defaultdict(set)

    class PreviewMemory(SliceableMemory):
        active = False

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.seen = set()

        def bind_registers(self, registers):
            self.registers = registers

        def observe(self, mode, address):
            if not self.active or self.o7ffd & 7 != 4 or address not in watched:
                return
            pc = self.registers[PC]
            accesses[watched[address]][mode, pc, address] += 1
            if address not in self.seen:
                self.seen.add(address)
                first_access[watched[address]].add((mode, pc, address))

        def __getitem__(self, address):
            if isinstance(address, int):
                self.observe('read', address)
            return super().__getitem__(address)

        def __setitem__(self, address, value):
            self.observe('write', address)
            super().__setitem__(address, value)

    _, _, banks = make_context()
    raw = payload(6)
    banks[4][:len(raw)] = list(raw)
    count = frames = irq_count = 0
    for selector, models in ((0, 7), (1, 4)):
        for model in range(models):
            for rectangle in ((1, 1, 16, 12), (3, 2, 24, 18), (1, 1, 2, 3)):
                fixture = Fixture(banks, selector, model, rectangle, memory_type=PreviewMemory, cpu_type=WatchedCPU)
                initial = fixture.run(0x6877)
                count += 1
                irq_count += initial['wakes']
                if rectangle[2] < 4:
                    assert 'E07F' not in initial['seen']
                    continue
                for _ in range(3):
                    put(fixture.memory, 0x7FFE, (255, 63))
                    fixture.sim.registers[:] = fixture.initial
                    fixture.wakes = 0
                    frame = fixture.run(0x68EA)
                    assert frame['seen']['E07F'] == 1
                    frames += 1
                    irq_count += frame['wakes']
    result = dict(passed=True, source_map_sha256=hashlib.sha256(source_map).hexdigest(),
                  watched_ranges=len(ranges), watched_bytes=len(watched), draw_profiles=count,
                  periodic_frames=frames, irq_wakeups=irq_count,
                  touched=[dict(path=path, first=[dict(mode=mode, pc=pc, address=address)
                                                for mode, pc, address in sorted(first_access[path])],
                                accesses=[dict(mode=mode, pc=pc, address=address, count=total)
                                          for (mode, pc, address), total in sorted(entries.items())])
                           for path, entries in sorted(accesses.items())],
                  physical_page=4, real_station_preview_callbacks=True, irq_only_at_explicit_halts=True,
                  all_game_paths_proved=False, assembly_executed=False, native_execution=False)
    (reports / 'PreviewUnclassifiedAccesses.json').write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
