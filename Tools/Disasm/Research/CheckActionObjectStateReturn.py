"""Возврат F85E, масштаб модели, обновление компонент и переход F735."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


def signed(value):
    return (value ^ 32768) - 32768


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    memory = RecordedBanks(banks=banks, out7ffd=16)
    sim = Simulator(memory)
    outcomes = Counter()

    def put(address, value):
        memory[address], memory[address + 1] = value & 255, value >> 8

    def word(address):
        return memory[address] | memory[address + 1] << 8

    for cls, offset in product(range(256), range(0, 256, 2)):
        pointer = 0xA100 + 64 * ((cls + offset) % 25)
        selected = offset % 5
        values = (0x80FF if selected == 4 else 0x120, 0x302, 0xFEA0)
        active = (29, 0xFFCF, 73)
        bases = [40, 75, 0xFFD8]
        if selected < 3 and cls != 18:
            bases[selected] = 0x7FFF
        for index, address in enumerate((0xE5B0, 0xE5CF, 0xE5EA)):
            put(address, bases[index])
        for address, value in zip((0xE5B3, 0xE5D2, 0xE5ED), active):
            put(address, value)
        for index, value in enumerate(values):
            put(pointer + index * 2, value)
        memory[pointer + 6], memory[pointer + 0x12], memory[pointer + 0x18] = offset, cls, 0
        memory[0x9B82] = 0
        put(0xBFFC, pointer)
        put(0xBFFE, 0x3FFF)
        expected = list(values)
        header = word(0x9E00 + offset)
        exponent = objects[header - 0xC000 + 1]
        bound = 125 - ((200 << (exponent - 1)) >> 8)
        outcome = 'reusable' if values[0] >> 8 == 128 else 'accepted'
        if outcome == 'accepted':
            for index, value in enumerate(values):
                delta = signed(active[index]) // 2 if cls == 20 else signed(active[index])
                result = signed(value) + signed((bases[index] - delta) & 65535)
                upper = (result >> 8) & 255
                if not -32768 <= result < 32768 or min(upper, 255 - upper) >= bound:
                    expected[0] = 0x8000
                    outcome = 'rejected'
                    break
                expected[index] = result & 65535
        sim.registers[:] = get_registers({'PC': 0xF85E, 'SP': 0xBFFC, 'IX': 0xABCD}, None, False)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.run(0xF85E, 0xF735)
        r = sim.registers
        context = (cls, offset, exponent, outcome)
        assert r[PC] == 0xF735 and r[SP] == 0xBFFE and r[8:10] == [pointer >> 8, pointer & 255], context
        assert [word(pointer + index * 2) for index in range(3)] == expected, context
        assert memory[pointer + 0x18] == (255 if outcome == 'rejected' else 0), context
        assert [word(address) for address in (0xE5B3, 0xE5D2, 0xE5ED)] == list(active), context
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 16)]
        outcomes[outcome] += 1
    callback_cases = 0
    for state, timer in product((0x13, 0x14, 0x15), range(256)):
        pointer = 0xA100
        put(pointer, 0x8000)
        memory[pointer + 6] = 0
        memory[pointer + 7] = timer ^ 0x55
        memory[pointer + 10], memory[pointer + 12], memory[pointer + 18] = state, 255, 16
        memory[pointer + 22], memory[pointer + 23], memory[pointer + 36] = 3, timer, 7
        put(0xBFFE, 0x3FFF)
        expected_offset = ((timer ^ 0x55) + (2 if state == 0x14 else -2 if state == 0x15 else 0)) & 255
        expected_state = 3 if state == 0x13 or (state == 0x15 and timer == 1) else 0x15 if state == 0x14 and timer == 1 else state
        expected_timer = timer if state == 0x13 else 30 if state == 0x14 and timer == 1 else (timer - 1) & 255
        sim.registers[:] = get_registers({'PC': 0xF843, 'SP': 0xBFFE, 'IX': pointer}, None, False)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.run(0xF843, 0xF735)
        assert sim.registers[SP] == 0xBFFE and sim.registers[8:10] == [0xA1, 0]
        assert [memory[pointer + offset] for offset in (7, 10, 12, 23, 36)] == [
            expected_offset, expected_state, 0, expected_timer, 0 if state == 0x13 else 7], (state, timer)
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 16)]
        callback_cases += 1
    report = dict(passed=True, total_cases=outcomes.total() + callback_cases, outcomes=dict(outcomes),
                  all_classes_and_even_model_offsets=True, warning_disabled=True,
                  actual_scale_and_update_executed=True, callback_cases=callback_cases,
                  callback_states=[19, 20, 21], callback_reusable_marker=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionObjectStateReturnVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
