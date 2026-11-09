"""Два участка UpdateFrame между вызовами, без подмены вызываемых процедур."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory
from CheckScreenUpdate import PortTrace


def main():
    memory = Memory(flat_action())
    # Проверка исходных шагов, произвольные изменяемые шаги проверяются отдельной моделью.
    assert (memory[0xA8B5],memory[0xA968])==(20,80)
    sim = Simulator(memory)
    totals = {'thresholds': 0, 'events': 0}

    def verify(entry, end, setup, writes, failure, context):
        for address, value in setup.items():
            memory[address] = value
        sim.registers[:] = get_registers({'PC': entry, 'SP': 0xBFFE}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(80):
            if sim.registers[PC] in (0x6054, end):
                break
            sim.run()
        memory.recording = False
        assert sim.registers[PC] == (0x6054 if failure else end), context
        assert sim.registers[SP] == 0xBFFE and memory.writes == writes, (context, memory.writes, writes)

    for first, third, fifth, fourth, inhibit, phase in product(
        range(256), (0, 45, 46, 255), (45, 46), (45, 46), (0, 1), (0, 235, 236, 255)
    ):
        setup = {0xA794: first, 0x6693: fifth, 0x6682: fourth, 0xE507: inhibit,
                 0xA8B3: phase, 0xA8BC: third}
        writes = [(0xE310, 1)]
        failure = fifth >= 46 or fourth >= 46
        if not failure and inhibit:
            writes.append((0xE507, 0))
            failure = first < 40
            if not failure:
                writes.extend(((0xA794, first - 40), (0x664A, 2)))
        if not failure:
            writes.append((0xA8B3, (phase + 20) & 255))
            if phase >= 236 and third < 46:
                writes.extend(((0xA8BC, third + 1), (0x666B, third + 1)))
        verify(0xA883, 0xA8C8, setup, writes, failure, setup)
        totals['thresholds'] += 1

    for first, flags, missing, blink, phase in product(
        range(256), range(8), range(8), (0, 1, 128, 255), (0, 175, 176, 255)
    ):
        setup = {0xA794: first, 0xA78C: flags, 0xA92D: blink, 0xA966: phase}
        setup.update({0x9C1C + index: (255 if missing & (1 << index) else index)
                      for index in range(3)})
        writes = []
        value = first
        failure = False
        if flags & 1:
            writes.extend(((0xA78C, 0), (0xECA9, 0x22), (0xECAA, 0xEF)))
            cost = next((3 - index for index in range(3) if not missing & (1 << index)), 4)
            failure = value < cost
            if not failure:
                value -= cost
                writes.extend(((0xA794, value), (0x664A, 1)))
        if not failure:
            if flags & 2:
                writes.append((0xA92D, (blink >> 1) | ((blink & 1) << 7)))
                if blink & 1:
                    writes.extend(((0xECF6, 0x8F), (0xECF7, 0xED)))
                writes.extend(((0x5A1C, 0x35 if blink & 1 else 5), (0xA78C, 0)))
            else:
                writes.append((0x5A1C, 5))
            if flags & 4:
                writes.append((0xA78C, 0))
                failure = value < 40
                if not failure:
                    value -= 40
                    writes.extend(((0xA794, value), (0x664A, 1)))
            if not failure:
                writes.append((0xA966, (phase + 80) & 255))
                if phase >= 176 and value < 46:
                    writes.extend(((0xA794, value + 1), (0x664A, 1)))
        verify(0xA8EB, 0xA97E, setup, writes, failure, setup)
        totals['events'] += 1

    for counter in range(256):
        decremented = (counter - 1) & 255
        writes = [] if decremented & 128 else [(0xA85F, decremented)]
        verify(0xA85E, 0xA867, {0xA85F: counter}, writes, False, counter)
    totals['entry_countdown'] = 256

    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    paged = RecordedBanks(banks=banks, out7ffd=16)
    banked_sim = Simulator(paged)
    for colour, overlay in product(range(256), range(256)):
        paged.out7ffd(16)
        paged[0xAA8E], paged[0xAA9A] = colour, overlay
        banked_sim.registers[:] = get_registers({'PC': 0xAA8D, 'SP': 0xBFFE}, None, False)
        trace = PortTrace(banked_sim)
        banked_sim.set_tracer(trace)
        banked_sim.run(0xAA8D, 0xAAA3)
        assert banked_sim.registers[SP] == 0xBFFE
        assert bool(banked_sim.registers[1] & 64) == (overlay == 1)
        assert paged[0x5A1A] == (0x15 if colour else 5)
        assert trace.writes == [(0x7FFD, 17)] and paged.o7ffd == 17
    totals['overlay_gate'] = 65536

    report = dict(passed=True, total_cases=sum(totals.values()), by_window=totals,
                  exact_write_order=True, original_page_selector_executed=True,
                  mutable_phase_steps_profile='original_defaults_14_50',assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionFrameGatesVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
