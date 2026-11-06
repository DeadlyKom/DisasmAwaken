"""Три исходных обработчика состояний 13..15 до общего продолжения F0F8."""
from collections import Counter
import json
import random

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsCircleSpan import add_flags
from CheckControlsSixRowGauge import inc_flags
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import cp_flags, refresh


def profiles(entry):
    if entry in (0xEF7D, 0xEF9A):
        for offset in range(256):
            for timer in range(256):
                yield {7: offset, 23: timer, 10: (offset + timer) & 255, 22: (offset * 73 + timer) & 255}, 0x11
    else:
        for phase in range(256):
            for counter in range(256):
                yield {18: (phase + counter) & 15, 36: counter, 22: counter ^ phase, 10: 0x13,
                       1: phase, 3: counter, 5: (phase + counter) & 255}, phase
        generator = random.Random(0xEFB5)
        for _ in range(4096):
            yield {offset: generator.randrange(256) for offset in (1, 3, 5, 10, 18, 22, 36)}, generator.randrange(256)


def dec_flags(previous):
    result = (previous - 1) & 255
    return (result & 0xA8) | (64 if result == 0 else 0) | (16 if previous & 15 == 0 else 0) | (4 if previous == 128 else 0) | 2


def reference(entry, initial, record, phase, ix):
    r = list(initial)
    writes = []
    if entry in (0xEF7D, 0xEF9A):
        previous = record[7]
        rising = entry == 0xEF7D
        carry = (add_flags(previous, 2) if rising else sub8_flags(previous, 2)) & 1
        timer = (record[23] - 1) & 255
        writes.extend(((ix + 7, (previous + (2 if rising else -2)) & 255), (ix + 23, timer)))
        r[0:2] = [timer, dec_flags(record[23]) | carry]
        m1 = 11
        path = 'countdown'
        if timer == 0:
            writes.append((ix + 10, 0x15 if rising else record[22]))
            if rising:
                writes.append((ix + 23, 30))
            else:
                r[0] = record[22]
            m1 += 5
            path = 'transition'
    else:
        cls = record[18]
        m1 = 4
        r[0:2] = [cls, cp_flags(cls, 8)]
        release = cls >= 8
        path = 'class_release' if release else 'continue'
        if not release:
            writes.append((0xEFBD, (phase >> 1) | ((phase & 1) << 7)))
            m1 += 4
            if phase & 1:
                m1 += 4
                if record[36] < 15:
                    writes.append((ix + 36, record[36] + 1))
                    m1 += 3
            folded = [value ^ (255 if value & 128 else 0) for value in (record[1], record[3], record[5])]
            x, y, z = folded
            r[2:4] = [y, x]
            m1 += 14 + sum(bool(record[offset] & 128) for offset in (1, 3, 5))
            m1 += 6 + int(z < y) + int(max(z, y) < x)
            maximum = max(folded)
            r[0:2] = [maximum, cp_flags(maximum, 20)]
            release = maximum < 20
            if release:
                path = 'component_release'
        if release:
            r[0] = record[22]
            writes.extend(((ix + 10, record[22]), (ix + 36, 0)))
            m1 += 7
    r[15], r[24] = refresh(initial[15], m1), 0xF0F8
    return r, writes, path


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(bank) for bank in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, paths = Counter(), Counter()
    touched = set()
    for entry in (0xEF7D, 0xEF9A, 0xEFB5):
        for record, phase in profiles(entry):
            serial = counts.total()
            ix = 0xA100 + 64 * (serial % 16)
            memory.recording = False
            for bank, offset in touched:
                memory.banks[bank][offset] = baseline[bank][offset]
            for offset, value in record.items():
                memory[ix + offset] = value
            memory[0xEFBD] = phase
            initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': ix, 'IY': 0x5C3A,
                'SP': 0xBFFE, 'PC': entry}, None, False)
            initial[14], initial[15], initial[26], initial[27] = serial & 255, (serial * 73) & 255, serial & 1, serial % 3
            wanted, writes, path = reference(entry, initial, record, phase, ix)
            expected = [(0 if address >= 0xC000 else 2, address & 0x3FFF, value) for address, value in writes]
            simulator.registers[:] = initial
            trace = PortTrace(simulator)
            simulator.set_tracer(trace)
            memory.writes = []
            memory.recording = True
            simulator.run(start=entry, stop=0xF0F8)
            memory.recording = False
            compared = (*range(25), 26, 27)
            assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, hex(entry), record, phase, path,
                [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
            assert Counter(expected) == Counter(memory.writes), (serial, 'writes')
            final = dict(writes)
            assert all(memory[address] == value for address, value in final.items())
            assert not trace.writes and memory.o7ffd == 16
            touched = {(bank, offset) for bank, offset, _ in expected}
            touched.update((2, (ix + offset) & 0x3FFF) for offset in record)
            touched.add((0, 0x2FBD))
            counts[f'{entry:04X}'] += 1
            paths[f'{entry:04X}_{path}'] += 1
    report = dict(passed=True, total_cases=counts.total(), cases_by_entry=dict(counts), paths=dict(paths),
        exact_registers_including_R=True, exact_write_multiplicity=True, no_cpu_stack_writes=True,
        stops_before_shared_F0F8=True, no_ports=True, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectPhaseHandlersVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
