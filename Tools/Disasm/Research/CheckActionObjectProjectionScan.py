"""Чтение записей от E0E4 до вычислителя или передачи в очередь."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(flat_action())
    sim = Simulator(memory)
    outcomes = Counter()
    start = 0xA100
    for axis, high, low, angles in product(range(3), range(256), (0, 127, 128, 255),
                                          ((0, 17, 0), (0, 0, 1), (1, 0, 0))):
        fields = [0x1234, 0xFFFF, 0x0102]
        fields[axis] = high << 8 | low
        rows = [fields, [0x80FF, 0, 0]]
        for index, values in enumerate(rows):
            pointer = start + index * 64
            data = b''.join(value.to_bytes(2, 'little') for value in values)
            data += bytes((0x2C, *angles))
            memory[pointer:pointer + len(data)] = list(data)
            memory[pointer + 27] = 0

        writes = []
        destination = 0xE4A6
        end_stack = start + 66

        def put(address, value):
            writes.extend(((address, value & 255), (address + 1, value >> 8)))

        for index, values in enumerate(rows):
            pointer = start + index * 64
            writes.append((pointer + 27, 128))
            if values[0] >> 8 == 128:
                if values[0] & 128:
                    end_stack = pointer + 2
                    outcome = 'end_marker'
                    break
                continue
            for position, value in enumerate(values):
                put(0x9B8F + 2 * position, value)
                upper = value >> 8
                if min(upper, 256 - upper) >= 112:
                    break
                put((0xAF48, 0xAF56, 0xAF69)[position], value)
            else:
                writes.extend(((0x9B8E, 0x2C), (0x9B12, angles[0]), (0x9B13, angles[1]),
                               (0x9B14, angles[2]), (0x9B8D, int(not (angles[0] | angles[2])))))
                destination = 0xAF43
                end_stack = pointer + 10
                outcome = 'transform'
                break
        sim.registers[:] = get_registers({'PC': 0xE0E4, 'SP': 0xBFFE, 'HL': start, 'BC': 64}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(140):
            if sim.registers[PC] in (0xAF43, 0xE4A6):
                break
            sim.run()
        memory.recording = False
        context = (axis, high, low, angles)
        assert sim.registers[PC] == destination and sim.registers[SP] == end_stack, context
        assert memory.writes == writes, (context, memory.writes, writes)
        if destination == 0xAF43:
            assert sim.registers[10:12] == [0xE1, 0x4C], context
        outcomes[outcome] += 1
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  all_high_bytes_each_axis=True, exact_write_order=True,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionObjectProjectionScanVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
