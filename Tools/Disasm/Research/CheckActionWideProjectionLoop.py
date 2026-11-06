"""Полный обход 6B16 с настоящими ветками преобразования и отрисовки."""
from collections import Counter
from itertools import product
import json
from random import Random

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import COEFFICIENTS, OUTPUTS
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionPatchedVector import evaluate


def signed(value, bits):
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    rng = Random(0x6B16)
    counts = Counter()
    for count, equal, selected, scenario in product(range(7), (False, True), (0, 1, 3, 5, 255), range(8)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)

        def put(address, value, size=2):
            for offset, byte in enumerate(value.to_bytes(size, 'little')):
                memory[address + offset] = byte

        def word(address):
            return memory[address] | memory[address + 1] << 8

        stack, original_iy = 0xBFFE, 0xA789
        put(stack, 0x3FFF)
        memory[0x688B] = count
        memory[0x9BCA] = selected
        put(0x9BC1, 0x7531)
        put(0x9BC3, 0x2468)
        put(0x9BC6, 0x7531 if equal or scenario & 1 else 0x7532)
        put(0x9BC8, 0x2468 if equal else 0x2469)
        rows = []
        matrix = ((0, 0, 0), (0, 0, 0), (0, 0, 0)) if scenario == 0 else tuple(
            tuple(rng.randrange(256) for _ in range(3)) for _ in range(3))
        for addresses, values in zip(COEFFICIENTS, matrix):
            for address, value in zip(addresses, values):
                memory[address] = value
        for index in range(count):
            near = (scenario + index) % 3 != 0
            values = tuple(rng.randrange(-60, 60) * 65536 + rng.randrange(65536) for _ in range(3)) if near else (
                rng.randrange(60, 32768) * 65536, rng.randrange(-(1 << 31), 1 << 31), rng.randrange(-(1 << 31), 1 << 31))
            values = tuple(value & 0xFFFFFFFF for value in values)
            rows.append(values)
            for axis, value in enumerate(values):
                put(0x9B27 + 12 * index + 4 * axis, value, 4)
        sim.registers[:] = get_registers({'PC': 0x6B16, 'SP': stack, 'IY': original_iy}, None, False)
        outputs = [word(address) for address in OUTPUTS]
        index = 0
        published = [128, 128, 128]
        armed = False
        before_draw = None
        expected_ports = []
        context = (count, equal, selected, scenario)
        for _ in range(150000):
            r = sim.registers
            pc = r[PC]
            if pc == 0x3FFF:
                break
            if pc in (0x6B6B, 0x6B42):
                assert index < count and not armed, (context, pc, index)
                values = rows[index]
                near = all(-60 <= signed(value >> 16, 16) <= 59 for value in values)
                assert (pc == 0x6B42) == near, (context, pc, values)
                vector = tuple(((value if near else signed(value, 32) // 16) >> 8) & 65535 for value in values)
                outputs = evaluate(vector, matrix, outputs)['outputs']
                if near:
                    expected_ports.extend(((0x7FFD, 0x11), (0x7FFD, 0x10)))
                    before_draw = bytes(memory.banks[2][:0xC00])
                counts['near' if near else 'far'] += 1
                armed = True
            if pc == 0x6B4B:
                assert armed and [word(address) for address in OUTPUTS] == list(outputs), (context, index)
                if before_draw is not None:
                    changed = bytes(memory.banks[2][:0xC00]) != before_draw
                    counts['draw_changed' if changed else 'draw_unchanged'] += 1
                    before_draw = None
                pointer = 0x9B27 + 12 * index
                countdown = ((selected + 1 if equal else 255) - index) & 255
                assert r[SP] == stack - 8
                assert (word(stack - 8), word(stack - 6), word(stack - 4), word(stack - 2)) == (
                    ((count - index) << 8) | countdown, pointer, 12, original_iy)
                if countdown == 1:
                    published = [value >> 8 for value in outputs]
                    counts['published'] += 1
                index += 1
                armed = False
            sim.run()
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000 and index == count, context
        assert sim.registers[10:12] == [original_iy >> 8, original_iy & 255], context
        assert list(memory[0x9B87:0x9B8A]) == published, (context, published)
        assert trace.writes == expected_ports and memory.o7ffd == 16, context
        counts['cases'] += 1
    assert counts['draw_changed'] and counts['draw_unchanged']
    report = dict(passed=True, total_cases=counts['cases'], outcomes=dict(counts),
                  actual_banked_draw_executed=True, record_counts=list(range(7)),
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionWideProjectionLoopVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
