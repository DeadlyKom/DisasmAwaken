"""Порог F792 и штатный возврат большого эффекта через F7BF."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[3][:] = bytes(memory_image()[0xC000:])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    baseline[4][:len(objects)] = objects
    counts = Counter()
    for linked, flags, first, second, value in product((0, 26), (0, 8), (0, 255), (0, 255), range(256)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        memory[0xA106], memory[0xA10B], memory[0xA10C], memory[0xA112], memory[0xA113] = 0, linked, flags, 16, value
        memory[0x9C1A], memory[0x9C1B] = first, second
        threshold = 10
        if linked == 26 and flags & 8:
            threshold = 30 if first != 255 else 60 if second != 255 else 20
        expect_effect = value < threshold
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0xF792, 'SP': 0xBFFE, 'IX': 0xA100}, None, False)
        context = (linked, flags, first, second, value, threshold)
        crossed_gap = False
        for _ in range(400):
            pc = sim.registers[PC]
            if pc in (0xF735, 0xF7E6):
                break
            if pc == 0xEA29:
                assert expect_effect and sim.registers[SP] == 0xBFFC
            if pc == 0xF7BF:
                assert expect_effect and sim.registers[SP] == 0xBFFE
                crossed_gap = True
            sim.run()
        assert sim.registers[PC] == (0xF735 if expect_effect else 0xF7E6), context
        assert sim.registers[SP] == 0xBFFE and crossed_gap == expect_effect, context
        if expect_effect:
            assert (memory[0xA10C], memory[0xA100], memory[0xA101], memory[0xA118]) == (0, 0, 128, 255)
            assert trace.writes == [(0x7FFD, page) for page in (20, 16, 19, 16)]
        else:
            assert memory[0xA10C] == flags and not trace.writes
        counts['effect' if expect_effect else 'dispatch'] += 1
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  all_threshold_input_bytes=True, real_effect_class=16, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionRecordEffectThresholdVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
