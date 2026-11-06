"""Общий путь F0F8 до RET или передачи вычислителю 6D06."""
from collections import Counter
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator, get_registers
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import cp_flags, refresh


def profiles():
    for current in range(256):
        for limit in range(256):
            yield False, current, limit, (current + limit) & 255, current ^ limit
    for cls in range(256):
        for state in range(256):
            yield False, (cls * 73 + state) & 255, cls ^ state, cls, state
    for af in range(65536):
        yield True, af & 255, af >> 8, 0, 0


def reference(initial, ix, record):
    r = list(initial)
    if record[1] == 128:
        r[0:2] = [128, cp_flags(128, 128)]
        r[12], r[15], r[24] = r[12] + 2, refresh(r[15], 4), 0x3FFF
        return r, [], 'marker_return'
    current, limit = record[16], record[15]
    candidate = (current + 1) & 255
    advance = candidate < limit
    writes = [(0xB045, record[7]), (0xB04F, (record[8] + 128) & 255), (0xB05C, record[9]),
              (ix + 16, candidate if advance else current)]
    m1 = 30 + int(not advance)
    cls, state = record[18], record[10]
    r[0:2] = [cls, cp_flags(cls, 16)]
    counter = record[36]
    if cls < 16:
        m1 += 4
        r[0:2] = [state, cp_flags(state, 0x13)]
        if state != 0x13:
            counter = 0
            writes.append((ix + 36, 0))
            m1 += 2
    r[4:6] = [counter, current]
    r[15], r[24] = refresh(r[15], m1), 0x6D06
    return r, writes, 'increment' if advance else 'preserve'


def main():
    original = flat_action()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    for marker, current, limit, cls, state in profiles():
        serial = counts.total()
        ix = 0xA100 + 64 * (serial % 16)
        stack = (0x9008, 0xBFFE)[serial & 1]
        record = {1: 128 if marker else (serial & 127), 7: serial & 255, 8: (serial >> 8) & 255,
                  9: (serial * 73) & 255, 10: state, 15: limit, 16: current, 18: cls, 36: (serial * 109) & 255}
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        for offset, value in record.items():
            memory[ix + offset] = value
        memory[stack], memory[stack + 1] = 255, 63
        initial = get_registers({'AF': ((limit << 8) | current) if marker else serial & 65535,
            'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            '^AF': 0xDEF0, 'IX': ix, 'IY': 0x5C3A, 'SP': stack, 'PC': 0xF0F8}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, (serial * 73) & 255, serial & 1, serial % 3
        wanted, writes, path = reference(initial, ix, record)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        simulator.run(start=0xF0F8, stop=wanted[24])
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, path, record,
            [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
        assert Counter(writes) == Counter(memory.writes) and all(memory[address] == value for address, value in writes)
        touched = {address for address, _ in writes} | {ix + offset for offset in record}
        counts[path] += 1
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), exact_registers_including_R=True,
        all_counter_limit_pairs=True, all_class_state_pairs=True, all_AF_at_marker_return=True,
        exact_write_multiplicity=True, actual_operand_updates=True, stopped_before_6D06=True,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionObjectOffsetTransferVerification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
