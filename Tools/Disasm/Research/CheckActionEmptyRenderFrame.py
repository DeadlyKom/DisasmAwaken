"""Сквозной вызов E020 с пустой очередью объектных моделей."""
import json
from itertools import product

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionRenderFrameSetup import DESTINATIONS
from CheckControlsTextQueue import base_memory
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    baseline[3][:] = bytes(memory_image()[0xC000:])
    cases = 0
    for mode, inactive, inhibit, count, profile in product((0, 1, 2), (0, 1, 4), (0, 255), (0, 2), range(8)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        for address, value in ((0x9B81, mode), (0xE021, inhibit), (0x688B, count), (0x9B19, 0x76),
                               (0x9B1A, 0x2C), (0xBFFE, 255), (0xBFFF, 63)):
            memory[address] = value
        for address in range(0x9B95, 0x9B98):
            memory[address] = 0
        for index in range(9):
            memory[0x9B00 + index * 2] = 0
            memory[0x9B01 + index * 2] = (profile * 41 + index * 71) & 255
        for address in range(0x9B27, 0x9B27 + 24):
            memory[address] = 0
        for index in range(inactive + 1):
            pointer = 0xA100 + 64 * index
            memory[pointer], memory[pointer + 1], memory[pointer + 27] = (255 if index == inactive else 0), 128, 0
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0xE020, 'SP': 0xBFFE, 'IY': 0x5C3A}, None, False)
        for _ in range(100000):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        context = (mode, inactive, inhibit, count, profile)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        assert bytes(memory[0x9BA1:0x9BA3]) == b'\x01\x00'
        assert bytes(memory[0xE4A7:0xE4A9]) == b'\xfe\xbf'
        assert (memory[0x9B19], memory[0x9B1A]) == ((0x76, 0x2C) if inhibit else (0x77, 0x2B))
        for index, address in enumerate(DESTINATIONS):
            high = (profile * 41 + index * 71) & 255
            assert memory[address] == (129 if high == 128 else high), context
        assert all(memory[0xA11B + 64 * index] == 128 for index in range(inactive + 1))
        assert trace.writes == [(0x7FFD, 19), (0x7FFD, 16)] + [(0x7FFD, 17), (0x7FFD, 16)] * (count + (mode != 1)), context
        assert memory.o7ffd == 16
        cases += 1
    report = dict(passed=True, total_cases=cases, actual_frame_entry_executed=True,
                  empty_object_queue_only=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionEmptyRenderFrameVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
