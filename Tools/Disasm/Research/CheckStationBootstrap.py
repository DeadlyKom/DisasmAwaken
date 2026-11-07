"""Перенос станционного загрузчика и ядра до первого обращения к диску."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


def main():
    data = (ROOT / 'Tools/Disasm/Extracted/Active/04_STATIONF.C.bin').read_bytes()
    cases = 0
    for page, stack in product((0, 8, 16, 24), (0x5FFF, 0x5DF0, 0xBFFE)):
        banks = [bytearray([0xA0 + bank] * 0x4000) for bank in range(8)]
        banks[5][0x2000:] = data[:0x2000]
        banks[2][:len(data) - 0x2000] = data[0x2000:]
        memory = RecordedBanks(banks=banks, out7ffd=page)
        simulator = Simulator(memory)
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        initial = get_registers({'PC': 0x6300, 'SP': stack, 'IX': 0x1234, 'IY': 0xABCD,
                                 '^HL': 0x2345, '^DE': 0x3456, '^BC': 0x4567, '^AF': 0x5678}, None, False)
        simulator.registers[:] = initial
        simulator.run(0x6300, 0x4000)
        assert bytes(memory[0x4000:0x42B5]) == data[0x319:0x5CE]
        entry_stack = simulator.registers[SP]
        simulator.run(0x4000, 0x4070)
        r = simulator.registers
        context = (page, stack)
        assert bytes(memory[0x6322:0x7F8C]) == data[0x5CE:0x2238], context
        assert r[PC] == 0x4070 and r[SP] == entry_stack and memory.o7ffd == 0x18, context
        assert r[0] == 0x18 and r[2:8] == [0, 0, 0xDB, 0, 0xDA, 0xFF], context
        assert r[8:12] == initial[8:12] and r[16:24] == initial[16:24], context
        assert not r[26] and memory[0x6306] == 0x18 and memory[0x9E78] == 0, context
        assert bytes(memory.banks[7][:0x1B00]) == bytes(0x1B00), context
        assert trace.writes == [(0x00FE, 0), (0x7FFD, 0x17), (0x7FFD, 0x18)], context
        cases += 1
    report = dict(passed=True, total_cases=cases, actual_banked_bootstrap=True,
                  bootstrap_bytes=0x2B5, core_bytes=0x1C6A,
                  stops_before_station_file_loads=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/StationBootstrapVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
