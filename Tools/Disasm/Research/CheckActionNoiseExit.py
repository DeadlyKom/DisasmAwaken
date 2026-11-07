"""Цикл 6054 с ROM, настоящим выводом и явным пробуждением HALT."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


class InputTrace(PortTrace):
    def __init__(self, simulator, keys):
        super().__init__(simulator)
        self.keys = iter(keys)
        self.reads = []

    def read_port(self, registers, port):
        if port == 0x00FE:
            value = next(self.keys)
            self.reads.append(value)
            return value
        if port == 0xFFFD:
            return self.ay[self.outfffd]
        return 255


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    total_frames = 0
    for ignored_key, wait in product((0, 255), (0, 2)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        sim = Simulator(memory)
        keys = [ignored_key] * 99 + [255] * wait + [254]
        trace = InputTrace(sim, keys)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0x6054, 'SP': 0xBFFE, 'DE': 0x2468,
                                         'BC': 0x369C, 'IY': 0xA789}, None, False)
        frames = 0
        rom_start = None
        for _ in range(1800000):
            r = sim.registers
            pc = r[PC]
            if pc == 0xAAC4:
                break
            if pc == 0x6070:
                rom_start = 0x500 + refresh(r[15], 2)
            if pc == 0x607B:
                assert bytes(memory[0x8000:0x8C00]) == bytes(memory.roms[1][rom_start:rom_start + 3072])
                assert memory[pc] == 0x76
                assert r[14] == 0x3F
                r[PC] += 1
                frames += 1
                continue
            sim.run()
        assert sim.registers[PC] == 0xAAC4 and sim.registers[SP] == 0xBFFE
        assert frames == 100 + wait and trace.reads == keys
        paging = [value for port, value in trace.writes if port == 0x7FFD]
        assert paging == [17, 16] * (frames + 1)
        assert memory.o7ffd == 16
        expected = bytes(memory.banks[1][0x1CA9:0x1DA9])
        sim.run(0xAAC4, 0x4000)
        assert sim.registers[PC] == 0x4000 and sim.registers[SP] == 0xBFFE
        assert memory.o7ffd == 17 and trace.writes[-1] == (0x7FFD, 17)
        assert bytes(memory.banks[5][:256]) == expected
        total_frames += frames
    report = dict(passed=True, total_cases=4, frames=total_frames,
                  actual_rom_copy_and_output_executed=True, halt_wakeup_injected=True,
                  station_loader_relocated_without_call=True, hardware_irq_executed=False, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseExitVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
