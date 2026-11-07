"""Полный запуск FINALF до смены двух экранов и выбора выхода по Space."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks
from CheckFinal import original_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


class InputPorts(PortTrace):
    def __init__(self, simulator, speed, space):
        super().__init__(simulator)
        self.speed = speed
        self.space = space
        self.reads = []

    def read_port(self, registers, port):
        self.reads.append(port)
        if port == self.speed or port == 0x7FFE and self.space:
            return 254
        return 255


def main():
    flat = original_memory()
    bitmaps = tuple(bytes(flat[0x62A9 + index * 0x1800:0x62A9 + (index + 1) * 0x1800])
                    for index in range(3))
    cases = 0
    for time, (speed, space) in product((0, 100, 70880), ((None, False), (0xFBFE, False), (0xFDFE, True))):
        banks = [bytearray([i] * 0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][:] = bytes(flat[0x8000:0xC000])
        memory = RecordedBanks(banks=banks, out7ffd=16)
        sim = Simulator(memory, config={'frame_duration': 70908, 'int_active': 36})
        trace = InputPorts(sim, speed, space)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6000, 'SP': 0x5FFE}, None, False)
        initial[25] = time
        sim.registers[:] = initial
        sim.run(0x6000, 0x607A, interrupts=True)
        context = (time, speed, space)
        assert sim.registers[SP] == 0x5FFE and memory.o7ffd == 1, context
        assert sim.registers[14] == 0xBE and sim.registers[27] == 2 and not sim.registers[26]
        assert bytes(memory[0xBE00:0xBF01]) == b'\xBF' * 257
        assert bytes(memory[0xBFBF:0xBFC2]) == bytes.fromhex('c36c61')
        for bank, bitmap in zip((7, 0, 1), bitmaps):
            assert bytes(memory.banks[bank][:6144]) == bitmap
        assert bytes(memory.banks[7][6144:6912]) == b'\x88' * 768
        assert trace.writes == [(0x7FFD, page) for page in (31, 7, 0, 1)]
        sim.run(0x607A, 0x60AC, interrupts=True)
        assert sim.registers[SP] == 0x5FFE and memory.o7ffd == 0, context
        assert bytes(memory.banks[5][:6144]) == bitmaps[1], context
        assert bytes(memory.banks[5][6144:6912]) == b'\x90' * 768, context
        sim.run(0x60AC, 0x6111, interrupts=True)
        assert sim.registers[SP] == 0x5FFE and memory.o7ffd == 1, context
        assert bytes(memory.banks[5][:6144]) == bitmaps[2], context
        assert bytes(memory.banks[5][6144:6912]) == b'\xA0' * 768, context
        paging = [value for port, value in trace.writes if port == 0x7FFD]
        assert paging == [31, 7, 0, 1, 0, 8, 0, 1, 1], (context, paging)
        expected_exit = 0x6148 if space else 0x607A
        sim.run(0x6111, expected_exit, interrupts=True)
        assert sim.registers[PC] == expected_exit and sim.registers[SP] == 0x5FFE
        assert memory[0x60D4] == {None: 1, 0xFBFE: 0, 0xFDFE: 2}[speed]
        assert trace.reads == ([0xFBFE, 0x7FFE] if speed == 0xFBFE else [0xFBFE, 0xFDFE, 0x7FFE])
        if space:
            sim.run(0x6148, 0x616B, interrupts=True)
            assert memory.o7ffd == 31 and bytes(memory.banks[7][6144:6912]) == bytes(768)
            assert sim.registers[27] == 0 and not sim.registers[26]
        cases += 1
    report = dict(passed=True, total_cases=cases, three_source_bitmaps_compared=True,
                  both_generated_draws_compared=True, frame_duration=70908,
                  actual_im2_executed=True, im2_switches_per_case=3, native_final_scene_verified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/FinalCycleVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
