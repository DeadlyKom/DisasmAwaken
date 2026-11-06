"""Подготовка состояния объекта и передача по EF50 до первой инструкции обработчика."""
from collections import Counter
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsBcdExact import or_flags
from ReferenceControlsPointRespawn import refresh


def profiles():
    for cls in range(256):
        for state in range(256):
            yield 0xF843, cls, state, cls, (cls + state) & 255
            yield 0xF7C6, cls, state, cls, (cls + state) & 255
            yield 0xF7E6, cls, state, cls, (cls * 73 + state) & 255
    for cls in range(16):
        for linked in (0, 255):
            for r in range(256):
                yield 0xF7E6, cls, 2, linked, r
    for r in range(256):
        yield 0xF075, 18, r, 0, r


def reference(initial, memory, entry, cls, state, linked):
    r = list(initial)
    stack = r[12]
    ix = (r[8] << 8) | r[9]
    writes = []
    m1 = 0

    def state_change(value):
        nonlocal state
        state = value
        writes.append((ix + 10, value))

    if entry == 0xF075:
        state_change(10)
        m1 = 3
    elif entry == 0xF7C6:
        m1 = 4
        if cls == 18:
            state_change(10)
            m1 += 3
        else:
            m1 += 2
            if cls < 16:
                m1 += 4
                if state != 7:
                    m1 += 2
                    if state != 6:
                        state_change(5)
                        m1 += 3
    elif entry == 0xF7E6:
        writes.append((ix + 19, r[0]))
        m1 = 6
        if cls < 16:
            m1 += 4
            if state == 2:
                m1 += 4
                r[3] = (linked + 1) & 255
                select = not r[3]
                if r[3]:
                    m1 += 2
                    select = refresh(r[15], m1) < 10
                    m1 += 2 if select else 3
            else:
                m1 += 2
                select = state < 4
                if not select:
                    m1 += 2
                    select = state >= 10
            if select:
                m1 += 6
                if cls == 3:
                    threshold = 0x70
                else:
                    m1 += 3
                    if cls == 0:
                        threshold = 0x75
                    else:
                        m1 += 3
                        threshold = 0x50
                r[3] = threshold
                m1 += 4
                if state != 7:
                    m1 += 2
                    if state != 6:
                        m1 += 2
                        choose_two = refresh(r[15], m1) < threshold
                        m1 += 3 if choose_two else 4
                        state_change(2 if choose_two else 5)
                        m1 += 2
    writes.append((ix + 12, 0))
    offset = (state << 1) & 255
    pointer = 0xEF50 + offset
    target = memory[pointer] | (memory[pointer + 1] << 8)
    flags = (or_flags(offset) & 0xC4) | ((pointer >> 8) & 0x28) | (16 if (0xEF50 & 4095) + offset > 4095 else 0)
    r[0:2] = [target & 255, flags]
    r[4:8] = [0xF8, 0x5E, target >> 8, target & 255]
    r[12], r[15], r[24] = stack - 4, refresh(r[15], m1 + 19), target
    writes.extend(((stack - 2, ix & 255), (stack - 1, ix >> 8), (stack - 4, 0x5E), (stack - 3, 0xF8)))
    return r, writes, state


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(bank) for bank in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, chosen = Counter(), Counter()
    touched = set()
    for entry, cls, state, linked, refresh_value in profiles():
        serial = counts.total()
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        ix = 0xA100 + 0x40 * (serial % 16)
        stack = (0x9008, 0xBFFE)[serial & 1]
        for displacement, value in ((10, state), (11, linked), (12, serial & 255), (18, cls), (19, 0x5A)):
            memory[ix + displacement] = value
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': ix, 'IY': 0x5C3A,
            'SP': stack, 'PC': entry}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, refresh_value, serial & 1, serial % 3
        wanted, writes, selected = reference(initial, memory, entry, cls, state, linked)
        expected = [(2, address & 0x3FFF, value) for address, value in writes]
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        simulator.run(start=entry, stop=0xF85D)
        simulator.run()
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, hex(entry), cls, state, linked, refresh_value,
            [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
        assert Counter(expected) == Counter(memory.writes), (serial, 'writes')
        assert all(memory[address] == value for address, value in writes)
        assert not trace.writes and memory.o7ffd == 16
        touched = {(bank, offset) for bank, offset, _ in expected}
        touched.update((2, (ix + displacement) & 0x3FFF) for displacement in (10, 11, 12, 18, 19))
        counts[f'{entry:04X}'] += 1
        chosen[f'{selected:02X}'] += 1
    report = dict(passed=True, total_cases=counts.total(), cases_by_entry=dict(counts), selected_state_counts=dict(chosen),
        exact_registers_including_R=True, exact_record_and_stack_writes=True, stopped_after_indirect_JP=True,
        all_byte_codes_preserve_original_offset_wrap=True, known_table_words=22, handler_execution_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectStateDispatchVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'selected_state_counts'}, indent=2))


if __name__ == '__main__':
    main()
