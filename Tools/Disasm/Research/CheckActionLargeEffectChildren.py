"""Создание дочерних записей EA6F с проверкой порядка полей и освобождения."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def main():
    baseline = flat_action()
    baseline[:256] = [(index * 71 + 39) & 255 for index in range(256)]
    memory = Memory(baseline)
    sim = Simulator(memory)
    counts = Counter()
    source = 0xA700
    vector = b'\x12\x23\x34\x45\x56\x67'
    for cls, available, seed, mask in product((0, 8, 15, 16, 255), (0, 1, 3, 6), range(16), (0x40, 0xA0)):
        slots = [0xA100 + 64 * (index * 3 + 1) for index in range(available)]
        memory[0xA100:0xA780] = baseline[0xA100:0xA780]
        for index in range(24):
            memory[0xA101 + 64 * index] = 0x11
        for slot in slots:
            memory[slot], memory[slot + 1] = 0, 128
        memory[source:source + 6] = list(vector)
        memory[source + 0x12] = cls
        memory[0xEAC4] = mask
        memory[0xBFFE:0xC000] = [255, 63]
        sim.registers[:] = get_registers({'PC': 0xEA6F, 'SP': 0xBFFE, 'IX': source}, None, False)
        sim.registers[15] = seed
        memory.writes = []
        memory.recording = True
        requested = 0
        samples, types = [], []
        for _ in range(2500):
            r = sim.registers
            pc = r[PC]
            if pc == 0x3FFF:
                break
            value = refresh(r[15], 2)
            if pc == 0xEA7A:
                requested = 2 + (value & 3)
            elif pc == 0xEAB2:
                samples.append(value)
            elif pc == 0xEABF:
                types.append(value)
            sim.run()
        memory.recording = False
        context = (cls, available, seed, mask)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        if cls < 16:
            assert requested == 2 + ((seed + 7) & 3), context
        else:
            assert not requested, context
        created = min(requested, available)
        assert len(samples) == len(types) == created, context
        writes = []
        for slot, sample, kind in zip(slots[:created], samples, types):
            writes.extend((slot + index, byte) for index, byte in enumerate(vector))
            writes.extend((slot + offset, value) for offset, value in (
                (6, 0xB8), (10, 4), (12, 0), (13, baseline[sample]), (14, baseline[sample + 1]),
                (16, mask | (kind & 31)), (18, 16), (19, 16), (20, 255), (21, 255), (22, 0)))
        writes.extend(((0xECF6, 0x4D), (0xECF7, 0xEE),
                       (source + 1, 128), (source, 0), (source + 24, 255)))
        assert memory.writes == writes, (context, memory.writes, writes)
        counts[created] += 1
    report = dict(passed=True, total_cases=counts.total(), allocations=dict(counts),
                  exact_write_order=True, refresh_samples_observed=True,
                  synthetic_rom_sample_table=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionLargeEffectChildrenVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
